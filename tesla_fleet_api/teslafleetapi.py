import aiohttp

from json import dumps
from .exceptions import raise_for_status, InvalidRegion, LibraryError, InvalidToken
from typing import Any
from .const import SERVERS, Method, LOGGER, VERSION
from .charging import Charging
from .energy import Energy
from .partner import Partner
from .user import User
from .vehicle import Vehicle


# Based on https://developer.tesla.com/docs/fleet-api
class TeslaFleetApi:
    """Class describing the Tesla Fleet API."""

    server: str | None = None
    session: aiohttp.ClientSession
    headers: dict[str, str]
    raise_for_status: bool

    def __init__(
        self,
        session: aiohttp.ClientSession,
        access_token: str | None = None,
        region: str | None = None,
        server: str | None = None,
        raise_for_status: bool = True,
        charging_scope: bool = True,
        energy_scope: bool = True,
        partner_scope: bool = True,
        user_scope: bool = True,
        vehicle_scope: bool = True,
    ):
        """Initialize the Tesla Fleet API."""

        self.session = session
        self.access_token = access_token
        self.raise_for_status = raise_for_status

        if server is not None:
            self.server = server
        elif region is not None:
            if region not in SERVERS:
                raise ValueError(f"Region must be one of {', '.join(SERVERS.keys())}")
            self.server = SERVERS.get(region)
        else:
            raise ValueError("Either server or region must be provided.")

        LOGGER.debug("Using server %s", self.server)

        if charging_scope:
            self.charging = Charging(self)
        if energy_scope:
            self.energy = Energy(self)
        if user_scope:
            self.user = User(self)
        if partner_scope:
            self.partner = Partner(self)
        if vehicle_scope:
            self.vehicle = Vehicle(self)

    async def find_server(self) -> str:
        """Find the server URL for the Tesla Fleet API."""
        for server in SERVERS.values():
            self.server = server
            try:
                region_response = await self.user.region()
                response = region_response.get("response")
                if response:
                    self.server = response["fleet_api_base_url"]
                    LOGGER.debug("Using server %s", self.server)
                    return response["region"]
            except InvalidRegion:
                continue
        raise LibraryError("Could not find a valid Tesla API server.")

    async def _request(
        self,
        method: Method,
        path: str,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> dict[str, Any] | str:
        """Send a request to the Tesla Fleet API."""

        if not self.server:
            raise ValueError("Server was not set at init. Call find_server() first.")

        if method == Method.GET and json is not None:
            raise ValueError("GET requests cannot have a body.")

        LOGGER.debug("Sending request to %s", path)

        # Remove None values from params and json
        if params:
            params = {k: v for k, v in params.items() if v is not None}
            LOGGER.debug("Parameters: %s", params)
        if json:
            json = {k: v for k, v in json.items() if v is not None}
            LOGGER.debug("Body: %s", dumps(json))

        async with self.session.request(
            method,
            f"{self.server}/{path}",
            headers={
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json",
                "X-Library": f"python tesla_fleet_api ${VERSION}",
            },
            json=json,
            params=params,
        ) as resp:
            LOGGER.debug("Response Status: %s", resp.status)
            if self.raise_for_status and not resp.ok:
                await raise_for_status(resp)
            elif resp.status == 401 and resp.content_type != "application/json":
                # Manufacture a response since Tesla doesn't provide a body for token expiration.
                return {
                    "response": None,
                    "error": InvalidToken.key,
                    "error_message": "The OAuth token has expired.",
                }
            if resp.content_type == "application/json":
                data = await resp.json()
                LOGGER.debug("Response JSON: %s", data)
                return data

            data = await resp.text()
            LOGGER.debug("Response Text: %s", data)
            return data

    async def status(self) -> str:
        """This endpoint returns the string "ok" if the API is operating normally. No HTTP headers are required."""
        if not self.server:
            raise ValueError("Server was not set at init. Call find_server() first.")
        async with self.session.get(f"{self.server}/status") as resp:
            return await resp.text()

    async def products(self) -> dict[str, Any]:
        """Returns products mapped to user."""
        return await self._request(
            Method.GET,
            "api/1/products",
        )
