"""Regression tests for VehicleBluetooth._send: ACK-then-data follow-up,
stale-queue flushing, and the total-timeout path.

Drives _send() directly with a mocked GATT client - write_gatt_char's
side_effect pushes canned replies onto the domain queue, standing in for
what _on_message would enqueue from a real notification - so these tests
exercise the real wait/ACK-follow-up state machine without a BLE connection.
"""

from __future__ import annotations

from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, MagicMock

from cryptography.hazmat.primitives.asymmetric import ec

from tesla_fleet_api.exceptions import BluetoothTimeout
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
