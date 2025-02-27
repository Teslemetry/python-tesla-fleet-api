from typing import Any

import aiohttp

from tesla_fleet_api.tesla.charging import Charging
from tesla_fleet_api.tesla.energysite import EnergySites
from tesla_fleet_api.tesla.user import User
from tesla_fleet_api.teslemetry.vehicles import TeslemetryVehicles
from tesla_fleet_api.const import LOGGER, Method
from tesla_fleet_api.tesla import TeslaFleetApi

class Teslemetry(TeslaFleetApi):

    server = "https://api.teslemetry.com"

    def __init__(
        self,
        session: aiohttp.ClientSession,
        access_token: str,
    ):
        """Initialize the Teslemetry API."""

        self.session = session
        self.access_token = access_token

        self.charging = Charging(self)
        self.energySites = EnergySites(self)
        self.user = User(self)
        self.vehicles = TeslemetryVehicles(self)

    async def ping(self) -> dict[str, bool]:
        """Send a ping."""
        return await self._request(
            Method.GET,
            "api/ping",
        )

    async def test(self) -> dict[str, bool]:
        """Test API Authentication."""
        return await self._request(
            Method.GET,
            "api/test",
        )

    async def userdata(self) -> dict[str, Any]:
        """Get userdata."""
        resp = await self._request(
            Method.GET,
            "api/userdata",
        )
        return resp

    async def metadata(self, update_region=True) -> dict[str, Any]:
        """Get user metadata including scopes."""
        resp = await self._request(
            Method.GET,
            "api/metadata",
        )
        if update_region and "region" in resp:
            self.region = resp["region"].lower()
            self.server = f"https://{self.region}.teslemetry.com"
            LOGGER.debug("Using server %s", self.server)
        return resp

    async def scopes(self) -> list[str]:
        """Get user scopes."""
        resp = await self.metadata(False)
        return resp["scopes"]

    async def find_server(self) -> str:
        """Find the server URL for the Tesla Fleet API."""
        await self.metadata(True)
        assert self.region
        return self.region

    async def server_side_polling(
        self, vin: str, value: bool | None = None
    ) -> bool | None:
        """Get or set Auto mode."""
        if value is True:
            return (
                await self._request(
                    Method.POST,
                    f"api/auto/{vin}",
                )
            ).get("response")
        if value is False:
            return (
                await self._request(
                    Method.DELETE,
                    f"api/auto/{vin}",
                )
            ).get("response")
        return (
            await self._request(
                Method.GET,
                f"api/auto/{vin}",
            )
        ).get("response")

    async def vehicle_data_refresh(self, vin: str) -> dict[str, Any]:
        """Force a refresh of the vehicle data."""
        return await self._request(
            Method.GET,
            f"api/refresh/{vin}",
        )
