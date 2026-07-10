"""Regression tests for ``ReassemblingBuffer`` framing and corruption resync.

Exercises the length-prefixed reassembly directly (no VehicleBluetooth, no
GATT) to lock down: a message split across multiple BLE notification
chunks, multiple complete messages delivered in a single chunk, and
resynchronization after a corrupted/oversized packet using the
``packet_starts`` boundary tracking in ``discard_packet``.
"""

from unittest import TestCase
from unittest.mock import patch

from tesla_fleet_api.tesla.vehicle.bluetooth import ReassemblingBuffer, prependLength
from tesla_fleet_api.tesla.vehicle.proto.universal_message_pb2 import (
    Destination,
    Domain,
    RoutableMessage,
)


def framed(msg: RoutableMessage) -> bytearray:
    """Length-prefix a RoutableMessage the way the vehicle would frame it."""
    return prependLength(msg.SerializeToString())


class ReassemblingBufferTests(TestCase):
    def setUp(self) -> None:
        self.received: list[RoutableMessage] = []
        self.buffer = ReassemblingBuffer(self.received.append)

    def test_single_message_single_chunk(self) -> None:
        msg = RoutableMessage(
            from_destination=Destination(domain=Domain.DOMAIN_INFOTAINMENT)
        )

        self.buffer.receive_data(framed(msg))

        self.assertEqual(len(self.received), 1)
        self.assertEqual(
            self.received[0].from_destination.domain, Domain.DOMAIN_INFOTAINMENT
        )

    def test_message_split_across_multiple_chunks(self) -> None:
        msg = RoutableMessage(
            from_destination=Destination(domain=Domain.DOMAIN_VEHICLE_SECURITY),
            request_uuid=b"0123456789abcdef",
        )
        payload = framed(msg)

        # Simulate GATT MTU fragmentation: deliver a few bytes at a time.
        chunk_size = 5
        for i in range(0, len(payload), chunk_size):
            self.buffer.receive_data(payload[i : i + chunk_size])
            if i + chunk_size < len(payload):
                self.assertEqual(
                    self.received, [], "must not fire callback before full message"
                )

        self.assertEqual(len(self.received), 1)
        self.assertEqual(
            self.received[0].from_destination.domain, Domain.DOMAIN_VEHICLE_SECURITY
        )
        self.assertEqual(self.received[0].request_uuid, b"0123456789abcdef")

    def test_multiple_messages_in_one_chunk(self) -> None:
        first = RoutableMessage(
            from_destination=Destination(domain=Domain.DOMAIN_VEHICLE_SECURITY)
        )
        second = RoutableMessage(
            from_destination=Destination(domain=Domain.DOMAIN_INFOTAINMENT)
        )

        self.buffer.receive_data(framed(first) + framed(second))

        self.assertEqual(len(self.received), 2)
        self.assertEqual(
            self.received[0].from_destination.domain, Domain.DOMAIN_VEHICLE_SECURITY
        )
        self.assertEqual(
            self.received[1].from_destination.domain, Domain.DOMAIN_INFOTAINMENT
        )

    def test_corrupt_packet_resyncs_to_next_packet_boundary(self) -> None:
        good = RoutableMessage(
            from_destination=Destination(domain=Domain.DOMAIN_INFOTAINMENT)
        )

        # A plausible-length header (so it's not caught by the oversized
        # check) whose payload is not a valid RoutableMessage.
        corrupt = prependLength(b"\xff" * 20)

        # Each call to receive_data is one physical BLE notification, so
        # this records two distinct packet_starts entries for resync.
        self.buffer.receive_data(corrupt)
        self.buffer.receive_data(framed(good))

        self.assertEqual(len(self.received), 1)
        self.assertEqual(
            self.received[0].from_destination.domain, Domain.DOMAIN_INFOTAINMENT
        )

    def test_oversized_length_header_discards_and_resyncs(self) -> None:
        good = RoutableMessage(
            from_destination=Destination(domain=Domain.DOMAIN_VEHICLE_SECURITY)
        )

        # Length header claims a message > 1024 bytes - must be treated as
        # corrupt rather than stalling forever waiting for more data.
        oversized_header = bytearray([0xFF, 0xFF]) + b"\x00" * 10

        self.buffer.receive_data(oversized_header)
        self.buffer.receive_data(framed(good))

        self.assertEqual(len(self.received), 1)
        self.assertEqual(
            self.received[0].from_destination.domain, Domain.DOMAIN_VEHICLE_SECURITY
        )

    def test_stale_partial_is_discarded_after_timeout(self) -> None:
        stale = RoutableMessage(
            from_destination=Destination(domain=Domain.DOMAIN_VEHICLE_SECURITY),
            request_uuid=b"0123456789abcdef",
        )
        stale_payload = framed(stale)

        fresh = RoutableMessage(
            from_destination=Destination(domain=Domain.DOMAIN_INFOTAINMENT)
        )

        with patch(
            "tesla_fleet_api.tesla.vehicle.bluetooth.time.monotonic"
        ) as mock_monotonic:
            # Deliver only the first half of `stale` - a dropped chunk mid-message.
            mock_monotonic.return_value = 0.0
            self.buffer.receive_data(stale_payload[: len(stale_payload) // 2])
            self.assertEqual(self.received, [])

            # The next chunk arrives well past the stale-chunk timeout: the
            # partial must be dropped, not prepended to the new message.
            mock_monotonic.return_value = 2.0
            self.buffer.receive_data(framed(fresh))

        self.assertEqual(len(self.received), 1)
        self.assertEqual(
            self.received[0].from_destination.domain, Domain.DOMAIN_INFOTAINMENT
        )

    def test_fast_multi_chunk_message_under_timeout_still_reassembles(self) -> None:
        msg = RoutableMessage(
            from_destination=Destination(domain=Domain.DOMAIN_VEHICLE_SECURITY),
            request_uuid=b"0123456789abcdef",
        )
        payload = framed(msg)
        chunk_size = 5

        with patch(
            "tesla_fleet_api.tesla.vehicle.bluetooth.time.monotonic"
        ) as mock_monotonic:
            # Each chunk arrives 0.1s after the previous one - well under the
            # stale-chunk timeout - so the partial must survive intact.
            clock = 0.0
            for i in range(0, len(payload), chunk_size):
                mock_monotonic.return_value = clock
                self.buffer.receive_data(payload[i : i + chunk_size])
                clock += 0.1

        self.assertEqual(len(self.received), 1)
        self.assertEqual(
            self.received[0].from_destination.domain, Domain.DOMAIN_VEHICLE_SECURITY
        )
        self.assertEqual(self.received[0].request_uuid, b"0123456789abcdef")
