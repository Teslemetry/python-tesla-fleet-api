from __future__ import annotations

from tesla_fleet_api.tesla.vehicle.vehicles import Vehicles
from tesla_fleet_api.tesla.vehicle.fleet import VehicleFleet


class TessieVehicle(VehicleFleet):
    """Tessie specific API vehicle."""
    pass

class TessieVehicles(Vehicles):
    """Class containing and creating vehicles."""

    Vehicle = TessieVehicle

    def create(self, vin: str) -> TessieVehicle:
        """Creates a specific vehicle."""
        vehicle = self.Vehicle(self._parent, vin)
        self[vin] = vehicle
        return vehicle

    def createFleet(self, vin: str):
        """Creates a specific vehicle."""
        raise NotImplementedError("Tessie cannot use Fleet API directly")

    def createSigned(self, vin: str):
        """Creates a specific vehicle."""
        raise NotImplementedError("Tessie cannot use Fleet API directly")

    def createBluetooth(self, vin: str):
        """Creates a specific vehicle."""
        raise NotImplementedError("Tessie cannot use local Bluetooth")
