from collections.abc import Awaitable, Callable
from time import time
from typing import Any

import aiohttp

from tesla_fleet_api.const import LOGGER, Method
from tesla_fleet_api.tesla import TeslaFleetApi
from tesla_fleet_api.teslemetry.vehicles import TeslemetryVehicles


class Teslemetry(TeslaFleetApi):
    Vehicles = TeslemetryVehicles

    def __init__(
        self,
        session: aiohttp.ClientSession,
        access_token: str | Callable[[], Awaitable[str | None]],
        server: str = "https://api.teslemetry.com",
    ):
        """Initialize the Teslemetry API."""

        self.session = session
        self.access_token = access_token
        self.server = server

        self.charging = self.Charging(self)
        self.energySites = self.EnergySites(self)
        self.user = self.User(self)
        self.vehicles = self.Vehicles(self)

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

    async def metadata(self, update_region: bool = True) -> dict[str, Any]:
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

    async def migrate_to_oauth(
        self, client_id: str = "homeassistant", name: str | None = None
    ) -> dict[str, Any]:
        """Migrate from access token to OAuth."""
        access_token = await self._access_token()
        migrate_data = {
            "grant_type": "migrate",
            "client_id": client_id,
            "access_token": access_token.strip(),
            "name": name,
        }

        new_token = await self._request(Method.POST, "oauth/token", json=migrate_data)
        new_token["expires_in"] = int(new_token["expires_in"])
        new_token["expires_at"] = time() + new_token["expires_in"]
        return new_token
