"""Tests for TeslemetryEnergySite.find_authorized_clients(), the typed accessor
over the Teslemetry ``command/authorized_clients`` endpoint.

This endpoint's schema is undocumented; the wire-shape variants covered here
(null body, bare list, wrapper envelope, key-name casing) are pinned from the
Home Assistant Teslemetry integration's own defensive parsing of it. No site
has been observed with a populated client list yet, so the per-entry shape
is not live-sample-confirmed - see ``AuthorizedClient`` in
``tesla_fleet_api/teslemetry/energysite.py``.

Tesla's upstream endpoint intermittently returns HTTP 200 with a null body;
a null body or any other unrecognized 200 shape is malformed data and must
raise :class:`~tesla_fleet_api.exceptions.InvalidResponse` rather than being
silently treated as "no clients" - only a genuinely empty
``authorized_clients`` list means that.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, MagicMock

from tesla_fleet_api.const import AuthorizedClientState
from tesla_fleet_api.exceptions import InvalidResponse
from tesla_fleet_api.teslemetry.teslemetry import Teslemetry

_UNSET = object()

PUBLIC_KEY_B64 = "MIIBCgKCAQEAsomeBase64EncodedRsaPublicKeyBytes=="


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
        site = _make_site(
            {
                "response": {
                    "authorized_clients": [
                        "not-a-dict",
                        {
                            "public_key": PUBLIC_KEY_B64,
                            "state": 3,
                        },
                    ]
                }
            }
        )

        result = await site.find_authorized_clients()

        self.assertEqual(len(result.clients), 1)
        matched = result.clients[0]
        self.assertEqual(matched.public_key, PUBLIC_KEY_B64)
        self.assertEqual(matched.state, AuthorizedClientState.VERIFIED)

    async def test_bare_list_payload_with_no_envelope(self) -> None:
        site = _make_site([{"public_key": PUBLIC_KEY_B64, "state": 1}])

        result = await site.find_authorized_clients()

        self.assertEqual(len(result.clients), 1)
        self.assertEqual(result.clients[0].state, AuthorizedClientState.PENDING)

    async def test_camel_case_entry_fields_are_recognized(self) -> None:
        site = _make_site(
            {
                "response": {
                    "authorized_clients": [
                        {
                            "publicKey": PUBLIC_KEY_B64,
                            "authorized_client_state": 3,
                        }
                    ]
                }
            }
        )

        result = await site.find_authorized_clients()

        self.assertEqual(len(result.clients), 1)
        matched = result.clients[0]
        self.assertEqual(matched.public_key, PUBLIC_KEY_B64)
        self.assertEqual(matched.state, AuthorizedClientState.VERIFIED)

    async def test_state_as_string_is_typed_via_enum(self) -> None:
        site = _make_site(
            {
                "response": {
                    "authorized_clients": [
                        {"public_key": PUBLIC_KEY_B64, "state": "verified"}
                    ]
                }
            }
        )

        result = await site.find_authorized_clients()

        self.assertEqual(result.clients[0].state, AuthorizedClientState.VERIFIED)

    async def test_unrecognized_present_state_is_preserved_not_dropped(self) -> None:
        site = _make_site(
            {
                "response": {
                    "authorized_clients": [{"public_key": PUBLIC_KEY_B64, "state": 0}]
                }
            }
        )

        result = await site.find_authorized_clients()

        # 0 is not a member of AuthorizedClientState, but it is a present
        # value - it must not be coerced to None (which means "absent").
        self.assertEqual(result.clients[0].state, 0)
        self.assertIsNotNone(result.clients[0].state)

    async def test_explicitly_empty_list_returns_typed_empty_list(self) -> None:
        site = _make_site({"response": {"authorized_clients": []}})

        result = await site.find_authorized_clients()

        self.assertEqual(result.clients, [])

    async def test_absent_field_raises_invalid_response(self) -> None:
        site = _make_site({"response": {"foo": "bar"}})

        with self.assertRaises(InvalidResponse):
            await site.find_authorized_clients()

    async def test_null_body_raises_invalid_response(self) -> None:
        site = _make_site(None)

        with self.assertRaises(InvalidResponse):
            await site.find_authorized_clients()

    async def test_unrecognized_non_dict_non_list_body_raises_invalid_response(
        self,
    ) -> None:
        site = _make_site("not-a-valid-shape")

        with self.assertRaises(InvalidResponse):
            await site.find_authorized_clients()

    async def test_non_dict_entries_are_skipped(self) -> None:
        site = _make_site(
            {
                "response": {
                    "authorized_clients": [
                        "not-a-dict",
                        {"public_key": PUBLIC_KEY_B64, "state": 3},
                    ]
                }
            }
        )

        result = await site.find_authorized_clients()

        self.assertEqual(len(result.clients), 1)
