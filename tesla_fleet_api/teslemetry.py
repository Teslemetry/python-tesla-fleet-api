from typing import Any

import aiohttp
from aiolimiter import AsyncLimiter

from .const import LOGGER, Method, VehicleDataEndpoint
from .teslafleetapi import TeslaFleetApi

# Rate limit should be global, even if multiple instances are created
rate_limit = AsyncLimiter(5, 10)


class Teslemetry(TeslaFleetApi):
    def __init__(
        self,
        session: aiohttp.ClientSession,
        access_token: str,
    ):
        """Initialize the Teslemetry API."""
        super().__init__(
            session=session,
            access_token=access_token,
            server="https://api.teslemetry.com",
            user_scope=False,
            partner_scope=False,
        )
        self.rate_limit = rate_limit

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

    async def vehicle_force_refresh(self, vin: str) -> dict[str, Any]:
        """Force a refresh of the vehicle data."""
        return await self._request(
            Method.GET,
            f"api/force/{vin}",
        )

    async def vehicle_data_cached(self, vin: str, endpoints: list[VehicleDataEndpoint | str] | None = None,) -> dict[str, Any]:
        """Get cached vehicle data."""
        endpoint_payload = ";".join(endpoints) if endpoints else None
        return await self._request(
            Method.GET,
            f"api/x/vehicles/{vin}/vehicle_data",
            {"endpoints": endpoint_payload}
        )

    async def _request(
        self,
        method: Method,
        path: str,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Send a request to the Teslemetry API."""
        async with rate_limit:
            return await super()._request(method, path, params, json)
