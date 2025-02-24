from __future__ import annotations

from locale import getlocale
from time import time
from typing import TYPE_CHECKING, Any, List

from tesla_fleet_api.const import (
    CabinOverheatProtectionTemp,
    ClimateKeeperMode,
    Level,
    Method,
    Seat,
    SunRoofCommand,
    Trunk,
    VehicleDataEndpoint,
    WindowCommand,
)
from tesla_fleet_api.tesla.vehicle.vehicle import Vehicle

DEFAULT_LOCALE = (getlocale()[0] or "en-US").replace("_","-")

if TYPE_CHECKING:
    from tesla_fleet_api.tesla.fleet import TeslaFleetApi

class VehicleFleet(Vehicle):
    """Class describing the Tesla Fleet API vehicle endpoints and commands."""

    def __init__(self, parent: TeslaFleetApi, vin: str):
        super().__init__(parent, vin)
        self._request = parent._request

    async def actuate_trunk(
        self, which_trunk: Trunk | str
    ) -> dict[str, Any]:
        """Controls the front or rear trunk."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{self.vin}/command/actuate_trunk",
            json={"which_trunk": which_trunk},
        )

    async def adjust_volume(
        self, volume: float
    ) -> dict[str, Any]:
        """Adjusts vehicle media playback volume."""
        if volume < 0.0 or volume > 11.0:
            raise ValueError("Volume must a number from 0.0 to 11.0")
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{self.vin}/command/adjust_volume",
            json={"volume": volume},
        )

    async def auto_conditioning_start(self) -> dict[str, Any]:
        """Starts climate preconditioning."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{self.vin}/command/auto_conditioning_start",
        )

    async def auto_conditioning_stop(self) -> dict[str, Any]:
        """Stops climate preconditioning."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{self.vin}/command/auto_conditioning_stop",
        )

    async def cancel_software_update(self) -> dict[str, Any]:
        """Cancels the countdown to install the vehicle software update."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{self.vin}/command/cancel_software_update",
        )

    async def charge_max_range(self) -> dict[str, Any]:
        """Charges in max range mode -- we recommend limiting the use of this mode to long trips."""
        return await self._request(
            Method.POST, f"api/1/vehicles/{self.vin}/command/charge_max_range"
        )

    async def charge_port_door_close(self) -> dict[str, Any]:
        """Closes the charge port door."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{self.vin}/command/charge_port_door_close",
        )

    async def charge_port_door_open(self) -> dict[str, Any]:
        """Opens the charge port door."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{self.vin}/command/charge_port_door_open",
        )

    async def charge_standard(self) -> dict[str, Any]:
        """Charges in Standard mode."""
        return await self._request(
            Method.POST, f"api/1/vehicles/{self.vin}/command/charge_standard"
        )

    async def charge_start(self) -> dict[str, Any]:
        """Starts charging the vehicle."""
        return await self._request(
            Method.POST, f"api/1/vehicles/{self.vin}/command/charge_start"
        )

    async def charge_stop(self) -> dict[str, Any]:
        """Stops charging the vehicle."""
        return await self._request(
            Method.POST, f"api/1/vehicles/{self.vin}/command/charge_stop"
        )

    async def clear_pin_to_drive_admin(self, pin: str | None = None):
        """Deactivates PIN to Drive and resets the associated PIN for vehicles running firmware versions 2023.44+. This command is only accessible to fleet managers or owners."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{self.vin}/command/clear_pin_to_drive_admin",
            json={"pin": pin}
        )

    async def door_lock(self) -> dict[str, Any]:
        """Locks the vehicle."""
        return await self._request(
            Method.POST, f"api/1/vehicles/{self.vin}/command/door_lock"
        )

    async def door_unlock(self) -> dict[str, Any]:
        """Unlocks the vehicle."""
        return await self._request(
            Method.POST, f"api/1/vehicles/{self.vin}/command/door_unlock"
        )

    async def erase_user_data(self) -> dict[str, Any]:
        """Erases user's data from the user interface. Requires the vehicle to be in park."""
        return await self._request(
            Method.POST, f"api/1/vehicles/{self.vin}/command/erase_user_data"
        )

    async def flash_lights(self) -> dict[str, Any]:
        """Briefly flashes the vehicle headlights. Requires the vehicle to be in park."""
        return await self._request(
            Method.POST, f"api/1/vehicles/{self.vin}/command/flash_lights"
        )

    async def guest_mode(self, enable: bool) -> dict[str, Any]:
        """Restricts certain vehicle UI functionality from guest users"""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{self.vin}/command/guest_mode",
            json={"enable": enable},
        )

    async def honk_horn(self) -> dict[str, Any]:
        """Honks the vehicle horn. Requires the vehicle to be in park."""
        return await self._request(
            Method.POST, f"api/1/vehicles/{self.vin}/command/honk_horn"
        )

    async def media_next_fav(self) -> dict[str, Any]:
        """Advances media player to next favorite track."""
        return await self._request(
            Method.POST, f"api/1/vehicles/{self.vin}/command/media_next_fav"
        )

    async def media_next_track(self) -> dict[str, Any]:
        """Advances media player to next track."""
        return await self._request(
            Method.POST, f"api/1/vehicles/{self.vin}/command/media_next_track"
        )

    async def media_prev_fav(self) -> dict[str, Any]:
        """Advances media player to previous favorite track."""
        return await self._request(
            Method.POST, f"api/1/vehicles/{self.vin}/command/media_prev_fav"
        )

    async def media_prev_track(self) -> dict[str, Any]:
        """Advances media player to previous track."""
        return await self._request(
            Method.POST, f"api/1/vehicles/{self.vin}/command/media_prev_track"
        )

    async def media_toggle_playback(self) -> dict[str, Any]:
        """Toggles current play/pause state."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{self.vin}/command/media_toggle_playback",
        )

    async def media_volume_down(self) -> dict[str, Any]:
        """Turns the volume down by one."""
        return await self._request(
            Method.POST, f"api/1/vehicles/{self.vin}/command/media_volume_down"
        )

    async def navigation_gps_request(
        self, lat: float, lon: float, order: int | None = None
    ) -> dict[str, Any]:
        """Start navigation to given coordinates. Order can be used to specify order of multiple stops."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{self.vin}/command/navigation_gps_request",
            json={"lat": lat, "lon": lon, "order": order},
        )

    async def navigation_request(
        self, value: str, type: str = "share_ext_content_raw", locale: str | None = None, timestamp_ms: int | None = None
    ) -> dict[str, Any]:
        """Sends a location to the in-vehicle navigation system."""
        timestamp_ms = timestamp_ms or int(time() * 1000)
        locale = locale or DEFAULT_LOCALE
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{self.vin}/command/navigation_request",
            json={"value": {"android.intent.extra.TEXT":value}, "type": type, "locale": locale, "timestamp_ms": timestamp_ms},
        )

    async def navigation_sc_request(
        self, id: int, order: int | None = None
    ) -> dict[str, Any]:
        """Sends a location to the in-vehicle navigation system."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{self.vin}/command/navigation_sc_request",
            json={"type": type, "id": id, "order": order},
        )

    async def remote_auto_seat_climate_request(
        self,
        auto_seat_position: int | Seat,
        auto_climate_on: bool,
    ) -> dict[str, Any]:
        """Sets automatic seat heating and cooling."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{self.vin}/command/remote_auto_seat_climate_request",
            json={
                "auto_seat_position": auto_seat_position,
                "auto_climate_on": auto_climate_on,
            },
        )

    async def remote_auto_steering_wheel_heat_climate_request(
        self, on: bool
    ) -> dict[str, Any]:
        """Sets automatic steering wheel heating on/off."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{self.vin}/command/remote_auto_steering_wheel_heat_climate_request",
            json={"on": on},
        )

    async def remote_boombox(
        self, sound: int
    ) -> dict[str, Any]:
        """Plays a sound through the vehicle external speaker."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{self.vin}/command/remote_boombox",
            json={"sound": sound},
        )

    async def remote_seat_cooler_request(
        self,
        seat_position: Seat | int,
        seat_cooler_level: Level | int,
    ) -> dict[str, Any]:
        """Sets seat cooling."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{self.vin}/command/remote_seat_cooler_request",
            json={
                "seat_position": seat_position,
                "seat_cooler_level": seat_cooler_level,
            },
        )

    async def remote_seat_heater_request(
        self,
        seat_position: Seat | int,
        seat_heater_level: Level | int,
    ) -> dict[str, Any]:
        """Sets seat heating."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{self.vin}/command/remote_seat_heater_request",
            json={
                "heater": seat_position,
                "level": seat_heater_level,
            },
        )

    async def remote_start_drive(self) -> dict[str, Any]:
        """Starts the vehicle remotely. Requires keyless driving to be enabled."""
        return await self._request(
            Method.POST, f"api/1/vehicles/{self.vin}/command/remote_start_drive"
        )

    async def remote_steering_wheel_heat_level_request(
        self, level: Level | int
    ) -> dict[str, Any]:
        """Sets steering wheel heat level."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{self.vin}/command/remote_steering_wheel_heat_level_request",
            json={"level": level},
        )

    async def remote_steering_wheel_heater_request(
        self, on: bool
    ) -> dict[str, Any]:
        """Sets steering wheel heating on/off. For vehicles that do not support auto steering wheel heat."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{self.vin}/command/remote_steering_wheel_heater_request",
            json={"on": on},
        )

    async def reset_pin_to_drive_pin(self) -> dict[str, Any]:
        """Removes PIN to Drive. Requires the car to be in Pin to Drive mode and not in Valet mode. Note that this only works if PIN to Drive is not active. This command also requires the Tesla Vehicle Command Protocol - for more information, please see refer to the documentation here."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{self.vin}/command/reset_pin_to_drive_pin",
        )

    async def reset_valet_pin(self) -> dict[str, Any]:
        """Removes PIN for Valet Mode."""
        return await self._request(
            Method.POST, f"api/1/vehicles/{self.vin}/command/reset_valet_pin"
        )

    async def schedule_software_update(
        self, offset_sec: int
    ) -> dict[str, Any]:
        """Schedules a vehicle software update (over the air "OTA") to be installed in the future."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{self.vin}/command/schedule_software_update",
            json={"offset_sec": offset_sec},
        )

    async def set_bioweapon_mode(
        self, on: bool, manual_override: bool
    ) -> dict[str, Any]:
        """Turns Bioweapon Defense Mode on and off."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{self.vin}/command/set_bioweapon_mode",
            json={"on": on, "manual_override": manual_override},
        )

    async def set_cabin_overheat_protection(
        self, on: bool, fan_only: bool
    ) -> dict[str, Any]:
        """Sets the vehicle overheat protection."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{self.vin}/command/set_cabin_overheat_protection",
            json={"on": on, "fan_only": fan_only},
        )

    async def set_charge_limit(
        self, percent: int
    ) -> dict[str, Any]:
        """Sets the vehicle charge limit."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{self.vin}/command/set_charge_limit",
            json={"percent": percent},
        )

    async def set_charging_amps(
        self, charging_amps: int
    ) -> dict[str, Any]:
        """Sets the vehicle charging amps."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{self.vin}/command/set_charging_amps",
            json={"charging_amps": charging_amps},
        )

    async def set_climate_keeper_mode(
        self, climate_keeper_mode: ClimateKeeperMode | int
    ) -> dict[str, Any]:
        """Enables climate keeper mode."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{self.vin}/command/set_climate_keeper_mode",
            json={"climate_keeper_mode": climate_keeper_mode},
        )

    async def set_cop_temp(
        self, cop_temp: CabinOverheatProtectionTemp | int
    ) -> dict[str, Any]:
        """Adjusts the Cabin Overheat Protection temperature (COP)."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{self.vin}/command/set_cop_temp",
            json={"cop_temp": cop_temp},
        )

    async def set_pin_to_drive(
        self, on: bool, password: str | int
    ) -> dict[str, Any]:
        """Sets a four-digit passcode for PIN to Drive. This PIN must then be entered before the vehicle can be driven."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{self.vin}/command/set_pin_to_drive",
            json={"on": on, "password": str(password)},
        )

    async def set_preconditioning_max(
        self, on: bool, manual_override: bool
    ) -> dict[str, Any]:
        """Sets an override for preconditioning — it should default to empty if no override is used."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{self.vin}/command/set_preconditioning_max",
            json={"on": on, "manual_override": manual_override},
        )

    async def set_scheduled_charging(
        self, enable: bool, time: int
    ) -> dict[str, Any]:
        """Sets a time at which charging should be completed. The time parameter is minutes after midnight (e.g: time=120 schedules charging for 2:00am vehicle local time)."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{self.vin}/command/set_scheduled_charging",
            json={"enable": enable, "time": time},
        )

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
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{self.vin}/command/set_scheduled_departure",
            json={
                "enable": enable,
                "preconditioning_enabled": preconditioning_enabled,
                "preconditioning_weekdays_only": preconditioning_weekdays_only,
                "departure_time": departure_time,
                "off_peak_charging_enabled": off_peak_charging_enabled,
                "off_peak_charging_weekdays_only": off_peak_charging_weekdays_only,
                "end_off_peak_time": end_off_peak_time,
            },
        )

    async def set_sentry_mode(self, on: bool) -> dict[str, Any]:
        """Enables and disables Sentry Mode. Sentry Mode allows customers to watch the vehicle cameras live from the mobile app, as well as record sentry events."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{self.vin}/command/set_sentry_mode",
            json={"on": on},
        )

    async def set_temps(
        self,
        driver_temp: float,
        passenger_temp: float,
    ) -> dict[str, Any]:
        """Sets the driver and/or passenger-side cabin temperature (and other zones if sync is enabled)."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{self.vin}/command/set_temps",
            json={"driver_temp": driver_temp, "passenger_temp": passenger_temp},
        )

    async def set_valet_mode(
        self, on: bool, password: str | int
    ) -> dict[str, Any]:
        """Turns on Valet Mode and sets a four-digit passcode that must then be entered to disable Valet Mode."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{self.vin}/command/set_valet_mode",
            json={"on": on, "password": str(password)},
        )

    async def set_vehicle_name(
        self, vehicle_name: str
    ) -> dict[str, Any]:
        """Changes the name of a vehicle. This command also requires the Tesla Vehicle Command Protocol - for more information, please see refer to the documentation here."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{self.vin}/command/set_vehicle_name",
            json={"vehicle_name": vehicle_name},
        )

    async def speed_limit_activate(
        self, pin: str | int
    ) -> dict[str, Any]:
        """Activates Speed Limit Mode with a four-digit PIN."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{self.vin}/command/speed_limit_activate",
            json={"pin": str(pin)},
        )

    async def speed_limit_clear_pin(
        self, pin: str | int
    ) -> dict[str, Any]:
        """Deactivates Speed Limit Mode and resets the associated PIN."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{self.vin}/command/speed_limit_clear_pin",
            json={"pin": str(pin)},
        )

    async def speed_limit_clear_pin_admin(
        self
    ) -> dict[str, Any]:
        """Deactivates Speed Limit Mode and resets the associated PIN for vehicles running firmware versions 2023.38+. This command is only accessible to fleet managers or owners."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{self.vin}/command/speed_limit_clear_pin_admin",
        )

    async def speed_limit_deactivate(
        self, pin: str | int
    ) -> dict[str, Any]:
        """Deactivates Speed Limit Mode."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{self.vin}/command/speed_limit_deactivate",
            json={"pin": str(pin)},
        )

    async def speed_limit_set_limit(
        self, limit_mph: int
    ) -> dict[str, Any]:
        """Sets the maximum speed allowed when Speed Limit Mode is active."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{self.vin}/command/speed_limit_set_limit",
            json={"limit_mph": limit_mph},
        )

    async def sun_roof_control(
        self, state: str | SunRoofCommand
    ) -> dict[str, Any]:
        """Controls the panoramic sunroof on the Model S."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{self.vin}/command/sun_roof_control",
            json={"state": state},
        )

    async def take_drivenote(self, note: str) -> dict[str, Any]:
        """Records a drive note. The note parameter is truncated to 80 characters in length."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{self.vin}/command/take_drivenote",
            json={"note": note},
        )

    async def trigger_homelink(
        self,
        token: str | None = None,
        lat: float | None = None,
        lon: float | None = None,
    ) -> dict[str, Any]:
        """Turns on HomeLink (used to open and close garage doors)."""
        data: dict[str, str | float] = {}
        if token:
            data["token"] = token
        if lat and lon:
            data["lat"] = lat
            data["lon"] = lon
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{self.vin}/command/trigger_homelink",
            json=data,
        )

    async def upcoming_calendar_entries(
        self,
        calendar_data: str
    ) -> dict[str, Any]:
        """Upcoming calendar entries stored on the vehicle."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{self.vin}/command/upcoming_calendar_entries",
            json={"calendar_data": calendar_data},
        )

    async def window_control(
        self,
        command: str | WindowCommand,
        lat: float | None = None,
        lon: float | None = None,
    ) -> dict[str, Any]:
        """Control the windows of a parked vehicle. Supported commands: vent and close. When closing, specify lat and lon of user to ensure they are within range of vehicle (unless this is an M3 platform vehicle)."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{self.vin}/command/window_control",
            json={"lat": lat, "lon": lon, "command": command},
        )

    async def drivers(self, ) -> dict[str, Any]:
        """Returns all allowed drivers for a vehicle. This endpoint is only available for the vehicle owner."""
        return await self._request(Method.GET, f"api/1/vehicles/{self.vin}/drivers")

    async def drivers_remove(
        self,  share_user_id: str | int | None = None
    ) -> dict[str, Any]:
        """Removes driver access from a vehicle. Share users can only remove their own access. Owners can remove share access or their own."""
        return await self._request(
            Method.DELETE,
            f"api/1/vehicles/{self.vin}/drivers",
            {"share_user_id": share_user_id},
        )

    async def list(
        self, page: int | None = None, per_page: int | None = None
    ) -> dict[str, Any]:
        """Returns vehicles belonging to the account."""
        return await self._request(
            Method.GET, "api/1/vehicles", {"page": page, "per_page": per_page}
        )

    async def mobile_enabled(self, ) -> dict[str, Any]:
        """Returns whether or not mobile access is enabled for the vehicle."""
        return await self._request(
            Method.GET, f"api/1/vehicles/{self.vin}/mobile_enabled"
        )

    async def nearby_charging_sites(
        self,
        count: int | None = None,
        radius: int | None = None,
        detail: bool | None = None,
    ) -> dict[str, Any]:
        """Returns the charging sites near the current location of the vehicle."""
        return await self._request(
            Method.GET,
            f"api/1/vehicles/{self.vin}/nearby_charging_sites",
            {"count": count, "radius": radius, "detail": detail},
        )

    async def options(self, vin: str) -> dict[str, Any]:
        """Returns vehicle option details."""
        return await self._request(
            Method.GET, "api/1/dx/vehicles/options", {"vin": vin}
        )

    async def recent_alerts(self) -> dict[str, Any]:
        """List of recent alerts"""
        return await self._request(
            Method.GET, f"api/1/vehicles/{self.vin}/recent_alerts"
        )

    async def release_notes(
        self,
        staged: bool | None = None,
        language: int | None = None,
    ) -> dict[str, Any]:
        """Returns firmware release notes."""
        return await self._request(
            Method.GET,
            f"api/1/vehicles/{self.vin}/release_notes",
            {"staged": staged, "language": language},
        )

    async def service_data(self) -> dict[str, Any]:
        """Returns service data."""
        return await self._request(
            Method.GET, f"api/1/vehicles/{self.vin}/service_data"
        )

    async def share_invites(self) -> dict[str, Any]:
        """Returns the share invites for a vehicle."""
        return await self._request(
            Method.GET, f"api/1/vehicles/{self.vin}/invitations"
        )

    async def share_invites_create(self) -> dict[str, Any]:
        """Creates a share invite for a vehicle."""
        return await self._request(
            Method.POST, f"api/1/vehicles/{self.vin}/invitations"
        )

    async def share_invites_redeem(self, code: str) -> dict[str, Any]:
        """Redeems a share invite."""
        return await self._request(
            Method.POST, "api/1/invitations/redeem", {code: code}
        )

    async def share_invites_revoke(
        self, id: str
    ) -> dict[str, Any]:
        """Revokes a share invite."""
        return await self._request(
            Method.POST, f"api/1/vehicles/{self.vin}/invitations/{id}/revoke"
        )

    async def signed_command(
        self, routable_message: str
    ) -> dict[str, Any]:
        """Signed Commands is a generic endpoint replacing legacy commands."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{self.vin}/signed_command",
            json={"routable_message": routable_message},
        )

    async def vehicle(self, ) -> dict[str, Any]:
        """Returns information about a vehicle."""
        return await self._request(Method.GET, f"api/1/vehicles/{self.vin}")

    async def vehicle_data(
        self, endpoints: list[VehicleDataEndpoint | str] | None = None,
    ) -> dict[str, Any]:
        """Makes a live call to the vehicle. This may return cached data if the vehicle is offline. For vehicles running firmware versions 2023.38+, location_data is required to fetch vehicle location. This will result in a location sharing icon to show on the vehicle UI."""
        endpoint_payload = ";".join(endpoints) if endpoints else None
        return await self._request(
            Method.GET,
            f"api/1/vehicles/{self.vin}/vehicle_data",
            {"endpoints": endpoint_payload},
        )

    async def wake_up(self) -> dict[str, Any]:
        """Wakes the vehicle from sleep, which is a state to minimize idle energy consumption."""
        return await self._request(Method.POST, f"api/1/vehicles/{self.vin}/wake_up")

    async def warranty_details(self, vin: str | None) -> dict[str, Any]:
        """Returns warranty details."""
        return await self._request(
            Method.GET, "api/1/dx/warranty/details", {"vin": vin}
        )

    async def fleet_status(self, vins: List[str]) -> dict[str, Any]:
        """Checks whether vehicles can accept Tesla commands protocol for the partner's public key"""
        return await self._request(
            Method.POST, "api/1/vehicles/fleet_status", json={"vins": vins}
        )

    async def fleet_telemetry_config_create(
        self, config: dict[str, Any]
    ) -> dict[str, Any]:
        """Configures fleet telemetry."""
        return await self._request(
            Method.POST, "api/1/vehicles/fleet_telemetry_config", json=config
        )

    async def fleet_telemetry_config_get(self) -> dict[str, Any]:
        """Configures fleet telemetry."""
        return await self._request(
            Method.GET, f"api/1/vehicles/{self.vin}/fleet_telemetry_config"
        )

    async def fleet_telemetry_config_delete(self) -> dict[str, Any]:
        """Configures fleet telemetry."""
        return await self._request(
            Method.DELETE, f"api/1/vehicles/{self.vin}/fleet_telemetry_config"
        )

    async def add_charge_schedule(
        self,
        days_of_week: str | int,
        enabled: bool,
        lat: float,
        lon: float,
        start_time: int | None = None,
        end_time: int | None = None,
        one_time: bool | None = None,
        id: int | None = None,
        name: str | None = None,

    ) -> dict[str, Any]:
        """Add a schedule for vehicle charging."""
        if not start_time and not end_time:
            raise ValueError("Either start_time or end_time or both must be provided")
        json_payload = {
            "days_of_week": days_of_week,
            "enabled": enabled,
            "end_enabled": end_time is not None,
            "lat": lat,
            "lon": lon,
            "start_enabled": start_time is not None,
        }
        if start_time is not None:
            json_payload["start_time"] = start_time
        if end_time is not None:
            json_payload["end_time"] = end_time
        if id is not None:
            json_payload["id"] = id
        if one_time is not None:
            json_payload["one_time"] = one_time

        return await self._request(
            Method.POST,
            f"api/1/vehicles/{self.vin}/command/add_charge_schedule",
            json=json_payload,
        )

    async def add_precondition_schedule(
        self,days_of_week: str | int,
        enabled: bool,
        lat: float,
        lon: float,
        precondition_time: int,
        id: int | None = None,
        one_time: bool | None = None,
        name: str | None = None,
    ) -> dict[str, Any]:
        """Add or modify a preconditioning schedule."""
        json_payload = {
            "days_of_week": days_of_week,
            "enabled": enabled,
            "lat": lat,
            "lon": lon,
            "precondition_time": precondition_time,
        }
        if id is not None:
            json_payload["id"] = id
        if one_time is not None:
            json_payload["one_time"] = one_time

        return await self._request(
            Method.POST,
            f"api/1/vehicles/{self.vin}/command/add_precondition_schedule",
            json=json_payload,
        )

    async def remove_charge_schedule(
        self,  id: int
    ) -> dict[str, Any]:
        """Removes the scheduled charging settings."""
        return await self._request(
            Method.POST, f"api/1/vehicles/{self.vin}/command/remove_charge_schedule", json={"id": id}
        )

    async def remove_precondition_schedule(
        self,  id: int
    ) -> dict[str, Any]:
        """Removes the scheduled precondition settings."""
        return await self._request(
            Method.POST, f"api/1/vehicles/{self.vin}/command/remove_precondition_schedule", json={"id": id}
        )
