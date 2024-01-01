import aiohttp
from .exceptions import raise_for_status
from typing import Any

# Based on https://developer.tesla.com/docs/fleet-api
class TeslaFleetApi:
    """Class describing the Tesla Fleet API."""

    server: str
    session: aiohttp.ClientSession
    headers: dict[str, str]
    raise_for_status: bool

    def __init__(
        self,
        access_token: str,
        server: str,
        session: aiohttp.ClientSession | None = None,
        raise_for_status: bool = True,
    ):
        """Initialize the Tesla Fleet API."""
        self.server = server
        self.session = session or aiohttp.ClientSession()
        self.headers = {"Authorization": f"Bearer {access_token}"}
        self.raise_for_status = raise_for_status

    async def _get(self, path, params:dict[str:Any] = {}, raise_for_status: bool = None):
        """Get data from the Tesla Fleet API."""
        params = {k: v for k, v in params.items() if v is not None}

        async with self.session.get(
            f"{self.server}/{path}",
            params=params,
            headers=self.headers,
        ) as resp:
            if raise_for_status is True or self.raise_for_status:
                await raise_for_status(resp)
            return await resp.json()

    async def _post(self, path, data: dict):
        """Post data to the Tesla Fleet API with URL encoded data."""

        async with self.session.post(
            f"{self.server}/{path}",
            headers=self.headers,
            data=data,
        ) as resp:
            if self.raise_for_status:
                await raise_for_status(resp)
            return await resp.json()

    async def status(self):
        """This endpoint returns the string "ok" if the API is operating normally. No HTTP headers are required."""
        async with self.session.get(
            f"{self.server}/status"
        ) as resp:
            return await resp.text()

    class charging:
        """Class describing the Tesla Fleet API charging endpoints."""

        async def history(self, vin:str|None = None, startTime:str|None = None, endTime:str|None = None, pageNo:int|None = None, pageSize:int|None = None, sortBy:str|None = None, sortOrder:str|None = None):
            """Returns the paginated charging history."""
            return await self._get("/api/1/dx/charging/history", {vin, startTime, endTime, pageNo, pageSize, sortBy, sortOrder})
        
        async def sessions(self, vin:str|None = None, date_from:str|None = None, date_to:str|None = None, limit:int|None = None, offset:int|None = None):
            """Returns the charging session information including pricing and energy data. This endpoint is only available for business accounts that own a fleet of vehicles."""
            return await self._get("/api/1/dx/charging/sessions", {vin, date_from, date_to, limit, offset})
        
    class partner:
        """Class describing the Tesla Fleet API partner endpoints"""

        async def public_key(self, domain:str|None = None):
            """Returns the public key associated with a domain. It can be used to ensure the registration was successful."""
            return await self._get("/api/1/partner_accounts/public_key", {domain})
        
        async def register(self, domain:str):
            """Registers an existing account before it can be used for general API access. Each application from developer.tesla.com must complete this step."""
            return await self._post("/api/1/partner_accounts", {domain})
        
    class user:
        """Class describing the Tesla Fleet API user endpoints"""

        async def backup_key(self):
           """Returns the public key associated with the user."""
           return await self._get("/api/1/users/backup_key")
       
        async def feature_config(self):
            """Returns any custom feature flag applied to a user."""
            return await self._get("/api/1/users/feature_config")
       
        async def me(self):
            """Returns a summary of a user's account."""
            return await self._get("/api/1/users/me")
       
        async def orders(self):
            """Returns the active orders for a user."""
            return await self._get("/api/1/users/orders")
       
        async def region(self):
            """Returns a user's region and appropriate fleet-api base URL. Accepts no parameters, response is based on the authentication token subject."""
            return await self._get("/api/1/users/region")

