from __future__ import annotations
from typing import TYPE_CHECKING, Any, Generic, TypeVar

from bleak.backends.device import BLEDevice
from cryptography.hazmat.primitives.asymmetric import ec

from tesla_fleet_api.tesla.vehicle.signed import VehicleSigned
from tesla_fleet_api.tesla.vehicle.bluetooth import (
    DEFAULT_KEEPALIVE_INTERVAL,
    VehicleBluetooth,
)
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
        self,
        vin: str,
        verify_commands: bool = False,
        keepalive_interval: float | None = DEFAULT_KEEPALIVE_INTERVAL,
        optimistic: bool = False,
        raise_unconfirmed: bool = True,
    ) -> VehicleBluetooth[FleetParentT]:
        """Creates a bluetooth vehicle that uses command protocol.

        Set ``verify_commands`` to confirm supported mutating BLE command
        timeouts by reading the resulting state before surfacing an unconfirmed
        command timeout.
        ``keepalive_interval`` seconds of GATT idleness triggers a passive read
        to hold the link open (``None``/``0`` disables).
        ``optimistic`` returns success as soon as a mutating command's GATT
        write is confirmed, skipping the ack wait and ``verify_commands``.
        ``raise_unconfirmed=False`` resolves an exhausted confirmation ladder
        as a best-effort success instead of raising
        ``BluetoothUnconfirmedCommand``. See ``VehicleBluetooth``'s docstring
        for the full ladder and what each flag does and does not affect.
        """
        vehicle = self.Bluetooth(
            self._parent,
            vin,
            verify_commands=verify_commands,
            keepalive_interval=keepalive_interval,
            optimistic=optimistic,
            raise_unconfirmed=raise_unconfirmed,
        )
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
        keepalive_interval: float | None = DEFAULT_KEEPALIVE_INTERVAL,
        optimistic: bool = False,
        raise_unconfirmed: bool = True,
    ) -> VehicleBluetooth[BluetoothClientT]:
        """Creates a bluetooth vehicle that uses command protocol.

        Set ``verify_commands`` to confirm supported mutating BLE command
        timeouts by reading the resulting state before surfacing an unconfirmed
        command timeout.
        ``keepalive_interval`` seconds of GATT idleness triggers a passive read
        to hold the link open (``None``/``0`` disables).
        ``optimistic`` returns success as soon as a mutating command's GATT
        write is confirmed, skipping the ack wait and ``verify_commands``.
        ``raise_unconfirmed=False`` resolves an exhausted confirmation ladder
        as a best-effort success instead of raising
        ``BluetoothUnconfirmedCommand``. See ``VehicleBluetooth``'s docstring
        for the full ladder and what each flag does and does not affect.
        """
        return self.createBluetooth(
            vin,
            key,
            device,
            verify_commands,
            keepalive_interval,
            optimistic,
            raise_unconfirmed,
        )

    def createBluetooth(
        self,
        vin: str,
        key: ec.EllipticCurvePrivateKey | None = None,
        device: BLEDevice | None = None,
        verify_commands: bool = False,
        keepalive_interval: float | None = DEFAULT_KEEPALIVE_INTERVAL,
        optimistic: bool = False,
        raise_unconfirmed: bool = True,
    ) -> VehicleBluetooth[BluetoothClientT]:
        """Creates a bluetooth vehicle that uses command protocol.

        Set ``verify_commands`` to confirm supported mutating BLE command
        timeouts by reading the resulting state before surfacing an unconfirmed
        command timeout.
        ``keepalive_interval`` seconds of GATT idleness triggers a passive read
        to hold the link open (``None``/``0`` disables).
        ``optimistic`` returns success as soon as a mutating command's GATT
        write is confirmed, skipping the ack wait and ``verify_commands``.
        ``raise_unconfirmed=False`` resolves an exhausted confirmation ladder
        as a best-effort success instead of raising
        ``BluetoothUnconfirmedCommand``. See ``VehicleBluetooth``'s docstring
        for the full ladder and what each flag does and does not affect.
        """
        vehicle = self.Bluetooth(
            self._parent,
            vin,
            key,
            device,
            verify_commands=verify_commands,
            keepalive_interval=keepalive_interval,
            optimistic=optimistic,
            raise_unconfirmed=raise_unconfirmed,
        )
        self[vin] = vehicle
        return vehicle
