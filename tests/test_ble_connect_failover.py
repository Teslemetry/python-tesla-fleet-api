"""BLE connect path failover and link teardown after a failed session setup.

Under Home Assistant every ``establish_connection`` attempt re-picks the best
connection path (local adapter or ESPHome proxy). Field logs showed a connect
give up after a failing local adapter and one timed-out proxy, never reaching
the third path, and a failed handshake leaving the link half-open so later
retries kept timing out. These tests drive the real ``establish_connection``
retry loop with a scripted client standing in for habluetooth's wrapper, and
lock in that every failed session setup drops the link before raising.
"""

from __future__ import annotations

from typing import Any
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, MagicMock, patch

import bleak_retry_connector
from bleak.backends.device import BLEDevice
from bleak.exc import BleakError
from bleak_retry_connector import BleakNotFoundError, BleakOutOfConnectionSlotsError
from cryptography.hazmat.primitives.asymmetric import ec

from tesla_fleet_api.exceptions import (
    BluetoothTimeout,
    BluetoothTransportError,
    NotOnWhitelistFault,
    SessionInfoAuthenticationFault,
    SigningDisabled,
)
from tesla_fleet_api.tesla.vehicle.bluetooth import (
    DEFAULT_CONNECT_ATTEMPTS,
    VehicleBluetooth,
)
from tesla_protocol.command.vcsec_pb2 import VehicleSleepStatus_E

VIN = "5YJXCAE43LF123456"
ASLEEP = VehicleSleepStatus_E.VEHICLE_SLEEP_STATUS_ASLEEP


class _PathClient:
    """Stand-in for habluetooth's client: each ``connect()`` attempt lands on
    the next scripted connection path, as habluetooth re-picks per attempt."""

    script: list[BaseException | None] = []
    attempts: list[float] = []

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.is_connected = False
        self.disconnect = AsyncMock()

    async def connect(self, **kwargs: Any) -> None:
        self.attempts.append(kwargs["timeout"])
        outcome = self.script.pop(0)
        if outcome is not None:
            raise outcome
        self.is_connected = True

    async def start_notify(self, *args: Any) -> None:
        pass


def _make_vehicle(key: Any = None) -> VehicleBluetooth[Any]:
    parent = MagicMock()
    parent.private_key = ec.generate_private_key(ec.SECP256R1())
    vehicle = VehicleBluetooth(parent, VIN, key=key, keepalive_interval=None)
    vehicle.device = BLEDevice("AA:BB:CC:DD:EE:FF", vehicle.ble_name, {})
    return vehicle


class ConnectPathFailoverTests(IsolatedAsyncioTestCase):
    """Drive the real ``establish_connection`` loop through scripted paths."""

    def setUp(self) -> None:
        _PathClient.attempts = []
        for patcher in (
            patch("bleak.BleakClient", _PathClient),
            # No real backoff sleeps or BlueZ lookups in a unit test.
            patch.object(
                bleak_retry_connector, "calculate_backoff_time", return_value=0
            ),
            patch.object(
                bleak_retry_connector,
                "get_connected_devices",
                AsyncMock(return_value=[]),
            ),
        ):
            patcher.start()
            self.addCleanup(patcher.stop)

    async def _connect(self, script: list[BaseException | None], **kwargs: Any):
        _PathClient.script = list(script)
        vehicle = _make_vehicle()
        try:
            await vehicle.connect(**kwargs)
        except BluetoothTransportError as err:
            return vehicle, err
        return vehicle, None

    async def test_reaches_a_third_path_after_adapter_and_proxy_fail(self) -> None:
        """The captured field sequence: local adapter fails instantly, the
        best proxy times out, the third path connects."""
        vehicle, err = await self._connect(
            [BleakError("hci0: device not found on BlueZ bus"), TimeoutError(), None]
        )

        self.assertIsNone(err)
        assert vehicle.client is not None
        self.assertTrue(vehicle.client.is_connected)
        self.assertEqual(len(_PathClient.attempts), 3)

    async def test_the_old_two_attempt_budget_gave_up_before_the_third_path(
        self,
    ) -> None:
        _, err = await self._connect(
            [BleakError("hci0: device not found on BlueZ bus"), TimeoutError(), None],
            max_attempts=2,
        )

        self.assertIsNotNone(err)
        self.assertEqual(len(_PathClient.attempts), 2)

    async def test_all_attempts_timing_out_keeps_the_not_found_cause(self) -> None:
        """Callers map a timed-out connect to 'out of range'; the connector's
        ``BleakNotFoundError`` must still be the chained cause."""
        _, err = await self._connect([TimeoutError()] * DEFAULT_CONNECT_ATTEMPTS)

        assert err is not None
        self.assertIsInstance(err.__cause__, BleakNotFoundError)
        self.assertEqual(len(_PathClient.attempts), DEFAULT_CONNECT_ATTEMPTS)

    async def test_out_of_slots_keeps_its_own_cause(self) -> None:
        _, err = await self._connect(
            [BleakError("No available connection slot on the proxy")] * 10
        )

        assert err is not None
        self.assertIsInstance(err.__cause__, BleakOutOfConnectionSlotsError)


