from __future__ import annotations
from typing import TYPE_CHECKING
from .signed import VehicleSigned
from .bluetooth import VehicleBluetooth
from .fleet import VehicleFleet

if TYPE_CHECKING:
    from ..tesla import TeslaFleetApi


class Vehicle:
    """Base class describing a Tesla vehicle."""

    vin: str

    def __init__(self, parent: TeslaFleetApi, vin: str):
        self.vin = vin

    def pre2021(self, vin: str) -> bool:
        """Checks if a vehicle is a pre-2021 model S or X."""
        return vin[3] in ["S", "X"] and (vin[9] <= "L" or (vin[9] == "M" and vin[7] in ['1', '2', '3', '4']))

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
