from __future__ import annotations
from typing import Any, List, TYPE_CHECKING
from cryptography.hazmat.primitives.asymmetric import ec
from .const import (
    Method,
    Trunk,
    ClimateKeeperMode,
    CabinOverheatProtectionTemp,
    VehicleDataEndpoint,
    SunRoofCommand,
    WindowCommand,
    DeviceType,
    Seat,
    Level,
)
from .vehiclespecific import VehicleSpecific
from .vehiclesigned import VehicleSigned

if TYPE_CHECKING:
    from .teslafleetapi import TeslaFleetApi


class Vehicle:
    """Class describing the Tesla Fleet API vehicle endpoints and commands."""

    _parent: TeslaFleetApi

    def __init__(self, parent: TeslaFleetApi):
        self._parent = parent
        self._request = parent._request

    def specific(self, vin: str) -> VehicleSpecific:
        """Creates a class for each vehicle."""
        return VehicleSpecific(self, vin)

    def specific_signed(
        self, vin: str, private_key: ec.EllipticCurvePrivateKey | None = None
    ) -> VehicleSigned:
        """Creates a class for each vehicle with command signing."""
        return VehicleSigned(self, vin, private_key)

    def pre2021(self, vin: str) -> bool:
        """Checks if a vehicle is a pre-2021 model S or X."""
        return vin[9] <= "L" and vin[3] in ["S", "X"]

    async def actuate_trunk(
        self, vehicle_tag: str | int, which_trunk: Trunk | str
    ) -> dict[str, Any]:
        """Controls the front or rear trunk."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{vehicle_tag}/command/actuate_trunk",
            json={"which_trunk": which_trunk},
        )

    async def adjust_volume(
        self, vehicle_tag: str | int, volume: float
    ) -> dict[str, Any]:
        """Adjusts vehicle media playback volume."""
        if volume < 0.0 or volume > 11.0:
            raise ValueError("Volume must a number from 0.0 to 11.0")
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{vehicle_tag}/command/adjust_volume",
            json={"volume": volume},
        )

    async def auto_conditioning_start(self, vehicle_tag: str | int) -> dict[str, Any]:
        """Starts climate preconditioning."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{vehicle_tag}/command/auto_conditioning_start",
        )

    async def auto_conditioning_stop(self, vehicle_tag: str | int) -> dict[str, Any]:
        """Stops climate preconditioning."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{vehicle_tag}/command/auto_conditioning_stop",
        )

    async def cancel_software_update(self, vehicle_tag: str | int) -> dict[str, Any]:
        """Cancels the countdown to install the vehicle software update."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{vehicle_tag}/command/cancel_software_update",
        )

    async def charge_max_range(self, vehicle_tag: str | int) -> dict[str, Any]:
        """Charges in max range mode -- we recommend limiting the use of this mode to long trips."""
        return await self._request(
            Method.POST, f"api/1/vehicles/{vehicle_tag}/command/charge_max_range"
        )

    async def charge_port_door_close(self, vehicle_tag: str | int) -> dict[str, Any]:
        """Closes the charge port door."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{vehicle_tag}/command/charge_port_door_close",
        )

    async def charge_port_door_open(self, vehicle_tag: str | int) -> dict[str, Any]:
        """Opens the charge port door."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{vehicle_tag}/command/charge_port_door_open",
        )

    async def charge_standard(self, vehicle_tag: str | int) -> dict[str, Any]:
        """Charges in Standard mode."""
        return await self._request(
            Method.POST, f"api/1/vehicles/{vehicle_tag}/command/charge_standard"
        )

    async def charge_start(self, vehicle_tag: str | int) -> dict[str, Any]:
        """Starts charging the vehicle."""
        return await self._request(
            Method.POST, f"api/1/vehicles/{vehicle_tag}/command/charge_start"
        )

    async def charge_stop(self, vehicle_tag: str | int) -> dict[str, Any]:
        """Stops charging the vehicle."""
        return await self._request(
            Method.POST, f"api/1/vehicles/{vehicle_tag}/command/charge_stop"
        )

    async def clear_pin_to_drive_admin(self, vehicle_tag: str | int):
        """Deactivates PIN to Drive and resets the associated PIN for vehicles running firmware versions 2023.44+. This command is only accessible to fleet managers or owners."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{vehicle_tag}/command/clear_pin_to_drive_admin",
        )

    async def door_lock(self, vehicle_tag: str | int) -> dict[str, Any]:
        """Locks the vehicle."""
        return await self._request(
            Method.POST, f"api/1/vehicles/{vehicle_tag}/command/door_lock"
        )

    async def door_unlock(self, vehicle_tag: str | int) -> dict[str, Any]:
        """Unlocks the vehicle."""
        return await self._request(
            Method.POST, f"api/1/vehicles/{vehicle_tag}/command/door_unlock"
        )

    async def erase_user_data(self, vehicle_tag: str | int) -> dict[str, Any]:
        """Erases user's data from the user interface. Requires the vehicle to be in park."""
        return await self._request(
            Method.POST, f"api/1/vehicles/{vehicle_tag}/command/erase_user_data"
        )

    async def flash_lights(self, vehicle_tag: str | int) -> dict[str, Any]:
        """Briefly flashes the vehicle headlights. Requires the vehicle to be in park."""
        return await self._request(
            Method.POST, f"api/1/vehicles/{vehicle_tag}/command/flash_lights"
        )

    async def guest_mode(self, vehicle_tag: str | int, enable: bool) -> dict[str, Any]:
        """Restricts certain vehicle UI functionality from guest users"""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{vehicle_tag}/command/guest_mode",
            json={"enable": enable},
        )

    async def honk_horn(self, vehicle_tag: str | int) -> dict[str, Any]:
        """Honks the vehicle horn. Requires the vehicle to be in park."""
        return await self._request(
            Method.POST, f"api/1/vehicles/{vehicle_tag}/command/honk_horn"
        )

    async def media_next_fav(self, vehicle_tag: str | int) -> dict[str, Any]:
        """Advances media player to next favorite track."""
        return await self._request(
            Method.POST, f"api/1/vehicles/{vehicle_tag}/command/media_next_fav"
        )

    async def media_next_track(self, vehicle_tag: str | int) -> dict[str, Any]:
        """Advances media player to next track."""
        return await self._request(
            Method.POST, f"api/1/vehicles/{vehicle_tag}/command/media_next_track"
        )

    async def media_prev_fav(self, vehicle_tag: str | int) -> dict[str, Any]:
        """Advances media player to previous favorite track."""
        return await self._request(
            Method.POST, f"api/1/vehicles/{vehicle_tag}/command/media_prev_fav"
        )

    async def media_prev_track(self, vehicle_tag: str | int) -> dict[str, Any]:
        """Advances media player to previous track."""
        return await self._request(
            Method.POST, f"api/1/vehicles/{vehicle_tag}/command/media_prev_track"
        )

    async def media_toggle_playback(self, vehicle_tag: str | int) -> dict[str, Any]:
        """Toggles current play/pause state."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{vehicle_tag}/command/media_toggle_playback",
        )

    async def media_volume_down(self, vehicle_tag: str | int) -> dict[str, Any]:
        """Turns the volume down by one."""
        return await self._request(
            Method.POST, f"api/1/vehicles/{vehicle_tag}/command/media_volume_down"
        )

    async def navigation_gps_request(
        self, vehicle_tag: str | int, lat: float, lon: float, order: int | None = None
    ) -> dict[str, Any]:
        """Start navigation to given coordinates. Order can be used to specify order of multiple stops."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{vehicle_tag}/command/navigation_gps_request",
            json={"lat": lat, "lon": lon, "order": order},
        )

    async def navigation_request(
        self, vehicle_tag: str | int, type: str, locale: str, timestamp_ms: str
    ) -> dict[str, Any]:
        """Sends a location to the in-vehicle navigation system."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{vehicle_tag}/command/navigation_request",
            json={"type": type, "locale": locale, "timestamp_ms": timestamp_ms},
        )

    async def navigation_sc_request(
        self, vehicle_tag: str | int, id: int, order: int | None = None
    ) -> dict[str, Any]:
        """Sends a location to the in-vehicle navigation system."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{vehicle_tag}/command/navigation_sc_request",
            json={"type": type, "id": id, "order": order},
        )

    async def remote_auto_seat_climate_request(
        self,
        vehicle_tag: str | int,
        auto_seat_position: int | Seat,
        auto_climate_on: bool,
    ) -> dict[str, Any]:
        """Sets automatic seat heating and cooling."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{vehicle_tag}/command/remote_auto_seat_climate_request",
            json={
                "auto_seat_position": auto_seat_position,
                "auto_climate_on": auto_climate_on,
            },
        )

    async def remote_auto_steering_wheel_heat_climate_request(
        self, vehicle_tag: str | int, on: bool
    ) -> dict[str, Any]:
        """Sets automatic steering wheel heating on/off."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{vehicle_tag}/command/remote_auto_steering_wheel_heat_climate_request",
            json={"on": on},
        )

    async def remote_boombox(
        self, vehicle_tag: str | int, sound: int
    ) -> dict[str, Any]:
        """Plays a sound through the vehicle external speaker."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{vehicle_tag}/command/remote_boombox",
            json={"sound": sound},
        )

    async def remote_seat_cooler_request(
        self,
        vehicle_tag: str | int,
        seat_position: Seat | int,
        seat_cooler_level: Level | int,
    ) -> dict[str, Any]:
        """Sets seat cooling."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{vehicle_tag}/command/remote_seat_cooler_request",
            json={
                "seat_position": seat_position,
                "seat_cooler_level": seat_cooler_level,
            },
        )

    async def remote_seat_heater_request(
        self,
        vehicle_tag: str | int,
        seat_position: Seat | int,
        seat_heater_level: Level | int,
    ) -> dict[str, Any]:
        """Sets seat heating."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{vehicle_tag}/command/remote_seat_heater_request",
            json={
                "heater": seat_position,
                "level": seat_heater_level,
            },
        )

    async def remote_start_drive(self, vehicle_tag: str | int) -> dict[str, Any]:
        """Starts the vehicle remotely. Requires keyless driving to be enabled."""
        return await self._request(
            Method.POST, f"api/1/vehicles/{vehicle_tag}/command/remote_start_drive"
        )

    async def remote_steering_wheel_heat_level_request(
        self, vehicle_tag: str | int, level: Level | int
    ) -> dict[str, Any]:
        """Sets steering wheel heat level."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{vehicle_tag}/command/remote_steering_wheel_heat_level_request",
            json={"level": level},
        )

    async def remote_steering_wheel_heater_request(
        self, vehicle_tag: str | int, on: bool
    ) -> dict[str, Any]:
        """Sets steering wheel heating on/off. For vehicles that do not support auto steering wheel heat."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{vehicle_tag}/command/remote_steering_wheel_heater_request",
            json={"on": on},
        )

    async def reset_pin_to_drive_pin(self, vehicle_tag: str | int) -> dict[str, Any]:
        """Removes PIN to Drive. Requires the car to be in Pin to Drive mode and not in Valet mode. Note that this only works if PIN to Drive is not active. This command also requires the Tesla Vehicle Command Protocol - for more information, please see refer to the documentation here."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{vehicle_tag}/command/reset_pin_to_drive_pin",
        )

    async def reset_valet_pin(self, vehicle_tag: str | int) -> dict[str, Any]:
        """Removes PIN for Valet Mode."""
        return await self._request(
            Method.POST, f"api/1/vehicles/{vehicle_tag}/command/reset_valet_pin"
        )

    async def schedule_software_update(
        self, vehicle_tag: str | int, offset_sec: int
    ) -> dict[str, Any]:
        """Schedules a vehicle software update (over the air "OTA") to be installed in the future."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{vehicle_tag}/command/schedule_software_update",
            json={"offset_sec": offset_sec},
        )

    async def set_bioweapon_mode(
        self, vehicle_tag: str | int, on: bool, manual_override: bool
    ) -> dict[str, Any]:
        """Turns Bioweapon Defense Mode on and off."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{vehicle_tag}/command/set_bioweapon_mode",
            json={"on": on, "manual_override": manual_override},
        )

    async def set_cabin_overheat_protection(
        self, vehicle_tag: str | int, on: bool, fan_only: bool
    ) -> dict[str, Any]:
        """Sets the vehicle overheat protection."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{vehicle_tag}/command/set_cabin_overheat_protection",
            json={"on": on, "fan_only": fan_only},
        )

    async def set_charge_limit(
        self, vehicle_tag: str | int, percent: int
    ) -> dict[str, Any]:
        """Sets the vehicle charge limit."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{vehicle_tag}/command/set_charge_limit",
            json={"percent": percent},
        )

    async def set_charging_amps(
        self, vehicle_tag: str | int, charging_amps: int
    ) -> dict[str, Any]:
        """Sets the vehicle charging amps."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{vehicle_tag}/command/set_charging_amps",
            json={"charging_amps": charging_amps},
        )

    async def set_climate_keeper_mode(
        self, vehicle_tag: str | int, climate_keeper_mode: ClimateKeeperMode | int
    ) -> dict[str, Any]:
        """Enables climate keeper mode."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{vehicle_tag}/command/set_climate_keeper_mode",
            json={"climate_keeper_mode": climate_keeper_mode},
        )

    async def set_cop_temp(
        self, vehicle_tag: str | int, cop_temp: CabinOverheatProtectionTemp | int
    ) -> dict[str, Any]:
        """Adjusts the Cabin Overheat Protection temperature (COP)."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{vehicle_tag}/command/set_cop_temp",
            json={"cop_temp": cop_temp},
        )

    async def set_pin_to_drive(
        self, vehicle_tag: str | int, on: bool, password: str | int
    ) -> dict[str, Any]:
        """Sets a four-digit passcode for PIN to Drive. This PIN must then be entered before the vehicle can be driven."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{vehicle_tag}/command/set_pin_to_drive",
            json={"on": on, "password": str(password)},
        )

    async def set_preconditioning_max(
        self, vehicle_tag: str | int, on: bool, manual_override: bool
    ) -> dict[str, Any]:
        """Sets an override for preconditioning — it should default to empty if no override is used."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{vehicle_tag}/command/set_preconditioning_max",
            json={"on": on, "manual_override": manual_override},
        )

    async def set_scheduled_charging(
        self, vehicle_tag: str | int, enable: bool, time: int
    ) -> dict[str, Any]:
        """Sets a time at which charging should be completed. The time parameter is minutes after midnight (e.g: time=120 schedules charging for 2:00am vehicle local time)."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{vehicle_tag}/command/set_scheduled_charging",
            json={"enable": enable, "time": time},
        )

    async def set_scheduled_departure(
        self,
        vehicle_tag: str | int,
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
            f"api/1/vehicles/{vehicle_tag}/command/set_scheduled_departure",
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

    async def set_sentry_mode(self, vehicle_tag: str | int, on: bool) -> dict[str, Any]:
        """Enables and disables Sentry Mode. Sentry Mode allows customers to watch the vehicle cameras live from the mobile app, as well as record sentry events."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{vehicle_tag}/command/set_sentry_mode",
            json={"on": on},
        )

    async def set_temps(
        self,
        vehicle_tag: str | int,
        driver_temp: float,
        passenger_temp: float,
    ) -> dict[str, Any]:
        """Sets the driver and/or passenger-side cabin temperature (and other zones if sync is enabled)."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{vehicle_tag}/command/set_temps",
            json={"driver_temp": driver_temp, "passenger_temp": passenger_temp},
        )

    async def set_valet_mode(
        self, vehicle_tag: str | int, on: bool, password: str | int
    ) -> dict[str, Any]:
        """Turns on Valet Mode and sets a four-digit passcode that must then be entered to disable Valet Mode."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{vehicle_tag}/command/set_valet_mode",
            json={"on": on, "password": str(password)},
        )

    async def set_vehicle_name(
        self, vehicle_tag: str | int, vehicle_name: str
    ) -> dict[str, Any]:
        """Changes the name of a vehicle. This command also requires the Tesla Vehicle Command Protocol - for more information, please see refer to the documentation here."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{vehicle_tag}/command/set_vehicle_name",
            json={"vehicle_name": vehicle_name},
        )

    async def speed_limit_activate(
        self, vehicle_tag: str | int, pin: str | int
    ) -> dict[str, Any]:
        """Activates Speed Limit Mode with a four-digit PIN."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{vehicle_tag}/command/speed_limit_activate",
            json={"pin": str(pin)},
        )

    async def speed_limit_clear_pin(
        self, vehicle_tag: str | int, pin: str | int
    ) -> dict[str, Any]:
        """Deactivates Speed Limit Mode and resets the associated PIN."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{vehicle_tag}/command/speed_limit_clear_pin",
            json={"pin": str(pin)},
        )

    async def speed_limit_clear_pin_admin(
        self, vehicle_tag: str | int
    ) -> dict[str, Any]:
        """Deactivates Speed Limit Mode and resets the associated PIN for vehicles running firmware versions 2023.38+. This command is only accessible to fleet managers or owners."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{vehicle_tag}/command/speed_limit_clear_pin_admin",
        )

    async def speed_limit_deactivate(
        self, vehicle_tag: str | int, pin: str | int
    ) -> dict[str, Any]:
        """Deactivates Speed Limit Mode."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{vehicle_tag}/command/speed_limit_deactivate",
            json={"pin": str(pin)},
        )

    async def speed_limit_set_limit(
        self, vehicle_tag: str | int, limit_mph: int
    ) -> dict[str, Any]:
        """Sets the maximum speed allowed when Speed Limit Mode is active."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{vehicle_tag}/command/speed_limit_set_limit",
            json={"limit_mph": limit_mph},
        )

    async def sun_roof_control(
        self, vehicle_tag: str | int, state: str | SunRoofCommand
    ) -> dict[str, Any]:
        """Controls the panoramic sunroof on the Model S."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{vehicle_tag}/command/sun_roof_control",
            json={"state": state},
        )

    async def take_drivenote(self, vehicle_tag: str | int, note: str) -> dict[str, Any]:
        """Records a drive note. The note parameter is truncated to 80 characters in length."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{vehicle_tag}/command/take_drivenote",
            json={"note": note},
        )

    async def trigger_homelink(
        self,
        vehicle_tag: str | int,
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
            f"api/1/vehicles/{vehicle_tag}/command/trigger_homelink",
            json=data,
        )

    async def upcoming_calendar_entries(
        self, vehicle_tag: str | int, calendar_data: str
    ) -> dict[str, Any]:
        """Upcoming calendar entries stored on the vehicle."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{vehicle_tag}/command/upcoming_calendar_entries",
            json={"calendar_data": calendar_data},
        )

    async def window_control(
        self,
        vehicle_tag: str | int,
        command: str | WindowCommand,
        lat: float | None = None,
        lon: float | None = None,
    ) -> dict[str, Any]:
        """Control the windows of a parked vehicle. Supported commands: vent and close. When closing, specify lat and lon of user to ensure they are within range of vehicle (unless this is an M3 platform vehicle)."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{vehicle_tag}/command/window_control",
            json={"lat": lat, "lon": lon, "command": command},
        )

    async def drivers(self, vehicle_tag: str | int) -> dict[str, Any]:
        """Returns all allowed drivers for a vehicle. This endpoint is only available for the vehicle owner."""
        return await self._request(Method.GET, f"api/1/vehicles/{vehicle_tag}/drivers")

    async def drivers_remove(
        self, vehicle_tag: str | int, share_user_id: str | int | None = None
    ) -> dict[str, Any]:
        """Removes driver access from a vehicle. Share users can only remove their own access. Owners can remove share access or their own."""
        return await self._request(
            Method.DELETE,
            f"api/1/vehicles/{vehicle_tag}/drivers",
            {"share_user_id": share_user_id},
        )

    async def list(
        self, page: int | None = None, per_page: int | None = None
    ) -> dict[str, Any]:
        """Returns vehicles belonging to the account."""
        return await self._request(
            Method.GET, "api/1/vehicles", {"page": page, "per_page": per_page}
        )

    async def mobile_enabled(self, vehicle_tag: str | int) -> dict[str, Any]:
        """Returns whether or not mobile access is enabled for the vehicle."""
        return await self._request(
            Method.GET, f"api/1/vehicles/{vehicle_tag}/mobile_enabled"
        )

    async def nearby_charging_sites(
        self,
        vehicle_tag: str | int,
        count: int | None = None,
        radius: int | None = None,
        detail: bool | None = None,
    ) -> dict[str, Any]:
        """Returns the charging sites near the current location of the vehicle."""
        return await self._request(
            Method.GET,
            f"api/1/vehicles/{vehicle_tag}/nearby_charging_sites",
            {"count": count, "radius": radius, "detail": detail},
        )

    async def options(self, vin: str) -> dict[str, Any]:
        """Returns vehicle option details."""
        return await self._request(
            Method.GET, "api/1/dx/vehicles/options", {"vin": vin}
        )

    async def recent_alerts(self, vehicle_tag: str | int) -> dict[str, Any]:
        """List of recent alerts"""
        return await self._request(
            Method.GET, f"api/1/vehicles/{vehicle_tag}/recent_alerts"
        )

    async def release_notes(
        self,
        vehicle_tag: str | int,
        staged: bool | None = None,
        language: int | None = None,
    ) -> dict[str, Any]:
        """Returns firmware release notes."""
        return await self._request(
            Method.GET,
            f"api/1/vehicles/{vehicle_tag}/release_notes",
            {"staged": staged, "language": language},
        )

    async def service_data(self, vehicle_tag: str | int) -> dict[str, Any]:
        """Returns service data."""
        return await self._request(
            Method.GET, f"api/1/vehicles/{vehicle_tag}/service_data"
        )

    async def share_invites(self, vehicle_tag: str | int) -> dict[str, Any]:
        """Returns the share invites for a vehicle."""
        return await self._request(
            Method.GET, f"api/1/vehicles/{vehicle_tag}/invitations"
        )

    async def share_invites_create(self, vehicle_tag: str | int) -> dict[str, Any]:
        """Creates a share invite for a vehicle."""
        return await self._request(
            Method.POST, f"api/1/vehicles/{vehicle_tag}/invitations"
        )

    async def share_invites_redeem(self, code: str) -> dict[str, Any]:
        """Redeems a share invite."""
        return await self._request(
            Method.POST, "api/1/invitations/redeem", {code: code}
        )

    async def share_invites_revoke(
        self, vehicle_tag: str | int, id: str
    ) -> dict[str, Any]:
        """Revokes a share invite."""
        return await self._request(
            Method.POST, f"api/1/vehicles/{vehicle_tag}/invitations/{id}/revoke"
        )

    async def signed_command(
        self, vehicle_tag: str | int, routable_message: str
    ) -> dict[str, Any]:
        """Signed Commands is a generic endpoint replacing legacy commands."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{vehicle_tag}/signed_command",
            json={"routable_message": routable_message},
        )

    async def vehicle(self, vehicle_tag: str | int) -> dict[str, Any]:
        """Returns information about a vehicle."""
        return await self._request(Method.GET, f"api/1/vehicles/{vehicle_tag}")

    async def vehicle_data(
        self,
        vehicle_tag: str | int,
        endpoints: List[VehicleDataEndpoint | str] | None = None,
    ) -> dict[str, Any]:
        """Makes a live call to the vehicle. This may return cached data if the vehicle is offline. For vehicles running firmware versions 2023.38+, location_data is required to fetch vehicle location. This will result in a location sharing icon to show on the vehicle UI."""
        endpoint_payload = ";".join(endpoints) if endpoints else None
        return await self._request(
            Method.GET,
            f"api/1/vehicles/{vehicle_tag}/vehicle_data",
            {"endpoints": endpoint_payload},
        )

    async def wake_up(self, vehicle_tag: str | int) -> dict[str, Any]:
        """Wakes the vehicle from sleep, which is a state to minimize idle energy consumption."""
        return await self._request(Method.POST, f"api/1/vehicles/{vehicle_tag}/wake_up")

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

    async def fleet_telemetry_config_get(
        self, vehicle_tag: str | int
    ) -> dict[str, Any]:
        """Configures fleet telemetry."""
        return await self._request(
            Method.GET, f"api/1/vehicles/{vehicle_tag}/fleet_telemetry_config"
        )

    async def fleet_telemetry_config_delete(
        self, vehicle_tag: str | int
    ) -> dict[str, Any]:
        """Configures fleet telemetry."""
        return await self._request(
            Method.DELETE, f"api/1/vehicles/{vehicle_tag}/fleet_telemetry_config"
        )
