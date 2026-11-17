"""Typed helpers over the :meth:`PowerwallClient.get_components` payload.

The components payload has the shape
``{"components": {<kind>: [{"partNumber", "serialNumber", "signals": [...],
"activeAlerts": [...]}, ...]}}``, where ``<kind>`` is one of ``pch``,
``pws``, ``bms``, ``hvp`` or ``baggr`` and each list position is a component
slot. Every signal is ``{"name", "value", "textValue", "boolValue",
"timestamp"}`` with at most one of the three value fields set.
"""

from __future__ import annotations

import logging
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Final, Literal, cast

from .models import ComponentsPayload, ConfigPayload, StatusPayload

_LOGGER = logging.getLogger(__name__)

SignalValue = float | str | bool

# PCH PV string currents read as ~1e-16 A float noise when a string is idle.
_PV_CURRENT_NOISE_FLOOR_A = 1e-3

BatteryRole = Literal["leader", "follower", "expansion"]

PV_STRINGS: Final = ("A", "B", "C", "D", "E", "F")
"""The PV string inputs of a Powerwall 3 PCH."""

PvStringState = Literal["active", "active_parallel", "standby"]

_PV_STRING_STATES: Final[dict[str, PvStringState]] = {
    "Pv_Active": "active",
    "Pv_Active_Parallel": "active_parallel",
    "Pv_Standby": "standby",
}
PV_STRING_STATES: Final[tuple[PvStringState, ...]] = tuple(_PV_STRING_STATES.values())
"""Every value :func:`pv_string_state` can return."""


def _path(data: Any, *keys: str | int) -> Any:
    """Walk nested mappings and lists; return None if a step is missing."""
    for key in keys:
        if isinstance(key, int):
            if not isinstance(data, list):
                return None
            items = cast(list[Any], data)
            if not 0 <= key < len(items):
                return None
            data = items[key]
        else:
            if not isinstance(data, Mapping):
                return None
            data = cast(Mapping[str, Any], data).get(key)
    return data


def component(
    components: ComponentsPayload, kind: str, slot: int = 0
) -> Mapping[str, Any] | None:
    """Return the ``kind`` component at ``slot``, or None if absent."""
    item = _path(components, "components", kind, slot)
    return cast(Mapping[str, Any], item) if isinstance(item, Mapping) else None


def _signal(item: Mapping[str, Any] | None, name: str) -> SignalValue | None:
    if item is None:
        return None
    signals: Any = item.get("signals") or ()
    for signal in signals:
        if not isinstance(signal, Mapping):
            continue
        signal = cast(Mapping[str, Any], signal)
        if signal.get("name") != name:
            continue
        for field in ("value", "textValue", "boolValue"):
            value = signal.get(field)
            if value is not None:
                return value  # type: ignore[no-any-return]
        return None
    return None


def component_signal(
    components: ComponentsPayload, kind: str, name: str, slot: int = 0
) -> SignalValue | None:
    """Return one signal of the ``kind`` component at ``slot``.

    Prefers the signal's ``value`` (number), then ``textValue``, then
    ``boolValue``. Returns None when the component, the signal or all three
    value fields are missing.
    """
    return _signal(component(components, kind, slot), name)


def component_float(
    components: ComponentsPayload, kind: str, name: str, slot: int = 0
) -> float | None:
    """Return a numeric signal as float, or None if it is missing or not a number."""
    value = component_signal(components, kind, name, slot)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return float(value)


def pv_string_current(
    components: ComponentsPayload, string: str, slot: int = 0
) -> float | None:
    """Return PCH PV string ``string`` (``"A"``-``"F"``) current in amps.

    An idle string reports float noise (about 1e-16 A) instead of 0; values
    below 1e-3 A are returned as 0.0.
    """
    value = component_float(components, "pch", f"PCH_PvCurrent{string}", slot)
    if value is not None and abs(value) < _PV_CURRENT_NOISE_FLOOR_A:
        return 0.0
    return value


