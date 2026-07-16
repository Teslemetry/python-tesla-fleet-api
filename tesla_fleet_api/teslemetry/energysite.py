from __future__ import annotations

import base64
import socket
import struct
from dataclasses import dataclass
from typing import Any, cast

from tesla_fleet_api.const import (
    AuthorizedClientKeyType,
    AuthorizedClientState,
    AuthorizedClientType,
    Method,
)
from tesla_fleet_api.exceptions import InvalidResponse
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


def _normalize_state(value: Any) -> AuthorizedClientState | int | str | None:
    """Type a raw ``state`` value against ``AuthorizedClientState``.

    Tesla has not published an OpenAPI schema for this pairing endpoint, so
    ``const.py``'s enum is the schema of record. A recognized int or member
    name (case-insensitive) becomes the enum member; a present-but-
    unrecognized value is returned unchanged rather than dropped to
    ``None``, since only a genuinely absent field means ``None``. ``bool``
    is excluded from the int branch since it subclasses ``int`` but is
    never a legal state code.
    """
    if (
        value is None
        or isinstance(value, AuthorizedClientState)
        or isinstance(value, bool)
    ):
        return value
    if isinstance(value, int):
        try:
            return AuthorizedClientState(value)
        except ValueError:
            return value
    if isinstance(value, str):
        try:
            return AuthorizedClientState[value.strip().upper()]
        except KeyError:
            return value
    return value


def _parse_client(payload: dict[str, Any]) -> AuthorizedClient:
    return AuthorizedClient(
        public_key=_field(payload, "public_key", "publicKey"),
        state=_normalize_state(_field(payload, "state", "authorized_client_state")),
        raw=payload,
    )


@dataclass(frozen=True, slots=True)
class AuthorizedClient:
    """One entry from a Teslemetry ``list_authorized_clients`` response.

    Only ``public_key`` and ``state`` are modeled - the two fields a
    pairing flow needs to confirm a registered key. Tesla has not
    published this response's schema, so anything else on an entry is
    available via ``raw`` rather than guessed at. Each field accepts the
    two key-name variants observed for it (``public_key``/``publicKey``,
    ``state``/``authorized_client_state``).
    """

    public_key: str | None
    state: AuthorizedClientState | int | str | None
    raw: dict[str, Any]


@dataclass(frozen=True, slots=True)
class AuthorizedClients:
    """Parsed result of :meth:`TeslemetryEnergySite.find_authorized_clients`.

    ``clients`` is a list of typed entries parsed from a well-formed
    response. A ``None`` response body or a response whose shape doesn't
    match the confirmed envelope raises
    :class:`~tesla_fleet_api.exceptions.InvalidResponse` instead of being
    silently collapsed to "no clients" - Tesla's endpoint intermittently
    returns HTTP 200 with a null body, which is malformed data, not zero
    clients. A genuinely empty list under either accepted key is not
    malformed and parses to ``[]``.

    The envelope this unwraps (``{"response": {"authorized_clients": [...]}}``
    or ``{"response": {"clients": [...]}}``) is pinned from the pairing
    flow's own defensive handling of this undocumented endpoint - see
    :class:`AuthorizedClient`.
    """

    clients: list[AuthorizedClient]
    raw: Any


def _authorized_clients_list(payload: Any) -> list[Any]:
    """Return the raw authorized-clients list from a command response.

    A precise, single-path unwrap of the confirmed envelope (a bare list,
    or ``{"response": {"authorized_clients": [...]}}`` /
    ``{"response": {"clients": [...]}}``) - not a search across candidate
    wrapper keys for this undocumented endpoint. Raises
    :class:`~tesla_fleet_api.exceptions.InvalidResponse` for a null body or
    any other shape, since a 200 that doesn't carry either expected key is
    malformed, not "zero clients". A genuinely empty list under either key
    is not malformed and returns ``[]``.
    """
    if payload is None:
        raise InvalidResponse("authorized_clients response body was null")
    if isinstance(payload, list):
        return cast("list[Any]", payload)
    if not isinstance(payload, dict):
        raise InvalidResponse(str(payload))
    body = cast("dict[str, Any]", payload)
    response = body.get("response")
    if isinstance(response, dict):
        body = cast("dict[str, Any]", response)
    value = _field(body, "authorized_clients", "clients")
    if not isinstance(value, list):
        raise InvalidResponse(cast("dict[str, Any]", payload))
    return cast("list[Any]", value)


def _parse_authorized_clients(payload: Any) -> AuthorizedClients:
    """Parse a raw ``list_authorized_clients()`` response into typed clients.

    Raises :class:`~tesla_fleet_api.exceptions.InvalidResponse` if
    ``payload`` is null or doesn't match the confirmed envelope shape - see
    :func:`_authorized_clients_list`.
    """
    clients = [
        _parse_client(cast("dict[str, Any]", entry))
        for entry in _authorized_clients_list(payload)
        if isinstance(entry, dict)
    ]
    return AuthorizedClients(clients=clients, raw=payload)


