"""Reusable base for BLE command tests: a VehicleBluetooth with a mocked ``_send``.

Feeds canned, already-decrypted ``RoutableMessage`` replies straight past the
real GATT/encryption layer so command-to-proto construction and reply-decoding
are unit-testable with no car and no BLE/GATT connection whatsoever. Both
signed-command sessions are pre-marked ready so ``_command`` never attempts a
real handshake.
"""

from __future__ import annotations

import struct
from typing import Any, cast
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, MagicMock

from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.hashes import SHA256, Hash

from tesla_fleet_api.tesla.vehicle.bluetooth import VehicleBluetooth
from tesla_fleet_api.tesla.vehicle.proto.car_server_pb2 import (
    ActionStatus,
    Response,
)
from tesla_fleet_api.tesla.vehicle.proto.car_server_pb2 import (
    OperationStatus_E as InfotainmentOperationStatus_E,
)
from tesla_fleet_api.tesla.vehicle.proto.signatures_pb2 import SignatureType, Tag
from tesla_fleet_api.tesla.vehicle.proto.universal_message_pb2 import (
    Destination,
    Domain,
    RoutableMessage,
)
from tesla_fleet_api.tesla.vehicle.proto.vcsec_pb2 import (
    CommandStatus,
    FromVCSECMessage,
    VehicleStatus,
)
from tesla_fleet_api.tesla.vehicle.proto.vcsec_pb2 import (
    OperationStatus_E as VcsecOperationStatus_E,
)
from tesla_fleet_api.tesla.vehicle.proto.vehicle_pb2 import VehicleData

VIN = "5YJXCAE43LF123456"


def vcsec_ok_reply() -> RoutableMessage:
    """A canned VCSEC reply as returned by a signed command that succeeded."""
    body = FromVCSECMessage(
        commandStatus=CommandStatus(
            operationStatus=VcsecOperationStatus_E.OPERATIONSTATUS_OK
        )
    )
    return RoutableMessage(
        from_destination=Destination(domain=Domain.DOMAIN_VEHICLE_SECURITY),
        protobuf_message_as_bytes=body.SerializeToString(),
    )


def vcsec_vehicle_status_reply(vehicle_status: VehicleStatus) -> RoutableMessage:
    """A canned VCSEC reply carrying a ``vehicleStatus`` (as returned by an InformationRequest)."""
    body = FromVCSECMessage(vehicleStatus=vehicle_status)
    return RoutableMessage(
        from_destination=Destination(domain=Domain.DOMAIN_VEHICLE_SECURITY),
        protobuf_message_as_bytes=body.SerializeToString(),
    )


def infotainment_action_ok_reply() -> RoutableMessage:
    """A canned infotainment reply as returned by a signed action that succeeded."""
    body = Response(
        actionStatus=ActionStatus(
            result=InfotainmentOperationStatus_E.OPERATIONSTATUS_OK
        )
    )
    return RoutableMessage(
        from_destination=Destination(domain=Domain.DOMAIN_INFOTAINMENT),
        protobuf_message_as_bytes=body.SerializeToString(),
    )


def infotainment_vehicle_data_reply(vehicle_data: VehicleData) -> RoutableMessage:
    """A canned infotainment ``vehicleData`` reply carrying the given proto."""
    body = Response(vehicleData=vehicle_data)
    return RoutableMessage(
        from_destination=Destination(domain=Domain.DOMAIN_INFOTAINMENT),
        protobuf_message_as_bytes=body.SerializeToString(),
    )


class MockedBleTransportTestCase(IsolatedAsyncioTestCase):
    """Base test case providing a ``VehicleBluetooth`` with ``_send`` mocked."""

    VIN = VIN

    def make_vehicle(
        self, verify_commands: bool = False
    ) -> tuple[VehicleBluetooth[Any], AsyncMock]:
        """Build a VehicleBluetooth whose ``_send`` and connection are fully mocked.

        Returns the vehicle plus the ``AsyncMock`` standing in for ``_send`` -
        set ``send.return_value``/``side_effect`` to script replies. Pass
        ``verify_commands=True`` to exercise the opt-in post-timeout state
        verification.
        """
        parent = MagicMock()
        parent.private_key = ec.generate_private_key(ec.SECP256R1())
        vehicle = VehicleBluetooth(parent, self.VIN, verify_commands=verify_commands)

        # Mark both signed-command sessions ready so _command skips the
        # handshake round-trip (which would otherwise also go through _send).
        sessions = cast("dict[int, Any]", getattr(vehicle, "_sessions"))
        for session in sessions.values():
            session.epoch = b"\x00" * 16
            session.hmac = b"\x00" * 32
            session.delta = 0
            session.sharedKey = b"\x00" * 16

        send = AsyncMock()
        setattr(vehicle, "_send", send)
        # connect_if_needed would otherwise attempt a real BLE connection.
        setattr(vehicle, "connect_if_needed", AsyncMock())

        return vehicle, send


def decrypt_sent_command(vehicle: VehicleBluetooth[Any], msg: RoutableMessage) -> bytes:
    """Decrypt the AES-GCM command payload of a ``RoutableMessage`` built by ``_commandAes``.

    Mirrors the AAD ``_commandAes`` builds when encrypting, using the fixed
    ``sharedKey`` ``make_vehicle`` installs, so a test can assert on the
    plaintext command proto that was actually about to be sent to the car.
    """
    domain = msg.to_destination.domain
    sessions = cast("dict[int, Any]", getattr(vehicle, "_sessions"))
    session = sessions[domain]
    assert session.sharedKey is not None
    sig = msg.signature_data.AES_GCM_Personalized_data

    metadata = bytes(
        [
            Tag.TAG_SIGNATURE_TYPE,
            1,
            SignatureType.SIGNATURE_TYPE_AES_GCM_PERSONALIZED,
            Tag.TAG_DOMAIN,
            1,
            domain,
            Tag.TAG_PERSONALIZATION,
            17,
            *vehicle.vin.encode(),
            Tag.TAG_EPOCH,
            len(sig.epoch),
            *sig.epoch,
            Tag.TAG_EXPIRES_AT,
            4,
            *struct.pack(">I", sig.expires_at),
            Tag.TAG_COUNTER,
            4,
            *struct.pack(">I", sig.counter),
            Tag.TAG_FLAGS,
            4,
            *struct.pack(">I", msg.flags),
            Tag.TAG_END,
        ]
    )

    aad = Hash(SHA256())
    aad.update(metadata)
    aesgcm = AESGCM(session.sharedKey)
    return aesgcm.decrypt(
        sig.nonce, msg.protobuf_message_as_bytes + sig.tag, aad.finalize()
    )
