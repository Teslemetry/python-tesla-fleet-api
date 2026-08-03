"""Tests for VehicleBluetooth's connection-status listener API.

``listen_connection_status`` fans genuine BLE session state changes - a
completed ``connect()`` and a session loss, clean or unexpected - out to
registered callbacks, mirroring the ``listen_*`` idiom in
``BroadcastListeners``. These tests drive the real ``connect()``/
``disconnect()`` machinery against a mocked ``establish_connection`` and a
mocked GATT client - no real BLE - and cover: connection established,
a clean disconnect, an unexpected drop detected mid-operation (bleak's own
``disconnected_callback``), no double-fires across a reconnect loop, and
unregistration.
"""

from __future__ import annotations

from typing import Any
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, MagicMock, patch

from cryptography.hazmat.primitives.asymmetric import ec

from tesla_fleet_api.tesla.vehicle.bluetooth import VehicleBluetooth

VIN = "5YJXCAE43LF123456"


def _make_vehicle() -> VehicleBluetooth[Any]:
    parent = MagicMock()
    parent.private_key = ec.generate_private_key(ec.SECP256R1())
    vehicle = VehicleBluetooth(parent, VIN, keepalive_interval=None)
    vehicle.device = MagicMock()
    return vehicle


def _make_client() -> MagicMock:
    client = MagicMock()
    client.is_connected = True
    client.start_notify = AsyncMock()
    client.disconnect = AsyncMock()
    return client


class ConnectionEstablishedTests(IsolatedAsyncioTestCase):
    async def test_connect_fires_true_after_notify_subscribed(self) -> None:
        vehicle = _make_vehicle()
        client = _make_client()
        events: list[bool] = []
        vehicle.listen_connection_status(events.append)

        with patch(
            "tesla_fleet_api.tesla.vehicle.bluetooth.establish_connection",
            AsyncMock(return_value=client),
        ):
            await vehicle.connect()

        self.assertEqual(events, [True])
        self.assertTrue(vehicle._connected)

    async def test_disconnected_callback_is_wired_into_establish_connection(
        self,
    ) -> None:
        vehicle = _make_vehicle()
        client = _make_client()
        mock_establish = AsyncMock(return_value=client)

        with patch(
            "tesla_fleet_api.tesla.vehicle.bluetooth.establish_connection",
            mock_establish,
        ):
            await vehicle.connect()

        _, kwargs = mock_establish.call_args
        self.assertEqual(kwargs["disconnected_callback"], vehicle._on_ble_disconnected)


class CleanDisconnectTests(IsolatedAsyncioTestCase):
    async def test_disconnect_fires_false(self) -> None:
        vehicle = _make_vehicle()
        client = _make_client()
        events: list[bool] = []

        with patch(
            "tesla_fleet_api.tesla.vehicle.bluetooth.establish_connection",
            AsyncMock(return_value=client),
        ):
            await vehicle.connect()
        vehicle.listen_connection_status(events.append)

        await vehicle.disconnect()

        self.assertEqual(events, [False])
        self.assertFalse(vehicle._connected)

    async def test_disconnect_without_prior_connection_does_not_fire(self) -> None:
        vehicle = _make_vehicle()
        events: list[bool] = []
        vehicle.listen_connection_status(events.append)

        result = await vehicle.disconnect()

        self.assertFalse(result)
        self.assertEqual(events, [])