_GATEWAY_INTERFACES = ("eth", "wifi")


def _decode_ipv4(value: Any) -> str | None:
    """Decode a raw big-endian uint32 into dotted-quad form.

    ``ipv4_config.address``/``subnet_mask``/``gateway`` in a
    ``networking_status`` response are network-byte-order uint32 integers,
    not strings - confirmed against a live Powerwall 3 capture where
    ``3232235914`` decodes to ``192.168.1.138``. ``bool`` is excluded since
    it subclasses ``int``; an out-of-range or non-int value returns
    ``None`` rather than raising, since a single bad address shouldn't
    fail the whole lookup. ``0`` and ``0xFFFFFFFF`` are also rejected -
    ``0.0.0.0``/``255.255.255.255`` are never a usable host address, and an
    unconfigured interface reporting ``address: 0`` must not shadow a real
    address on another interface in the fallback selection.
    """
    if not isinstance(value, int) or isinstance(value, bool):
        return None
    if not 0 < value < 0xFFFFFFFF:
        return None
    return socket.inet_ntoa(struct.pack(">I", value))


def _interface_address(interface: Any) -> str | None:
    if not isinstance(interface, dict):
        return None
    ipv4 = cast("dict[str, Any]", interface).get("ipv4_config")
    if not isinstance(ipv4, dict) or "address" not in ipv4:
        return None
    return _decode_ipv4(cast("dict[str, Any]", ipv4)["address"])


def _networking_status_body(payload: Any) -> dict[str, Any]:
    """Unwrap a ``networking_status`` response into its interface-block dict.

    Raises :class:`~tesla_fleet_api.exceptions.InvalidResponse` for a null
    body, a shape that isn't a dict, or a ``response`` envelope whose value
    isn't a dict (``{"response": null}`` is the endpoint's known
    intermittent malformed mode, not "no address") - anything else is a
    well-formed body, even if it carries no usable interface.
    """
    if payload is None:
        raise InvalidResponse("networking_status response body was null")
    if not isinstance(payload, dict):
        raise InvalidResponse(str(payload))
    body = cast("dict[str, Any]", payload)
    if "response" in body:
        response = body["response"]
        if not isinstance(response, dict):
            raise InvalidResponse(cast("dict[str, Any]", payload))
        body = cast("dict[str, Any]", response)
    return body


def _parse_gateway_address(payload: Any) -> str | None:
    """Pick the gateway's LAN IPv4 from a ``networking_status`` response.

    Considers only ``eth``/``wifi`` (never ``gsm`` - cellular isn't a LAN
    path): prefers whichever of those has ``active_route`` set and a
    decodable address, then falls back to the first of the two (in
    ``eth``, ``wifi`` order) that has any decodable address. Returns
    ``None`` when neither yields one - a well-formed response can simply
    lack a usable interface.
    """
    body = _networking_status_body(payload)
    interfaces = [body.get(name) for name in _GATEWAY_INTERFACES]

    for interface in interfaces:
        if (
            isinstance(interface, dict)
            and cast("dict[str, Any]", interface).get("active_route")
            and (address := _interface_address(interface)) is not None
        ):
            return address

    for interface in interfaces:
        address = _interface_address(interface)
        if address is not None:
            return address

    return None


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

    async def find_gateway_address(self) -> str | None:
        """Discover the gateway's LAN IPv4 address, for pre-filling a local
        control host.

        Prefer this over :meth:`get_networking_status` for consumers that
        just need a host to connect to - it centralizes the ``eth``/``wifi``
        interface selection and uint32-to-dotted-quad decoding here instead
        of in the caller. Raises
        :class:`~tesla_fleet_api.exceptions.InvalidResponse` on a null
        response body or an unrecognized response shape; returns ``None``
        when the response is well-formed but no interface yields an
        address. See :func:`_parse_gateway_address` for the exact selection
        rule.
        """
        return _parse_gateway_address(await self.get_networking_status())

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

    async def find_authorized_clients(self) -> AuthorizedClients:
        """List authorized clients on the energy gateway, parsed into a typed result.

        Prefer this over :meth:`list_authorized_clients` for consumers that
        need to inspect the client list - it centralizes the response
        parsing (envelope unwrap, ``state`` typing) here instead of in the
        caller. Raises
        :class:`~tesla_fleet_api.exceptions.InvalidResponse` on a null
        response body or an unrecognized response shape rather than
        treating either as "no clients". See :class:`AuthorizedClients` for
        the exact parsing semantics.
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
