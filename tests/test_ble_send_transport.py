"""Regression tests for VehicleBluetooth._send: ACK-then-data follow-up,
stale-queue flushing, and the total-timeout path.

Drives _send() directly with a mocked GATT client - write_gatt_char's
side_effect pushes canned replies onto the domain queue, standing in for
what _on_message would enqueue from a real notification - so these tests
exercise the real wait/ACK-follow-up state machine without a BLE connection.
"""

from __future__ import annotations

import asyncio
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, MagicMock, patch

from bleak.exc import BleakCharacteristicNotFoundError, BleakError
from cryptography.hazmat.primitives.asymmetric import ec

from tesla_fleet_api.exceptions import BluetoothTimeout, BluetoothTransportError
from tesla_fleet_api.tesla.vehicle.bluetooth import VehicleBluetooth
from tesla_fleet_api.tesla.vehicle.proto.universal_message_pb2 import (
    Destination,
    Domain,
    RoutableMessage,
)

VIN = "5YJXCAE43LF123456"
DOMAIN = Domain.DOMAIN_VEHICLE_SECURITY


def _make_vehicle() -> VehicleBluetooth:
    parent = MagicMock()
    parent.private_key = ec.generate_private_key(ec.SECP256R1())
    vehicle = VehicleBluetooth(parent, VIN)
    vehicle.connect_if_needed = AsyncMock()  # type: ignore[method-assign]
    vehicle.client = MagicMock()
    return vehicle


def _outgoing() -> RoutableMessage:
    return RoutableMessage(
        to_destination=Destination(domain=DOMAIN),
        uuid=b"0123456789abcdef",
    )


class SendImmediateResponseTests(IsolatedAsyncioTestCase):
    async def test_returns_response_that_already_has_required_field(self) -> None:
        vehicle = _make_vehicle()
        msg = _outgoing()
        reply = RoutableMessage(
            from_destination=Destination(domain=DOMAIN),
            protobuf_message_as_bytes=b"data",
        )

        async def fake_write(_uuid, _payload, _response):
            vehicle._queues[DOMAIN].put_nowait(reply)

        vehicle.client.write_gatt_char = AsyncMock(side_effect=fake_write)

        result = await vehicle._send(msg, "protobuf_message_as_bytes")

        self.assertEqual(result, reply)
        vehicle.client.write_gatt_char.assert_awaited_once()


class SendAckFollowupTests(IsolatedAsyncioTestCase):
    async def test_waits_past_ack_for_data_followup(self) -> None:
        vehicle = _make_vehicle()
        msg = _outgoing()
        ack = RoutableMessage(
            from_destination=Destination(domain=DOMAIN), request_uuid=msg.uuid
        )
        data = RoutableMessage(
            from_destination=Destination(domain=DOMAIN),
            protobuf_message_as_bytes=b"payload",
        )

        async def fake_write(_uuid, _payload, _response):
            vehicle._queues[DOMAIN].put_nowait(ack)
            vehicle._queues[DOMAIN].put_nowait(data)

        vehicle.client.write_gatt_char = AsyncMock(side_effect=fake_write)

        result = await vehicle._send(msg, "protobuf_message_as_bytes")

        self.assertEqual(result, data)

    async def test_ack_without_followup_times_out_and_returns_ack(self) -> None:
        vehicle = _make_vehicle()
        vehicle._ack_followup_timeout = 0.05
        msg = _outgoing()
        ack = RoutableMessage(
            from_destination=Destination(domain=DOMAIN), request_uuid=msg.uuid
        )

        async def fake_write(_uuid, _payload, _response):
            vehicle._queues[DOMAIN].put_nowait(ack)

        vehicle.client.write_gatt_char = AsyncMock(side_effect=fake_write)

        result = await vehicle._send(msg, "protobuf_message_as_bytes")

        self.assertEqual(result, ack)

    async def test_unrelated_message_is_ignored_until_matching_data_arrives(
        self,
    ) -> None:
        vehicle = _make_vehicle()
        msg = _outgoing()
        stray = RoutableMessage(
            from_destination=Destination(domain=DOMAIN), request_uuid=b"not-ours"
        )
        data = RoutableMessage(
            from_destination=Destination(domain=DOMAIN),
            protobuf_message_as_bytes=b"payload",
        )

        async def fake_write(_uuid, _payload, _response):
            vehicle._queues[DOMAIN].put_nowait(stray)
            vehicle._queues[DOMAIN].put_nowait(data)

        vehicle.client.write_gatt_char = AsyncMock(side_effect=fake_write)

        result = await vehicle._send(msg, "protobuf_message_as_bytes")

        self.assertEqual(result, data)


