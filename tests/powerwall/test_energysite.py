"""Unit tests for the EnergySite-compatible adapter.

These exercise :class:`PowerwallEnergySite` against a hand-rolled fake
:class:`PowerwallClient` — no real hardware, LAN, or transport. They assert
that each implemented command maps to the right client call and returns the
cloud command envelope, that placeholder commands raise ``NotImplementedError``,
that ``site_info`` is absent (so a router falls through to the cloud), and that
``live_status``/``local_config`` produce the expected cloud-shaped keys from
mocked local data.
"""

from __future__ import annotations

from typing import Any, cast

import pytest

from tesla_fleet_api.tesla.powerwall import AuthorizedClients, AuthorizedClientState, PowerwallClient
from tesla_fleet_api.tesla.powerwall.client import raw_to_scaled_reserve
from tesla_fleet_api.tesla.powerwall.energysite import (
    ISLAND_MODE_OFF_GRID,
    ISLAND_MODE_ON_GRID,
    PowerwallEnergySite,
)


class FakeClient:
    """Records the client calls the adapter makes and returns canned reads."""

    def __init__(self) -> None:
        self.calls: list[tuple[Any, ...]] = []
        self.config: dict[str, Any] = {
            "site_info": {"backup_reserve_percent": 25.0},
            "default_real_mode": "self_consumption",
        }

    # writes / commands -----------------------------------------------------
    async def connect(self) -> str:
        self.calls.append(("connect",))
        return "1234567-00-A--CJ2000000000"

    async def set_operation_mode(self, mode: str) -> None:
        self.calls.append(("set_operation_mode", mode))

    async def set_backup_reserve(self, percent: float) -> None:
        self.calls.append(("set_backup_reserve", percent))

    async def set_grid_import_export(
        self,
        *,
        customer_preferred_export_rule: str | None = None,
        disallow_charge_from_grid_with_solar_installed: bool | None = None,
    ) -> None:
        self.calls.append(
            (
                "set_grid_import_export",
                customer_preferred_export_rule,
                disallow_charge_from_grid_with_solar_installed,
            )
        )

    async def set_island_mode(
        self,
        *,
        off_grid: bool,
        force: bool = True,
        mode_override: int | None = None,
    ) -> None:
        self.calls.append(("set_island_mode", off_grid, force, mode_override))

    async def go_off_grid(
        self, *, force: bool = True, mode_override: int | None = None
    ) -> None:
        self.calls.append(("go_off_grid",))

    async def reconnect_grid(self) -> None:
        self.calls.append(("reconnect_grid",))

    async def schedule_max_backup(self, duration_seconds: int = 7200) -> None:
        self.calls.append(("schedule_max_backup", duration_seconds))

    async def cancel_max_backup(self) -> None:
        self.calls.append(("cancel_max_backup",))

    async def dispatch_battery_power(
        self, power_watts: float, duration_seconds: int
    ) -> None:
        self.calls.append(("dispatch_battery_power", power_watts, duration_seconds))

    async def resume_battery_operation(self) -> None:
        self.calls.append(("resume_battery_operation",))

    # reads -----------------------------------------------------------------
    async def get_backup_events(self) -> dict[str, Any]:
        self.calls.append(("get_backup_events",))
        return {
            "manual_backup": {"active": True, "duration_seconds": 3600},
            "backup_events": [{"id": "abc", "name": "evt"}],
        }

    async def get_meters_aggregates(self) -> dict[str, Any]:
        return {
            "site": {"instant_power": 1500.0},
            "battery": {"instant_power": -1000.0},
            "load": {"instant_power": 500.0},
            "solar": {"instant_power": 2000.0},
            "generator": {"instant_power": 0.0},
        }

    async def get_status(self) -> dict[str, Any]:
        return {
            "control": {
                "systemStatus": {
                    "nominalEnergyRemainingWh": 52777.8,
                    "nominalFullPackEnergyWh": 100000.0,
                }
            }
        }

    async def get_grid_status(self) -> str:
        return "SystemGridConnected"

    async def get_config(self) -> dict[str, Any]:
        self.calls.append(("get_config",))
        return self.config

    async def list_authorized_clients(self) -> dict[str, Any]:
        self.calls.append(("list_authorized_clients",))
        return {
            "clients": [{"public_key": "abcd", "state": "VERIFIED"}],
            "enable_line_switch_off": False,
        }

    async def remove_authorized_client(self, public_key: bytes | str) -> None:
        self.calls.append(("remove_authorized_client", public_key))


