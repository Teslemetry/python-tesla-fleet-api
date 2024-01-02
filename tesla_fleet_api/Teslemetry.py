import aiohttp
from .TeslaFleetApi import TeslaFleetApi


class Teslemetry(TeslaFleetApi):
    def __init__(
        self, session: aiohttp.ClientSession, access_token: str, raise_for_status: bool
    ):
        """Initialize the Teslemetry API."""
        super().__init__(
            session,
            access_token,
            use_command_protocol=False,
            server="https://teslemetry.com",
            raise_for_status=raise_for_status,
        )

    async def find_server(self):
        """Find the server URL for the Tesla Fleet API."""
        raise NotImplementedError("Do not use this function for Teslemetry.")
