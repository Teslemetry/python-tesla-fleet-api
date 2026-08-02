"""Tests for energy-gateway authorized-client enums, key helpers, and removal.

Enum values are pinned to the gateway's numbers - live-verified on a real
Powerwall 3 - so a future regression back to the old, mislabelled names
fails loudly. See ``AuthorizedClientState`` in ``tesla_fleet_api/const.py``
for the breaking rename this locks in.
"""

from __future__ import annotations

import base64
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec

from tesla_fleet_api.const import (
    AuthorizationRole,
    AuthorizedClientKeyType,
    AuthorizedClientState,
    AuthorizedVerificationType,
)
from tesla_fleet_api.tesla.energysite import EnergySite
from tesla_fleet_api.tesla.tesla import Tesla
from tesla_fleet_api.teslemetry.energysite import TeslemetryEnergySite


class AuthorizedClientStateValuesTests(IsolatedAsyncioTestCase):
    async def test_state_values_match_the_gateway(self) -> None:
        self.assertEqual(AuthorizedClientState.INVALID, 0)
        self.assertEqual(AuthorizedClientState.PENDING_VERIFICATION, 1)
        self.assertEqual(AuthorizedClientState.PENDING_VERIFICATION_TIMEOUT, 2)
        self.assertEqual(AuthorizedClientState.VERIFIED, 3)
        self.assertEqual(AuthorizedClientState.REMOVED, 4)

    async def test_key_type_values_match_the_gateway(self) -> None:
        self.assertEqual(AuthorizedClientKeyType.INVALID, 0)
        self.assertEqual(AuthorizedClientKeyType.RSA, 1)
        self.assertEqual(AuthorizedClientKeyType.ECC, 2)

    async def test_role_values_match_the_gateway(self) -> None:
        self.assertEqual(AuthorizationRole.INVALID, 0)
        self.assertEqual(AuthorizationRole.CUSTOMER, 1)
        self.assertEqual(AuthorizationRole.VEHICLE, 2)

    async def test_verification_type_values_match_the_gateway(self) -> None:
        self.assertEqual(AuthorizedVerificationType.INVALID, 0)
        self.assertEqual(AuthorizedVerificationType.PRESENCE_PROOF, 1)
        self.assertEqual(AuthorizedVerificationType.BLE, 2)
        self.assertEqual(AuthorizedVerificationType.SIGNED, 3)
        self.assertEqual(AuthorizedVerificationType.HERMES_COMMAND, 4)


class EcPublicDerSpkiTests(IsolatedAsyncioTestCase):
    async def test_matches_cryptography_spki_encoding(self) -> None:
        tesla = Tesla()
        tesla.private_key = ec.generate_private_key(ec.SECP256R1())

        der = tesla.ec_public_der_spki

        expected = tesla.private_key.public_key().public_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        self.assertEqual(der, expected)
        # SPKI DER for a P-256 key is 91 bytes - distinct from the 65-byte
        # raw X9.62 uncompressed point the gateway rejects (finding #3).
        self.assertEqual(len(der), 91)

    async def test_b64_matches_base64_of_der(self) -> None:
        tesla = Tesla()
        tesla.private_key = ec.generate_private_key(ec.SECP256R1())

        self.assertEqual(
            tesla.ec_public_der_spki_b64,
            base64.b64encode(tesla.ec_public_der_spki).decode("ascii"),
        )

    async def test_raises_without_a_private_key(self) -> None:
        tesla = Tesla()
        with self.assertRaises(ValueError):
            _ = tesla.ec_public_der_spki


def _make_base_site() -> tuple[EnergySite, AsyncMock]:
    request_mock: AsyncMock = AsyncMock(return_value={})
    parent = AsyncMock()
    parent._request = request_mock
    site = EnergySite(parent, 12345)
    return site, request_mock


def _make_teslemetry_site() -> tuple[TeslemetryEnergySite, AsyncMock]:
    request_mock: AsyncMock = AsyncMock(return_value={})
    parent = AsyncMock()
    parent._request = request_mock
    site = TeslemetryEnergySite(parent, 12345)
    return site, request_mock


class BaseRemoveAuthorizedClientTests(IsolatedAsyncioTestCase):
    async def test_bytes_public_key_is_base64_encoded(self) -> None:
        site, request_mock = _make_base_site()

        await site.remove_authorized_client(b"raw-der-bytes")

        _, kwargs = request_mock.call_args
        message = kwargs["json"]["command_properties"]["message"]
        params = message["authorization"]["remove_authorized_client_request"]
        self.assertEqual(
            params["public_key"],
            base64.b64encode(b"raw-der-bytes").decode("ascii"),
        )

    async def test_str_public_key_passes_through_unchanged(self) -> None:
        site, request_mock = _make_base_site()
        b64_key = "already-base64=="

        await site.remove_authorized_client(b64_key)

        _, kwargs = request_mock.call_args
        message = kwargs["json"]["command_properties"]["message"]
        params = message["authorization"]["remove_authorized_client_request"]
        self.assertEqual(params["public_key"], b64_key)


class TeslemetryRemoveAuthorizedClientTests(IsolatedAsyncioTestCase):
    async def test_bytes_public_key_is_base64_encoded(self) -> None:
        site, request_mock = _make_teslemetry_site()

        await site.remove_authorized_client(b"raw-der-bytes")

        _, kwargs = request_mock.call_args
        self.assertEqual(
            kwargs["json"]["public_key"],
            base64.b64encode(b"raw-der-bytes").decode("ascii"),
        )

    async def test_str_public_key_passes_through_unchanged(self) -> None:
        site, request_mock = _make_teslemetry_site()
        b64_key = "already-base64=="

        await site.remove_authorized_client(b64_key)

        _, kwargs = request_mock.call_args
        self.assertEqual(kwargs["json"]["public_key"], b64_key)
