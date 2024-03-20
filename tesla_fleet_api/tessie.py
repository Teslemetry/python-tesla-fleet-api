import aiohttp
from typing import Any
from .teslafleetapi import TeslaFleetApi
from .const import Method


class Tessie(TeslaFleetApi):
    def __init__(
        self,
        session: aiohttp.ClientSession,
        access_token: str,
        raise_for_status: bool = True,
    ):
        """Initialize the Tessie API."""
        super().__init__(
            session,
            access_token,
            server="https://api.tessie.com",
            raise_for_status=raise_for_status,
            partner_scope=False,
            user_scope=False,
            energy_scope=False,
        )

    async def find_server(self):
        """Find the server URL for the Tesla Fleet API."""
        raise NotImplementedError("Do not use this function for Tessie.")
