"""Unit tests for backup-reserve raw<->scaled conversion and setters.

The scaling relationship was verified empirically against a Powerwall 3
gateway: the user-facing (Tesla app / Fleet API) reserve maps to the
gateway's raw ``config.json`` value as ``raw = scaled * 0.95 + 5``.

Datapoints (scaled -> raw): 5 -> 9.75, 10 -> 14.5, 20 -> 24, 35 -> 38.25,
60 -> 62.
"""

from __future__ import annotations

import pytest

from tesla_fleet_api.tesla.powerwall import (
    PowerwallClient,
    raw_to_scaled_reserve,
    scaled_to_raw_reserve,
)

# (scaled, raw) pairs measured on real hardware.
MEASURED = [(5, 9.75), (10, 14.5), (20, 24.0), (35, 38.25), (60, 62.0)]


@pytest.mark.parametrize("scaled,raw", MEASURED)
def test_scaled_to_raw_matches_hardware(scaled: float, raw: float) -> None:
    assert scaled_to_raw_reserve(scaled) == raw


@pytest.mark.parametrize("scaled,raw", MEASURED)
def test_raw_to_scaled_matches_hardware(scaled: float, raw: float) -> None:
    assert raw_to_scaled_reserve(raw) == scaled


def test_round_trip_is_identity() -> None:
    for scaled in (0, 1, 12.5, 50, 99, 100):
        assert raw_to_scaled_reserve(scaled_to_raw_reserve(scaled)) == scaled


def test_endpoints() -> None:
    # app 0% is not raw 0% — it's the 5% buffer floor.
    assert scaled_to_raw_reserve(0) == 5.0
    assert scaled_to_raw_reserve(100) == 100.0
    assert raw_to_scaled_reserve(5) == 0.0
    assert raw_to_scaled_reserve(100) == 100.0


@pytest.mark.parametrize("bad", [-1, 100.1, 150])
def test_scaled_to_raw_rejects_out_of_range(bad: float) -> None:
    with pytest.raises(ValueError):
        scaled_to_raw_reserve(bad)


@pytest.fixture
def client() -> tuple[PowerwallClient, list[dict]]:
    """A bare client (no transport/session) with write_config captured.

    The reserve setters only call ``self.write_config``, so we skip
    ``__init__`` (which would load an RSA key) and stub that one method.
    """
    pw = PowerwallClient.__new__(PowerwallClient)
    calls: list[dict] = []

    async def fake_write_config(updates: dict) -> None:
        calls.append(dict(updates))

    pw.write_config = fake_write_config  # type: ignore[method-assign]
    return pw, calls


async def test_set_backup_reserve_writes_scaled_raw(
    client: tuple[PowerwallClient, list[dict]],
) -> None:
    pw, calls = client
    await pw.set_backup_reserve(20)  # user-facing 20% -> raw 24
    assert calls == [{"site_info.backup_reserve_percent": 24.0}]


async def test_set_backup_reserve_raw_writes_verbatim(
    client: tuple[PowerwallClient, list[dict]],
) -> None:
    pw, calls = client
    await pw.set_backup_reserve_raw(24)  # raw written as-is
    assert calls == [{"site_info.backup_reserve_percent": 24}]


async def test_set_backup_reserve_rejects_out_of_range(
    client: tuple[PowerwallClient, list[dict]],
) -> None:
    pw, _ = client
    with pytest.raises(ValueError):
        await pw.set_backup_reserve(101)
    with pytest.raises(ValueError):
        await pw.set_backup_reserve_raw(-1)
