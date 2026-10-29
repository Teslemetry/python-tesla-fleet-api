"""Tests for the client-signed energy ``device_command`` transport.

A site built with ``private_key`` and ``din`` signs every device command except
the four pre-pairing reads and posts it to ``device_command``: Tesla's cloud
answered 400 to every other unsigned command on a live Powerwall 3. Those four
stay on the unsigned ``grpc_command`` path, and a site without a key behaves as
before.
"""

from __future__ import annotations

import base64
import struct
from typing import Any
from unittest import IsolatedAsyncioTestCase, TestCase
from unittest.mock import AsyncMock

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, padding, rsa
from tesla_protocol.energy_device import (
    authorization_types_pb2,
    signed_message_pb2,
    transport_pb2,
)

from tesla_fleet_api.const import EnergyIslandMode, Method
from tesla_fleet_api.exceptions import (
    DeviceUnexpectedResponse,
    InvalidCommand,
    SignedCommandRequired,
)
from tesla_fleet_api.router import EnergySiteRouter
from tesla_fleet_api.tesla.energy_signing import (
    ENERGY_SIGNATURE_TTL_SECONDS,
    EnergyDeviceSigner,
)
from tesla_fleet_api.tesla.energysite import EnergySite, EnergySites
from tesla_fleet_api.teslemetry.energysite import (
    TeslemetryEnergySite,
    TeslemetryEnergySites,
)

SITE_ID = 12345
DIN = "1232100-00-E--TG123456789ABC"
NOW = 1_790_000_000.25
MESSAGE_UUID = bytes(range(16))

# A test key only; it is not registered on any gateway.
TEST_KEY = rsa.generate_private_key(public_exponent=65537, key_size=2048)


def _expected_signed_data(din: str, expires_at: int, envelope: bytes) -> bytes:
    """The TLV header from the protocol, written out byte by byte."""
    personalization = din.encode("ascii")
    return (
        bytes([0, 1, 7])  # TAG_SIGNATURE_TYPE = SIGNATURE_TYPE_RSA
        + bytes([1, 1, 7])  # TAG_DOMAIN = DOMAIN_ENERGY_DEVICE
        + bytes([2, len(personalization)])
        + personalization  # TAG_PERSONALIZATION = DIN
        + bytes([4, 4])
        + struct.pack(">I", expires_at)  # TAG_EXPIRES_AT
        + bytes([255])  # TAG_END
        + envelope
    )


def _decode(routable_message: bytes) -> signed_message_pb2.RoutableMessage:
    message = signed_message_pb2.RoutableMessage()
    message.ParseFromString(routable_message)
    return message


def _verify(message: signed_message_pb2.RoutableMessage, din: str) -> None:
    """Raise ``InvalidSignature`` unless the message is signed by TEST_KEY for ``din``."""
    TEST_KEY.public_key().verify(
        message.signature_data.rsa_data.signature,
        _expected_signed_data(
            din,
            message.signature_data.rsa_data.expires_at,
            message.protobuf_message_as_bytes,
        ),
        padding.PKCS1v15(),
        hashes.SHA512(),
    )


def _envelope(
    message: signed_message_pb2.RoutableMessage,
) -> transport_pb2.MessageEnvelope:
    envelope = transport_pb2.MessageEnvelope()
    envelope.ParseFromString(message.protobuf_message_as_bytes)
    return envelope


