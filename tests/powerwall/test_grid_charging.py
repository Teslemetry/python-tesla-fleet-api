"""Unit tests for the grid-charging setter.

``set_grid_charging(enabled)`` writes the *inverse* disallow flag
``site_info.disallow_charge_from_grid_with_solar_installed``. Verified on a
Powerwall 3 gateway (via the Fleet->local sync and a direct local v1r write)
that ``disallow=true`` persists the key as ``true`` while ``disallow=false``
causes the gateway to drop the key entirely (its absence means "grid charging
allowed").
"""

from __future__ import annotations

import pytest

from tesla_fleet_api.tesla.powerwall import PowerwallClient

_KEY = "site_info.disallow_charge_from_grid_with_solar_installed"


@pytest.fixture
def client() -> tuple[PowerwallClient, list[dict]]:
    """A bare client (no transport/session) with write_config captured.

    ``set_grid_charging`` only calls ``self.write_config``, so we skip
    ``__init__`` (which would load an RSA key) and stub that one method.
    """
    pw = PowerwallClient.__new__(PowerwallClient)
    calls: list[dict] = []

    async def fake_write_config(updates: dict) -> None:
        calls.append(dict(updates))

    pw.write_config = fake_write_config  # type: ignore[method-assign]
    return pw, calls


@pytest.mark.parametrize(
    "enabled,disallow", [(True, False), (False, True)]
)
async def test_set_grid_charging_writes_inverse_disallow(
    client: tuple[PowerwallClient, list[dict]], enabled: bool, disallow: bool
) -> None:
    pw, calls = client
    await pw.set_grid_charging(enabled)
    assert calls == [{_KEY: disallow}]
    # Must be a real bool so the gateway receives JSON true/false, not 1/0.
    assert calls[0][_KEY] is disallow
