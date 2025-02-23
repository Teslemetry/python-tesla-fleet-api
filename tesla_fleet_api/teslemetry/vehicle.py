from __future__ import annotations
from typing import TYPE_CHECKING, Any

from ..const import Method
from ..tesla.vehicle.proto.universal_message_pb2 import Domain
from ..tesla.vehicle.vehicle import Vehicle
from ..tesla.vehicle.vehicles import Vehicles
from ..tesla.vehicle.bluetooth import VehicleBluetooth
from ..tesla.vehicle.fleet import VehicleFleet

if TYPE_CHECKING:
    from .teslemetry import Teslemetry

class TeslemetryVehicle(Vehicle):
    """Teslemetry specific base vehicle."""
    pass

class TeslemetryVehicleFleet(VehicleFleet):
    """Teslemetry specific API vehicle."""

    async def server_side_polling(
        self, value: bool | None = None
    ) -> bool | None:
        """Get or set Auto mode."""
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


class TeslemetryVehicles(Vehicles):
    """Class containing and creating vehicles."""

    def create(self, vin: str) -> TeslemetryVehicleFleet:
        """Creates a specific vehicle."""
        return self.createFleet(vin)

    def createFleet(self, vin: str) -> TeslemetryVehicleFleet:
        """Creates a specific vehicle."""
        vehicle = TeslemetryVehicleFleet(self._parent, vin)
        self[vin] = vehicle
        return vehicle

    def createSigned(self, vin: str):
        """Creates a specific vehicle."""
        raise NotImplementedError("Signing is handled by Teslemetry server-side")

    def createBluetooth(self, vin: str):
        """Creates a specific vehicle."""
        raise NotImplementedError("Bluetooth is only handled locally")
