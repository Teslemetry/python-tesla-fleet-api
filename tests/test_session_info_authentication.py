"""Tests for session_info authentication, counter monotonicity, and response
counter replay protection - the signed-command session-establishment path
that the BLE-mocked command tests never exercise (they pre-mark sessions
ready and mock ``_send`` wholesale, so a real ``session_info`` reply never
reaches ``validate_msg``/``Session.commit``).

``GoldenVectorTests`` reproduces the handshake worked example published in
``teslamotors/vehicle-command``'s ``pkg/protocol/protocol.md`` verbatim, so it
is independent of every other test here: if it passes, this library's
session_info HMAC-tag construction matches the authoritative upstream spec
exactly, not just its own internal consistency.

The remaining classes drive a synthetic-but-realistic "fake vehicle" keypair
through the real ``Commands.validate_msg``/``Session.commit`` and, for the
BLE transport, the real (unmocked) ``_send``/``_await_response``/``_handshake``
state machine with only the GATT client faked - modeling VCSEC's real quirk
of leaving the wire-level ``request_uuid`` field empty.
"""

from __future__ import annotations

import hashlib
import hmac
import struct
import time
from typing import Any, cast
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, MagicMock

from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.hashes import SHA256, Hash
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

from tesla_fleet_api.exceptions import (
    NotOnWhitelistFault,
    SessionInfoAuthenticationFault,
    SignedCommandResponseReplayed,
)
from tesla_fleet_api.tesla.vehicle.bluetooth import VehicleBluetooth
from tesla_fleet_api.tesla.vehicle.commands import Commands
from tesla_protocol.command.car_server_pb2 import (
    Action,
    ActionStatus,
    Ping,
    Response,
    VehicleAction,
)
from tesla_protocol.command.car_server_pb2 import (
    OperationStatus_E as InfotainmentOperationStatus_E,
)
from tesla_protocol.command.signatures_pb2 import (
    AES_GCM_Response_Signature_Data,
    HMAC_Signature_Data,
    Session_Info_Status,
    SessionInfo,
    SignatureData,
    SignatureType,
    Tag,
)
from tesla_protocol.command.universal_message_pb2 import (
    Destination,
    Domain,
    RoutableMessage,
)

VIN = "5YJXCAE43LF123456"


class _ConcreteCommands(Commands):
    """Minimal concrete subclass so ``Commands`` can be instantiated directly."""

    _auth_method = "hmac"
    _transport_name = "test"

    async def _send(self, msg, requires, expects_data=True, *, confirm_broadcast=None):
        raise AssertionError("_send should not be called in these tests")


def _make_commands(
    vin: str = VIN, private_key: ec.EllipticCurvePrivateKey | None = None
) -> _ConcreteCommands:
    parent = MagicMock()
    parent.private_key = private_key or ec.generate_private_key(ec.SECP256R1())
    return _ConcreteCommands(parent, vin)


def _public_key_bytes(private_key: ec.EllipticCurvePrivateKey) -> bytes:
    return private_key.public_key().public_bytes(
        encoding=Encoding.X962, format=PublicFormat.UncompressedPoint
    )


def _session_info_tag(
    session_info_key: bytes, vin: str, request_uuid: bytes, session_info_bytes: bytes
) -> bytes:
    """Independently compute the expected session_info_tag (mirrors commands.py)."""
    metadata = bytes(
        [
            Tag.TAG_SIGNATURE_TYPE,
            1,
            SignatureType.SIGNATURE_TYPE_HMAC,
            Tag.TAG_PERSONALIZATION,
            17,
            *vin.encode(),
            Tag.TAG_CHALLENGE,
            len(request_uuid),
            *request_uuid,
            Tag.TAG_END,
        ]
    )
    return hmac.new(
        session_info_key, metadata + session_info_bytes, hashlib.sha256
    ).digest()


