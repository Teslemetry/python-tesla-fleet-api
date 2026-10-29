"""Unit tests for the site import/export power-limit setters.

The gateway stores these as whole-kilowatt integers in ``site_info`` matching
the Tesla app: ``max_site_meter_power_ac`` is the import cap (positive) and
``min_site_meter_power_ac`` is the export cap (stored negative). Verified on a
Powerwall 3 that a local write persists verbatim in kilowatts with no scaling,
and that fractional values (e.g. ``-2.5``) are stored as-is.
"""

from __future__ import annotations

import pytest

from tesla_fleet_api.tesla.powerwall import PowerwallClient


@pytest.fixture
def client() -> tuple[PowerwallClient, list[dict]]:
    """A bare client (no transport/session) with write_config captured."""
    pw = PowerwallClient.__new__(PowerwallClient)
    calls: list[dict] = []

    async def fake_write_config(updates: dict) -> None:
        calls.append(dict(updates))

    pw.write_config = fake_write_config  # type: ignore[method-assign]
    return pw, calls


async def test_set_import_limit_writes_max_site_meter_power(
    client: tuple[PowerwallClient, list[dict]],
) -> None:
    pw, calls = client
    await pw.set_import_limit(14)
    assert calls == [{"site_info.max_site_meter_power_ac": 14}]


async def test_set_export_limit_writes_negative_min_site_meter_power(
    client: tuple[PowerwallClient, list[dict]],
) -> None:
    pw, calls = client
    await pw.set_export_limit(14)
    assert calls == [{"site_info.min_site_meter_power_ac": -14}]


async def test_set_export_limit_zero_stays_zero(
    client: tuple[PowerwallClient, list[dict]],
) -> None:
    pw, calls = client
    await pw.set_export_limit(0)
    # -0 == 0; make sure we don't emit a negative-zero surprise.
    assert calls == [{"site_info.min_site_meter_power_ac": 0}]


async def test_set_import_limit_accepts_decimal(
    client: tuple[PowerwallClient, list[dict]],
) -> None:
    pw, calls = client
    await pw.set_import_limit(14.5)
    assert calls == [{"site_info.max_site_meter_power_ac": 14.5}]


async def test_set_export_limit_accepts_decimal(
    client: tuple[PowerwallClient, list[dict]],
) -> None:
    pw, calls = client
    await pw.set_export_limit(2.5)
    assert calls == [{"site_info.min_site_meter_power_ac": -2.5}]


@pytest.mark.parametrize("setter", ["set_import_limit", "set_export_limit"])
async def test_negative_kilowatts_rejected(
    client: tuple[PowerwallClient, list[dict]], setter: str
) -> None:
    pw, calls = client
    with pytest.raises(ValueError):
        await getattr(pw, setter)(-1)
    assert calls == []
