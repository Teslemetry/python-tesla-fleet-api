"""Unit tests for the on-grid solar curtailment setter.

``on_grid_solar_curtailment_enabled`` is a boolean in ``site_info`` with no
scaling. Verified on a Powerwall 3 gateway that a local v1r write of ``True``
persists the key as ``true``, while a write of ``False`` causes the gateway to
drop the key entirely (its absence is the "disabled" state).
"""

from __future__ import annotations

import pytest

from tesla_fleet_api.tesla.powerwall import PowerwallClient


@pytest.fixture
def client() -> tuple[PowerwallClient, list[dict]]:
    """A bare client (no transport/session) with write_config captured.

    ``set_on_grid_solar_curtailment`` only calls ``self.write_config``, so we
    skip ``__init__`` (which would load an RSA key) and stub that one method.
    """
    pw = PowerwallClient.__new__(PowerwallClient)
    calls: list[dict] = []

    async def fake_write_config(updates: dict) -> None:
        calls.append(dict(updates))

    pw.write_config = fake_write_config  # type: ignore[method-assign]
    return pw, calls


@pytest.mark.parametrize("enabled", [True, False])
async def test_set_on_grid_solar_curtailment_writes_bool(
    client: tuple[PowerwallClient, list[dict]], enabled: bool
) -> None:
    pw, calls = client
    await pw.set_on_grid_solar_curtailment(enabled)
    assert calls == [{"site_info.on_grid_solar_curtailment_enabled": enabled}]


async def test_set_on_grid_solar_curtailment_coerces_to_bool(
    client: tuple[PowerwallClient, list[dict]],
) -> None:
    pw, calls = client
    await pw.set_on_grid_solar_curtailment(1)  # type: ignore[arg-type]
    # Must be a real bool so the gateway receives JSON ``true``, not ``1``.
    assert calls[0]["site_info.on_grid_solar_curtailment_enabled"] is True