# (method, args, category, request field) for every device command that is
# signed when the site has a key.
SIGNED_COMMANDS: list[tuple[str, tuple[Any, ...], str, str]] = [
    ("wifi_scan", (), "common", "wifi_scan_request"),
    ("get_device_cert", (), "common", "device_cert_request"),
    ("get_cellular_info", (), "common", "get_cellular_info_request"),
    ("check_for_update", (), "common", "check_for_update_request"),
    ("check_for_update_urgency", (), "common", "check_for_update_urgency_request"),
    ("check_internet", (), "common", "check_internet_request"),
    ("set_local_site_config", (), "common", "set_local_site_config_request"),
    (
        "add_authorized_client",
        (b"key",),
        "authorization",
        "add_authorized_client_request",
    ),
    (
        "remove_authorized_client",
        (b"key",),
        "authorization",
        "remove_authorized_client_request",
    ),
    ("get_backup_events", (), "teg", "get_backup_events_request"),
    ("schedule_backup_event", (), "teg", "schedule_manual_backup_event_request"),
    ("cancel_backup_event", (), "teg", "cancel_manual_backup_event_request"),
    ("get_teg_config", (), "teg", "get_config_request"),
    ("dispatch_battery_power", (-2000, 120), "teg", "dispatch_battery_power_request"),
    ("resume_battery_operation", (), "teg", "dispatch_battery_power_request"),
    ("set_island_mode", (EnergyIslandMode.ON_GRID,), "teg", "set_island_mode_request"),
]

# The pre-pairing reads Tesla's cloud accepts unsigned.
UNSIGNED_COMMANDS: list[tuple[str, str, str]] = [
    ("get_system_info", "common", "get_system_info_request"),
    ("raw_networking_status", "common", "get_networking_status_request"),
    (
        "get_signed_commands_public_key",
        "authorization",
        "get_signed_commands_public_key_request",
    ),
    ("list_authorized_clients", "authorization", "list_authorized_clients_request"),
]


def _make_site(
    cls: type[EnergySite], private_key: rsa.RSAPrivateKey | None = TEST_KEY
) -> tuple[EnergySite, AsyncMock]:
    request_mock: AsyncMock = AsyncMock(return_value={"response": "AA=="})
    parent = AsyncMock()
    parent._request = request_mock
    din = DIN if private_key is not None else None
    return cls(parent, SITE_ID, private_key=private_key, din=din), request_mock


def _sent(request_mock: AsyncMock) -> tuple[str, dict[str, Any]]:
    request_mock.assert_awaited_once()
    call = request_mock.await_args
    assert call is not None
    method, path = call.args
    assert method == Method.POST
    return path, call.kwargs["json"]


class EnergyDeviceSignerTests(TestCase):
    def test_signed_message_layout(self) -> None:
        signer = EnergyDeviceSigner(TEST_KEY)
        envelope = signer.envelope(
            DIN, "teg", "set_island_mode_request", {"mode": 6, "force": True}
        )
        message = _decode(
            signer.sign(envelope, DIN, now=NOW, message_uuid=MESSAGE_UUID)
        )

        self.assertEqual(
            message.to_destination.domain, signed_message_pb2.DOMAIN_ENERGY_DEVICE
        )
        self.assertEqual(message.uuid, MESSAGE_UUID)
        self.assertEqual(message.protobuf_message_as_bytes, envelope)
        # expires_at rounds the clock up, then adds the 30 s TTL.
        self.assertEqual(ENERGY_SIGNATURE_TTL_SECONDS, 30)
        self.assertEqual(message.signature_data.rsa_data.expires_at, 1_790_000_001 + 30)
        self.assertEqual(
            message.signature_data.signer_identity.public_key,
            TEST_KEY.public_key().public_bytes(
                serialization.Encoding.DER, serialization.PublicFormat.PKCS1
            ),
        )
        _verify(message, DIN)

    def test_signature_is_personalised_to_the_din(self) -> None:
        signer = EnergyDeviceSigner(TEST_KEY)
        envelope = signer.envelope(DIN, "teg", "get_backup_events_request")
        message = _decode(signer.sign(envelope, DIN, now=NOW))
        with self.assertRaises(InvalidSignature):
            _verify(message, "1232100-00-E--TG000000000000")

    def test_envelope_header_and_payload(self) -> None:
        envelope = transport_pb2.MessageEnvelope()
        envelope.ParseFromString(
            EnergyDeviceSigner.envelope(
                DIN, "teg", "set_island_mode_request", {"mode": 6, "force": True}
            )
        )
        self.assertEqual(
            envelope.sender.authorized_client,
            authorization_types_pb2.AUTHORIZED_CLIENT_TYPE_CUSTOMER_MOBILE_APP,
        )
        self.assertEqual(envelope.recipient.din, DIN)
        # The envelope proven on the cloud path left delivery_channel unset.
        self.assertEqual(
            envelope.delivery_channel, transport_pb2.DELIVERY_CHANNEL_INVALID
        )
        self.assertEqual(envelope.teg.set_island_mode_request.mode, 6)
        self.assertTrue(envelope.teg.set_island_mode_request.force)

    def test_empty_request_sets_the_payload(self) -> None:
        envelope = transport_pb2.MessageEnvelope()
        envelope.ParseFromString(
            EnergyDeviceSigner.envelope(DIN, "teg", "get_config_request")
        )
        self.assertEqual(envelope.WhichOneof("payload"), "teg")
        self.assertEqual(envelope.teg.WhichOneof("message"), "get_config_request")

    def test_each_message_gets_a_fresh_uuid(self) -> None:
        signer = EnergyDeviceSigner(TEST_KEY)
        envelope = signer.envelope(DIN, "teg", "get_config_request")
        self.assertNotEqual(
            _decode(signer.sign(envelope, DIN)).uuid,
            _decode(signer.sign(envelope, DIN)).uuid,
        )

    def test_rejects_an_ecc_key(self) -> None:
        with self.assertRaises(TypeError):
            EnergyDeviceSigner(ec.generate_private_key(ec.SECP256R1()))  # type: ignore[arg-type]


