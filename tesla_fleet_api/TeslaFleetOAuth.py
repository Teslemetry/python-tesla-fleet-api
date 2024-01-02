import aiohttp
from .TeslaFleetApi import TeslaFleetApi


class TeslaFleetOAuth(TeslaFleetApi):
    """Tesla Fleet OAuth API."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        refresh_token: str,
        client_id: str,
        server: str | None = None,
        raise_for_status: bool = True,
    ):
        super().__init__(
            session,
            refresh_token,
            server,
            raise_for_status,
        )
