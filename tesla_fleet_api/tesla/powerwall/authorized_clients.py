"""Typed ``find_authorized_clients()`` result, aligned with tesla-fleet-api.

:class:`AuthorizedClient` / :class:`AuthorizedClients` mirror the field names,
types, and member values of
``tesla_fleet_api.teslemetry.energysite.AuthorizedClient`` /
``AuthorizedClients`` (and the ``AuthorizedClientState`` /
``AuthorizationRole`` / ``AuthorizedVerificationType`` enums in
``tesla_fleet_api.const``) so a caller can treat a local
:meth:`~aiopowerwall.energysite.PowerwallEnergySite.find_authorized_clients`
result and a cloud ``TeslemetryEnergySite.find_authorized_clients()`` result
identically, with no local-vs-cloud conversion. **This module never imports
`tesla_fleet_api`** — parity is verified by
``tests/test_tesla_protocol_compat.py``-style descriptor checks, not a
dependency. Fields with no faithful local mapping (``type``, ``key_type``,
``added_time``, ``identifier``, ``authorized_by_public_key``) are still
available on the raw entry under ``raw``.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from typing import Any, cast


class AuthorizedClientState(IntEnum):
    """State of an authorized client registered on an energy gateway."""

    INVALID = 0
    PENDING_VERIFICATION = 1
    PENDING_VERIFICATION_TIMEOUT = 2
    VERIFIED = 3
    REMOVED = 4


class AuthorizationRole(IntEnum):
    """Role granted to an authorized client on an energy gateway."""

    INVALID = 0
    CUSTOMER = 1
    VEHICLE = 2


class AuthorizedVerificationType(IntEnum):
    """How an authorized client's presence was verified on an energy gateway."""

    INVALID = 0
    PRESENCE_PROOF = 1
    BLE = 2
    SIGNED = 3
    HERMES_COMMAND = 4


def _normalize_state(value: Any) -> AuthorizedClientState | int | str | None:
    """Type a raw ``state`` value, leaving an unrecognized one unchanged.

    A newer gateway firmware can report a state number this enum does not
    know; returning it unchanged (never raising, never guessing ``None``)
    matches ``tesla_fleet_api``'s ``_normalize_state`` for the same case.
    """
    if value is None or isinstance(value, (AuthorizedClientState, bool)):
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
    return cast("int | str | None", value)


def _normalize_role(value: Any) -> AuthorizationRole | int | str | None:
    if value is None or isinstance(value, (AuthorizationRole, bool)):
        return value
    if isinstance(value, int):
        try:
            return AuthorizationRole(value)
        except ValueError:
            return value
    if isinstance(value, str):
        try:
            return AuthorizationRole[value.strip().upper()]
        except KeyError:
            return value
    return cast("int | str | None", value)


def _normalize_verification(value: Any) -> AuthorizedVerificationType | int | str | None:
    if value is None or isinstance(value, (AuthorizedVerificationType, bool)):
        return value
    if isinstance(value, int):
        try:
            return AuthorizedVerificationType(value)
        except ValueError:
            return value
    if isinstance(value, str):
        try:
            return AuthorizedVerificationType[value.strip().upper()]
        except KeyError:
            return value
    return cast("int | str | None", value)


@dataclass(frozen=True, slots=True)
class AuthorizedClient:
    """One registered client entry, typed to match tesla-fleet-api's shape.

    Anything with no faithful cloud counterpart (``type``, ``key_type``,
    ``added_time``, ``identifier``, ``authorized_by_public_key``) is still
    reachable via ``raw`` rather than being dropped.
    """

    public_key: str | None
    state: AuthorizedClientState | int | str | None
    roles: list[AuthorizationRole | int | str | None] | None
    verification: AuthorizedVerificationType | int | str | None
    raw: dict[str, Any]


@dataclass(frozen=True, slots=True)
class AuthorizedClients:
    """Parsed result of
    :meth:`~aiopowerwall.energysite.PowerwallEnergySite.find_authorized_clients`.
    """

    clients: list[AuthorizedClient]
    raw: Any


def _parse_client(entry: dict[str, Any]) -> AuthorizedClient:
    roles = entry.get("roles")
    return AuthorizedClient(
        public_key=entry.get("public_key"),
        state=_normalize_state(entry.get("state")),
        roles=[_normalize_role(role) for role in roles] if isinstance(roles, list) else None,
        verification=_normalize_verification(entry.get("verification")),
        raw=entry,
    )


def parse_authorized_clients(payload: dict[str, Any]) -> AuthorizedClients:
    """Parse a :meth:`PowerwallClient.list_authorized_clients` payload.

    ``payload`` is the unwrapped ``{"clients": [...], ...}`` shape (not the
    ``{"response": {...}}`` envelope).
    """
    entries = payload.get("clients", [])
    clients = [_parse_client(entry) for entry in entries if isinstance(entry, dict)]
    return AuthorizedClients(clients=clients, raw=payload)


__all__ = [
    "AuthorizationRole",
    "AuthorizedClient",
    "AuthorizedClientState",
    "AuthorizedClients",
    "AuthorizedVerificationType",
    "parse_authorized_clients",
]
