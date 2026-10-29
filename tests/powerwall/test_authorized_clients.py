"""Unit tests for the typed `find_authorized_clients()` result shape.

Exercises the local parsing (`parse_authorized_clients` and its per-field
normalizers) directly, plus a parity check against `tesla_fleet_api`'s own
`AuthorizedClientState`/`AuthorizationRole`/`AuthorizedVerificationType`
enums and `AuthorizedClient`/`AuthorizedClients` dataclasses when that
package is importable in the dev environment — this package never depends
on it at runtime.
"""

from __future__ import annotations

import dataclasses

import pytest

from tesla_fleet_api.tesla.powerwall.authorized_clients import (
    AuthorizationRole,
    AuthorizedClient,
    AuthorizedClients,
    AuthorizedClientState,
    AuthorizedVerificationType,
    parse_authorized_clients,
)


def test_parse_authorized_clients_types_known_fields() -> None:
    payload = {
        "clients": [
            {
                "public_key": "AQID",
                "state": "VERIFIED",
                "roles": ["CUSTOMER"],
                "verification": "SIGNED",
                "type": "CUSTOMER_MOBILE_APP",
                "identifier": "abc-123",
            }
        ],
        "enable_line_switch_off": True,
    }
    result = parse_authorized_clients(payload)
    assert isinstance(result, AuthorizedClients)
    assert len(result.clients) == 1
    client = result.clients[0]
    assert client.public_key == "AQID"
    assert client.state is AuthorizedClientState.VERIFIED
    assert client.roles == [AuthorizationRole.CUSTOMER]
    assert client.verification is AuthorizedVerificationType.SIGNED
    assert client.raw == payload["clients"][0]
    assert result.raw is payload


def test_parse_authorized_clients_empty_list() -> None:
    result = parse_authorized_clients({"clients": []})
    assert result.clients == []


def test_unknown_state_int_is_returned_unchanged() -> None:
    """A state number the enum doesn't know must never raise or become None."""
    result = parse_authorized_clients({"clients": [{"public_key": "AQID", "state": 99}]})
    assert result.clients[0].state == 99


def test_unknown_state_name_is_returned_unchanged() -> None:
    result = parse_authorized_clients(
        {"clients": [{"public_key": "AQID", "state": "SOME_FUTURE_STATE"}]}
    )
    assert result.clients[0].state == "SOME_FUTURE_STATE"


def test_missing_optional_fields_become_none() -> None:
    result = parse_authorized_clients({"clients": [{"public_key": None}]})
    client = result.clients[0]
    assert client.state is None
    assert client.roles is None
    assert client.verification is None


def test_non_dict_entries_are_skipped() -> None:
    result = parse_authorized_clients({"clients": [{"public_key": "AQID"}, "garbage", None]})
    assert len(result.clients) == 1


def _tesla_fleet_api_const() -> object:
    return pytest.importorskip("tesla_fleet_api.const")


def _tesla_fleet_api_energysite() -> object:
    return pytest.importorskip("tesla_fleet_api.teslemetry.energysite")


def test_authorized_client_state_matches_tesla_fleet_api() -> None:
    const = _tesla_fleet_api_const()
    their_state = const.AuthorizedClientState  # type: ignore[attr-defined]
    assert {m.name: m.value for m in AuthorizedClientState} == {
        m.name: m.value for m in their_state
    }


def test_authorization_role_matches_tesla_fleet_api() -> None:
    const = _tesla_fleet_api_const()
    their_role = const.AuthorizationRole  # type: ignore[attr-defined]
    assert {m.name: m.value for m in AuthorizationRole} == {m.name: m.value for m in their_role}


def test_authorized_verification_type_matches_tesla_fleet_api() -> None:
    const = _tesla_fleet_api_const()
    their_verification = const.AuthorizedVerificationType  # type: ignore[attr-defined]
    assert {m.name: m.value for m in AuthorizedVerificationType} == {
        m.name: m.value for m in their_verification
    }


def test_authorized_client_fields_match_tesla_fleet_api() -> None:
    energysite = _tesla_fleet_api_energysite()
    their_client = energysite.AuthorizedClient  # type: ignore[attr-defined]
    ours = {f.name for f in dataclasses.fields(AuthorizedClient)}
    theirs = {f.name for f in dataclasses.fields(their_client)}
    assert ours == theirs


def test_authorized_clients_fields_match_tesla_fleet_api() -> None:
    energysite = _tesla_fleet_api_energysite()
    their_clients = energysite.AuthorizedClients  # type: ignore[attr-defined]
    ours = {f.name for f in dataclasses.fields(AuthorizedClients)}
    theirs = {f.name for f in dataclasses.fields(their_clients)}
    assert ours == theirs
