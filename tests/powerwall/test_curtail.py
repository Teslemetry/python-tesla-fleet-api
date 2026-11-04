"""Unit tests for ``curtail`` / ``restore_from_curtailment``."""

from __future__ import annotations

from typing import Any

from tesla_fleet_api.tesla.powerwall import PowerwallClient


async def test_restore_writes_back_fractional_reserve() -> None:
    pw = PowerwallClient.__new__(PowerwallClient)
    pw._saved_real_mode = None  # type: ignore[attr-defined]
    pw._saved_reserve_percent = None  # type: ignore[attr-defined]
    pw._curtailment_active = False  # type: ignore[attr-defined]
    calls: list[dict[str, Any]] = []

    async def fake_get_config() -> dict[str, Any]:
        return {
            "default_real_mode": "self_consumption",
            "site_info": {"backup_reserve_percent": 20.5},
        }

    async def fake_write_config(updates: dict[str, Any]) -> None:
        calls.append(dict(updates))

    pw.get_config = fake_get_config  # type: ignore[method-assign]
    pw.write_config = fake_write_config  # type: ignore[method-assign]

    await pw.curtail()
    await pw.restore_from_curtailment()

    assert calls[-1] == {
        "default_real_mode": "self_consumption",
        "site_info.backup_reserve_percent": 20.5,
    }
