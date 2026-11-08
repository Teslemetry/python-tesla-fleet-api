from collections.abc import Awaitable, Callable
from typing import Literal, NotRequired, TypedDict, cast

import aiohttp

from tesla_fleet_api.const import Method
from tesla_fleet_api.tesla import TeslaFleetApi


class BusinessProduct(TypedDict):
    """One product a customer has consented to share with the business."""

    type: Literal["vehicle", "energy"]
    vin: NotRequired[str]
    energy_site_id: NotRequired[int]
    customer: str
    granted_at: str
    ref: str | None
    name: str | None
    available: bool | None
    access: str
    permission: NotRequired[Literal["OWNER", "DRIVER", "GUEST"] | None]
    state: NotRequired[str | None]
    issue: NotRequired[Literal["no_data", "streaming_toggle", "key", "scope"] | None]
    signing: NotRequired[bool | None]
    fleet_telemetry: NotRequired[str | None]
    firmware: NotRequired[str | None]


class BusinessProducts(TypedDict):
    """One page of consented products."""

    response: list[BusinessProduct]
    count: int
    next_cursor: str | None


class TeslemetryBusiness(TeslaFleetApi):
    """Teslemetry for Business API, authenticated with a business token."""

    _transport_name = "teslemetry_business"

    def __init__(
        self,
        session: aiohttp.ClientSession,
        access_token: str | Callable[[], Awaitable[str | None]],
        server: str = "https://api.teslemetry.pro",
    ) -> None:
        super().__init__(
            session,
            access_token,
            server=server,
            charging_scope=False,
            energy_scope=False,
            partner_scope=False,
            user_scope=False,
            vehicle_scope=False,
        )

    async def products(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        type: Literal["vehicle", "energy"] | None = None,
        ref: str | None = None,
        since: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> BusinessProducts:
        """Return one page of the products customers have consented to share.

        Pass the previous page's ``next_cursor`` as ``cursor`` to get the next
        page; it is ``None`` on the last page. ``since`` is an ISO 8601 time.
        """
        return cast(
            BusinessProducts,
            await self._request(
                Method.GET,
                "api/business/products",
                params={
                    "type": type,
                    "ref": ref,
                    "since": since,
                    "limit": limit,
                    "cursor": cursor,
                },
            ),
        )
