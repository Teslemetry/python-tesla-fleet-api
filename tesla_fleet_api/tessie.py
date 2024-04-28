import aiohttp
from typing import Any
from .teslafleetapi import TeslaFleetApi
from .const import Method


class Tessie(TeslaFleetApi):
    def __init__(
        self,
        session: aiohttp.ClientSession,
        access_token: str,
        raise_for_status: bool = True,
    ):
        """Initialize the Tessie API."""
        super().__init__(
            session,
            access_token,
            server="https://api.tessie.com",
            raise_for_status=raise_for_status,
            partner_scope=False,
            user_scope=False,
            energy_scope=False,
        )

    async def find_server(self) -> str:
        """Find the server URL for the Tesla Fleet API."""
        raise NotImplementedError("Do not use this function for Tessie.")

    async def vehicles(self, only_active: bool = False) -> Any:
        """Get vehicles."""
        return await self._request(
            Method.GET, "vehicles", params={"only_active": only_active}
        )

    async def state(self, vin: str) -> Any:
        """Get vehicle data."""
        return await self._request(Method.GET, f"{vin}/state")

    async def battery(self, vin: str) -> Any:
        """Get battery data."""
        return await self._request(Method.GET, f"{vin}/battery")

    async def battery_health(
        self,
        vin: str,
        start: int | None = None,
        end: int | None = None,
        distance_format: str | None = None,
    ) -> Any:
        """Get battery health data."""
        return await self._request(
            Method.GET,
            f"{vin}/battery_health",
            params={"from": start, "to": end, "distance_format": distance_format},
        )

    async def all_battery_health(
        self,
        start: int | None = None,
        end: int | None = None,
        distance_format: str | None = None,
        only_active: bool = False,
    ) -> Any:
        """Get battery health data."""
        return await self._request(
            Method.GET,
            "battery_health",
            params={
                "from": start,
                "to": end,
                "distance_format": distance_format,
                "only_active": only_active,
            },
        )
