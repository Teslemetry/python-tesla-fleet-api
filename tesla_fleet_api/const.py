"""Tesla Fleet API constants."""

from enum import Enum
import logging

VERSION = "0.8.4"
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
    REAR_CENTER = 4
    REAR_RIGHT = 5
    THIRD_LEFT = 6
    THIRD_RIGHT = 7


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


class TelemetryField(StrEnum):
    """Fields available in telemetry streams"""

    AC_CHARGING_ENERGY_IN = "ACChargingEnergyIn"
    AC_CHARGING_POWER = "ACChargingPower"
    AUTO_SEAT_CLIMATE_LEFT = "AutoSeatClimateLeft"
    AUTO_SEAT_CLIMATE_RIGHT = "AutoSeatClimateRight"
    AUTOMATIC_BLIND_SPOT_CAMERA = "AutomaticBlindSpotCamera"
    AUTOMATIC_EMERGENCY_BRAKING_OFF = "AutomaticEmergencyBrakingOff"
    BMS_STATE = "BMSState"
    BATTERY_HEATER_ON = "BatteryHeaterOn"
    BATTERY_LEVEL = "BatteryLevel"
    BLIND_SPOT_COLLISION_WARNING_CHIME = "BlindSpotCollisionWarningChime"
    BMS_FULL_CHARGE_COMPLETE = "BmsFullchargecomplete"
    BRAKE_PEDAL = "BrakePedal"
    BRAKE_PEDAL_POS = "BrakePedalPos"
    BRICK_VOLTAGE_MAX = "BrickVoltageMax"
    BRICK_VOLTAGE_MIN = "BrickVoltageMin"
    CAR_TYPE = "CarType"
    CHARGE_AMPS = "ChargeAmps"
    CHARGE_CURRENT_REQUEST = "ChargeCurrentRequest"
    CHARGE_CURRENT_REQUEST_MAX = "ChargeCurrentRequestMax"
    CHARGE_ENABLE_REQUEST = "ChargeEnableRequest"
    CHARGE_LIMIT_SOC = "ChargeLimitSoc"
    CHARGE_PORT = "ChargePort"
    CHARGE_PORT_COLD_WEATHER_MODE = "ChargePortColdWeatherMode"
    CHARGE_PORT_LATCH = "ChargePortLatch"
    CHARGE_STATE = "ChargeState"
    CHARGER_PHASES = "ChargerPhases"
    CRUISE_FOLLOW_DISTANCE = "CruiseFollowDistance"
    CRUISE_SET_SPEED = "CruiseSetSpeed"
    CRUISE_STATE = "CruiseState"
    CURRENT_LIMIT_MPH = "CurrentLimitMph"
    DC_CHARGING_ENERGY_IN = "DCChargingEnergyIn"
    DC_CHARGING_POWER = "DCChargingPower"
    DC_DC_ENABLE = "DCDCEnable"
    DESTINATION_LOCATION = "DestinationLocation"
    DI_AXLE_SPEED_F = "DiAxleSpeedF"
    DI_AXLE_SPEED_R = "DiAxleSpeedR"
    DI_AXLE_SPEED_REL = "DiAxleSpeedREL"
    DI_AXLE_SPEED_RER = "DiAxleSpeedRER"
    DI_HEATSINK_TF = "DiHeatsinkTF"
    DI_HEATSINK_TR = "DiHeatsinkTR"
    DI_HEATSINK_TREL = "DiHeatsinkTREL"
    DI_HEATSINK_TRER = "DiHeatsinkTRER"
    DI_MOTOR_CURRENT_F = "DiMotorCurrentF"
    DI_MOTOR_CURRENT_R = "DiMotorCurrentR"
    DI_MOTOR_CURRENT_REL = "DiMotorCurrentREL"
    DI_MOTOR_CURRENT_RER = "DiMotorCurrentRER"
    DI_SLAVE_TORQUE_CMD = "DiSlaveTorqueCmd"
    DI_STATE_F = "DiStateF"
    DI_STATE_R = "DiStateR"
    DI_STATE_REL = "DiStateREL"
    DI_STATE_RER = "DiStateRER"
    DI_STATOR_TEMP_F = "DiStatorTempF"
    DI_STATOR_TEMP_R = "DiStatorTempR"
    DI_STATOR_TEMP_REL = "DiStatorTempREL"
    DI_STATOR_TEMP_RER = "DiStatorTempRER"
    DI_TORQUE_ACTUAL_F = "DiTorqueActualF"
    DI_TORQUE_ACTUAL_R = "DiTorqueActualR"
    DI_TORQUE_ACTUAL_REL = "DiTorqueActualREL"
    DI_TORQUE_ACTUAL_RER = "DiTorqueActualRER"
    DI_TORQUEMOTOR = "DiTorquemotor"
    DI_V_BAT_F = "DiVBatF"
    DI_V_BAT_R = "DiVBatR"
    DI_V_BAT_REL = "DiVBatREL"
    DI_V_BAT_RER = "DiVBatRER"
    DOOR_STATE = "DoorState"
    DRIVE_RAIL = "DriveRail"
    DRIVER_SEAT_BELT = "DriverSeatBelt"
    DRIVER_SEAT_OCCUPIED = "DriverSeatOccupied"
    EMERGENCY_LANE_DEPARTURE_AVOIDANCE = "EmergencyLaneDepartureAvoidance"
    ENERGY_REMAINING = "EnergyRemaining"
    EST_BATTERY_RANGE = "EstBatteryRange"
    # EXPERIMENTAL_1 = "Experimental_1"
    # EXPERIMENTAL_2 = "Experimental_2"
    # EXPERIMENTAL_3 = "Experimental_3"
    # EXPERIMENTAL_4 = "Experimental_4"
    EXTERIOR_COLOR = "ExteriorColor"
    FAST_CHARGER_PRESENT = "FastChargerPresent"
    FD_WINDOW = "FdWindow"
    FORWARD_COLLISION_WARNING = "ForwardCollisionWarning"
    FP_WINDOW = "FpWindow"
    GEAR = "Gear"
    GPS_HEADING = "GpsHeading"
    GPS_STATE = "GpsState"
    GUEST_MODE_ENABLED = "GuestModeEnabled"
    GUEST_MODE_MOBILE_ACCESS_STATE = "GuestModeMobileAccessState"
    HVIL = "Hvil"
    IDEAL_BATTERY_RANGE = "IdealBatteryRange"
    INSIDE_TEMP = "InsideTemp"
    ISOLATION_RESISTANCE = "IsolationResistance"
    LANE_DEPARTURE_AVOIDANCE = "LaneDepartureAvoidance"
    LATERAL_ACCELERATION = "LateralAcceleration"
    LIFETIME_ENERGY_GAINED_REGEN = "LifetimeEnergyGainedRegen"
    LIFETIME_ENERGY_USED = "LifetimeEnergyUsed"
    LIFETIME_ENERGY_USED_DRIVE = "LifetimeEnergyUsedDrive"
    LOCATION = "Location"
    LOCKED = "Locked"
    LONGITUDINAL_ACCELERATION = "LongitudinalAcceleration"
    MILES_TO_ARRIVAL = "MilesToArrival"
    MINUTES_TO_ARRIVAL = "MinutesToArrival"
    MODULE_TEMP_MAX = "ModuleTempMax"
    MODULE_TEMP_MIN = "ModuleTempMin"
    NOT_ENOUGH_POWER_TO_HEAT = "NotEnoughPowerToHeat"
    NUM_BRICK_VOLTAGE_MAX = "NumBrickVoltageMax"
    NUM_BRICK_VOLTAGE_MIN = "NumBrickVoltageMin"
    NUM_MODULE_TEMP_MAX = "NumModuleTempMax"
    NUM_MODULE_TEMP_MIN = "NumModuleTempMin"
    ODOMETER = "Odometer"
    ORIGIN_LOCATION = "OriginLocation"
    OUTSIDE_TEMP = "OutsideTemp"
    PACK_CURRENT = "PackCurrent"
    PACK_VOLTAGE = "PackVoltage"
    PAIRED_PHONE_KEY_AND_KEY_FOB_QTY = "PairedPhoneKeyAndKeyFobQty"
    PASSENGER_SEAT_BELT = "PassengerSeatBelt"
    PEDAL_POSITION = "PedalPosition"
    PIN_TO_DRIVE_ENABLED = "PinToDriveEnabled"
    PRECONDITIONING_ENABLED = "PreconditioningEnabled"
    RATED_RANGE = "RatedRange"
    RD_WINDOW = "RdWindow"
    ROOF_COLOR = "RoofColor"
    ROUTE_LAST_UPDATED = "RouteLastUpdated"
    ROUTE_LINE = "RouteLine"
    RP_WINDOW = "RpWindow"
    SCHEDULED_CHARGING_MODE = "ScheduledChargingMode"
    SCHEDULED_CHARGING_PENDING = "ScheduledChargingPending"
    SCHEDULED_CHARGING_START_TIME = "ScheduledChargingStartTime"
    SCHEDULED_DEPARTURE_TIME = "ScheduledDepartureTime"
    SEAT_HEATER_LEFT = "SeatHeaterLeft"
    SEAT_HEATER_REAR_CENTER = "SeatHeaterRearCenter"
    SEAT_HEATER_REAR_LEFT = "SeatHeaterRearLeft"
    SEAT_HEATER_REAR_RIGHT = "SeatHeaterRearRight"
    SEAT_HEATER_RIGHT = "SeatHeaterRight"
    SENTRY_MODE = "SentryMode"
    SERVICE_MODE = "ServiceMode"
    SOC = "Soc"
    SPEED_LIMIT_MODE = "SpeedLimitMode"
    SPEED_LIMIT_WARNING = "SpeedLimitWarning"
    SUPERCHARGER_SESSION_TRIP_PLANNER = "SuperchargerSessionTripPlanner"
    TIME_TO_FULL_CHARGE = "TimeToFullCharge"
    TPMS_LAST_SEEN_PRESSURE_TIME_FL = "TpmsLastSeenPressureTimeFl"
    TPMS_LAST_SEEN_PRESSURE_TIME_FR = "TpmsLastSeenPressureTimeFr"
    TPMS_LAST_SEEN_PRESSURE_TIME_RL = "TpmsLastSeenPressureTimeRl"
    TPMS_LAST_SEEN_PRESSURE_TIME_RR = "TpmsLastSeenPressureTimeRr"
    TPMS_PRESSURE_FL = "TpmsPressureFl"
    TPMS_PRESSURE_FR = "TpmsPressureFr"
    TPMS_PRESSURE_RL = "TpmsPressureRl"
    TPMS_PRESSURE_RR = "TpmsPressureRr"
    TRIM = "Trim"
    VEHICLE_NAME = "VehicleName"
    VEHICLE_SPEED = "VehicleSpeed"
    VERSION = "Version"


class TelemetryAlert(StrEnum):
    """Alerts available in telemetry streams"""

    CUSTOMER = "Customer"
    SERVICE = "Service"
    SERVICE_FIX = "ServiceFix"


class TeslaEnergyPeriod(StrEnum):
    """Period for history for energy sites"""

    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"
    LIFETIME = "lifetime"
