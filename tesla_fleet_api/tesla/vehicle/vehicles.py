from __future__ import annotations
from typing import TYPE_CHECKING, Any, Generic, TypeVar

from bleak.backends.device import BLEDevice
from cryptography.hazmat.primitives.asymmetric import ec

from tesla_fleet_api.const import BluetoothConfirmation
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
        confirmation: BluetoothConfirmation | bool = "ack",
        keepalive_interval: float | None = DEFAULT_KEEPALIVE_INTERVAL,
        optimistic: bool | None = None,
        raise_unconfirmed: bool = False,
        *,
        verify_commands: bool | None = None,
    ) -> VehicleBluetooth[FleetParentT]:
        """Creates a bluetooth vehicle that uses command protocol.

        ``confirmation`` sets the confirmation ladder depth: ``"optimistic"``
        skips reply waits after a confirmed write, ``"ack"`` (default) waits
        for an addressed ack or a matching state broadcast, ``"verify"``
        additionally reads back state on an ack/broadcast timeout.
        ``keepalive_interval`` seconds of GATT idleness triggers a passive read
        to hold the link open (``None``/``0`` disables).
        ``raise_unconfirmed=True`` raises ``BluetoothUnconfirmedCommand``
        instead of resolving a still-inconclusive ladder as a best-effort
        success. ``verify_commands``/``optimistic`` are deprecated aliases for
        ``confirmation="verify"``/``confirmation="optimistic"``. See
        ``VehicleBluetooth``'s docstring for the full ladder.
        """
        vehicle = self.Bluetooth(
            self._parent,
            vin,
            confirmation=confirmation,
            keepalive_interval=keepalive_interval,
            optimistic=optimistic,
            raise_unconfirmed=raise_unconfirmed,
            verify_commands=verify_commands,
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
        confirmation: BluetoothConfirmation | bool = "ack",
        keepalive_interval: float | None = DEFAULT_KEEPALIVE_INTERVAL,
        optimistic: bool | None = None,
        raise_unconfirmed: bool = False,
        *,
        verify_commands: bool | None = None,
    ) -> VehicleBluetooth[BluetoothClientT]:
        """Creates a bluetooth vehicle that uses command protocol.

        ``confirmation`` sets the confirmation ladder depth: ``"optimistic"``
        skips reply waits after a confirmed write, ``"ack"`` (default) waits
        for an addressed ack or a matching state broadcast, ``"verify"``
        additionally reads back state on an ack/broadcast timeout.
        ``keepalive_interval`` seconds of GATT idleness triggers a passive read
        to hold the link open (``None``/``0`` disables).
        ``raise_unconfirmed=True`` raises ``BluetoothUnconfirmedCommand``
        instead of resolving a still-inconclusive ladder as a best-effort
        success. ``verify_commands``/``optimistic`` are deprecated aliases for
        ``confirmation="verify"``/``confirmation="optimistic"``. See
        ``VehicleBluetooth``'s docstring for the full ladder.
        """
        return self.createBluetooth(
            vin,
            key,
            device,
            confirmation,
            keepalive_interval,
            optimistic,
            raise_unconfirmed,
            verify_commands=verify_commands,
        )

    def createBluetooth(
        self,
        vin: str,
        key: ec.EllipticCurvePrivateKey | None = None,
        device: BLEDevice | None = None,
        confirmation: BluetoothConfirmation | bool = "ack",
        keepalive_interval: float | None = DEFAULT_KEEPALIVE_INTERVAL,
        optimistic: bool | None = None,
        raise_unconfirmed: bool = False,
        *,
        verify_commands: bool | None = None,
    ) -> VehicleBluetooth[BluetoothClientT]:
        """Creates a bluetooth vehicle that uses command protocol.

        ``confirmation`` sets the confirmation ladder depth: ``"optimistic"``
        skips reply waits after a confirmed write, ``"ack"`` (default) waits
        for an addressed ack or a matching state broadcast, ``"verify"``
        additionally reads back state on an ack/broadcast timeout.
        ``keepalive_interval`` seconds of GATT idleness triggers a passive read
        to hold the link open (``None``/``0`` disables).
        ``raise_unconfirmed=True`` raises ``BluetoothUnconfirmedCommand``
        instead of resolving a still-inconclusive ladder as a best-effort
        success. ``verify_commands``/``optimistic`` are deprecated aliases for
        ``confirmation="verify"``/``confirmation="optimistic"``. See
        ``VehicleBluetooth``'s docstring for the full ladder.
        """
        vehicle = self.Bluetooth(
            self._parent,
            vin,
            key,
            device,
            confirmation=confirmation,
            keepalive_interval=keepalive_interval,
            optimistic=optimistic,
            raise_unconfirmed=raise_unconfirmed,
            verify_commands=verify_commands,
        )
        self[vin] = vehicle
        return vehicle
