from __future__ import annotations
from typing import TYPE_CHECKING, Any

from ..const import Method
from ..tesla.vehicle.proto.universal_message_pb2 import Domain
from ..tesla.vehicle.vehicle import Vehicle
from ..tesla.vehicle.vehicles import Vehicles
from ..tesla.vehicle.bluetooth import VehicleBluetooth
from ..tesla.vehicle.fleet import VehicleFleet

if TYPE_CHECKING:
    from .tessie import Tessie

class TessieVehicle(Vehicle):
    """Tessie specific base vehicle."""
    pass

class TessieVehicleFleet(VehicleFleet):
    """Tessie specific API vehicle."""
    pass

class TessieVehicles(Vehicles):
    """Class containing and creating vehicles."""

    def create(self, vin: str) -> TessieVehicleFleet:
        """Creates a specific vehicle."""
        return self.createFleet(vin)

    def createFleet(self, vin: str) -> TessieVehicleFleet:
        """Creates a specific vehicle."""
        vehicle = TessieVehicleFleet(self._parent, vin)
        self[vin] = vehicle
        return vehicle

    def createSigned(self, vin: str):
        """Creates a specific vehicle."""
        raise NotImplementedError("Signing is handled by Tessie server-side")

    def createBluetooth(self, vin: str):
        """Creates a specific vehicle."""
        raise NotImplementedError("Bluetooth is only handled locally")
