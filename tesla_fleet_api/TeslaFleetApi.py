import aiohttp
from .exceptions import raise_for_status
from typing import Any
from enum import StrEnum, IntEnum


# Based on https://developer.tesla.com/docs/fleet-api
class TeslaFleetApi:
    """Class describing the Tesla Fleet API."""

    server: str
    session: aiohttp.ClientSession
    headers: dict[str, str]
    raise_for_status: bool

    def __init__(
        self,
        access_token: str,
        server: str,
        session: aiohttp.ClientSession,
        raise_for_status: bool = True,
    ):
        """Initialize the Tesla Fleet API."""
        self.server = server
        self.session = session
        self.headers = {"Authorization": f"Bearer {access_token}"}
        self.raise_for_status = raise_for_status

        self.user = self.User(self)
        self.charging = self.Charging(self)
        self.partner = self.Partner(self)
        self.vehicle = self.Vehicle(self)

    async def _get(self, path, params: dict[str:Any] | None = None):
        """Get data from the Tesla Fleet API."""
        if params:
            params = {k: v for k, v in params.items() if v is not None}

        async with self.session.get(
            f"{self.server}/{path}",
            params=params,
            headers=self.headers,
        ) as resp:
            if self.raise_for_status:
                await raise_for_status(resp)
            return await resp.json()

    async def _post(self, path, data: dict):
        """Post data to the Tesla Fleet API with URL encoded data."""

        async with self.session.post(
            f"{self.server}/{path}",
            headers=self.headers,
            data=data,
        ) as resp:
            if self.raise_for_status:
                await raise_for_status(resp)
            return await resp.json()

    async def status(self):
        """This endpoint returns the string "ok" if the API is operating normally. No HTTP headers are required."""
        async with self.session.get(f"{self.server}/status") as resp:
            return await resp.text()

    class Charging:
        """Class describing the Tesla Fleet API charging endpoints."""

        def __init__(self, parent):
            self._get = parent._get
            self._post = parent._post

        async def history(
            self,
            vin: str | None = None,
            startTime: str | None = None,
            endTime: str | None = None,
            pageNo: int | None = None,
            pageSize: int | None = None,
            sortBy: str | None = None,
            sortOrder: str | None = None,
        ) -> dict[str, Any]:
            """Returns the paginated charging history."""
            return await self._get(
                "/api/1/dx/charging/history",
                {vin, startTime, endTime, pageNo, pageSize, sortBy, sortOrder},
            )

        async def sessions(
            self,
            vin: str | None = None,
            date_from: str | None = None,
            date_to: str | None = None,
            limit: int | None = None,
            offset: int | None = None,
        ) -> dict[str, Any]:
            """Returns the charging session information including pricing and energy data. This endpoint is only available for business accounts that own a fleet of vehicles."""
            return await self._get(
                "/api/1/dx/charging/sessions", {vin, date_from, date_to, limit, offset}
            )

    class Partner:
        """Class describing the Tesla Fleet API partner endpoints"""

        def __init__(self, parent):
            self._get = parent._get
            self._post = parent._post

        async def public_key(self, domain: str | None = None) -> dict[str, Any]:
            """Returns the public key associated with a domain. It can be used to ensure the registration was successful."""
            return await self._get("/api/1/partner_accounts/public_key", {domain})

        async def register(self, domain: str) -> dict[str, Any]:
            """Registers an existing account before it can be used for general API access. Each application from developer.tesla.com must complete this step."""
            return await self._post("/api/1/partner_accounts", {domain})

    class User:
        """Class describing the Tesla Fleet API user endpoints"""

        def __init__(self, parent):
            self._get = parent._get
            self._post = parent._post

        async def backup_key(self) -> dict[str, Any]:
            """Returns the public key associated with the user."""
            return await self._get("/api/1/users/backup_key")

        async def feature_config(self) -> dict[str, Any]:
            """Returns any custom feature flag applied to a user."""
            return await self._get("/api/1/users/feature_config")

        async def me(self) -> dict[str, Any]:
            """Returns a summary of a user's account."""
            return await self._get("/api/1/users/me")

        async def orders(self) -> dict[str, Any]:
            """Returns the active orders for a user."""
            return await self._get("/api/1/users/orders")

        async def region(self) -> dict[str, Any]:
            """Returns a user's region and appropriate fleet-api base URL. Accepts no parameters, response is based on the authentication token subject."""
            return await self._get("/api/1/users/region")

    class Vehicle:
        """Class describing the Tesla Fleet API vehicle endpoints and commands."""

        def __init__(self, parent):
            self._get = parent._get
            self._post = parent._post

        class Trunk(StrEnum):
            """Trunk options"""

            FRONT: "front"
            REAR: "rear"

        async def actuate_trunk(
            self, vehicle_tag: str | int, which_trunk: Trunk | str
        ) -> dict[str, Any]:
            """Controls the front or rear trunk."""
            return await self._post(
                f"/api/1/vehicles/{vehicle_tag}/command/actuate_trunk", {which_trunk}
            )

        async def adjust_volume(
            self, vehicle_tag: str | int, volume: float
        ) -> dict[str, Any]:
            """Adjusts vehicle media playback volume."""
            if volume < 0.0 or volume > 11.0:
                raise ValueError("Volume must a number from 0.0 to 11.0")
            return await self._post(
                f"/api/1/vehicles/{vehicle_tag}/command/adjust_volume", {volume}
            )

        async def auto_conditioning_start(
            self, vehicle_tag: str | int
        ) -> dict[str, Any]:
            """Starts climate preconditioning."""
            return await self._post(
                f"/api/1/vehicles/{vehicle_tag}/command/auto_conditioning_start"
            )

        async def auto_conditioning_stop(
            self, vehicle_tag: str | int
        ) -> dict[str, Any]:
            """Stops climate preconditioning."""
            return await self._post(
                f"/api/1/vehicles/{vehicle_tag}/command/auto_conditioning_stop"
            )

        async def cancel_software_update(
            self, vehicle_tag: str | int
        ) -> dict[str, Any]:
            """Cancels the countdown to install the vehicle software update. This operation will no longer work after the vehicle begins the software installation."""
            return await self._post(
                f"/api/1/vehicles/{vehicle_tag}/command/cancel_software_update"
            )

        async def charge_max_range(self, vehicle_tag: str | int) -> dict[str, Any]:
            """Charges in max range mode -- we recommend limiting the use of this mode to long trips."""
            return await self._post(
                f"/api/1/vehicles/{vehicle_tag}/command/charge_max_range"
            )

        async def charge_port_door_close(
            self, vehicle_tag: str | int
        ) -> dict[str, Any]:
            """Closes the charge port door."""
            return await self._post(
                f"/api/1/vehicles/{vehicle_tag}/command/charge_port_door_close"
            )

        async def charge_port_door_open(self, vehicle_tag: str | int) -> dict[str, Any]:
            """Opens the charge port door."""
            return await self._post(
                f"/api/1/vehicles/{vehicle_tag}/command/charge_port_door_open"
            )

        async def charge_standard(self, vehicle_tag: str | int) -> dict[str, Any]:
            """Charges in Standard mode."""
            return await self._post(
                f"/api/1/vehicles/{vehicle_tag}/command/charge_standard"
            )

        async def charge_start(self, vehicle_tag: str | int) -> dict[str, Any]:
            """Starts charging the vehicle."""
            return await self._post(
                f"/api/1/vehicles/{vehicle_tag}/command/charge_start"
            )

        async def charge_stop(self, vehicle_tag: str | int) -> dict[str, Any]:
            """Stops charging the vehicle."""
            return await self._post(
                f"/api/1/vehicles/{vehicle_tag}/command/charge_stop"
            )

        async def clear_pin_to_drive_admin(self, vehicle_tag: str | int):
            """Deactivates PIN to Drive and resets the associated PIN for vehicles running firmware versions 2023.44+. This command is only accessible to fleet managers or owners."""
            return await self._post(
                f"/api/1/vehicles/{vehicle_tag}/command/clear_pin_to_drive_admin"
            )

        async def door_lock(self, vehicle_tag: str | int) -> dict[str, Any]:
            """Locks the vehicle."""
            return await self._post(f"/api/1/vehicles/{vehicle_tag}/command/door_lock")

        async def door_unlock(self, vehicle_tag: str | int) -> dict[str, Any]:
            """Unlocks the vehicle."""
            return await self._post(
                f"/api/1/vehicles/{vehicle_tag}/command/door_unlock"
            )

        async def erase_user_data(self, vehicle_tag: str | int) -> dict[str, Any]:
            """Erases user's data from the user interface. Requires the vehicle to be in park."""
            return await self._post(
                f"/api/1/vehicles/{vehicle_tag}/command/erase_user_data"
            )

        async def flash_lights(self, vehicle_tag: str | int) -> dict[str, Any]:
            """Briefly flashes the vehicle headlights. Requires the vehicle to be in park."""
            return await self._post(
                f"/api/1/vehicles/{vehicle_tag}/command/flash_lights"
            )

        async def guest_mode(
            self, vehicle_tag: str | int, enable: bool
        ) -> dict[str, Any]:
            """Restricts certain vehicle UI functionality from guest users"""
            return await self._post(
                f"/api/1/vehicles/{vehicle_tag}/command/guest_mode", {enable}
            )

        async def honk_horn(self, vehicle_tag: str | int) -> dict[str, Any]:
            """Honks the vehicle horn. Requires the vehicle to be in park."""
            return await self._post(f"/api/1/vehicles/{vehicle_tag}/command/honk_horn")

        async def media_next_fav(self, vehicle_tag: str | int) -> dict[str, Any]:
            """Advances media player to next favorite track."""
            return await self._post(
                f"/api/1/vehicles/{vehicle_tag}/command/media_next_fav"
            )

        async def media_next_track(self, vehicle_tag: str | int) -> dict[str, Any]:
            """Advances media player to next track."""
            return await self._post(
                f"/api/1/vehicles/{vehicle_tag}/command/media_next_track"
            )

        async def media_prev_fav(self, vehicle_tag: str | int) -> dict[str, Any]:
            """Advances media player to previous favorite track."""
            return await self._post(
                f"/api/1/vehicles/{vehicle_tag}/command/media_prev_fav"
            )

        async def media_prev_track(self, vehicle_tag: str | int) -> dict[str, Any]:
            """Advances media player to previous track."""
            return await self._post(
                f"/api/1/vehicles/{vehicle_tag}/command/media_prev_track"
            )

        async def media_toggle_playback(self, vehicle_tag: str | int) -> dict[str, Any]:
            """Toggles current play/pause state."""
            return await self._post(
                f"/api/1/vehicles/{vehicle_tag}/command/media_toggle_playback"
            )

        async def media_volume_down(self, vehicle_tag: str | int) -> dict[str, Any]:
            """Turns the volume down by one."""
            return await self._post(
                f"/api/1/vehicles/{vehicle_tag}/command/media_volume_down"
            )

        async def navigation_gps_request(
            self, vehicle_tag: str | int, lat: float, lon: float, order: int
        ) -> dict[str, Any]:
            """Start navigation to given coordinates. Order can be used to specify order of multiple stops."""
            return await self._post(
                f"/api/1/vehicles/{vehicle_tag}/command/navigation_gps_request",
                {lat, lon, order},
            )

        async def navigation_request(
            self, vehicle_tag: str | int, type: str, locale: str, timestamp_ms: str
        ) -> dict[str, Any]:
            """Sends a location to the in-vehicle navigation system."""
            return await self._post(
                f"/api/1/vehicles/{vehicle_tag}/command/navigation_request",
                {type, locale, timestamp_ms},
            )

        async def navigation_sc_request(
            self, vehicle_tag: str | int, id: int, order: int
        ) -> dict[str, Any]:
            """Sends a location to the in-vehicle navigation system."""
            return await self._post(
                f"/api/1/vehicles/{vehicle_tag}/command/navigation_sc_request",
                {type, id, order},
            )

        async def remote_auto_seat_climate_request(
            self, vehicle_tag: str | int, auto_seat_position: int, auto_climate_on: bool
        ) -> dict[str, Any]:
            """Sets automatic seat heating and cooling."""
            return await self._post(
                f"/api/1/vehicles/{vehicle_tag}/command/remote_auto_seat_climate_request",
                {auto_seat_position, auto_climate_on},
            )

        async def remote_auto_steering_wheel_heat_climate_request(
            self, vehicle_tag: str | int, on: bool
        ) -> dict[str, Any]:
            """Sets automatic steering wheel heating on/off."""
            return await self._post(
                f"/api/1/vehicles/{vehicle_tag}/command/remote_auto_steering_wheel_heat_climate_request",
                {on},
            )

        async def remote_boombox(
            self, vehicle_tag: str | int, sound: int
        ) -> dict[str, Any]:
            """Plays a sound through the vehicle external speaker."""
            return await self._post(
                f"/api/1/vehicles/{vehicle_tag}/command/remote_boombox", {sound}
            )

        async def remote_seat_cooler_request(
            self, vehicle_tag: str | int, seat_position: int, seat_cooler_level: int
        ) -> dict[str, Any]:
            """Sets seat cooling."""
            return await self._post(
                f"/api/1/vehicles/{vehicle_tag}/command/remote_seat_cooler_request",
                {seat_position, seat_cooler_level},
            )

        async def remote_seat_heater_request(
            self, vehicle_tag: str | int
        ) -> dict[str, Any]:
            """Sets seat heating."""
            return await self._post(
                f"/api/1/vehicles/{vehicle_tag}/command/remote_seat_heater_request"
            )

        async def remote_start_drive(self, vehicle_tag: str | int) -> dict[str, Any]:
            """Starts the vehicle remotely. Requires keyless driving to be enabled."""
            return await self._post(
                f"/api/1/vehicles/{vehicle_tag}/command/remote_start_drive"
            )

        async def remote_steering_wheel_heat_level_request(
            self, vehicle_tag: str | int, level: int
        ) -> dict[str, Any]:
            """Sets steering wheel heat level."""
            return await self._post(
                f"/api/1/vehicles/{vehicle_tag}/command/remote_steering_wheel_heat_level_request",
                {level},
            )

        async def remote_steering_wheel_heater_request(
            self, vehicle_tag: str | int, on: bool
        ) -> dict[str, Any]:
            """Sets steering wheel heating on/off. For vehicles that do not support auto steering wheel heat."""
            return await self._post(
                f"/api/1/vehicles/{vehicle_tag}/command/remote_steering_wheel_heater_request",
                {on},
            )

        async def reset_pin_to_drive_pin(
            self, vehicle_tag: str | int
        ) -> dict[str, Any]:
            """Removes PIN to Drive. Requires the car to be in Pin to Drive mode and not in Valet mode. Note that this only works if PIN to Drive is not active. This command also requires the Tesla Vehicle Command Protocol - for more information, please see refer to the documentation here."""
            return await self._post(
                f"/api/1/vehicles/{vehicle_tag}/command/reset_pin_to_drive_pin"
            )

        async def reset_valet_pin(self, vehicle_tag: str | int) -> dict[str, Any]:
            """Removes PIN for Valet Mode."""
            return await self._post(
                f"/api/1/vehicles/{vehicle_tag}/command/reset_valet_pin"
            )

        async def schedule_software_update(
            self, vehicle_tag: str | int, offset_sec: int
        ) -> dict[str, Any]:
            """Schedules a vehicle software update (over the air "OTA") to be installed in the future."""
            return await self._post(
                f"/api/1/vehicles/{vehicle_tag}/command/schedule_software_update",
                {offset_sec},
            )

        async def set_bioweapon_mode(
            self, vehicle_tag: str | int, on: bool, manual_override: bool
        ) -> dict[str, Any]:
            """Turns Bioweapon Defense Mode on and off."""
            return await self._post(
                f"/api/1/vehicles/{vehicle_tag}/command/set_bioweapon_mode",
                {on, manual_override},
            )

        async def set_cabin_overheat_protection(
            self, vehicle_tag: str | int, on: bool, fan_only: bool
        ) -> dict[str, Any]:
            """Sets the vehicle overheat protection."""
            return await self._post(
                f"/api/1/vehicles/{vehicle_tag}/command/set_cabin_overheat_protection",
                {on, fan_only},
            )

        async def set_charge_limit(
            self, vehicle_tag: str | int, percent: int
        ) -> dict[str, Any]:
            """Sets the vehicle charge limit."""
            return await self._post(
                f"/api/1/vehicles/{vehicle_tag}/command/set_charge_limit", {percent}
            )

        async def set_charging_amps(
            self, vehicle_tag: str | int, charging_amps: int
        ) -> dict[str, Any]:
            """Sets the vehicle charging amps."""
            return await self._post(
                f"/api/1/vehicles/{vehicle_tag}/command/set_charging_amps",
                {charging_amps},
            )

        class ClimateKeeperMode(IntEnum):
            """Climate Keeper Mode options"""

            OFF = 0
            KEEP_MODE = 1
            DOG_MODE = 2
            CAMP_MODE = 3

        async def set_climate_keeper_mode(
            self, vehicle_tag: str | int, climate_keeper_mode: ClimateKeeperMode | int
        ) -> dict[str, Any]:
            """Enables climate keeper mode."""
            return await self._post(
                f"/api/1/vehicles/{vehicle_tag}/command/set_climate_keeper_mode",
                {climate_keeper_mode},
            )

        class CopTemp(IntEnum):
            """COP Temp options"""

            LOW = 0  # 30C 90F
            MEDIUM = 1  # 35C 95F
            HIGH = 2  # 40C 100F

        async def set_cop_temp(
            self, vehicle_tag: str | int, cop_temp: CopTemp | int
        ) -> dict[str, Any]:
            """Adjusts the Cabin Overheat Protection temperature (COP)."""
            return await self._post(
                f"/api/1/vehicles/{vehicle_tag}/command/set_cop_temp", {cop_temp}
            )

        async def set_pin_to_drive(
            self, vehicle_tag: str | int, on: bool, password: str | int
        ) -> dict[str, Any]:
            """Sets a four-digit passcode for PIN to Drive. This PIN must then be entered before the vehicle can be driven."""
            return await self._post(
                f"/api/1/vehicles/{vehicle_tag}/command/set_pin_to_drive",
                {on, str(password)},
            )

        async def set_preconditioning_max(
            self, vehicle_tag: str | int, on: bool, manual_override: bool
        ) -> dict[str, Any]:
            """Sets an override for preconditioning — it should default to empty if no override is used."""
            return await self._post(
                f"/api/1/vehicles/{vehicle_tag}/command/set_preconditioning_max",
                {on, manual_override},
            )

        async def set_scheduled_charging(
            self, vehicle_tag: str | int, enable: bool, time: int
        ) -> dict[str, Any]:
            """Sets a time at which charging should be completed. The time parameter is minutes after midnight (e.g: time=120 schedules charging for 2:00am vehicle local time)."""
            return await self._post(
                f"/api/1/vehicles/{vehicle_tag}/command/set_scheduled_charging",
                {enable, time},
            )

        async def set_scheduled_departure(
            self, vehicle_tag: str | int, enable: bool, time: int
        ) -> dict[str, Any]:
            """Sets a time at which departure should be completed. The time parameter is minutes after midnight (e.g: time=120 schedules departure for 2:00am vehicle local time)."""
            return await self._post(
                f"/api/1/vehicles/{vehicle_tag}/command/set_scheduled_departure",
                {enable, time},
            )

        async def set_sentry_mode(
            self, vehicle_tag: str | int, on: bool
        ) -> dict[str, Any]:
            """Enables and disables Sentry Mode. Sentry Mode allows customers to watch the vehicle cameras live from the mobile app, as well as record sentry events."""
            return await self._post(
                f"/api/1/vehicles/{vehicle_tag}/command/set_sentry_mode", {on}
            )

        async def set_temps(
            self, vehicle_tag: str | int, driver_temp: int, passenger_temp: int
        ) -> dict[str, Any]:
            """Sets the driver and/or passenger-side cabin temperature (and other zones if sync is enabled)."""
            return await self._post(
                f"/api/1/vehicles/{vehicle_tag}/command/set_temps",
                {driver_temp, passenger_temp},
            )

        async def set_valet_mode(
            self, vehicle_tag: str | int, on: bool, password: str | int
        ) -> dict[str, Any]:
            """Turns on Valet Mode and sets a four-digit passcode that must then be entered to disable Valet Mode."""
            return await self._post(
                f"/api/1/vehicles/{vehicle_tag}/command/set_valet_mode",
                {on, str(password)},
            )

        async def set_vehicle_name(
            self, vehicle_tag: str | int, vehicle_name: str
        ) -> dict[str, Any]:
            """Changes the name of a vehicle. This command also requires the Tesla Vehicle Command Protocol - for more information, please see refer to the documentation here."""
            return await self._post(
                f"/api/1/vehicles/{vehicle_tag}/command/set_vehicle_name",
                {vehicle_name},
            )

        async def speed_limit_activate(
            self, vehicle_tag: str | int, pin: str | int
        ) -> dict[str, Any]:
            """Activates Speed Limit Mode with a four-digit PIN."""
            return await self._post(
                f"/api/1/vehicles/{vehicle_tag}/command/speed_limit_activate",
                {str(pin)},
            )

        async def speed_limit_clear_pin(
            self, vehicle_tag: str | int, pin: str | int
        ) -> dict[str, Any]:
            """Deactivates Speed Limit Mode and resets the associated PIN."""
            return await self._post(
                f"/api/1/vehicles/{vehicle_tag}/command/speed_limit_clear_pin",
                {str(pin)},
            )

        async def speed_limit_clear_pin_admin(
            self, vehicle_tag: str | int
        ) -> dict[str, Any]:
            """Deactivates Speed Limit Mode and resets the associated PIN for vehicles running firmware versions 2023.38+. This command is only accessible to fleet managers or owners."""
            return await self._post(
                f"/api/1/vehicles/{vehicle_tag}/command/speed_limit_clear_pin_admin"
            )

        async def speed_limit_deactivate(
            self, vehicle_tag: str | int, pin: str | int
        ) -> dict[str, Any]:
            """Deactivates Speed Limit Mode."""
            return await self._post(
                f"/api/1/vehicles/{vehicle_tag}/command/speed_limit_deactivate",
                {str(pin)},
            )

        async def speed_limit_set_limit(
            self, vehicle_tag: str | int, limit_mph: int
        ) -> dict[str, Any]:
            """Sets the maximum speed allowed when Speed Limit Mode is active."""
            return await self._post(
                f"/api/1/vehicles/{vehicle_tag}/command/speed_limit_set_limit",
                {limit_mph},
            )

        class SunRoof(StrEnum):
            """Sunroof options"""

            STOP = "stop"
            CLOSE = "close"
            VENT = "vent"

        async def sun_roof_control(
            self, vehicle_tag: str | int, state: str | SunRoof
        ) -> dict[str, Any]:
            """Controls the panoramic sunroof on the Model S."""
            return await self._post(
                f"/api/1/vehicles/{vehicle_tag}/command/sun_roof_control", {state}
            )

        async def take_drivenote(
            self, vehicle_tag: str | int, note: str
        ) -> dict[str, Any]:
            """Records a drive note. The note parameter is truncated to 80 characters in length."""
            return await self._post(
                f"/api/1/vehicles/{vehicle_tag}/command/take_drivenote", {note}
            )

        async def trigger_homelink(
            self, vehicle_tag: str | int, lat: float, lon: float, token: str
        ) -> dict[str, Any]:
            """Turns on HomeLink (used to open and close garage doors)."""
            return await self._post(
                f"/api/1/vehicles/{vehicle_tag}/command/trigger_homelink",
                {lat, lon, token},
            )

        async def upcoming_calendar_entries(
            self, vehicle_tag: str | int, calendar_data: str
        ) -> dict[str, Any]:
            """Upcoming calendar entries stored on the vehicle."""
            return await self._post(
                f"/api/1/vehicles/{vehicle_tag}/command/upcoming_calendar_entries",
                {calendar_data},
            )

        class WindowControl(StrEnum):
            """Window Control options"""

            VENT = "vent"
            CLOSE = "close"

        async def window_control(
            self,
            vehicle_tag: str | int,
            lat: float,
            lon: float,
            command: str | WindowControl,
        ) -> dict[str, Any]:
            """Control the windows of a parked vehicle. Supported commands: vent and close. When closing, specify lat and lon of user to ensure they are within range of vehicle (unless this is an M3 platform vehicle)."""
            return await self._post(
                f"/api/1/vehicles/{vehicle_tag}/command/window_control",
                {lat, lon, command},
            )
