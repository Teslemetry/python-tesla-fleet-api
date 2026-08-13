"""Tests for ``register_client()``, the Teslemetry OAuth dynamic client
registration (RFC 7591) transport helper.

Mirrors the registration semantics of the Home Assistant Teslemetry
integration's ``oauth.py`` (endpoint, request payload, response parsing,
and failure modes): a transport/timeout failure, a server-rejected
registration, and a malformed/missing-``client_id`` response all raise
:class:`~tesla_fleet_api.exceptions.TeslemetryRegistrationError`.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, MagicMock

import aiohttp

from tesla_fleet_api.exceptions import TeslemetryRegistrationError
from tesla_fleet_api.teslemetry.teslemetry import (
    REGISTER_URL,
    TeslemetryClientRegistration,
    register_client,
)


def _fake_response(
    *, json_body: object = None, raise_for_status_error: Exception | None = None
) -> MagicMock:
    resp = MagicMock()
    resp.raise_for_status = MagicMock(side_effect=raise_for_status_error)
    if isinstance(json_body, Exception):
        resp.json = AsyncMock(side_effect=json_body)
    else:
        resp.json = AsyncMock(return_value=json_body)
    return resp


def _make_session(
    *,
    response: object = None,
    post_error: Exception | None = None,
) -> MagicMock:
    session = MagicMock()

    if post_error is not None:
        session.post = MagicMock(side_effect=post_error)
        return session

    @asynccontextmanager
    async def _ctx(*args: Any, **kwargs: Any):
        yield response

    session.post = MagicMock(side_effect=lambda *a, **k: _ctx(*a, **k))
    return session


class RegisterClientSuccessTests(IsolatedAsyncioTestCase):
    async def test_registers_new_client(self) -> None:
        session = _make_session(
            response=_fake_response(json_body={"client_id": "new-client-id"})
        )

        result = await register_client(
            session, "Home Assistant", "home-assistant", "2026.1.0"
        )

        self.assertEqual(
            result,
            TeslemetryClientRegistration(
                client_id="new-client-id", raw={"client_id": "new-client-id"}
            ),
        )
        args, kwargs = session.post.call_args
        self.assertEqual(args[0], REGISTER_URL)
        self.assertEqual(
            kwargs["json"],
            {
                "client_name": "Home Assistant",
                "software_id": "home-assistant",
                "software_version": "2026.1.0",
            },
        )


class RegisterClientRejectionTests(IsolatedAsyncioTestCase):
    async def test_server_rejected_registration_raises_typed_error(self) -> None:
        error = aiohttp.ClientResponseError(
            MagicMock(), (), status=400, message="Bad Request"
        )
        session = _make_session(
            response=_fake_response(json_body={}, raise_for_status_error=error)
        )

        with self.assertRaises(TeslemetryRegistrationError):
            await register_client(session, "Home Assistant", "home-assistant", "1")

    async def test_connection_error_raises_typed_error(self) -> None:
        session = _make_session(post_error=aiohttp.ClientConnectionError("boom"))

        with self.assertRaises(TeslemetryRegistrationError):
            await register_client(session, "Home Assistant", "home-assistant", "1")

    async def test_timeout_raises_typed_error(self) -> None:
        session = _make_session(post_error=TimeoutError())

        with self.assertRaises(TeslemetryRegistrationError):
            await register_client(session, "Home Assistant", "home-assistant", "1")


class RegisterClientMalformedResponseTests(IsolatedAsyncioTestCase):
    async def test_non_json_body_raises_typed_error(self) -> None:
        session = _make_session(
            response=_fake_response(json_body=ValueError("not json"))
        )

        with self.assertRaises(TeslemetryRegistrationError):
            await register_client(session, "Home Assistant", "home-assistant", "1")

    async def test_missing_client_id_raises_typed_error(self) -> None:
        session = _make_session(response=_fake_response(json_body={}))

        with self.assertRaises(TeslemetryRegistrationError):
            await register_client(session, "Home Assistant", "home-assistant", "1")

    async def test_non_string_client_id_raises_typed_error(self) -> None:
        session = _make_session(response=_fake_response(json_body={"client_id": 12345}))

        with self.assertRaises(TeslemetryRegistrationError):
            await register_client(session, "Home Assistant", "home-assistant", "1")

    async def test_empty_string_client_id_raises_typed_error(self) -> None:
        session = _make_session(response=_fake_response(json_body={"client_id": ""}))

        with self.assertRaises(TeslemetryRegistrationError):
            await register_client(session, "Home Assistant", "home-assistant", "1")

    async def test_non_dict_body_raises_typed_error(self) -> None:
        session = _make_session(
            response=_fake_response(json_body=["unexpected", "list", "body"])
        )

        with self.assertRaises(TeslemetryRegistrationError):
            await register_client(session, "Home Assistant", "home-assistant", "1")

    async def test_null_body_raises_typed_error(self) -> None:
        session = _make_session(response=_fake_response(json_body=None))

        with self.assertRaises(TeslemetryRegistrationError):
            await register_client(session, "Home Assistant", "home-assistant", "1")
