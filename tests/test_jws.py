"""Tesla.SS256 signing (``tesla_fleet_api.tesla.jws``) and its Fleet API wiring.

Correctness is gated on byte-for-byte agreement with Tesla's Go SDK
(``teslamotors/vehicle-command``): the signature scheme is deterministic, so a
Python signature that matches Go's for the same key and message proves the
challenge framing and nonce derivation, not just internal consistency.
``fixtures/ss256_vectors.json`` was produced by ``fixtures/ss256_vectors_gen.go``
against that SDK; the inline vectors are copied from the SDK's own tests.
"""

from __future__ import annotations

import base64
import hashlib
import json
import unittest
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock

from cryptography.hazmat.primitives.asymmetric import ec

from tesla_fleet_api.const import Method
from tesla_fleet_api.exceptions import SigningDisabled
from tesla_fleet_api.tesla import jws
from tesla_fleet_api.tesla.vehicle.fleet import VehicleFleet
from tesla_fleet_api.tesla.vehicle.signed import VehicleSigned

VECTORS: dict[str, Any] = json.loads(
    (Path(__file__).parent / "fixtures" / "ss256_vectors.json").read_text()
)

# vehicle-command internal/schnorr/schnorr_test.go: testKey() is the scalar
# 0x03 followed by 31 zero bytes, goodSig() signs "hello world".
GO_TEST_SCALAR = bytes([3]) + bytes(31)
GO_GOOD_SIGNATURE = bytes.fromhex(
    "7cfdbeb5baa730540401550bdefa20976453e8539ae4b2f26ce33125801a08f9"
    "0ed20c3d846497ff82cc9772e3db4703982f47bd0b0b89dfb9a49cd2e5240546"
    "02b1e05fbf95f5686faea7a5809eb92f5ecc22eae74ceccc5e2a65dd67ff20fc"
)


def _key(scalar_hex: str) -> ec.EllipticCurvePrivateKey:
    return ec.derive_private_key(int(scalar_hex, 16), ec.SECP256R1())


def _b64url_decode(part: str) -> bytes:
    return base64.urlsafe_b64decode(part + "=" * (-len(part) % 4))


class CurveConstantsTests(unittest.TestCase):
    def test_generator_matches_cryptography(self) -> None:
        one = jws.public_key_bytes(ec.derive_private_key(1, ec.SECP256R1()))
        self.assertEqual(one, jws._encode_point(*jws._G))  # pyright: ignore[reportPrivateUsage]

    def test_order_matches_cryptography(self) -> None:
        # (n - 1)G = -G: same x, negated y.
        minus_one = ec.derive_private_key(jws._N - 1, ec.SECP256R1())  # pyright: ignore[reportPrivateUsage]
        numbers = minus_one.public_key().public_numbers()
        self.assertEqual(numbers.x, jws._G[0])  # pyright: ignore[reportPrivateUsage]
        self.assertEqual(numbers.y, jws._P - jws._G[1])  # pyright: ignore[reportPrivateUsage]


class DeterministicNonceTests(unittest.TestCase):
    """Vectors from vehicle-command internal/schnorr/sign_test.go."""

    def test_rfc6979_a25_vector(self) -> None:
        scalar = bytes.fromhex(
            "c9afa9d845ba75166b5c215767b1d6934e50c3db36e89b127b8a622b120f6721"
        )
        nonce = jws._deterministic_nonce(  # pyright: ignore[reportPrivateUsage]
            scalar, hashlib.sha256(b"sample").digest()
        )
        self.assertEqual(
            nonce.hex(),
            "a6e3c57dd01abe90086538398355dd4c3b17aa873382b0f24d6129493d8aad60",
        )

    def test_rejection_sampling(self) -> None:
        # The first candidate for this digest exceeds the group order.
        digest = bytes.fromhex(
            "0080c36864c5f2f460e3767983c65677b65cef901bcedcb223f9b365c68f52f6"
        )
        nonce = jws._deterministic_nonce(GO_TEST_SCALAR, digest)  # pyright: ignore[reportPrivateUsage]
        self.assertEqual(
            nonce.hex(),
            "264fc6592fbea24fd0954e0b86b886e8743161758ddad2f7e9fed75a0019e005",
        )


class SignatureVectorTests(unittest.TestCase):
    def test_go_sdk_published_signature(self) -> None:
        key = ec.derive_private_key(
            int.from_bytes(GO_TEST_SCALAR, "big"), ec.SECP256R1()
        )
        self.assertEqual(jws.sign(key, b"hello world"), GO_GOOD_SIGNATURE)

    def test_go_generated_signatures(self) -> None:
        for vector in VECTORS["signatures"]:
            with self.subTest(scalar=vector["scalar"], message=vector["message_hex"]):
                key = _key(vector["scalar"])
                message = bytes.fromhex(vector["message_hex"])
                public = bytes.fromhex(vector["public"])
                signature = bytes.fromhex(vector["signature"])
                self.assertEqual(jws.public_key_bytes(key), public)
                self.assertEqual(jws.sign(key, message), signature)
                self.assertTrue(jws.verify(public, message, signature))

    def test_signature_is_fixed_width(self) -> None:
        # One Go vector has a leading zero byte in V_x; padding must survive.
        leading_zero = [
            v for v in VECTORS["signatures"] if v["signature"].startswith("00")
        ]
        self.assertTrue(leading_zero)
        for vector in leading_zero:
            signature = jws.sign(
                _key(vector["scalar"]), bytes.fromhex(vector["message_hex"])
            )
            self.assertEqual(len(signature), jws.SIGNATURE_LENGTH)

    def test_random_key_round_trip(self) -> None:
        key = ec.generate_private_key(ec.SECP256R1())
        signature = jws.sign(key, b"payload")
        self.assertEqual(signature, jws.sign(key, b"payload"))
        self.assertTrue(jws.verify(jws.public_key_bytes(key), b"payload", signature))

    def test_rejects_non_p256_key(self) -> None:
        with self.assertRaises(ValueError):
            jws.sign(ec.generate_private_key(ec.SECP384R1()), b"payload")


