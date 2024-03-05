import aiohttp
from aiolimiter import AsyncLimiter
from typing import Any
from .teslafleetapi import TeslaFleetApi
from .const import Method

# Rate limit should be global, even if multiple instances are created
rate_limit = AsyncLimiter(5, 10)


class Teslemetry(TeslaFleetApi):
    def __init__(
        self,
        session: aiohttp.ClientSession,
        access_token: str,
        raise_for_status: bool = True,
    ):
        """Initialize the Teslemetry API."""
        super().__init__(
            session,
            access_token,
            server="https://api.teslemetry.com",
            raise_for_status=raise_for_status,
            partner_scope=False,
            user_scope=False,
        )
        self.rate_limit = rate_limit

    async def ping(self) -> bool:
        """Send a ping."""
        return await self._request(
            Method.GET,
            "api/ping",
        )

    async def test(self) -> bool:
        """Test API Authentication."""
        return await self._request(
            Method.GET,
            "api/test",
        )

    async def metadata(self) -> bool:
        """Test API Authentication."""
        return await self._request(
            Method.GET,
            "api/metadata",
        )

    async def find_server(self):
        """Find the server URL for the Tesla Fleet API."""
        raise NotImplementedError("Do not use this function for Teslemetry.")

    async def _request(
        self,
        method: Method,
        path: str,
        params: dict[str:Any] | None = None,
        json: dict[str:Any] | None = None,
    ):
        """Send a request to the Teslemetry API."""
        async with rate_limit:
            return await super()._request(method, path, params, json)
