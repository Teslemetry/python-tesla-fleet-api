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
        """Creates a specific vehicle."""
        vehicle = VehicleFleet(self._parent, vin)
        self[vin] = vehicle
        return vehicle

    def createSigned(self, vin: str) -> VehicleSigned:
        """Creates a specific vehicle."""
        vehicle = VehicleSigned(self._parent, vin)
        self[vin] = vehicle
        return vehicle

    def createBluetooth(self, vin: str) -> VehicleBluetooth:
        """Creates a specific vehicle."""
        vehicle = VehicleBluetooth(self._parent, vin)
        self[vin] = vehicle
        return vehicle
