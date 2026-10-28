"""Permissions, confirmation, durable deduplication and SDK delegation."""

import asyncio
import dataclasses
import tempfile
import time
from pathlib import Path
from unittest import IsolatedAsyncioTestCase, TestCase
from unittest.mock import AsyncMock, MagicMock, patch

from mcp_server.auth import ManagedOAuth, login
from mcp_server.commands import CommandJournal
from mcp_server.config import Config, READ_TOOLS, WRITE_TOOLS
from mcp_server.service import TeslaService, ToolFailure
from mcp_server.storage import Store
from tesla_fleet_api.exceptions import VehicleOffline

VIN = "LRWYGCEK0NC000001"
OTHER = "LRWYGCEK0NC000002"
RID = "test-request-00001"


def config(path, **kwargs):
    return Config(client_id="id", vins=frozenset({VIN}), state_dir=Path(path), **kwargs)


class StoreTests(TestCase):
    def test_permissions_atomic_update_and_symlinks(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "state"
            store = Store(root)
            store.write("tokens.json", {"v": 1})
            store.write("tokens.json", {"v": 2})
            self.assertEqual(store.read("tokens.json"), {"v": 2})
            self.assertEqual(root.stat().st_mode & 0o777, 0o700)
            self.assertEqual((root / "tokens.json").stat().st_mode & 0o777, 0o600)
            (root / "link").symlink_to(root / "tokens.json")
            with self.assertRaises(OSError):
                store.read("link")
            (root / "tokens.json").chmod(0o644)
            with self.assertRaises(ValueError):
                store.read("tokens.json")
            root.chmod(0o755)
            with self.assertRaises(ValueError):
                Store(root)

    def test_service_lease_rejects_second_process(self):
        with tempfile.TemporaryDirectory() as temp:
            store = Store(Path(temp))
            with store.lock("service.lock", blocking=False):
                with self.assertRaises(BlockingIOError):
                    with store.lock("service.lock", blocking=False):
                        self.fail("Second service acquired lease")

    def test_config_fails_closed(self):
        for kwargs in (
            {"vins": frozenset()},
            {"region": "xx"},
            {"tools": frozenset({"door_unlock"})},
            {"redirect_uri": "http://example.com"},
        ):
            values = {
                "client_id": "id",
                "vins": frozenset({VIN}),
                "state_dir": Path("unused"),
            }
            values.update(kwargs)
            with self.assertRaises(ValueError):
                Config(**values)
        self.assertNotIn("get_location", config("unused").tools)
        self.assertFalse(config("unused").enable_commands)


class ServiceTests(IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.store = Store(Path(self.temp.name))
        self.config = config(
            self.temp.name,
            tools=READ_TOOLS | WRITE_TOOLS,
            enable_commands=True,
            enable_waypoints=True,
            private_key=Path(self.temp.name) / "key.pem",
        )
        self.api = MagicMock()
        self.api.private_key = object()
        self.vehicle = MagicMock()
        self.vehicle.list = AsyncMock(
            return_value={"response": [{"vin": VIN, "state": "online"}, {"vin": OTHER}]}
        )
        self.vehicle.vehicle_data = AsyncMock(
            return_value={
                "response": {
                    "charge_state": {"battery_level": 77},
                    "vehicle_state": {"locked": True, "saved_location": "SECRET"},
                    "drive_state": {
                        "latitude": 31,
                        "longitude": 121,
                        "timestamp": 42,
                        "SECRET": 1,
                    },
                }
            }
        )
        self.vehicle.wake_up = AsyncMock(return_value={"response": {"state": "asleep"}})
        self.vehicle.navigation_request = AsyncMock(return_value={"result": True})
        self.vehicle.navigation_waypoints_request = AsyncMock(
            return_value={"result": True}
        )
        self.api.vehicles.createFleet.return_value = self.vehicle
        self.api.vehicles.createSigned.return_value = self.vehicle
        self.journal = CommandJournal(self.store)
        self.service = TeslaService(self.api, self.config, self.journal)

    async def prepare(self, tool="wake_vehicle", value="", rid=RID):
        result = await self.service.command(tool, VIN, rid, value)
        self.assertEqual(result["status"], "pending")
        self.journal.approve(rid)

    async def test_list_filters_and_minimizes_account_data(self):
        result = await self.service.read("list_vehicles")
        self.assertEqual(result["response"], [{"vin": VIN, "state": "online"}])

    async def test_status_does_not_expose_location_or_saved_addresses(self):
        result = await self.service.read("get_vehicle_state", VIN)
        self.assertNotIn("SECRET", str(result))
        self.assertNotIn("drive_state", str(result))
        self.assertEqual(
            self.vehicle.vehicle_data.call_args.kwargs["endpoints"],
            ["charge_state", "climate_state", "vehicle_state"],
        )

    async def test_location_uses_explicit_endpoint_and_returns_timestamp(self):
        result = await self.service.read("get_location", VIN)
        self.assertEqual(
            result["response"], {"latitude": 31, "longitude": 121, "timestamp": 42}
        )
        self.vehicle.vehicle_data.assert_awaited_once_with(endpoints=["location_data"])

    async def test_withheld_location_is_unavailable_not_empty_success(self):
        self.vehicle.vehicle_data.return_value = {
            "response": {"drive_state": {"latitude": None, "longitude": None}}
        }
        with self.assertRaises(ToolFailure):
            await self.service.read("get_location", VIN)

    async def test_permissions_and_vin_enforced_before_sdk_calls(self):
        for tool, vin in (
            ("door_unlock", VIN),
            ("get_location", OTHER),
            ("get_vehicle_state", "../../x"),
        ):
            with self.assertRaises(ToolFailure):
                await self.service.read(tool, vin)
        self.api.vehicles.createFleet.assert_not_called()
        readonly = TeslaService(self.api, config(self.temp.name), self.journal)
        with self.assertRaises(ToolFailure):
            await readonly.command("wake_vehicle", VIN, RID)
        with self.assertRaises(ToolFailure):
            await readonly.read("get_location", VIN)

    async def test_prepare_does_not_submit_approved_executes_once_after_restart(self):
        await self.prepare()
        self.vehicle.wake_up.assert_not_awaited()
        result = await self.service.command("wake_vehicle", VIN, RID)
        self.assertEqual(result["status"], "accepted")
        restarted = TeslaService(
            self.api, self.config, CommandJournal(Store(Path(self.temp.name)))
        )
        self.assertEqual(
            (await restarted.command("wake_vehicle", VIN, RID))["status"], "accepted"
        )
        self.vehicle.wake_up.assert_awaited_once_with(wait=False)

    async def test_equivalent_payload_with_new_id_does_not_bypass_confirmation(self):
        await self.prepare()
        result = await self.service.command("wake_vehicle", VIN, RID + "new")
        self.assertEqual(result["duplicate_of"], RID)
        self.vehicle.wake_up.assert_not_awaited()
        self.assertEqual(
            (await self.service.command("wake_vehicle", VIN, RID))["status"], "accepted"
        )
        result = await self.service.command("wake_vehicle", VIN, RID + "other")
        self.assertEqual(result["duplicate_of"], RID)
        self.vehicle.wake_up.assert_awaited_once()

    async def test_concurrent_duplicate_has_one_submission(self):
        await self.prepare()
        results = await asyncio.gather(
            *(self.service.command("wake_vehicle", VIN, RID) for _ in range(10))
        )
        self.assertTrue(all(r["status"] == "accepted" for r in results))
        self.vehicle.wake_up.assert_awaited_once()

    async def test_binding_and_expiry(self):
        await self.prepare("navigate_to", "Shanghai")
        with self.assertRaises(ToolFailure):
            await self.service.command("navigate_to", VIN, RID, "Beijing")
        with patch("mcp_server.commands.time.time", return_value=time.time() + 600):
            self.assertEqual(
                (await self.service.command("navigate_to", VIN, RID, "Shanghai"))[
                    "status"
                ],
                "expired",
            )
        self.vehicle.navigation_request.assert_not_awaited()

    async def test_delivery_unknown_is_durable_and_never_replayed(self):
        cases = (
            ("wake_vehicle", "", self.vehicle.wake_up, TimeoutError("secret")),
            (
                "navigate_to",
                "Shanghai",
                self.vehicle.navigation_request,
                VehicleOffline(),
            ),
        )
        for index, (tool, value, method, error) in enumerate(cases):
            rid = RID + str(index)
            await self.prepare(tool, value, rid)
            method.side_effect = error
            result = await self.service.command(tool, VIN, rid, value)
            self.assertEqual(result["status"], "unknown")
            await self.service.command(tool, VIN, rid, value)
            method.assert_awaited_once()

    async def test_cancellation_leaves_reservation_and_no_replay(self):
        await self.prepare()
        self.vehicle.wake_up.side_effect = asyncio.CancelledError
        with self.assertRaises(asyncio.CancelledError):
            await self.service.command("wake_vehicle", VIN, RID)
        self.assertEqual(
            (await self.service.command("wake_vehicle", VIN, RID))["status"], "unknown"
        )
        self.vehicle.wake_up.assert_awaited_once()

    async def test_navigation_delegates_exact_string_to_signed_sdk(self):
        for tool, value, method in (
            ("navigate_to", "上海市人民广场", self.vehicle.navigation_request),
            (
                "navigate_waypoints",
                '{"opaque":"Tesla-compatible payload"}',
                self.vehicle.navigation_waypoints_request,
            ),
        ):
            rid = RID + tool
            await self.prepare(tool, value, rid)
            self.assertEqual(
                (await self.service.command(tool, VIN, rid, value))["status"],
                "accepted",
            )
            method.assert_awaited_once_with(value)
        self.vehicle.wake_up.assert_not_awaited()

    async def test_navigation_rejection_and_feature_gate(self):
        await self.prepare("navigate_to", "Shanghai")
        self.vehicle.navigation_request.return_value = {"result": False}
        self.assertEqual(
            (await self.service.command("navigate_to", VIN, RID, "Shanghai"))["status"],
            "rejected",
        )
        gated = TeslaService(
            self.api,
            dataclasses.replace(self.config, enable_waypoints=False),
            self.journal,
        )
        with self.assertRaises(ToolFailure):
            await gated.command("navigate_waypoints", VIN, RID + "x", "value")

    async def test_read_errors_redacted_including_baseexception_sdk_errors(self):
        for error in (
            ValueError("TOKEN-SECRET"),
            VehicleOffline(data={"secret": "TOKEN-SECRET"}),
        ):
            self.vehicle.vehicle_data.side_effect = error
            with self.assertRaises(ToolFailure) as caught:
                await self.service.read("get_location", VIN)
            self.assertNotIn("TOKEN-SECRET", str(caught.exception))

    async def test_bad_input_never_enters_journal(self):
        for rid, value in (("short", "Shanghai"), (RID, ""), (RID, "x" * 16385)):
            with self.assertRaises(ToolFailure):
                await self.service.command("navigate_to", VIN, rid, value)
        self.assertFalse(self.store.read("commands.json"))


class ManagedOAuthTests(IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.store = Store(Path(self.temp.name))
        self.config = config(self.temp.name)
        self.store.write(
            "tokens.json",
            {
                "region": "cn",
                "client_id": "id",
                "access_token": "old",
                "refresh_token": "refresh",
                "expires": 0,
            },
        )
        self.api = ManagedOAuth(MagicMock(), self.config, self.store)

    async def test_concurrent_refresh_and_rotation_saved_once(self):
        async def refresh(api):
            await asyncio.sleep(0)
            api._access_token = "new"
            api.refresh_token = "rotated"
            api.expires = int(time.time()) + 3600
            return {}

        with patch(
            "tesla_fleet_api.tesla.oauth.TeslaFleetOAuth.refresh_access_token",
            autospec=True,
            side_effect=refresh,
        ) as call:
            self.assertEqual(
                await asyncio.gather(*(self.api.access_token() for _ in range(20))),
                ["new"] * 20,
            )
        self.assertEqual(call.await_count, 1)
        self.assertEqual(self.store.read("tokens.json")["refresh_token"], "rotated")

    async def test_region_mismatch_rejected(self):
        with self.assertRaises(ValueError):
            ManagedOAuth(
                MagicMock(), dataclasses.replace(self.config, region="eu"), self.store
            )

    async def test_persistence_failure_stops_future_requests(self):
        self.api._access_token = "new"
        self.api.expires = int(time.time()) + 3600
        with patch.object(self.store, "write", side_effect=OSError("SECRET")):
            with self.assertRaises(RuntimeError):
                self.api.save()
        with self.assertRaises(RuntimeError):
            await self.api.access_token()

    async def test_login_rejects_mismatched_state_before_exchange(self):
        cfg = dataclasses.replace(
            self.config, client_secret="secret", redirect_uri="https://example.com/cb"
        )
        with (
            patch(
                "mcp_server.auth.getpass.getpass",
                return_value="https://example.com/cb?code=code&state=wrong",
            ),
            patch("builtins.print"),
            patch.object(
                ManagedOAuth, "get_refresh_token", new_callable=AsyncMock
            ) as exchange,
        ):
            with self.assertRaises(ValueError):
                await login(cfg, self.store)
            exchange.assert_not_awaited()
