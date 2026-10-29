"""Async RSA-signed transport for the Powerwall 3 `/tedapi/v1r` endpoint.

`/tedapi/v1r` authenticates each request with a detached RSA-PKCS1v15 + SHA-512
signature over a TLV envelope (signature type, domain, DIN personalization,
expires-at), embedded in a Tesla `RoutableMessage` protobuf. The RSA key pair
is registered out-of-band — typically via the Tesla Fleet API — and the
private key bytes are passed in here.

This module owns nothing user-visible above the wire format: HTTP plumbing,
request signing, fault decoding, bearer-token lifecycle. The high-level
:mod:`aiopowerwall.client` builds on top of it.
"""

from __future__ import annotations

import asyncio
import gzip
import logging
import math
import re
import struct
import time
import uuid
from contextlib import suppress
from typing import Any, Final

import aiohttp
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from tesla_protocol.energy_device import signed_message_pb2

from .exceptions import (
    PowerwallAuthenticationError,
    PowerwallConnectionError,
    PowerwallFaultError,
    PowerwallProtocolError,
    PowerwallRateLimitError,
)

_LOGGER = logging.getLogger(__name__)

# v1r signature TLV tag identifiers — signed_message_pb2, enum Tag.
_TAG_SIGNATURE_TYPE: Final = signed_message_pb2.TAG_SIGNATURE_TYPE
_TAG_DOMAIN: Final = signed_message_pb2.TAG_DOMAIN
_TAG_PERSONALIZATION: Final = signed_message_pb2.TAG_PERSONALIZATION
_TAG_EXPIRES_AT: Final = signed_message_pb2.TAG_EXPIRES_AT
_TAG_END: Final = signed_message_pb2.TAG_END

_SIGNATURE_TYPE_RSA: Final = signed_message_pb2.SIGNATURE_TYPE_RSA
_DOMAIN_ENERGY_DEVICE: Final = signed_message_pb2.DOMAIN_ENERGY_DEVICE

# Signed messages must be consumed by the gateway within this window.
_SIGNATURE_TTL_SECONDS: Final = 12

_RATE_LIMIT_STATUSES: Final = frozenset({429, 503})

# The gateway signals a rejected/unverified RSA key by returning HTTP 200 with
# a placeholder string in place of a real payload. The exact wording and casing
# vary across firmware ("v1r: client authorization not verified",
# "Client authorization not verified", …), so match the stable core phrase
# case-insensitively. `re.search` on the raw bytes avoids allocating a
# lowercased copy of large (~100 KB) success payloads on every call.
_AUTH_NOT_VERIFIED_RE: Final = re.compile(rb"authorization not verified", re.IGNORECASE)


def _decompress(content: bytes) -> bytes:
    """Transparently decompress gzipped responses (firmware 25.42.2+)."""
    if len(content) > 2 and content[:2] == b"\x1f\x8b":
        with suppress(OSError):
            return gzip.decompress(content)
    return content


def _tlv(tag: int, value: bytes) -> bytes:
    """Encode a single tag-length-value entry."""
    return bytes([tag, len(value)]) + value


def _customer_password(gateway_password: str) -> str:
    """Derive the `/api/login/Basic` "customer" password from the gateway password.

    The gateway's local v1r login accepts only the *last 5 characters* of the
    gateway/WiFi password, not the full value - an undocumented Tesla
    convention that other local Powerwall clients (e.g. pypowerwall) already
    auto-derive rather than require callers to know out-of-band.
    """
    return gateway_password[-5:]