class SigningKeyConstructorTests(TestCase):
    def test_key_requires_din(self) -> None:
        parent = AsyncMock()
        with self.assertRaises(ValueError):
            EnergySite(parent, SITE_ID, private_key=TEST_KEY)

    def test_create_passes_key_and_din(self) -> None:
        parent = AsyncMock()
        for sites in (EnergySites(parent), TeslemetryEnergySites(parent)):
            with self.subTest(sites=type(sites).__name__):
                site = sites.create(SITE_ID, private_key=TEST_KEY, din=DIN)
                self.assertEqual(site.din, DIN)
                self.assertIsNotNone(site._signer)  # pyright: ignore[reportPrivateUsage]
                self.assertIsNone(sites.create(SITE_ID + 1)._signer)  # pyright: ignore[reportPrivateUsage]


class FleetSignedTransportTests(IsolatedAsyncioTestCase):
    async def test_set_island_mode_posts_signed_device_command(self) -> None:
        site, request_mock = _make_site(EnergySite)
        await site.set_island_mode(EnergyIslandMode.OFF_GRID, force=True)

        path, body = _sent(request_mock)
        self.assertEqual(path, f"api/1/energy_sites/{SITE_ID}/device_command")
        # Tesla requires the body inside "data" and identifier_type as an int.
        self.assertEqual(list(body), ["data"])
        data = body["data"]
        self.assertEqual(data["identifier_type"], 1)
        self.assertIsInstance(data["identifier_type"], int)
        self.assertEqual(data["target_id"], DIN)
        message = _decode(base64.b64decode(data["routable_message"]))
        _verify(message, DIN)
        request = _envelope(message).teg.set_island_mode_request
        self.assertEqual(request.mode, EnergyIslandMode.OFF_GRID)
        self.assertTrue(request.force)

    async def test_go_off_grid_forces_and_reconnect_does_not(self) -> None:
        site, request_mock = _make_site(EnergySite)
        await site.go_off_grid()
        message = _decode(
            base64.b64decode(_sent(request_mock)[1]["data"]["routable_message"])
        )
        request = _envelope(message).teg.set_island_mode_request
        self.assertEqual(request.mode, EnergyIslandMode.OFF_GRID)
        self.assertTrue(request.force)

        request_mock.reset_mock()
        await site.reconnect_grid()
        message = _decode(
            base64.b64decode(_sent(request_mock)[1]["data"]["routable_message"])
        )
        request = _envelope(message).teg.set_island_mode_request
        self.assertEqual(request.mode, EnergyIslandMode.ON_GRID)
        self.assertFalse(request.force)

    async def test_island_mode_without_key_still_raises(self) -> None:
        site, request_mock = _make_site(EnergySite, private_key=None)
        for call in (
            lambda: site.set_island_mode(EnergyIslandMode.OFF_GRID),
            site.go_off_grid,
            site.reconnect_grid,
        ):
            with self.assertRaises(SignedCommandRequired):
                await call()
        request_mock.assert_not_called()

    async def test_device_commands_go_signed_with_a_key(self) -> None:
        for name, args, category, request_field in SIGNED_COMMANDS:
            with self.subTest(name=name):
                site, request_mock = _make_site(EnergySite)
                await getattr(site, name)(*args)
                path, body = _sent(request_mock)
                self.assertEqual(path, f"api/1/energy_sites/{SITE_ID}/device_command")
                message = _decode(base64.b64decode(body["data"]["routable_message"]))
                _verify(message, DIN)
                self.assertEqual(
                    getattr(_envelope(message), category).WhichOneof("message"),
                    request_field,
                )

    async def test_device_commands_without_a_key_stay_unsigned(self) -> None:
        for name, args, category, request_field in SIGNED_COMMANDS:
            if name == "set_island_mode":
                continue
            with self.subTest(name=name):
                site, request_mock = _make_site(EnergySite, private_key=None)
                await getattr(site, name)(*args)
                path, body = _sent(request_mock)
                self.assertEqual(path, f"api/1/energy_sites/{SITE_ID}/command")
                self.assertEqual(body["command_type"], "grpc_command")
                self.assertEqual(
                    list(body["command_properties"]["message"][category]),
                    [request_field],
                )

    async def test_dispatch_with_key_signs_the_setpoint(self) -> None:
        site, request_mock = _make_site(EnergySite)
        await site.dispatch_battery_power(-2000, 120)
        message = _decode(
            base64.b64decode(_sent(request_mock)[1]["data"]["routable_message"])
        )
        request = _envelope(message).teg.dispatch_battery_power_request
        self.assertTrue(request.HasField("real_power"))
        self.assertEqual(request.real_power.power_watts, -2000)
        self.assertEqual(request.real_power.duration_seconds, 120)

        request_mock.reset_mock()
        await site.resume_battery_operation()
        message = _decode(
            base64.b64decode(_sent(request_mock)[1]["data"]["routable_message"])
        )
        request = _envelope(message).teg.dispatch_battery_power_request
        self.assertTrue(request.HasField("resume_device_mode"))
        self.assertFalse(request.HasField("real_power"))

    async def test_signed_add_authorized_client_uses_proto_field_names(self) -> None:
        site, request_mock = _make_site(EnergySite)
        await site.add_authorized_client(b"key", description="HA")
        message = _decode(
            base64.b64decode(_sent(request_mock)[1]["data"]["routable_message"])
        )
        request = _envelope(message).authorization.add_authorized_client_request
        self.assertEqual(request.public_key, b"key")
        self.assertEqual(request.description, "HA")
        self.assertEqual(
            request.type,
            authorization_types_pb2.AUTHORIZED_CLIENT_TYPE_CUSTOMER_MOBILE_APP,
        )

    async def test_pre_pairing_reads_stay_unsigned_with_a_key(self) -> None:
        for name, category, request_field in UNSIGNED_COMMANDS:
            with self.subTest(name=name):
                site, request_mock = _make_site(EnergySite)
                await getattr(site, name)()
                path, body = _sent(request_mock)
                self.assertEqual(path, f"api/1/energy_sites/{SITE_ID}/command")
                self.assertEqual(body["command_type"], "grpc_command")
                self.assertEqual(
                    body["command_properties"]["message"],
                    {category: {request_field: {}}},
                )


