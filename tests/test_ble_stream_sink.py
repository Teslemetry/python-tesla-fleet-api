"""Tests for the subscription-push/command-reply queue collision.

A live ``vehicleDataSubscription`` pushes addressed frames on the same
INFOTAINMENT domain an ordinary command uses for its reply. Before the
``_stream_sinks`` routing fix, ``_send`` would discard any push sitting
unconsumed in ``_queues`` before every send, and ``_await_response`` could
return a push as an unrelated command's own reply. These tests drive the
real (unmocked) ``_send``/``_on_message`` state machine - only the GATT
client is faked - so pushes are injected exactly as ``_on_notify``/the
reassembling buffer would deliver them from a real notification.
"""

from __future__ import annotations

import asyncio
from random import randbytes
from typing import Any
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, MagicMock

from cryptography.hazmat.primitives.asymmetric import ec

from tesla_fleet_api.tesla.vehicle.bluetooth import VehicleBluetooth
from tesla_protocol.command.universal_message_pb2 import (
    Destination,
    Domain,
    RoutableMessage,
)

VIN = "5YJXCAE43LF123456"
DOMAIN = Domain.DOMAIN_INFOTAINMENT


def _make_vehicle(**kwargs: Any) -> VehicleBluetooth[Any]:
    """A VehicleBluetooth with real send/routing logic but a faked GATT client."""
    parent = MagicMock()
    parent.private_key = ec.generate_private_key(ec.SECP256R1())
    vehicle = VehicleBluetooth(parent, VIN, **kwargs)
    vehicle.connect_if_needed = AsyncMock()  # type: ignore[method-assign]
    vehicle.client = MagicMock()
    vehicle.client.write_gatt_char = AsyncMock()
    return vehicle


def _outgoing_msg() -> RoutableMessage:
    return RoutableMessage(
        to_destination=Destination(domain=DOMAIN),
        uuid=randbytes(16),
    )


def _addressed_reply(vehicle: VehicleBluetooth[Any]) -> RoutableMessage:
    """An addressed reply to an ordinary command."""
    return RoutableMessage(
        to_destination=Destination(
            domain=DOMAIN, routing_address=vehicle._from_destination
        ),
        from_destination=Destination(domain=DOMAIN),
        protobuf_message_as_bytes=b"command-reply",
    )


def _subscription_ack(
    vehicle: VehicleBluetooth[Any], request_uuid: bytes
) -> RoutableMessage:
    return RoutableMessage(
        to_destination=Destination(
            domain=DOMAIN, routing_address=vehicle._from_destination
        ),
        from_destination=Destination(domain=DOMAIN),
        request_uuid=request_uuid,
    )


def _subscription_push(
    vehicle: VehicleBluetooth[Any], request_uuid: bytes
) -> RoutableMessage:
    """An addressed subscription push, correlated by the subscribe request's uuid."""
    return RoutableMessage(
        to_destination=Destination(
            domain=DOMAIN, routing_address=vehicle._from_destination
        ),
        from_destination=Destination(domain=DOMAIN),
        protobuf_message_as_bytes=b"push-data",
        request_uuid=request_uuid,
    )


class StreamSinkQueueCollisionTests(IsolatedAsyncioTestCase):
    async def test_already_arrived_push_survives_a_concurrent_send(self) -> None:
        vehicle = _make_vehicle()
        subscribe_uuid = randbytes(16)
        sink = vehicle._register_stream_sink(subscribe_uuid)

        # A push arrives and piles up in the sink before any other command runs.
        vehicle._on_message(_subscription_push(vehicle, subscribe_uuid))
        self.assertFalse(sink.empty())

        async def write_then_ack(*_: Any) -> None:
            vehicle._on_message(_addressed_reply(vehicle))
            await asyncio.sleep(0)

        vehicle.client.write_gatt_char = AsyncMock(side_effect=write_then_ack)

        resp = await asyncio.wait_for(
            vehicle._send(_outgoing_msg(), "protobuf_message_as_bytes"), timeout=1.0
        )

        # The command got its own real reply, and the earlier push is still
        # sitting in the sink - not silently discarded by _send's pre-send
        # drain of _queues.
        self.assertEqual(resp.protobuf_message_as_bytes, b"command-reply")
        self.assertFalse(sink.empty())
        received = await asyncio.wait_for(sink.get(), timeout=0.1)
        self.assertEqual(received.request_uuid, subscribe_uuid)
        self.assertEqual(received.protobuf_message_as_bytes, b"push-data")

    async def test_push_arriving_mid_wait_is_not_returned_as_command_reply(
        self,
    ) -> None:
        vehicle = _make_vehicle()
        subscribe_uuid = randbytes(16)
        sink = vehicle._register_stream_sink(subscribe_uuid)

        async def write_then_push_then_ack(*_: Any) -> None:
            # A push lands while the command is still waiting for its reply.
            vehicle._on_message(_subscription_push(vehicle, subscribe_uuid))
            await asyncio.sleep(0)
            vehicle._on_message(_addressed_reply(vehicle))

        vehicle.client.write_gatt_char = AsyncMock(side_effect=write_then_push_then_ack)

        resp = await asyncio.wait_for(
            vehicle._send(_outgoing_msg(), "protobuf_message_as_bytes"), timeout=1.0
        )

        # A push carries protobuf_message_as_bytes too, so pre-fix it could
        # satisfy _await_response's HasField(requires) check and be returned
        # as the command's own reply. It must not be.
        self.assertEqual(resp.protobuf_message_as_bytes, b"command-reply")
        self.assertFalse(sink.empty())

    async def test_subscription_ack_completes_atomic_registration(self) -> None:
        vehicle = _make_vehicle()
        outgoing = _outgoing_msg()

        async def write_then_push_then_ack(*_: Any) -> None:
            vehicle._on_message(_subscription_push(vehicle, outgoing.uuid))
            vehicle._on_message(_subscription_ack(vehicle, outgoing.uuid))

        vehicle.client.write_gatt_char = AsyncMock(side_effect=write_then_push_then_ack)

        response, sink = await asyncio.wait_for(
            vehicle._send_with_stream_sink(
                outgoing, "protobuf_message_as_bytes", timeout=1.0
            ),
            timeout=1.0,
        )

        self.assertEqual(response.request_uuid, outgoing.uuid)
        self.assertEqual(
            (await asyncio.wait_for(sink.get(), timeout=0.1)).protobuf_message_as_bytes,
            b"push-data",
        )

    async def test_unregistered_sink_drops_late_pushes(self) -> None:
        vehicle = _make_vehicle()
        subscribe_uuid = randbytes(16)
        sink = vehicle._register_stream_sink(subscribe_uuid)
        vehicle._unregister_stream_sink(subscribe_uuid)

        vehicle._on_message(_subscription_push(vehicle, subscribe_uuid))

        self.assertTrue(sink.empty())
        self.assertTrue(vehicle._queues[DOMAIN].empty())

    async def test_sink_drops_oldest_when_full(self) -> None:
        vehicle = _make_vehicle()
        subscribe_uuid = randbytes(16)
        sink = vehicle._register_stream_sink(subscribe_uuid)

        for _ in range(sink._queue.maxsize + 5):
            vehicle._on_message(_subscription_push(vehicle, subscribe_uuid))

        self.assertEqual(sink.dropped, 5)
        self.assertEqual(sink._queue.qsize(), sink._queue.maxsize)
