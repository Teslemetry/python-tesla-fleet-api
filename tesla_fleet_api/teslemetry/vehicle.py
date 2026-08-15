from __future__ import annotations

from typing import TYPE_CHECKING, Any

from tesla_fleet_api.const import (
    BluetoothConfirmation,
    DistanceUnit,
    EnergyDisplayFormat,
    Method,
    ClosureState,
    SeatHeaterLevel,
    TemperatureUnit,
    TimeDisplayFormat,
    TirePressureUnit,
)
from tesla_fleet_api.tesla.vehicle.vehicles import Vehicles
from tesla_fleet_api.tesla.vehicle.fleet import VehicleFleet
from tesla_fleet_api.const import LOGGER

if TYPE_CHECKING:
    from tesla_fleet_api.teslemetry.teslemetry import Teslemetry


class TeslemetryVehicle(VehicleFleet["Teslemetry"]):
    """Teslemetry specific API vehicle."""

    parent: Teslemetry

    async def server_side_polling(self, value: bool | None = None) -> bool | None:
        """Get or set Auto mode."""
        LOGGER.warning(
            "This method is deprecated and will be removed in a future release."
        )
        if value is True:
            return (
                await self._request(
                    Method.POST,
                    f"api/auto/{self.vin}",
                )
            ).get("response")
        if value is False:
            return (
                await self._request(
                    Method.DELETE,
                    f"api/auto/{self.vin}",
                )
            ).get("response")
        return (
            await self._request(
                Method.GET,
                f"api/auto/{self.vin}",
            )
        ).get("response")

    async def data_refresh(self) -> dict[str, Any]:
        """Force a refresh of the vehicle data."""
        return await self._request(
            Method.GET,
            f"api/refresh/{self.vin}",
        )

    async def ping(self) -> dict[str, Any]:
        """Performs a no-op on the vehicle."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{self.vin}/custom_command/ping",
        )

    async def closure(
        self,
        front_driver_door: ClosureState = ClosureState.NONE,
        front_passenger_door: ClosureState = ClosureState.NONE,
        rear_driver_door: ClosureState = ClosureState.NONE,
        rear_passenger_door: ClosureState = ClosureState.NONE,
        rear_trunk: ClosureState = ClosureState.NONE,
        front_trunk: ClosureState = ClosureState.NONE,
        charge_port: ClosureState = ClosureState.NONE,
        tonneau: ClosureState = ClosureState.NONE,
    ) -> dict[str, Any]:
        """Open, Close, Move and Stop the vehicle's windows, doors, and frunk/trunk.

        Args:
            front_driver_door: Action for front driver door
            front_passenger_door: Action for front passenger door
            rear_driver_door: Action for rear driver door
            rear_passenger_door: Action for rear passenger door
            rear_trunk: Action for rear trunk
            front_trunk: Action for front trunk
            charge_port: Action for charge port
            tonneau: Action for tonneau

        Example:
            # Open the front trunk
            await vehicle.closure(front_trunk=ClosureState.OPEN)

            # Close all doors
            await vehicle.closure(
                front_driver_door=ClosureState.CLOSE,
                front_passenger_door=ClosureState.CLOSE,
                rear_driver_door=ClosureState.CLOSE,
                rear_passenger_door=ClosureState.CLOSE
            )
        """
        data: dict[str, Any] = {}
        if front_driver_door != ClosureState.NONE:
            data["frontDriverDoor"] = front_driver_door.value
        if front_passenger_door != ClosureState.NONE:
            data["frontPassengerDoor"] = front_passenger_door.value
        if rear_driver_door != ClosureState.NONE:
            data["rearDriverDoor"] = rear_driver_door.value
        if rear_passenger_door != ClosureState.NONE:
            data["rearPassengerDoor"] = rear_passenger_door.value
        if rear_trunk != ClosureState.NONE:
            data["rearTrunk"] = rear_trunk.value
        if front_trunk != ClosureState.NONE:
            data["frontTrunk"] = front_trunk.value
        if charge_port != ClosureState.NONE:
            data["chargePort"] = charge_port.value
        if tonneau != ClosureState.NONE:
            data["tonneau"] = tonneau.value

        return await self._request(
            Method.POST,
            f"api/1/vehicles/{self.vin}/custom_command/closure",
            json=data,
        )

    async def seat_heater(
        self,
        front_left: SeatHeaterLevel | None = None,
        front_right: SeatHeaterLevel | None = None,
        rear_left: SeatHeaterLevel | None = None,
        rear_right: SeatHeaterLevel | None = None,
        rear_left_back: SeatHeaterLevel | None = None,
        rear_center: SeatHeaterLevel | None = None,
        rear_right_back: SeatHeaterLevel | None = None,
        third_row_left: SeatHeaterLevel | None = None,
        third_row_right: SeatHeaterLevel | None = None,
    ) -> dict[str, Any]:
        """Sets multiple seat heaters at once.

        Args:
            front_left: Front left seat heater level
            front_right: Front right seat heater level
            rear_left: Rear left seat heater level
            rear_right: Rear right seat heater level
            rear_left_back: Rear left back seat heater level
            rear_center: Rear center seat heater level
            rear_right_back: Rear right back seat heater level
            third_row_left: Third row left seat heater level
            third_row_right: Third row right seat heater level

        Example:
            # Set front seats to high heat
            await vehicle.seat_heater(
                front_left=SeatHeaterLevel.HIGH,
                front_right=SeatHeaterLevel.HIGH
            )

            # Turn off all seat heaters
            await vehicle.seat_heater(
                front_left=SeatHeaterLevel.OFF,
                front_right=SeatHeaterLevel.OFF,
                rear_left=SeatHeaterLevel.OFF,
                rear_right=SeatHeaterLevel.OFF
            )
        """
        data: dict[str, Any] = {}
        if front_left is not None:
            data["frontLeft"] = front_left.value
        if front_right is not None:
            data["frontRight"] = front_right.value
        if rear_left is not None:
            data["rearLeft"] = rear_left.value
        if rear_right is not None:
            data["rearRight"] = rear_right.value
        if rear_left_back is not None:
            data["rearLeftBack"] = rear_left_back.value
        if rear_center is not None:
            data["rearCenter"] = rear_center.value
        if rear_right_back is not None:
            data["rearRightBack"] = rear_right_back.value
        if third_row_left is not None:
            data["thirdRowLeft"] = third_row_left.value
        if third_row_right is not None:
            data["thirdRowRight"] = third_row_right.value

        return await self._request(
            Method.POST,
            f"api/1/vehicles/{self.vin}/custom_command/seat_heater",
            json=data,
        )

    async def charge_on_solar(
        self,
        enabled: bool | None = None,
        lower_charge_limit: int | None = None,
        upper_charge_limit: int | None = None,
    ) -> dict[str, Any]:
        """Enable or disable charging on solar, set lower and upper charge limits.

        Args:
            enabled: Enable or disable charging on solar
            lower_charge_limit: Lower charge limit (0 - upper_charge_limit)
            upper_charge_limit: Upper charge limit (lower_charge_limit - 100)
        """
        data: dict[str, Any] = {}
        if enabled is not None:
            data["enabled"] = enabled
        if lower_charge_limit is not None:
            data["lowerChargeLimit"] = lower_charge_limit
        if upper_charge_limit is not None:
            data["upperChargeLimit"] = upper_charge_limit

        return await self._request(
            Method.POST,
            f"api/1/vehicles/{self.vin}/custom_command/charge_on_solar",
            json=data,
        )

    async def dashcam_save(self) -> dict[str, Any]:
        """Save the last 10 minutes of dashcam footage."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{self.vin}/custom_command/dashcam_save",
        )

    async def play_video(self, url: str) -> dict[str, Any]:
        """Play a supported video URL in the vehicle.

        Args:
            url: Video URL to play (e.g., YouTube URL)
        """
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{self.vin}/custom_command/play_video",
            json={"url": url},
        )

    async def stop_light_show(self) -> dict[str, Any]:
        """Stop the currently playing light show."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{self.vin}/custom_command/stop_light_show",
        )

    async def start_light_show(
        self,
        show_index: int,
        start_time: int | None = None,
        volume: float | None = None,
        dance_moves: bool | None = None,
    ) -> dict[str, Any]:
        """Start a light show on the vehicle.

        Args:
            show_index: Index of the light show to play
            start_time: Start time in milliseconds since epoch
            volume: Volume level for the light show
            dance_moves: Enable dance moves during the light show
        """
        data: dict[str, Any] = {"show_index": show_index}
        if start_time is not None:
            data["start_time"] = start_time
        if volume is not None:
            data["volume"] = volume
        if dance_moves is not None:
            data["dance_moves"] = dance_moves

        return await self._request(
            Method.POST,
            f"api/1/vehicles/{self.vin}/custom_command/start_light_show",
            json=data,
        )

    async def clear_pin_to_drive(self, pin: str) -> dict[str, Any]:
        """Deactivates PIN to Drive.

        Args:
            pin: 4-digit PIN to clear
        """
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{self.vin}/custom_command/clear_pin_to_drive",
            json={"pin": pin},
        )

    async def remove_key(self) -> dict[str, Any]:
        """Remove all impermanent keys from the vehicle."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{self.vin}/custom_command/remove_key",
        )

    async def get_charge_on_solar(self) -> dict[str, Any]:
        """Gets the current charge-on-solar feature settings."""
        return await self._request(
            Method.GET,
            f"api/1/vehicles/{self.vin}/custom_command/charge_on_solar",
        )

    # Below: custom_command routes with no public OpenAPI schema. Body key
    # names are inferred from tesla-protocol field names and the confirmed
    # set_keep_accessory_power_mode {on: bool} shape, not independently
    # verified against Tesla/Teslemetry documentation.

    async def set_front_zone_lights(self, level: int) -> dict[str, Any]:
        """Sets front zone light level (0=off, 1=low, 2=med, 3=high).

        Named to match the BLE ``Commands.set_front_zone_lights`` sibling so
        ``VehicleRouter`` failover can find this method by attribute name.
        """
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{self.vin}/custom_command/front_zone_light",
            json={"level": level},
        )

    async def set_rear_zone_lights(self, level: int) -> dict[str, Any]:
        """Sets rear zone light level (0=off, 1=low, 2=med, 3=high).

        Named to match the BLE ``Commands.set_rear_zone_lights`` sibling so
        ``VehicleRouter`` failover can find this method by attribute name.
        """
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{self.vin}/custom_command/rear_zone_light",
            json={"level": level},
        )

    async def set_outlets(self, request: int) -> dict[str, Any]:
        """Sets outlets on/off (0=off, 1=cabin+bed, 2=cabin)."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{self.vin}/custom_command/set_outlets",
            json={"request": request},
        )

    async def set_outlet_soc_limit(self, percent: int) -> dict[str, Any]:
        """Sets the outlet SOC limit percentage."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{self.vin}/custom_command/set_outlet_soc_limit",
            json={"percent": percent},
        )

    async def set_power_feed(self, request: int) -> dict[str, Any]:
        """Sets power feed on/off (0=off, 1=feed1, 2=feed2, 3=both)."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{self.vin}/custom_command/set_power_feed",
            json={"request": request},
        )

    async def set_power_feed_soc_limit(self, percent: int) -> dict[str, Any]:
        """Sets the power feed SOC limit percentage."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{self.vin}/custom_command/set_power_feed_soc_limit",
            json={"percent": percent},
        )

    async def set_lightbar_brightness(self, brightness: int) -> dict[str, Any]:
        """Sets the lightbar brightness."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{self.vin}/custom_command/set_lightbar_brightness",
            json={"brightness": brightness},
        )

    async def set_lightbar_middle(self, on: bool) -> dict[str, Any]:
        """Enables or disables the lightbar middle light."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{self.vin}/custom_command/set_lightbar_middle",
            json={"on": on},
        )

    async def set_lightbar_ditch(self, on: bool) -> dict[str, Any]:
        """Enables or disables the ditch lights."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{self.vin}/custom_command/set_lightbar_ditch",
            json={"on": on},
        )

    async def set_trailer_light_test(self, on: bool) -> dict[str, Any]:
        """Starts or stops the trailer light test."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{self.vin}/custom_command/set_trailer_light_test",
            json={"on": on},
        )

    async def set_truck_bed_light_auto(self, on: bool) -> dict[str, Any]:
        """Sets truck bed light auto state."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{self.vin}/custom_command/set_truck_bed_light_auto",
            json={"on": on},
        )

    async def set_truck_bed_light_brightness(self, brightness: int) -> dict[str, Any]:
        """Sets truck bed light brightness."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{self.vin}/custom_command/set_truck_bed_light_brightness",
            json={"brightness": brightness},
        )

    async def set_powershare_feature(self, on: bool) -> dict[str, Any]:
        """Enables or disables the Powershare feature."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{self.vin}/custom_command/set_powershare_feature",
            json={"on": on},
        )

    async def set_powershare_request(self, on: bool) -> dict[str, Any]:
        """Enables or disables an active Powershare session."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{self.vin}/custom_command/set_powershare_request",
            json={"on": on},
        )

    async def set_powershare_discharge_limit(self, percent: int) -> dict[str, Any]:
        """Sets the Powershare discharge limit percentage."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{self.vin}/custom_command/set_powershare_discharge_limit",
            json={"percent": percent},
        )

    async def set_recirculation(self, on: bool) -> dict[str, Any]:
        """Sets HVAC recirculation mode on/off.

        Named to match the BLE ``Commands.set_recirculation`` sibling so
        ``VehicleRouter`` failover can find this method by attribute name.
        """
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{self.vin}/custom_command/hvac_recirculation",
            json={"on": on},
        )

    async def set_tent_mode(self, on: bool) -> dict[str, Any]:
        """Enables or disables tent mode."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{self.vin}/custom_command/set_tent_mode",
            json={"on": on},
        )

    async def set_suspension_level(self, level: int) -> dict[str, Any]:
        """Sets the vehicle suspension level (1=entry, 2=low, 3=medium, 4=high, 5=very_high, 6=extract)."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{self.vin}/custom_command/set_suspension_level",
            json={"level": level},
        )

    async def set_low_power_mode(self, on: bool) -> dict[str, Any]:
        """Turns Low Power mode on and off, reducing standby power consumption while the vehicle is parked."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{self.vin}/custom_command/set_low_power_mode",
            json={"on": on},
        )

    async def set_keep_accessory_power_mode(self, on: bool) -> dict[str, Any]:
        """Turns Keep Accessory Power mode on and off, keeping 12V accessory power available while the vehicle is parked."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{self.vin}/custom_command/set_keep_accessory_power_mode",
            json={"on": on},
        )

    async def set_temperature_unit(self, unit: TemperatureUnit | int) -> dict[str, Any]:
        """Sets the vehicle's displayed temperature unit."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{self.vin}/custom_command/set_temperature_unit",
            json={"unit": unit},
        )

    async def set_distance_unit(self, unit: DistanceUnit | int) -> dict[str, Any]:
        """Sets the vehicle's displayed distance unit."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{self.vin}/custom_command/set_distance_unit",
            json={"unit": unit},
        )

    async def set_time_display_format(
        self, format: TimeDisplayFormat | int
    ) -> dict[str, Any]:
        """Sets the vehicle's displayed clock format (12h/24h)."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{self.vin}/custom_command/set_time_display_format",
            json={"format": format},
        )

    async def set_tire_pressure_unit(
        self, unit: TirePressureUnit | int
    ) -> dict[str, Any]:
        """Sets the vehicle's displayed tire pressure unit."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{self.vin}/custom_command/set_tire_pressure_unit",
            json={"unit": unit},
        )

    async def set_energy_display_format(
        self, format: EnergyDisplayFormat | int
    ) -> dict[str, Any]:
        """Sets the vehicle's displayed energy/range unit (percentage/distance)."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{self.vin}/custom_command/set_energy_display_format",
            json={"format": format},
        )

    async def parental_controls(self, activate: bool, pin: str) -> dict[str, Any]:
        """Activates or deactivates parental controls with a PIN."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{self.vin}/custom_command/parental_controls",
            json={"activate": activate, "pin": pin},
        )

    async def parental_controls_clear_pin(self, pin: str) -> dict[str, Any]:
        """Clears the parental controls PIN."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{self.vin}/custom_command/parental_controls_clear_pin",
            json={"pin": pin},
        )

    async def parental_controls_clear_pin_admin(self) -> dict[str, Any]:
        """Clears the parental controls PIN as admin (fleet manager/owner)."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{self.vin}/custom_command/parental_controls_clear_pin_admin",
        )

    async def parental_controls_enable_setting(
        self, setting: int, enable: bool
    ) -> dict[str, Any]:
        """Enables or disables a parental controls setting (1=speed_limit, 2=acceleration, 3=safety_features, 4=curfew)."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{self.vin}/custom_command/parental_controls_enable_setting",
            json={"setting": setting, "enable": enable},
        )

    async def parental_controls_set_speed_limit(
        self, limit_mph: float
    ) -> dict[str, Any]:
        """Sets the parental controls speed limit."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{self.vin}/custom_command/parental_controls_set_speed_limit",
            json={"limit_mph": limit_mph},
        )

    async def navigation_gps_destination_request(
        self, lat: float, lon: float, destination: str, order: int
    ) -> dict[str, Any]:
        """Navigates to coordinates with a named destination string.

        ``order`` is the Tesla remote-nav order integer: 1 replaces the
        trip, 2 prepends a stop, and 3 appends a stop. Named to match the
        BLE ``Commands.navigation_gps_destination_request`` sibling so
        ``VehicleRouter`` failover can find this method by attribute name.
        """
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{self.vin}/custom_command/navigation_gps_destination",
            json={
                "lat": lat,
                "lon": lon,
                "destination": destination,
                "order": order,
            },
        )

    async def auto_secure_vehicle(self) -> dict[str, Any]:
        """Auto-secures the vehicle (locks, closes windows, etc.)."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{self.vin}/custom_command/auto_secure_vehicle",
        )

    async def cancel_soh_test(self) -> dict[str, Any]:
        """Cancels a State of Health test."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{self.vin}/custom_command/cancel_soh_test",
        )

    async def get_nearby_charging_sites(
        self,
        count: int | None = None,
        radius: int | None = None,
        detail: bool | None = None,
    ) -> dict[str, Any]:
        """Returns the charging sites near the current location of the vehicle."""
        data: dict[str, Any] = {}
        if count is not None:
            data["count"] = count
        if radius is not None:
            data["radius"] = radius
        if detail is not None:
            data["detail"] = detail
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{self.vin}/custom_command/get_nearby_charging_sites",
            json=data,
        )

    async def get_rate_tariff(self) -> dict[str, Any]:
        """Gets the current time-of-use rate tariff schedule."""
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{self.vin}/custom_command/get_rate_tariff",
        )

    async def trigger_rate_tariff_update(self) -> dict[str, Any]:
        """Triggers a time-of-use rate tariff update with no schedule payload.

        Teslemetry's backend does not forward a schedule to the vehicle for
        this route today, so it functions as a trigger, not a configurable
        setter, until a real schema is published. Deliberately not named
        ``set_rate_tariff`` - the BLE ``Commands.set_rate_tariff`` sibling
        takes a required ``seasons``/``tariff`` schedule, and a same-named,
        payload-free method here would raise ``TypeError`` if ``VehicleRouter``
        failover forwarded those arguments to it.
        """
        return await self._request(
            Method.POST,
            f"api/1/vehicles/{self.vin}/custom_command/set_rate_tariff",
        )


class TeslemetryVehicles(Vehicles["Teslemetry"]):
    """Class containing and creating vehicles."""

    _parent: Teslemetry
    Vehicle = TeslemetryVehicle

    def create(self, vin: str) -> TeslemetryVehicle:
        """Creates a specific vehicle."""
        vehicle = self.Vehicle(self._parent, vin)
        self[vin] = vehicle
        return vehicle

    def createFleet(self, vin: str) -> Any:
        """Creates a specific vehicle."""
        raise NotImplementedError("Teslemetry cannot use Fleet API directly")

    def createSigned(self, vin: str) -> Any:
        """Creates a specific vehicle."""
        raise NotImplementedError("Teslemetry cannot use Fleet API directly")

    def createBluetooth(
        self,
        vin: str,
        confirmation: BluetoothConfirmation | bool = "ack",
        keepalive_interval: float | None = None,
        optimistic: bool | None = None,
        raise_unconfirmed: bool = False,
        *,
        verify_commands: bool | None = None,
    ) -> Any:
        """Not supported; parameters match the Fleet API Bluetooth factory."""
        raise NotImplementedError("Teslemetry cannot use local Bluetooth")
