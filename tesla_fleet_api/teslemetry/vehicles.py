from __future__ import annotations

from typing import TYPE_CHECKING, Any

from tesla_fleet_api.const import Method, ClosureState, SeatHeaterLevel
from tesla_fleet_api.tesla.vehicle.vehicles import Vehicles
from tesla_fleet_api.tesla.vehicle.fleet import VehicleFleet
from tesla_fleet_api.const import LOGGER

if TYPE_CHECKING:
    pass

class TeslemetryVehicle(VehicleFleet):
    """Teslemetry specific API vehicle."""

    async def server_side_polling(
        self, value: bool | None = None
    ) -> bool | None:
        """Get or set Auto mode."""
        LOGGER.warning("This method is deprecated and will be removed in a future release.")
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
        data = {}
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
        data = {}
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
        data = {}
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


class TeslemetryVehicles(Vehicles):
    """Class containing and creating vehicles."""

    Vehicle = TeslemetryVehicle

    def create(self, vin: str) -> TeslemetryVehicle:
        """Creates a specific vehicle."""
        vehicle = self.Vehicle(self._parent, vin)
        self[vin] = vehicle
        return vehicle

    def createFleet(self, vin: str):
        """Creates a specific vehicle."""
        raise NotImplementedError("Teslemetry cannot use Fleet API directly")

    def createSigned(self, vin: str):
        """Creates a specific vehicle."""
        raise NotImplementedError("Teslemetry cannot use Fleet API directly")

    def createBluetooth(self, vin: str):
        """Creates a specific vehicle."""
        raise NotImplementedError("Teslemetry cannot use local Bluetooth")
