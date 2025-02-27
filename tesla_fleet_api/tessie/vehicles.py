from __future__ import annotations

from tesla_fleet_api.tesla.vehicle.vehicle import Vehicle
from tesla_fleet_api.tesla.vehicle.vehicles import Vehicles
from tesla_fleet_api.tesla.vehicle.fleet import VehicleFleet


class TessieVehicle(Vehicle):
    """Tessie specific base vehicle."""
    pass

class TessieVehicleFleet(VehicleFleet):
    """Tessie specific API vehicle."""
    pass

class TessieVehicles(Vehicles):
    """Class containing and creating vehicles."""

    Fleet = TessieVehicleFleet

    def create(self, vin: str) -> TessieVehicleFleet:
        """Creates a specific vehicle."""
        return self.createFleet(vin)

    def createFleet(self, vin: str) -> TessieVehicleFleet:
        """Creates a specific vehicle."""
        vehicle = self.Fleet(self._parent, vin)
        self[vin] = vehicle
        return vehicle

    def createSigned(self, vin: str):
        """Creates a specific vehicle."""
        raise NotImplementedError("Signing is handled by Tessie server-side")

    def createBluetooth(self, vin: str):
        """Creates a specific vehicle."""
        raise NotImplementedError("Bluetooth is only handled locally")
