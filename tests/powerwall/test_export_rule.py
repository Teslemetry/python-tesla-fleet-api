"""Unit tests for the grid-export-rule setter.

``customer_preferred_export_rule`` is a plain nested string in ``config.json``
with no scaling — verified on a Powerwall 3 gateway that a local v1r write of
``battery_ok`` / ``pv_only`` / ``never`` sticks and reads back verbatim, and
that ``net_meter_mode`` is an independent key left untouched by the write.
"""

from __future__ import annotations

import pytest

from tesla_fleet_api.tesla.powerwall import GRID_EXPORT_RULES, PowerwallClient


def test_export_rules_are_the_three_known_values() -> None:
    assert GRID_EXPORT_RULES == ("battery_ok", "pv_only", "never")


@pytest.fixture
def client() -> tuple[PowerwallClient, list[dict]]:
    """A bare client (no transport/session) with write_config captured.

    ``set_export_rule`` only calls ``self.write_config``, so we skip
    ``__init__`` (which would load an RSA key) and stub that one method.
    """
    pw = PowerwallClient.__new__(PowerwallClient)
    calls: list[dict] = []

    async def fake_write_config(updates: dict) -> None:
        calls.append(dict(updates))

    pw.write_config = fake_write_config  # type: ignore[method-assign]
    return pw, calls


@pytest.mark.parametrize("rule", ["battery_ok", "pv_only", "never"])
async def test_set_export_rule_writes_only_the_export_key(
    client: tuple[PowerwallClient, list[dict]], rule: str
) -> None:
    pw, calls = client
    await pw.set_export_rule(rule)
    # Only customer_preferred_export_rule is written — net_meter_mode is left
    # untouched (the two are independent settings).
    assert calls == [{"site_info.customer_preferred_export_rule": rule}]


@pytest.mark.parametrize("bad", ["", "Battery_OK", "solar_only", "pvonly", "off"])
async def test_set_export_rule_rejects_unknown(
    client: tuple[PowerwallClient, list[dict]], bad: str
) -> None:
    pw, calls = client
    with pytest.raises(ValueError):
        await pw.set_export_rule(bad)
    assert calls == []
