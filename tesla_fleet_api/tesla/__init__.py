"""Tesla Fleet API classes."""

from typing import TYPE_CHECKING, Any

from tesla_fleet_api.tesla.fleet import TeslaFleetApi
from tesla_fleet_api.tesla.oauth import TeslaFleetOAuth
from tesla_fleet_api.tesla.charging import Charging
from tesla_fleet_api.tesla.energysite import EnergySites, EnergySite
from tesla_fleet_api.tesla.partner import Partner
from tesla_fleet_api.router import (
    Router,
    VehicleRouter,
    EnergySiteRouter,
    LOCAL_LIVE_STATUS_KEYS,
    LOCAL_SITE_INFO_KEYS,
    merge_local_into_cloud,
    merge_live_status,
    merge_site_info,
)
from tesla_fleet_api.tesla.user import User
from tesla_fleet_api.tesla.vehicle import (
    Vehicles,
    VehiclesBluetooth,
    VehicleFleet,
    VehicleSigned,
    Vehicle,
)
from tesla_fleet_api.util import import_ble_class

if TYPE_CHECKING:
    from tesla_fleet_api.tesla.bluetooth import TeslaBluetooth as TeslaBluetooth
    from tesla_fleet_api.tesla.vehicle import VehicleBluetooth as VehicleBluetooth

__all__ = [
    "TeslaFleetApi",
    "TeslaFleetOAuth",
    "Charging",
    "EnergySites",
    "EnergySite",
    "EnergySiteRouter",
    "Partner",
    "User",
    "Vehicles",
    "Vehicle",
    "VehiclesBluetooth",
    "VehicleFleet",
    "VehicleSigned",
    "Router",
    "VehicleRouter",
    "LOCAL_LIVE_STATUS_KEYS",
    "LOCAL_SITE_INFO_KEYS",
    "merge_local_into_cloud",
    "merge_live_status",
    "merge_site_info",
]


def __getattr__(name: str) -> Any:
    # TeslaBluetooth/VehicleBluetooth require bleak (the "ble" extra);
    # import them lazily so importing this package doesn't require bleak.
    if name == "TeslaBluetooth":
        return import_ble_class("tesla_fleet_api.tesla.bluetooth", "TeslaBluetooth")
    if name == "VehicleBluetooth":
        return import_ble_class(
            "tesla_fleet_api.tesla.vehicle.bluetooth", "VehicleBluetooth"
        )
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
