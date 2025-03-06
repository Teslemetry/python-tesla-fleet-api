"""Bluetooth only interface."""

import asyncio
import hashlib
import re
from bleak import BleakClient
from bleak.backends.device import BLEDevice
from bleak_retry_connector import establish_connection
from google.protobuf.json_format import MessageToJson, MessageToDict

from tesla_fleet_api.const import LOGGER
from tesla_fleet_api.tesla.tesla import Tesla
from tesla_fleet_api.tesla.vehicle.bluetooth import NAME_UUID
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

    async def query_display_name(self, device: BLEDevice, max_attempts=5) -> str | None:
        """Queries the name of a bluetooth vehicle."""
        client = await establish_connection(
            BleakClient,
            device,
            device.name or "Unknown",
            max_attempts=max_attempts
        )
        name: str | None = None
        for i in range(max_attempts):
            try:
                # Standard GATT Device Name characteristic (0x2A00)
                device_name = (await client.read_gatt_char(NAME_UUID)).decode('utf-8')
                if device_name.startswith("🔑 "):
                    name = device_name.replace("🔑 ","")
                    break
                await asyncio.sleep(1)
                LOGGER.debug(f"Attempt {i+1} to query display name failed, {device_name}")
            except Exception as e:
                LOGGER.error(f"Failed to read device name: {e}")

        await client.disconnect()
        return name


# Helpers

def toJson(message) -> str:
    """Convert a protobuf message to JSON."""
    return MessageToJson(message, preserving_proto_field_name=True)

def toDict(message) -> dict:
    """Convert a protobuf message to a dictionary."""
    return MessageToDict(message, preserving_proto_field_name=True)
