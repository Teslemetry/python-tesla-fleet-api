"""Tesla Fleet API for Python."""

from json import dumps
from typing import Any, Awaitable, Callable
import aiohttp

from tesla_fleet_api.tesla.tesla import Tesla
from tesla_fleet_api.exceptions import raise_for_status, InvalidRegion, LibraryError, ResponseError
from tesla_fleet_api.const import SERVERS, Method, LOGGER, Scope
from tesla_fleet_api import __version__ as VERSION

# Based on https://developer.tesla.com/docs/fleet-api
class TeslaFleetApi(Tesla):
    """Class describing the Tesla Fleet API."""

    access_token: str | None = None
    region: str | None = None
    server: str | None = None
    session: aiohttp.ClientSession
    headers: dict[str, str]
    refresh_hook: Callable[[], Awaitable[str | None]] | None = None

    def __init__(
        self,
        session: aiohttp.ClientSession,
        access_token: str | None = None,
        region: str | None = None,
        server: str | None = None,
        charging_scope: bool = True,
        energy_scope: bool = True,
        partner_scope: bool = True,
        user_scope: bool = True,
        vehicle_scope: bool = True,
        refresh_hook: Callable[[], Awaitable[str | None]] | None = None,
    ):
        """Initialize the Tesla Fleet API."""

        self.session = session
        self.access_token = access_token
        self.refresh_hook = refresh_hook

        if server is not None:
            self.server = server
        elif region is not None:
            if region not in SERVERS:
                raise ValueError(f"Region must be one of {', '.join(SERVERS.keys())}")
            self.server = SERVERS.get(region)

        LOGGER.debug("Using server %s", self.server)

        if charging_scope:
            self.charging = self.Charging(self)
        if energy_scope:
            self.energySites = self.EnergySites(self)
        if user_scope:
            self.user = self.User(self)
        if partner_scope:
            self.partner = self.Partner(self)
        if vehicle_scope:
            self.vehicles = self.Vehicles(self)

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
        json: dict[str, Any] | None = {},
    ) -> dict[str, Any]:
        """Send a request to the Tesla Fleet API."""

        if not self.server:
            raise ValueError("Server was not set at init. Call find_server() first.")

        if method == Method.GET:
            json = None

        # Call a pre-request hook if provided
        if self.refresh_hook is not None:
            if access_token := await self.refresh_hook():
                self.access_token = access_token

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "X-Library": f"python tesla_fleet_api {VERSION}",
        }

        # Remove None values from params and json
        if params:
            params = {k: v for k, v in params.items() if v is not None}
            LOGGER.debug("Parameters: %s", params)
        if json:
            json = {k: v for k, v in json.items() if v is not None}
            LOGGER.debug("Body: %s", dumps(json))
            headers["Content-Type"] = "application/json"

        async with self.session.request(
            method,
            f"{self.server}/{path}",
            headers=headers,
            json=json,
            params=params,
        ) as resp:
            LOGGER.debug("Status %s from %s", resp.status, resp.url)
            if "x-txid" in resp.headers:
                LOGGER.debug("Response TXID: %s", resp.headers["x-txid"])
            if "RateLimit-Reset" in resp.headers:
                LOGGER.debug(
                    "Rate limit reset: %s", resp.headers.get("RateLimit-Reset")
                )
            if "Retry-After" in resp.headers:
                LOGGER.debug("Retry after: %s", resp.headers.get("Retry-After"))

            if not resp.ok:
                await raise_for_status(resp)

            if not resp.content_type.lower().startswith("application/json"):
                LOGGER.debug("Response type is: %s", resp.content_type)
                raise ResponseError(status=resp.status, data=await resp.text())

            data = await resp.json()
            LOGGER.debug("Response JSON: %s", data)
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

    async def partner_login(
        self,
        client_id: str,
        client_secret: str,
        scopes: list[Scope] = [Scope.VEHICLE_DEVICE_DATA],
    ) -> dict[str, Any]:
        """Generate a partner token using client credentials authentication.

        Args:
            client_id: Partner application client ID
            client_secret: Partner application client secret
            scopes: Optional list of scopes to request

        Returns:
            Dictionary containing access token and token metadata
        """

        # Throw if there is no server set
        if not self.server:
            raise ValueError("Server was not set at init. Call find_server() first.")

        data = {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
            "audience": self.server,
            "scope": " ".join(scopes),
        }

        async with self.session.post(
            "https://fleet-auth.prd.vn.cloud.tesla.com/oauth2/v3/token",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data=data,
        ) as resp:
            if resp.ok:
                token_data = await resp.json()
                # Set the access token for subsequent API calls
                self.access_token = token_data["access_token"]
                return token_data
            else:
                error_data = await resp.json()
                raise ValueError(f"Partner login failed: {error_data}")
