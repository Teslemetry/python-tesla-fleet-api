"""Regression tests for dynamic ``bleak`` client/scanner resolution.

Home Assistant's habluetooth stack replaces ``bleak.BleakClient`` (and
``bleak.BleakScanner``) at runtime with a multi-adapter/proxy-aware client
*after* this library may already have been imported. A class captured by an
``from bleak import BleakClient`` at module load never sees that replacement,
so the library would connect on the pristine local backend instead of the
Home Assistant-selected adapter or ESPHome proxy. These tests import the
modules first, install a late sentinel onto the ``bleak`` module, and prove the
sentinel - not a stale import-time class - reaches ``establish_connection`` and
``BleakScanner`` construction.

They also lock in the stage-specific connect diagnostics and confirm the fix
leaves ``Router`` failover semantics untouched.
"""

from __future__ import annotations

from typing import Any
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, MagicMock, patch

from bleak.exc import BleakError
from cryptography.hazmat.primitives.asymmetric import ec

# Import the modules under test up front, exactly as a consumer that loads this
# library before habluetooth installs its wrappers would.
import tesla_fleet_api.tesla.bluetooth as tesla_bluetooth
import tesla_fleet_api.tesla.vehicle.bluetooth as vehicle_bluetooth
from tesla_fleet_api.exceptions import (
    BluetoothTransportError,
    BluetoothUnconfirmedCommand,
)
from tesla_fleet_api.router import VehicleRouter
from tesla_fleet_api.tesla.bluetooth import TeslaBluetooth
from tesla_fleet_api.tesla.vehicle.bluetooth import VehicleBluetooth

VIN = "5YJXCAE43LF123456"


class _SentinelClient:
    """Stand-in for habluetooth's late-installed multi-adapter BleakClient."""


def _make_vehicle() -> VehicleBluetooth[Any]:
    parent = MagicMock()
    parent.private_key = ec.generate_private_key(ec.SECP256R1())
    vehicle = VehicleBluetooth(parent, VIN)
    vehicle.device = MagicMock()
    vehicle._start_keepalive = AsyncMock()  # type: ignore[method-assign]
    return vehicle


def _make_connected_client() -> MagicMock:
    client = MagicMock()
    client.start_notify = AsyncMock()
    client.disconnect = AsyncMock()
    client.is_connected = True
    return client


class LateBleakClientBindingTests(IsolatedAsyncioTestCase):
    """The vehicle transport must honor a bleak.BleakClient swapped in late."""

    async def test_connect_uses_late_installed_bleak_client(self) -> None:
        vehicle = _make_vehicle()
        captured: dict[str, Any] = {}

        async def fake_establish(client_cls: Any, *args: Any, **kwargs: Any) -> Any:
            captured["client_cls"] = client_cls
            return _make_connected_client()

        # Install the sentinel onto the live bleak module AFTER import, then
        # dispatch a connect. A dynamic lookup passes the sentinel through; the
        # stale import-time class would still be handed to establish_connection.
        with (
            patch("bleak.BleakClient", _SentinelClient),
            patch.object(
                vehicle_bluetooth, "establish_connection", side_effect=fake_establish
            ),
        ):
            await vehicle.connect()

        self.assertIs(captured["client_cls"], _SentinelClient)


class LateBleakClientBindingTopLevelTests(IsolatedAsyncioTestCase):
    """The top-level Bluetooth helper must honor the same late swap."""

    async def test_query_display_name_uses_late_installed_bleak_client(self) -> None:
        helper = TeslaBluetooth()
        device = MagicMock()
        device.name = "S8831fdab22879fd7C"
        captured: dict[str, Any] = {}

        client = MagicMock()
        client.read_gatt_char = AsyncMock(return_value="🔑 MyCar".encode("utf-8"))
        client.disconnect = AsyncMock()

        async def fake_establish(client_cls: Any, *args: Any, **kwargs: Any) -> Any:
            captured["client_cls"] = client_cls
            return client

        with (
            patch("bleak.BleakClient", _SentinelClient),
            patch.object(
                tesla_bluetooth, "establish_connection", side_effect=fake_establish
            ),
        ):
            name = await helper.query_display_name(device)

        self.assertIs(captured["client_cls"], _SentinelClient)
        self.assertEqual(name, "MyCar")


