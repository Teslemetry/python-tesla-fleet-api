from typing import Any
from tesla_fleet_api.const import Method


class Charging:
    """Class describing the Tesla Fleet API charging endpoints."""

    def __init__(self, parent):
        self._request = parent._request

    async def history(
        self,
        vin: str | None = None,
        startTime: str | None = None,
        endTime: str | None = None,
        pageNo: int | None = None,
        pageSize: int | None = None,
        sortBy: str | None = None,
        sortOrder: str | None = None,
    ) -> dict[str, Any]:
        """Returns the paginated charging history."""
        return await self._request(
            Method.GET,
            "api/1/dx/charging/history",
            {
                "vin": vin,
                "startTime": startTime,
                "endTime": endTime,
                "pageNo": pageNo,
                "pageSize": pageSize,
                "sortBy": sortBy,
                "sortOrder": sortOrder,
            },
        )

    async def sessions(
        self,
        vin: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """Returns the charging session information including pricing and energy data. This endpoint is only available for business accounts that own a fleet of vehicles."""
        return await self._request(
            Method.GET,
            "api/1/dx/charging/sessions",
            {
                "vin": vin,
                "date_from": date_from,
                "date_to": date_to,
                "limit": limit,
                "offset": offset,
            },
        )
