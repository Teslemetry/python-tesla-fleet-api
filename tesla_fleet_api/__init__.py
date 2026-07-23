"""Tesla Fleet API"""

__author__ = "hello@teslemetry.com"
__version__ = "1.7.7"

from tesla_fleet_api.const import Region, is_valid_region
from tesla_fleet_api.tariff import (
    TariffPeriod,
    TariffRate,
    TariffResolution,
    get_tariff_periods,
    unwrap_tariff_v2,
)
from tesla_fleet_api.tesla.bluetooth import TeslaBluetooth
from tesla_fleet_api.tesla.fleet import TeslaFleetApi
from tesla_fleet_api.tesla.oauth import TeslaFleetOAuth
from tesla_fleet_api.teslemetry.teslemetry import Teslemetry
from tesla_fleet_api.tessie.tessie import Tessie
from tesla_fleet_api.util import firmware_at_least, firmware_compare

__all__ = [
    "Region",
    "TariffPeriod",
    "TariffRate",
    "TariffResolution",
    "TeslaFleetApi",
    "TeslaBluetooth",
    "TeslaFleetOAuth",
    "Teslemetry",
    "Tessie",
    "firmware_at_least",
    "firmware_compare",
    "get_tariff_periods",
    "is_valid_region",
    "unwrap_tariff_v2",
]
