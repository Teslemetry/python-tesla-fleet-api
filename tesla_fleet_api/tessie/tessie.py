from typing import Any

import aiohttp

from tesla_fleet_api.const import Method
from tesla_fleet_api.tesla import TeslaFleetApi
from tesla_fleet_api.tessie.vehicles import TessieVehicles


class Tessie(TeslaFleetApi):
    server = "https://api.tessie.com"
    Vehicles = TessieVehicles

    def __init__(
        self,
        session: aiohttp.ClientSession,
        access_token: str,
    ):
        """Initialize the Tessie API."""

        self.session = session
        self._access_token = access_token

        self.charging = self.Charging(self)
        self.energySites = self.EnergySites(self)
        self.user = self.User(self)
        self.vehicles = self.Vehicles(self)

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

    async def states(
        self,
        vin: str,
        start: int | None = None,
        end: int | None = None,
        results: int | None = None,
        page: int | None = None,
        exclude: str | None = None,
        fields: str | None = None,
    ) -> Any:
        """Get historical vehicle states within timeframe."""
        return await self._request(
            Method.GET,
            f"{vin}/states",
            params={
                "from": start,
                "to": end,
                "results": results,
                "page": page,
                "exclude": exclude,
                "fields": fields,
            },
        )

    async def location(self, vin: str) -> Any:
        """Get coordinates, address, and saved location."""
        return await self._request(Method.GET, f"{vin}/location")

    async def firmware_alerts(self, vin: str) -> Any:
        """Get list of firmware-generated alerts."""
        return await self._request(Method.GET, f"{vin}/firmware_alerts")

    async def map(
        self,
        vin: str,
        width: int | None = None,
        height: int | None = None,
        zoom: int | None = None,
    ) -> Any:
        """Get map image of vehicle location."""
        return await self._request(
            Method.GET,
            f"{vin}/map",
            params={"width": width, "height": height, "zoom": zoom},
        )

    async def consumption_since_charge(self, vin: str) -> Any:
        """Get energy use data since last charge."""
        return await self._request(Method.GET, f"{vin}/consumption_since_charge")

    async def weather(self, vin: str) -> Any:
        """Get weather forecast around vehicle."""
        return await self._request(Method.GET, f"{vin}/weather")

    async def drives(
        self,
        vin: str,
        start: int | None = None,
        end: int | None = None,
        results: int | None = None,
        page: int | None = None,
        timezone: str | None = None,
        distance_format: str | None = None,
    ) -> Any:
        """Get historical drive records."""
        return await self._request(
            Method.GET,
            f"{vin}/drives",
            params={
                "from": start,
                "to": end,
                "results": results,
                "page": page,
                "timezone": timezone,
                "distance_format": distance_format,
            },
        )

    async def path(
        self,
        vin: str,
        start: int,
        end: int,
        timezone: str | None = None,
    ) -> Any:
        """Get driving route during specified timeframe."""
        return await self._request(
            Method.GET,
            f"{vin}/path",
            params={"from": start, "to": end, "timezone": timezone},
        )

    async def charges(
        self,
        vin: str,
        start: int | None = None,
        end: int | None = None,
        results: int | None = None,
        page: int | None = None,
        timezone: str | None = None,
        distance_format: str | None = None,
    ) -> Any:
        """Get charging history."""
        return await self._request(
            Method.GET,
            f"{vin}/charges",
            params={
                "from": start,
                "to": end,
                "results": results,
                "page": page,
                "timezone": timezone,
                "distance_format": distance_format,
            },
        )

    async def charging_invoices(
        self,
        start: int | None = None,
        end: int | None = None,
        only_active: bool = False,
    ) -> Any:
        """Get charging costs for all vehicles (fleet)."""
        return await self._request(
            Method.GET,
            "charging_invoices",
            params={"from": start, "to": end, "only_active": only_active},
        )

    async def idles(
        self,
        vin: str,
        start: int | None = None,
        end: int | None = None,
        results: int | None = None,
        page: int | None = None,
        timezone: str | None = None,
    ) -> Any:
        """Get idle periods when vehicle inactive."""
        return await self._request(
            Method.GET,
            f"{vin}/idles",
            params={
                "from": start,
                "to": end,
                "results": results,
                "page": page,
                "timezone": timezone,
            },
        )

    async def last_idle_state(self, vin: str) -> Any:
        """Get latest idle period data."""
        return await self._request(Method.GET, f"{vin}/last_idle_state")