class LateBleakScannerBindingTests(IsolatedAsyncioTestCase):
    """find_vehicle must construct a late-installed scanner, unfiltered/active."""

    async def test_find_vehicle_uses_late_installed_scanner(self) -> None:
        vehicle = _make_vehicle()

        scanner_instance = MagicMock()
        scanner_instance.find_device_by_name = AsyncMock(return_value=MagicMock())
        scanner_factory = MagicMock(return_value=scanner_instance)

        with patch("bleak.BleakScanner", scanner_factory):
            await vehicle.find_vehicle()

        scanner_factory.assert_called_once()
        _, kwargs = scanner_factory.call_args
        # Active scanning is required (the name lives in the scan response), and
        # the vehicle advertises no service UUID pre-connect, so the scan must
        # stay unfiltered.
        self.assertEqual(kwargs.get("scanning_mode"), "active")
        self.assertNotIn("service_uuids", kwargs)


class ConnectStageDiagnosticsTests(IsolatedAsyncioTestCase):
    """A failed connect must name the stage and chain the original cause."""

    async def _assert_stage_logged(
        self,
        *,
        establish_side_effect: BaseException | None,
        start_notify_side_effect: BaseException | None,
        expected_stage: str,
        underlying: BaseException,
    ) -> None:
        vehicle = _make_vehicle()

        if establish_side_effect is not None:
            establish = AsyncMock(side_effect=establish_side_effect)
        else:
            client = _make_connected_client()
            if start_notify_side_effect is not None:
                client.start_notify = AsyncMock(side_effect=start_notify_side_effect)
            establish = AsyncMock(return_value=client)

        with patch.object(vehicle_bluetooth, "establish_connection", establish):
            with self.assertLogs("tesla_fleet_api", level="DEBUG") as logs:
                with self.assertRaises(BluetoothTransportError) as ctx:
                    await vehicle.connect()

        self.assertIs(ctx.exception.__cause__, underlying)
        record = "\n".join(logs.output)
        self.assertIn(f"stage={expected_stage}", record)
        self.assertIn(type(underlying).__name__, record)
        self.assertIn(str(underlying), record)

    async def test_establish_connection_bleak_error_names_stage(self) -> None:
        err = BleakError("no adapter")
        await self._assert_stage_logged(
            establish_side_effect=err,
            start_notify_side_effect=None,
            expected_stage="establish_connection",
            underlying=err,
        )

    async def test_establish_connection_timeout_names_stage(self) -> None:
        err = TimeoutError("connect timed out")
        await self._assert_stage_logged(
            establish_side_effect=err,
            start_notify_side_effect=None,
            expected_stage="establish_connection",
            underlying=err,
        )

    async def test_start_notify_bleak_error_names_stage(self) -> None:
        err = BleakError("notify failed")
        await self._assert_stage_logged(
            establish_side_effect=None,
            start_notify_side_effect=err,
            expected_stage="start_notify",
            underlying=err,
        )

    async def test_start_notify_timeout_names_stage(self) -> None:
        err = TimeoutError("start_notify timed out")
        await self._assert_stage_logged(
            establish_side_effect=None,
            start_notify_side_effect=err,
            expected_stage="start_notify",
            underlying=err,
        )


class _FakeCloudFallback:
    """A cloud secondary tracking whether the router fell over to it."""

    def __init__(self) -> None:
        self.vin = VIN
        self.wake_up_calls = 0

    async def wake_up(self) -> dict[str, Any]:
        self.wake_up_calls += 1
        return {"response": {"result": True, "reason": ""}}


class RouterFailoverUnchangedTests(IsolatedAsyncioTestCase):
    """The fix must not alter Router failover: a pre-command connect
    BluetoothTransportError still fails over to cloud exactly once, and an
    ambiguous BluetoothUnconfirmedCommand still never replays."""

    async def test_pre_command_connect_error_fails_over_once(self) -> None:
        primary = _make_vehicle()
        primary.connect = AsyncMock(  # type: ignore[method-assign]
            side_effect=BluetoothTransportError()
        )
        primary.connect_if_needed = AsyncMock(  # type: ignore[method-assign]
            side_effect=BluetoothTransportError()
        )
        fallback = _FakeCloudFallback()
        router = VehicleRouter(primary, fallback)

        result = await router.wake_up()

        self.assertEqual(result, {"response": {"result": True, "reason": ""}})
        self.assertEqual(fallback.wake_up_calls, 1)

    async def test_unconfirmed_command_does_not_replay(self) -> None:
        primary = _make_vehicle()
        primary.wake_up = AsyncMock(  # type: ignore[method-assign]
            side_effect=BluetoothUnconfirmedCommand()
        )
        fallback = _FakeCloudFallback()
        router = VehicleRouter(primary, fallback)

        with self.assertRaises(BluetoothUnconfirmedCommand):
            await router.wake_up()

        self.assertEqual(fallback.wake_up_calls, 0)