class V1rTransport:
    """RSA-signed wire transport for `/tedapi/v1r`.

    The transport is stateless apart from a cached bearer token. Concurrent
    calls share the underlying :class:`aiohttp.ClientSession`; signing is
    CPU-bound and is offloaded to a thread to avoid blocking the event loop.
    """

    def __init__(
        self,
        host: str,
        password: str,
        rsa_private_key_pem: bytes,
        *,
        session: aiohttp.ClientSession,
        timeout: float = 5.0,
        legacy_gateway: bool = False,
    ) -> None:
        self._host = host
        # Early Gateway 1 (Powerwall 2) units reject the truncated password
        # and need the full value.
        self._password = password if legacy_gateway else _customer_password(password)
        self._session = session
        self._timeout = aiohttp.ClientTimeout(total=timeout)
        self._token: str | None = None
        self._token_lock = asyncio.Lock()
        self._private_key = self._load_private_key(rsa_private_key_pem)
        # PKCS1 DER of the public key — sent as the v1r KeyIdentity so the
        # gateway can look up the registered key.
        self._public_key_der: bytes = self._private_key.public_key().public_bytes(
            serialization.Encoding.DER,
            serialization.PublicFormat.PKCS1,
        )

    # ── Public API ──────────────────────────────────────────────────────────

    @property
    def host(self) -> str:
        return self._host

    @property
    def has_token(self) -> bool:
        return self._token is not None

    async def login(self) -> str:
        """Acquire a fresh bearer token via `/api/login/Basic`.

        Raises :class:`PowerwallAuthenticationError` on bad credentials and
        :class:`PowerwallConnectionError` on transport failure.
        """
        url = f"https://{self._host}/api/login/Basic"
        payload: dict[str, Any] = {
            "username": "customer",
            "password": self._password,
            "email": "customer@customer.domain",
            "clientInfo": {"timezone": "America/Chicago"},
        }
        try:
            async with self._session.post(
                url, json=payload, ssl=False, timeout=self._timeout
            ) as resp:
                if resp.status in (401, 403):
                    raise PowerwallAuthenticationError(
                        f"Login rejected ({resp.status}): check the gateway password"
                    )
                if resp.status in _RATE_LIMIT_STATUSES:
                    raise PowerwallRateLimitError(
                        f"Rate-limited by gateway on login (status {resp.status})"
                    )
                if resp.status != 200:
                    body = await resp.text()
                    raise PowerwallProtocolError(
                        f"Login failed ({resp.status}): {body[:200]}"
                    )
                data = await resp.json()
        except aiohttp.ClientError as err:
            raise PowerwallConnectionError(f"Login transport error: {err}") from err
        except TimeoutError as err:
            raise PowerwallConnectionError("Login timed out") from err

        token = data.get("token") if isinstance(data, dict) else None
        if not isinstance(token, str) or not token:
            raise PowerwallProtocolError("Login response missing 'token'")
        self._token = token
        return token

    async def fetch_din(self) -> str:
        """Fetch the gateway DIN from `/tedapi/din` using the bearer token."""
        body = await self._authed_get("/tedapi/din", expect_json=False)
        if not isinstance(body, (bytes, bytearray)):
            raise PowerwallProtocolError("DIN response is not bytes")
        try:
            din = body.decode("utf-8").strip()
        except UnicodeDecodeError as err:
            raise PowerwallProtocolError(f"DIN response is not UTF-8: {err}") from err
        if not din:
            raise PowerwallProtocolError("Empty DIN from gateway")
        return din

    async def api_get(self, path: str) -> Any:
        """GET a JSON-returning Powerwall REST endpoint with bearer auth.

        Used for `/api/meters/aggregates`, `/api/system_status/soe`,
        `/api/system_status/grid_status`, etc.
        """
        return await self._authed_get(path, expect_json=True)

    async def post_v1r(self, envelope_bytes: bytes, din: str) -> bytes:
        """POST a signed RoutableMessage and return the inner protobuf bytes.

        `envelope_bytes` is a serialized inner protobuf — a
        ``transport_pb2.MessageEnvelope``.
        """
        payload = await self._build_signed_request(envelope_bytes, din)
        url = f"https://{self._host}/tedapi/v1r"
        headers = {"Content-Type": "application/octet-stream"}

        content = await self._post_octets(url, payload, headers)

        # If the cached token expired the gateway returns 401/403 *and* we
        # already re-logged-in inside _post_octets, but the inner signature
        # was bound to that login. Bearer auth and v1r signing are
        # independent — a re-login does not invalidate the signature, so a
        # single retry is sufficient.
        try:
            response = signed_message_pb2.RoutableMessage()
            response.ParseFromString(content)
        except Exception as err:  # protobuf raises generic Exceptions
            raise PowerwallProtocolError(f"Malformed RoutableMessage: {err}") from err

        fault = response.signed_message_status.message_fault
        if fault != signed_message_pb2.MESSAGEFAULT_ERROR_NONE:
            fault_name = signed_message_pb2.MessageFault_E.Name(fault)
            if fault == signed_message_pb2.MESSAGEFAULT_ERROR_UNKNOWN_KEY_ID:
                raise PowerwallAuthenticationError(
                    "RSA key not registered with this Powerwall — pair the public "
                    "key via the Tesla Fleet API before calling v1r endpoints "
                    f"(fault: {fault_name})"
                )
            raise PowerwallFaultError(fault_name)

        inner: bytes = response.protobuf_message_as_bytes
        # The gateway signals a rejected RSA signature by returning HTTP 200
        # with no MESSAGEFAULT and a MessageEnvelope whose `common.placeholder`
        # carries an "authorization not verified" string. Detect it centrally
        # so callers see a clear auth error instead of every downstream parser
        # failing with "missing payload". The exact prefix/casing varies across
        # firmware, so match the core phrase case-insensitively.
        if _AUTH_NOT_VERIFIED_RE.search(inner):
            raise PowerwallAuthenticationError(
                "v1r: client authorization not verified — the RSA key is not "
                "paired with this Powerwall. Register the matching public key "
                "via the Tesla Fleet API before calling v1r endpoints."
            )
        if not inner:
            _LOGGER.warning(
                "v1r RoutableMessage has empty protobuf_message_as_bytes; "
                "full response (len=%d): %s\nparsed=%s",
                len(content),
                content.hex(),
                str(response).replace("\n", " | "),
            )
            raise PowerwallProtocolError("RoutableMessage response is empty")
        return inner

    # ── Internals ───────────────────────────────────────────────────────────

    @staticmethod
    def _load_private_key(pem: bytes) -> rsa.RSAPrivateKey:
        try:
            key = serialization.load_pem_private_key(pem, password=None)
        except (ValueError, TypeError) as err:
            raise PowerwallAuthenticationError(
                f"Invalid RSA private key PEM: {err}"
            ) from err
        if not isinstance(key, rsa.RSAPrivateKey):
            raise PowerwallAuthenticationError(
                f"v1r requires an RSA private key, got {type(key).__name__}"
            )
        return key

    async def _ensure_token(self) -> str:
        token = self._token
        if token is not None:
            return token
        async with self._token_lock:
            token = self._token
            if token is not None:
                return token
            return await self.login()

    async def _refresh_token(self) -> str:
        async with self._token_lock:
            self._token = None
            return await self.login()

    async def _authed_get(self, path: str, *, expect_json: bool) -> Any:
        url = f"https://{self._host}{path}"
        token = await self._ensure_token()
        for attempt in range(2):
            headers = {"Authorization": f"Bearer {token}"}
            try:
                async with self._session.get(
                    url, headers=headers, ssl=False, timeout=self._timeout
                ) as resp:
                    if resp.status in (401, 403) and attempt == 0:
                        token = await self._refresh_token()
                        continue
                    if resp.status in _RATE_LIMIT_STATUSES:
                        raise PowerwallRateLimitError(
                            f"Rate-limited by gateway on GET {path} "
                            f"(status {resp.status})"
                        )
                    if resp.status != 200:
                        raise PowerwallProtocolError(
                            f"GET {path} returned {resp.status}"
                        )
                    if expect_json:
                        return await resp.json(content_type=None)
                    body: bytes = await resp.read()
                    return _decompress(body)
            except aiohttp.ClientError as err:
                raise PowerwallConnectionError(
                    f"GET {path} transport error: {err}"
                ) from err
            except TimeoutError as err:
                raise PowerwallConnectionError(f"GET {path} timed out") from err
        raise PowerwallAuthenticationError(
            f"GET {path} unauthorized after token refresh"
        )

    async def _post_octets(
        self, url: str, payload: bytes, headers: dict[str, str]
    ) -> bytes:
        # v1r POSTs do *not* carry the bearer token — the body itself is RSA
        # signed. We still surface 401/403 distinctly in case the gateway
        # changes that contract in the future.
        try:
            async with self._session.post(
                url, data=payload, headers=headers, ssl=False, timeout=self._timeout
            ) as resp:
                if resp.status in (401, 403):
                    raise PowerwallAuthenticationError(
                        f"v1r POST rejected with {resp.status}"
                    )
                if resp.status in _RATE_LIMIT_STATUSES:
                    raise PowerwallRateLimitError(
                        f"Rate-limited by gateway on v1r POST (status {resp.status})"
                    )
                if resp.status != 200:
                    raise PowerwallProtocolError(
                        f"v1r POST returned {resp.status}"
                    )
                body: bytes = await resp.read()
                return _decompress(body)
        except aiohttp.ClientError as err:
            raise PowerwallConnectionError(
                f"v1r POST transport error: {err}"
            ) from err
        except TimeoutError as err:
            raise PowerwallConnectionError("v1r POST timed out") from err

    async def _build_signed_request(
        self, envelope_bytes: bytes, din: str
    ) -> bytes:
        """Wrap `envelope_bytes` in a signed RoutableMessage and serialize it.

        Signing is offloaded to a thread because RSA-4096 with SHA-512 is
        ~10 ms of CPU work and would otherwise block the event loop.
        """
        routable = signed_message_pb2.RoutableMessage()
        routable.to_destination.domain = _DOMAIN_ENERGY_DEVICE
        routable.protobuf_message_as_bytes = envelope_bytes
        routable.uuid = uuid.uuid4().bytes

        expires_at = math.ceil(time.time()) + _SIGNATURE_TTL_SECONDS
        tlv_payload = self._build_tlv(din, expires_at, envelope_bytes)
        signature = await asyncio.to_thread(self._sign, tlv_payload)

        routable.signature_data.signer_identity.public_key = self._public_key_der
        routable.signature_data.rsa_data.expires_at = expires_at
        routable.signature_data.rsa_data.signature = signature

        serialized: bytes = routable.SerializeToString()
        return serialized

    @staticmethod
    def _build_tlv(din: str, expires_at: int, inner: bytes) -> bytes:
        return b"".join(
            (
                _tlv(_TAG_SIGNATURE_TYPE, bytes([_SIGNATURE_TYPE_RSA])),
                _tlv(_TAG_DOMAIN, bytes([_DOMAIN_ENERGY_DEVICE])),
                _tlv(_TAG_PERSONALIZATION, din.encode("ascii")),
                _tlv(_TAG_EXPIRES_AT, struct.pack(">I", expires_at)),
                bytes([_TAG_END]),
                inner,
            )
        )

    def _sign(self, tlv_payload: bytes) -> bytes:
        signature: bytes = self._private_key.sign(
            data=tlv_payload,
            padding=padding.PKCS1v15(),
            algorithm=hashes.SHA512(),
        )
        return signature