def _session_info_reply(
    commands: _ConcreteCommands,
    domain: "Domain.ValueType",
    session_info: SessionInfo,
    request_uuid: bytes,
    *,
    echo_request_uuid: bytes = b"",
    tag_override: bytes | None = None,
    omit_tag: bool = False,
) -> RoutableMessage:
    """Build a session_info reply with a correctly-derived tag, unless overridden."""
    session_info_bytes = session_info.SerializeToString()
    _, _, session_info_key = commands._sessions[domain].keys_for(session_info.publicKey)
    tag = (
        tag_override
        if tag_override is not None
        else _session_info_tag(
            session_info_key, commands.vin, request_uuid, session_info_bytes
        )
    )
    signature_data = SignatureData()
    if not omit_tag:
        signature_data.session_info_tag.CopyFrom(HMAC_Signature_Data(tag=tag))
    return RoutableMessage(
        from_destination=Destination(domain=domain),
        session_info=session_info_bytes,
        request_uuid=echo_request_uuid,
        signature_data=signature_data,
    )


class GoldenVectorTests(IsolatedAsyncioTestCase):
    """Reproduces protocol.md's own published handshake worked example
    (Test keys / Handshake / Response authentication sections) verbatim,
    using its published test keys and intermediate values."""

    CLIENT_PRIVATE_KEY = int(
        "2538CDC29A97C19C1E99A637D6CF4F8C970C118B56EDE1E6323E6D162C4B30DB", 16
    )
    VEHICLE_PUBLIC_KEY = bytes.fromhex(
        "04c7a1f47138486aa4729971494878d33b1a24e39571f748a6e16c5955b3d877d3"
        "a6aaa0e955166474af5d32c410f439a2234137ad1bb085fd4e8813c958f11d97"
    )
    VIN = "5YJ30123456789ABC"
    REQUEST_UUID = bytes.fromhex("1588d5a30eabc6f8fc9a951b11f6fd11")
    SESSION_INFO_BYTES = bytes.fromhex(
        "0806124104c7a1f47138486aa4729971494878d33b1a24e39571f748a6e16c5955"
        "b3d877d3a6aaa0e955166474af5d32c410f439a2234137ad1bb085fd4e8813c958"
        "f11d971a104c463f9cc0d3d26906e982ed224adde6255a0a0000"
    )
    GOLDEN_K = bytes.fromhex("1b2fce19967b79db696f909cff89ea9a")
    GOLDEN_SESSION_INFO_KEY = bytes.fromhex(
        "fceb679ee7bca756fcd441bf238bf2f338629b41d9eb9c67be1b32c9672ce300"
    )
    GOLDEN_TAG = bytes.fromhex(
        "996c1fe38331be138f8039c194b14db2198846ed7d8251e6749284d7b32ea002"
    )

    def _client_private_key(self) -> ec.EllipticCurvePrivateKey:
        return ec.derive_private_key(self.CLIENT_PRIVATE_KEY, ec.SECP256R1())

    def test_shared_key_matches_the_spec_published_k(self) -> None:
        commands = _make_commands(self.VIN, self._client_private_key())
        self.assertEqual(commands.shared_key(self.VEHICLE_PUBLIC_KEY), self.GOLDEN_K)

    def test_session_info_key_matches_the_spec_published_value(self) -> None:
        commands = _make_commands(self.VIN, self._client_private_key())
        domain = Domain.DOMAIN_INFOTAINMENT
        _, _, session_info_key = commands._sessions[domain].keys_for(
            self.VEHICLE_PUBLIC_KEY
        )
        self.assertEqual(session_info_key, self.GOLDEN_SESSION_INFO_KEY)

    def test_authenticates_and_commits_the_spec_published_handshake_reply(self) -> None:
        commands = _make_commands(self.VIN, self._client_private_key())
        domain = Domain.DOMAIN_INFOTAINMENT
        session = commands._sessions[domain]

        reply = RoutableMessage(
            from_destination=Destination(domain=domain),
            session_info=self.SESSION_INFO_BYTES,
            request_uuid=self.REQUEST_UUID,
            signature_data=SignatureData(
                session_info_tag=HMAC_Signature_Data(tag=self.GOLDEN_TAG)
            ),
        )

        commands.validate_msg(reply, self.REQUEST_UUID)

        self.assertTrue(session.ready)
        self.assertEqual(session.counter, 6)
        self.assertEqual(
            session.epoch, bytes.fromhex("4c463f9cc0d3d26906e982ed224adde6")
        )

    def test_a_single_flipped_tag_bit_fails_authentication(self) -> None:
        commands = _make_commands(self.VIN, self._client_private_key())
        domain = Domain.DOMAIN_INFOTAINMENT
        corrupted_tag = bytes([self.GOLDEN_TAG[0] ^ 0x01]) + self.GOLDEN_TAG[1:]

        reply = RoutableMessage(
            from_destination=Destination(domain=domain),
            session_info=self.SESSION_INFO_BYTES,
            request_uuid=self.REQUEST_UUID,
            signature_data=SignatureData(
                session_info_tag=HMAC_Signature_Data(tag=corrupted_tag)
            ),
        )

        with self.assertRaises(SessionInfoAuthenticationFault):
            commands.validate_msg(reply, self.REQUEST_UUID)
        self.assertFalse(commands._sessions[domain].ready)