class TeslemetrySignedTransportTests(IsolatedAsyncioTestCase):
    async def test_set_island_mode_with_key_signs_through_super(self) -> None:
        site, request_mock = _make_site(TeslemetryEnergySite)
        await site.go_off_grid()

        path, body = _sent(request_mock)
        self.assertEqual(path, f"api/1/energy_sites/{SITE_ID}/device_command")
        # Teslemetry takes the flat body and adds Tesla's "data" wrapper.
        self.assertEqual(
            sorted(body), ["identifier_type", "routable_message", "target_id"]
        )
        self.assertEqual(body["identifier_type"], 1)
        self.assertEqual(body["target_id"], DIN)
        message = _decode(base64.b64decode(body["routable_message"]))
        _verify(message, DIN)
        request = _envelope(message).teg.set_island_mode_request
        self.assertEqual(request.mode, EnergyIslandMode.OFF_GRID)
        self.assertTrue(request.force)

    async def test_device_commands_with_key_sign_through_super(self) -> None:
        for name, args, category, request_field in SIGNED_COMMANDS:
            with self.subTest(name=name):
                site, request_mock = _make_site(TeslemetryEnergySite)
                await getattr(site, name)(*args)
                path, body = _sent(request_mock)
                self.assertEqual(path, f"api/1/energy_sites/{SITE_ID}/device_command")
                message = _decode(base64.b64decode(body["routable_message"]))
                _verify(message, DIN)
                self.assertEqual(
                    getattr(_envelope(message), category).WhichOneof("message"),
                    request_field,
                )

    async def test_island_mode_without_key_uses_the_server_signed_route(self) -> None:
        calls: list[tuple[str, tuple[Any, ...], dict[str, Any]]] = [
            ("go_off_grid", (), {"mode": 6, "force": True}),
            ("reconnect_grid", (), {"mode": 1}),
            (
                "set_island_mode",
                (EnergyIslandMode.ON_GRID, False),
                {"mode": 1, "force": False},
            ),
        ]
        for name, args, body in calls:
            with self.subTest(name=name):
                site, request_mock = _make_site(TeslemetryEnergySite, private_key=None)
                await getattr(site, name)(*args)
                request_mock.assert_awaited_once_with(
                    Method.POST,
                    f"api/1/energy_sites/{SITE_ID}/command/set_island_mode",
                    json=body,
                )

    async def test_reads_without_key_use_the_server_signed_routes(self) -> None:
        for name, route in (
            ("get_backup_events", "backup_events"),
            ("get_teg_config", "config"),
        ):
            with self.subTest(name=name):
                site, request_mock = _make_site(TeslemetryEnergySite, private_key=None)
                await getattr(site, name)()
                request_mock.assert_awaited_once_with(
                    Method.GET, f"api/1/energy_sites/{SITE_ID}/command/{route}"
                )

    async def test_routes_without_key(self) -> None:
        calls: list[tuple[str, tuple[Any, ...], str]] = [
            ("dispatch_battery_power", (5000, 60), "dispatch_battery_power"),
            ("resume_battery_operation", (), "resume_battery_operation"),
            ("add_authorized_client", (), "add_authorized_client"),
            ("remove_authorized_client", (b"key",), "remove_authorized_client"),
        ]
        for name, args, route in calls:
            with self.subTest(name=name):
                site, request_mock = _make_site(TeslemetryEnergySite, private_key=None)
                await getattr(site, name)(*args)
                request_mock.assert_awaited_once()
                call = request_mock.await_args
                assert call is not None
                self.assertEqual(
                    call.args,
                    (Method.POST, f"api/1/energy_sites/{SITE_ID}/command/{route}"),
                )

    async def test_add_authorized_client_with_key_but_no_public_key_uses_route(
        self,
    ) -> None:
        # Without a public key the route registers Teslemetry's own key, which
        # the client key cannot sign for.
        site, request_mock = _make_site(TeslemetryEnergySite)
        assert isinstance(site, TeslemetryEnergySite)
        await site.add_authorized_client()
        path, _ = _sent(request_mock)
        self.assertEqual(
            path, f"api/1/energy_sites/{SITE_ID}/command/add_authorized_client"
        )

    async def test_pre_pairing_routes_stay_unsigned_with_a_key(self) -> None:
        for name, route in (
            ("get_networking_status", "networking_status"),
            ("list_authorized_clients", "authorized_clients"),
            ("get_system_info", "system_info"),
            ("raw_networking_status", "networking_status"),
            ("get_signed_commands_public_key", "signed_commands_public_key"),
        ):
            with self.subTest(name=name):
                site, request_mock = _make_site(TeslemetryEnergySite)
                await getattr(site, name)()
                request_mock.assert_awaited_once_with(
                    Method.GET, f"api/1/energy_sites/{SITE_ID}/command/{route}"
                )