def _adapter() -> tuple[PowerwallEnergySite, FakeClient]:
    fake = FakeClient()
    site = PowerwallEnergySite(cast(PowerwallClient, fake))
    return site, fake


_OK = {"response": {"code": 201, "message": "", "result": True}}


# ── Implemented commands ────────────────────────────────────────────────────


async def test_operation_maps_to_set_operation_mode() -> None:
    site, fake = _adapter()
    result = await site.operation("autonomous")
    assert fake.calls == [("set_operation_mode", "autonomous")]
    assert result == _OK


async def test_backup_maps_to_set_backup_reserve() -> None:
    site, fake = _adapter()
    result = await site.backup(20)
    assert fake.calls == [("set_backup_reserve", 20)]
    assert result == _OK


async def test_grid_import_export_maps_to_set_grid_import_export() -> None:
    site, fake = _adapter()
    result = await site.grid_import_export(
        disallow_charge_from_grid_with_solar_installed=True,
        customer_preferred_export_rule="battery_ok",
    )
    assert fake.calls == [
        ("set_grid_import_export", "battery_ok", True)
    ]
    assert result == _OK


async def test_grid_import_export_export_rule_only() -> None:
    site, fake = _adapter()
    result = await site.grid_import_export(customer_preferred_export_rule="never")
    assert fake.calls == [("set_grid_import_export", "never", None)]
    assert result == _OK


async def test_set_island_mode_off_grid_defaults_force_true() -> None:
    site, fake = _adapter()
    result = await site.set_island_mode(ISLAND_MODE_OFF_GRID)
    assert fake.calls == [
        ("set_island_mode", True, True, ISLAND_MODE_OFF_GRID)
    ]
    assert result == _OK


async def test_set_island_mode_on_grid_defaults_force_false() -> None:
    site, fake = _adapter()
    result = await site.set_island_mode(ISLAND_MODE_ON_GRID)
    assert fake.calls == [
        ("set_island_mode", False, False, ISLAND_MODE_ON_GRID)
    ]
    assert result == _OK


async def test_set_island_mode_explicit_force_overrides_default() -> None:
    site, fake = _adapter()
    await site.set_island_mode(ISLAND_MODE_OFF_GRID, force=False)
    assert fake.calls == [
        ("set_island_mode", True, False, ISLAND_MODE_OFF_GRID)
    ]


async def test_go_off_grid_maps_to_client() -> None:
    site, fake = _adapter()
    result = await site.go_off_grid()
    assert fake.calls == [("go_off_grid",)]
    assert result == _OK


async def test_reconnect_grid_maps_to_client() -> None:
    site, fake = _adapter()
    result = await site.reconnect_grid()
    assert fake.calls == [("reconnect_grid",)]
    assert result == _OK


async def test_schedule_backup_event_uses_duration() -> None:
    site, fake = _adapter()
    result = await site.schedule_backup_event(duration_seconds=3600)
    assert fake.calls == [("schedule_max_backup", 3600)]
    assert result == _OK


async def test_schedule_backup_event_defaults_duration() -> None:
    site, fake = _adapter()
    # start_time / priority are accepted but not honoured locally.
    await site.schedule_backup_event(start_time="2026-01-01T00:00:00Z", priority=5)
    assert fake.calls == [("schedule_max_backup", 7200)]


async def test_cancel_backup_event_maps_to_client() -> None:
    site, fake = _adapter()
    result = await site.cancel_backup_event()
    assert fake.calls == [("cancel_max_backup",)]
    assert result == _OK


async def test_dispatch_battery_power_maps_to_client() -> None:
    site, fake = _adapter()
    result = await site.dispatch_battery_power(-2500.0, 30)
    assert fake.calls == [("dispatch_battery_power", -2500.0, 30)]
    assert result == _OK


