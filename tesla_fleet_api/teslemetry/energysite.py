from __future__ import annotations

import base64
from dataclasses import dataclass
from typing import Any, cast

from tesla_fleet_api.const import (
    AuthorizedClientKeyType,
    AuthorizedClientType,
    Method,
)
from tesla_fleet_api.tesla.energysite import EnergySite, EnergySites


def _field(payload: dict[str, Any], *keys: str) -> Any:
    """Return the first present key's value.

    Checks key presence rather than truthiness, so a legal falsy value
    (``0``, ``False``, ``""``) is never mistaken for a missing field.
    """
    for key in keys:
        if key in payload:
            return payload[key]
    return None


def _parse_client(payload: dict[str, Any]) -> AuthorizedClient:
    return AuthorizedClient(
        public_key=_field(payload, "public_key", "publicKey"),
        description=_field(payload, "description"),
        key_type=_field(payload, "key_type", "keyType"),
        authorized_client_type=_field(
            payload, "authorized_client_type", "authorizedClientType"
        ),
        state=_field(payload, "state", "authorized_client_state"),
        raw=payload,
    )


@dataclass(frozen=True, slots=True)
class AuthorizedClient:
    """One entry from a Teslemetry ``list_authorized_clients`` response.

    Tesla has not published this response shape, so fields are read
    defensively (snake_case and camelCase key variants). ``raw`` keeps the
    original entry for any field not modeled here.
    """

    public_key: str | None
    description: str | None
    key_type: int | None
    authorized_client_type: int | None
    state: int | None
    raw: dict[str, Any]


@dataclass(frozen=True, slots=True)
class AuthorizedClients:
    """Parsed result of :meth:`TeslemetryEnergySite.get_authorized_clients`.

    ``clients`` is ``None`` when the outcome is genuinely unknown: the
    response body itself was ``None`` (Teslemetry may return a null body),
    or no ``authorized_clients``/``authorizedClients`` key could be found in
    it. An explicitly present but empty client list is authoritative and
    distinct from that - it means the gateway reports zero authorized
    clients, not "keep looking elsewhere in the payload" - so it is
    returned as ``[]``, never coerced to ``None``.
    """

    clients: list[AuthorizedClient] | None
    raw: Any


def _find_authorized_clients_list(payload: Any) -> tuple[bool, list[Any]]:
    """Locate the raw authorized-clients list in a command response.

    Returns ``(found, entries)``. ``found`` is ``False`` only when no
    ``authorized_clients``/``authorizedClients`` key exists anywhere
    checked (the payload itself, or its ``response`` wrapper) - an unknown
    outcome, never conflated with a found-but-empty list.
    """
    body: Any = payload
    if isinstance(body, dict):
        body = cast("dict[str, Any]", body)
        wrapped = _field(body, "response")
        if isinstance(wrapped, dict):
            body = cast("dict[str, Any]", wrapped)
    if isinstance(body, list):
        return True, cast("list[Any]", body)
    if not isinstance(body, dict):
        return False, []
    body = cast("dict[str, Any]", body)
    for key in ("authorized_clients", "authorizedClients"):
        if key in body:
            value = body[key]
            return True, cast("list[Any]", value) if isinstance(value, list) else []
    return False, []


def _parse_authorized_clients(payload: Any) -> AuthorizedClients:
    """Parse a raw ``list_authorized_clients()`` response into typed clients."""
    if payload is None:
        return AuthorizedClients(clients=None, raw=None)
    found, entries = _find_authorized_clients_list(payload)
    if not found:
        return AuthorizedClients(clients=None, raw=payload)
    clients = [
        _parse_client(cast("dict[str, Any]", entry))
        for entry in entries
        if isinstance(entry, dict)
    ]
    return AuthorizedClients(clients=clients, raw=payload)


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

    async def get_authorized_clients(self) -> AuthorizedClients:
        """List authorized clients on the energy gateway, parsed into a typed result.

        Prefer this over :meth:`list_authorized_clients` for consumers that
        need to inspect the client list - it centralizes the response
        parsing (including the null-body and empty-vs-absent-list cases)
        here instead of in the caller. See :class:`AuthorizedClients` for
        the exact semantics.
        """
        return _parse_authorized_clients(await self.list_authorized_clients())

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
