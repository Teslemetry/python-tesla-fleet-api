"""Bluetooth only interface."""

import hashlib
import re
from google.protobuf.json_format import MessageToJson, MessageToDict

from tesla_fleet_api.tesla.tesla import Tesla
from tesla_fleet_api.tesla.vehicle.vehicles import VehiclesBluetooth

class TeslaBluetooth(Tesla):
    """Class describing a Tesla Bluetooth connection."""

    Vehicles = VehiclesBluetooth

    def __init__(
        self,
    ):
        """Initialize the Tesla Fleet API."""

        self.vehicles = self.Vehicles(self)

    def valid_name(self, name: str) -> bool:
        """Check if a BLE device name is a valid Tesla vehicle."""
        return bool(re.match("^S[a-f0-9]{16}[CDRP]$", name))

    def get_name(self, vin: str) -> str:
        """Get the name of a vehicle."""
        return "S" + hashlib.sha1(vin.encode('utf-8')).hexdigest()[:16] + "C"


# Helpers

def toJson(message) -> str:
    """Convert a protobuf message to JSON."""
    return MessageToJson(message, preserving_proto_field_name=True)

def toDict(message) -> dict:
    """Convert a protobuf message to a dictionary."""
    return MessageToDict(message, preserving_proto_field_name=True)
