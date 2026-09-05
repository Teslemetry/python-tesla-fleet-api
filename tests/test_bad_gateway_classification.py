"""502 classification: always a TeslaFleetError, regardless of body shape.

A 502 must always become a ``TeslaFleetError`` subclass instead of leaking a
raw ``aiohttp.ClientResponseError`` - see
``tesla_fleet_api.exceptions.raise_for_status``.
"""

from contextlib import asynccontextmanager
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, MagicMock

from yarl import URL

from tesla_fleet_api.const import Method
from tesla_fleet_api.exceptions import BadGateway
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


def _make_api(*, response: object) -> _RequestTestApi:
    session = MagicMock()

    @asynccontextmanager
    async def _ctx(*args, **kwargs):
        yield response

    session.request = MagicMock(side_effect=lambda *a, **k: _ctx(*a, **k))
    return _RequestTestApi(
        session=session,
        access_token="access-token",
        server="https://fleet.example.com",
    )


def _fake_response(
    *,
    path: str,
    content_type: str = "application/json",
    json_body: object = None,
    text_body: str = "",
):
    resp = MagicMock()
    resp.status = 502
    resp.ok = False
    resp.content_type = content_type
    resp.url = URL(f"https://fleet.example.com{path}")
    resp.headers = {}
    resp.json = AsyncMock(return_value=json_body if json_body is not None else {})
    resp.text = AsyncMock(return_value=text_body)
    return resp


class BadGatewayClassificationTests(IsolatedAsyncioTestCase):
    async def test_json_bodied_502_raises_bad_gateway(self) -> None:
        resp = _fake_response(
            path="/api/1/energy_sites/123/command/add_authorized_client",
            json_body={"error": "gateway unreachable"},
        )
        api = _make_api(response=resp)
        with self.assertRaises(BadGateway):
            await api.request(
                Method.POST, "api/1/energy_sites/123/command/add_authorized_client"
            )

    async def test_bodyless_502_raises_bad_gateway(self) -> None:
        resp = _fake_response(
            path="/api/1/energy_sites/123/command/authorized_clients",
            content_type="text/plain",
            text_body="",
        )
        api = _make_api(response=resp)
        with self.assertRaises(BadGateway):
            await api.request(
                Method.GET, "api/1/energy_sites/123/command/authorized_clients"
            )

    async def test_non_gateway_endpoint_502_also_raises_bad_gateway(self) -> None:
        resp = _fake_response(
            path="/api/1/vehicles/123/vehicle_data",
            json_body={"error": "upstream error"},
        )
        api = _make_api(response=resp)
        with self.assertRaises(BadGateway):
            await api.request(Method.GET, "api/1/vehicles/123/vehicle_data")
