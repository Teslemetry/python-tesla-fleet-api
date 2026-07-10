from __future__ import annotations
from typing import TYPE_CHECKING, Any, Generic, TypeVar

from bleak.backends.device import BLEDevice
from cryptography.hazmat.primitives.asymmetric import ec

from tesla_fleet_api.tesla.vehicle.signed import VehicleSigned
from tesla_fleet_api.tesla.vehicle.bluetooth import VehicleBluetooth
from tesla_fleet_api.tesla.vehicle.fleet import VehicleFleet
from tesla_fleet_api.tesla.vehicle.vehicle import Vehicle

if TYPE_CHECKING:
    from tesla_fleet_api.tesla.fleet import TeslaFleetApi
    from tesla_fleet_api.tesla.bluetooth import TeslaBluetooth

FleetParentT = TypeVar("FleetParentT", bound="TeslaFleetApi")
BluetoothClientT = TypeVar("BluetoothClientT", bound="TeslaBluetooth")


class Vehicles(dict[str, Vehicle[Any]], Generic[FleetParentT]):
    """Class containing and creating vehicles."""

    _parent: FleetParentT
    Fleet: type[VehicleFleet[FleetParentT]] = VehicleFleet
    Signed: type[VehicleSigned[FleetParentT]] = VehicleSigned
    Bluetooth: type[VehicleBluetooth[FleetParentT]] = VehicleBluetooth

    def __init__(self, parent: FleetParentT):
        self._parent = parent

    def createFleet(self, vin: str) -> VehicleFleet[FleetParentT]:
        """Creates a Fleet API vehicle."""
        vehicle = self.Fleet(self._parent, vin)
        self[vin] = vehicle
        return vehicle

    def createSigned(self, vin: str) -> VehicleSigned[FleetParentT]:
        """Creates a Fleet API vehicle that uses command protocol."""
        vehicle = self.Signed(self._parent, vin)
        self[vin] = vehicle
        return vehicle

    def createBluetooth(
        self, vin: str, verify_commands: bool = False
    ) -> VehicleBluetooth[FleetParentT]:
        """Creates a bluetooth vehicle that uses command protocol."""
        vehicle = self.Bluetooth(self._parent, vin, verify_commands=verify_commands)
        self[vin] = vehicle
        return vehicle

    def specific(self, vin: str) -> VehicleFleet[FleetParentT]:
        """Legacy method for creating a Fleet API vehicle."""
        return self.createFleet(vin)

    def specificSigned(self, vin: str) -> VehicleSigned[FleetParentT]:
        """Legacy method for creating a Fleet API vehicle that uses command protocol."""
        return self.createSigned(vin)


class VehiclesBluetooth(dict[str, Vehicle[Any]], Generic[BluetoothClientT]):
    """Class containing and creating bluetooth vehicles."""

    _parent: BluetoothClientT
    Bluetooth: type[VehicleBluetooth[BluetoothClientT]] = VehicleBluetooth

    def __init__(self, parent: BluetoothClientT):
        self._parent = parent

    def create(
        self,
        vin: str,
        key: ec.EllipticCurvePrivateKey | None = None,
        device: BLEDevice | None = None,
        verify_commands: bool = False,
    ) -> VehicleBluetooth[BluetoothClientT]:
        """Creates a bluetooth vehicle that uses command protocol."""
        return self.createBluetooth(vin, key, device, verify_commands)

    def createBluetooth(
        self,
        vin: str,
        key: ec.EllipticCurvePrivateKey | None = None,
        device: BLEDevice | None = None,
        verify_commands: bool = False,
    ) -> VehicleBluetooth[BluetoothClientT]:
        """Creates a bluetooth vehicle that uses command protocol."""
        vehicle = self.Bluetooth(
            self._parent, vin, key, device, verify_commands=verify_commands
        )
        self[vin] = vehicle
        return vehicle
