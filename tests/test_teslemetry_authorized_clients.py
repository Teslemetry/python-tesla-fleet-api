"""Tests for TeslemetryEnergySite.get_authorized_clients(), the typed accessor
over the Teslemetry ``command/authorized_clients`` endpoint.

Covers the two upstream-review-flagged correctness points: a falsy field
value (e.g. an enum ``0``) must survive parsing, and an explicitly present
but empty ``authorized_clients`` list must be treated as authoritative
(zero clients) rather than as "field missing, keep looking".
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, MagicMock

from tesla_fleet_api.teslemetry.teslemetry import Teslemetry

_UNSET = object()

# A realistic sanitized fixture shape, matching what the Home Assistant
# Teslemetry integration's config flow (PR #176328) exercises against this
# endpoint.
PUBLIC_KEY_B64 = "MIIBCgKCAQEAsomeBase64EncodedRsaPublicKeyBytes=="


def _verified_clients_response() -> dict[str, Any]:
    return {
        "response": {
            "authorized_clients": [
                "not-a-dict",
                {"public_key": "some-other-key", "state": 3},
                {
                    "public_key": PUBLIC_KEY_B64,
                    "state": 3,
                    "description": "Home Assistant",
                    "key_type": 1,
                    "authorized_client_type": 0,
                },
            ]
        }
    }


def _fake_response(*, json_body: object = _UNSET) -> MagicMock:
    resp = MagicMock()
    resp.status = 200
    resp.ok = True
    resp.content_type = "application/json"
    resp.url = "https://example.com/x"
    resp.headers = {}
    resp.json = AsyncMock(return_value={} if json_body is _UNSET else json_body)
    resp.text = AsyncMock(return_value="")
    return resp


def _make_session(response: object) -> MagicMock:
    session = MagicMock()

    @asynccontextmanager
    async def _ctx(*args: Any, **kwargs: Any):
        yield response

    session.request = MagicMock(side_effect=lambda *a, **k: _ctx(*a, **k))
    return session


def _make_site(json_body: object):
    api = Teslemetry(
        session=_make_session(_fake_response(json_body=json_body)),
        access_token="token",
    )
    return api.energySites.create(12345)


class GetAuthorizedClientsTests(IsolatedAsyncioTestCase):
    async def test_normal_payload_round_trips(self) -> None:
        site = _make_site(_verified_clients_response())

        result = await site.get_authorized_clients()

        self.assertIsNotNone(result.clients)
        assert result.clients is not None
        self.assertEqual(len(result.clients), 2)
        matched = result.clients[1]
        self.assertEqual(matched.public_key, PUBLIC_KEY_B64)
        self.assertEqual(matched.state, 3)
        self.assertEqual(matched.description, "Home Assistant")
        self.assertEqual(matched.key_type, 1)

    async def test_falsy_zero_field_is_preserved(self) -> None:
        site = _make_site(_verified_clients_response())

        result = await site.get_authorized_clients()

        assert result.clients is not None
        matched = result.clients[1]
        # authorized_client_type=0 (AuthorizedClientType.INVALID) is a legal
        # value, not a stand-in for "field absent".
        self.assertEqual(matched.authorized_client_type, 0)
        self.assertIsNotNone(matched.authorized_client_type)

    async def test_explicitly_empty_list_is_authoritative(self) -> None:
        site = _make_site({"response": {"authorized_clients": []}})

        result = await site.get_authorized_clients()

        self.assertEqual(result.clients, [])
        self.assertIsNotNone(result.clients)

    async def test_absent_field_is_distinct_from_empty_list(self) -> None:
        site = _make_site({"response": {"foo": "bar"}})

        result = await site.get_authorized_clients()

        self.assertIsNone(result.clients)

    async def test_null_body_is_handled_without_raising(self) -> None:
        site = _make_site(None)

        result = await site.get_authorized_clients()

        self.assertIsNone(result.clients)
        self.assertIsNone(result.raw)

    async def test_non_dict_entries_are_skipped(self) -> None:
        site = _make_site(_verified_clients_response())

        result = await site.get_authorized_clients()

        assert result.clients is not None
        # The "not-a-dict" entry in the fixture is dropped, not raised on.
        self.assertTrue(all(hasattr(c, "public_key") for c in result.clients))