class SessionInfoTagAuthenticationTests(IsolatedAsyncioTestCase):
    """Unit tests against a synthetic fake-vehicle keypair (not spec-pinned)."""

    def setUp(self) -> None:
        self.commands = _make_commands()
        self.domain = Domain.DOMAIN_VEHICLE_SECURITY
        self.vehicle_key = ec.generate_private_key(ec.SECP256R1())
        self.vehicle_public_key = _public_key_bytes(self.vehicle_key)
        self.request_uuid = b"\x11" * 16

    def _session_info(self, **overrides: Any) -> SessionInfo:
        kwargs: dict[str, Any] = dict(
            counter=100,
            publicKey=self.vehicle_public_key,
            epoch=b"\x01" * 16,
            clock_time=int(time.time()),
            status=Session_Info_Status.SESSION_INFO_STATUS_OK,
        )
        kwargs.update(overrides)
        return SessionInfo(**kwargs)

    def test_rejects_reply_with_no_tag(self) -> None:
        reply = _session_info_reply(
            self.commands,
            self.domain,
            self._session_info(),
            self.request_uuid,
            omit_tag=True,
        )
        with self.assertRaises(SessionInfoAuthenticationFault):
            self.commands.validate_msg(reply, self.request_uuid)
        self.assertFalse(self.commands._sessions[self.domain].ready)

    def test_rejects_reply_with_forged_tag(self) -> None:
        reply = _session_info_reply(
            self.commands,
            self.domain,
            self._session_info(),
            self.request_uuid,
            tag_override=b"\x00" * 32,
        )
        with self.assertRaises(SessionInfoAuthenticationFault):
            self.commands.validate_msg(reply, self.request_uuid)
        self.assertFalse(self.commands._sessions[self.domain].ready)

    def test_rejects_reply_authenticated_against_a_different_request(self) -> None:
        info = self._session_info()
        # Tag is computed for a request we never sent - proves the tag, not
        # just presence, is what's checked.
        reply = _session_info_reply(self.commands, self.domain, info, b"\x99" * 16)
        with self.assertRaises(SessionInfoAuthenticationFault):
            self.commands.validate_msg(reply, self.request_uuid)
        self.assertFalse(self.commands._sessions[self.domain].ready)

    def test_accepts_valid_tag_with_empty_wire_level_request_uuid(self) -> None:
        # The real VCSEC quirk (protocol.md: "request_uuid is typically not
        # populated"): the tag is still bound to our sent request_uuid as
        # TAG_CHALLENGE, so authentication does not depend on the echo field
        # at all. Must never regress into gating acceptance on this field.
        reply = _session_info_reply(
            self.commands,
            self.domain,
            self._session_info(),
            self.request_uuid,
            echo_request_uuid=b"",
        )
        self.commands.validate_msg(reply, self.request_uuid)
        session = self.commands._sessions[self.domain]
        self.assertTrue(session.ready)
        self.assertEqual(session.counter, 100)

    def test_accepts_valid_tag_with_matching_echoed_request_uuid(self) -> None:
        reply = _session_info_reply(
            self.commands,
            self.domain,
            self._session_info(),
            self.request_uuid,
            echo_request_uuid=self.request_uuid,
        )
        self.commands.validate_msg(reply, self.request_uuid)
        self.assertTrue(self.commands._sessions[self.domain].ready)

    def test_tag_is_verified_before_whitelist_status_is_trusted(self) -> None:
        # A forged whitelist-rejection with a bad tag must surface as an
        # authentication failure, not NotOnWhitelistFault - proving the tag
        # check runs strictly before any field of the reply is acted on.
        info = self._session_info(
            status=Session_Info_Status.SESSION_INFO_STATUS_KEY_NOT_ON_WHITELIST
        )
        reply = _session_info_reply(
            self.commands,
            self.domain,
            info,
            self.request_uuid,
            tag_override=b"\x00" * 32,
        )
        with self.assertRaises(SessionInfoAuthenticationFault):
            self.commands.validate_msg(reply, self.request_uuid)

    def test_authenticated_whitelist_rejection_still_raises_not_on_whitelist(
        self,
    ) -> None:
        info = self._session_info(
            status=Session_Info_Status.SESSION_INFO_STATUS_KEY_NOT_ON_WHITELIST
        )
        reply = _session_info_reply(self.commands, self.domain, info, self.request_uuid)
        with self.assertRaises(NotOnWhitelistFault):
            self.commands.validate_msg(reply, self.request_uuid)
        self.assertFalse(self.commands._sessions[self.domain].ready)


