"""Tests for TeslemetryBusiness.products(), the ``GET /api/business/products``
call on the Teslemetry for Business (teslemetry.pro) api."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, MagicMock

from tesla_fleet_api.teslemetry import TeslemetryBusiness

# Response shape from the api's business products route test.
PAGE: dict[str, Any] = {
    "response": [
        {
            "type": "vehicle",
            "vin": "5YJ3E1EA7KF000001",
            "customer": "q3V1d8sXbE2mJ0kZp4R7aA",
            "granted_at": "2026-10-06T00:00:00.000Z",
            "ref": "cust-1",
            "access": "allowed",
            "name": "Family car",
            "available": True,
            "permission": "OWNER",
            "state": "online",
            "issue": None,
            "signing": True,
            "fleet_telemetry": "1.1.0",
            "firmware": "2026.32.1",
        },
        {
            "type": "energy",
            "energy_site_id": 1234567890,
            "customer": "Zt0bQ9wYc5nL2hV8xR1kMg",
            "granted_at": "2026-10-05T00:00:00.000Z",
            "ref": None,
            "access": "allowed",
            "name": "Home",
            "available": True,
        },
    ],
    "count": 3,
    "next_cursor": "page2",
}


def _session(body: object) -> MagicMock:
    resp = MagicMock()
    resp.status = 200
    resp.ok = True
    resp.content_type = "application/json"
    resp.url = "https://api.teslemetry.pro/api/business/products"
    resp.headers = {}
    resp.json = AsyncMock(return_value=body)

    @asynccontextmanager
    async def _ctx(*args: Any, **kwargs: Any):
        yield resp

    session = MagicMock()
    session.request = MagicMock(side_effect=_ctx)
    return session


class BusinessProductsTests(IsolatedAsyncioTestCase):
    async def test_products_returns_the_page(self) -> None:
        session = _session(PAGE)
        api = TeslemetryBusiness(session, "business.abc.def")

        page = await api.products()

        self.assertEqual(page, PAGE)
        args, kwargs = session.request.call_args
        self.assertEqual(
            args, ("GET", "https://api.teslemetry.pro/api/business/products")
        )
        self.assertEqual(kwargs["params"], {})
        self.assertEqual(kwargs["headers"]["Authorization"], "Bearer business.abc.def")

    async def test_products_sends_filters_and_cursor(self) -> None:
        session = _session({"response": [], "count": 0, "next_cursor": None})
        api = TeslemetryBusiness(
            session, "business.abc.def", server="https://eu.teslemetry.pro"
        )

        page = await api.products(
            type="energy",
            ref="cust-1",
            since="2026-10-02T00:00:00.000Z",
            limit=200,
            cursor="page2",
        )

        self.assertIsNone(page["next_cursor"])
        args, kwargs = session.request.call_args
        self.assertEqual(args[1], "https://eu.teslemetry.pro/api/business/products")
        self.assertEqual(
            kwargs["params"],
            {
                "type": "energy",
                "ref": "cust-1",
                "since": "2026-10-02T00:00:00.000Z",
                "limit": 200,
                "cursor": "page2",
            },
        )
