"""Bluetooth only interface."""

import hashlib
import re
from google.protobuf.json_format import MessageToJson, MessageToDict
from bleak.backends.device import BLEDevice
from cryptography.hazmat.primitives.asymmetric import ec

from tesla_fleet_api.tesla.tesla import Tesla
from tesla_fleet_api.tesla.vehicle.bluetooth import VehicleBluetooth

class TeslaBluetooth(Tesla):
    """Class describing a Tesla Bluetooth connection."""

    def __init__(
        self,
    ):
        """Initialize the Tesla Fleet API."""

        self.vehicles = Vehicles(self)

    def valid_name(self, name: str) -> bool:
        """Check if a BLE device name is a valid Tesla vehicle."""
        return bool(re.match("^S[a-f0-9]{16}[CDRP]$", name))

    def get_name(self, vin: str) -> str:
        """Get the name of a vehicle."""
        return "S" + hashlib.sha1(vin.encode('utf-8')).hexdigest()[:16] + "C"

class Vehicles(dict[str, VehicleBluetooth]):
    """Class containing and creating vehicles."""

    _parent: TeslaBluetooth

    def __init__(self, parent: TeslaBluetooth):
        self._parent = parent

    def create(self, vin: str) -> VehicleBluetooth:
        """Creates a specific vehicle."""
        return self.createBluetooth(vin)

    def createBluetooth(self, vin: str, key: ec.EllipticCurvePrivateKey | None = None, device: None | str | BLEDevice = None) -> VehicleBluetooth:
        """Creates a specific vehicle."""
        vehicle = VehicleBluetooth(self._parent, vin, key, device)
        self[vin] = vehicle
        return vehicle

def toJson(message) -> str:
    """Convert a protobuf message to JSON."""
    return MessageToJson(message, preserving_proto_field_name=True)

def toDict(message) -> dict:
    """Convert a protobuf message to a dictionary."""
    return MessageToDict(message, preserving_proto_field_name=True)
