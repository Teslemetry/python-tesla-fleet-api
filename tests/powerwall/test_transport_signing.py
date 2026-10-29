"""Fixed byte vector for the `/tedapi/v1r` signed request.

RSA PKCS#1 v1.5 signing is deterministic, so with a fixed key, envelope, DIN,
clock and message UUID the whole signed `RoutableMessage` is fixed. Any change
to the TLV header, the 12 second LAN TTL or the message layout breaks this test.
"""

from __future__ import annotations

import uuid
from typing import Any
from unittest.mock import patch

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from tesla_protocol.energy_device import signed_message_pb2

from tesla_fleet_api.tesla.powerwall.transport import V1rTransport

# A test key only; it is not registered on any gateway.
TEST_KEY_PEM = b"""-----BEGIN PRIVATE KEY-----
MIICdQIBADANBgkqhkiG9w0BAQEFAASCAl8wggJbAgEAAoGBAJmlOoA/z98lbrJt
SCpsXVPsgRDc2KkclGXGDR+4iMP/Fttoy0Hx+t8q01WIDHCoOpoQv1NwOWg1ycEU
DLvIryyXH4eOrqY+ZWaAqiqyZ+HjMeNhW4HpD43SkquIn9+hosXJaJxfrNvI1h9g
PIxUnqdKQM+zYmhl3p2NxKkpbnQ7AgMBAAECgYB/TSM3d6en37/kHh+Y5sg87MvT
SOhK1d8uo/XjvmWy3vv1NtKSBQgzN6x6RYrpHLnRROcBHw6xhT9wtkgGnrRkGPqu
cKK7w9Dr6jr02IlUL2vUVb2OY1exef9CP40BMfMM5QxqSE2IrG+u6YR+I3dMPPEP
PrJqucOf/Y78MJuUoQJBAMfGCBJKy19ByzP2xv5d//w7o0E8vGZlYdOy8LtYMNeX
4cM74LzZgA9MmDruT+v1tLTwPKAt2HgnDuEA9AYTdU8CQQDE45lrTItafMAnC9a4
x9Zu0PgPl2z3ibtd0k0vTvVhYN7k6+ulRy5EaEPfdSkxSRfAayA/pXDPy/3IIe8I
4S9VAkA6ohnOXJtyGtpsJvriv24ZdtuEkzHsj8b1nmhfZBP5wv8lERb19pRKaT2o
1jco1xWxoWz5ylrlcPlB+sikW+OrAkAu0jUsyBInnZ0QbAdO/+7lgXpMMuVt5GoT
QKysQGmoE6JN7DCoqEm/aNAjNrhqCQjF8HPFzvEJ6WfbjP5MLUjVAkAa4eA/MCuB
ip8rpmlk2gKy5kT48ehO4GSwb168TI+Bkw0hRAwV+4r1STkCJR+z7fWEi+uBn7VI
IZvqjXsKph1j
-----END PRIVATE KEY-----
"""

DIN = "1232100-00-E--TG123456789ABC"
NOW = 1_790_000_000.25
MESSAGE_UUID = bytes(range(16))
# A MessageEnvelope from the customer mobile app client, addressed to DIN.
ENVELOPE = bytes.fromhex(
    "120220011a1e0a1c313233323130302d30302d452d2d5447313233343536373839414243"
)

EXPECTED_SIGNED_REQUEST = bytes.fromhex(
    "320208075224120220011a1e0a1c313233323130302d30302d452d2d54473132"
    "333435363738394142436a9d020a8f010a8c013081890281810099a53a803fcf"
    "df256eb26d482a6c5d53ec8110dcd8a91c9465c60d1fb888c3ff16db68cb41f1"
    "fadf2ad355880c70a83a9a10bf5370396835c9c1140cbbc8af2c971f878eaea6"
    "3e656680aa2ab267e1e331e3615b81e90f8dd292ab889fdfa1a2c5c9689c5fac"
    "dbc8d61f603c8c549ea74a40cfb3626865de9d8dc4a9296e743b02030100013a"
    "88010d8d3bb16a1280016f5fd6a464eeb8e293b9efe76d1036c4fb09ac801dcd"
    "d6aebc3fd06ed15629626f307a1f7cd16cd5fbec82adb9b0b82faaaf9327452f"
    "3d93ebe0b8538b40090900ce9bd0f4f83b3783bd9a33ba97d72ce921cc0fa40c"
    "3b7eb65dea88cd26ef013085b2cf3315caa23a13429ca71b3fd97ee41411d97a"
    "2948117e0e07d5e7c55b9a0310000102030405060708090a0b0c0d0e0f"
)

REPLY_ENVELOPE = b"\x2a\x03\xb2\x02\x00"


class _FakeResponse:
    def __init__(self, body: bytes) -> None:
        self.status = 200
        self._body = body

    async def __aenter__(self) -> _FakeResponse:
        return self

    async def __aexit__(self, *exc_info: object) -> None:
        return None

    async def read(self) -> bytes:
        return self._body


class _FakeSession:
    def __init__(self) -> None:
        self.posted: list[bytes] = []

    def post(self, url: str, *, data: bytes, **kwargs: Any) -> _FakeResponse:
        self.posted.append(data)
        reply = signed_message_pb2.RoutableMessage()
        reply.protobuf_message_as_bytes = REPLY_ENVELOPE
        return _FakeResponse(reply.SerializeToString())


async def _post_fixed_request() -> tuple[bytes, bytes]:
    session = _FakeSession()
    transport = V1rTransport(
        host="192.168.91.1",
        password="MyWiFiPassword123",
        rsa_private_key_pem=TEST_KEY_PEM,
        session=session,  # type: ignore[arg-type]
    )
    with (
        patch("time.time", return_value=NOW),
        patch("uuid.uuid4", return_value=uuid.UUID(bytes=MESSAGE_UUID)),
    ):
        inner = await transport.post_v1r(ENVELOPE, DIN)
    assert len(session.posted) == 1
    return session.posted[0], inner


async def test_signed_request_matches_fixed_byte_vector() -> None:
    posted, inner = await _post_fixed_request()

    assert posted == EXPECTED_SIGNED_REQUEST
    assert inner == REPLY_ENVELOPE


async def test_fixed_vector_signature_verifies_with_12_second_ttl() -> None:
    posted, _ = await _post_fixed_request()
    message = signed_message_pb2.RoutableMessage()
    message.ParseFromString(posted)

    expires_at = 1_790_000_001 + 12
    assert message.signature_data.rsa_data.expires_at == expires_at
    assert message.uuid == MESSAGE_UUID
    assert message.protobuf_message_as_bytes == ENVELOPE

    key = load_pem_private_key(TEST_KEY_PEM, password=None)
    assert isinstance(key, rsa.RSAPrivateKey)
    personalization = DIN.encode("ascii")
    signed_data = (
        bytes([0, 1, 7])  # TAG_SIGNATURE_TYPE = SIGNATURE_TYPE_RSA
        + bytes([1, 1, 7])  # TAG_DOMAIN = DOMAIN_ENERGY_DEVICE
        + bytes([2, len(personalization)])
        + personalization
        + bytes([4, 4])
        + expires_at.to_bytes(4, "big")
        + bytes([255])  # TAG_END
        + ENVELOPE
    )
    # Raises InvalidSignature on a mismatch.
    key.public_key().verify(
        message.signature_data.rsa_data.signature,
        signed_data,
        padding.PKCS1v15(),
        hashes.SHA512(),
    )
