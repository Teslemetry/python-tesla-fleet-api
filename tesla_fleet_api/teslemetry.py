import aiohttp
from .teslafleetapi import TeslaFleetApi
from .const import Methods


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
            use_command_protocol=False,
            server="https://teslemetry.com",
            raise_for_status=raise_for_status,
            partner_scope=False,
            user_scope=False,
        )

    async def subscription_status(self) -> bool:
        """Get the subscribed vehicles."""
        return await self._request(
            Methods.GET,
            "/api/subscription/active",
        )

    async def find_server(self):
        """Find the server URL for the Tesla Fleet API."""
        raise NotImplementedError("Do not use this function for Teslemetry.")
