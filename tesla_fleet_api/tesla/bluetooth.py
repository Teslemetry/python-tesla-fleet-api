"""Bluetooth only interface."""

import re
from .tesla import Tesla
from .vehicle.bluetooth import VehicleBluetooth

class TeslaBluetooth(Tesla):
    """Class describing a Tesla Bluetooth connection."""

    def __init__(
        self,
    ):
        """Initialize the Tesla Fleet API."""

        self.vehicles = Vehicles(self)

    def valid_name(self, name: str) -> bool:
        """Check if a BLE device name is a valid Tesla vehicle."""
        return bool(re.match("^S[a-f0-9]{16}[A-F]$", name))

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
