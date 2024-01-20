import aiohttp
from .exceptions import raise_for_status, InvalidRegion, LibraryError
from typing import Any
from .const import SERVERS, Methods, Errors
from .charging import Charging
from .energy import Energy
from .partner import Partner
from .user import User
from .vehicle import Vehicle
from .vehiclespecific import VehicleSpecific


# Based on https://developer.tesla.com/docs/fleet-api
class TeslaFleetApi:
    """Class describing the Tesla Fleet API."""

    server: str
    session: aiohttp.ClientSession
    headers: dict[str, str]
    raise_for_status: bool
    vehicles: list[VehicleSpecific]

    def __init__(
        self,
        session: aiohttp.ClientSession,
        access_token: str,
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

        if region and not server and region not in SERVERS:
            raise ValueError(f"Region must be one of {', '.join(SERVERS.keys())}")
        self.server = server or SERVERS.get(region)
        self.raise_for_status = raise_for_status

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
                response = await (self.user.region()).get("response")
                if response:
                    self.server = response["fleet_api_base_url"]
                    return response["region"]
            except InvalidRegion:
                continue
        raise LibraryError("Could not find a valid Tesla API server.")

    async def _request(
        self,
        method: Methods,
        path: str,
        params: dict[str:Any] | None = None,
        data: dict[str:Any] | None = None,
        json: dict[str:Any] | None = None,
    ):
        """Send a request to the Tesla Fleet API."""

        if not self.server:
            raise ValueError("Server was not set at init. Call find_server() first.")

        if method == Methods.GET and (data is not None or json is not None):
            raise ValueError("GET requests cannot have data or json parameters.")

        if params:
            params = {k: v for k, v in params.items() if v is not None}
        if data:
            data = {k: v for k, v in data.items() if v is not None}
        if json:
            json = {k: v for k, v in json.items() if v is not None}

        async with self.session.request(
            method,
            f"{self.server}/{path}",
            headers={
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json",
            },
            data=data,
            json=json,
            params=params,
        ) as resp:
            if self.raise_for_status:
                await raise_for_status(resp)
            elif not resp.content_length:
                # Manufacture a response since Tesla doesn't provide a body for token expiration.
                return {
                    "response": None,
                    "error": Errors.INVALID_TOKEN,
                    "error_message": "The OAuth token has expired.",
                }
            return await resp.json()

    async def status(self):
        """This endpoint returns the string "ok" if the API is operating normally. No HTTP headers are required."""
        if not self.server:
            raise ValueError("Server was not set at init. Call find_server() first.")
        async with self.session.get(f"{self.server}/status") as resp:
            return await resp.text()

    async def products(self) -> dict[str, Any]:
        """Returns products mapped to user."""
        return await self._request(
            Methods.GET,
            "api/1/products",
        )
