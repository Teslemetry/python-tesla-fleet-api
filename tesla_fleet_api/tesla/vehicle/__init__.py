"""Tesla Fleet API classes."""

from typing import TYPE_CHECKING, Any

from tesla_fleet_api.tesla.vehicle.vehicles import Vehicles, VehiclesBluetooth
from tesla_fleet_api.tesla.vehicle.fleet import VehicleFleet
from tesla_fleet_api.tesla.vehicle.signed import VehicleSigned
from tesla_fleet_api.tesla.vehicle.vehicle import Vehicle

if TYPE_CHECKING:
    from tesla_fleet_api.tesla.vehicle.bluetooth import (
        VehicleBluetooth as VehicleBluetooth,
    )

__all__ = [
    "Vehicles",
    "VehiclesBluetooth",
    "Vehicle",
    "VehicleFleet",
    "VehicleSigned",
]


def __getattr__(name: str) -> Any:
    # VehicleBluetooth requires bleak (the "ble" extra); import it lazily so
    # importing this package doesn't require bleak to be installed.
    if name == "VehicleBluetooth":
        from tesla_fleet_api.tesla.vehicle.bluetooth import VehicleBluetooth

        return VehicleBluetooth
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
