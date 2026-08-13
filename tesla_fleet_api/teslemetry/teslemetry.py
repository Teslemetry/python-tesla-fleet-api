from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from time import time
from typing import Any, Final, cast

import aiohttp

from tesla_fleet_api.const import LOGGER, Method, is_valid_region
from tesla_fleet_api.exceptions import TeslemetryRegistrationError
from tesla_fleet_api.tesla import TeslaFleetApi
from tesla_fleet_api.teslemetry.energysite import TeslemetryEnergySites
from tesla_fleet_api.teslemetry.vehicle import TeslemetryVehicles

REGISTER_URL: Final = "https://api.teslemetry.com/oauth/register"


@dataclass(frozen=True, slots=True)
class TeslemetryClientRegistration:
    """Parsed result of :func:`register_client`.

    ``client_id`` is the OAuth client identifier this installation should
    present for every future authorization, including reauthentication.
    ``raw`` is the full decoded registration response for anything this
    wrapper doesn't model.
    """

    client_id: str
    raw: dict[str, Any]


async def register_client(
    session: aiohttp.ClientSession,
    client_name: str,
    software_id: str,
    software_version: str,
) -> TeslemetryClientRegistration:
    """Dynamically register an OAuth client with Teslemetry (RFC 7591).

    Posts to Teslemetry's client-registration endpoint and parses the
    result. This is a bare transport call - it always registers a new
    client and has no knowledge of whether the caller already has one;
    callers are responsible for persisting the returned ``client_id`` and
    skipping registration on subsequent runs.

    Args:
        session: An aiohttp session to issue the request on.
        client_name: Human-readable client name shown during consent.
        software_id: Identifier for the calling application.
        software_version: Version string for the calling application.

    Returns:
        The parsed registration result.

    Raises:
        TeslemetryRegistrationError: The endpoint could not be reached, the
            response was not valid JSON, or the response didn't contain a
            usable ``client_id``.
    """
    try:
        async with session.post(
            REGISTER_URL,
            json={
                "client_name": client_name,
                "software_id": software_id,
                "software_version": software_version,
            },
        ) as response:
            response.raise_for_status()
            registration = await response.json()
    except (aiohttp.ClientError, TimeoutError) as err:
        raise TeslemetryRegistrationError(
            "Could not reach Teslemetry to register a client",
            status=getattr(err, "status", None),
        ) from err
    except ValueError as err:
        raise TeslemetryRegistrationError(
            "Teslemetry returned a malformed registration response"
        ) from err

    registration_dict = (
        cast("dict[str, Any]", registration) if isinstance(registration, dict) else None
    )
    client_id = registration_dict.get("client_id") if registration_dict else None
    if not isinstance(client_id, str) or not client_id:
        raise TeslemetryRegistrationError(
            "Teslemetry registration response did not contain a client_id"
        )

    return TeslemetryClientRegistration(
        client_id=client_id, raw=registration_dict or {}
    )


