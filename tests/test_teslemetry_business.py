"""Tests for Teslemetry for Business API key (``sk_...``) support.

The contract is Teslemetry/api PR 607: a business key may not call
``/api/metadata`` (403 ``business_route_not_allowed``), so ``find_server()``
must never request it for an ``sk_`` key; ``GET /api/business/products``
lists the consented products; and the business error codes map to typed
exceptions that still subclass ``Forbidden``/``ServiceUnavailable``.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import UTC, datetime
from typing import Any
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, MagicMock

from tesla_fleet_api.exceptions import (
    BusinessAuthUnavailable,
    BusinessForbidden,
    BusinessNotActive,
    BusinessPermissionMissing,
    BusinessProductNotConsented,
    BusinessRegionRequired,
    BusinessRouteNotAllowed,
    CustomerReconnectRequired,
    CustomerScopeMissing,
    Forbidden,
    InvalidResponse,
    ServiceUnavailable,
)
from tesla_fleet_api.teslemetry import BusinessProductType
from tesla_fleet_api.teslemetry.teslemetry import Teslemetry

# Verbatim from the PR 607 live transcript (S11/S12).
PRODUCTS_RESPONSE = {
    "response": [
        {
            "product_type": "vehicle",
            "product_id": "5YJ3E1EA1JF000001",
            "region": "NA",
            "customer": {"id": "vMcI3f7ajt8Jhf1Fcx_duj", "ref": None},
            "granted_at": "2026-10-01T00:00:00.000Z",
        },
        {
            "product_type": "energy",
            "product_id": "1234567",
            "region": "EU",
            "customer": {"id": "C1NEQ39IQ_btuJHUXIbwBc", "ref": "acct-42"},
            "granted_at": "2026-10-02T00:00:00.000Z",
        },
    ]
}


def _fake_response(
    *,
    status: int = 200,
    json_body: object = None,
    headers: dict[str, str] | None = None,
) -> MagicMock:
    resp = MagicMock()
    resp.status = status
    resp.ok = status < 400
    resp.content_type = "application/json"
    resp.url = "https://example.com/x"
    resp.headers = headers or {}
    resp.json = AsyncMock(return_value=json_body)
    resp.text = AsyncMock(return_value="")
    return resp


def _make_api(
    response: MagicMock | None = None,
    token: str = "sk_live_test",
    **kwargs: Any,
) -> tuple[Teslemetry, MagicMock]:
    session = MagicMock()

    @asynccontextmanager
    async def _ctx(*args: Any, **kw: Any):
        yield response

    session.request = MagicMock(side_effect=lambda *a, **k: _ctx(*a, **k))
    return Teslemetry(session=session, access_token=token, **kwargs), session


class RegionTests(IsolatedAsyncioTestCase):
    async def test_business_key_find_server_makes_no_request(self) -> None:
        api, session = _make_api(region="eu")
        self.assertEqual(api.server, "https://eu.teslemetry.com")
        self.assertEqual(await api.find_server(), "eu")
        session.request.assert_not_called()

    async def test_business_key_without_region_raises(self) -> None:
        api, session = _make_api()
        with self.assertRaises(BusinessRegionRequired):
            await api.find_server()
        session.request.assert_not_called()

    async def test_callable_business_token_is_detected(self) -> None:
        session = MagicMock()
        api = Teslemetry(
            session=session, access_token=AsyncMock(return_value="sk_live_x")
        )
        with self.assertRaises(BusinessRegionRequired):
            await api.find_server()
        session.request.assert_not_called()

    async def test_consumer_token_still_uses_metadata(self) -> None:
        api, session = _make_api(
            _fake_response(json_body={"region": "EU", "scopes": []}),
            token="consumer-token",
        )
        self.assertEqual(api.server, "https://api.teslemetry.com")
        self.assertEqual(await api.find_server(), "eu")
        self.assertEqual(api.server, "https://eu.teslemetry.com")
        method, url = session.request.call_args.args[:2]
        self.assertEqual(
            (method, url), ("GET", "https://api.teslemetry.com/api/metadata")
        )

    def test_explicit_server_wins_over_region(self) -> None:
        api, _ = _make_api(region="na", server="https://example.test")
        self.assertEqual(api.server, "https://example.test")
        self.assertEqual(api.region, "na")

    def test_invalid_region_raises(self) -> None:
        with self.assertRaises(ValueError):
            _make_api(region="cn")  # pyright: ignore[reportArgumentType]


class ProductsTests(IsolatedAsyncioTestCase):
    async def test_products_parses_listing(self) -> None:
        api, session = _make_api(
            _fake_response(json_body=PRODUCTS_RESPONSE), region="na"
        )
        products = await api.business.products()

        method, url = session.request.call_args.args[:2]
        self.assertEqual(
            (method, url), ("GET", "https://na.teslemetry.com/api/business/products")
        )
        self.assertEqual(len(products), 2)
        vehicle, energy = products
        self.assertIs(vehicle.product_type, BusinessProductType.VEHICLE)
        self.assertEqual(vehicle.product_id, "5YJ3E1EA1JF000001")
        self.assertEqual(vehicle.region, "na")
        self.assertEqual(vehicle.server, "https://na.teslemetry.com")
        self.assertEqual(vehicle.customer.id, "vMcI3f7ajt8Jhf1Fcx_duj")
        self.assertIsNone(vehicle.customer.ref)
        self.assertEqual(vehicle.granted_at, datetime(2026, 10, 1, tzinfo=UTC))
        self.assertIs(energy.product_type, BusinessProductType.ENERGY)
        self.assertEqual(energy.region, "eu")
        self.assertEqual(energy.server, "https://eu.teslemetry.com")
        self.assertEqual(energy.customer.ref, "acct-42")
        self.assertEqual(energy.raw, PRODUCTS_RESPONSE["response"][1])

    async def test_empty_listing_is_empty(self) -> None:
        api, _ = _make_api(_fake_response(json_body={"response": []}), region="na")
        self.assertEqual(await api.business.products(), [])

    async def test_malformed_listing_raises(self) -> None:
        item = PRODUCTS_RESPONSE["response"][0]
        bodies: list[object] = [
            None,
            {},
            {"response": None},
            {"response": [None]},
            {"response": [{**item, "region": "CN"}]},
            {"response": [{**item, "product_type": "wall_connector"}]},
            {"response": [{**item, "granted_at": "yesterday"}]},
            {"response": [{k: v for k, v in item.items() if k != "product_id"}]},
            {"response": [{**item, "customer": {"id": "x"}}]},
        ]
        for body in bodies:
            with self.subTest(body=body):
                api, _ = _make_api(_fake_response(json_body=body), region="na")
                with self.assertRaises(InvalidResponse):
                    await api.business.products()


class ErrorTests(IsolatedAsyncioTestCase):
    async def test_business_403_codes_map_to_typed_errors(self) -> None:
        cases: dict[str, type[BusinessForbidden]] = {
            "business_not_active": BusinessNotActive,
            "business_route_not_allowed": BusinessRouteNotAllowed,
            "business_permission_missing": BusinessPermissionMissing,
            "business_product_not_consented": BusinessProductNotConsented,
            "customer_reconnect_required": CustomerReconnectRequired,
            "customer_scope_missing": CustomerScopeMissing,
        }
        for code, exception in cases.items():
            with self.subTest(code=code):
                body = {"response": None, "error": code, "error_description": "x"}
                api, _ = _make_api(_fake_response(status=403, json_body=body))
                with self.assertRaises(exception) as ctx:
                    await api.test()
                self.assertIsInstance(ctx.exception, Forbidden)
                self.assertEqual(ctx.exception.data, body)

    async def test_metadata_with_business_key_raises_route_not_allowed(self) -> None:
        body = {"response": None, "error": "business_route_not_allowed"}
        api, _ = _make_api(_fake_response(status=403, json_body=body))
        with self.assertRaises(BusinessRouteNotAllowed):
            await api.metadata()

    async def test_business_auth_unavailable_carries_retry_after(self) -> None:
        body = {"response": None, "error": "business_auth_unavailable"}
        api, _ = _make_api(
            _fake_response(status=503, json_body=body, headers={"Retry-After": "5"})
        )
        with self.assertRaises(BusinessAuthUnavailable) as ctx:
            await api.test()
        self.assertIsInstance(ctx.exception, ServiceUnavailable)
        self.assertEqual(ctx.exception.retry_after, "5")

    async def test_other_403_is_still_plain_forbidden(self) -> None:
        body = {"response": None, "error": "something_else"}
        api, _ = _make_api(_fake_response(status=403, json_body=body))
        with self.assertRaises(Forbidden) as ctx:
            await api.test()
        self.assertNotIsInstance(ctx.exception, BusinessForbidden)
