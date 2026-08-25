"""Tests for constructing a ``VehicleBluetooth`` with signing explicitly disabled.

Omitting ``key``/``private_key`` keeps the existing behaviour of falling back
to the parent's key and raising if it has none. Passing ``key=None``/
``private_key=None`` explicitly is a distinct, additive path: it constructs
successfully with signing disabled, still receives broadcasts via the
``listen_*`` methods, and raises a clear ``SigningDisabled`` (not a generic
attribute/type error from deep in the signing path) on any operation that
actually needs to sign.
"""

from __future__ import annotations

from typing import Any
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, MagicMock

from cryptography.hazmat.primitives.asymmetric import ec

from tesla_fleet_api.exceptions import SigningDisabled
from tesla_fleet_api.tesla.vehicle.bluetooth import VehicleBluetooth
from tesla_protocol.command.universal_message_pb2 import (
    Destination,
    Domain,
    RoutableMessage,
)
from tesla_protocol.command.vcsec_pb2 import (
    FromVCSECMessage,
    VehicleLockState_E,
    VehicleStatus,
)

VIN = "5YJXCAE43LF123456"


def _status_broadcast(status: VehicleStatus) -> RoutableMessage:
    body = FromVCSECMessage(vehicleStatus=status)
    return RoutableMessage(
        from_destination=Destination(domain=Domain.DOMAIN_VEHICLE_SECURITY),
        protobuf_message_as_bytes=body.SerializeToString(),
    )


class OmittedKeyStillRaisesTests(IsolatedAsyncioTestCase):
    async def test_omitted_key_with_no_parent_key_raises_value_error(self) -> None:
        """Not passing a key at all keeps today's behaviour unchanged."""
        parent = MagicMock()
        parent.private_key = None

        with self.assertRaisesRegex(ValueError, "No private key."):
            VehicleBluetooth(parent, VIN)

    async def test_omitted_key_falls_back_to_parent_key(self) -> None:
        """Not passing a key still inherits the parent's, as before."""
        parent = MagicMock()
        parent.private_key = ec.generate_private_key(ec.SECP256R1())

        vehicle = VehicleBluetooth(parent, VIN)

        self.assertIs(vehicle.private_key, parent.private_key)


class ExplicitNullKeyTests(IsolatedAsyncioTestCase):
    async def test_explicit_null_key_constructs_even_with_no_parent_key(self) -> None:
        """An explicit ``key=None`` disables signing rather than falling back."""
        parent = MagicMock()
        parent.private_key = None

        vehicle = VehicleBluetooth(parent, VIN, key=None)

        self.assertIsNone(vehicle.private_key)

    async def test_explicit_null_key_overrides_an_available_parent_key(self) -> None:
        """``key=None`` disables signing even when the parent does have a key."""
        parent = MagicMock()
        parent.private_key = ec.generate_private_key(ec.SECP256R1())

        vehicle = VehicleBluetooth(parent, VIN, key=None)

        self.assertIsNone(vehicle.private_key)

    async def test_can_still_receive_broadcasts(self) -> None:
        """A key-less vehicle still fans out unsolicited status broadcasts."""
        parent = MagicMock()
        parent.private_key = None
        vehicle = VehicleBluetooth(parent, VIN, key=None)

        seen: list[Any] = []
        vehicle.listen_vehicle_lock_state(seen.append)

        vehicle._on_message(
            _status_broadcast(
                VehicleStatus(
                    vehicleLockState=VehicleLockState_E.VEHICLELOCKSTATE_LOCKED
                )
            )
        )

        self.assertEqual(seen, [VehicleLockState_E.VEHICLELOCKSTATE_LOCKED])


class SignedOperationOnNullKeyTests(IsolatedAsyncioTestCase):
    async def test_signed_command_raises_signing_disabled(self) -> None:
        """A signed operation on a key-less vehicle fails clearly, not deep in the signing path."""
        parent = MagicMock()
        parent.private_key = None
        vehicle = VehicleBluetooth(parent, VIN, key=None)
        vehicle.connect_if_needed = AsyncMock()  # type: ignore[method-assign]
        vehicle._send = AsyncMock()  # type: ignore[method-assign]

        with self.assertRaises(SigningDisabled):
            await vehicle.door_lock()

    async def test_handshake_raises_signing_disabled(self) -> None:
        parent = MagicMock()
        parent.private_key = None
        vehicle = VehicleBluetooth(parent, VIN, key=None)

        with self.assertRaises(SigningDisabled):
            await vehicle.handshakeVehicleSecurity()

    async def test_pair_raises_signing_disabled_without_touching_transport(
        self,
    ) -> None:
        """pair() must fail before it builds/sends a whitelist request.

        A key-less vehicle has an empty ``_public_key``; without this guard
        pair() would proceed to connect and send a malformed whitelist
        request to real hardware instead of failing clearly up front.
        """
        parent = MagicMock()
        parent.private_key = None
        vehicle = VehicleBluetooth(parent, VIN, key=None)
        vehicle.connect_if_needed = AsyncMock()  # type: ignore[method-assign]
        vehicle._send = AsyncMock()  # type: ignore[method-assign]

        with self.assertRaises(SigningDisabled):
            await vehicle.pair()

        vehicle.connect_if_needed.assert_not_awaited()
        vehicle._send.assert_not_awaited()