def pv_string_voltage(
    components: ComponentsPayload, string: str, slot: int = 0
) -> float | None:
    """Return PCH PV string ``string`` (``"A"``-``"F"``) voltage in volts."""
    return component_float(components, "pch", f"PCH_PvVoltage{string}", slot)


def pv_string_state(
    components: ComponentsPayload, string: str, slot: int = 0
) -> PvStringState | None:
    """Return the state of PCH PV string ``string`` (``"A"``-``"F"``).

    Only the states in :data:`PV_STRING_STATES` are returned; any other
    gateway value returns None.
    """
    value = component_signal(components, "pch", f"PCH_PvState_{string}", slot)
    return _PV_STRING_STATES.get(value) if isinstance(value, str) else None


def pv_power(components: ComponentsPayload, slot: int = 0) -> float | None:
    """Return the total PV power of the PCH at ``slot`` in watts."""
    return component_float(components, "pch", "PCH_SlowPvPowerSum", slot)


def _component_text(
    components: ComponentsPayload, kind: str, name: str, slot: int
) -> str | None:
    value = component_signal(components, kind, name, slot)
    return value if isinstance(value, str) else None


def component_serial(components: ComponentsPayload, slot: int) -> str | None:
    """Return the first non-empty serial number reported for component ``slot``."""
    for kind in ("hvp", "bms", "pch", "baggr"):
        value = _path(components, "components", kind, slot, "serialNumber")
        if isinstance(value, str) and value:
            return value
    return None


def component_part_number(components: ComponentsPayload, slot: int) -> str | None:
    """Return the first non-empty part number reported for component ``slot``."""
    for kind in ("hvp", "bms", "pch", "baggr"):
        value = _path(components, "components", kind, slot, "partNumber")
        if isinstance(value, str) and value:
            return value
    return None


@dataclass(frozen=True, slots=True)
class BatteryUnit:
    """One battery unit: a Powerwall (leader or follower) or an expansion.

    ``din`` is the physical DIN from ``config.json`` / status when the gateway
    reports one, else None (an expansion found only in the components
    payload). ``serial_number`` and ``part_number`` come from the components
    payload. ``component_slot`` is the index to read in each
    ``components[<kind>]`` list for this unit; it can be past the end of those
    lists when the gateway returns no BMS rows yet. ``block_index`` is the
    position of the owning Powerwall in ``config.json`` ``battery_blocks``.
    """

    role: BatteryRole
    block_index: int
    component_slot: int
    din: str | None
    serial_number: str | None
    part_number: str | None

    @property
    def unit_id(self) -> str | None:
        """Return a stable id for this unit: its serial number for an expansion, else its DIN.

        An expansion's DIN is only in ``config.json``, so its serial number is
        the id that is known from the status and components payloads alone.
        """
        return self.serial_number if self.role == "expansion" else self.din


def _din(item: Mapping[str, Any]) -> str | None:
    for key in ("din", "vin"):
        value = item.get(key)
        if isinstance(value, str) and value:
            return value
    return None


def _serial_from_din(din: str) -> str:
    return din.rsplit("--", 1)[-1]


def _status_battery_dins(status: StatusPayload) -> list[str]:
    blocks = _path(status, "control", "batteryBlocks")
    if not isinstance(blocks, list):
        return []
    return [
        din
        for block in cast(list[Any], blocks)
        if isinstance(block, Mapping)
        and (din := _din(cast(Mapping[str, Any], block))) is not None
    ]


def _bms_slots(components: ComponentsPayload) -> list[int]:
    """Return component slots that look like real BMS modules."""
    items = _path(components, "components", "bms")
    if not isinstance(items, list):
        return []
    slots: list[int] = []
    for slot in range(len(cast(list[Any], items))):
        full = component_float(components, "bms", "BMS_nominalFullPackEnergy", slot)
        if full is not None and full > 0:
            slots.append(slot)
    return slots


