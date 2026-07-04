from typing import Any

import aiohttp

from tesla_fleet_api.const import Method
from tesla_fleet_api.tesla import TeslaFleetApi
from tesla_fleet_api.tessie.vehicle import TessieVehicles


class Tessie(TeslaFleetApi):
    server = "https://api.tessie.com"
    vehicles: TessieVehicles
    Vehicles = TessieVehicles

    def __init__(
        self,
        session: aiohttp.ClientSession,
        access_token: str,
        wait_for_completion: bool = True,
        max_attempts: int = 3,
    ):
        """Initialize the Tessie API."""

        self.session = session
        self._access_token = access_token
        self.wait_for_completion = wait_for_completion
        self.max_attempts = max_attempts

        self.charging = self.Charging(self)
        self.energySites = self.EnergySites(self)
        self.user = self.User(self)
        self.vehicles = self.Vehicles(self)  # pyright: ignore

    async def scopes(self) -> list[str]:
        """Get user scopes."""
        resp = await self._request(
            Method.GET,
            "auth/tesla_scopes",
        )
        return resp["scopes"]

    async def find_server(self) -> str:
        """Find the server URL for the Tesla Fleet API."""
        raise NotImplementedError("Do not use this function for Tessie.")

    async def list_vehicles(self, only_active: bool = False) -> Any:
        """Get vehicles."""
        return await self._request(
            Method.GET, "vehicles", params={"only_active": only_active}
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

    async def charging_invoices(
        self,
        start: int | None = None,
        end: int | None = None,
        timezone: str | None = None,
        vin: str | None = None,
        format: str | None = None,
        only_active: bool | None = None,
    ) -> Any:
        """Get charging costs for all vehicles (fleet)."""
        return await self._request(
            Method.GET,
            "charging_invoices",
            params={
                "from": start,
                "to": end,
                "timezone": timezone,
                "vin": vin,
                "format": format,
                "only_active": only_active,
            },
        )
