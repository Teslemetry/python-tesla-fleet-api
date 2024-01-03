import aiohttp
from .exceptions import raise_for_status, TeslaFleetError
from typing import Any
from enum import StrEnum, IntEnum
from .const import SERVERS

GET = "GET"
POST = "POST"
DELETE = "DELETE"


# Based on https://developer.tesla.com/docs/fleet-api
class TeslaFleetApi:
    """Class describing the Tesla Fleet API."""

    server: str
    session: aiohttp.ClientSession
    headers: dict[str, str]
    raise_for_status: bool

    def __init__(
        self,
        session: aiohttp.ClientSession,
        access_token: str,
        use_command_protocol: bool = False,
        region: str | None = None,
        server: str | None = None,
        raise_for_status: bool = True,
    ):
        """Initialize the Tesla Fleet API."""

        self.session = session
        self.access_token = access_token
        self.use_command_protocol = use_command_protocol

        if region and not server and region not in SERVERS:
            raise ValueError(f"Region must be one of {", ".join(SERVERS.keys())}")
        self.server = server or SERVERS.get(region)
        self.raise_for_status = raise_for_status

        self.user = self.User(self)
        self.charging = self.Charging(self)
        self.partner = self.Partner(self)
        self.vehicle = self.Vehicle(self)

    async def find_server(self) -> None:
        """Find the server URL for the Tesla Fleet API."""
        for server in SERVERS.values():
            self.server = server
            try:
                await self.user.region()
                return
            except TeslaFleetError.Base:
                print(f"not {server}")
                continue
        raise TeslaFleetError.Base("Could not find a valid server.")

    async def _request(
        self,
        method: str,
        path: str,
        data: dict[str:Any] | None = None,
        json: dict[str:Any] | None = None,
        params: dict[str:Any] | None = None,
    ):
        """Send a request to the Tesla Fleet API."""

        if not self.server:
            raise ValueError("Server was not set at init. Call find_server() first.")

        if data:
            data = {k: v for k, v in data.items() if v is not None}
        if json:
            json = {k: v for k, v in json.items() if v is not None}
        if params:
            params = {k: v for k, v in params.items() if v is not None}

        async with self.session.request(
            method,
            f"{self.server}/{path}",
            headers={
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json",
            },
            data=data,
            json=json,
            params=params,
        ) as resp:
            if self.raise_for_status:
                await raise_for_status(resp)
            return await resp.json()

    async def status(self):
        """This endpoint returns the string "ok" if the API is operating normally. No HTTP headers are required."""
        if not self.server:
            raise ValueError("Server was not set at init. Call find_server() first.")
        async with self.session.get(f"{self.server}/status") as resp:
            return await resp.text()

    class Charging:
        """Class describing the Tesla Fleet API charging endpoints."""

        def __init__(self, parent):
            self._request = parent._request

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
            return await self._request(
                GET,
                "api/1/dx/charging/history",
                {
                    vin: vin,
                    startTime: startTime,
                    endTime: endTime,
                    pageNo: pageNo,
                    pageSize: pageSize,
                    sortBy: sortBy,
                    sortOrder: sortOrder,
                },
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
            return await self._request(
                GET,
                "api/1/dx/charging/sessions",
                {
                    vin: vin,
                    date_from: date_from,
                    date_to: date_to,
                    limit: limit,
                    offset: offset,
                },
            )

    class Partner:
        """Class describing the Tesla Fleet API partner endpoints"""

        def __init__(self, parent):
            self._request = parent._request

        async def public_key(self, domain: str | None = None) -> dict[str, Any]:
            """Returns the public key associated with a domain. It can be used to ensure the registration was successful."""
            return await self._request(
                GET, "api/1/partner_accounts/public_key", data={domain: domain}
            )

        async def register(self, domain: str) -> dict[str, Any]:
            """Registers an existing account before it can be used for general API access. Each application from developer.tesla.com must complete this step."""
            return await self._request(
                POST, "api/1/partner_accounts", data={domain: domain}
            )

    class User:
        """Class describing the Tesla Fleet API user endpoints"""

        def __init__(self, parent):
            self._request = parent._request

        async def backup_key(self) -> dict[str, Any]:
            """Returns the public key associated with the user."""
            return await self._request(GET, "api/1/users/backup_key")

        async def feature_config(self) -> dict[str, Any]:
            """Returns any custom feature flag applied to a user."""
            return await self._request(GET, "api/1/users/feature_config")

        async def me(self) -> dict[str, Any]:
            """Returns a summary of a user's account."""
            return await self._request(GET, "api/1/users/me")

        async def orders(self) -> dict[str, Any]:
            """Returns the active orders for a user."""
            return await self._request(GET, "api/1/users/orders")

        async def region(self) -> dict[str, Any]:
            """Returns a user's region and appropriate fleet-api base URL. Accepts no parameters, response is based on the authentication token subject."""
            return await self._request(GET, "api/1/users/region")

    class Vehicle:
        """Class describing the Tesla Fleet API vehicle endpoints and commands."""

        def __init__(self, parent):
            self._request = parent._request
            self.use_command_protocol = parent.use_command_protocol

        class Trunk(StrEnum):
            """Trunk options"""

            FRONT: "front"
            REAR: "rear"

        async def actuate_trunk(
            self, vehicle_tag: str | int, which_trunk: Trunk | str
        ) -> dict[str, Any]:
            """Controls the front or rear trunk."""
            if self.use_command_protocol:
                raise NotImplementedError("Command Protocol not implemented")
            return await self._request(
                POST,
                f"api/1/vehicles/{vehicle_tag}/command/actuate_trunk",
                json={which_trunk: which_trunk},
            )

        async def adjust_volume(
            self, vehicle_tag: str | int, volume: float
        ) -> dict[str, Any]:
            """Adjusts vehicle media playback volume."""
            if self.use_command_protocol:
                raise NotImplementedError("Command Protocol not implemented")
            if volume < 0.0 or volume > 11.0:
                raise ValueError("Volume must a number from 0.0 to 11.0")
            return await self._request(
                POST,
                f"api/1/vehicles/{vehicle_tag}/command/adjust_volume",
                json={volume: volume},
            )

        async def auto_conditioning_start(
            self, vehicle_tag: str | int
        ) -> dict[str, Any]:
            """Starts climate preconditioning."""
            if self.use_command_protocol:
                raise NotImplementedError("Command Protocol not implemented")
            return await self._request(
                POST, f"api/1/vehicles/{vehicle_tag}/command/auto_conditioning_start"
            )

        async def auto_conditioning_stop(
            self, vehicle_tag: str | int
        ) -> dict[str, Any]:
            """Stops climate preconditioning."""
            if self.use_command_protocol:
                raise NotImplementedError("Command Protocol not implemented")
            return await self._request(
                POST, f"api/1/vehicles/{vehicle_tag}/command/auto_conditioning_stop"
            )

        async def cancel_software_update(
            self, vehicle_tag: str | int
        ) -> dict[str, Any]:
            """Cancels the countdown to install the vehicle software update."""
            if self.use_command_protocol:
                raise NotImplementedError("Command Protocol not implemented")
            return await self._request(
                POST, f"api/1/vehicles/{vehicle_tag}/command/cancel_software_update"
            )

        async def charge_max_range(self, vehicle_tag: str | int) -> dict[str, Any]:
            """Charges in max range mode -- we recommend limiting the use of this mode to long trips."""
            if self.use_command_protocol:
                raise NotImplementedError("Command Protocol not implemented")
            return await self._request(
                POST, f"api/1/vehicles/{vehicle_tag}/command/charge_max_range"
            )

        async def charge_port_door_close(
            self, vehicle_tag: str | int
        ) -> dict[str, Any]:
            """Closes the charge port door."""
            if self.use_command_protocol:
                raise NotImplementedError("Command Protocol not implemented")
            return await self._request(
                POST, f"api/1/vehicles/{vehicle_tag}/command/charge_port_door_close"
            )

        async def charge_port_door_open(self, vehicle_tag: str | int) -> dict[str, Any]:
            """Opens the charge port door."""
            if self.use_command_protocol:
                raise NotImplementedError("Command Protocol not implemented")
            return await self._request(
                POST, f"api/1/vehicles/{vehicle_tag}/command/charge_port_door_open"
            )

        async def charge_standard(self, vehicle_tag: str | int) -> dict[str, Any]:
            """Charges in Standard mode."""
            if self.use_command_protocol:
                raise NotImplementedError("Command Protocol not implemented")
            return await self._request(
                POST, f"api/1/vehicles/{vehicle_tag}/command/charge_standard"
            )

        async def charge_start(self, vehicle_tag: str | int) -> dict[str, Any]:
            """Starts charging the vehicle."""
            if self.use_command_protocol:
                raise NotImplementedError("Command Protocol not implemented")
            return await self._request(
                POST, f"api/1/vehicles/{vehicle_tag}/command/charge_start"
            )

        async def charge_stop(self, vehicle_tag: str | int) -> dict[str, Any]:
            """Stops charging the vehicle."""
            if self.use_command_protocol:
                raise NotImplementedError("Command Protocol not implemented")
            return await self._request(
                POST, f"api/1/vehicles/{vehicle_tag}/command/charge_stop"
            )

        async def clear_pin_to_drive_admin(self, vehicle_tag: str | int):
            """Deactivates PIN to Drive and resets the associated PIN for vehicles running firmware versions 2023.44+. This command is only accessible to fleet managers or owners."""
            return await self._request(
                POST, f"api/1/vehicles/{vehicle_tag}/command/clear_pin_to_drive_admin"
            )

        async def door_lock(self, vehicle_tag: str | int) -> dict[str, Any]:
            """Locks the vehicle."""
            if self.use_command_protocol:
                raise NotImplementedError("Command Protocol not implemented")
            return await self._request(
                POST, f"api/1/vehicles/{vehicle_tag}/command/door_lock"
            )

        async def door_unlock(self, vehicle_tag: str | int) -> dict[str, Any]:
            """Unlocks the vehicle."""
            if self.use_command_protocol:
                raise NotImplementedError("Command Protocol not implemented")
            return await self._request(
                POST, f"api/1/vehicles/{vehicle_tag}/command/door_unlock"
            )

        async def erase_user_data(self, vehicle_tag: str | int) -> dict[str, Any]:
            """Erases user's data from the user interface. Requires the vehicle to be in park."""
            return await self._request(
                POST, f"api/1/vehicles/{vehicle_tag}/command/erase_user_data"
            )

        async def flash_lights(self, vehicle_tag: str | int) -> dict[str, Any]:
            """Briefly flashes the vehicle headlights. Requires the vehicle to be in park."""
            if self.use_command_protocol:
                raise NotImplementedError("Command Protocol not implemented")
            return await self._request(
                POST, f"api/1/vehicles/{vehicle_tag}/command/flash_lights"
            )

        async def guest_mode(
            self, vehicle_tag: str | int, enable: bool
        ) -> dict[str, Any]:
            """Restricts certain vehicle UI functionality from guest users"""
            if self.use_command_protocol:
                raise NotImplementedError("Command Protocol not implemented")
            return await self._request(
                POST,
                f"api/1/vehicles/{vehicle_tag}/command/guest_mode",
                json={enable: enable},
            )

        async def honk_horn(self, vehicle_tag: str | int) -> dict[str, Any]:
            """Honks the vehicle horn. Requires the vehicle to be in park."""
            if self.use_command_protocol:
                raise NotImplementedError("Command Protocol not implemented")
            return await self._request(
                POST, f"api/1/vehicles/{vehicle_tag}/command/honk_horn"
            )

        async def media_next_fav(self, vehicle_tag: str | int) -> dict[str, Any]:
            """Advances media player to next favorite track."""
            return await self._request(
                POST, f"api/1/vehicles/{vehicle_tag}/command/media_next_fav"
            )

        async def media_next_track(self, vehicle_tag: str | int) -> dict[str, Any]:
            """Advances media player to next track."""
            return await self._request(
                POST, f"api/1/vehicles/{vehicle_tag}/command/media_next_track"
            )

        async def media_prev_fav(self, vehicle_tag: str | int) -> dict[str, Any]:
            """Advances media player to previous favorite track."""
            return await self._request(
                POST, f"api/1/vehicles/{vehicle_tag}/command/media_prev_fav"
            )

        async def media_prev_track(self, vehicle_tag: str | int) -> dict[str, Any]:
            """Advances media player to previous track."""
            return await self._request(
                POST, f"api/1/vehicles/{vehicle_tag}/command/media_prev_track"
            )

        async def media_toggle_playback(self, vehicle_tag: str | int) -> dict[str, Any]:
            """Toggles current play/pause state."""
            return await self._request(
                POST, f"api/1/vehicles/{vehicle_tag}/command/media_toggle_playback"
            )

        async def media_volume_down(self, vehicle_tag: str | int) -> dict[str, Any]:
            """Turns the volume down by one."""
            return await self._request(
                POST, f"api/1/vehicles/{vehicle_tag}/command/media_volume_down"
            )

        async def navigation_gps_request(
            self, vehicle_tag: str | int, lat: float, lon: float, order: int
        ) -> dict[str, Any]:
            """Start navigation to given coordinates. Order can be used to specify order of multiple stops."""
            if self.use_command_protocol:
                raise NotImplementedError("Command Protocol not implemented")
            return await self._request(
                POST,
                f"api/1/vehicles/{vehicle_tag}/command/navigation_gps_request",
                json={lat: lat, lon: lon, order: order},
            )

        async def navigation_request(
            self, vehicle_tag: str | int, type: str, locale: str, timestamp_ms: str
        ) -> dict[str, Any]:
            """Sends a location to the in-vehicle navigation system."""
            return await self._request(
                POST,
                f"api/1/vehicles/{vehicle_tag}/command/navigation_request",
                json={type: type, locale: locale, timestamp_ms: timestamp_ms},
            )

        async def navigation_sc_request(
            self, vehicle_tag: str | int, id: int, order: int
        ) -> dict[str, Any]:
            """Sends a location to the in-vehicle navigation system."""
            return await self._request(
                POST,
                f"api/1/vehicles/{vehicle_tag}/command/navigation_sc_request",
                json={type: type, id: id, order: order},
            )

        async def remote_auto_seat_climate_request(
            self, vehicle_tag: str | int, auto_seat_position: int, auto_climate_on: bool
        ) -> dict[str, Any]:
            """Sets automatic seat heating and cooling."""
            if self.use_command_protocol:
                raise NotImplementedError("Command Protocol not implemented")
            return await self._request(
                POST,
                f"api/1/vehicles/{vehicle_tag}/command/remote_auto_seat_climate_request",
                json={
                    auto_seat_position: auto_seat_position,
                    auto_climate_on: auto_climate_on,
                },
            )

        async def remote_auto_steering_wheel_heat_climate_request(
            self, vehicle_tag: str | int, on: bool
        ) -> dict[str, Any]:
            """Sets automatic steering wheel heating on/off."""
            return await self._request(
                POST,
                f"api/1/vehicles/{vehicle_tag}/command/remote_auto_steering_wheel_heat_climate_request",
                json={on: on},
            )

        async def remote_boombox(
            self, vehicle_tag: str | int, sound: int
        ) -> dict[str, Any]:
            """Plays a sound through the vehicle external speaker."""
            return await self._request(
                POST,
                f"api/1/vehicles/{vehicle_tag}/command/remote_boombox",
                json={sound: sound},
            )

        async def remote_seat_cooler_request(
            self, vehicle_tag: str | int, seat_position: int, seat_cooler_level: int
        ) -> dict[str, Any]:
            """Sets seat cooling."""
            if self.use_command_protocol:
                raise NotImplementedError("Command Protocol not implemented")
            return await self._request(
                POST,
                f"api/1/vehicles/{vehicle_tag}/command/remote_seat_cooler_request",
                json={
                    seat_position: seat_position,
                    seat_cooler_level: seat_cooler_level,
                },
            )

        async def remote_seat_heater_request(
            self, vehicle_tag: str | int
        ) -> dict[str, Any]:
            """Sets seat heating."""
            if self.use_command_protocol:
                raise NotImplementedError("Command Protocol not implemented")
            return await self._request(
                POST,
                f"api/1/vehicles/{vehicle_tag}/command/remote_seat_heater_request",
            )

        async def remote_start_drive(self, vehicle_tag: str | int) -> dict[str, Any]:
            """Starts the vehicle remotely. Requires keyless driving to be enabled."""
            if self.use_command_protocol:
                raise NotImplementedError("Command Protocol not implemented")
            return await self._request(
                POST, f"api/1/vehicles/{vehicle_tag}/command/remote_start_drive"
            )

        async def remote_steering_wheel_heat_level_request(
            self, vehicle_tag: str | int, level: int
        ) -> dict[str, Any]:
            """Sets steering wheel heat level."""
            if self.use_command_protocol:
                raise NotImplementedError("Command Protocol not implemented")
            return await self._request(
                POST,
                f"api/1/vehicles/{vehicle_tag}/command/remote_steering_wheel_heat_level_request",
                json={level: level},
            )

        async def remote_steering_wheel_heater_request(
            self, vehicle_tag: str | int, on: bool
        ) -> dict[str, Any]:
            """Sets steering wheel heating on/off. For vehicles that do not support auto steering wheel heat."""
            if self.use_command_protocol:
                raise NotImplementedError("Command Protocol not implemented")
            return await self._request(
                POST,
                f"api/1/vehicles/{vehicle_tag}/command/remote_steering_wheel_heater_request",
                json={on: on},
            )

        async def reset_pin_to_drive_pin(
            self, vehicle_tag: str | int
        ) -> dict[str, Any]:
            """Removes PIN to Drive. Requires the car to be in Pin to Drive mode and not in Valet mode. Note that this only works if PIN to Drive is not active. This command also requires the Tesla Vehicle Command Protocol - for more information, please see refer to the documentation here."""
            if self.use_command_protocol:
                raise NotImplementedError("Command Protocol not implemented")
            return await self._request(
                POST, f"api/1/vehicles/{vehicle_tag}/command/reset_pin_to_drive_pin"
            )

        async def reset_valet_pin(self, vehicle_tag: str | int) -> dict[str, Any]:
            """Removes PIN for Valet Mode."""
            if self.use_command_protocol:
                raise NotImplementedError("Command Protocol not implemented")
            return await self._request(
                POST, f"api/1/vehicles/{vehicle_tag}/command/reset_valet_pin"
            )

        async def schedule_software_update(
            self, vehicle_tag: str | int, offset_sec: int
        ) -> dict[str, Any]:
            """Schedules a vehicle software update (over the air "OTA") to be installed in the future."""
            if self.use_command_protocol:
                raise NotImplementedError("Command Protocol not implemented")
            return await self._request(
                POST,
                f"api/1/vehicles/{vehicle_tag}/command/schedule_software_update",
                json={offset_sec: offset_sec},
            )

        async def set_bioweapon_mode(
            self, vehicle_tag: str | int, on: bool, manual_override: bool
        ) -> dict[str, Any]:
            """Turns Bioweapon Defense Mode on and off."""
            if self.use_command_protocol:
                raise NotImplementedError("Command Protocol not implemented")
            return await self._request(
                POST,
                f"api/1/vehicles/{vehicle_tag}/command/set_bioweapon_mode",
                json={on: on, manual_override: manual_override},
            )

        async def set_cabin_overheat_protection(
            self, vehicle_tag: str | int, on: bool, fan_only: bool
        ) -> dict[str, Any]:
            """Sets the vehicle overheat protection."""
            if self.use_command_protocol:
                raise NotImplementedError("Command Protocol not implemented")
            return await self._request(
                POST,
                f"api/1/vehicles/{vehicle_tag}/command/set_cabin_overheat_protection",
                json={on: on, fan_only: fan_only},
            )

        async def set_charge_limit(
            self, vehicle_tag: str | int, percent: int
        ) -> dict[str, Any]:
            """Sets the vehicle charge limit."""
            if self.use_command_protocol:
                raise NotImplementedError("Command Protocol not implemented")
            return await self._request(
                POST,
                f"api/1/vehicles/{vehicle_tag}/command/set_charge_limit",
                json={percent: percent},
            )

        async def set_charging_amps(
            self, vehicle_tag: str | int, charging_amps: int
        ) -> dict[str, Any]:
            """Sets the vehicle charging amps."""
            if self.use_command_protocol:
                raise NotImplementedError("Command Protocol not implemented")
            return await self._request(
                POST,
                f"api/1/vehicles/{vehicle_tag}/command/set_charging_amps",
                json={charging_amps: charging_amps},
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
            if self.use_command_protocol:
                raise NotImplementedError("Command Protocol not implemented")
            return await self._request(
                POST,
                f"api/1/vehicles/{vehicle_tag}/command/set_climate_keeper_mode",
                json={climate_keeper_mode: climate_keeper_mode},
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
            if self.use_command_protocol:
                raise NotImplementedError("Command Protocol not implemented")
            return await self._request(
                POST,
                f"api/1/vehicles/{vehicle_tag}/command/set_cop_temp",
                json={cop_temp: cop_temp},
            )

        async def set_pin_to_drive(
            self, vehicle_tag: str | int, on: bool, password: str | int
        ) -> dict[str, Any]:
            """Sets a four-digit passcode for PIN to Drive. This PIN must then be entered before the vehicle can be driven."""
            if self.use_command_protocol:
                raise NotImplementedError("Command Protocol not implemented")
            return await self._request(
                POST,
                f"api/1/vehicles/{vehicle_tag}/command/set_pin_to_drive",
                json={on: on, password: str(password)},
            )

        async def set_preconditioning_max(
            self, vehicle_tag: str | int, on: bool, manual_override: bool
        ) -> dict[str, Any]:
            """Sets an override for preconditioning — it should default to empty if no override is used."""
            if self.use_command_protocol:
                raise NotImplementedError("Command Protocol not implemented")
            return await self._request(
                POST,
                f"api/1/vehicles/{vehicle_tag}/command/set_preconditioning_max",
                json={on: on, manual_override: manual_override},
            )

        async def set_scheduled_charging(
            self, vehicle_tag: str | int, enable: bool, time: int
        ) -> dict[str, Any]:
            """Sets a time at which charging should be completed. The time parameter is minutes after midnight (e.g: time=120 schedules charging for 2:00am vehicle local time)."""
            if self.use_command_protocol:
                raise NotImplementedError("Command Protocol not implemented")
            return await self._request(
                POST,
                f"api/1/vehicles/{vehicle_tag}/command/set_scheduled_charging",
                json={enable: enable, time: time},
            )

        async def set_scheduled_departure(
            self, vehicle_tag: str | int, enable: bool, time: int
        ) -> dict[str, Any]:
            """Sets a time at which departure should be completed. The time parameter is minutes after midnight (e.g: time=120 schedules departure for 2:00am vehicle local time)."""
            if self.use_command_protocol:
                raise NotImplementedError("Command Protocol not implemented")
            return await self._request(
                POST,
                f"api/1/vehicles/{vehicle_tag}/command/set_scheduled_departure",
                json={enable: enable, time: time},
            )

        async def set_sentry_mode(
            self, vehicle_tag: str | int, on: bool
        ) -> dict[str, Any]:
            """Enables and disables Sentry Mode. Sentry Mode allows customers to watch the vehicle cameras live from the mobile app, as well as record sentry events."""
            if self.use_command_protocol:
                raise NotImplementedError("Command Protocol not implemented")
            return await self._request(
                POST,
                f"api/1/vehicles/{vehicle_tag}/command/set_sentry_mode",
                json={on: on},
            )

        async def set_temps(
            self, vehicle_tag: str | int, driver_temp: int, passenger_temp: int
        ) -> dict[str, Any]:
            """Sets the driver and/or passenger-side cabin temperature (and other zones if sync is enabled)."""
            if self.use_command_protocol:
                raise NotImplementedError("Command Protocol not implemented")
            return await self._request(
                POST,
                f"api/1/vehicles/{vehicle_tag}/command/set_temps",
                json={driver_temp: driver_temp, passenger_temp: passenger_temp},
            )

        async def set_valet_mode(
            self, vehicle_tag: str | int, on: bool, password: str | int
        ) -> dict[str, Any]:
            """Turns on Valet Mode and sets a four-digit passcode that must then be entered to disable Valet Mode."""
            if self.use_command_protocol:
                raise NotImplementedError("Command Protocol not implemented")
            return await self._request(
                POST,
                f"api/1/vehicles/{vehicle_tag}/command/set_valet_mode",
                json={on: on, password: str(password)},
            )

        async def set_vehicle_name(
            self, vehicle_tag: str | int, vehicle_name: str
        ) -> dict[str, Any]:
            """Changes the name of a vehicle. This command also requires the Tesla Vehicle Command Protocol - for more information, please see refer to the documentation here."""
            if self.use_command_protocol:
                raise NotImplementedError("Command Protocol not implemented")
            return await self._request(
                POST,
                f"api/1/vehicles/{vehicle_tag}/command/set_vehicle_name",
                json={vehicle_name: vehicle_name},
            )

        async def speed_limit_activate(
            self, vehicle_tag: str | int, pin: str | int
        ) -> dict[str, Any]:
            """Activates Speed Limit Mode with a four-digit PIN."""
            if self.use_command_protocol:
                raise NotImplementedError("Command Protocol not implemented")
            return await self._request(
                POST,
                f"api/1/vehicles/{vehicle_tag}/command/speed_limit_activate",
                json={pin: str(pin)},
            )

        async def speed_limit_clear_pin(
            self, vehicle_tag: str | int, pin: str | int
        ) -> dict[str, Any]:
            """Deactivates Speed Limit Mode and resets the associated PIN."""
            if self.use_command_protocol:
                raise NotImplementedError("Command Protocol not implemented")
            return await self._request(
                POST,
                f"api/1/vehicles/{vehicle_tag}/command/speed_limit_clear_pin",
                json={pin: str(pin)},
            )

        async def speed_limit_clear_pin_admin(
            self, vehicle_tag: str | int
        ) -> dict[str, Any]:
            """Deactivates Speed Limit Mode and resets the associated PIN for vehicles running firmware versions 2023.38+. This command is only accessible to fleet managers or owners."""
            return await self._request(
                POST,
                f"api/1/vehicles/{vehicle_tag}/command/speed_limit_clear_pin_admin",
            )

        async def speed_limit_deactivate(
            self, vehicle_tag: str | int, pin: str | int
        ) -> dict[str, Any]:
            """Deactivates Speed Limit Mode."""
            if self.use_command_protocol:
                raise NotImplementedError("Command Protocol not implemented")
            return await self._request(
                POST,
                f"api/1/vehicles/{vehicle_tag}/command/speed_limit_deactivate",
                json={pin: str(pin)},
            )

        async def speed_limit_set_limit(
            self, vehicle_tag: str | int, limit_mph: int
        ) -> dict[str, Any]:
            """Sets the maximum speed allowed when Speed Limit Mode is active."""
            if self.use_command_protocol:
                raise NotImplementedError("Command Protocol not implemented")
            return await self._request(
                POST,
                f"api/1/vehicles/{vehicle_tag}/command/speed_limit_set_limit",
                json={limit_mph: limit_mph},
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
            return await self._request(
                POST,
                f"api/1/vehicles/{vehicle_tag}/command/sun_roof_control",
                {state: state},
            )

        async def take_drivenote(
            self, vehicle_tag: str | int, note: str
        ) -> dict[str, Any]:
            """Records a drive note. The note parameter is truncated to 80 characters in length."""
            return await self._request(
                POST,
                f"api/1/vehicles/{vehicle_tag}/command/take_drivenote",
                {note: note},
            )

        async def trigger_homelink(
            self, vehicle_tag: str | int, lat: float, lon: float, token: str
        ) -> dict[str, Any]:
            """Turns on HomeLink (used to open and close garage doors)."""
            if self.use_command_protocol:
                raise NotImplementedError("Command Protocol not implemented")
            return await self._request(
                POST,
                f"api/1/vehicles/{vehicle_tag}/command/trigger_homelink",
                {lat: lat, lon: lon, token: token},
            )

        async def upcoming_calendar_entries(
            self, vehicle_tag: str | int, calendar_data: str
        ) -> dict[str, Any]:
            """Upcoming calendar entries stored on the vehicle."""
            return await self._request(
                POST,
                f"api/1/vehicles/{vehicle_tag}/command/upcoming_calendar_entries",
                {calendar_data: calendar_data},
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
            return await self._request(
                POST,
                f"api/1/vehicles/{vehicle_tag}/command/window_control",
                {lat: lat, lon: lon, command: command},
            )

        async def drivers(self, vehicle_tag: str | int) -> dict[str, Any]:
            """Returns all allowed drivers for a vehicle. This endpoint is only available for the vehicle owner."""
            return await self._request(GET, f"api/1/vehicles/{vehicle_tag}/drivers")

        async def drivers_remove(
            self, vehicle_tag: str | int, share_user_id: str | int | None = None
        ) -> dict[str, Any]:
            """Removes driver access from a vehicle. Share users can only remove their own access. Owners can remove share access or their own."""
            return await self._request(
                DELETE,
                f"api/1/vehicles/{vehicle_tag}/drivers",
                {share_user_id: share_user_id},
            )

        async def list(
            self, page: int | None = None, per_page: int | None = None
        ) -> dict[str, Any]:
            """Returns vehicles belonging to the account."""
            return await self._request(
                GET, "api/1/vehicles", {page: page, per_page: per_page}
            )

        async def mobile_enabled(self, vehicle_tag: str | int) -> dict[str, Any]:
            """Returns whether or not mobile access is enabled for the vehicle."""
            return await self._request(
                GET, f"api/1/vehicles/{vehicle_tag}/mobile_enabled"
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
                GET,
                f"api/1/vehicles/{vehicle_tag}/nearby_charging_sites",
                {count: count, radius: radius, detail: detail},
            )

        async def options(self, vin: str) -> dict[str, Any]:
            """Returns vehicle option details."""
            return await self._request(GET, "api/1/dx/vehicles/options", {vin: vin})

        async def recent_alerts(self, vehicle_tag: str | int) -> dict[str, Any]:
            """List of recent alerts"""
            return await self._request(
                GET, f"api/1/vehicles/{vehicle_tag}/recent_alerts"
            )

        async def release_notes(
            self,
            vehicle_tag: str | int,
            staged: bool | None = None,
            language: int | None = None,
        ) -> dict[str, Any]:
            """Returns firmware release notes."""
            return await self._request(
                GET,
                f"api/1/vehicles/{vehicle_tag}/release_notes",
                {staged: staged, language: language},
            )

        async def service_data(self, vehicle_tag: str | int) -> dict[str, Any]:
            """Returns service data."""
            return await self._request(
                GET, f"api/1/vehicles/{vehicle_tag}/service_data"
            )

        async def share_invites(self, vehicle_tag: str | int) -> dict[str, Any]:
            """Returns the share invites for a vehicle."""
            return await self._request(GET, f"api/1/vehicles/{vehicle_tag}/invitations")

        async def share_invites_create(self, vehicle_tag: str | int) -> dict[str, Any]:
            """Creates a share invite for a vehicle."""
            return await self._request(
                POST, f"api/1/vehicles/{vehicle_tag}/invitations"
            )

        async def share_invites_redeem(self, code: str) -> dict[str, Any]:
            """Redeems a share invite."""
            return await self._request(POST, "api/1/invitations/redeem", {code: code})

        async def share_invites_revoke(
            self, vehicle_tag: str | int, id: str
        ) -> dict[str, Any]:
            """Revokes a share invite."""
            return await self._request(
                POST, f"api/1/vehicles/{vehicle_tag}/invitations/{id}/revoke"
            )

        async def signed_command(
            self, vehicle_tag: str | int, routable_message: str
        ) -> dict[str, Any]:
            """Signed Commands is a generic endpoint replacing legacy commands."""
            return await self._request(
                POST,
                f"api/1/vehicles/{vehicle_tag}/signed_command",
                {routable_message: routable_message},
            )

        async def subscriptions(
            self, device_token: str, device_type: str
        ) -> dict[str, Any]:
            """Returns the list of vehicles for which this mobile device currently subscribes to push notifications."""
            return await self._request(
                GET,
                "api/1/subscriptions",
                query={device_token: device_token, device_type: device_type},
            )

        async def subscriptions_set(
            self, device_token: str, device_type: str
        ) -> dict[str, Any]:
            """Allows a mobile device to specify which vehicles to receive push notifications from."""
            return await self._request(
                POST,
                "api/1/subscriptions",
                query={device_token: device_token, device_type: device_type},
            )

        async def vehicle(self, vehicle_tag: str | int) -> dict[str, Any]:
            """Returns information about a vehicle."""
            return await self._request(GET, f"api/1/vehicles/{vehicle_tag}")

        class Endpoints(StrEnum):
            """Endpoints options"""

            CHARGE_STATE = "charge_state"
            CLIMATE_STATE = "climate_state"
            CLOSURES_STATE = "closures_state"
            DRIVE_STATE = "drive_state"
            GUI_SETTINGS = "gui_settings"
            LOCATION_DATA = "location_data"
            VEHICLE_CONFIG = "vehicle_config"
            VEHICLE_STATE = "vehicle_state"
            VEHICLE_DATA_COMBO = "vehicle_data_combo"

        async def vehicle_data(
            self,
            vehicle_tag: str | int,
            endpoints: Endpoints | str | None = None,
        ) -> dict[str, Any]:
            """Makes a live call to the vehicle. This may return cached data if the vehicle is offline. For vehicles running firmware versions 2023.38+, location_data is required to fetch vehicle location. This will result in a location sharing icon to show on the vehicle UI."""
            return await self._request(
                GET,
                f"api/1/vehicles/{vehicle_tag}/vehicle_data",
                {endpoints: endpoints},
            )

        class DeviceType(StrEnum):
            """Device Type options"""

            ANDROID = "android"
            IOS_DEVELOPMENT = "ios-development"
            IOS_ENTERPRISE = "ios-enterprise"
            IOS_BETA = "ios-beta"
            IOS_PRODUCTION = "ios-production"

        async def vehicle_subscriptions(
            self, device_token: str, device_type: DeviceType | str
        ) -> dict[str, Any]:
            """Returns the list of vehicles for which this mobile device currently subscribes to push notifications."""
            return await self._request(
                GET,
                "api/1/vehicle_subscriptions",
                {device_token: device_token, device_type: device_type},
            )

        async def vehicle_subscriptions_set(
            self, device_token: str, device_type: DeviceType | str
        ) -> dict[str, Any]:
            """Allows a mobile device to specify which vehicles to receive push notifications from."""
            return await self._request(
                POST,
                "api/1/vehicle_subscriptions",
                params={device_token: device_token, device_type: device_type},
            )

        async def wake_up(self, vehicle_tag: str | int) -> dict[str, Any]:
            """Wakes the vehicle from sleep, which is a state to minimize idle energy consumption."""
            return await self._request(POST, f"api/1/vehicles/{vehicle_tag}/wake_up")

        async def warranty_details(self, vin: str | None) -> dict[str, Any]:
            """Returns warranty details."""
            return await self._request(GET, "api/1/dx/warranty/details", {vin: vin})

        async def fleet_telemetry_config(
            self, config: dict[str, Any]
        ) -> dict[str, Any]:
            """Configures fleet telemetry."""
            return await self._request(
                POST, "api/1/vehicles/fleet_telemetry_config", json=config
            )
