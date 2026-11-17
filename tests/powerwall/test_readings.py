"""Unit tests for the typed readers over the status, config and components payloads.

``fixtures/powerwall_{status,config,components}.json`` are a Powerwall 3
leader with two expansions and an empty fourth component slot, with serial
numbers replaced. The single Powerwall and leader + follower sites are
derived from them.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import pytest

from tesla_fleet_api.tesla.powerwall import (
    PV_STRING_STATES,
    PV_STRINGS,
    BatteryUnit,
    PvString,
    battery_unit_readings,
    battery_units,
    islander_frequency,
    islander_voltage,
    pv_power,
    pv_string_state,
    pv_strings,
    site_info,
)

FIXTURES = Path(__file__).parent / "fixtures"
STATUS: dict[str, Any] = json.loads((FIXTURES / "powerwall_status.json").read_text())
CONFIG: dict[str, Any] = json.loads((FIXTURES / "powerwall_config.json").read_text())
COMPONENTS: dict[str, Any] = json.loads(
    (FIXTURES / "powerwall_components.json").read_text()
)
LEADER_DIN = "1707000-30-L--TG10000000000A"
FOLLOWER_DIN = "1707000-30-L--TG10000000004E"
NO_PV = PvString(voltage=None, current=None, state=None)


def _set_signal(row: dict[str, Any], name: str, value: Any) -> None:
    for signal in row["signals"]:
        if signal["name"] == name:
            signal["value"] = None
            signal["textValue"] = None
            signal["value" if isinstance(value, (int, float)) else "textValue"] = value
            return
    raise AssertionError(name)


@pytest.fixture
def components() -> dict[str, Any]:
    return copy.deepcopy(COMPONENTS)


@pytest.fixture
def single_powerwall() -> dict[str, Any]:
    """A Powerwall 3 with no expansions."""
    components = copy.deepcopy(COMPONENTS)
    for kind in ("bms", "hvp"):
        components["components"][kind] = components["components"][kind][:1]
    return components


@pytest.fixture
def leader_and_follower() -> tuple[dict[str, Any], dict[str, Any]]:
    """A leader and one follower Powerwall 3, each with its own PCH and PWS row."""
    status = copy.deepcopy(STATUS)
    status["control"]["batteryBlocks"].append(
        {"din": FOLLOWER_DIN, "disableReasons": []}
    )
    status["control"]["systemStatus"]["nominalFullPackEnergyWh"] = 28840
    components = copy.deepcopy(COMPONENTS)
    for kind in ("bms", "hvp"):
        components["components"][kind] = components["components"][kind][:2]
    components["components"]["hvp"][1]["partNumber"] = "1707000-30-L"
    for kind in ("pch", "pws"):
        components["components"][kind].append(
            copy.deepcopy(components["components"][kind][0])
        )
    follower_pch = components["components"]["pch"][1]
    _set_signal(follower_pch, "PCH_PvVoltageA", 401.5)
    _set_signal(follower_pch, "PCH_PvState_A", "Pv_Active_Parallel")
    _set_signal(follower_pch, "PCH_BatteryPower", -2500)
    _set_signal(follower_pch, "PCH_SlowPvPowerSum", 1200.0)
    _set_signal(components["components"]["pws"][1], "PWS_appGitHash", "abc123")
    return status, components


# ── Battery units ───────────────────────────────────────────────────────────


def test_leader_with_expansions(components: dict[str, Any]) -> None:
    units = battery_units({}, STATUS, components)
    assert [(u.role, u.component_slot, u.unit_id) for u in units] == [
        ("leader", 0, LEADER_DIN),
        ("expansion", 1, "TG10000000002C"),
        ("expansion", 2, "TG10000000003D"),
    ]
    leader = battery_unit_readings(components, units[0])
    assert leader.energy_remaining == pytest.approx(10.54)
    assert leader.full_pack_energy == 14.42
    assert leader.percentage_charged == pytest.approx(10.54 / 14.42 * 100)
    assert leader.hvp_state == "HVP_ACTIVE"
    assert leader.hvp_firmware == "04d5dd98fb2037"
    assert leader.battery_connection_status == "CONNECTED"
    assert leader.battery_power == 1020.0
    assert leader.ac_power == 880.0
    assert leader.ac_voltage_ab == 238.4
    assert leader.ac_voltage_an == 118.8
    assert leader.ac_voltage_bn == 119.6
    assert leader.ac_frequency == 50.0025
    assert leader.pch_state == "Pch_Active"
    assert leader.pch_firmware == "4f924de839f0c4"
    assert leader.pws_firmware == "04d5dd98fb2037"
    assert leader.pv_strings == pv_strings(components)

    expansion = battery_unit_readings(components, units[2])
    assert expansion.energy_remaining == 11.27
    assert expansion.full_pack_energy == 14.38
    assert expansion.hvp_state == "HVP_ACTIVE"
    assert expansion.battery_connection_status == "CONNECTED"


def test_expansion_never_reads_powerwall_rows(components: dict[str, Any]) -> None:
    """An expansion's slot must not pick up a Powerwall 3's PCH or PWS row."""
    for kind in ("pch", "pws"):
        rows = components["components"][kind]
        rows.extend(copy.deepcopy(rows[0]) for _ in range(2))
    expansion = battery_units({}, STATUS, components)[1]
    readings = battery_unit_readings(components, expansion)
    assert readings.battery_power is None
    assert readings.ac_power is None
    assert readings.ac_voltage_ab is None
    assert readings.ac_voltage_an is None
    assert readings.ac_voltage_bn is None
    assert readings.ac_frequency is None
    assert readings.pch_state is None
    assert readings.pch_firmware is None
    assert readings.pws_firmware is None
    assert readings.pv_strings == dict.fromkeys(PV_STRINGS, NO_PV)


def test_single_powerwall(single_powerwall: dict[str, Any]) -> None:
    (leader,) = battery_units({}, STATUS, single_powerwall)
    assert leader.role == "leader"
    assert leader.unit_id == LEADER_DIN
    readings = battery_unit_readings(single_powerwall, leader)
    assert readings.battery_power == 1020.0
    assert readings.pv_strings["A"] == PvString(
        voltage=385.2, current=6.42, state="active"
    )


def test_leader_and_follower(
    leader_and_follower: tuple[dict[str, Any], dict[str, Any]],
) -> None:
    status, components = leader_and_follower
    units = battery_units({}, status, components)
    assert [(u.role, u.component_slot, u.unit_id) for u in units] == [
        ("leader", 0, LEADER_DIN),
        ("follower", 1, FOLLOWER_DIN),
    ]
    leader = battery_unit_readings(components, units[0])
    follower = battery_unit_readings(components, units[1])
    assert leader.battery_power == 1020.0
    assert follower.battery_power == -2500.0
    assert leader.pws_firmware == "04d5dd98fb2037"
    assert follower.pws_firmware == "abc123"
    assert follower.energy_remaining == 11.83
    assert follower.battery_connection_status == "CONNECTED"
    assert leader.pv_strings["A"] == PvString(
        voltage=385.2, current=6.42, state="active"
    )
    assert follower.pv_strings["A"] == PvString(
        voltage=401.5, current=6.42, state="active_parallel"
    )
    assert follower.pv_strings == pv_strings(components, 1)
    assert pv_power(components) == 4868.0
    assert pv_power(components, 1) == 1200.0


def test_unit_id_falls_back_to_none() -> None:
    expansion = BatteryUnit(
        role="expansion",
        block_index=0,
        component_slot=1,
        din="1807000-20-B--TG10000000002C",
        serial_number=None,
        part_number=None,
    )
    assert expansion.unit_id is None


def test_percentage_charged_needs_both_energies(components: dict[str, Any]) -> None:
    leader = battery_units({}, STATUS, components)[0]
    _set_signal(components["components"]["bms"][0], "BMS_nominalFullPackEnergy", 0)
    assert battery_unit_readings(components, leader).percentage_charged is None
    components["components"]["bms"][0]["signals"] = []
    readings = battery_unit_readings(components, leader)
    assert readings.energy_remaining is None
    assert readings.percentage_charged is None


def test_connection_status_is_read_at_the_unit_slot(
    components: dict[str, Any],
) -> None:
    _set_signal(
        components["components"]["baggr"][0],
        "BAGGR_LOG_BattConnectionStatus2",
        "NOT_CONNECTED",
    )
    units = battery_units({}, STATUS, components)
    statuses = [
        battery_unit_readings(components, u).battery_connection_status for u in units
    ]
    assert statuses == ["CONNECTED", "CONNECTED", "NOT_CONNECTED"]


def test_empty_components_read_as_none() -> None:
    (leader,) = battery_units({}, {}, {})
    readings = battery_unit_readings({}, leader)
    assert readings.energy_remaining is None
    assert readings.hvp_state is None
    assert readings.battery_connection_status is None
    assert readings.battery_power is None
    assert readings.pv_strings == dict.fromkeys(PV_STRINGS, NO_PV)


# ── PV strings ──────────────────────────────────────────────────────────────


def test_pv_strings(components: dict[str, Any]) -> None:
    strings = pv_strings(components)
    assert list(strings) == list(PV_STRINGS)
    assert strings["B"] == PvString(voltage=379.6, current=6.31, state="active")
    # The fixture's idle string C reports float noise current.
    assert strings["C"] == PvString(voltage=0.0, current=0.0, state="standby")
    assert pv_power(components) == 4868.0


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("Pv_Active", "active"),
        ("Pv_Active_Parallel", "active_parallel"),
        ("Pv_Standby", "standby"),
        ("Pv_Fault", None),
        (1, None),
    ],
)
def test_pv_string_state_is_an_allowlist(
    components: dict[str, Any], raw: Any, expected: str | None
) -> None:
    _set_signal(components["components"]["pch"][0], "PCH_PvState_A", raw)
    assert pv_string_state(components, "A") == expected
    assert expected is None or expected in PV_STRING_STATES


def test_pv_readings_missing() -> None:
    assert pv_strings({}) == dict.fromkeys(PV_STRINGS, NO_PV)
    assert pv_power({}) is None


# ── Status and config ───────────────────────────────────────────────────────


def test_islander_measurements() -> None:
    assert islander_frequency(STATUS, 1, "load") == 50.01
    assert islander_frequency(STATUS, 3, "main") == 50.03
    assert islander_voltage(STATUS, 1, "main") == 240.5
    assert islander_voltage(STATUS, 2, "load") == 7.5
    assert islander_voltage(STATUS, 3, "main") == 0.5


def test_islander_measurements_missing() -> None:
    assert islander_frequency({}, 1, "main") is None
    status = copy.deepcopy(STATUS)
    measurements = status["esCan"]["bus"]["ISLANDER"]["ISLAND_AcMeasurements"]
    measurements["ISLAND_VL1N_Main"] = None
    measurements["ISLAND_FreqL1_Main"] = True
    assert islander_voltage(status, 1, "main") is None
    assert islander_frequency(status, 1, "main") is None


def test_site_info() -> None:
    info = site_info(CONFIG)
    assert info.grid_code == "50Hz_230V_1_SMC_ASNZS4777.2_2020_AUS_A"
    assert info.country == "Australia"
    assert info.distributor == "Energex"


def test_site_info_missing() -> None:
    info = site_info({"site_info": {"country": 1}})
    assert info.grid_code is None
    assert info.country is None
    assert info.distributor is None
    assert site_info({}).grid_code is None
