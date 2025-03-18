"""Tesla Fleet API constants."""

from enum import Enum
import logging

VERSION = "1.0.13"
LOGGER = logging.getLogger(__package__)
SERVERS = {
    "na": "https://fleet-api.prd.na.vn.cloud.tesla.com",
    "eu": "https://fleet-api.prd.eu.vn.cloud.tesla.com",
    "cn": "https://fleet-api.prd.cn.vn.cloud.tesla.cn",
}


class IntEnum(int, Enum):
    """Integer Enum."""

    def __str__(self) -> str:
        return str(self.value)


class StrEnum(str, Enum):
    """String Enum."""

    def __str__(self) -> str:
        return self.value


class Method(StrEnum):
    """HTTP Methods."""

    GET = "GET"
    POST = "POST"
    DELETE = "DELETE"


class Trunk(StrEnum):
    """Trunk options"""

    FRONT = "front"
    REAR = "rear"


class Seat(IntEnum):
    """Seat positions"""

    FRONT_LEFT = 0
    FRONT_RIGHT = 1
    REAR_LEFT = 2
    REAT_LEFT_BACK = 3
    REAR_CENTER = 4
    REAR_RIGHT = 5
    REAR_RIGHT_BACK = 6
    THIRD_LEFT = 7
    THIRD_RIGHT = 8

class AutoSeat(IntEnum):
    """Auto Climate Seat positions"""

    FRONT_LEFT = 1
    FRONT_RIGHT = 2


class Level(IntEnum):
    """Level options"""

    OFF = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3


class ClimateKeeperMode(IntEnum):
    """Climate Keeper Mode options"""

    OFF = 0
    KEEP_MODE = 1
    DOG_MODE = 2
    CAMP_MODE = 3


class CabinOverheatProtectionTemp(IntEnum):
    """COP Temp options"""

    LOW = 0  # 30C 90F
    MEDIUM = 1  # 35C 95F
    HIGH = 2  # 40C 100F


class VehicleDataEndpoint(StrEnum):
    """Endpoints options"""

    CHARGE_STATE = "charge_state"
    CLIMATE_STATE = "climate_state"
    CLOSURES_STATE = "closures_state"
    DRIVE_STATE = "drive_state"
    GUI_SETTINGS = "gui_settings"
    LOCATION_DATA = "location_data"
    CHARGE_SCHEDULE_DATA = "charge_schedule_data"
    PRECONDITIONING_SCHEDULE_DATA = "preconditioning_schedule_data"
    VEHICLE_CONFIG = "vehicle_config"
    VEHICLE_STATE = "vehicle_state"
    VEHICLE_DATA_COMBO = "vehicle_data_combo"



class SunRoofCommand(StrEnum):
    """Sunroof options"""

    STOP = "stop"
    CLOSE = "close"
    VENT = "vent"


class WindowCommand(StrEnum):
    """Window Control options"""

    VENT = "vent"
    CLOSE = "close"


class DeviceType(StrEnum):
    """Device Type options"""

    ANDROID = "android"
    IOS_DEVELOPMENT = "ios-development"
    IOS_ENTERPRISE = "ios-enterprise"
    IOS_BETA = "ios-beta"
    IOS_PRODUCTION = "ios-production"


class Scope(StrEnum):
    """Fleet API Scope"""

    OPENID = "openid"
    OFFLINE_ACCESS = "offline_access"
    USER_DATA = "user_data"
    VEHICLE_DEVICE_DATA = "vehicle_device_data"
    VEHICLE_LOCATION = "vehicle_location"
    VEHICLE_CMDS = "vehicle_cmds"
    VEHICLE_CHARGING_CMDS = "vehicle_charging_cmds"
    ENERGY_DEVICE_DATA = "energy_device_data"
    ENERGY_CMDS = "energy_cmds"


class EnergyOperationMode(StrEnum):
    """Energy Operation Mode options"""

    AUTONOMOUS = "autonomous"
    SELF_CONSUMPTION = "self_consumption"
    BACKUP = "backup"


class EnergyExportMode(StrEnum):
    """Energy Export Mode options"""

    BATTERY_OK = "battery_ok"
    PV_ONLY = "pv_only"
    NEVER = "never"


class TeslaEnergyPeriod(StrEnum):
    """Period for history for energy sites"""

    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"
    LIFETIME = "lifetime"

class BluetoothVehicleData(StrEnum):
    CHARGE_STATE = "GetChargeState"
    CLIMATE_STATE = "GetClimateState"
    DRIVE_STATE = "GetDriveState"
    LOCATION_STATE = "GetLocationState"
    CLOSURES_STATE = "GetClosuresState"
    CHARGE_SCHEDULE_STATE = "GetChargeScheduleState"
    PRECONDITIONING_SCHEDULE_STATE = "GetPreconditioningScheduleState"
    TIRE_PRESSURE_STATE = "GetTirePressureState"
    MEDIA_STATE = "GetMediaState"
    MEDIA_DETAIL_STATE = "GetMediaDetailState"
    SOFTWARE_UPDATE_STATE = "GetSoftwareUpdateState"
    PARENTAL_CONTROLS_STATE = "GetParentalControlsState"