class CounterAndClockMonotonicityTests(IsolatedAsyncioTestCase):
    """Covers commands.py's Session.commit: clamp within an epoch, refuse a
    same-epoch clock regression, reset only on an epoch change."""

    def setUp(self) -> None:
        self.commands = _make_commands()
        self.domain = Domain.DOMAIN_VEHICLE_SECURITY
        self.vehicle_key = ec.generate_private_key(ec.SECP256R1())
        self.vehicle_public_key = _public_key_bytes(self.vehicle_key)
        self.session = self.commands._sessions[self.domain]

    def _authenticate(
        self, *, counter: int, epoch: bytes, clock_time: int, request_uuid: bytes
    ) -> None:
        info = SessionInfo(
            counter=counter,
            publicKey=self.vehicle_public_key,
            epoch=epoch,
            clock_time=clock_time,
            status=Session_Info_Status.SESSION_INFO_STATUS_OK,
        )
        reply = _session_info_reply(self.commands, self.domain, info, request_uuid)
        self.commands.validate_msg(reply, request_uuid)

    def test_baseline_establishes_counter_and_epoch(self) -> None:
        self._authenticate(
            counter=100, epoch=b"\x01" * 16, clock_time=1_000, request_uuid=b"\x01" * 16
        )
        self.assertEqual(self.session.counter, 100)
        self.assertEqual(self.session.epoch, b"\x01" * 16)

    def test_same_epoch_lower_counter_and_regressed_clock_is_refused(self) -> None:
        self._authenticate(
            counter=100, epoch=b"\x01" * 16, clock_time=1_000, request_uuid=b"\x01" * 16
        )

        with self.assertRaises(SessionInfoAuthenticationFault):
            self._authenticate(
                counter=5, epoch=b"\x01" * 16, clock_time=900, request_uuid=b"\x02" * 16
            )

        # Neither the counter nor the delta must have moved.
        self.assertEqual(self.session.counter, 100)

    def test_same_epoch_lower_counter_with_non_regressed_clock_clamps_not_rolls_back(
        self,
    ) -> None:
        self._authenticate(
            counter=100, epoch=b"\x01" * 16, clock_time=1_000, request_uuid=b"\x01" * 16
        )

        # Clock moves forward (not a regression) but counter is lower - must
        # clamp to the existing high-water mark, not adopt the lower value.
        self._authenticate(
            counter=5, epoch=b"\x01" * 16, clock_time=1_010, request_uuid=b"\x02" * 16
        )

        self.assertEqual(self.session.counter, 100)

    def test_same_epoch_higher_counter_advances_normally(self) -> None:
        self._authenticate(
            counter=100, epoch=b"\x01" * 16, clock_time=1_000, request_uuid=b"\x01" * 16
        )
        self._authenticate(
            counter=150, epoch=b"\x01" * 16, clock_time=1_010, request_uuid=b"\x02" * 16
        )
        self.assertEqual(self.session.counter, 150)

    def test_epoch_change_resets_counter_even_if_lower(self) -> None:
        self._authenticate(
            counter=100, epoch=b"\x01" * 16, clock_time=1_000, request_uuid=b"\x01" * 16
        )
        self._authenticate(
            counter=3, epoch=b"\x02" * 16, clock_time=1, request_uuid=b"\x02" * 16
        )
        self.assertEqual(self.session.counter, 3)
        self.assertEqual(self.session.epoch, b"\x02" * 16)


