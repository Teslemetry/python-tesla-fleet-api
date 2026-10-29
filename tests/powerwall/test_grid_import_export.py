"""Unit tests for the grid-export-rule / grid-charge-with-solar setter.

``customer_preferred_export_rule`` and
``disallow_charge_from_grid_with_solar_installed`` are both plain
``site_info``-nested fields in ``config.json`` (alongside
``backup_reserve_percent``) — field names and the export-rule enum
(``battery_ok``/``pv_only``/``never``) confirmed against the sibling
jasonacox/pypowerwall project's v1r config-write path, which targets the
same Tesla local gateway schema.
"""

from __future__ import annotations

import pytest

from tesla_fleet_api.tesla.powerwall import GRID_EXPORT_RULES, PowerwallClient


def test_grid_export_rules_are_the_three_known_values() -> None:
    assert GRID_EXPORT_RULES == ("battery_ok", "pv_only", "never")


@pytest.fixture
def client() -> tuple[PowerwallClient, list[dict]]:
    """A bare client (no transport/session) with write_config captured.

    ``set_grid_import_export`` only calls ``self.write_config``, so we skip
    ``__init__`` (which would load an RSA key) and stub that one method.
    """
    pw = PowerwallClient.__new__(PowerwallClient)
    calls: list[dict] = []

    async def fake_write_config(updates: dict) -> None:
        calls.append(dict(updates))

    pw.write_config = fake_write_config  # type: ignore[method-assign]
    return pw, calls


@pytest.mark.parametrize("rule", ["battery_ok", "pv_only", "never"])
async def test_set_grid_import_export_writes_export_rule(
    client: tuple[PowerwallClient, list[dict]], rule: str
) -> None:
    pw, calls = client
    await pw.set_grid_import_export(customer_preferred_export_rule=rule)
    assert calls == [{"site_info.customer_preferred_export_rule": rule}]


@pytest.mark.parametrize("allow", [True, False])
async def test_set_grid_import_export_writes_charge_from_grid_flag(
    client: tuple[PowerwallClient, list[dict]], allow: bool
) -> None:
    pw, calls = client
    await pw.set_grid_import_export(
        disallow_charge_from_grid_with_solar_installed=allow
    )
    assert calls == [
        {"site_info.disallow_charge_from_grid_with_solar_installed": allow}
    ]


async def test_set_grid_import_export_writes_both_atomically(
    client: tuple[PowerwallClient, list[dict]],
) -> None:
    pw, calls = client
    await pw.set_grid_import_export(
        customer_preferred_export_rule="battery_ok",
        disallow_charge_from_grid_with_solar_installed=True,
    )
    # One write_config call carrying both dotted paths, not two round-trips.
    assert calls == [
        {
            "site_info.customer_preferred_export_rule": "battery_ok",
            "site_info.disallow_charge_from_grid_with_solar_installed": True,
        }
    ]


@pytest.mark.parametrize("bad", ["", "Battery_Ok", "always", "solar_only"])
async def test_set_grid_import_export_rejects_unknown_rule(
    client: tuple[PowerwallClient, list[dict]], bad: str
) -> None:
    pw, calls = client
    with pytest.raises(ValueError):
        await pw.set_grid_import_export(customer_preferred_export_rule=bad)
    assert calls == []


async def test_set_grid_import_export_rejects_no_arguments(
    client: tuple[PowerwallClient, list[dict]],
) -> None:
    pw, calls = client
    with pytest.raises(ValueError):
        await pw.set_grid_import_export()
    assert calls == []
