from __future__ import annotations
import asyncio
from typing import TYPE_CHECKING
from bleak import BleakClient
from bleak.backends.device import BLEDevice
from bleak_retry_connector import establish_connection
from cryptography.hazmat.primitives.asymmetric import ec

from tesla_fleet_api.tesla.vehicle.signed import VehicleSigned
from tesla_fleet_api.tesla.vehicle.bluetooth import NAME_UUID, VehicleBluetooth
from tesla_fleet_api.tesla.vehicle.fleet import VehicleFleet
from tesla_fleet_api.tesla.vehicle.vehicle import Vehicle
from tesla_fleet_api.const import LOGGER

if TYPE_CHECKING:
    from tesla_fleet_api.tesla.fleet import TeslaFleetApi
    from tesla_fleet_api.tesla.bluetooth import TeslaBluetooth


class Vehicles(dict[str, Vehicle]):
    """Class containing and creating vehicles."""

    _parent: TeslaFleetApi
    Fleet = VehicleFleet
    Signed = VehicleSigned
    Bluetooth = VehicleBluetooth

    def __init__(self, parent: TeslaFleetApi):
        self._parent = parent

    def createFleet(self, vin: str) -> VehicleFleet:
        """Creates a Fleet API vehicle."""
        vehicle = self.Fleet(self._parent, vin)
        self[vin] = vehicle
        return vehicle

    def createSigned(self, vin: str) -> VehicleSigned:
        """Creates a Fleet API vehicle that uses command protocol."""
        vehicle = self.Signed(self._parent, vin)
        self[vin] = vehicle
        return vehicle

    def createBluetooth(self, vin: str):
        """Creates a bluetooth vehicle that uses command protocol."""
        vehicle = self.Bluetooth(self._parent, vin)
        self[vin] = vehicle
        return vehicle

    def specific(self, vin: str) -> Vehicle:
        """Legacy method for creating a Fleet API vehicle."""
        return self.createFleet(vin)

    def specificSigned(self, vin: str) -> VehicleSigned:
        """Legacy method for creating a Fleet API vehicle that uses command protocol."""
        return self.createSigned(vin)


class VehiclesBluetooth(dict[str, Vehicle]):
    """Class containing and creating bluetooth vehicles."""

    _parent: TeslaBluetooth
    Bluetooth = VehicleBluetooth

    def __init__(self, parent: TeslaBluetooth):
        self._parent = parent

    def create(self, vin: str, key: ec.EllipticCurvePrivateKey | None = None, device: BLEDevice | None = None) -> VehicleBluetooth:
        """Creates a bluetooth vehicle that uses command protocol."""
        return self.createBluetooth(vin, key, device)

    def createBluetooth(self, vin: str, key: ec.EllipticCurvePrivateKey | None = None, device: BLEDevice | None = None) -> VehicleBluetooth:
        """Creates a bluetooth vehicle that uses command protocol."""
        vehicle = self.Bluetooth(self._parent, vin, key, device)
        self[vin] = vehicle
        return vehicle

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
