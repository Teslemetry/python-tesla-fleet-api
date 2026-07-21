from google.protobuf import wrappers_pb2 as _wrappers_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ChargeOnSolarNoChargeReason(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CHARGE_ON_SOLAR_NO_CHARGE_REASON_INVALID: _ClassVar[ChargeOnSolarNoChargeReason]
    CHARGE_ON_SOLAR_NO_CHARGE_REASON_POWERWALL_CHARGE_PRIORITY: _ClassVar[ChargeOnSolarNoChargeReason]
    CHARGE_ON_SOLAR_NO_CHARGE_REASON_INSUFFICIENT_SOLAR: _ClassVar[ChargeOnSolarNoChargeReason]
    CHARGE_ON_SOLAR_NO_CHARGE_REASON_GRID_EXPORT_PRIORITY: _ClassVar[ChargeOnSolarNoChargeReason]
    CHARGE_ON_SOLAR_NO_CHARGE_REASON_ALTERNATE_VEHICLE_CHARGE_PRIORITY: _ClassVar[ChargeOnSolarNoChargeReason]

class ErrorCode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ERROR_CODE_INVALID: _ClassVar[ErrorCode]
    ERROR_CODE_FEATURE_NOT_SUPPORTED: _ClassVar[ErrorCode]
    ERROR_CODE_INTERNAL: _ClassVar[ErrorCode]
CHARGE_ON_SOLAR_NO_CHARGE_REASON_INVALID: ChargeOnSolarNoChargeReason
CHARGE_ON_SOLAR_NO_CHARGE_REASON_POWERWALL_CHARGE_PRIORITY: ChargeOnSolarNoChargeReason
CHARGE_ON_SOLAR_NO_CHARGE_REASON_INSUFFICIENT_SOLAR: ChargeOnSolarNoChargeReason
CHARGE_ON_SOLAR_NO_CHARGE_REASON_GRID_EXPORT_PRIORITY: ChargeOnSolarNoChargeReason
CHARGE_ON_SOLAR_NO_CHARGE_REASON_ALTERNATE_VEHICLE_CHARGE_PRIORITY: ChargeOnSolarNoChargeReason
ERROR_CODE_INVALID: ErrorCode
ERROR_CODE_FEATURE_NOT_SUPPORTED: ErrorCode
ERROR_CODE_INTERNAL: ErrorCode

class ChargeOnSolarLimits(_message.Message):
    __slots__ = ("max_excess_solar_power_w",)
    MAX_EXCESS_SOLAR_POWER_W_FIELD_NUMBER: _ClassVar[int]
    max_excess_solar_power_w: float
    def __init__(self, max_excess_solar_power_w: _Optional[float] = ...) -> None: ...

class ChargeOnSolarNoChargeRecommended(_message.Message):
    __slots__ = ("reason",)
    REASON_FIELD_NUMBER: _ClassVar[int]
    reason: ChargeOnSolarNoChargeReason
    def __init__(self, reason: _Optional[_Union[ChargeOnSolarNoChargeReason, str]] = ...) -> None: ...

class ChargeOnSolarResponse(_message.Message):
    __slots__ = ("solar_limits", "no_charge_recommended")
    SOLAR_LIMITS_FIELD_NUMBER: _ClassVar[int]
    NO_CHARGE_RECOMMENDED_FIELD_NUMBER: _ClassVar[int]
    solar_limits: ChargeOnSolarLimits
    no_charge_recommended: ChargeOnSolarNoChargeRecommended
    def __init__(self, solar_limits: _Optional[_Union[ChargeOnSolarLimits, _Mapping]] = ..., no_charge_recommended: _Optional[_Union[ChargeOnSolarNoChargeRecommended, _Mapping]] = ...) -> None: ...

class ErrorResponse(_message.Message):
    __slots__ = ("error_code",)
    ERROR_CODE_FIELD_NUMBER: _ClassVar[int]
    error_code: ErrorCode
    def __init__(self, error_code: _Optional[_Union[ErrorCode, str]] = ...) -> None: ...

class SessionConfigs(_message.Message):
    __slots__ = ("poll_interval_ms",)
    POLL_INTERVAL_MS_FIELD_NUMBER: _ClassVar[int]
    poll_interval_ms: _wrappers_pb2.Int32Value
    def __init__(self, poll_interval_ms: _Optional[_Union[_wrappers_pb2.Int32Value, _Mapping]] = ...) -> None: ...

class ManageVehicleChargingResponse(_message.Message):
    __slots__ = ("session_configs", "charge_on_solar")
    SESSION_CONFIGS_FIELD_NUMBER: _ClassVar[int]
    CHARGE_ON_SOLAR_FIELD_NUMBER: _ClassVar[int]
    session_configs: SessionConfigs
    charge_on_solar: ChargeOnSolarResponse
    def __init__(self, session_configs: _Optional[_Union[SessionConfigs, _Mapping]] = ..., charge_on_solar: _Optional[_Union[ChargeOnSolarResponse, _Mapping]] = ...) -> None: ...

class ManagedChargingAction(_message.Message):
    __slots__ = ("error_response", "manage_vehicle_charging_response")
    ERROR_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    MANAGE_VEHICLE_CHARGING_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    error_response: ErrorResponse
    manage_vehicle_charging_response: ManageVehicleChargingResponse
    def __init__(self, error_response: _Optional[_Union[ErrorResponse, _Mapping]] = ..., manage_vehicle_charging_response: _Optional[_Union[ManageVehicleChargingResponse, _Mapping]] = ...) -> None: ...
