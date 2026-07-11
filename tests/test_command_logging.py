"""Tests for the DEBUG-level command/transport/outcome logging added for
troubleshooting whether a command went over Bluetooth, Fleet API, Teslemetry,
or Tessie, and why it failed.

Covers the three logging choke points: ``Commands._sendVehicleSecurity`` /
``_sendInfotainment`` (BLE and Fleet-signed commands), ``TeslaFleetApi._request``
(Fleet/Teslemetry/Tessie REST commands), and ``Router._dispatch`` (backend
selection and failover).
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, MagicMock

from tesla_fleet_api.const import Method
from tesla_fleet_api.exceptions import BluetoothTimeout, NotFound
from tesla_fleet_api.router import Router
from tesla_fleet_api.tesla.fleet import TeslaFleetApi
from tesla_fleet_api.teslemetry.teslemetry import Teslemetry
from tesla_fleet_api.tessie.tessie import Tessie

from ble_mocked_transport import MockedBleTransportTestCase, vcsec_ok_reply

LOGGER_NAME = "tesla_fleet_api"


class BleCommandLoggingTests(MockedBleTransportTestCase):
    """BLE commands log their command name, ``transport=bluetooth``, and outcome."""

    async def test_success_logs_command_transport_and_result(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = vcsec_ok_reply()

        with self.assertLogs(LOGGER_NAME, level="DEBUG") as captured:
            await vehicle.door_lock()

        self.assertTrue(
            any(
                "command=RKE_ACTION_LOCK" in line
                and "transport=bluetooth" in line
                and "result=True" in line
                for line in captured.output
            ),
            captured.output,
        )

    async def test_timeout_logs_error_with_exception_type(self) -> None:
        vehicle, send = self.make_vehicle()
        send.side_effect = BluetoothTimeout()

        with self.assertLogs(LOGGER_NAME, level="DEBUG") as captured:
            with self.assertRaises(BluetoothTimeout):
                await vehicle.door_lock()

        self.assertTrue(
            any(
                "command=RKE_ACTION_LOCK" in line
                and "transport=bluetooth" in line
                and "result=error" in line
                and "BluetoothTimeout" in line
                for line in captured.output
            ),
            captured.output,
        )

    async def test_verify_commands_resolution_logs_verified_outcome(self) -> None:
        from tesla_fleet_api.tesla.vehicle.proto.vcsec_pb2 import (
            VehicleLockState_E,
            VehicleStatus,
        )

        from ble_mocked_transport import vcsec_vehicle_status_reply

        vehicle, send = self.make_vehicle(verify_commands=True)
        send.side_effect = [
            BluetoothTimeout(),
            vcsec_vehicle_status_reply(
                VehicleStatus(
                    vehicleLockState=VehicleLockState_E.VEHICLELOCKSTATE_LOCKED
                )
            ),
        ]

        with self.assertLogs(LOGGER_NAME, level="DEBUG") as captured:
            result = await vehicle.door_lock()

        self.assertEqual(result, {"response": {"result": True, "reason": ""}})
        self.assertTrue(
            any(
                "command=RKE_ACTION_LOCK" in line
                and "transport=bluetooth" in line
                and "verify_commands=resolved" in line
                for line in captured.output
            ),
            captured.output,
        )


def _fake_response(
    *,
    status: int = 200,
    ok: bool = True,
    content_type: str = "application/json",
    json_body: object = None,
):
    resp = MagicMock()
    resp.status = status
    resp.ok = ok
    resp.content_type = content_type
    resp.url = "https://example.com/x"
    resp.headers = {}
    resp.json = AsyncMock(return_value=json_body if json_body is not None else {})
    resp.text = AsyncMock(return_value="")
    return resp


def _make_session(response: object) -> MagicMock:
    session = MagicMock()

    @asynccontextmanager
    async def _ctx(*args, **kwargs):
        yield response

    session.request = MagicMock(side_effect=lambda *a, **k: _ctx(*a, **k))
    return session


class RestCommandLoggingTests(IsolatedAsyncioTestCase):
    """REST commands (Fleet/Teslemetry/Tessie) log endpoint name, transport, outcome."""

    async def test_fleet_success_logs_command_transport_and_result(self) -> None:
        resp = _fake_response(json_body={"response": {"result": True, "reason": ""}})
        api = TeslaFleetApi(
            session=_make_session(resp),
            access_token="token",
            server="https://fleet.example.com",
        )

        with self.assertLogs(LOGGER_NAME, level="DEBUG") as captured:
            await api._request(Method.POST, "api/1/vehicles/VIN123/command/door_lock")

        self.assertTrue(
            any(
                "command=door_lock" in line
                and "transport=fleet" in line
                and "result=True" in line
                and "reason=" in line
                for line in captured.output
            ),
            captured.output,
        )

    async def test_fleet_command_rejection_logs_response_result(self) -> None:
        resp = _fake_response(
            json_body={
                "response": {
                    "result": False,
                    "reason": "cabin comfort remote settings not enabled",
                }
            }
        )
        api = TeslaFleetApi(
            session=_make_session(resp),
            access_token="token",
            server="https://fleet.example.com",
        )

        with self.assertLogs(LOGGER_NAME, level="DEBUG") as captured:
            await api._request(
                Method.POST,
                "api/1/vehicles/VIN123/command/remote_seat_heater_request",
            )

        self.assertTrue(
            any(
                "command=remote_seat_heater_request" in line
                and "transport=fleet" in line
                and "result=False" in line
                and "reason=cabin comfort remote settings not enabled" in line
                for line in captured.output
            ),
            captured.output,
        )

    async def test_fleet_non_command_json_logs_transport_success(self) -> None:
        resp = _fake_response(json_body={"response": {"vehicle_id": 123}})
        api = TeslaFleetApi(
            session=_make_session(resp),
            access_token="token",
            server="https://fleet.example.com",
        )

        with self.assertLogs(LOGGER_NAME, level="DEBUG") as captured:
            await api._request(Method.GET, "api/1/vehicles/VIN123/vehicle_data")

        self.assertTrue(
            any(
                "command=vehicle_data" in line
                and "transport=fleet" in line
                and "result=success" in line
                for line in captured.output
            ),
            captured.output,
        )

    async def test_fleet_failure_logs_command_transport_and_error(self) -> None:
        resp = _fake_response(status=404, ok=False, json_body={"error": "not found"})
        api = TeslaFleetApi(
            session=_make_session(resp),
            access_token="token",
            server="https://fleet.example.com",
        )

        with self.assertLogs(LOGGER_NAME, level="DEBUG") as captured:
            with self.assertRaises(NotFound):
                await api._request(
                    Method.POST, "api/1/vehicles/VIN123/command/door_lock"
                )

        self.assertTrue(
            any(
                "command=door_lock" in line
                and "transport=fleet" in line
                and "result=error" in line
                and "NotFound" in line
                for line in captured.output
            ),
            captured.output,
        )

    async def test_teslemetry_success_logs_transport_teslemetry(self) -> None:
        resp = _fake_response(json_body={"response": {"result": True}})
        api = Teslemetry(session=_make_session(resp), access_token="token")

        with self.assertLogs(LOGGER_NAME, level="DEBUG") as captured:
            await api._request(Method.POST, "api/1/vehicles/VIN123/command/door_lock")

        self.assertTrue(
            any("transport=teslemetry" in line for line in captured.output),
            captured.output,
        )

    async def test_tessie_success_logs_transport_tessie(self) -> None:
        resp = _fake_response(json_body={"result": True})
        api = Tessie(session=_make_session(resp), access_token="token")

        with self.assertLogs(LOGGER_NAME, level="DEBUG") as captured:
            await api._request(Method.POST, "vehicles/VIN123/command/door_lock")

        self.assertTrue(
            any("transport=tessie" in line for line in captured.output),
            captured.output,
        )

    async def test_tessie_command_rejection_logs_top_level_result(self) -> None:
        resp = _fake_response(json_body={"result": False, "reason": "already_locked"})
        api = Tessie(session=_make_session(resp), access_token="token")

        with self.assertLogs(LOGGER_NAME, level="DEBUG") as captured:
            await api._request(Method.POST, "vehicles/VIN123/command/door_lock")

        self.assertTrue(
            any(
                "command=door_lock" in line
                and "transport=tessie" in line
                and "result=False" in line
                and "reason=already_locked" in line
                for line in captured.output
            ),
            captured.output,
        )


class _FakePrimary:
    def __init__(self, *, fail: bool = False):
        self.fail = fail

    async def shared(self, value: int) -> str:
        if self.fail:
            raise ConnectionError("primary failed")
        return f"primary:{value}"


class _FakeFallback:
    async def shared(self, value: int) -> str:
        return f"fallback:{value}"


class RouterCommandLoggingTests(IsolatedAsyncioTestCase):
    """Router logs which backend served a call, and any failover hop."""

    async def test_primary_success_logs_backend_and_result(self) -> None:
        router = Router(_FakePrimary(), _FakeFallback())

        with self.assertLogs(LOGGER_NAME, level="DEBUG") as captured:
            result = await router.shared(1)

        self.assertEqual(result, "primary:1")
        self.assertTrue(
            any(
                "command=shared" in line
                and "backend=_FakePrimary" in line
                and "result=success" in line
                for line in captured.output
            ),
            captured.output,
        )

    async def test_primary_failure_fails_over_and_logs_both_hops(self) -> None:
        router = Router(_FakePrimary(fail=True), _FakeFallback())

        with self.assertLogs(LOGGER_NAME, level="DEBUG") as captured:
            result = await router.shared(1)

        self.assertEqual(result, "fallback:1")
        joined = "\n".join(captured.output)
        self.assertIn("backend=_FakePrimary", joined)
        self.assertIn("result=error", joined)
        self.assertIn("ConnectionError", joined)
        self.assertIn("backend=_FakeFallback", joined)
        self.assertIn("result=success", joined)