class UnexpectedDropTests(IsolatedAsyncioTestCase):
    async def test_bleak_disconnected_callback_fires_false_mid_operation(self) -> None:
        vehicle = _make_vehicle()
        client = _make_client()
        events: list[bool] = []

        with patch(
            "tesla_fleet_api.tesla.vehicle.bluetooth.establish_connection",
            AsyncMock(return_value=client),
        ):
            await vehicle.connect()
        vehicle.listen_connection_status(events.append)

        # Simulate the link dropping while a command is in flight, exactly as
        # bleak would invoke its disconnected_callback - not via our own
        # disconnect() path.
        vehicle._on_ble_disconnected(client)

        self.assertEqual(events, [False])
        self.assertFalse(vehicle._connected)

    async def test_stale_client_disconnect_does_not_change_active_session(self) -> None:
        vehicle = _make_vehicle()
        stale_client = _make_client()
        active_client = _make_client()
        events: list[bool] = []

        with patch(
            "tesla_fleet_api.tesla.vehicle.bluetooth.establish_connection",
            AsyncMock(side_effect=[stale_client, active_client]),
        ):
            await vehicle.connect()
            await vehicle.connect()
        vehicle.listen_connection_status(events.append)

        vehicle._on_ble_disconnected(stale_client)

        self.assertEqual(events, [])
        self.assertTrue(vehicle._connected)
        self.assertIs(vehicle.client, active_client)

    async def test_explicit_disconnect_after_unexpected_drop_does_not_double_fire(
        self,
    ) -> None:
        vehicle = _make_vehicle()
        client = _make_client()
        events: list[bool] = []

        with patch(
            "tesla_fleet_api.tesla.vehicle.bluetooth.establish_connection",
            AsyncMock(return_value=client),
        ):
            await vehicle.connect()
        vehicle.listen_connection_status(events.append)

        vehicle._on_ble_disconnected(client)
        await vehicle.disconnect()

        self.assertEqual(events, [False])


class ReconnectLoopTests(IsolatedAsyncioTestCase):
    async def test_reconnect_cycle_fires_exactly_one_event_per_transition(
        self,
    ) -> None:
        vehicle = _make_vehicle()
        events: list[bool] = []
        vehicle.listen_connection_status(events.append)

        for _ in range(3):
            client = _make_client()
            with patch(
                "tesla_fleet_api.tesla.vehicle.bluetooth.establish_connection",
                AsyncMock(return_value=client),
            ):
                await vehicle.connect()
            await vehicle.disconnect()

        self.assertEqual(events, [True, False, True, False, True, False])

    async def test_redundant_connect_while_already_connected_does_not_refire(
        self,
    ) -> None:
        vehicle = _make_vehicle()
        client = _make_client()
        events: list[bool] = []

        with patch(
            "tesla_fleet_api.tesla.vehicle.bluetooth.establish_connection",
            AsyncMock(return_value=client),
        ):
            await vehicle.connect()
            vehicle.listen_connection_status(events.append)
            await vehicle.connect()

        self.assertEqual(events, [])


class UnregisterTests(IsolatedAsyncioTestCase):
    async def test_unsubscribe_stops_further_dispatch(self) -> None:
        vehicle = _make_vehicle()
        client = _make_client()
        events: list[bool] = []
        unsubscribe = vehicle.listen_connection_status(events.append)

        with patch(
            "tesla_fleet_api.tesla.vehicle.bluetooth.establish_connection",
            AsyncMock(return_value=client),
        ):
            await vehicle.connect()

        unsubscribe()
        await vehicle.disconnect()

        self.assertEqual(events, [True])

    async def test_unsubscribe_is_idempotent(self) -> None:
        vehicle = _make_vehicle()
        unsubscribe = vehicle.listen_connection_status(lambda _connected: None)

        unsubscribe()
        unsubscribe()  # must not raise


class CallbackFailureIsolationTests(IsolatedAsyncioTestCase):
    async def test_a_raising_listener_does_not_block_others(self) -> None:
        vehicle = _make_vehicle()
        client = _make_client()
        events: list[bool] = []

        def bad_listener(_connected: bool) -> None:
            raise RuntimeError("boom")

        vehicle.listen_connection_status(bad_listener)
        vehicle.listen_connection_status(events.append)

        with patch(
            "tesla_fleet_api.tesla.vehicle.bluetooth.establish_connection",
            AsyncMock(return_value=client),
        ):
            await vehicle.connect()

        self.assertEqual(events, [True])
