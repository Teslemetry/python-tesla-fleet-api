"""TypedDict definitions for the JSON payloads returned by the TEDAPI.

These describe the shape of well-known fields the client uses or surfaces;
the gateway returns deeply nested objects with many more keys, so all of
these models are declared `total=False` and consumers should treat unknown
keys as opaque.
"""

from __future__ import annotations

from typing import Any, Literal, TypedDict

PowerLocation = Literal[
    "BATTERY", "SITE", "LOAD", "SOLAR", "SOLAR_RGM", "GENERATOR", "CONDUCTOR"
]
"""Meter aggregate locations as reported by `control.meterAggregates[].location`."""


class FirmwareDetails(TypedDict, total=False):
    """Detailed firmware payload returned by `get_firmware_details()`."""

    system: dict[str, Any]


class BackupEvent(TypedDict, total=False):
    id: str
    name: str
    start_time: int
    duration_seconds: int
    priority: int


class ManualBackupInfo(TypedDict, total=False):
    start_time: int
    duration_seconds: int
    end_time: int
    active: bool
    priority: int


class BatteryCalibrationDelayStatus(TypedDict, total=False):
    """Result of :meth:`PowerwallClient.get_battery_calibration_delay_status`."""

    calibration_delays_left: int
    calibration_delay_remaining_seconds: int
    max_calibration_delays: int


class ControllableDeviceProgram(TypedDict):
    """One load program from :meth:`PowerwallClient.get_controllable_device_programs`.

    ``priority`` and ``contactor_state`` are the enum name with its prefix
    stripped (e.g. ``"CUSTOMER_DEFAULT"``, ``"OPEN"``), or the raw int for a
    value this package does not recognize. Schedule times are epoch seconds,
    or ``None`` when unset.
    """

    key: dict[str, Any]
    settings: dict[str, Any]
    schedule: dict[str, int | None]


class ControllableDeviceProgramsPayload(TypedDict):
    """Result of :meth:`PowerwallClient.get_controllable_device_programs`."""

    active_programs: list[ControllableDeviceProgram]
    inactive_programs: list[ControllableDeviceProgram]


class BackupEventsPayload(TypedDict, total=False):
    """Result of :meth:`PowerwallClient.get_backup_events`."""

    manual_backup: ManualBackupInfo | None
    backup_events: list[BackupEvent]


class AuthorizedClient(TypedDict, total=False):
    """One registered client entry from `list_authorized_clients()`.

    This is the raw form: enum fields are the gateway's enum name with its
    common prefix stripped (e.g. ``"VERIFIED"``), falling back to the raw
    int for a value newer than this package's `tesla-protocol` pin knows
    the name of. See
    :meth:`~tesla_fleet_api.tesla.powerwall.energysite.PowerwallEnergySite.find_authorized_clients`
    for a typed, tesla-fleet-api-aligned alternative.
    """

    public_key: str
    state: str | int
    type: str | int
    description: str
    key_type: str | int
    roles: list[str | int]
    verification: str | int
    added_time: int | None
    identifier: str | None
    authorized_by_public_key: str | None


class AuthorizedClientsPayload(TypedDict, total=False):
    """Result of :meth:`PowerwallClient.list_authorized_clients`."""

    clients: list[AuthorizedClient]
    enable_line_switch_off: bool


# The Powerwall returns deeply nested config/status/components/controller
# payloads. These aliases give callers a stable named type without forcing
# us to enumerate every signal — for static analysis they behave like
# `dict[str, Any]` but are easier to grep for at call sites.

ConfigPayload = dict[str, Any]
StatusPayload = dict[str, Any]
ControllerPayload = dict[str, Any]
ComponentsPayload = dict[str, Any]

__all__ = [
    "AuthorizedClient",
    "AuthorizedClientsPayload",
    "BackupEvent",
    "BackupEventsPayload",
    "ComponentsPayload",
    "ConfigPayload",
    "ControllableDeviceProgram",
    "ControllableDeviceProgramsPayload",
    "ControllerPayload",
    "FirmwareDetails",
    "ManualBackupInfo",
    "PowerLocation",
    "StatusPayload",
]
