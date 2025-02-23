from __future__ import annotations
from typing import TYPE_CHECKING

from .signed import VehicleSigned
from .bluetooth import VehicleBluetooth
from .fleet import VehicleFleet
from .vehicle import Vehicle

if TYPE_CHECKING:
    from ..fleet import TeslaFleetApi



class Vehicles(dict[str, Vehicle]):
    """Class containing and creating vehicles."""

    _parent: TeslaFleetApi

    def __init__(self, parent: TeslaFleetApi):
        self._parent = parent

    def createFleet(self, vin: str) -> VehicleFleet:
        """Creates a Fleet API vehicle."""
        vehicle = VehicleFleet(self._parent, vin)
        self[vin] = vehicle
        return vehicle

    def createSigned(self, vin: str) -> VehicleSigned:
        """Creates a Fleet API vehicle that uses command protocol."""
        vehicle = VehicleSigned(self._parent, vin)
        self[vin] = vehicle
        return vehicle

    def createBluetooth(self, vin: str) -> VehicleBluetooth:
        """Creates a bluetooth vehicle that uses command protocol."""
        vehicle = VehicleBluetooth(self._parent, vin)
        self[vin] = vehicle
        return vehicle

    def specific(self, vin: str) -> Vehicle:
        """Legacy method for creating a Fleet API vehicle."""
        return self.createFleet(vin)

    def specificSigned(self, vin: str) -> VehicleSigned:
        """Legacy method for creating a Fleet API vehicle that uses command protocol."""
        return self.createSigned(vin)