def _vehicle_with_link(key: Any = None) -> tuple[VehicleBluetooth[Any], MagicMock]:
    """A vehicle holding a live (mocked) link and fresh, unready sessions."""
    vehicle = _make_vehicle(key)
    client = MagicMock()
    client.is_connected = True
    client.disconnect = AsyncMock()
    vehicle.client = client
    setattr(vehicle, "connect_if_needed", AsyncMock())
    return vehicle, client


class LinkTeardownTests(IsolatedAsyncioTestCase):
    """A failed session setup must not leave a half-open link behind."""

    def setUp(self) -> None:
        self.status: list[bool] = []

    def _track(self, vehicle: VehicleBluetooth[Any]) -> None:
        setattr(vehicle, "_connected", True)
        vehicle.listen_connection_status(self.status.append)

    def assertDropped(self, vehicle: VehicleBluetooth[Any], client: MagicMock):
        client.disconnect.assert_awaited_once()
        self.assertIsNone(vehicle.client)
        self.assertEqual(self.status, [False])

    def assertKept(self, vehicle: VehicleBluetooth[Any], client: MagicMock):
        client.disconnect.assert_not_awaited()
        self.assertIs(vehicle.client, client)
        self.assertEqual(self.status, [])

    async def test_connect_drops_link_on_unexpected_notify_failure(self) -> None:
        vehicle = _make_vehicle()
        client = MagicMock()
        client.disconnect = AsyncMock()
        client.start_notify = AsyncMock(side_effect=RuntimeError("proxy bug"))
        establish = AsyncMock(return_value=client)

        with patch(
            "tesla_fleet_api.tesla.vehicle.bluetooth.establish_connection", establish
        ):
            with self.assertRaises(RuntimeError):
                await vehicle.connect()

        client.disconnect.assert_awaited_once()
        self.assertIsNone(vehicle.client)

    async def test_vcsec_handshake_timeout_drops_link(self) -> None:
        vehicle, client = _vehicle_with_link()
        self._track(vehicle)
        setattr(vehicle, "_send", AsyncMock(side_effect=BluetoothTimeout()))

        with self.assertRaises(BluetoothTimeout):
            await vehicle.door_lock()

        self.assertDropped(vehicle, client)

    async def test_vcsec_session_auth_failure_drops_link(self) -> None:
        vehicle, client = _vehicle_with_link()
        self._track(vehicle)
        setattr(
            vehicle,
            "_send",
            AsyncMock(side_effect=SessionInfoAuthenticationFault("invalid tag")),
        )

        with self.assertRaises(SessionInfoAuthenticationFault):
            await vehicle.door_lock()

        self.assertDropped(vehicle, client)

    async def test_public_handshake_failure_drops_link(self) -> None:
        vehicle, client = _vehicle_with_link()
        self._track(vehicle)
        setattr(vehicle, "_send", AsyncMock(side_effect=NotOnWhitelistFault()))

        with self.assertRaises(NotOnWhitelistFault):
            await vehicle.handshakeVehicleSecurity()

        self.assertDropped(vehicle, client)

    async def test_infotainment_handshake_timeout_drops_link(self) -> None:
        vehicle, client = _vehicle_with_link()
        self._track(vehicle)
        setattr(vehicle, "_send", AsyncMock(side_effect=BluetoothTimeout()))
        setattr(vehicle, "_sleep_status", AsyncMock(return_value=None))

        with self.assertRaises(BluetoothTimeout):
            await vehicle.handshakeInfotainment()

        self.assertDropped(vehicle, client)

    async def test_infotainment_handshake_on_sleeping_car_keeps_link(self) -> None:
        """A sleeping car's silent infotainment is expected, and the VCSEC
        sleep read proves the link alive - dropping it would churn a held
        broadcast link on every read of a parked car."""
        vehicle, client = _vehicle_with_link()
        self._track(vehicle)
        setattr(vehicle, "_send", AsyncMock(side_effect=BluetoothTimeout()))
        setattr(vehicle, "_sleep_status", AsyncMock(return_value=ASLEEP))

        with self.assertRaises(BluetoothTimeout):
            await vehicle.handshakeInfotainment()

        self.assertKept(vehicle, client)

    async def test_infotainment_command_unreadable_vcsec_drops_link(self) -> None:
        vehicle, client = _vehicle_with_link()
        self._track(vehicle)
        setattr(vehicle, "_send", AsyncMock(side_effect=BluetoothTimeout()))
        setattr(vehicle, "_sleep_status", AsyncMock(return_value=None))

        with self.assertRaises(BluetoothTimeout):
            await vehicle.charge_start()

        self.assertDropped(vehicle, client)

    async def test_infotainment_command_on_sleeping_car_keeps_link(self) -> None:
        vehicle, client = _vehicle_with_link()
        vehicle.wake_if_asleep = False
        self._track(vehicle)
        setattr(vehicle, "_send", AsyncMock(side_effect=BluetoothTimeout()))
        setattr(vehicle, "_sleep_status", AsyncMock(return_value=ASLEEP))

        with self.assertRaises(BluetoothTimeout):
            await vehicle.charge_start()

        self.assertKept(vehicle, client)

    async def test_failed_wake_drops_link(self) -> None:
        vehicle, client = _vehicle_with_link()
        self._track(vehicle)
        setattr(
            vehicle, "_await_infotainment", AsyncMock(side_effect=BluetoothTimeout())
        )

        with self.assertRaises(BluetoothTimeout):
            await vehicle.wake_up(wait=True)

        self.assertDropped(vehicle, client)

    async def test_pair_timeout_drops_link(self) -> None:
        vehicle, client = _vehicle_with_link()
        self._track(vehicle)
        setattr(vehicle, "_send", AsyncMock(side_effect=BluetoothTimeout()))
        setattr(vehicle, "_pair_probe", AsyncMock(return_value=False))

        with self.assertRaises(BluetoothTimeout):
            await vehicle.pair(timeout=0.01, poll_interval=0.01)

        self.assertDropped(vehicle, client)

    async def test_signing_disabled_keeps_a_passive_listeners_link(self) -> None:
        vehicle, client = _vehicle_with_link(key=False)
        self._track(vehicle)

        with self.assertRaises(SigningDisabled):
            await vehicle.door_lock()

        self.assertKept(vehicle, client)

    async def test_successful_handshake_keeps_link(self) -> None:
        vehicle, client = _vehicle_with_link()
        self._track(vehicle)
        setattr(vehicle, "_send", AsyncMock())

        await vehicle.handshakeVehicleSecurity()

        self.assertKept(vehicle, client)

    async def test_teardown_failure_never_masks_the_original_error(self) -> None:
        vehicle, client = _vehicle_with_link()
        client.disconnect = AsyncMock(side_effect=BleakError("already gone"))
        setattr(vehicle, "_send", AsyncMock(side_effect=BluetoothTimeout()))

        with self.assertRaises(BluetoothTimeout):
            await vehicle.door_lock()

        self.assertIsNone(vehicle.client)
