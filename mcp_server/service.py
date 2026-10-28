"""Allowlisted SDK facade. No raw HTTP, arbitrary method names, or retries."""

import asyncio
from typing import Any, cast

from mcp_server.auth import ManagedOAuth
from mcp_server.commands import CommandJournal
from mcp_server.config import Config, VIN_PATTERN, WRITE_TOOLS
from tesla_fleet_api.exceptions import TeslaFleetError
from tesla_fleet_api.tesla.vehicle.fleet import VehicleFleet


class ToolFailure(Exception):
    """A safe message that may be exposed to a model/client."""


class TeslaService:
    def __init__(self, api: ManagedOAuth, config: Config, journal: CommandJournal):
        self.api = api
        self.config = config
        self.journal = journal
        self._vehicles: dict[str, VehicleFleet[Any]] = {}
        self._command_lock = asyncio.Lock()

    def authorize(self, tool: str, vin: str | None = None) -> None:
        if tool not in self.config.tools:
            raise ToolFailure("Tool permission is disabled")
        if vin is not None and (
            not VIN_PATTERN.fullmatch(vin) or vin not in self.config.vins
        ):
            raise ToolFailure("Vehicle is not allowed")
        if tool in WRITE_TOOLS and not self.config.enable_commands:
            raise ToolFailure("Vehicle commands are disabled")
        if tool == "navigate_waypoints" and not self.config.enable_waypoints:
            raise ToolFailure("Experimental waypoint navigation is disabled")

    def vehicle(self, vin: str) -> VehicleFleet[Any]:
        if vin not in self._vehicles:
            # No BLE/router fallback; a cloud command must never replay on another transport.
            self._vehicles[vin] = self.api.vehicles.createFleet(vin)
        return self._vehicles[vin]

    async def read(
        self, tool: str, vin: str | None = None, page: int = 1
    ) -> dict[str, Any]:
        self.authorize(tool, vin)
        try:
            if tool == "list_vehicles":
                if not 1 <= page <= 10000:
                    raise ToolFailure("Page is out of range")
                # SDK list is account-wide; use an allowed VIN to access its existing list method.
                result = await self.vehicle(sorted(self.config.vins)[0]).list(
                    page=page, per_page=100
                )
                rows = result.get("response")
                if not isinstance(rows, list):
                    raise ToolFailure("Unexpected vehicle-list response")
                rows = cast(list[Any], rows)
                return {
                    "response": [
                        {
                            k: row[k]
                            for k in ("vin", "display_name", "state")
                            if k in row
                        }
                        for row in rows
                        if isinstance(row, dict)
                        and cast(dict[str, Any], row).get("vin") in self.config.vins
                    ],
                    "page": page,
                    "next_page": page + 1 if len(rows) == 100 else None,
                }
            if vin is None:
                raise ToolFailure("VIN is required")
            endpoints = (
                ["location_data"]
                if tool == "get_location"
                else ["charge_state", "climate_state", "vehicle_state"]
            )
            result = await self.vehicle(vin).vehicle_data(endpoints=endpoints)
            body = result.get("response")
            if not isinstance(body, dict):
                raise ToolFailure("Unexpected vehicle-data response")
            body = cast(dict[str, Any], body)
            if tool == "get_location":
                # Tesla returns location fields within drive_state for location_data requests.
                drive = body.get("drive_state")
                if not isinstance(drive, dict):
                    raise ToolFailure(
                        "Location is unavailable; check sharing and vehicle_location scope"
                    )
                drive = cast(dict[str, Any], drive)
                if not any(
                    drive.get(lat) is not None and drive.get(lon) is not None
                    for lat, lon in (
                        ("latitude", "longitude"),
                        ("native_latitude", "native_longitude"),
                    )
                ):
                    raise ToolFailure(
                        "Location is unavailable; check sharing and vehicle_location scope"
                    )
                return {
                    "response": {
                        k: drive[k]
                        for k in (
                            "latitude",
                            "longitude",
                            "heading",
                            "timestamp",
                            "native_latitude",
                            "native_longitude",
                            "native_type",
                        )
                        if k in drive
                    },
                    "may_be_cached": True,
                }
            # Positive projection keeps location, saved addresses and route data out of state reads.
            fields = {
                "charge_state": (
                    "battery_level",
                    "charging_state",
                    "battery_range",
                    "timestamp",
                ),
                "climate_state": (
                    "inside_temp",
                    "outside_temp",
                    "is_climate_on",
                    "timestamp",
                ),
                "vehicle_state": ("locked", "odometer", "car_version", "timestamp"),
            }
            return {
                "response": {
                    section: {k: body[section][k] for k in keys if k in body[section]}
                    for section, keys in fields.items()
                    if isinstance(body.get(section), dict)
                },
                "may_be_cached": True,
            }
        except (TeslaFleetError, Exception) as error:
            if isinstance(error, ToolFailure):
                raise
            raise ToolFailure(
                "Tesla read failed; check credentials, scopes, rate limits and vehicle availability"
            ) from None

    async def command(
        self, tool: str, vin: str, request_id: str, value: str = ""
    ) -> dict[str, Any]:
        self.authorize(tool, vin)
        if tool not in WRITE_TOOLS:
            raise ToolFailure("Unknown command")
        if tool != "wake_vehicle" and (
            not value.strip() or len(value.encode()) > 16384
        ):
            raise ToolFailure("Navigation payload must be nonempty and at most 16 KiB")
        payload = {
            "tool": tool,
            "vin": vin,
            "value": value,
            "region": self.config.region,
            "client_id": self.config.client_id,
        }
        # Serialize commands, including signed-session construction. No automatic wake or retry.
        async with self._command_lock:
            try:
                decision = self.journal.prepare_or_reserve(request_id, payload)
            except ValueError as error:
                raise ToolFailure(str(error)) from None
            if decision["status"] != "execute":
                return decision
            try:
                vehicle = self.vehicle(vin)
                if tool == "wake_vehicle":
                    response = await vehicle.wake_up(wait=False)
                    status = (
                        "accepted"
                        if isinstance(response.get("response"), dict)
                        else "unknown"
                    )
                else:
                    if self.config.private_key is None:
                        raise ToolFailure(
                            "A registered command signing key is required"
                        )
                    # Signing is entirely delegated to the existing SDK.
                    if self.api.private_key is None:
                        await self.api.get_private_key(str(self.config.private_key))
                    signed = self.api.vehicles.createSigned(vin)
                    response = (
                        await signed.navigation_request(value)
                        if tool == "navigate_to"
                        else await signed.navigation_waypoints_request(value)
                    )
                    body = response.get("response", response)
                    status = (
                        "accepted"
                        if isinstance(body, dict)
                        and cast(dict[str, Any], body).get("result") is True
                        else "unknown"
                    )
                    if (
                        isinstance(body, dict)
                        and cast(dict[str, Any], body).get("result") is False
                    ):
                        status = "rejected"
                return self.journal.finish(request_id, status)
            except (TeslaFleetError, Exception):
                # Do not expose Tesla exception bodies, tokens, coordinates, or URLs.
                return self.journal.finish(request_id, "unknown")
            # Cancellation/termination leaves durable reserved -> unknown on the next call.
