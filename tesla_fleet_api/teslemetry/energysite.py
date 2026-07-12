from __future__ import annotations

import base64
from typing import Any

from tesla_fleet_api.const import (
    AuthorizedClientKeyType,
    AuthorizedClientType,
    Method,
)
from tesla_fleet_api.tesla.energysite import EnergySite, EnergySites


class TeslemetryEnergySite(EnergySite):
    """Teslemetry specific energy site."""

    async def add_authorized_client(
        self,
        public_key: bytes | str | None = None,
        description: str | None = None,
        key_type: AuthorizedClientKeyType | int | None = None,
        authorized_client_type: AuthorizedClientType | int | None = None,
    ) -> dict[str, Any]:
        """Register an authorized client with the energy gateway via the
        Teslemetry custom endpoint.

        All arguments are optional — if omitted, the Teslemetry server
        pre-populates the request with its own key details.

        Args:
            public_key: The public key to register. Either raw DER PKCS1
                bytes (which will be base64-encoded), or an already
                base64-encoded string.
            description: Human-readable description of the client.
            key_type: The type of key being registered.
            authorized_client_type: The authorized client type.
        """
        data: dict[str, Any] = {}
        if public_key is not None:
            if isinstance(public_key, bytes):
                data["public_key"] = base64.b64encode(public_key).decode("ascii")
            else:
                data["public_key"] = public_key
        if description is not None:
            data["description"] = description
        if key_type is not None:
            data["key_type"] = int(key_type)
        if authorized_client_type is not None:
            data["authorized_client_type"] = int(authorized_client_type)
        return await self._request(
            Method.POST,
            f"api/1/energy_sites/{self.energy_site_id}/command/add_authorized_client",
            json=data,
        )

    async def get_networking_status(self) -> dict[str, Any]:
        """Retrieve networking status from the energy gateway via the
        Teslemetry custom endpoint.

        Includes WiFi configuration, WiFi interface, Ethernet interface,
        and GSM/cellular interface details.
        """
        return await self._request(
            Method.GET,
            f"api/1/energy_sites/{self.energy_site_id}/command/networking_status",
        )

    async def list_authorized_clients(self) -> dict[str, Any]:
        """List authorized clients on the energy gateway via the Teslemetry
        custom endpoint.

        Teslemetry may return JSON ``null`` when no authorized-client payload
        is available; that value is returned unchanged.
        """
        return await self._request(
            Method.GET,
            f"api/1/energy_sites/{self.energy_site_id}/command/authorized_clients",
        )

    async def remove_authorized_client(
        self, params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Remove an authorized client from the energy gateway via the
        Teslemetry custom endpoint.

        Accepts raw protobuf request fields. Keys and nesting must match
        Tesla's snake_case proto field names.
        """
        return await self._request(
            Method.POST,
            f"api/1/energy_sites/{self.energy_site_id}/command/remove_authorized_client",
            json=params or {},
        )


class TeslemetryEnergySites(EnergySites):
    """Class containing and creating Teslemetry energy sites."""

    Site = TeslemetryEnergySite

    def create(self, energy_site_id: int) -> TeslemetryEnergySite:
        """Create a specific energy site."""
        site = self.Site(self._parent, energy_site_id)
        self[energy_site_id] = site
        return site
