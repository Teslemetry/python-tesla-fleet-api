"""Unit tests for SoC raw<->scaled conversion and the scaled readers.

The local gateway reports state-of-charge on the raw physical pack scale
(``get_battery_soe_raw`` and ``battery_level_raw``); the Tesla app / Fleet API
show a user-facing value with the bottom-5% buffer removed — the *same* buffer
as backup reserve, so ``raw = scaled * 0.95 + 5``.

Verified on a Powerwall 3 (2026-06-26): local raw 52.7778
mapped exactly to Fleet ``live_status.percentage_charged`` 50.2924
(= ``(52.7778 - 5) / 0.95``), matching to full float precision.
"""

from __future__ import annotations

import pytest

from tesla_fleet_api.tesla.powerwall import (
    PowerwallClient,
    battery_level,
    battery_level_raw,
    raw_to_scaled_soc,
    scaled_to_raw_soc,
)

# (scaled, raw) pairs that hold exactly under the 4-dp rounding.
MEASURED = [(0, 5.0), (20, 24.0), (50, 52.5), (100, 100.0)]


@pytest.mark.parametrize("scaled,raw", MEASURED)
def test_scaled_to_raw_matches_formula(scaled: float, raw: float) -> None:
    assert scaled_to_raw_soc(scaled) == raw


@pytest.mark.parametrize("scaled,raw", MEASURED)
def test_raw_to_scaled_matches_formula(scaled: float, raw: float) -> None:
    assert raw_to_scaled_soc(raw) == scaled


def test_hardware_datapoint() -> None:
    # Measured on PW3: local raw 52.7778 -> Fleet scaled 50.2924.
    assert raw_to_scaled_soc(52.77777777777778) == pytest.approx(50.2924)


def test_round_trip_is_identity() -> None:
    for scaled in (0, 1, 12.5, 50, 99, 100):
        assert raw_to_scaled_soc(scaled_to_raw_soc(scaled)) == scaled


def test_endpoints() -> None:
    # User-facing 0% is the 5% buffer floor, not raw 0%.
    assert scaled_to_raw_soc(0) == 5.0
    assert scaled_to_raw_soc(100) == 100.0
    assert raw_to_scaled_soc(5) == 0.0
    assert raw_to_scaled_soc(100) == 100.0


@pytest.mark.parametrize("bad", [-1, 100.1, 150])
def test_scaled_to_raw_rejects_out_of_range(bad: float) -> None:
    with pytest.raises(ValueError):
        scaled_to_raw_soc(bad)


def test_battery_level_applies_transform() -> None:
    # remaining/full = 9500/18000 -> raw 52.7778 -> user-facing 50.2924.
    status = {
        "control": {
            "systemStatus": {
                "nominalEnergyRemainingWh": 9500,
                "nominalFullPackEnergyWh": 18000,
            }
        }
    }
    assert battery_level_raw(status) == pytest.approx(52.77777777777778)
    assert battery_level(status) == pytest.approx(50.2924)


def test_battery_level_returns_none_when_unknown() -> None:
    assert battery_level({}) is None
    assert battery_level_raw({}) is None
    assert battery_level(
        {"control": {"systemStatus": {"nominalFullPackEnergyWh": 0}}}
    ) is None


@pytest.fixture
def client() -> PowerwallClient:
    """A bare client (no transport) with ``get_battery_soe_raw`` stubbed.

    ``get_battery_soe`` only calls ``self.get_battery_soe_raw``, so we skip
    ``__init__`` (which would load an RSA key) and stub that one method.
    """
    pw = PowerwallClient.__new__(PowerwallClient)

    async def fake_get_battery_soe_raw() -> float:
        return 52.77777777777778

    pw.get_battery_soe_raw = fake_get_battery_soe_raw  # type: ignore[method-assign]
    return pw


async def test_get_battery_soe_returns_user_facing(
    client: PowerwallClient,
) -> None:
    assert await client.get_battery_soe() == pytest.approx(50.2924)
