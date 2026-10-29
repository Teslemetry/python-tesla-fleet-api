"""Unit tests for V1rTransport login-password handling.

Covers the gateway's undocumented "last 5 characters" convention for the
`/api/login/Basic` customer password - the transport must derive it from
the full gateway/WiFi password rather than require callers to already know
the truncated value.
"""

from __future__ import annotations

from typing import Any

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from tesla_fleet_api.tesla.powerwall.client import PowerwallClient
from tesla_fleet_api.tesla.powerwall.transport import V1rTransport, _customer_password


def _rsa_pem() -> bytes:
    key = rsa.generate_private_key(public_exponent=65537, key_size=1024)
    return key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    )


class _FakeResponse:
    def __init__(self, status: int, json_body: dict[str, Any]) -> None:
        self.status = status
        self._json_body = json_body

    async def __aenter__(self) -> _FakeResponse:
        return self

    async def __aexit__(self, *exc_info: object) -> None:
        return None

    async def json(self) -> dict[str, Any]:
        return self._json_body

    async def text(self) -> str:
        return str(self._json_body)


class _FakeSession:
    def __init__(self, status: int = 200, token: str = "test-token") -> None:
        self.status = status
        self.token = token
        self.sent_payloads: list[dict[str, Any]] = []

    def post(self, url: str, *, json: dict[str, Any], **kwargs: Any) -> _FakeResponse:
        self.sent_payloads.append(json)
        return _FakeResponse(self.status, {"token": self.token})


def test_customer_password_truncates_to_last_5_chars() -> None:
    assert _customer_password("MyWiFiPassword123") == "rd123"


def test_customer_password_is_idempotent_for_already_5_char_input() -> None:
    assert _customer_password("rd123") == "rd123"


async def test_login_sends_last_5_chars_of_full_password() -> None:
    session = _FakeSession()
    transport = V1rTransport(
        host="192.168.91.1",
        password="MyWiFiPassword123",
        rsa_private_key_pem=_rsa_pem(),
        session=session,  # type: ignore[arg-type]
    )

    token = await transport.login()

    assert token == "test-token"
    assert len(session.sent_payloads) == 1
    assert session.sent_payloads[0]["password"] == "rd123"


async def test_legacy_gateway_login_sends_full_password() -> None:
    session = _FakeSession()
    transport = V1rTransport(
        host="192.168.91.1",
        password="MyWiFiPassword123",
        rsa_private_key_pem=_rsa_pem(),
        session=session,  # type: ignore[arg-type]
        legacy_gateway=True,
    )

    await transport.login()

    assert session.sent_payloads[0]["password"] == "MyWiFiPassword123"


async def test_client_legacy_gateway_constructor_sends_full_password() -> None:
    session = _FakeSession()
    default = PowerwallClient(
        gateway_password="MyWiFiPassword123",
        rsa_private_key_pem=_rsa_pem(),
        session=session,  # type: ignore[arg-type]
    )
    legacy = PowerwallClient.legacy_gateway(
        gateway_password="MyWiFiPassword123",
        rsa_private_key_pem=_rsa_pem(),
        session=session,  # type: ignore[arg-type]
    )

    await default._transport.login()
    await legacy._transport.login()

    assert [p["password"] for p in session.sent_payloads] == [
        "rd123",
        "MyWiFiPassword123",
    ]
