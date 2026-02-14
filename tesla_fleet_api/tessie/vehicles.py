from __future__ import annotations
from typing import Any

from tesla_fleet_api.const import Method
from tesla_fleet_api.tesla.vehicle.vehicles import Vehicles
from tesla_fleet_api.tesla.vehicle.fleet import VehicleFleet


class TessieVehicle(VehicleFleet):
    """Tessie specific API vehicle."""

    async def wake(self, wait_for_completion: bool = True) -> dict[str, Any]:
        """Wake vehicle from sleep mode."""
        return await self._request(
            Method.POST,
            f"{self.vin}/wake",
            params={"wait_for_completion": wait_for_completion},
        )

    async def lock(self, wait_for_completion: bool = True) -> dict[str, Any]:
        """Lock vehicle doors."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/lock",
            params={"wait_for_completion": wait_for_completion},
        )

    async def unlock(self, wait_for_completion: bool = True) -> dict[str, Any]:
        """Unlock vehicle doors."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/unlock",
            params={"wait_for_completion": wait_for_completion},
        )

    async def activate_front_trunk(
        self, wait_for_completion: bool = True
    ) -> dict[str, Any]:
        """Open front trunk."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/activate_front_trunk",
            params={"wait_for_completion": wait_for_completion},
        )

    async def activate_rear_trunk(
        self, wait_for_completion: bool = True
    ) -> dict[str, Any]:
        """Open or close rear trunk."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/activate_rear_trunk",
            params={"wait_for_completion": wait_for_completion},
        )

    async def open_tonneau(self, wait_for_completion: bool = True) -> dict[str, Any]:
        """Open truck tonneau cover."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/open_tonneau",
            params={"wait_for_completion": wait_for_completion},
        )

    async def close_tonneau(self, wait_for_completion: bool = True) -> dict[str, Any]:
        """Close truck tonneau cover."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/close_tonneau",
            params={"wait_for_completion": wait_for_completion},
        )

    async def vent_windows(self, wait_for_completion: bool = True) -> dict[str, Any]:
        """Open all windows."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/vent_windows",
            params={"wait_for_completion": wait_for_completion},
        )

    async def close_windows(self, wait_for_completion: bool = True) -> dict[str, Any]:
        """Close all windows."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/close_windows",
            params={"wait_for_completion": wait_for_completion},
        )

    async def start_climate(
        self, wait_for_completion: bool = True
    ) -> dict[str, Any]:
        """Activate climate system."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/start_climate",
            params={"wait_for_completion": wait_for_completion},
        )

    async def stop_climate(self, wait_for_completion: bool = True) -> dict[str, Any]:
        """Deactivate climate system."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/stop_climate",
            params={"wait_for_completion": wait_for_completion},
        )

    async def set_temperatures(
        self,
        temperature: float,
        wait_for_completion: bool = True,
    ) -> dict[str, Any]:
        """Set cabin temperature."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/set_temperatures",
            params={"temperature": temperature, "wait_for_completion": wait_for_completion},
        )

    async def set_seat_heat(
        self,
        seat: str,
        level: int,
        wait_for_completion: bool = True,
    ) -> dict[str, Any]:
        """Adjust seat heating level."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/set_seat_heat",
            params={"seat": seat, "level": level, "wait_for_completion": wait_for_completion},
        )

    async def set_seat_cool(
        self,
        seat: str,
        level: int,
        wait_for_completion: bool = True,
    ) -> dict[str, Any]:
        """Adjust seat cooling level."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/set_seat_cool",
            params={"seat": seat, "level": level, "wait_for_completion": wait_for_completion},
        )

    async def start_max_defrost(
        self, wait_for_completion: bool = True
    ) -> dict[str, Any]:
        """Begin defrosting."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/start_max_defrost",
            params={"wait_for_completion": wait_for_completion},
        )

    async def stop_max_defrost(
        self, wait_for_completion: bool = True
    ) -> dict[str, Any]:
        """End defrosting."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/stop_max_defrost",
            params={"wait_for_completion": wait_for_completion},
        )

    async def start_steering_wheel_heater(
        self, wait_for_completion: bool = True
    ) -> dict[str, Any]:
        """Enable heated steering wheel."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/start_steering_wheel_heater",
            params={"wait_for_completion": wait_for_completion},
        )

    async def stop_steering_wheel_heater(
        self, wait_for_completion: bool = True
    ) -> dict[str, Any]:
        """Disable heated steering wheel."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/stop_steering_wheel_heater",
            params={"wait_for_completion": wait_for_completion},
        )

    async def tessie_set_cabin_overheat_protection(
        self,
        mode: str,
        wait_for_completion: bool = True,
    ) -> dict[str, Any]:
        """Configure overheat protection (Tessie API)."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/set_cabin_overheat_protection",
            params={"mode": mode, "wait_for_completion": wait_for_completion},
        )

    async def tessie_set_cop_temp(
        self,
        temperature: str,
        wait_for_completion: bool = True,
    ) -> dict[str, Any]:
        """Set overheat protection temperature (Tessie API)."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/set_cop_temp",
            params={"temperature": temperature, "wait_for_completion": wait_for_completion},
        )

    async def tessie_set_bioweapon_mode(
        self,
        enable: bool,
        wait_for_completion: bool = True,
    ) -> dict[str, Any]:
        """Enable/disable defense mode (Tessie API)."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/set_bioweapon_mode",
            params={"enable": enable, "wait_for_completion": wait_for_completion},
        )

    async def tessie_set_climate_keeper_mode(
        self,
        mode: int,
        wait_for_completion: bool = True,
    ) -> dict[str, Any]:
        """Configure climate keeper (Tessie API)."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/set_climate_keeper_mode",
            params={"mode": mode, "wait_for_completion": wait_for_completion},
        )

    async def start_charging(
        self, wait_for_completion: bool = True
    ) -> dict[str, Any]:
        """Begin charging session."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/start_charging",
            params={"wait_for_completion": wait_for_completion},
        )

    async def stop_charging(self, wait_for_completion: bool = True) -> dict[str, Any]:
        """End charging session."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/stop_charging",
            params={"wait_for_completion": wait_for_completion},
        )

    async def set_charge_limit(
        self,
        percent: int,
        wait_for_completion: bool = True,
    ) -> dict[str, Any]:
        """Set target charge percentage."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/set_charge_limit",
            params={"percent": percent, "wait_for_completion": wait_for_completion},
        )

    async def tessie_set_charging_amps(
        self,
        amps: int,
        wait_for_completion: bool = True,
    ) -> dict[str, Any]:
        """Adjust charging amperage (Tessie API)."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/set_charging_amps",
            params={"amps": amps, "wait_for_completion": wait_for_completion},
        )

    async def open_charge_port(
        self, wait_for_completion: bool = True
    ) -> dict[str, Any]:
        """Open or unlock charge port."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/open_charge_port",
            params={"wait_for_completion": wait_for_completion},
        )

    async def close_charge_port(
        self, wait_for_completion: bool = True
    ) -> dict[str, Any]:
        """Close charge port."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/close_charge_port",
            params={"wait_for_completion": wait_for_completion},
        )

    async def flash(self, wait_for_completion: bool = True) -> dict[str, Any]:
        """Flash vehicle lights."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/flash",
            params={"wait_for_completion": wait_for_completion},
        )

    async def honk(self, wait_for_completion: bool = True) -> dict[str, Any]:
        """Sound vehicle horn."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/honk",
            params={"wait_for_completion": wait_for_completion},
        )

    async def tessie_trigger_homelink(
        self, wait_for_completion: bool = True
    ) -> dict[str, Any]:
        """Activate HomeLink device (Tessie API)."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/trigger_homelink",
            params={"wait_for_completion": wait_for_completion},
        )

    async def remote_start(self, wait_for_completion: bool = True) -> dict[str, Any]:
        """Enable keyless driving."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/remote_start",
            params={"wait_for_completion": wait_for_completion},
        )

    async def vent_sunroof(self, wait_for_completion: bool = True) -> dict[str, Any]:
        """Open sunroof."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/vent_sunroof",
            params={"wait_for_completion": wait_for_completion},
        )

    async def close_sunroof(self, wait_for_completion: bool = True) -> dict[str, Any]:
        """Close sunroof."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/close_sunroof",
            params={"wait_for_completion": wait_for_completion},
        )

    async def enable_sentry(self, wait_for_completion: bool = True) -> dict[str, Any]:
        """Activate Sentry Mode."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/enable_sentry",
            params={"wait_for_completion": wait_for_completion},
        )

    async def disable_sentry(self, wait_for_completion: bool = True) -> dict[str, Any]:
        """Deactivate Sentry Mode."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/disable_sentry",
            params={"wait_for_completion": wait_for_completion},
        )

    async def enable_valet(
        self,
        pin: str | int,
        wait_for_completion: bool = True,
    ) -> dict[str, Any]:
        """Activate Valet Mode."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/enable_valet",
            params={"pin": str(pin), "wait_for_completion": wait_for_completion},
        )

    async def disable_valet(
        self,
        pin: str | int,
        wait_for_completion: bool = True,
    ) -> dict[str, Any]:
        """Deactivate Valet Mode."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/disable_valet",
            params={"pin": str(pin), "wait_for_completion": wait_for_completion},
        )

    async def tessie_schedule_software_update(
        self,
        offset_seconds: int,
        wait_for_completion: bool = True,
    ) -> dict[str, Any]:
        """Schedule update installation (Tessie API)."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/schedule_software_update",
            params={"offset_seconds": offset_seconds, "wait_for_completion": wait_for_completion},
        )

    async def cancel_software_update(
        self, wait_for_completion: bool = True
    ) -> dict[str, Any]:
        """Cancel pending update."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/cancel_software_update",
            params={"wait_for_completion": wait_for_completion},
        )

    async def set_scheduled_charging(
        self,
        enable: bool,
        time: int,
        wait_for_completion: bool = True,
    ) -> dict[str, Any]:
        """Configure scheduled charging."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/set_scheduled_charging",
            params={"enable": enable, "time": time, "wait_for_completion": wait_for_completion},
        )

    async def tessie_set_scheduled_departure(
        self,
        enable: bool,
        departure_time: int,
        preconditioning_enabled: bool = False,
        preconditioning_weekdays_only: bool = False,
        off_peak_charging_enabled: bool = False,
        off_peak_charging_weekdays_only: bool = False,
        end_off_peak_time: int | None = None,
        wait_for_completion: bool = True,
    ) -> dict[str, Any]:
        """Configure scheduled departure (Tessie API)."""
        params: dict[str, Any] = {
            "enable": enable,
            "departure_time": departure_time,
            "preconditioning_enabled": preconditioning_enabled,
            "preconditioning_weekdays_only": preconditioning_weekdays_only,
            "off_peak_charging_enabled": off_peak_charging_enabled,
            "off_peak_charging_weekdays_only": off_peak_charging_weekdays_only,
            "wait_for_completion": wait_for_completion,
        }
        if end_off_peak_time is not None:
            params["end_off_peak_time"] = end_off_peak_time
        return await self._request(
            Method.POST,
            f"{self.vin}/command/set_scheduled_departure",
            params=params,
        )

    async def tessie_add_charge_schedule(
        self,
        id: int,
        enabled: bool,
        days_of_week: str,
        start_time: int,
        end_time: int,
        lat: float,
        lon: float,
        wait_for_completion: bool = True,
    ) -> dict[str, Any]:
        """Add new charging schedule (Tessie API)."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/add_charge_schedule",
            params={
                "id": id,
                "enabled": enabled,
                "days_of_week": days_of_week,
                "start_time": start_time,
                "end_time": end_time,
                "lat": lat,
                "lon": lon,
                "wait_for_completion": wait_for_completion,
            },
        )

    async def remove_charge_schedule(
        self,
        id: int,
        wait_for_completion: bool = True,
    ) -> dict[str, Any]:
        """Delete charging schedule."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/remove_charge_schedule",
            params={"id": id, "wait_for_completion": wait_for_completion},
        )

    async def tessie_add_precondition_schedule(
        self,
        id: int,
        enabled: bool,
        days_of_week: str,
        precondition_time: int,
        lat: float,
        lon: float,
        wait_for_completion: bool = True,
    ) -> dict[str, Any]:
        """Add preconditioning schedule (Tessie API)."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/add_precondition_schedule",
            params={
                "id": id,
                "enabled": enabled,
                "days_of_week": days_of_week,
                "precondition_time": precondition_time,
                "lat": lat,
                "lon": lon,
                "wait_for_completion": wait_for_completion,
            },
        )

    async def remove_precondition_schedule(
        self,
        id: int,
        wait_for_completion: bool = True,
    ) -> dict[str, Any]:
        """Delete preconditioning schedule."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/remove_precondition_schedule",
            params={"id": id, "wait_for_completion": wait_for_completion},
        )

    async def share(
        self,
        value: str,
        locale: str = "en-US",
        wait_for_completion: bool = True,
    ) -> dict[str, Any]:
        """Share address/location to vehicle."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/share",
            params={"value": value, "locale": locale, "wait_for_completion": wait_for_completion},
        )

    async def remote_boombox(
        self,
        sound: int,
        wait_for_completion: bool = True,
    ) -> dict[str, Any]:
        """Trigger novelty sound effect."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/remote_boombox",
            params={"sound": sound, "wait_for_completion": wait_for_completion},
        )

    async def set_speed_limit(
        self,
        limit_mph: int,
        wait_for_completion: bool = True,
    ) -> dict[str, Any]:
        """Set speed limit."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/set_speed_limit",
            params={"limit_mph": limit_mph, "wait_for_completion": wait_for_completion},
        )

    async def enable_speed_limit(
        self,
        pin: str | int,
        wait_for_completion: bool = True,
    ) -> dict[str, Any]:
        """Activate speed limit."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/enable_speed_limit",
            params={"pin": str(pin), "wait_for_completion": wait_for_completion},
        )

    async def disable_speed_limit(
        self,
        pin: str | int,
        wait_for_completion: bool = True,
    ) -> dict[str, Any]:
        """Deactivate speed limit."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/disable_speed_limit",
            params={"pin": str(pin), "wait_for_completion": wait_for_completion},
        )

    async def clear_speed_limit_pin(
        self,
        pin: str | int,
        wait_for_completion: bool = True,
    ) -> dict[str, Any]:
        """Remove speed limit PIN."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/clear_speed_limit_pin",
            params={"pin": str(pin), "wait_for_completion": wait_for_completion},
        )

    async def enable_guest(self, wait_for_completion: bool = True) -> dict[str, Any]:
        """Activate guest mode."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/enable_guest",
            params={"wait_for_completion": wait_for_completion},
        )

    async def disable_guest(self, wait_for_completion: bool = True) -> dict[str, Any]:
        """Deactivate guest mode."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/disable_guest",
            params={"wait_for_completion": wait_for_completion},
        )

    async def enable_keep_accessory_power_mode(
        self, wait_for_completion: bool = True
    ) -> dict[str, Any]:
        """Enable Keep Accessory Power Mode."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/enable_keep_accessory_power_mode",
            params={"wait_for_completion": wait_for_completion},
        )

    async def disable_keep_accessory_power_mode(
        self, wait_for_completion: bool = True
    ) -> dict[str, Any]:
        """Disable Keep Accessory Power Mode."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/disable_keep_accessory_power_mode",
            params={"wait_for_completion": wait_for_completion},
        )

    async def enable_low_power_mode(
        self, wait_for_completion: bool = True
    ) -> dict[str, Any]:
        """Enable Low Power Mode."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/enable_low_power_mode",
            params={"wait_for_completion": wait_for_completion},
        )

    async def disable_low_power_mode(
        self, wait_for_completion: bool = True
    ) -> dict[str, Any]:
        """Disable Low Power Mode."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/disable_low_power_mode",
            params={"wait_for_completion": wait_for_completion},
        )

    # Driver Management
    async def drivers(self) -> dict[str, Any]:
        """List additional authorized drivers."""
        return await self._request(Method.GET, f"{self.vin}/drivers")

    async def delete_driver(self, id: str | int) -> dict[str, Any]:
        """Remove driver access."""
        return await self._request(
            Method.POST,
            f"{self.vin}/drivers/{id}/delete",
        )

    async def invitations(self) -> dict[str, Any]:
        """List pending driver invitations."""
        return await self._request(Method.GET, f"{self.vin}/invitations")

    async def create_invitation(
        self,
        email: str,
        role: str = "driver",
    ) -> dict[str, Any]:
        """Create new driver invitation."""
        return await self._request(
            Method.POST,
            f"{self.vin}/invitations",
            params={"email": email, "role": role},
        )

    async def revoke_invitation(self, id: str | int) -> dict[str, Any]:
        """Cancel driver invitation."""
        return await self._request(
            Method.POST,
            f"{self.vin}/invitations/{id}/revoke",
        )

    # Fleet Telemetry
    async def get_fleet_telemetry_config(self) -> dict[str, Any]:
        """Retrieve telemetry configuration."""
        return await self._request(Method.GET, f"{self.vin}/fleet_telemetry_config")

    async def set_fleet_telemetry_config(
        self, config: dict[str, Any]
    ) -> dict[str, Any]:
        """Set telemetry configuration."""
        return await self._request(
            Method.POST,
            f"{self.vin}/fleet_telemetry_config",
            json=config,
        )

    async def delete_fleet_telemetry_config(self) -> dict[str, Any]:
        """Remove telemetry configuration."""
        return await self._request(
            Method.DELETE,
            f"{self.vin}/fleet_telemetry_config",
        )

    # Data Management
    async def set_drive_tag(
        self,
        start: int,
        end: int,
        tag: str,
    ) -> dict[str, Any]:
        """Assign tag to drives."""
        return await self._request(
            Method.POST,
            f"{self.vin}/drives/set_tag",
            params={"from": start, "to": end, "tag": tag},
        )

    async def set_charge_cost(
        self,
        charge_id: int,
        cost: float,
        currency: str = "USD",
    ) -> dict[str, Any]:
        """Record charging cost."""
        return await self._request(
            Method.POST,
            f"{self.vin}/charges/{charge_id}/set_cost",
            params={"cost": cost, "currency": currency},
        )

    # Vehicle Information
    async def tire_pressure(self) -> dict[str, Any]:
        """Get current tire pressure readings."""
        return await self._request(Method.GET, f"{self.vin}/tire_pressure")

    async def vehicle_status(self) -> dict[str, Any]:
        """Get vehicle operational status."""
        return await self._request(Method.GET, f"{self.vin}/status")

    async def plate(self) -> dict[str, Any]:
        """Get license plate information."""
        return await self._request(Method.GET, f"{self.vin}/plate")

    async def update_plate(
        self,
        plate: str,
        state: str | None = None,
    ) -> dict[str, Any]:
        """Update license plate information."""
        params: dict[str, str] = {"plate": plate}
        if state:
            params["state"] = state
        return await self._request(Method.POST, f"{self.vin}/plate", params=params)

class TessieVehicles(Vehicles):
    """Class containing and creating vehicles."""

    Vehicle = TessieVehicle

    def create(self, vin: str) -> TessieVehicle:
        """Creates a specific vehicle."""
        vehicle = self.Vehicle(self._parent, vin)
        self[vin] = vehicle
        return vehicle

    def createFleet(self, vin: str) -> Any:
        """Creates a specific vehicle."""
        raise NotImplementedError("Tessie cannot use Fleet API directly")

    def createSigned(self, vin: str) -> Any:
        """Creates a specific vehicle."""
        raise NotImplementedError("Tessie cannot use Fleet API directly")

    def createBluetooth(self, vin: str) -> Any:
        """Creates a specific vehicle."""
        raise NotImplementedError("Tessie cannot use local Bluetooth")
