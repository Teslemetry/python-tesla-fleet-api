import aiohttp
from . import TeslaFleetApi


class Teslemetry(TeslaFleetApi):
    def __init__(self, access_token: str, session: aiohttp.ClientSession | None = None):
        """Initialize the Teslemetry API."""
        super().__init__(access_token, "https://teslemetry.com", session)
