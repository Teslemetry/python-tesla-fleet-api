"""Bluetooth only interface."""

from tesla_fleet_api.tesla.tesla import Tesla
from tesla_fleet_api.tesla.vehicle.bluetooth import VehicleBluetooth

class TeslaBluetooth(Tesla):
    """Class describing a Tesla Bluetooth connection."""

    def __init__(
        self,
    ):
        """Initialize the Tesla Fleet API."""

        self.vehicles = Vehicles(self)

class Vehicles(dict[str, VehicleBluetooth]):
    """Class containing and creating vehicles."""

    _parent: TeslaBluetooth

    def __init__(self, parent: TeslaBluetooth):
        self._parent = parent

    def createBluetooth(self, vin: str) -> VehicleBluetooth:
        """Creates a specific vehicle."""
        vehicle = VehicleBluetooth(self._parent, vin)
        self[vin] = vehicle
        return vehicle