class Teslemetry(TeslaFleetApi):
    vehicles: TeslemetryVehicles
    Vehicles = TeslemetryVehicles
    EnergySites = TeslemetryEnergySites
    _transport_name = "teslemetry"

    def __init__(
        self,
        session: aiohttp.ClientSession,
        access_token: str | Callable[[], Awaitable[str | None]],
        server: str = "https://api.teslemetry.com",
    ):
        """Initialize the Teslemetry API."""

        self.session = session
        self._access_token = access_token
        self.server = server

        self.charging = self.Charging(self)
        self.energySites = self.EnergySites(self)
        self.user = self.User(self)
        self.vehicles = self.Vehicles(self)  # pyright: ignore

    async def ping(self) -> dict[str, bool]:
        """Send a ping."""
        return await self._request(
            Method.GET,
            "api/ping",
        )

    async def test(self) -> dict[str, bool]:
        """Test API Authentication."""
        return await self._request(
            Method.GET,
            "api/test",
        )

    async def userdata(self) -> dict[str, Any]:
        """Get userdata."""
        resp = await self._request(
            Method.GET,
            "api/userdata",
        )
        return resp

    async def metadata(self, update_region: bool = True) -> dict[str, Any]:
        """Get user metadata including scopes."""
        resp = await self._request(
            Method.GET,
            "api/metadata",
        )
        if update_region and "region" in resp:
            region = resp["region"].lower()
            if is_valid_region(region):
                self.region = region
            self.server = f"https://{region}.teslemetry.com"
            LOGGER.debug("Using server %s", self.server)
        return resp

    async def scopes(self) -> list[str]:
        """Get user scopes."""
        resp = await self.metadata(False)
        return resp["scopes"]

    async def find_server(self) -> str:
        """Find the server URL for the Tesla Fleet API."""
        await self.metadata(True)
        assert self.region
        return self.region

    async def server_side_polling(
        self, vin: str, value: bool | None = None
    ) -> bool | None:
        """Get or set Auto mode."""
        if value is True:
            return (
                await self._request(
                    Method.POST,
                    f"api/auto/{vin}",
                )
            ).get("response")
        if value is False:
            return (
                await self._request(
                    Method.DELETE,
                    f"api/auto/{vin}",
                )
            ).get("response")
        return (
            await self._request(
                Method.GET,
                f"api/auto/{vin}",
            )
        ).get("response")

    async def vehicle_data_refresh(self, vin: str) -> dict[str, Any]:
        """Force a refresh of the vehicle data."""
        return await self._request(
            Method.GET,
            f"api/refresh/{vin}",
        )

    async def migrate_to_oauth(
        self, client_id: str = "homeassistant", name: str | None = None
    ) -> dict[str, Any]:
        """Migrate from access token to OAuth."""
        access_token = await self.access_token()
        migrate_data = {
            "grant_type": "migrate",
            "client_id": client_id,
            "access_token": access_token.strip(),
            "name": name,
        }

        new_token = await self._request(Method.POST, "oauth/token", json=migrate_data)
        new_token["expires_in"] = int(new_token["expires_in"])
        new_token["expires_at"] = time() + new_token["expires_in"]
        return new_token

    async def fields(self) -> dict[str, Any]:
        """Get streaming field parameters and metadata."""
        return await self._request(
            Method.GET,
            "fields.json",
        )

    async def vehicle_config(self, vin: str) -> dict[str, Any]:
        """Get the saved vehicle configuration.

        Args:
            vin: Vehicle identification number
        """
        return await self._request(
            Method.GET,
            f"api/vehicle_config/{vin}",
        )

    async def streaming_config(self, vin: str) -> dict[str, Any]:
        """Get the streaming configuration for a specific vehicle.

        Returns certificate, hostname, port, and configurable telemetry fields.

        Args:
            vin: Vehicle identification number
        """
        return await self._request(
            Method.GET,
            f"api/config/{vin}",
        )

    async def stop_streaming(self, vin: str) -> dict[str, Any]:
        """Stop streaming data from a specific vehicle.

        Args:
            vin: Vehicle identification number
        """
        return await self._request(
            Method.DELETE,
            f"api/config/{vin}",
        )

    async def modify_streaming_config(
        self, vin: str, fields: dict[str, Any]
    ) -> dict[str, Any]:
        """Modify the streaming configuration for a specific vehicle.

        Args:
            vin: Vehicle identification number
            fields: Fields to stream with their configuration
        """
        return await self._request(
            Method.PATCH,
            f"api/config/{vin}",
            json={"fields": fields},
        )

    async def create_streaming_config(
        self, vin: str, fields: dict[str, Any]
    ) -> dict[str, Any]:
        """Create/update the streaming configuration for a specific vehicle.

        Args:
            vin: Vehicle identification number
            fields: Fields to stream with their configuration
        """
        return await self._request(
            Method.POST,
            f"api/config/{vin}",
            json={"fields": fields},
        )
