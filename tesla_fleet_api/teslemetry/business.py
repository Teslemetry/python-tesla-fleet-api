"""Teslemetry for Business: the endpoints only a business API key may call.

A business authenticates with a WorkOS organization API key
(``Authorization: Bearer sk_...``) and may read only the vehicles and energy
sites its customers have shared with it.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Any, Literal, cast

from tesla_fleet_api.const import Method
from tesla_fleet_api.exceptions import InvalidResponse
from tesla_fleet_api.teslemetry.const import BusinessProductType

if TYPE_CHECKING:
    from tesla_fleet_api.teslemetry.teslemetry import Teslemetry

BUSINESS_KEY_PREFIX = "sk_"

TeslemetryRegion = Literal["na", "eu"]

_REGIONS: dict[str, TeslemetryRegion] = {"NA": "na", "EU": "eu"}


def is_business_key(token: str) -> bool:
    """Whether ``token`` is a Teslemetry for Business API key."""
    return token.startswith(BUSINESS_KEY_PREFIX)


def teslemetry_server(region: TeslemetryRegion) -> str:
    """The Teslemetry API host for ``region``."""
    return f"https://{region}.teslemetry.com"


@dataclass(frozen=True, slots=True)
class BusinessCustomer:
    """The customer who shared a product, as the business sees them.

    ``id`` is a pseudonym, stable for this business and different for every
    other business. ``ref`` is the business's own customer reference from
    enrolment, or ``None``.
    """

    id: str
    ref: str | None


@dataclass(frozen=True, slots=True)
class BusinessProduct:
    """One vehicle or energy site a customer has shared with the business.

    ``product_id`` is the VIN, or the energy site id as a digit string.
    ``region`` is the customer's Teslemetry region; ``server`` is that
    region's API host, which answers without a cross-region proxy hop.
    ``raw`` is the decoded item, for anything this wrapper doesn't model.
    """

    product_type: BusinessProductType
    product_id: str
    region: TeslemetryRegion
    customer: BusinessCustomer
    granted_at: datetime
    raw: dict[str, Any]

    @property
    def server(self) -> str:
        """The Teslemetry API host for this product's region."""
        return teslemetry_server(self.region)


def _field(item: dict[str, Any], key: str) -> Any:
    if key not in item:
        raise InvalidResponse({"error": f"product is missing {key}"})
    return item[key]


def _str_field(item: dict[str, Any], key: str) -> str:
    value = _field(item, key)
    if not isinstance(value, str):
        raise InvalidResponse({"error": f"product {key} is not a string"})
    return value


def _parse_product(item: object) -> BusinessProduct:
    if not isinstance(item, dict):
        raise InvalidResponse({"error": "product is not an object"})
    product = cast("dict[str, Any]", item)

    product_type = _str_field(product, "product_type")
    try:
        typed_product_type = BusinessProductType(product_type)
    except ValueError as err:
        raise InvalidResponse(
            {"error": f"unknown product_type {product_type}"}
        ) from err

    region = _str_field(product, "region")
    if region not in _REGIONS:
        raise InvalidResponse({"error": f"unknown region {region}"})

    customer = _field(product, "customer")
    if not isinstance(customer, dict):
        raise InvalidResponse({"error": "product customer is not an object"})
    customer = cast("dict[str, Any]", customer)
    ref = _field(customer, "ref")
    if ref is not None and not isinstance(ref, str):
        raise InvalidResponse({"error": "customer ref is not a string"})

    granted_at = _str_field(product, "granted_at")
    try:
        granted = datetime.fromisoformat(granted_at)
    except ValueError as err:
        raise InvalidResponse({"error": f"invalid granted_at {granted_at}"}) from err

    return BusinessProduct(
        product_type=typed_product_type,
        product_id=_str_field(product, "product_id"),
        region=_REGIONS[region],
        customer=BusinessCustomer(id=_str_field(customer, "id"), ref=ref),
        granted_at=granted,
        raw=product,
    )


def parse_business_products(payload: object) -> list[BusinessProduct]:
    """Parse a ``GET /api/business/products`` response body.

    Raises:
        InvalidResponse: The body is ``None`` or not the documented shape.
    """
    if not isinstance(payload, dict) or "response" not in payload:
        raise InvalidResponse({"error": "products response has no response"})
    items = cast("dict[str, Any]", payload)["response"]
    if not isinstance(items, list):
        raise InvalidResponse({"error": "products response is not a list"})
    return [_parse_product(item) for item in cast("list[object]", items)]


class TeslemetryBusiness:
    """Endpoints for a Teslemetry for Business API key (``sk_...``)."""

    def __init__(self, parent: Teslemetry) -> None:
        self._parent = parent

    async def list_products(self) -> dict[str, Any]:
        """Get the raw ``GET /api/business/products`` response."""
        return await self._parent._request(Method.GET, "api/business/products")  # pyright: ignore[reportPrivateUsage]

    async def products(self) -> list[BusinessProduct]:
        """List every product the business's customers have shared with it.

        Each product carries its customer's ``region``. Create one
        ``Teslemetry(..., region=product.region)`` per region to call each
        product on its own region's host.

        Raises:
            InvalidResponse: The response is not the documented shape.
        """
        return parse_business_products(await self.list_products())
