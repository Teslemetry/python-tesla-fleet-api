"""Tesla Fleet API for Python."""

from json import dumps
from typing import Any, Awaitable
from os.path import exists
import aiohttp
import aiofiles

# cryptography
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

from .exceptions import raise_for_status, InvalidRegion, LibraryError, ResponseError
from .const import SERVERS, Method, LOGGER, VERSION
from .charging import Charging
from .energy import Energy
from .partner import Partner
from .user import User
from .vehicle import Vehicle


# Based on https://developer.tesla.com/docs/fleet-api
class TeslaFleetApi:
    """Class describing the Tesla Fleet API."""

    access_token: str | None = None
    region: str | None = None
    server: str | None = None
    session: aiohttp.ClientSession
    headers: dict[str, str]
    refresh_hook: Awaitable | None = None
    private_key: ec.EllipticCurvePrivateKey | None = None

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
        refresh_hook: Awaitable | None = None,
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
    ) -> dict[str, Any]:
        """Send a request to the Tesla Fleet API."""

        if not self.server:
            raise ValueError("Server was not set at init. Call find_server() first.")

        if method == Method.GET and json is not None:
            raise ValueError("GET requests cannot have a body.")

        # Call a pre-request hook if provided
        if self.refresh_hook is not None:
            if access_token := await self.refresh_hook():
                self.access_token = access_token

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
                "X-Library": f"python tesla_fleet_api {VERSION}",
            },
            json=json,
            params=params,
        ) as resp:
            LOGGER.debug("Requested: %s", resp.url)
            LOGGER.debug("Response Status: %s", resp.status)
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

    async def get_private_key(
        self, path: str = "private_key.pem"
    ) -> ec.EllipticCurvePrivateKey:
        """Get or create the private key."""
        if not exists(path):
            self.private_key = ec.generate_private_key(
                ec.SECP256R1(), default_backend()
            )
            # save the key
            pem = self.private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption(),
            )
            async with aiofiles.open(path, "wb") as key_file:
                await key_file.write(pem)
        else:
            try:
                async with aiofiles.open(path, "rb") as key_file:
                    key_data = await key_file.read()
                value = serialization.load_pem_private_key(
                    key_data, password=None, backend=default_backend()
                )
            except FileNotFoundError:
                raise FileNotFoundError(f"Private key file not found at {path}")
            except PermissionError:
                raise PermissionError(f"Permission denied when trying to read {path}")

            if not isinstance(value, ec.EllipticCurvePrivateKey):
                raise AssertionError("Loaded key is not an EllipticCurvePrivateKey")
            self.private_key = value
        return self.private_key

    @property
    def has_private_key(self) -> bool:
        """Check if the private key has been set."""
        return self.private_key is not None