async def test_resume_battery_operation_maps_to_client() -> None:
    site, fake = _adapter()
    result = await site.resume_battery_operation()
    assert fake.calls == [("resume_battery_operation",)]
    assert result == _OK


async def test_get_backup_events_wraps_payload_under_response() -> None:
    site, fake = _adapter()
    result = await site.get_backup_events()
    assert ("get_backup_events",) in fake.calls
    assert result == {
        "response": {
            "manual_backup": {"active": True, "duration_seconds": 3600},
            "backup_events": [{"id": "abc", "name": "evt"}],
        }
    }


async def test_list_authorized_clients_wraps_payload_under_response() -> None:
    site, fake = _adapter()
    result = await site.list_authorized_clients()
    assert ("list_authorized_clients",) in fake.calls
    assert result == {
        "response": {
            "clients": [{"public_key": "abcd", "state": "VERIFIED"}],
            "enable_line_switch_off": False,
        }
    }


async def test_find_authorized_clients_returns_typed_result() -> None:
    site, fake = _adapter()
    result = await site.find_authorized_clients()
    assert ("list_authorized_clients",) in fake.calls
    assert isinstance(result, AuthorizedClients)
    assert len(result.clients) == 1
    client = result.clients[0]
    assert client.public_key == "abcd"
    assert client.state is AuthorizedClientState.VERIFIED
    assert client.raw == {"public_key": "abcd", "state": "VERIFIED"}


async def test_find_authorized_clients_unknown_state_is_not_dropped() -> None:
    site, _fake = _adapter()

    async def list_authorized_clients() -> dict[str, Any]:
        return {"clients": [{"public_key": "abcd", "state": 99}], "enable_line_switch_off": False}

    site._client.list_authorized_clients = list_authorized_clients  # type: ignore[method-assign]
    result = await site.find_authorized_clients()
    assert isinstance(result, AuthorizedClients)
    assert result.clients[0].state == 99


async def test_remove_authorized_client_delegates_and_returns_ok_envelope() -> None:
    site, fake = _adapter()
    result = await site.remove_authorized_client("abcd")
    assert ("remove_authorized_client", "abcd") in fake.calls
    assert result == {"response": {"code": 201, "message": "", "result": True}}


async def test_connect_if_needed_delegates_to_connect() -> None:
    site, fake = _adapter()
    await site.connect_if_needed()
    assert fake.calls == [("connect",)]


# ── live_status ─────────────────────────────────────────────────────────────

_LIVE_STATUS_KEYS = {
    "solar_power",
    "energy_left",
    "total_pack_energy",
    "percentage_charged",
    "backup_capable",
    "battery_power",
    "load_power",
    "grid_power",
    "grid_services_power",
    "generator_power",
    "grid_status",
    "grid_services_active",
    "island_status",
    "storm_mode_active",
    "timestamp",
    "wall_connectors",
}


async def test_live_status_shape_and_available_values() -> None:
    site, _ = _adapter()
    result = await site.live_status()
    assert set(result) == {"response"}
    payload = result["response"]
    assert set(payload) == _LIVE_STATUS_KEYS

    # Values derived from the mocked local reads.
    assert payload["solar_power"] == 2000.0
    assert payload["battery_power"] == -1000.0
    assert payload["load_power"] == 500.0
    assert payload["grid_power"] == 1500.0
    assert payload["generator_power"] == 0.0
    assert payload["percentage_charged"] == 50.2924
    assert payload["energy_left"] == 52777.8
    assert payload["total_pack_energy"] == 100000.0
    assert payload["grid_status"] == "Active"
    assert payload["island_status"] == "on_grid"

    # Documented gaps are surfaced as None, not guessed.
    for gap in (
        "backup_capable",
        "grid_services_power",
        "grid_services_active",
        "storm_mode_active",
        "timestamp",
        "wall_connectors",
    ):
        assert payload[gap] is None


async def test_live_status_missing_meter_yields_none() -> None:
    site, fake = _adapter()

    async def _empty_meters() -> dict[str, Any]:
        return {}

    fake.get_meters_aggregates = _empty_meters  # type: ignore[method-assign]
    payload = (await site.live_status())["response"]
    assert payload["solar_power"] is None
    assert payload["battery_power"] is None