class VerifyRejectionTests(unittest.TestCase):
    def setUp(self) -> None:
        vector = VECTORS["signatures"][0]
        self.public = bytes.fromhex(vector["public"])
        self.message = bytes.fromhex(vector["message_hex"])
        self.signature = bytes.fromhex(vector["signature"])

    def test_wrong_message(self) -> None:
        self.assertFalse(jws.verify(self.public, b"hello worle", self.signature))

    def test_wrong_public_key(self) -> None:
        other = jws.public_key_bytes(ec.derive_private_key(4 << 248, ec.SECP256R1()))
        self.assertFalse(jws.verify(other, self.message, self.signature))

    def test_tampered_nonce_and_scalar(self) -> None:
        for index in (0, jws.SCALAR_LENGTH, jws.SIGNATURE_LENGTH - 1):
            with self.subTest(index=index):
                tampered = bytearray(self.signature)
                tampered[index] ^= 1
                self.assertFalse(jws.verify(self.public, self.message, bytes(tampered)))

    def test_malformed_inputs(self) -> None:
        self.assertFalse(jws.verify(self.public, self.message, self.signature[:-1]))
        self.assertFalse(jws.verify(b"\x04" + bytes(64), self.message, self.signature))


class JwsTests(unittest.TestCase):
    def test_matches_go_sdk_token(self) -> None:
        vector = VECTORS["jws"]
        key = _key(vector["scalar"])
        self.assertEqual(
            jws.sign_fleet_telemetry_config(key, vector["config"]), vector["token"]
        )

    def test_go_token_structure_and_signature(self) -> None:
        vector = VECTORS["jws"]
        key = _key(vector["scalar"])
        header, payload, signature = vector["token"].split(".")
        self.assertEqual(
            json.loads(_b64url_decode(header)), {"alg": "Tesla.SS256", "typ": "JWT"}
        )
        claims = json.loads(_b64url_decode(payload))
        public = jws.public_key_bytes(key)
        self.assertEqual(claims["iss"], base64.b64encode(public).decode())
        self.assertEqual(claims["aud"], "com.tesla.fleet.TelemetryClient")
        self.assertTrue(
            jws.verify(
                public, f"{header}.{payload}".encode(), _b64url_decode(signature)
            )
        )

    def test_overwrites_iss_and_aud(self) -> None:
        key = _key(VECTORS["jws"]["scalar"])
        token = jws.sign_jws(key, {"iss": "spoof", "aud": "spoof", "x": 1}, "aud.test")
        claims = json.loads(_b64url_decode(token.split(".")[1]))
        self.assertEqual(claims["aud"], "aud.test")
        self.assertEqual(
            claims["iss"], base64.b64encode(jws.public_key_bytes(key)).decode()
        )
        self.assertEqual(claims["x"], 1)

    def test_does_not_mutate_claims(self) -> None:
        claims = {"exp": 1}
        jws.sign_jws(_key(VECTORS["jws"]["scalar"]), claims, "aud.test")
        self.assertEqual(claims, {"exp": 1})


class FleetTelemetryConfigTests(unittest.IsolatedAsyncioTestCase):
    VIN = "LRWYGCEK0PC000000"

    def _signed(
        self, private_key: ec.EllipticCurvePrivateKey
    ) -> tuple[VehicleSigned[Any], AsyncMock]:
        parent = MagicMock()
        parent.private_key = private_key
        request = AsyncMock(return_value={"response": {"updated_vehicles": 1}})
        parent._request = request  # pyright: ignore[reportAttributeAccessIssue]
        return VehicleSigned(parent, self.VIN), request

    async def test_jws_endpoint_body(self) -> None:
        parent = MagicMock()
        request = AsyncMock(return_value={"response": {}})
        parent._request = request  # pyright: ignore[reportAttributeAccessIssue]
        await VehicleFleet(parent, self.VIN).fleet_telemetry_config_jws(
            [self.VIN], "a.b.c"
        )
        request.assert_awaited_once_with(
            Method.POST,
            "api/1/vehicles/fleet_telemetry_config_jws",
            json={"vins": [self.VIN], "token": "a.b.c"},
        )

    async def test_signed_create_posts_verifiable_jws(self) -> None:
        key = _key(VECTORS["jws"]["scalar"])
        vehicle, request = self._signed(key)
        config = VECTORS["jws"]["config"]

        result = await vehicle.fleet_telemetry_config_create(
            {"vins": [self.VIN], "config": config}
        )

        self.assertEqual(result, {"response": {"updated_vehicles": 1}})
        request.assert_awaited_once_with(
            Method.POST,
            "api/1/vehicles/fleet_telemetry_config_jws",
            json={"vins": [self.VIN], "token": VECTORS["jws"]["token"]},
        )

    async def test_signed_create_requires_signing_key(self) -> None:
        vehicle, request = self._signed(_key(VECTORS["jws"]["scalar"]))
        # What Commands.__init__ stores for private_key=False.
        vehicle.private_key = None
        with self.assertRaises(SigningDisabled):
            await vehicle.fleet_telemetry_config_create(
                {"vins": [self.VIN], "config": {}}
            )
        request.assert_not_awaited()
