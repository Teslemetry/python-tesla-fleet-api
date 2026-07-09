"""Regression tests for VehicleBluetooth._on_message routing and filtering.

Covers VCSEC-vs-INFO domain routing, dropping messages not addressed to us
(broadcast filtering), and the domain KeyError crash fixed in bluetooth.py:
``Domain`` has values (DOMAIN_BROADCAST, DOMAIN_AUTHD, ...) with no entry in
``_queues``, so a message addressed to us but from one of those domains must
be dropped rather than raising and aborting the reassembly loop mid-buffer.
"""

from unittest import TestCase
from unittest.mock import MagicMock

from cryptography.hazmat.primitives.asymmetric import ec

from tesla_fleet_api.tesla.vehicle.bluetooth import VehicleBluetooth
from tesla_fleet_api.tesla.vehicle.proto.universal_message_pb2 import (
    Destination,
    Domain,
    RoutableMessage,
)

VIN = "5YJXCAE43LF123456"


def _make_vehicle() -> VehicleBluetooth:
    parent = MagicMock()
    parent.private_key = ec.generate_private_key(ec.SECP256R1())
    return VehicleBluetooth(parent, VIN)


class OnMessageRoutingTests(TestCase):
    def test_vcsec_reply_routed_to_vehicle_security_queue(self) -> None:
        vehicle = _make_vehicle()
        msg = RoutableMessage(
            to_destination=Destination(routing_address=vehicle._from_destination),
            from_destination=Destination(domain=Domain.DOMAIN_VEHICLE_SECURITY),
        )

        vehicle._on_message(msg)

        self.assertEqual(vehicle._queues[Domain.DOMAIN_VEHICLE_SECURITY].qsize(), 1)
        self.assertEqual(vehicle._queues[Domain.DOMAIN_INFOTAINMENT].qsize(), 0)

    def test_infotainment_reply_routed_to_infotainment_queue(self) -> None:
        vehicle = _make_vehicle()
        msg = RoutableMessage(
            to_destination=Destination(routing_address=vehicle._from_destination),
            from_destination=Destination(domain=Domain.DOMAIN_INFOTAINMENT),
        )

        vehicle._on_message(msg)

        self.assertEqual(vehicle._queues[Domain.DOMAIN_INFOTAINMENT].qsize(), 1)
        self.assertEqual(vehicle._queues[Domain.DOMAIN_VEHICLE_SECURITY].qsize(), 0)

    def test_message_not_addressed_to_us_is_dropped(self) -> None:
        vehicle = _make_vehicle()
        msg = RoutableMessage(
            to_destination=Destination(routing_address=b"someone-elses-address"),
            from_destination=Destination(domain=Domain.DOMAIN_INFOTAINMENT),
        )

        vehicle._on_message(msg)

        self.assertEqual(vehicle._queues[Domain.DOMAIN_INFOTAINMENT].qsize(), 0)
        self.assertEqual(vehicle._queues[Domain.DOMAIN_VEHICLE_SECURITY].qsize(), 0)

    def test_message_addressed_to_us_from_unhandled_domain_is_dropped_not_raised(
        self,
    ) -> None:
        vehicle = _make_vehicle()
        msg = RoutableMessage(
            to_destination=Destination(routing_address=vehicle._from_destination),
            from_destination=Destination(domain=Domain.DOMAIN_BROADCAST),
        )

        # Must not raise KeyError - DOMAIN_BROADCAST has no entry in _queues.
        vehicle._on_message(msg)

        self.assertEqual(vehicle._queues[Domain.DOMAIN_VEHICLE_SECURITY].qsize(), 0)
        self.assertEqual(vehicle._queues[Domain.DOMAIN_INFOTAINMENT].qsize(), 0)

    def test_message_addressed_to_us_from_authd_domain_is_dropped_not_raised(
        self,
    ) -> None:
        vehicle = _make_vehicle()
        msg = RoutableMessage(
            to_destination=Destination(routing_address=vehicle._from_destination),
            from_destination=Destination(domain=Domain.DOMAIN_AUTHD),
        )

        vehicle._on_message(msg)

        self.assertEqual(vehicle._queues[Domain.DOMAIN_VEHICLE_SECURITY].qsize(), 0)
        self.assertEqual(vehicle._queues[Domain.DOMAIN_INFOTAINMENT].qsize(), 0)