def _ghost_filtered_bms_slots(
    components: ComponentsPayload, status: StatusPayload
) -> list[int]:
    """Return BMS slots after dropping phantom expansion rows.

    The gateway can keep a registered-but-not-installed expansion row: it has
    a plausible full capacity, no serial number and near-zero remaining
    energy. Drop such rows only when the system aggregate capacity already
    matches the kept rows, so a real pack with no serial and a stale
    remaining-energy reading is kept.
    """
    slots = _bms_slots(components)
    aggregate_wh = _path(status, "control", "systemStatus", "nominalFullPackEnergyWh")
    if (
        not slots
        or isinstance(aggregate_wh, bool)
        or not isinstance(aggregate_wh, (int, float))
        or aggregate_wh <= 0
    ):
        return slots
    aggregate_kwh = aggregate_wh / 1000

    ghosts: list[int] = []
    for slot in slots:
        if component_serial(components, slot):
            continue
        full = component_float(components, "bms", "BMS_nominalFullPackEnergy", slot)
        remaining = component_float(
            components, "bms", "BMS_nominalEnergyRemaining", slot
        )
        if full is None or full <= 0 or remaining is None:
            continue
        if remaining < 0.5 or remaining / full < 0.05:
            ghosts.append(slot)
    if not ghosts:
        return slots

    kept = [slot for slot in slots if slot not in ghosts]
    kept_kwh = sum(
        component_float(components, "bms", "BMS_nominalFullPackEnergy", slot) or 0.0
        for slot in kept
    )
    if kept_kwh > 0 and abs(aggregate_kwh - kept_kwh) / aggregate_kwh < 0.10:
        _LOGGER.warning(
            "Dropping %d ghost Powerwall expansion slot(s): aggregate %.2f kWh "
            "matches real BMS slot sum %.2f kWh",
            len(ghosts),
            aggregate_kwh,
            kept_kwh,
        )
        return kept
    return slots


def _follower_slots(
    components: ComponentsPayload,
    powerwall_count: int,
    expansion_slots: set[int],
    bms_slots: list[int],
) -> list[int]:
    """Choose component slots for follower Powerwalls.

    Slots matched to a configured expansion are never chosen. When enough
    candidate BMS rows have no serial number, prefer those; otherwise take
    the last candidate slots.
    """
    follower_count = max(0, powerwall_count - 1)
    if follower_count == 0:
        return []
    if not bms_slots:
        return list(range(1, powerwall_count))

    candidates = [s for s in bms_slots if s != 0 and s not in expansion_slots]
    no_serial = [s for s in candidates if not component_serial(components, s)]
    pool = no_serial if len(no_serial) >= follower_count else candidates
    chosen = pool[-follower_count:]
    fallback = 1
    while len(chosen) < follower_count:
        if fallback not in chosen and fallback not in expansion_slots:
            chosen.append(fallback)
        fallback += 1
    return sorted(chosen)