def _reply(envelope: transport_pb2.MessageEnvelope) -> dict[str, Any]:
    """A ``device_command`` reply, shaped as captured live on 2026-10-29."""
    return {
        "response": {
            "request_id": "546681d7ff2f1fd5c72a543415a8fe1f",
            "message_envelope_as_bytes": base64.b64encode(
                envelope.SerializeToString()
            ).decode("ascii"),
        }
    }


def _error_reply(code: int, message: str) -> dict[str, Any]:
    envelope = transport_pb2.MessageEnvelope()
    envelope.common.error_response.status.code = code
    envelope.common.error_response.status.message = message
    return _reply(envelope)


class SignedReplyDecodeTests(IsolatedAsyncioTestCase):
    async def test_out_of_range_refusal_raises(self) -> None:
        for cls in (EnergySite, TeslemetryEnergySite):
            with self.subTest(cls=cls.__name__):
                site, request_mock = _make_site(cls)
                request_mock.return_value = _error_reply(
                    11, "power 11000.000000 exceeds discharge limit 10000"
                )
                with self.assertRaises(DeviceUnexpectedResponse) as ctx:
                    await site.dispatch_battery_power(11000, 30)
                self.assertEqual(
                    ctx.exception.data,
                    {
                        "code": 11,
                        "message": "power 11000.000000 exceeds discharge limit 10000",
                    },
                )

    async def test_unimplemented_raises_invalid_command(self) -> None:
        site, request_mock = _make_site(EnergySite)
        request_mock.return_value = _error_reply(12, "")
        with self.assertRaises(InvalidCommand) as ctx:
            await site.get_teg_config()
        self.assertEqual(ctx.exception.data, {"code": 12, "message": ""})

    async def test_ack_is_returned_unchanged(self) -> None:
        site, request_mock = _make_site(EnergySite)
        envelope = transport_pb2.MessageEnvelope()
        envelope.teg.dispatch_battery_power_response.SetInParent()
        reply = _reply(envelope)
        self.assertEqual(reply["response"]["message_envelope_as_bytes"], "KgOyAgA=")
        request_mock.return_value = reply
        self.assertIs(await site.dispatch_battery_power(-2000, 120), reply)


class _LocalPowerwallSite:
    """A local backend that cannot reach the gateway."""

    def __init__(self) -> None:
        self.calls: list[str] = []

    async def go_off_grid(self) -> None:
        self.calls.append("go_off_grid")
        raise ConnectionError("local unreachable")


class RouterSignedTransportTests(IsolatedAsyncioTestCase):
    async def test_router_falls_back_to_signed_cloud(self) -> None:
        for cls in (EnergySite, TeslemetryEnergySite):
            with self.subTest(cls=cls.__name__):
                local = _LocalPowerwallSite()
                cloud, request_mock = _make_site(cls)
                router = EnergySiteRouter(local, cloud)

                await router.go_off_grid()

                self.assertEqual(local.calls, ["go_off_grid"])
                path, _ = _sent(request_mock)
                self.assertEqual(path, f"api/1/energy_sites/{SITE_ID}/device_command")
