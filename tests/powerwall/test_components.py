"""Unit tests for the components-payload helpers.

``fixtures/components_pw3_two_expansions.json`` is a real Powerwall 3 site
(one leader, two expansions) captured with ``get_config``, ``get_status`` and
``get_components``, trimmed to the fields these helpers read, with serial
numbers replaced. Its ``bms[3]`` / ``hvp[3]`` row is an empty fourth slot.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import pytest

from tesla_fleet_api.tesla.powerwall import (
    BatteryUnit,
    battery_units,
    component_float,
    component_serial,
    component_signal,
    pv_string_current,
)

SAMPLE: dict[str, Any] = json.loads(
    (Path(__file__).parent / "fixtures" / "components_pw3_two_expansions.json")
    .read_text()
)
LEADER_DIN = "1707000-30-L--TG10000000000A"
EXP1_DIN = "1807000-20-B--TG10000000002C"
EXP2_DIN = "1807000-20-B--TG10000000003D"


@pytest.fixture
def sample() -> dict[str, Any]:
    return copy.deepcopy(SAMPLE)


def _bms(components: dict[str, Any], slot: int) -> dict[str, Any]:
    row: dict[str, Any] = components["components"]["bms"][slot]
    return row


def _set_signal(row: dict[str, Any], name: str, value: float) -> None:
    for signal in row["signals"]:
        if signal["name"] == name:
            signal["value"] = value


# ── L1a: signal accessor ────────────────────────────────────────────────────


def test_component_signal_prefers_value_then_text_then_bool() -> None:
    components = SAMPLE["components"]
    assert component_signal(components, "bms", "BMS_nominalFullPackEnergy", 2) == 14.38
    assert component_signal(components, "pch", "PCH_State") == "Pch_Active"
    assert component_signal(components, "pws", "PWS_ProdSwitch_State") is True
    assert component_signal(components, "baggr", "BAGGR_NumBatteriesConnected") == 3


def test_component_signal_missing_returns_none() -> None:
    components = SAMPLE["components"]
    assert component_signal(components, "bms", "BMS_nominalFullPackEnergy", 3) is None
    assert component_signal(components, "bms", "BMS_nominalFullPackEnergy", 9) is None
    assert component_signal(components, "bms", "NoSuchSignal") is None
    assert component_signal(components, "nope", "BMS_nominalFullPackEnergy") is None
    assert component_signal({}, "bms", "BMS_nominalFullPackEnergy") is None


def test_component_float_rejects_text_and_bool() -> None:
    components = SAMPLE["components"]
    assert component_float(components, "bms", "BMS_nominalEnergyRemaining", 1) == 11.83
    assert component_float(components, "pch", "PCH_State") is None
    assert component_float(components, "pws", "PWS_ProdSwitch_State") is None


def test_component_serial_skips_empty() -> None:
    components = SAMPLE["components"]
    assert component_serial(components, 0) == "TG10000000001B"
    assert component_serial(components, 3) is None


# ── L1c: PV string current noise ────────────────────────────────────────────


def test_pv_string_current_rounds_idle_noise_to_zero(sample: dict[str, Any]) -> None:
    components = sample["components"]
    # The sample reports -3.6e-16 A on every idle string.
    assert component_float(components, "pch", "PCH_PvCurrentA") == pytest.approx(0)
    assert pv_string_current(components, "A") == 0.0
    _set_signal(components["components"]["pch"][0], "PCH_PvCurrentB", 4.25)
    assert pv_string_current(components, "B") == 4.25
    assert pv_string_current({}, "A") is None


# ── L1b: per-battery unit model ─────────────────────────────────────────────


def test_battery_units_real_sample() -> None:
    units = battery_units(SAMPLE["config"], SAMPLE["status"], SAMPLE["components"])
    assert units == (
        BatteryUnit("leader", 0, 0, LEADER_DIN, "TG10000000001B", "1800420-11-F"),
        BatteryUnit("expansion", 0, 1, EXP1_DIN, "TG10000000002C", "1807000-20-B"),
        BatteryUnit("expansion", 0, 2, EXP2_DIN, "TG10000000003D", "1807000-20-B"),
    )


def test_ghost_expansion_dropped_when_aggregate_matches(
    sample: dict[str, Any],
) -> None:
    # Slot 3 looks like a pack with no serial and almost no energy left; the
    # aggregate 43.2 kWh already matches slots 0-2.
    ghost = _bms(sample["components"], 3)
    _set_signal(ghost, "BMS_nominalFullPackEnergy", 14.4)
    _set_signal(ghost, "BMS_nominalEnergyRemaining", 0.1)

    units = battery_units(sample["config"], sample["status"], sample["components"])
    assert [u.component_slot for u in units] == [0, 1, 2]


def test_no_serial_pack_kept_when_aggregate_includes_it(
    sample: dict[str, Any],
) -> None:
    pack = _bms(sample["components"], 3)
    _set_signal(pack, "BMS_nominalFullPackEnergy", 14.4)
    _set_signal(pack, "BMS_nominalEnergyRemaining", 0.1)
    sample["status"]["control"]["systemStatus"]["nominalFullPackEnergyWh"] = 57600

    units = battery_units(sample["config"], sample["status"], sample["components"])
    assert units[-1] == BatteryUnit("expansion", 0, 3, None, None, None)


def test_configured_expansion_without_bms_row_dropped(
    sample: dict[str, Any],
) -> None:
    sample["config"]["battery_blocks"][0]["battery_expansions"].append(
        {"din": "1807000-20-B--TG10000000009Z"}
    )
    units = battery_units(sample["config"], sample["status"], sample["components"])
    assert [u.din for u in units] == [LEADER_DIN, EXP1_DIN, EXP2_DIN]


def test_follower_from_status_takes_unserialed_slot(sample: dict[str, Any]) -> None:
    # A follower Powerwall only in the status batteryBlocks; its BMS row
    # (slot 3) has no serial, so it is preferred over the expansion slots.
    follower_din = "1707000-30-L--TG10000000004E"
    sample["status"]["control"]["batteryBlocks"].append({"din": follower_din})
    pack = _bms(sample["components"], 3)
    _set_signal(pack, "BMS_nominalFullPackEnergy", 14.4)
    _set_signal(pack, "BMS_nominalEnergyRemaining", 10.0)

    units = battery_units(sample["config"], sample["status"], sample["components"])
    assert [(u.role, u.block_index, u.component_slot, u.din) for u in units] == [
        ("leader", 0, 0, LEADER_DIN),
        ("expansion", 0, 1, EXP1_DIN),
        ("expansion", 0, 2, EXP2_DIN),
        ("follower", 1, 3, follower_din),
    ]


def test_unconfigured_bms_row_inferred_as_leader_expansion(
    sample: dict[str, Any],
) -> None:
    sample["config"]["battery_blocks"][0]["battery_expansions"] = [{"din": EXP1_DIN}]
    units = battery_units(sample["config"], sample["status"], sample["components"])
    assert units[-1] == BatteryUnit(
        "expansion", 0, 2, None, "TG10000000003D", "1807000-20-B"
    )


def test_no_bms_rows_keeps_config_shape(sample: dict[str, Any]) -> None:
    sample["components"]["components"]["bms"] = []
    units = battery_units(sample["config"], sample["status"], sample["components"])
    assert [(u.role, u.component_slot, u.din) for u in units] == [
        ("leader", 0, LEADER_DIN),
        ("expansion", 1, EXP1_DIN),
        ("expansion", 2, EXP2_DIN),
    ]


def test_empty_payloads_yield_single_leader() -> None:
    assert battery_units({}, {}, {}) == (
        BatteryUnit("leader", 0, 0, None, None, None),
    )