def battery_units(
    config: ConfigPayload,
    status: StatusPayload,
    components: ComponentsPayload,
) -> tuple[BatteryUnit, ...]:
    """Return every battery unit of the site with its component slot.

    Powerwalls come from ``config.json`` ``battery_blocks`` plus any extra DIN
    in the status ``batteryBlocks``; the first is the leader (slot 0), the
    rest are followers. Expansions come from each block's
    ``battery_expansions`` and are matched to a component slot by serial
    number. A configured expansion with no real BMS row is dropped, and a real
    BMS row that no configured unit claims is added as an expansion of the
    leader with ``din=None``. Phantom expansion rows are filtered first (see
    :func:`_ghost_filtered_bms_slots`).

    Units are ordered by block: each Powerwall, then its expansions.
    """
    blocks: list[Mapping[str, Any]] = [
        cast(Mapping[str, Any], b)
        for b in cast(list[Any], config.get("battery_blocks") or [])
        if isinstance(b, Mapping)
    ]
    known = {_din(b) for b in blocks}
    for status_din in _status_battery_dins(status):
        if status_din not in known:
            blocks.append({"din": status_din})
            known.add(status_din)
    if not blocks:
        blocks.append({})
    powerwall_count = len(blocks)

    expansion_dins_by_block = [
        [
            din
            for expansion in cast(list[Any], block.get("battery_expansions") or [])
            if isinstance(expansion, Mapping)
            and (din := _din(cast(Mapping[str, Any], expansion)))
        ]
        for block in blocks
    ]
    bms_slots = _ghost_filtered_bms_slots(components, status)

    serial_to_din = {
        serial: din
        for dins in expansion_dins_by_block
        for din in dins
        if (serial := _serial_from_din(din))
    }
    matched: dict[str, int] = {}
    for bms_slot in bms_slots:
        slot_serial = component_serial(components, bms_slot)
        matched_din = serial_to_din.get(slot_serial) if slot_serial else None
        if matched_din is not None and matched_din not in matched:
            matched[matched_din] = bms_slot

    follower_slots = _follower_slots(
        components, powerwall_count, set(matched.values()), bms_slots
    )
    assigned = {0, *follower_slots, *matched.values()}
    unclaimed = [s for s in bms_slots if s not in assigned]
    next_unobserved = max(powerwall_count, len(bms_slots))

    expansions_by_block: list[list[tuple[str | None, int]]] = []
    for dins in expansion_dins_by_block:
        expansions: list[tuple[str | None, int]] = []
        for expansion_din in dins:
            expansion_slot = matched.get(expansion_din)
            if expansion_slot is None:
                # A serialized row that matched no configured DIN is a
                # different unit; only an unserialized row can be this one.
                unserialized = [
                    s for s in unclaimed if not component_serial(components, s)
                ]
                if unserialized:
                    expansion_slot = unserialized[0]
                    unclaimed.remove(expansion_slot)
                elif not bms_slots:
                    # No BMS rows at all: keep the config-driven unit list
                    # until the gateway starts returning them.
                    expansion_slot = next_unobserved
                    next_unobserved += 1
                else:
                    _LOGGER.warning(
                        "Dropping configured Powerwall expansion %s because no "
                        "real BMS component slot is present",
                        expansion_din,
                    )
                    continue
            expansions.append((expansion_din, expansion_slot))
        expansions_by_block.append(expansions)
    expansions_by_block[0].extend((None, slot) for slot in unclaimed)

    units: list[BatteryUnit] = []
    for index, block in enumerate(blocks):
        slot = (
            0
            if index == 0
            else follower_slots[index - 1]
            if index - 1 < len(follower_slots)
            else index
        )
        members: list[tuple[BatteryRole, str | None, int]] = [
            ("leader" if index == 0 else "follower", _din(block), slot)
        ]
        members.extend(("expansion", din, s) for din, s in expansions_by_block[index])
        units.extend(
            BatteryUnit(
                role=role,
                block_index=index,
                component_slot=s,
                din=din,
                serial_number=component_serial(components, s),
                part_number=component_part_number(components, s),
            )
            for role, din, s in members
        )
    return tuple(units)


@dataclass(frozen=True, slots=True)
class PvString:
    """One PV string input of a Powerwall 3."""

    voltage: float | None
    """Volts."""
    current: float | None
    """Amps, with idle noise read as 0.0 (see :func:`pv_string_current`)."""
    state: PvStringState | None


def pv_strings(components: ComponentsPayload, slot: int = 0) -> dict[str, PvString]:
    """Return every PV string of the PCH at ``slot``, keyed by :data:`PV_STRINGS`."""
    return {
        string: PvString(
            voltage=pv_string_voltage(components, string, slot),
            current=pv_string_current(components, string, slot),
            state=pv_string_state(components, string, slot),
        )
        for string in PV_STRINGS
    }