async def test_live_status_missing_status_yields_none() -> None:
    site, fake = _adapter()

    async def _empty_status() -> dict[str, Any]:
        return {}

    fake.get_status = _empty_status  # type: ignore[method-assign]
    payload = (await site.live_status())["response"]
    assert payload["percentage_charged"] is None
    assert payload["energy_left"] is None
    assert payload["total_pack_energy"] is None


async def test_live_status_islanded_grid_status() -> None:
    site, fake = _adapter()

    async def _islanded() -> str:
        return "SystemIslandedActive"

    fake.get_grid_status = _islanded  # type: ignore[method-assign]
    payload = (await site.live_status())["response"]
    assert payload["grid_status"] == "Inactive"
    assert payload["island_status"] == "off_grid"


async def test_live_status_unknown_grid_status_falls_back() -> None:
    site, fake = _adapter()

    async def _weird() -> str:
        return "SomethingBrandNew"

    fake.get_grid_status = _weird  # type: ignore[method-assign]
    payload = (await site.live_status())["response"]
    assert payload["grid_status"] == "Unknown"
    assert payload["island_status"] == "island_status_unknown"


# ── local_config ─────────────────────────────────────────────────────────────


async def test_local_config_returns_both_keys_scaled() -> None:
    site, fake = _adapter()
    fake.config = {
        "site_info": {"backup_reserve_percent": 25.0},
        "default_real_mode": "self_consumption",
    }
    result = await site.local_config()
    assert result == {
        "backup_reserve_percent": raw_to_scaled_reserve(25.0),
        "default_real_mode": "self_consumption",
    }
    assert set(result) == {"backup_reserve_percent", "default_real_mode"}


async def test_local_config_omits_missing_backup_reserve_percent() -> None:
    site, fake = _adapter()
    fake.config = {
        "site_info": {},
        "default_real_mode": "self_consumption",
    }
    result = await site.local_config()
    assert result == {"default_real_mode": "self_consumption"}


async def test_local_config_omits_missing_default_real_mode() -> None:
    site, fake = _adapter()
    fake.config = {"site_info": {"backup_reserve_percent": 25.0}}
    result = await site.local_config()
    assert "default_real_mode" not in result
    assert result["backup_reserve_percent"] == raw_to_scaled_reserve(25.0)


async def test_local_config_empty_when_no_source_present() -> None:
    site, fake = _adapter()
    fake.config = {}
    result = await site.local_config()
    assert result == {}


# ── site_info is deliberately absent ─────────────────────────────────────────


def test_site_info_is_absent_on_adapter() -> None:
    site, _ = _adapter()
    assert not hasattr(site, "site_info")


# ── Placeholder commands raise NotImplementedError ───────────────────────────

_PLACEHOLDERS: list[tuple[str, tuple[Any, ...]]] = [
    ("storm_mode", (True,)),
    ("off_grid_vehicle_charging_reserve", (10,)),
    ("time_of_use_settings", ({},)),
    ("backup_history", ("day",)),
    ("charge_history", ("2026-01-01", "2026-01-31")),
    ("energy_history", ("day",)),
    ("get_system_info", ()),
    ("raw_networking_status", ()),
    ("get_networking_status", ()),
    ("wifi_scan", ()),
    ("get_device_cert", ()),
    ("get_cellular_info", ()),
    ("check_for_update", ()),
    ("check_for_update_urgency", ()),
    ("check_internet", ()),
    ("set_local_site_config", ()),
    ("get_teg_config", ()),
    ("add_authorized_client", ()),
    ("get_signed_commands_public_key", ()),
]


@pytest.mark.parametrize("name,args", _PLACEHOLDERS)
async def test_placeholder_raises_not_implemented(
    name: str, args: tuple[Any, ...]
) -> None:
    site, fake = _adapter()
    method = getattr(site, name)
    with pytest.raises(NotImplementedError):
        await method(*args)
    # Placeholders must not touch the local client.
    assert fake.calls == []
