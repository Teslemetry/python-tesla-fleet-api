from __future__ import annotations
from typing import TYPE_CHECKING, Any

from tesla_fleet_api.const import BluetoothConfirmation, Method
from tesla_fleet_api.tesla.vehicle.vehicles import Vehicles
from tesla_fleet_api.tesla.vehicle.fleet import VehicleFleet

if TYPE_CHECKING:
    from tesla_fleet_api.tessie.tessie import Tessie


class TessieVehicle(VehicleFleet["Tessie"]):
    """Tessie specific API vehicle."""

    parent: Tessie

    def _command_params(
        self,
        wait_for_completion: bool | None = None,
        max_attempts: int | None = None,
        **params: Any,
    ) -> dict[str, Any]:
        data: dict[str, Any] = {
            "wait_for_completion": self.parent.wait_for_completion
            if wait_for_completion is None
            else wait_for_completion,
            **params,
        }
        resolved_max_attempts = (
            self.parent.max_attempts if max_attempts is None else max_attempts
        )
        data["max_attempts"] = resolved_max_attempts
        return data

    async def wake(self, wait_for_completion: bool | None = None) -> dict[str, Any]:
        """Wake vehicle from sleep mode."""
        _ = wait_for_completion
        return await self._request(
            Method.POST,
            f"{self.vin}/wake",
        )

    async def lock(
        self, wait_for_completion: bool | None = None, max_attempts: int | None = None
    ) -> dict[str, Any]:
        """Lock vehicle doors."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/lock",
            params=self._command_params(wait_for_completion, max_attempts),
        )

    async def unlock(
        self, wait_for_completion: bool | None = None, max_attempts: int | None = None
    ) -> dict[str, Any]:
        """Unlock vehicle doors."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/unlock",
            params=self._command_params(wait_for_completion, max_attempts),
        )

    async def activate_front_trunk(
        self, wait_for_completion: bool | None = None, max_attempts: int | None = None
    ) -> dict[str, Any]:
        """Open front trunk."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/activate_front_trunk",
            params=self._command_params(wait_for_completion, max_attempts),
        )

    async def activate_rear_trunk(
        self, wait_for_completion: bool | None = None, max_attempts: int | None = None
    ) -> dict[str, Any]:
        """Open or close rear trunk."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/activate_rear_trunk",
            params=self._command_params(wait_for_completion, max_attempts),
        )

    async def open_tonneau(
        self, wait_for_completion: bool | None = None, max_attempts: int | None = None
    ) -> dict[str, Any]:
        """Open truck tonneau cover."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/open_tonneau",
            params=self._command_params(wait_for_completion, max_attempts),
        )

    async def close_tonneau(
        self, wait_for_completion: bool | None = None, max_attempts: int | None = None
    ) -> dict[str, Any]:
        """Close truck tonneau cover."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/close_tonneau",
            params=self._command_params(wait_for_completion, max_attempts),
        )

    async def vent_windows(
        self, wait_for_completion: bool | None = None, max_attempts: int | None = None
    ) -> dict[str, Any]:
        """Open all windows."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/vent_windows",
            params=self._command_params(wait_for_completion, max_attempts),
        )

    async def close_windows(
        self, wait_for_completion: bool | None = None, max_attempts: int | None = None
    ) -> dict[str, Any]:
        """Close all windows."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/close_windows",
            params=self._command_params(wait_for_completion, max_attempts),
        )

    async def start_climate(
        self, wait_for_completion: bool | None = None, max_attempts: int | None = None
    ) -> dict[str, Any]:
        """Activate climate system."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/start_climate",
            params=self._command_params(wait_for_completion, max_attempts),
        )

    async def stop_climate(
        self, wait_for_completion: bool | None = None, max_attempts: int | None = None
    ) -> dict[str, Any]:
        """Deactivate climate system."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/stop_climate",
            params=self._command_params(wait_for_completion, max_attempts),
        )

    async def set_temperatures(
        self,
        temperature: float,
        wait_for_completion: bool | None = None,
        max_attempts: int | None = None,
    ) -> dict[str, Any]:
        """Set cabin temperature."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/set_temperatures",
            params=self._command_params(
                wait_for_completion, max_attempts, temperature=temperature
            ),
        )

    async def set_seat_heat(
        self,
        seat: str,
        level: int,
        wait_for_completion: bool | None = None,
        max_attempts: int | None = None,
    ) -> dict[str, Any]:
        """Adjust seat heating level."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/set_seat_heat",
            params=self._command_params(
                wait_for_completion, max_attempts, seat=seat, level=level
            ),
        )

    async def set_seat_cool(
        self,
        seat: str,
        level: int,
        wait_for_completion: bool | None = None,
        max_attempts: int | None = None,
    ) -> dict[str, Any]:
        """Adjust seat cooling level."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/set_seat_cool",
            params=self._command_params(
                wait_for_completion, max_attempts, seat=seat, level=level
            ),
        )

    async def start_max_defrost(
        self, wait_for_completion: bool | None = None, max_attempts: int | None = None
    ) -> dict[str, Any]:
        """Begin defrosting."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/start_max_defrost",
            params=self._command_params(wait_for_completion, max_attempts),
        )

    async def stop_max_defrost(
        self, wait_for_completion: bool | None = None, max_attempts: int | None = None
    ) -> dict[str, Any]:
        """End defrosting."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/stop_max_defrost",
            params=self._command_params(wait_for_completion, max_attempts),
        )

    async def start_steering_wheel_heater(
        self, wait_for_completion: bool | None = None, max_attempts: int | None = None
    ) -> dict[str, Any]:
        """Enable heated steering wheel."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/start_steering_wheel_heater",
            params=self._command_params(wait_for_completion, max_attempts),
        )

    async def stop_steering_wheel_heater(
        self, wait_for_completion: bool | None = None, max_attempts: int | None = None
    ) -> dict[str, Any]:
        """Disable heated steering wheel."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/stop_steering_wheel_heater",
            params=self._command_params(wait_for_completion, max_attempts),
        )

    async def tessie_set_cabin_overheat_protection(
        self,
        on: bool,
        fan_only: bool = False,
        max_attempts: int | None = None,
        wait_for_completion: bool | None = None,
    ) -> dict[str, Any]:
        """Configure overheat protection (Tessie API)."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/set_cabin_overheat_protection",
            params=self._command_params(
                wait_for_completion, max_attempts, on=on, fan_only=fan_only
            ),
        )

    async def tessie_set_cop_temp(
        self,
        cop_temp: int,
        max_attempts: int | None = None,
        wait_for_completion: bool | None = None,
    ) -> dict[str, Any]:
        """Set overheat protection temperature (Tessie API)."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/set_cop_temp",
            params=self._command_params(
                wait_for_completion, max_attempts, cop_temp=cop_temp
            ),
        )

    async def tessie_set_bioweapon_mode(
        self,
        on: bool,
        max_attempts: int | None = None,
        wait_for_completion: bool | None = None,
    ) -> dict[str, Any]:
        """Enable/disable defense mode (Tessie API)."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/set_bioweapon_mode",
            params=self._command_params(wait_for_completion, max_attempts, on=on),
        )

    async def tessie_set_climate_keeper_mode(
        self,
        mode: int,
        max_attempts: int | None = None,
        wait_for_completion: bool | None = None,
    ) -> dict[str, Any]:
        """Configure climate keeper (Tessie API)."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/set_climate_keeper_mode",
            params=self._command_params(wait_for_completion, max_attempts, mode=mode),
        )

    async def start_charging(
        self, wait_for_completion: bool | None = None, max_attempts: int | None = None
    ) -> dict[str, Any]:
        """Begin charging session."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/start_charging",
            params=self._command_params(wait_for_completion, max_attempts),
        )

    async def stop_charging(
        self, wait_for_completion: bool | None = None, max_attempts: int | None = None
    ) -> dict[str, Any]:
        """End charging session."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/stop_charging",
            params=self._command_params(wait_for_completion, max_attempts),
        )

    async def set_charge_limit(
        self,
        percent: int,
        wait_for_completion: bool | None = None,
        max_attempts: int | None = None,
    ) -> dict[str, Any]:
        """Set target charge percentage."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/set_charge_limit",
            params=self._command_params(
                wait_for_completion, max_attempts, percent=percent
            ),
        )

    async def tessie_set_charging_amps(
        self,
        amps: int,
        max_attempts: int | None = None,
        wait_for_completion: bool | None = None,
    ) -> dict[str, Any]:
        """Adjust charging amperage (Tessie API)."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/set_charging_amps",
            params=self._command_params(wait_for_completion, max_attempts, amps=amps),
        )

    async def open_charge_port(
        self, wait_for_completion: bool | None = None, max_attempts: int | None = None
    ) -> dict[str, Any]:
        """Open or unlock charge port."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/open_charge_port",
            params=self._command_params(wait_for_completion, max_attempts),
        )

    async def close_charge_port(
        self, wait_for_completion: bool | None = None, max_attempts: int | None = None
    ) -> dict[str, Any]:
        """Close charge port."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/close_charge_port",
            params=self._command_params(wait_for_completion, max_attempts),
        )

    async def flash(
        self, wait_for_completion: bool | None = None, max_attempts: int | None = None
    ) -> dict[str, Any]:
        """Flash vehicle lights."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/flash",
            params=self._command_params(wait_for_completion, max_attempts),
        )

    async def honk(
        self, wait_for_completion: bool | None = None, max_attempts: int | None = None
    ) -> dict[str, Any]:
        """Sound vehicle horn."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/honk",
            params=self._command_params(wait_for_completion, max_attempts),
        )

    async def tessie_trigger_homelink(
        self,
        max_attempts: int | None = None,
        wait_for_completion: bool | None = None,
    ) -> dict[str, Any]:
        """Activate HomeLink device (Tessie API)."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/trigger_homelink",
            params=self._command_params(wait_for_completion, max_attempts),
        )

    async def remote_start(
        self, wait_for_completion: bool | None = None, max_attempts: int | None = None
    ) -> dict[str, Any]:
        """Enable keyless driving."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/remote_start",
            params=self._command_params(wait_for_completion, max_attempts),
        )

    async def vent_sunroof(
        self, wait_for_completion: bool | None = None, max_attempts: int | None = None
    ) -> dict[str, Any]:
        """Open sunroof."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/vent_sunroof",
            params=self._command_params(wait_for_completion, max_attempts),
        )

    async def close_sunroof(
        self, wait_for_completion: bool | None = None, max_attempts: int | None = None
    ) -> dict[str, Any]:
        """Close sunroof."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/close_sunroof",
            params=self._command_params(wait_for_completion, max_attempts),
        )

    async def enable_sentry(
        self, wait_for_completion: bool | None = None, max_attempts: int | None = None
    ) -> dict[str, Any]:
        """Activate Sentry Mode."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/enable_sentry",
            params=self._command_params(wait_for_completion, max_attempts),
        )

    async def disable_sentry(
        self, wait_for_completion: bool | None = None, max_attempts: int | None = None
    ) -> dict[str, Any]:
        """Deactivate Sentry Mode."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/disable_sentry",
            params=self._command_params(wait_for_completion, max_attempts),
        )

    async def enable_valet(
        self,
        pin: str | int | None = None,
        wait_for_completion: bool | None = None,
        max_attempts: int | None = None,
    ) -> dict[str, Any]:
        """Activate Valet Mode."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/enable_valet",
            params=self._command_params(
                wait_for_completion,
                max_attempts,
                pin=str(pin) if pin is not None else None,
            ),
        )

    async def disable_valet(
        self,
        pin: str | int | None = None,
        wait_for_completion: bool | None = None,
        max_attempts: int | None = None,
    ) -> dict[str, Any]:
        """Deactivate Valet Mode."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/disable_valet",
            params=self._command_params(
                wait_for_completion,
                max_attempts,
                pin=str(pin) if pin is not None else None,
            ),
        )

    async def tessie_schedule_software_update(
        self,
        in_seconds: int,
        max_attempts: int | None = None,
        wait_for_completion: bool | None = None,
    ) -> dict[str, Any]:
        """Schedule update installation (Tessie API)."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/schedule_software_update",
            params=self._command_params(
                wait_for_completion, max_attempts, in_seconds=in_seconds
            ),
        )

    async def cancel_software_update(
        self, wait_for_completion: bool | None = None, max_attempts: int | None = None
    ) -> dict[str, Any]:
        """Cancel pending update."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/cancel_software_update",
            params=self._command_params(wait_for_completion, max_attempts),
        )

    async def set_scheduled_charging(
        self,
        enable: bool,
        time: int,
        wait_for_completion: bool | None = None,
        max_attempts: int | None = None,
    ) -> dict[str, Any]:
        """Configure scheduled charging."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/set_scheduled_charging",
            params=self._command_params(
                wait_for_completion, max_attempts, enable=enable, time=time
            ),
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
        max_attempts: int | None = None,
        wait_for_completion: bool | None = None,
    ) -> dict[str, Any]:
        """Configure scheduled departure (Tessie API)."""
        params: dict[str, Any] = {
            "enable": enable,
            "departure_time": departure_time,
            "preconditioning_enabled": preconditioning_enabled,
            "preconditioning_weekdays_only": preconditioning_weekdays_only,
            "off_peak_charging_enabled": off_peak_charging_enabled,
            "off_peak_charging_weekdays_only": off_peak_charging_weekdays_only,
        }
        if end_off_peak_time is not None:
            params["end_off_peak_time"] = end_off_peak_time
        return await self._request(
            Method.POST,
            f"{self.vin}/command/set_scheduled_departure",
            params=self._command_params(wait_for_completion, max_attempts, **params),
        )

    async def tessie_add_charge_schedule(
        self,
        days_of_week: str,
        enabled: bool,
        start_enabled: bool,
        end_enabled: bool,
        lat: float,
        lon: float,
        start_time: int | None = None,
        end_time: int | None = None,
        one_time: bool = False,
        id: int | None = None,
        max_attempts: int | None = None,
        wait_for_completion: bool | None = None,
    ) -> dict[str, Any]:
        """Add new charging schedule (Tessie API)."""
        if not start_enabled and not end_enabled:
            raise ValueError("Either start_enabled or end_enabled must be True")
        if start_enabled and start_time is None:
            raise ValueError("start_time is required when start_enabled is True")
        if end_enabled and end_time is None:
            raise ValueError("end_time is required when end_enabled is True")
        params: dict[str, Any] = {
            "days_of_week": days_of_week,
            "enabled": enabled,
            "start_enabled": start_enabled,
            "end_enabled": end_enabled,
            "lat": lat,
            "lon": lon,
            "one_time": one_time,
        }
        if start_time is not None:
            params["start_time"] = start_time
        if end_time is not None:
            params["end_time"] = end_time
        if id is not None:
            params["id"] = id
        return await self._request(
            Method.POST,
            f"{self.vin}/command/add_charge_schedule",
            params=self._command_params(wait_for_completion, max_attempts, **params),
        )

    async def remove_charge_schedule(
        self,
        id: int,
        wait_for_completion: bool | None = None,
        max_attempts: int | None = None,
    ) -> dict[str, Any]:
        """Delete charging schedule."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/remove_charge_schedule",
            params=self._command_params(wait_for_completion, max_attempts, id=id),
        )

    async def tessie_add_precondition_schedule(
        self,
        days_of_week: str,
        enabled: bool,
        lat: float,
        lon: float,
        precondition_time: int,
        one_time: bool = False,
        id: int | None = None,
        max_attempts: int | None = None,
        wait_for_completion: bool | None = None,
    ) -> dict[str, Any]:
        """Add preconditioning schedule (Tessie API)."""
        params: dict[str, Any] = {
            "days_of_week": days_of_week,
            "enabled": enabled,
            "lat": lat,
            "lon": lon,
            "precondition_time": precondition_time,
            "one_time": one_time,
        }
        if id is not None:
            params["id"] = id
        return await self._request(
            Method.POST,
            f"{self.vin}/command/add_precondition_schedule",
            params=self._command_params(wait_for_completion, max_attempts, **params),
        )

    async def remove_precondition_schedule(
        self,
        id: int,
        wait_for_completion: bool | None = None,
        max_attempts: int | None = None,
    ) -> dict[str, Any]:
        """Delete preconditioning schedule."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/remove_precondition_schedule",
            params=self._command_params(wait_for_completion, max_attempts, id=id),
        )

    async def share(
        self,
        value: str,
        locale: str = "en-US",
        wait_for_completion: bool | None = None,
        max_attempts: int | None = None,
    ) -> dict[str, Any]:
        """Share address/location to vehicle."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/share",
            params=self._command_params(
                wait_for_completion, max_attempts, value=value, locale=locale
            ),
        )

    async def remote_boombox(
        self,
        sound: int | None = None,
        wait_for_completion: bool | None = None,
        max_attempts: int | None = None,
    ) -> dict[str, Any]:
        """Trigger novelty sound effect."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/remote_boombox",
            params=self._command_params(wait_for_completion, max_attempts, sound=sound),
        )

    async def set_speed_limit(
        self,
        limit_mph: int | None = None,
        wait_for_completion: bool | None = None,
        max_attempts: int | None = None,
        mph: int | None = None,
    ) -> dict[str, Any]:
        """Set speed limit."""
        speed_limit = mph if mph is not None else limit_mph
        if speed_limit is None:
            raise ValueError("mph or limit_mph is required")
        return await self._request(
            Method.POST,
            f"{self.vin}/command/set_speed_limit",
            params=self._command_params(
                wait_for_completion, max_attempts, mph=speed_limit
            ),
        )

    async def enable_speed_limit(
        self,
        pin: str | int,
        wait_for_completion: bool | None = None,
        max_attempts: int | None = None,
    ) -> dict[str, Any]:
        """Activate speed limit."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/enable_speed_limit",
            params=self._command_params(
                wait_for_completion, max_attempts, pin=str(pin)
            ),
        )

    async def disable_speed_limit(
        self,
        pin: str | int,
        wait_for_completion: bool | None = None,
        max_attempts: int | None = None,
    ) -> dict[str, Any]:
        """Deactivate speed limit."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/disable_speed_limit",
            params=self._command_params(
                wait_for_completion, max_attempts, pin=str(pin)
            ),
        )

    async def clear_speed_limit_pin(
        self,
        pin: str | int,
        wait_for_completion: bool | None = None,
        max_attempts: int | None = None,
    ) -> dict[str, Any]:
        """Remove speed limit PIN."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/clear_speed_limit_pin",
            params=self._command_params(
                wait_for_completion, max_attempts, pin=str(pin)
            ),
        )

    async def enable_guest(
        self, wait_for_completion: bool | None = None, max_attempts: int | None = None
    ) -> dict[str, Any]:
        """Activate guest mode."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/enable_guest",
            params=self._command_params(wait_for_completion, max_attempts),
        )

    async def disable_guest(
        self, wait_for_completion: bool | None = None, max_attempts: int | None = None
    ) -> dict[str, Any]:
        """Deactivate guest mode."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/disable_guest",
            params=self._command_params(wait_for_completion, max_attempts),
        )

    async def enable_keep_accessory_power_mode(
        self, wait_for_completion: bool | None = None, max_attempts: int | None = None
    ) -> dict[str, Any]:
        """Enable Keep Accessory Power Mode."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/enable_keep_accessory_power_mode",
            params=self._command_params(wait_for_completion, max_attempts),
        )

    async def disable_keep_accessory_power_mode(
        self, wait_for_completion: bool | None = None, max_attempts: int | None = None
    ) -> dict[str, Any]:
        """Disable Keep Accessory Power Mode."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/disable_keep_accessory_power_mode",
            params=self._command_params(wait_for_completion, max_attempts),
        )

    async def enable_low_power_mode(
        self, wait_for_completion: bool | None = None, max_attempts: int | None = None
    ) -> dict[str, Any]:
        """Enable Low Power Mode."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/enable_low_power_mode",
            params=self._command_params(wait_for_completion, max_attempts),
        )

    async def disable_low_power_mode(
        self, wait_for_completion: bool | None = None, max_attempts: int | None = None
    ) -> dict[str, Any]:
        """Disable Low Power Mode."""
        return await self._request(
            Method.POST,
            f"{self.vin}/command/disable_low_power_mode",
            params=self._command_params(wait_for_completion, max_attempts),
        )

    # Vehicle Data
    async def state(self, use_cache: bool = True) -> dict[str, Any]:
        """Get vehicle data."""
        return await self._request(
            Method.GET, f"{self.vin}/state", params={"use_cache": use_cache}
        )

    async def vehicle(self, use_cache: bool = True) -> dict[str, Any]:
        """Alias for get-vehicle style access."""
        return await self.state(use_cache=use_cache)

    async def battery(self) -> dict[str, Any]:
        """Get battery data."""
        return await self._request(Method.GET, f"{self.vin}/battery")

    async def battery_health(
        self,
        start: int | None = None,
        end: int | None = None,
        distance_format: str | None = None,
    ) -> dict[str, Any]:
        """Get battery health data."""
        return await self._request(
            Method.GET,
            f"{self.vin}/battery_health",
            params={"from": start, "to": end, "distance_format": distance_format},
        )

    async def states(
        self,
        start: int | None = None,
        end: int | None = None,
        interval: int | None = None,
        condense: bool | None = None,
        timezone: str | None = None,
        distance_format: str | None = None,
        temperature_format: str | None = None,
        format: str | None = None,
        results: int | None = None,
        page: int | None = None,
        exclude: str | None = None,
        fields: str | None = None,
    ) -> dict[str, Any]:
        """Get historical vehicle states within timeframe."""
        return await self._request(
            Method.GET,
            f"{self.vin}/states",
            params={
                "from": start,
                "to": end,
                "interval": interval,
                "condense": condense,
                "timezone": timezone,
                "distance_format": distance_format,
                "temperature_format": temperature_format,
                "format": format,
                "results": results,
                "page": page,
                "exclude": exclude,
                "fields": fields,
            },
        )

    async def location(self) -> dict[str, Any]:
        """Get coordinates, address, and saved location."""
        return await self._request(Method.GET, f"{self.vin}/location")

    async def firmware_alerts(self) -> dict[str, Any]:
        """Get list of firmware-generated alerts."""
        return await self._request(Method.GET, f"{self.vin}/firmware_alerts")

    async def map(
        self,
        width: int | None = None,
        height: int | None = None,
        zoom: int | None = None,
        marker_size: str | None = None,
        style: str | None = None,
    ) -> dict[str, Any]:
        """Get map image of vehicle location."""
        return await self._request(
            Method.GET,
            f"{self.vin}/map",
            params={
                "width": width,
                "height": height,
                "zoom": zoom,
                "marker_size": marker_size,
                "style": style,
            },
        )

    async def consumption_since_charge(self) -> dict[str, Any]:
        """Get energy use data since last charge."""
        return await self._request(Method.GET, f"{self.vin}/consumption_since_charge")

    async def weather(self) -> dict[str, Any]:
        """Get weather forecast around vehicle."""
        return await self._request(Method.GET, f"{self.vin}/weather")

    async def drives(
        self,
        start: int | None = None,
        end: int | None = None,
        timezone: str | None = None,
        distance_format: str | None = None,
        temperature_format: str | None = None,
        origin_latitude: float | None = None,
        origin_longitude: float | None = None,
        origin_radius: int | None = None,
        exclude_origin: bool | None = None,
        destination_latitude: float | None = None,
        destination_longitude: float | None = None,
        destination_radius: int | None = None,
        exclude_destination: bool | None = None,
        tag: str | None = None,
        exclude_tag: str | None = None,
        driver_profile: str | None = None,
        exclude_driver_profile: str | None = None,
        format: str | None = None,
        minimum_distance: float | None = None,
        limit: int | None = None,
        results: int | None = None,
        page: int | None = None,
    ) -> dict[str, Any]:
        """Get historical drive records."""
        return await self._request(
            Method.GET,
            f"{self.vin}/drives",
            params={
                "from": start,
                "to": end,
                "timezone": timezone,
                "distance_format": distance_format,
                "temperature_format": temperature_format,
                "origin_latitude": origin_latitude,
                "origin_longitude": origin_longitude,
                "origin_radius": origin_radius,
                "exclude_origin": exclude_origin,
                "destination_latitude": destination_latitude,
                "destination_longitude": destination_longitude,
                "destination_radius": destination_radius,
                "exclude_destination": exclude_destination,
                "tag": tag,
                "exclude_tag": exclude_tag,
                "driver_profile": driver_profile,
                "exclude_driver_profile": exclude_driver_profile,
                "format": format,
                "minimum_distance": minimum_distance,
                "limit": limit if limit is not None else results,
                "page": page,
            },
        )

    async def path(
        self,
        start: int,
        end: int,
        separate: bool | None = None,
        simplify: bool | None = None,
        details: bool | None = None,
        timezone: str | None = None,
    ) -> dict[str, Any]:
        """Get driving route during specified timeframe."""
        return await self._request(
            Method.GET,
            f"{self.vin}/path",
            params={
                "from": start,
                "to": end,
                "separate": separate,
                "simplify": simplify,
                "details": details,
                "timezone": timezone,
            },
        )

    async def charges(
        self,
        start: int | None = None,
        end: int | None = None,
        timezone: str | None = None,
        distance_format: str | None = None,
        format: str | None = None,
        superchargers_only: bool | None = None,
        origin_latitude: float | None = None,
        origin_longitude: float | None = None,
        origin_radius: int | None = None,
        exclude_origin: bool | None = None,
        minimum_energy_added: float | None = None,
        limit: int | None = None,
        results: int | None = None,
        page: int | None = None,
    ) -> dict[str, Any]:
        """Get charging history."""
        return await self._request(
            Method.GET,
            f"{self.vin}/charges",
            params={
                "from": start,
                "to": end,
                "timezone": timezone,
                "distance_format": distance_format,
                "format": format,
                "superchargers_only": superchargers_only,
                "origin_latitude": origin_latitude,
                "origin_longitude": origin_longitude,
                "origin_radius": origin_radius,
                "exclude_origin": exclude_origin,
                "minimum_energy_added": minimum_energy_added,
                "limit": limit if limit is not None else results,
                "page": page,
            },
        )

    async def idles(
        self,
        start: int | None = None,
        end: int | None = None,
        timezone: str | None = None,
        distance_format: str | None = None,
        format: str | None = None,
        origin_latitude: float | None = None,
        origin_longitude: float | None = None,
        origin_radius: int | None = None,
        exclude_origin: bool | None = None,
        limit: int | None = None,
        results: int | None = None,
        page: int | None = None,
    ) -> dict[str, Any]:
        """Get idle periods when vehicle inactive."""
        return await self._request(
            Method.GET,
            f"{self.vin}/idles",
            params={
                "from": start,
                "to": end,
                "timezone": timezone,
                "distance_format": distance_format,
                "format": format,
                "origin_latitude": origin_latitude,
                "origin_longitude": origin_longitude,
                "origin_radius": origin_radius,
                "exclude_origin": exclude_origin,
                "limit": limit if limit is not None else results,
                "page": page,
            },
        )

    async def last_idle_state(self) -> dict[str, Any]:
        """Get latest idle period data."""
        return await self._request(Method.GET, f"{self.vin}/last_idle_state")

    # Driver Management
    async def drivers(self) -> dict[str, Any]:
        """List additional authorized drivers."""
        return await self._request(Method.GET, f"{self.vin}/drivers")

    async def delete_driver(
        self, id: str | int, user_id: int | None = None
    ) -> dict[str, Any]:
        """Remove driver access."""
        return await self._request(
            Method.POST,
            f"{self.vin}/drivers/{id}/delete",
            json={"user_id": user_id},
        )

    async def invitations(self) -> dict[str, Any]:
        """List pending driver invitations."""
        return await self._request(Method.GET, f"{self.vin}/invitations")

    async def create_invitation(
        self,
        email: str | None = None,
        role: str | None = None,
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
        self,
        config: dict[str, Any] | None = None,
        fields: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Set telemetry configuration."""
        payload = dict(config or {})
        if fields is not None:
            payload["fields"] = fields
        return await self._request(
            Method.POST,
            f"{self.vin}/fleet_telemetry_config",
            json=payload,
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
        start: int | None = None,
        end: int | None = None,
        tag: str | None = None,
        drives: list[int] | None = None,
    ) -> dict[str, Any]:
        """Assign tag to drives."""
        if tag is None:
            raise ValueError("tag is required")
        if drives is not None:
            return await self._request(
                Method.POST,
                f"{self.vin}/drives/set_tag",
                json={"drives": drives, "tag": tag},
            )
        if start is None or end is None:
            raise ValueError("Provide drives or both start and end")
        return await self._request(
            Method.POST,
            f"{self.vin}/drives/set_tag",
            params={"from": start, "to": end, "tag": tag},
        )

    async def set_charge_cost(
        self,
        charge_id: int,
        cost: float | None,
        currency: str | None = None,
    ) -> dict[str, Any]:
        """Record charging cost."""
        return await self._request(
            Method.POST,
            f"{self.vin}/charges/{charge_id}/set_cost",
            params={"cost": cost, "currency": currency},
        )

    # Vehicle Information
    async def tire_pressure(
        self,
        pressure_format: str | None = None,
        start: int | None = None,
        end: int | None = None,
    ) -> dict[str, Any]:
        """Get current tire pressure readings."""
        return await self._request(
            Method.GET,
            f"{self.vin}/tire_pressure",
            params={"pressure_format": pressure_format, "from": start, "to": end},
        )

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
        payload: dict[str, str] = {"plate": plate}
        if state:
            payload["state"] = state
        return await self._request(Method.POST, f"{self.vin}/plate", json=payload)


class TessieVehicles(Vehicles["Tessie"]):
    """Class containing and creating vehicles."""

    _parent: Tessie
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

    def createBluetooth(
        self,
        vin: str,
        confirmation: BluetoothConfirmation = "ack",
        keepalive_interval: float | None = None,
        raise_unconfirmed: bool = False,
        *,
        verify_commands: bool | None = None,
        optimistic: bool | None = None,
    ) -> Any:
        """Not supported; parameters match the Fleet API Bluetooth factory."""
        raise NotImplementedError("Tessie cannot use local Bluetooth")