@dataclass(frozen=True, slots=True)
class BatteryUnitReadings:
    """The components-payload readings of one :class:`BatteryUnit`.

    Every value is None when the gateway does not report it for the unit.
    An expansion has no PCH or PWS, so its PCH and PWS readings are always
    None and its PV strings are all None, rather than another unit's row at
    the same slot.
    """

    energy_remaining: float | None
    """BMS nominal energy remaining, kWh."""
    full_pack_energy: float | None
    """BMS nominal full pack energy, kWh."""
    percentage_charged: float | None
    """``energy_remaining / full_pack_energy * 100``.

    This is the raw pack ratio, including the bottom buffer that
    :func:`~tesla_fleet_api.tesla.powerwall.battery_level` scales out, so it
    reads slightly above the site percentage. None while either value is
    missing or the full pack energy is 0.
    """
    hvp_state: str | None
    """The gateway's own text, such as ``HVP_ACTIVE``."""
    hvp_firmware: str | None
    battery_connection_status: str | None
    """The battery aggregator's status for this slot, such as ``CONNECTED``."""
    battery_power: float | None
    """PCH battery power, W."""
    ac_power: float | None
    """PCH AC real power, W."""
    ac_voltage_ab: float | None
    ac_voltage_an: float | None
    ac_voltage_bn: float | None
    ac_frequency: float | None
    """Hz."""
    pch_state: str | None
    """The gateway's own text, such as ``Pch_Active``."""
    pch_firmware: str | None
    pws_firmware: str | None
    pv_strings: dict[str, PvString]
    """Keyed by :data:`PV_STRINGS`."""


def battery_unit_readings(
    components: ComponentsPayload, unit: BatteryUnit
) -> BatteryUnitReadings:
    """Return the readings of ``unit`` from a components payload."""
    slot = unit.component_slot
    powerwall = unit.role != "expansion"

    def number(kind: str, name: str) -> float | None:
        return component_float(components, kind, name, slot)

    def text(kind: str, name: str) -> str | None:
        return _component_text(components, kind, name, slot)

    def powerwall_number(name: str) -> float | None:
        return number("pch", name) if powerwall else None

    def powerwall_text(kind: str, name: str) -> str | None:
        return text(kind, name) if powerwall else None

    remaining = number("bms", "BMS_nominalEnergyRemaining")
    full = number("bms", "BMS_nominalFullPackEnergy")
    return BatteryUnitReadings(
        energy_remaining=remaining,
        full_pack_energy=full,
        percentage_charged=(
            remaining / full * 100 if remaining is not None and full else None
        ),
        hvp_state=text("hvp", "HVP_State"),
        hvp_firmware=text("hvp", "HVP_appGitHash"),
        # The battery aggregator reports one connection status per slot.
        battery_connection_status=_component_text(
            components, "baggr", f"BAGGR_LOG_BattConnectionStatus{slot}", 0
        ),
        battery_power=powerwall_number("PCH_BatteryPower"),
        ac_power=powerwall_number("PCH_AcRealPowerAB"),
        ac_voltage_ab=powerwall_number("PCH_AcVoltageAB"),
        ac_voltage_an=powerwall_number("PCH_AcVoltageAN"),
        ac_voltage_bn=powerwall_number("PCH_AcVoltageBN"),
        ac_frequency=powerwall_number("PCH_AcFrequency"),
        pch_state=powerwall_text("pch", "PCH_State"),
        pch_firmware=powerwall_text("pch", "PCH_appGitHash"),
        pws_firmware=powerwall_text("pws", "PWS_appGitHash"),
        pv_strings=(
            pv_strings(components, slot)
            if powerwall
            else dict.fromkeys(PV_STRINGS, PvString(None, None, None))
        ),
    )


__all__ = [
    "PV_STRINGS",
    "PV_STRING_STATES",
    "BatteryRole",
    "BatteryUnit",
    "BatteryUnitReadings",
    "PvString",
    "PvStringState",
    "SignalValue",
    "battery_unit_readings",
    "battery_units",
    "component",
    "component_float",
    "component_part_number",
    "component_serial",
    "component_signal",
    "pv_power",
    "pv_string_current",
    "pv_string_state",
    "pv_string_voltage",
    "pv_strings",
]
