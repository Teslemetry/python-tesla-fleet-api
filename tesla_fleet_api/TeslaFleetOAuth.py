import aiohttp
from .TeslaFleetApi import TeslaFleetApi


class TeslaFleetOAuth(TeslaFleetApi):
    """Tesla Fleet OAuth API."""

    def __init__(
        self,
        refresh_token: str,
        client_id: str,
        session: aiohttp.ClientSession,
        raise_for_status: bool = True,
    ):
        super().__init__(
            refresh_token,
            "https://fleet-api.prd.na.vn.cloud.tesla.com",
            session,
            raise_for_status,
        )