class SendActuationEarlyReturnTests(IsolatedAsyncioTestCase):
    """expects_data=False: a bare terminal actuation ack returns immediately."""

    async def test_terminal_ack_returns_without_waiting_followup(self) -> None:
        vehicle = _make_vehicle()
        # A large follow-up window would dominate if the early return regressed;
        # wait_for below fails fast instead of hanging the suite.
        vehicle._ack_followup_timeout = 30
        msg = _outgoing()
        ack = RoutableMessage(
            from_destination=Destination(domain=DOMAIN), request_uuid=msg.uuid
        )

        async def fake_write(_uuid, _payload, _response):
            vehicle._queues[DOMAIN].put_nowait(ack)

        vehicle.client.write_gatt_char = AsyncMock(side_effect=fake_write)

        result = await asyncio.wait_for(
            vehicle._send(msg, "protobuf_message_as_bytes", expects_data=False),
            timeout=1.0,
        )

        self.assertEqual(result, ack)

    async def test_read_still_waits_followup_when_expects_data(self) -> None:
        # Contrast: with expects_data (a read), the same bare ack is NOT terminal
        # - _send waits the follow-up window before returning it, unchanged.
        vehicle = _make_vehicle()
        vehicle._ack_followup_timeout = 0.05
        msg = _outgoing()
        ack = RoutableMessage(
            from_destination=Destination(domain=DOMAIN), request_uuid=msg.uuid
        )

        async def fake_write(_uuid, _payload, _response):
            vehicle._queues[DOMAIN].put_nowait(ack)

        vehicle.client.write_gatt_char = AsyncMock(side_effect=fake_write)

        result = await vehicle._send(
            msg, "protobuf_message_as_bytes", expects_data=True
        )

        self.assertEqual(result, ack)


class SendActuationTimeoutTests(IsolatedAsyncioTestCase):
    """A lost actuation ack raises after the short actuation timeout, not the default."""

    async def test_lost_actuation_ack_uses_short_timeout(self) -> None:
        vehicle = _make_vehicle()
        vehicle._actuation_timeout = 0.05
        vehicle._default_timeout = 5
        msg = _outgoing()
        vehicle.client.write_gatt_char = AsyncMock()  # nothing enqueued

        # wait_for(1.0) would trip first (asyncio.TimeoutError) if _send wrongly
        # waited the 5s default; BluetoothTimeout proves the short path ran.
        with self.assertRaises(BluetoothTimeout):
            await asyncio.wait_for(
                vehicle._send(msg, "protobuf_message_as_bytes", expects_data=False),
                timeout=1.0,
            )

    async def test_read_keeps_default_timeout(self) -> None:
        vehicle = _make_vehicle()
        vehicle._actuation_timeout = 0.05
        vehicle._default_timeout = 5
        msg = _outgoing()
        vehicle.client.write_gatt_char = AsyncMock()  # nothing enqueued

        # A read must ignore the short actuation timeout: _send is still waiting
        # on the default at 0.3s, so the outer wait_for fires instead of the
        # short-path BluetoothTimeout.
        with self.assertRaises(asyncio.TimeoutError):
            await asyncio.wait_for(
                vehicle._send(msg, "protobuf_message_as_bytes", expects_data=True),
                timeout=0.3,
            )


class SendQueueHygieneTests(IsolatedAsyncioTestCase):
    async def test_stale_queued_message_is_discarded_before_send(self) -> None:
        vehicle = _make_vehicle()
        stale = RoutableMessage(
            from_destination=Destination(domain=DOMAIN),
            protobuf_message_as_bytes=b"stale-leftover",
        )
        vehicle._queues[DOMAIN].put_nowait(stale)

        msg = _outgoing()
        fresh = RoutableMessage(
            from_destination=Destination(domain=DOMAIN),
            protobuf_message_as_bytes=b"fresh",
        )

        async def fake_write(_uuid, _payload, _response):
            vehicle._queues[DOMAIN].put_nowait(fresh)

        vehicle.client.write_gatt_char = AsyncMock(side_effect=fake_write)

        result = await vehicle._send(msg, "protobuf_message_as_bytes")

        self.assertEqual(result, fresh)


class SendTimeoutTests(IsolatedAsyncioTestCase):
    async def test_no_response_raises_bluetooth_timeout(self) -> None:
        vehicle = _make_vehicle()
        msg = _outgoing()
        vehicle.client.write_gatt_char = AsyncMock()

        with self.assertRaises(BluetoothTimeout):
            await vehicle._send(msg, "protobuf_message_as_bytes", timeout=0.05)


