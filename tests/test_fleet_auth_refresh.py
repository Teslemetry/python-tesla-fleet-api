"""Characterization tests for TeslaFleetApi._request behavior.

These tests assert what ``_request`` does today; they do not assume any
auth-refresh / retry feature exists. If that feature is added later, extend
these tests to cover the retry path rather than deleting them.
"""

from contextlib import asynccontextmanager
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, MagicMock

from tesla_fleet_api.const import Method
from tesla_fleet_api.exceptions import MissingToken, NotFound, ResponseError
from tesla_fleet_api.tesla.fleet import TeslaFleetApi


class _RequestTestApi(TeslaFleetApi):
    """Expose the protected _request for testing."""

    async def request(
        self,
        method: Method,
        path: str,
        params: dict[str, object] | None = None,
        json: dict[str, object] | None = {},
    ) -> dict[str, object]:
        return await self._request(method, path, params=params, json=json)


def _make_api(
    token: str | None = "access-token",
    *,
    response: object = None,
    session: object = None,
) -> _RequestTestApi:
    """Create an API whose session.request yields the given fake response."""
    if session is None:
        session = MagicMock()

        @asynccontextmanager
        async def _ctx(*args, **kwargs):
            yield response

        # session.request(...) must return an async context manager
        session.request = MagicMock(side_effect=lambda *a, **k: _ctx(*a, **k))

    return _RequestTestApi(
        session=session,
        access_token=token,
        server="https://fleet.example.com",
    )


def _fake_response(
    *,
    status: int = 200,
    ok: bool = True,
    content_type: str = "application/json",
    json_body: object = None,
    text_body: str = "",
):
    resp = MagicMock()
    resp.status = status
    resp.ok = ok
    resp.content_type = content_type
    resp.url = "https://fleet.example.com/x"
    resp.headers = {}
    resp.json = AsyncMock(return_value=json_body if json_body is not None else {})
    resp.text = AsyncMock(return_value=text_body)
    return resp


class RequestBehaviorTests(IsolatedAsyncioTestCase):
    """Verify the real, current behavior of TeslaFleetApi._request."""

    async def test_missing_token_raises_missing_token(self) -> None:
        api = _make_api(token=None, response=_fake_response())
        with self.assertRaises(MissingToken):
            await api.request(Method.GET, "api/1/products")

    async def test_get_returns_parsed_json_and_sends_no_body(self) -> None:
        resp = _fake_response(json_body={"response": "ok"})
        api = _make_api(response=resp)
        result = await api.request(Method.GET, "api/1/products")
        self.assertEqual(result, {"response": "ok"})
        # GET must send json=None
        _, kwargs = api.session.request.call_args
        self.assertIsNone(kwargs["json"])
        self.assertEqual(kwargs["headers"]["Authorization"], "Bearer access-token")

    async def test_request_targets_server_and_path(self) -> None:
        resp = _fake_response(json_body={"response": "ok"})
        api = _make_api(response=resp)
        await api.request(Method.GET, "api/1/products")
        args, _ = api.session.request.call_args
        self.assertEqual(args[0], Method.GET)
        self.assertEqual(args[1], "https://fleet.example.com/api/1/products")

    async def test_non_json_content_type_raises_response_error(self) -> None:
        resp = _fake_response(content_type="text/html", text_body="<html>")
        api = _make_api(response=resp)
        with self.assertRaises(ResponseError):
            await api.request(Method.GET, "api/1/products")

    async def test_none_params_are_stripped_and_booleans_normalized(self) -> None:
        resp = _fake_response(json_body={"response": "ok"})
        api = _make_api(response=resp)
        await api.request(Method.GET, "api/1/x", params={"a": None, "b": True})
        _, kwargs = api.session.request.call_args
        self.assertEqual(kwargs["params"], {"b": "true"})

    async def test_error_status_routes_through_raise_for_status(self) -> None:
        resp = _fake_response(status=404, ok=False, json_body={"error": "not found"})
        api = _make_api(response=resp)
        with self.assertRaises(NotFound):
            await api.request(Method.GET, "api/1/products")