class ResponseCounterReplayTests(IsolatedAsyncioTestCase):
    """Covers the AES-GCM response-counter dedup check (protocol.md
    "Counter verification"): a response reusing an already-seen counter for
    this session must be rejected, defending against a captured encrypted
    response being replayed back at the client."""

    def _make_aes_commands(self) -> tuple[Any, Any]:
        class _AesCommands(Commands):
            _auth_method = "aes"
            _transport_name = "test"

            def __init__(self, *args: Any, **kwargs: Any) -> None:
                super().__init__(*args, **kwargs)
                self.next_reply: RoutableMessage | None = None

            async def _send(
                self, msg, requires, expects_data=True, *, confirm_broadcast=None
            ):
                assert self.next_reply is not None
                return self.next_reply

        parent = MagicMock()
        parent.private_key = ec.generate_private_key(ec.SECP256R1())
        commands = _AesCommands(parent, VIN)
        session = commands._sessions[Domain.DOMAIN_INFOTAINMENT]
        session.epoch = b"\x00" * 16
        session.hmac = b"\x00" * 32
        session.delta = 0
        session.sharedKey = b"\x42" * 16
        return commands, session

    def _encrypted_reply(
        self, commands: Any, session: Any, sent_msg: RoutableMessage, counter: int
    ) -> RoutableMessage:
        domain = Domain.DOMAIN_INFOTAINMENT
        body = Response(
            actionStatus=ActionStatus(
                result=InfotainmentOperationStatus_E.OPERATIONSTATUS_OK
            )
        ).SerializeToString()

        request_hash = (
            bytes([SignatureType.SIGNATURE_TYPE_AES_GCM_PERSONALIZED])
            + sent_msg.signature_data.AES_GCM_Personalized_data.tag
        )
        flags = 0
        metadata = bytes(
            [
                Tag.TAG_SIGNATURE_TYPE,
                1,
                SignatureType.SIGNATURE_TYPE_AES_GCM_RESPONSE,
                Tag.TAG_DOMAIN,
                1,
                domain,
                Tag.TAG_PERSONALIZATION,
                17,
                *commands.vin.encode(),
                Tag.TAG_COUNTER,
                4,
                *struct.pack(">I", counter),
                Tag.TAG_FLAGS,
                4,
                *struct.pack(">I", flags),
                Tag.TAG_REQUEST_HASH,
                17,
                *request_hash,
                Tag.TAG_FAULT,
                4,
                *struct.pack(">I", 0),
                Tag.TAG_END,
            ]
        )
        aad = Hash(SHA256())
        aad.update(metadata)
        nonce = b"\x07" * 12
        aesgcm = AESGCM(session.sharedKey)
        ct = aesgcm.encrypt(nonce, body, aad.finalize())
        return RoutableMessage(
            from_destination=Destination(domain=domain),
            protobuf_message_as_bytes=ct[:-16],
            flags=flags,
            signature_data=SignatureData(
                AES_GCM_Response_data=AES_GCM_Response_Signature_Data(
                    nonce=nonce, counter=counter, tag=ct[-16:]
                )
            ),
        )

    async def test_first_response_of_a_session_is_accepted(self) -> None:
        commands, session = self._make_aes_commands()
        sent: list[RoutableMessage] = []

        async def capture_send(
            msg, requires, expects_data=True, *, confirm_broadcast=None
        ):
            sent.append(msg)
            return self._encrypted_reply(commands, session, msg, counter=6)

        commands._send = capture_send  # type: ignore[method-assign]

        result = await commands._sendInfotainment(
            Action(vehicleAction=VehicleAction(ping=Ping(ping_id=0)))
        )
        self.assertTrue(result["response"]["result"])
        self.assertEqual(session.last_response_counter, 6)

    async def test_replayed_response_counter_is_rejected(self) -> None:
        commands, session = self._make_aes_commands()

        async def replay_send(
            msg, requires, expects_data=True, *, confirm_broadcast=None
        ):
            # Always answers with the same counter, simulating a captured
            # response being replayed back regardless of the new request.
            return self._encrypted_reply(commands, session, msg, counter=6)

        commands._send = replay_send  # type: ignore[method-assign]

        await commands._sendInfotainment(
            Action(vehicleAction=VehicleAction(ping=Ping(ping_id=0)))
        )
        self.assertEqual(session.last_response_counter, 6)

        with self.assertRaises(SignedCommandResponseReplayed):
            await commands._sendInfotainment(
                Action(vehicleAction=VehicleAction(ping=Ping(ping_id=0)))
            )

    async def test_increasing_counters_across_commands_are_accepted(self) -> None:
        commands, session = self._make_aes_commands()
        counters = iter([6, 9])

        async def increasing_send(
            msg, requires, expects_data=True, *, confirm_broadcast=None
        ):
            return self._encrypted_reply(commands, session, msg, counter=next(counters))

        commands._send = increasing_send  # type: ignore[method-assign]

        await commands._sendInfotainment(
            Action(vehicleAction=VehicleAction(ping=Ping(ping_id=0)))
        )
        await commands._sendInfotainment(
            Action(vehicleAction=VehicleAction(ping=Ping(ping_id=0)))
        )
        self.assertEqual(session.last_response_counter, 9)


