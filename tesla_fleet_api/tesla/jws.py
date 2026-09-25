"""Tesla.SS256: Schnorr signatures over P-256 and the compact JWS that carries them.

Tesla signs messages for fleet-wide or offline delivery (e.g. a Fleet Telemetry
configuration) with Schnorr/P-256/SHA-256 (RFC 8235) using the same EC key the
partner registered for signed commands, wrapped in a compact JWS with
``"alg": "Tesla.SS256"``. This is a clean-room implementation of the scheme in
Tesla's Go SDK (``teslamotors/vehicle-command``, Apache-2.0):
``internal/schnorr`` for the signature and ``internal/authentication/jwt.go`` /
``pkg/sign`` for the token. ``tests/test_jws.py`` cross-checks it against
vectors produced by that Go code.

A signature is 96 bytes ``V_x || V_y || r``, where ``V = vG`` is the public
nonce and ``r = v - a*c (mod n)`` for private key ``a`` and challenge ``c``.
The nonce ``v`` is deterministic (RFC 6979 over SHA-256 of the message), so
signing the same message with the same key is reproducible. There is
deliberately no low-``s`` normalisation: that is an ECDSA malleability fix, not
part of this scheme, and applying it would produce signatures Tesla rejects.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
from typing import Any, Mapping

from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

ALGORITHM = "Tesla.SS256"
TELEMETRY_AUDIENCE = "com.tesla.fleet.TelemetryClient"
SCALAR_LENGTH = 32
SIGNATURE_LENGTH = 3 * SCALAR_LENGTH

# NIST P-256 domain parameters (a = -3), as Go's crypto/elliptic.P256() reports them.
_P = 0xFFFFFFFF00000001000000000000000000000000FFFFFFFFFFFFFFFFFFFFFFFF
_N = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551
_G = (
    0x6B17D1F2E12C4247F8BCE6E563A440F277037D812DEB33A0F4A13945D898C296,
    0x4FE342E2FE1A7F9B8EE7EB4A7C0F9E162BCE33576B315ECECBB6406837BF51F5,
)

_Point = tuple[int, int] | None  # None is the point at infinity


def _encode_point(x: int, y: int) -> bytes:
    """Uncompressed SEC1 encoding: 0x04 || X || Y."""
    return b"\x04" + x.to_bytes(SCALAR_LENGTH, "big") + y.to_bytes(SCALAR_LENGTH, "big")


def _length_value(buf: bytes) -> bytes:
    return len(buf).to_bytes(4, "big") + buf


def _challenge(public_nonce: bytes, public_key: bytes, message: bytes) -> int:
    """SHA-256 over the length-prefixed generator, public nonce, signer key and message."""
    digest = hashlib.sha256(
        _length_value(_encode_point(*_G))
        + _length_value(public_nonce)
        + _length_value(public_key)
        + _length_value(message)
    ).digest()
    return int.from_bytes(digest, "big")


def _deterministic_nonce(scalar: bytes, message_hash: bytes) -> bytes:
    """RFC 6979 section 3.2 nonce, specialised to P-256 with SHA-256 (hlen = qlen)."""
    h1 = (int.from_bytes(message_hash, "big") % _N).to_bytes(SCALAR_LENGTH, "big")
    k = b"\x00" * 32
    v = b"\x01" * 32
    k = hmac.digest(k, v + b"\x00" + scalar + h1, "sha256")
    v = hmac.digest(k, v, "sha256")
    k = hmac.digest(k, v + b"\x01" + scalar + h1, "sha256")
    v = hmac.digest(k, v, "sha256")
    while True:
        v = hmac.digest(k, v, "sha256")
        if 0 < int.from_bytes(v, "big") < _N:
            return v
        k = hmac.digest(k, v + b"\x00", "sha256")
        v = hmac.digest(k, v, "sha256")


def public_key_bytes(private_key: ec.EllipticCurvePrivateKey) -> bytes:
    """The 65-byte uncompressed public point for ``private_key``."""
    return private_key.public_key().public_bytes(
        Encoding.X962, PublicFormat.UncompressedPoint
    )


def sign(private_key: ec.EllipticCurvePrivateKey, message: bytes) -> bytes:
    """Return the 96-byte Tesla.SS256 Schnorr signature of ``message``."""
    if not isinstance(private_key.curve, ec.SECP256R1):
        raise ValueError("Tesla.SS256 requires a P-256 (SECP256R1) key.")
    a = private_key.private_numbers().private_value
    nonce = _deterministic_nonce(
        a.to_bytes(SCALAR_LENGTH, "big"), hashlib.sha256(message).digest()
    )
    v = int.from_bytes(nonce, "big")
    public_nonce = public_key_bytes(ec.derive_private_key(v, ec.SECP256R1()))
    c = _challenge(public_nonce, public_key_bytes(private_key), message)
    r = (v - a * c) % _N
    return public_nonce[1:] + r.to_bytes(SCALAR_LENGTH, "big")


def _add(p: _Point, q: _Point) -> _Point:
    if p is None:
        return q
    if q is None:
        return p
    if p[0] == q[0]:
        if (p[1] + q[1]) % _P == 0:
            return None
        slope = (3 * p[0] * p[0] - 3) * pow(2 * p[1], -1, _P)
    else:
        slope = (q[1] - p[1]) * pow(q[0] - p[0], -1, _P)
    x = (slope * slope - p[0] - q[0]) % _P
    return x, (slope * (p[0] - x) - p[1]) % _P


def _multiply(k: int, point: _Point) -> _Point:
    result: _Point = None
    while k:
        if k & 1:
            result = _add(result, point)
        point = _add(point, point)
        k >>= 1
    return result


def verify(public_key: bytes, message: bytes, signature: bytes) -> bool:
    """Check a Tesla.SS256 signature against a 65-byte uncompressed public key.

    Verification uses only public values, so the plain-integer point
    arithmetic here is not a side-channel concern.
    """
    if len(signature) != SIGNATURE_LENGTH:
        return False
    try:
        numbers = ec.EllipticCurvePublicKey.from_encoded_point(
            ec.SECP256R1(), public_key
        ).public_numbers()
    except ValueError:
        return False
    r = int.from_bytes(signature[2 * SCALAR_LENGTH :], "big")
    c = _challenge(b"\x04" + signature[: 2 * SCALAR_LENGTH], public_key, message)
    expected = _add(_multiply(c, (numbers.x, numbers.y)), _multiply(r, _G))
    return expected is not None and _encode_point(*expected)[1:] == bytes(
        signature[: 2 * SCALAR_LENGTH]
    )


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _json(value: Mapping[str, Any]) -> bytes:
    # Sorted and compact to match the Go SDK's encoding/json output.
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def sign_jws(
    private_key: ec.EllipticCurvePrivateKey,
    claims: Mapping[str, Any],
    audience: str,
) -> str:
    """Return a compact Tesla.SS256 JWS over ``claims``.

    Like the Go SDK, ``iss`` is set to the standard (padded) base64 of the
    signer's uncompressed public key and ``aud`` to ``audience``, overwriting
    any caller-supplied values.
    """
    payload = {
        **claims,
        "iss": base64.b64encode(public_key_bytes(private_key)).decode(),
        "aud": audience,
    }
    signing_input = (
        _b64url(_json({"alg": ALGORITHM, "typ": "JWT"})) + "." + _b64url(_json(payload))
    )
    return signing_input + "." + _b64url(sign(private_key, signing_input.encode()))


def sign_fleet_telemetry_config(
    private_key: ec.EllipticCurvePrivateKey, config: Mapping[str, Any]
) -> str:
    """Return the JWS token ``fleet_telemetry_config_jws`` expects for ``config``."""
    return sign_jws(private_key, config, TELEMETRY_AUDIENCE)
