from __future__ import annotations
from typing import TYPE_CHECKING, Any, Generic, Literal, TypeVar

from cryptography.hazmat.primitives.asymmetric import ec

from tesla_fleet_api.const import DEFAULT_KEEPALIVE_INTERVAL, BluetoothConfirmation
from tesla_fleet_api.tesla.vehicle.signed import VehicleSigned
from tesla_fleet_api.tesla.vehicle.fleet import VehicleFleet
from tesla_fleet_api.tesla.vehicle.vehicle import Vehicle

if TYPE_CHECKING:
    from bleak.backends.device import BLEDevice

    from tesla_fleet_api.tesla.fleet import TeslaFleetApi
    from tesla_fleet_api.tesla.bluetooth import TeslaBluetooth
    from tesla_fleet_api.tesla.vehicle.bluetooth import VehicleBluetooth


def _import_vehicle_bluetooth() -> type["VehicleBluetooth[Any]"]:
    """Import VehicleBluetooth on demand so the ``ble`` extra stays optional
    for callers who never create a bluetooth vehicle."""
    try:
        from tesla_fleet_api.tesla.vehicle.bluetooth import VehicleBluetooth
    except ImportError as err:
        raise ImportError(
            "Bluetooth support requires the 'ble' extra: "
            "install with `pip install tesla-fleet-api[ble]`."
        ) from err
    return VehicleBluetooth


FleetParentT = TypeVar("FleetParentT", bound="TeslaFleetApi")
BluetoothClientT = TypeVar("BluetoothClientT", bound="TeslaBluetooth")


class Vehicles(dict[str, Vehicle[Any]], Generic[FleetParentT]):
    """Class containing and creating vehicles."""

    _parent: FleetParentT
    Fleet: type[VehicleFleet[FleetParentT]] = VehicleFleet
    Signed: type[VehicleSigned[FleetParentT]] = VehicleSigned

    def __init__(self, parent: FleetParentT):
        self._parent = parent

    @property
    def Bluetooth(self) -> type[VehicleBluetooth[FleetParentT]]:
        """The bluetooth vehicle class, imported on demand so the ``ble``
        extra stays optional for callers who never create one."""
        return _import_vehicle_bluetooth()

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
        key: ec.EllipticCurvePrivateKey | Literal[False] | None = None,
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
        ``key=False`` explicitly disables signing, for a passive listener;
        ``key=None`` (the default) keeps the usual parent-key fallback.
        """
        vehicle = self.Bluetooth(
            self._parent,
            vin,
            key,
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

    def __init__(self, parent: BluetoothClientT):
        self._parent = parent

    @property
    def Bluetooth(self) -> type[VehicleBluetooth[BluetoothClientT]]:
        """The bluetooth vehicle class, imported on demand so the ``ble``
        extra stays optional for callers who never create one."""
        return _import_vehicle_bluetooth()

    def create(
        self,
        vin: str,
        key: ec.EllipticCurvePrivateKey | Literal[False] | None = None,
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
        ``key=False`` explicitly disables signing, for a passive listener;
        ``key=None`` (the default) keeps the usual parent-key fallback.
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
        key: ec.EllipticCurvePrivateKey | Literal[False] | None = None,
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
        ``key=False`` explicitly disables signing, for a passive listener;
        ``key=None`` (the default) keeps the usual parent-key fallback.
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