class SendTransportErrorTests(IsolatedAsyncioTestCase):
    """Write-level failures split on delivery certainty.

    A characteristic-resolution failure is raised by bleak synchronously,
    before any backend I/O - provably pre-submission, so it stays
    ``BluetoothTransportError``. Everything else from ``write_gatt_char``
    happens inside backend I/O, where delivery can't be proven either way, so
    it is treated like a lost ack (``BluetoothTimeout``), not a provable miss.
    """

    async def test_characteristic_not_found_raises_bluetooth_transport_error(
        self,
    ) -> None:
        vehicle = _make_vehicle()
        msg = _outgoing()
        underlying = BleakCharacteristicNotFoundError("write-uuid")
        vehicle.client.write_gatt_char = AsyncMock(side_effect=underlying)

        with self.assertRaises(BluetoothTransportError) as ctx:
            await vehicle._send(msg, "protobuf_message_as_bytes")

        self.assertIs(ctx.exception.__cause__, underlying)

    async def test_mid_write_gatt_failure_raises_bluetooth_timeout(
        self,
    ) -> None:
        vehicle = _make_vehicle()
        msg = _outgoing()
        underlying = BleakError("write failed")
        vehicle.client.write_gatt_char = AsyncMock(side_effect=underlying)

        with self.assertRaises(BluetoothTimeout) as ctx:
            await vehicle._send(msg, "protobuf_message_as_bytes")

        self.assertNotIsInstance(ctx.exception, BluetoothTransportError)
        self.assertIs(ctx.exception.__cause__, underlying)

    async def test_write_gatt_timeout_raises_bluetooth_timeout(
        self,
    ) -> None:
        # bleak-esphome surfaces an aioesphomeapi GATT-write timeout as a
        # builtin TimeoutError (not a BleakError); it must still reach callers
        # as a TeslaFleetError, not a bare TimeoutError.
        vehicle = _make_vehicle()
        msg = _outgoing()
        underlying = TimeoutError(
            "Timeout waiting for BluetoothGATTWriteResponse after 30.0s"
        )
        vehicle.client.write_gatt_char = AsyncMock(side_effect=underlying)

        with self.assertRaises(BluetoothTimeout) as ctx:
            await vehicle._send(msg, "protobuf_message_as_bytes")

        self.assertNotIsInstance(ctx.exception, BluetoothTransportError)
        self.assertIs(ctx.exception.__cause__, underlying)


class ConnectTransportErrorTests(IsolatedAsyncioTestCase):
    async def test_establish_connection_failure_raises_bluetooth_transport_error(
        self,
    ) -> None:
        parent = MagicMock()
        parent.private_key = ec.generate_private_key(ec.SECP256R1())
        vehicle = VehicleBluetooth(parent, VIN)
        vehicle.device = MagicMock()
        underlying = BleakError("connect failed")

        with patch(
            "tesla_fleet_api.tesla.vehicle.bluetooth.establish_connection",
            AsyncMock(side_effect=underlying),
        ):
            with self.assertRaises(BluetoothTransportError) as ctx:
                await vehicle.connect()

        self.assertIs(ctx.exception.__cause__, underlying)

    async def test_connect_if_needed_propagates_transport_error(self) -> None:
        parent = MagicMock()
        parent.private_key = ec.generate_private_key(ec.SECP256R1())
        vehicle = VehicleBluetooth(parent, VIN)
        vehicle.device = MagicMock()
        underlying = BleakError("connect failed")

        with patch(
            "tesla_fleet_api.tesla.vehicle.bluetooth.establish_connection",
            AsyncMock(side_effect=underlying),
        ):
            with self.assertRaises(BluetoothTransportError) as ctx:
                await vehicle.connect_if_needed()

        self.assertIs(ctx.exception.__cause__, underlying)

    async def test_establish_connection_timeout_raises_bluetooth_transport_error(
        self,
    ) -> None:
        # bleak-esphome surfaces an aioesphomeapi connect timeout as a builtin
        # TimeoutError; the connect path must wrap it in BluetoothTransportError.
        parent = MagicMock()
        parent.private_key = ec.generate_private_key(ec.SECP256R1())
        vehicle = VehicleBluetooth(parent, VIN)
        vehicle.device = MagicMock()
        underlying = TimeoutError("connect timed out")

        with patch(
            "tesla_fleet_api.tesla.vehicle.bluetooth.establish_connection",
            AsyncMock(side_effect=underlying),
        ):
            with self.assertRaises(BluetoothTransportError) as ctx:
                await vehicle.connect()

        self.assertIs(ctx.exception.__cause__, underlying)

    async def test_start_notify_timeout_raises_bluetooth_transport_error(
        self,
    ) -> None:
        # start_notify is likewise decorated by bleak-esphome and can raise a
        # builtin TimeoutError after the link is established.
        parent = MagicMock()
        parent.private_key = ec.generate_private_key(ec.SECP256R1())
        vehicle = VehicleBluetooth(parent, VIN)
        vehicle.device = MagicMock()
        underlying = TimeoutError("start_notify timed out")
        client = MagicMock()
        client.start_notify = AsyncMock(side_effect=underlying)
        client.disconnect = AsyncMock()

        with patch(
            "tesla_fleet_api.tesla.vehicle.bluetooth.establish_connection",
            AsyncMock(return_value=client),
        ):
            with self.assertRaises(BluetoothTransportError) as ctx:
                await vehicle.connect()

        self.assertIs(ctx.exception.__cause__, underlying)
        client.disconnect.assert_awaited_once()
        self.assertIsNone(vehicle.client)