def _make_ble_vehicle() -> VehicleBluetooth[Any]:
    """A VehicleBluetooth with the real handshake/_send state machine but a faked GATT client."""
    parent = MagicMock()
    parent.private_key = ec.generate_private_key(ec.SECP256R1())
    vehicle = VehicleBluetooth(parent, VIN)
    vehicle.connect_if_needed = AsyncMock()  # type: ignore[method-assign]
    vehicle.client = MagicMock()
    vehicle.client.write_gatt_char = AsyncMock()
    return vehicle


class BleHandshakeAuthenticationTests(IsolatedAsyncioTestCase):
    """End-to-end through the real (unmocked) BLE handshake/_send/_await_response
    state machine - only the GATT client is faked - proving the request_uuid
    threading and validate_msg wiring, not just the isolated auth logic."""

    async def test_forged_session_info_is_rejected_and_session_stays_not_ready(
        self,
    ) -> None:
        vehicle = _make_ble_vehicle()
        vehicle._default_timeout = 1.0
        domain = Domain.DOMAIN_VEHICLE_SECURITY
        attacker_key = ec.generate_private_key(ec.SECP256R1())
        attacker_public_key = _public_key_bytes(attacker_key)

        async def deliver_forged_reply(*_: Any) -> None:
            forged_info = SessionInfo(
                counter=1,
                publicKey=attacker_public_key,
                epoch=b"\x09" * 16,
                clock_time=int(time.time()),
                status=Session_Info_Status.SESSION_INFO_STATUS_OK,
            )
            reply = RoutableMessage(
                to_destination=Destination(
                    domain=domain, routing_address=vehicle._from_destination
                ),
                from_destination=Destination(domain=domain),
                session_info=forged_info.SerializeToString(),
                signature_data=SignatureData(
                    session_info_tag=HMAC_Signature_Data(tag=b"\x00" * 32)
                ),
            )
            vehicle._on_message(reply)

        vehicle.client.write_gatt_char = AsyncMock(side_effect=deliver_forged_reply)

        with self.assertRaises(SessionInfoAuthenticationFault):
            await vehicle.handshakeVehicleSecurity()

        self.assertFalse(cast("dict[Any, Any]", vehicle._sessions)[domain].ready)

    async def test_valid_handshake_with_empty_wire_request_uuid_succeeds(self) -> None:
        # Real VCSEC leaves the wire-level request_uuid empty; the handshake
        # must still complete via the session_info_tag alone.
        vehicle = _make_ble_vehicle()
        vehicle._default_timeout = 1.0
        domain = Domain.DOMAIN_VEHICLE_SECURITY
        vehicle_key = ec.generate_private_key(ec.SECP256R1())
        vehicle_public_key = _public_key_bytes(vehicle_key)

        async def deliver_valid_reply(*_: Any) -> None:
            sessions = cast("dict[Any, Any]", vehicle._sessions)
            session = sessions[domain]
            info = SessionInfo(
                counter=6,
                publicKey=vehicle_public_key,
                epoch=b"\x0a" * 16,
                clock_time=int(time.time()),
                status=Session_Info_Status.SESSION_INFO_STATUS_OK,
            )
            info_bytes = info.SerializeToString()
            _, _, session_info_key = session.keys_for(vehicle_public_key)
            # The real request uuid the client just sent is only observable
            # via the outgoing GATT write; the handshake message's uuid is
            # random per-call, so recover it from the session's in-flight
            # queue state is unnecessary - VCSEC's own quirk of never echoing
            # it back means the client authenticates purely off the tag, so
            # any tag computed against *some* uuid should fail unless it's
            # the one actually sent. We fetch it from the write payload.
            sent_uuid = _extract_request_uuid(vehicle.client.write_gatt_char)
            tag = _session_info_tag(
                session_info_key, vehicle.vin, sent_uuid, info_bytes
            )
            reply = RoutableMessage(
                to_destination=Destination(
                    domain=domain, routing_address=vehicle._from_destination
                ),
                from_destination=Destination(domain=domain),
                session_info=info_bytes,
                request_uuid=b"",
                signature_data=SignatureData(
                    session_info_tag=HMAC_Signature_Data(tag=tag)
                ),
            )
            vehicle._on_message(reply)

        vehicle.client.write_gatt_char = AsyncMock(side_effect=deliver_valid_reply)

        await vehicle.handshakeVehicleSecurity()

        sessions = cast("dict[Any, Any]", vehicle._sessions)
        self.assertTrue(sessions[domain].ready)
        self.assertEqual(sessions[domain].counter, 6)


def _extract_request_uuid(write_mock: AsyncMock) -> bytes:
    """Recover the request uuid from the last GATT write this test's handshake sent."""
    payload = bytes(write_mock.call_args.args[1])
    # payload = 2-byte big-endian length prefix followed by the serialized
    # RoutableMessage (see bluetooth.py's prependLength).
    msg = RoutableMessage.FromString(payload[2:])
    return msg.uuid
