from __future__ import annotations
from typing import Any, TYPE_CHECKING
from .const import (
    Trunk,
    ClimateKeeperMode,
    CabinOverheatProtectionTemp,
    VehicleDataEndpoint,
    SunRoofCommand,
    WindowCommand,
    DeviceType,
)

if TYPE_CHECKING:
    from .vehicle import Vehicle


class VehicleSpecific:
    """Class describing the Tesla Fleet API vehicle endpoints and commands for a specific vehicle."""

    _parent: Vehicle
    vin: str

    def __init__(self, parent: Vehicle, vin: str):
        self._parent = parent
        self.vin = vin

    @property
    def pre2021(self) -> bool:
        """Checks if a vehicle is pre-2021."""
        return self._parent.pre2021(self.vin)

    async def actuate_trunk(self, which_trunk: Trunk | str) -> dict[str, Any]:
        """Controls the front or rear trunk."""
        return await self._parent.actuate_trunk(self.vin, which_trunk)

    async def adjust_volume(self, volume: float) -> dict[str, Any]:
        """Adjusts vehicle media playback volume."""
        return await self._parent.adjust_volume(self.vin, volume)

    async def auto_conditioning_start(self) -> dict[str, Any]:
        """Starts climate preconditioning."""
        return await self._parent.auto_conditioning_start(self.vin)

    async def auto_conditioning_stop(self) -> dict[str, Any]:
        """Stops climate preconditioning."""
        return await self._parent.auto_conditioning_stop(self.vin)

    async def cancel_software_update(self) -> dict[str, Any]:
        """Cancels the countdown to install the vehicle software update."""
        return await self._parent.cancel_software_update(self.vin)

    async def charge_max_range(self) -> dict[str, Any]:
        """Charges in max range mode -- we recommend limiting the use of this mode to long trips."""
        return await self._parent.charge_max_range(self.vin)

    async def charge_port_door_close(self) -> dict[str, Any]:
        """Closes the charge port door."""
        return await self._parent.charge_port_door_close(self.vin)

    async def charge_port_door_open(self) -> dict[str, Any]:
        """Opens the charge port door."""
        return await self._parent.charge_port_door_open(self.vin)

    async def charge_standard(self) -> dict[str, Any]:
        """Charges in Standard mode."""
        return await self._parent.charge_standard(self.vin)

    async def charge_start(self) -> dict[str, Any]:
        """Starts charging the vehicle."""
        return await self._parent.charge_start(self.vin)

    async def charge_stop(self) -> dict[str, Any]:
        """Stops charging the vehicle."""
        return await self._parent.charge_stop(self.vin)

    async def clear_pin_to_drive_admin(self):
        """Deactivates PIN to Drive and resets the associated PIN for vehicles running firmware versions 2023.44+. This command is only accessible to fleet managers or owners."""
        return await self._parent.clear_pin_to_drive_admin(self.vin)

    async def door_lock(self) -> dict[str, Any]:
        """Locks the vehicle."""
        return await self._parent.door_lock(self.vin)

    async def door_unlock(self) -> dict[str, Any]:
        """Unlocks the vehicle."""
        return await self._parent.door_unlock(self.vin)

    async def erase_user_data(self) -> dict[str, Any]:
        """Erases user's data from the user interface. Requires the vehicle to be in park."""
        return await self._parent.erase_user_data(self.vin)

    async def flash_lights(self) -> dict[str, Any]:
        """Briefly flashes the vehicle headlights. Requires the vehicle to be in park."""
        return await self._parent.flash_lights(self.vin)

    async def guest_mode(self, enable: bool) -> dict[str, Any]:
        """Restricts certain vehicle UI functionality from guest users"""
        return await self._parent.guest_mode(self.vin, enable)

    async def honk_horn(self) -> dict[str, Any]:
        """Honks the vehicle horn. Requires the vehicle to be in park."""
        return await self._parent.honk_horn(self.vin)

    async def media_next_fav(self) -> dict[str, Any]:
        """Advances media player to next favorite track."""
        return await self._parent.media_next_fav(self.vin)

    async def media_next_track(self) -> dict[str, Any]:
        """Advances media player to next track."""
        return await self._parent.media_next_track(self.vin)

    async def media_prev_fav(self) -> dict[str, Any]:
        """Advances media player to previous favorite track."""
        return await self._parent.media_prev_fav(self.vin)

    async def media_prev_track(self) -> dict[str, Any]:
        """Advances media player to previous track."""
        return await self._parent.media_prev_track(self.vin)

    async def media_toggle_playback(self) -> dict[str, Any]:
        """Toggles current play/pause state."""
        return await self._parent.media_toggle_playback(self.vin)

    async def media_volume_down(self) -> dict[str, Any]:
        """Turns the volume down by one."""
        return await self._parent.media_volume_down(self.vin)

    async def navigation_gps_request(
        self, lat: float, lon: float, order: int | None = None
    ) -> dict[str, Any]:
        """Start navigation to given coordinates. Order can be used to specify order of multiple stops."""
        return await self._parent.navigation_gps_request(self.vin, lat, lon, order)

    async def navigation_request(
        self, type: str, locale: str, timestamp_ms: str
    ) -> dict[str, Any]:
        """Sends a location to the in-vehicle navigation system."""
        return await self._parent.navigation_request(
            self.vin, type, locale, timestamp_ms
        )

    async def navigation_sc_request(
        self, id: int, order: int | None = None
    ) -> dict[str, Any]:
        """Sends a location to the in-vehicle navigation system."""
        return await self._parent.navigation_sc_request(self.vin, id, order)

    async def remote_auto_seat_climate_request(
        self, auto_seat_position: int, auto_climate_on: bool
    ) -> dict[str, Any]:
        """Sets automatic seat heating and cooling."""
        return await self._parent.remote_auto_seat_climate_request(
            self.vin, auto_seat_position, auto_climate_on
        )

    async def remote_auto_steering_wheel_heat_climate_request(
        self, on: bool
    ) -> dict[str, Any]:
        """Sets automatic steering wheel heating on/off."""
        return await self._parent.remote_auto_steering_wheel_heat_climate_request(
            self.vin, on
        )

    async def remote_boombox(self, sound: int) -> dict[str, Any]:
        """Plays a sound through the vehicle external speaker."""
        return await self._parent.remote_boombox(self.vin, sound)

    async def remote_seat_cooler_request(
        self, seat_position: int, seat_cooler_level: int
    ) -> dict[str, Any]:
        """Sets seat cooling."""
        return await self._parent.remote_seat_cooler_request(
            self.vin, seat_position, seat_cooler_level
        )

    async def remote_seat_heater_request(
        self, seat_position: int, seat_heater_level: int
    ) -> dict[str, Any]:
        """Sets seat heating."""
        return await self._parent.remote_seat_heater_request(
            self.vin, seat_position, seat_heater_level
        )

    async def remote_start_drive(self) -> dict[str, Any]:
        """Starts the vehicle remotely. Requires keyless driving to be enabled."""
        return await self._parent.remote_start_drive(self.vin)

    async def remote_steering_wheel_heat_level_request(
        self, level: int
    ) -> dict[str, Any]:
        """Sets steering wheel heat level."""
        return await self._parent.remote_steering_wheel_heat_level_request(
            self.vin, level
        )

    async def remote_steering_wheel_heater_request(self, on: bool) -> dict[str, Any]:
        """Sets steering wheel heating on/off. For vehicles that do not support auto steering wheel heat."""
        return await self._parent.remote_steering_wheel_heater_request(self.vin, on)

    async def reset_pin_to_drive_pin(self) -> dict[str, Any]:
        """Removes PIN to Drive. Requires the car to be in Pin to Drive mode and not in Valet mode. Note that this only works if PIN to Drive is not active. This command also requires the Tesla Vehicle Command Protocol - for more information, please see refer to the documentation here."""
        return await self._parent.reset_pin_to_drive_pin(self.vin)

    async def reset_valet_pin(self) -> dict[str, Any]:
        """Removes PIN for Valet Mode."""
        return await self._parent.reset_valet_pin(self.vin)

    async def schedule_software_update(self, offset_sec: int) -> dict[str, Any]:
        """Schedules a vehicle software update (over the air "OTA") to be installed in the future."""
        return await self._parent.schedule_software_update(self.vin, offset_sec)

    async def set_bioweapon_mode(
        self, on: bool, manual_override: bool
    ) -> dict[str, Any]:
        """Turns Bioweapon Defense Mode on and off."""
        return await self._parent.set_bioweapon_mode(self.vin, on, manual_override)

    async def set_cabin_overheat_protection(
        self, on: bool, fan_only: bool
    ) -> dict[str, Any]:
        """Sets the vehicle overheat protection."""
        return await self._parent.set_cabin_overheat_protection(self.vin, on, fan_only)

    async def set_charge_limit(self, percent: int) -> dict[str, Any]:
        """Sets the vehicle charge limit."""
        return await self._parent.set_charge_limit(self.vin, percent)

    async def set_charging_amps(self, charging_amps: int) -> dict[str, Any]:
        """Sets the vehicle charging amps."""
        return await self._parent.set_charging_amps(self.vin, charging_amps)

    async def set_climate_keeper_mode(
        self, climate_keeper_mode: ClimateKeeperMode | int
    ) -> dict[str, Any]:
        """Enables climate keeper mode."""
        return await self._parent.set_climate_keeper_mode(self.vin, climate_keeper_mode)

    async def set_cop_temp(
        self, cop_temp: CabinOverheatProtectionTemp | int
    ) -> dict[str, Any]:
        """Adjusts the Cabin Overheat Protection temperature (COP)."""
        return await self._parent.set_cop_temp(self.vin, cop_temp)

    async def set_pin_to_drive(self, on: bool, password: str | int) -> dict[str, Any]:
        """Sets a four-digit passcode for PIN to Drive. This PIN must then be entered before the vehicle can be driven."""
        return await self._parent.set_pin_to_drive(self.vin, on, password)

    async def set_preconditioning_max(
        self, on: bool, manual_override: bool
    ) -> dict[str, Any]:
        """Sets an override for preconditioning — it should default to empty if no override is used."""
        return await self._parent.set_preconditioning_max(self.vin, on, manual_override)

    async def set_scheduled_charging(self, enable: bool, time: int) -> dict[str, Any]:
        """Sets a time at which charging should be completed. The time parameter is minutes after midnight (e.g: time=120 schedules charging for 2:00am vehicle local time)."""
        return await self._parent.set_scheduled_charging(self.vin, enable, time)

    async def set_scheduled_departure(
        self,
        enable: bool = True,
        preconditioning_enabled: bool = False,
        preconditioning_weekdays_only: bool = False,
        departure_time: int = 0,
        off_peak_charging_enabled: bool = False,
        off_peak_charging_weekdays_only: bool = False,
        end_off_peak_time: int = 0,
    ) -> dict[str, Any]:
        """Sets a time at which departure should be completed. The time parameter is minutes after midnight (e.g: time=120 schedules departure for 2:00am vehicle local time)."""
        return await self._parent.set_scheduled_departure(
            self.vin,
            enable,
            preconditioning_enabled,
            preconditioning_weekdays_only,
            departure_time,
            off_peak_charging_enabled,
            off_peak_charging_weekdays_only,
            end_off_peak_time,
        )

    async def set_sentry_mode(self, on: bool) -> dict[str, Any]:
        """Enables and disables Sentry Mode. Sentry Mode allows customers to watch the vehicle cameras live from the mobile app, as well as record sentry events."""
        return await self._parent.set_sentry_mode(self.vin, on)

    async def set_temps(
        self, driver_temp: float, passenger_temp: float
    ) -> dict[str, Any]:
        """Sets the driver and/or passenger-side cabin temperature (and other zones if sync is enabled)."""
        return await self._parent.set_temps(self.vin, driver_temp, passenger_temp)

    async def set_valet_mode(self, on: bool, password: str | int) -> dict[str, Any]:
        """Turns on Valet Mode and sets a four-digit passcode that must then be entered to disable Valet Mode."""
        return await self._parent.set_valet_mode(self.vin, on, password)

    async def set_vehicle_name(self, vehicle_name: str) -> dict[str, Any]:
        """Changes the name of a vehicle. This command also requires the Tesla Vehicle Command Protocol - for more information, please see refer to the documentation here."""
        return await self._parent.set_vehicle_name(self.vin, vehicle_name)

    async def speed_limit_activate(self, pin: str | int) -> dict[str, Any]:
        """Activates Speed Limit Mode with a four-digit PIN."""
        return await self._parent.speed_limit_activate(self.vin, pin)

    async def speed_limit_clear_pin(self, pin: str | int) -> dict[str, Any]:
        """Deactivates Speed Limit Mode and resets the associated PIN."""
        return await self._parent.speed_limit_clear_pin(self.vin, pin)

    async def speed_limit_clear_pin_admin(self) -> dict[str, Any]:
        """Deactivates Speed Limit Mode and resets the associated PIN for vehicles running firmware versions 2023.38+. This command is only accessible to fleet managers or owners."""
        return await self._parent.speed_limit_clear_pin_admin(self.vin)

    async def speed_limit_deactivate(self, pin: str | int) -> dict[str, Any]:
        """Deactivates Speed Limit Mode."""
        return await self._parent.speed_limit_deactivate(self.vin, pin)

    async def speed_limit_set_limit(self, limit_mph: int) -> dict[str, Any]:
        """Sets the maximum speed allowed when Speed Limit Mode is active."""
        return await self._parent.speed_limit_set_limit(self.vin, limit_mph)

    async def sun_roof_control(self, state: str | SunRoofCommand) -> dict[str, Any]:
        """Controls the panoramic sunroof on the Model S."""
        return await self._parent.sun_roof_control(self.vin, state)

    async def take_drivenote(self, note: str) -> dict[str, Any]:
        """Records a drive note. The note parameter is truncated to 80 characters in length."""
        return await self._parent.take_drivenote(self.vin, note)

    async def trigger_homelink(
        self,
        token: str | None = None,
        lat: float | None = None,
        lon: float | None = None,
    ) -> dict[str, Any]:
        """Turns on HomeLink (used to open and close garage doors)."""
        return await self._parent.trigger_homelink(
            self.vin,
            token,
            lat,
            lon,
        )

    async def upcoming_calendar_entries(self, calendar_data: str) -> dict[str, Any]:
        """Upcoming calendar entries stored on the vehicle."""
        return await self._parent.upcoming_calendar_entries(self.vin, calendar_data)

    async def window_control(
        self,
        command: str | WindowCommand,
        lat: float | None = None,
        lon: float | None = None,
    ) -> dict[str, Any]:
        """Control the windows of a parked vehicle. Supported commands: vent and close. When closing, specify lat and lon of user to ensure they are within range of vehicle (unless this is an M3 platform vehicle)."""
        return await self._parent.window_control(self.vin, command, lat, lon)

    async def drivers(self) -> dict[str, Any]:
        """Returns all allowed drivers for a vehicle. This endpoint is only available for the vehicle owner."""
        return await self._parent.drivers(self.vin)

    async def drivers_remove(
        self, share_user_id: str | int | None = None
    ) -> dict[str, Any]:
        """Removes driver access from a vehicle. Share users can only remove their own access. Owners can remove share access or their own."""
        return await self._parent.drivers_remove(self.vin, share_user_id)

    async def mobile_enabled(self) -> dict[str, Any]:
        """Returns whether or not mobile access is enabled for the vehicle."""
        return await self._parent.mobile_enabled(self.vin)

    async def nearby_charging_sites(
        self,
        count: int | None = None,
        radius: int | None = None,
        detail: bool | None = None,
    ) -> dict[str, Any]:
        """Returns the charging sites near the current location of the vehicle."""
        return await self._parent.nearby_charging_sites(self.vin, count, radius, detail)

    async def options(self) -> dict[str, Any]:
        """Returns vehicle option details."""
        return await self._parent.options(self.vin)

    async def recent_alerts(self) -> dict[str, Any]:
        """List of recent alerts"""
        return await self._parent.recent_alerts(self.vin)

    async def release_notes(
        self,
        staged: bool | None = None,
        language: int | None = None,
    ) -> dict[str, Any]:
        """Returns firmware release notes."""
        return await self._parent.release_notes(self.vin, staged, language)

    async def service_data(self) -> dict[str, Any]:
        """Returns service data."""
        return await self._parent.service_data(self.vin)

    async def share_invites(self) -> dict[str, Any]:
        """Returns the share invites for a vehicle."""
        return await self._parent.share_invites(self.vin)

    async def share_invites_create(self) -> dict[str, Any]:
        """Creates a share invite for a vehicle."""
        return await self._parent.share_invites_create(self.vin)

    async def share_invites_redeem(self, code: str) -> dict[str, Any]:
        """Redeems a share invite."""
        return await self._parent.share_invites_redeem(code)

    async def share_invites_revoke(self, id: str) -> dict[str, Any]:
        """Revokes a share invite."""
        return await self._parent.share_invites_revoke(self.vin, id)

    async def signed_command(self, routable_message: str) -> dict[str, Any]:
        """Signed Commands is a generic endpoint replacing legacy commands."""
        return await self._parent.signed_command(self.vin, routable_message)

    async def vehicle(self) -> dict[str, Any]:
        """Returns information about a vehicle."""
        return await self._parent.vehicle(self.vin)

    async def vehicle_data(
        self,
        endpoints: list[VehicleDataEndpoint | str] | None = None,
    ) -> dict[str, Any]:
        """Makes a live call to the vehicle. This may return cached data if the vehicle is offline. For vehicles running firmware versions 2023.38+, location_data is required to fetch vehicle location. This will result in a location sharing icon to show on the vehicle UI."""
        return await self._parent.vehicle_data(self.vin, endpoints)

    async def wake_up(self) -> dict[str, Any]:
        """Wakes the vehicle from sleep, which is a state to minimize idle energy consumption."""
        return await self._parent.wake_up(self.vin)

    async def warranty_details(self) -> dict[str, Any]:
        """Returns warranty details."""
        return await self._parent.warranty_details(self.vin)

    async def fleet_status(self) -> dict[str, Any]:
        """Checks whether vehicles can accept Tesla commands protocol for the partner's public key"""
        return await self._parent.fleet_status([self.vin])

    async def fleet_telemetry_config_create(
        self, config: dict[str, Any]
    ) -> dict[str, Any]:
        """Configures fleet telemetry."""
        return await self._parent.fleet_telemetry_config_create(
            {"vins": [self.vin], "config": config}
        )

    async def fleet_telemetry_config_get(self) -> dict[str, Any]:
        """Configures fleet telemetry."""
        return await self._parent.fleet_telemetry_config_get(self.vin)

    async def fleet_telemetry_config_delete(self) -> dict[str, Any]:
        """Configures fleet telemetry."""
        return await self._parent.fleet_telemetry_config_delete(self.vin)
