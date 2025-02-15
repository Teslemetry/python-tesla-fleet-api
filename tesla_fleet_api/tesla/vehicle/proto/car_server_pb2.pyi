import vehicle_pb2 as _vehicle_pb2
import signatures_pb2 as _signatures_pb2
import common_pb2 as _common_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union
DESCRIPTOR: _descriptor.FileDescriptor

class OperationStatus_E(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    OPERATIONSTATUS_OK: _ClassVar[OperationStatus_E]
    OPERATIONSTATUS_ERROR: _ClassVar[OperationStatus_E]
OPERATIONSTATUS_OK: OperationStatus_E
OPERATIONSTATUS_ERROR: OperationStatus_E

class Action(_message.Message):
    __slots__ = ('vehicleAction',)
    VEHICLEACTION_FIELD_NUMBER: _ClassVar[int]
    vehicleAction: VehicleAction

    def __init__(self, vehicleAction: _Optional[_Union[VehicleAction, _Mapping]]=...) -> None:
        ...

class VehicleAction(_message.Message):
    __slots__ = ('getVehicleData', 'chargingSetLimitAction', 'chargingStartStopAction', 'drivingClearSpeedLimitPinAction', 'drivingSetSpeedLimitAction', 'drivingSpeedLimitAction', 'hvacAutoAction', 'hvacSetPreconditioningMaxAction', 'hvacSteeringWheelHeaterAction', 'hvacTemperatureAdjustmentAction', 'mediaPlayAction', 'mediaUpdateVolume', 'mediaNextFavorite', 'mediaPreviousFavorite', 'mediaNextTrack', 'mediaPreviousTrack', 'getNearbyChargingSites', 'vehicleControlCancelSoftwareUpdateAction', 'vehicleControlFlashLightsAction', 'vehicleControlHonkHornAction', 'vehicleControlResetValetPinAction', 'vehicleControlScheduleSoftwareUpdateAction', 'vehicleControlSetSentryModeAction', 'vehicleControlSetValetModeAction', 'vehicleControlSunroofOpenCloseAction', 'vehicleControlTriggerHomelinkAction', 'vehicleControlWindowAction', 'hvacBioweaponModeAction', 'hvacSeatHeaterActions', 'scheduledChargingAction', 'scheduledDepartureAction', 'setChargingAmpsAction', 'hvacClimateKeeperAction', 'ping', 'autoSeatClimateAction', 'hvacSeatCoolerActions', 'setCabinOverheatProtectionAction', 'setVehicleNameAction', 'chargePortDoorClose', 'chargePortDoorOpen', 'guestModeAction', 'setCopTempAction', 'eraseUserDataAction', 'vehicleControlSetPinToDriveAction', 'vehicleControlResetPinToDriveAction', 'addChargeScheduleAction', 'removeChargeScheduleAction', 'addPreconditionScheduleAction', 'removePreconditionScheduleAction', 'batchRemovePreconditionSchedulesAction', 'batchRemoveChargeSchedulesAction')
    GETVEHICLEDATA_FIELD_NUMBER: _ClassVar[int]
    CHARGINGSETLIMITACTION_FIELD_NUMBER: _ClassVar[int]
    CHARGINGSTARTSTOPACTION_FIELD_NUMBER: _ClassVar[int]
    DRIVINGCLEARSPEEDLIMITPINACTION_FIELD_NUMBER: _ClassVar[int]
    DRIVINGSETSPEEDLIMITACTION_FIELD_NUMBER: _ClassVar[int]
    DRIVINGSPEEDLIMITACTION_FIELD_NUMBER: _ClassVar[int]
    HVACAUTOACTION_FIELD_NUMBER: _ClassVar[int]
    HVACSETPRECONDITIONINGMAXACTION_FIELD_NUMBER: _ClassVar[int]
    HVACSTEERINGWHEELHEATERACTION_FIELD_NUMBER: _ClassVar[int]
    HVACTEMPERATUREADJUSTMENTACTION_FIELD_NUMBER: _ClassVar[int]
    MEDIAPLAYACTION_FIELD_NUMBER: _ClassVar[int]
    MEDIAUPDATEVOLUME_FIELD_NUMBER: _ClassVar[int]
    MEDIANEXTFAVORITE_FIELD_NUMBER: _ClassVar[int]
    MEDIAPREVIOUSFAVORITE_FIELD_NUMBER: _ClassVar[int]
    MEDIANEXTTRACK_FIELD_NUMBER: _ClassVar[int]
    MEDIAPREVIOUSTRACK_FIELD_NUMBER: _ClassVar[int]
    GETNEARBYCHARGINGSITES_FIELD_NUMBER: _ClassVar[int]
    VEHICLECONTROLCANCELSOFTWAREUPDATEACTION_FIELD_NUMBER: _ClassVar[int]
    VEHICLECONTROLFLASHLIGHTSACTION_FIELD_NUMBER: _ClassVar[int]
    VEHICLECONTROLHONKHORNACTION_FIELD_NUMBER: _ClassVar[int]
    VEHICLECONTROLRESETVALETPINACTION_FIELD_NUMBER: _ClassVar[int]
    VEHICLECONTROLSCHEDULESOFTWAREUPDATEACTION_FIELD_NUMBER: _ClassVar[int]
    VEHICLECONTROLSETSENTRYMODEACTION_FIELD_NUMBER: _ClassVar[int]
    VEHICLECONTROLSETVALETMODEACTION_FIELD_NUMBER: _ClassVar[int]
    VEHICLECONTROLSUNROOFOPENCLOSEACTION_FIELD_NUMBER: _ClassVar[int]
    VEHICLECONTROLTRIGGERHOMELINKACTION_FIELD_NUMBER: _ClassVar[int]
    VEHICLECONTROLWINDOWACTION_FIELD_NUMBER: _ClassVar[int]
    HVACBIOWEAPONMODEACTION_FIELD_NUMBER: _ClassVar[int]
    HVACSEATHEATERACTIONS_FIELD_NUMBER: _ClassVar[int]
    SCHEDULEDCHARGINGACTION_FIELD_NUMBER: _ClassVar[int]
    SCHEDULEDDEPARTUREACTION_FIELD_NUMBER: _ClassVar[int]
    SETCHARGINGAMPSACTION_FIELD_NUMBER: _ClassVar[int]
    HVACCLIMATEKEEPERACTION_FIELD_NUMBER: _ClassVar[int]
    PING_FIELD_NUMBER: _ClassVar[int]
    AUTOSEATCLIMATEACTION_FIELD_NUMBER: _ClassVar[int]
    HVACSEATCOOLERACTIONS_FIELD_NUMBER: _ClassVar[int]
    SETCABINOVERHEATPROTECTIONACTION_FIELD_NUMBER: _ClassVar[int]
    SETVEHICLENAMEACTION_FIELD_NUMBER: _ClassVar[int]
    CHARGEPORTDOORCLOSE_FIELD_NUMBER: _ClassVar[int]
    CHARGEPORTDOOROPEN_FIELD_NUMBER: _ClassVar[int]
    GUESTMODEACTION_FIELD_NUMBER: _ClassVar[int]
    SETCOPTEMPACTION_FIELD_NUMBER: _ClassVar[int]
    ERASEUSERDATAACTION_FIELD_NUMBER: _ClassVar[int]
    VEHICLECONTROLSETPINTODRIVEACTION_FIELD_NUMBER: _ClassVar[int]
    VEHICLECONTROLRESETPINTODRIVEACTION_FIELD_NUMBER: _ClassVar[int]
    ADDCHARGESCHEDULEACTION_FIELD_NUMBER: _ClassVar[int]
    REMOVECHARGESCHEDULEACTION_FIELD_NUMBER: _ClassVar[int]
    ADDPRECONDITIONSCHEDULEACTION_FIELD_NUMBER: _ClassVar[int]
    REMOVEPRECONDITIONSCHEDULEACTION_FIELD_NUMBER: _ClassVar[int]
    BATCHREMOVEPRECONDITIONSCHEDULESACTION_FIELD_NUMBER: _ClassVar[int]
    BATCHREMOVECHARGESCHEDULESACTION_FIELD_NUMBER: _ClassVar[int]
    getVehicleData: GetVehicleData
    chargingSetLimitAction: ChargingSetLimitAction
    chargingStartStopAction: ChargingStartStopAction
    drivingClearSpeedLimitPinAction: DrivingClearSpeedLimitPinAction
    drivingSetSpeedLimitAction: DrivingSetSpeedLimitAction
    drivingSpeedLimitAction: DrivingSpeedLimitAction
    hvacAutoAction: HvacAutoAction
    hvacSetPreconditioningMaxAction: HvacSetPreconditioningMaxAction
    hvacSteeringWheelHeaterAction: HvacSteeringWheelHeaterAction
    hvacTemperatureAdjustmentAction: HvacTemperatureAdjustmentAction
    mediaPlayAction: MediaPlayAction
    mediaUpdateVolume: MediaUpdateVolume
    mediaNextFavorite: MediaNextFavorite
    mediaPreviousFavorite: MediaPreviousFavorite
    mediaNextTrack: MediaNextTrack
    mediaPreviousTrack: MediaPreviousTrack
    getNearbyChargingSites: GetNearbyChargingSites
    vehicleControlCancelSoftwareUpdateAction: VehicleControlCancelSoftwareUpdateAction
    vehicleControlFlashLightsAction: VehicleControlFlashLightsAction
    vehicleControlHonkHornAction: VehicleControlHonkHornAction
    vehicleControlResetValetPinAction: VehicleControlResetValetPinAction
    vehicleControlScheduleSoftwareUpdateAction: VehicleControlScheduleSoftwareUpdateAction
    vehicleControlSetSentryModeAction: VehicleControlSetSentryModeAction
    vehicleControlSetValetModeAction: VehicleControlSetValetModeAction
    vehicleControlSunroofOpenCloseAction: VehicleControlSunroofOpenCloseAction
    vehicleControlTriggerHomelinkAction: VehicleControlTriggerHomelinkAction
    vehicleControlWindowAction: VehicleControlWindowAction
    hvacBioweaponModeAction: HvacBioweaponModeAction
    hvacSeatHeaterActions: HvacSeatHeaterActions
    scheduledChargingAction: ScheduledChargingAction
    scheduledDepartureAction: ScheduledDepartureAction
    setChargingAmpsAction: SetChargingAmpsAction
    hvacClimateKeeperAction: HvacClimateKeeperAction
    ping: Ping
    autoSeatClimateAction: AutoSeatClimateAction
    hvacSeatCoolerActions: HvacSeatCoolerActions
    setCabinOverheatProtectionAction: SetCabinOverheatProtectionAction
    setVehicleNameAction: SetVehicleNameAction
    chargePortDoorClose: ChargePortDoorClose
    chargePortDoorOpen: ChargePortDoorOpen
    guestModeAction: _vehicle_pb2.VehicleState.GuestMode
    setCopTempAction: SetCopTempAction
    eraseUserDataAction: EraseUserDataAction
    vehicleControlSetPinToDriveAction: VehicleControlSetPinToDriveAction
    vehicleControlResetPinToDriveAction: VehicleControlResetPinToDriveAction
    addChargeScheduleAction: _common_pb2.ChargeSchedule
    removeChargeScheduleAction: RemoveChargeScheduleAction
    addPreconditionScheduleAction: _common_pb2.PreconditionSchedule
    removePreconditionScheduleAction: RemovePreconditionScheduleAction
    batchRemovePreconditionSchedulesAction: BatchRemovePreconditionSchedulesAction
    batchRemoveChargeSchedulesAction: BatchRemoveChargeSchedulesAction

    def __init__(self, getVehicleData: _Optional[_Union[GetVehicleData, _Mapping]]=..., chargingSetLimitAction: _Optional[_Union[ChargingSetLimitAction, _Mapping]]=..., chargingStartStopAction: _Optional[_Union[ChargingStartStopAction, _Mapping]]=..., drivingClearSpeedLimitPinAction: _Optional[_Union[DrivingClearSpeedLimitPinAction, _Mapping]]=..., drivingSetSpeedLimitAction: _Optional[_Union[DrivingSetSpeedLimitAction, _Mapping]]=..., drivingSpeedLimitAction: _Optional[_Union[DrivingSpeedLimitAction, _Mapping]]=..., hvacAutoAction: _Optional[_Union[HvacAutoAction, _Mapping]]=..., hvacSetPreconditioningMaxAction: _Optional[_Union[HvacSetPreconditioningMaxAction, _Mapping]]=..., hvacSteeringWheelHeaterAction: _Optional[_Union[HvacSteeringWheelHeaterAction, _Mapping]]=..., hvacTemperatureAdjustmentAction: _Optional[_Union[HvacTemperatureAdjustmentAction, _Mapping]]=..., mediaPlayAction: _Optional[_Union[MediaPlayAction, _Mapping]]=..., mediaUpdateVolume: _Optional[_Union[MediaUpdateVolume, _Mapping]]=..., mediaNextFavorite: _Optional[_Union[MediaNextFavorite, _Mapping]]=..., mediaPreviousFavorite: _Optional[_Union[MediaPreviousFavorite, _Mapping]]=..., mediaNextTrack: _Optional[_Union[MediaNextTrack, _Mapping]]=..., mediaPreviousTrack: _Optional[_Union[MediaPreviousTrack, _Mapping]]=..., getNearbyChargingSites: _Optional[_Union[GetNearbyChargingSites, _Mapping]]=..., vehicleControlCancelSoftwareUpdateAction: _Optional[_Union[VehicleControlCancelSoftwareUpdateAction, _Mapping]]=..., vehicleControlFlashLightsAction: _Optional[_Union[VehicleControlFlashLightsAction, _Mapping]]=..., vehicleControlHonkHornAction: _Optional[_Union[VehicleControlHonkHornAction, _Mapping]]=..., vehicleControlResetValetPinAction: _Optional[_Union[VehicleControlResetValetPinAction, _Mapping]]=..., vehicleControlScheduleSoftwareUpdateAction: _Optional[_Union[VehicleControlScheduleSoftwareUpdateAction, _Mapping]]=..., vehicleControlSetSentryModeAction: _Optional[_Union[VehicleControlSetSentryModeAction, _Mapping]]=..., vehicleControlSetValetModeAction: _Optional[_Union[VehicleControlSetValetModeAction, _Mapping]]=..., vehicleControlSunroofOpenCloseAction: _Optional[_Union[VehicleControlSunroofOpenCloseAction, _Mapping]]=..., vehicleControlTriggerHomelinkAction: _Optional[_Union[VehicleControlTriggerHomelinkAction, _Mapping]]=..., vehicleControlWindowAction: _Optional[_Union[VehicleControlWindowAction, _Mapping]]=..., hvacBioweaponModeAction: _Optional[_Union[HvacBioweaponModeAction, _Mapping]]=..., hvacSeatHeaterActions: _Optional[_Union[HvacSeatHeaterActions, _Mapping]]=..., scheduledChargingAction: _Optional[_Union[ScheduledChargingAction, _Mapping]]=..., scheduledDepartureAction: _Optional[_Union[ScheduledDepartureAction, _Mapping]]=..., setChargingAmpsAction: _Optional[_Union[SetChargingAmpsAction, _Mapping]]=..., hvacClimateKeeperAction: _Optional[_Union[HvacClimateKeeperAction, _Mapping]]=..., ping: _Optional[_Union[Ping, _Mapping]]=..., autoSeatClimateAction: _Optional[_Union[AutoSeatClimateAction, _Mapping]]=..., hvacSeatCoolerActions: _Optional[_Union[HvacSeatCoolerActions, _Mapping]]=..., setCabinOverheatProtectionAction: _Optional[_Union[SetCabinOverheatProtectionAction, _Mapping]]=..., setVehicleNameAction: _Optional[_Union[SetVehicleNameAction, _Mapping]]=..., chargePortDoorClose: _Optional[_Union[ChargePortDoorClose, _Mapping]]=..., chargePortDoorOpen: _Optional[_Union[ChargePortDoorOpen, _Mapping]]=..., guestModeAction: _Optional[_Union[_vehicle_pb2.VehicleState.GuestMode, _Mapping]]=..., setCopTempAction: _Optional[_Union[SetCopTempAction, _Mapping]]=..., eraseUserDataAction: _Optional[_Union[EraseUserDataAction, _Mapping]]=..., vehicleControlSetPinToDriveAction: _Optional[_Union[VehicleControlSetPinToDriveAction, _Mapping]]=..., vehicleControlResetPinToDriveAction: _Optional[_Union[VehicleControlResetPinToDriveAction, _Mapping]]=..., addChargeScheduleAction: _Optional[_Union[_common_pb2.ChargeSchedule, _Mapping]]=..., removeChargeScheduleAction: _Optional[_Union[RemoveChargeScheduleAction, _Mapping]]=..., addPreconditionScheduleAction: _Optional[_Union[_common_pb2.PreconditionSchedule, _Mapping]]=..., removePreconditionScheduleAction: _Optional[_Union[RemovePreconditionScheduleAction, _Mapping]]=..., batchRemovePreconditionSchedulesAction: _Optional[_Union[BatchRemovePreconditionSchedulesAction, _Mapping]]=..., batchRemoveChargeSchedulesAction: _Optional[_Union[BatchRemoveChargeSchedulesAction, _Mapping]]=...) -> None:
        ...

class GetVehicleData(_message.Message):
    __slots__ = ('getChargeState', 'getClimateState', 'getDriveState', 'getLocationState', 'getClosuresState', 'getChargeScheduleState', 'getPreconditioningScheduleState', 'getTirePressureState', 'getMediaState', 'getMediaDetailState', 'getSoftwareUpdateState', 'getParentalControlsState')
    GETCHARGESTATE_FIELD_NUMBER: _ClassVar[int]
    GETCLIMATESTATE_FIELD_NUMBER: _ClassVar[int]
    GETDRIVESTATE_FIELD_NUMBER: _ClassVar[int]
    GETLOCATIONSTATE_FIELD_NUMBER: _ClassVar[int]
    GETCLOSURESSTATE_FIELD_NUMBER: _ClassVar[int]
    GETCHARGESCHEDULESTATE_FIELD_NUMBER: _ClassVar[int]
    GETPRECONDITIONINGSCHEDULESTATE_FIELD_NUMBER: _ClassVar[int]
    GETTIREPRESSURESTATE_FIELD_NUMBER: _ClassVar[int]
    GETMEDIASTATE_FIELD_NUMBER: _ClassVar[int]
    GETMEDIADETAILSTATE_FIELD_NUMBER: _ClassVar[int]
    GETSOFTWAREUPDATESTATE_FIELD_NUMBER: _ClassVar[int]
    GETPARENTALCONTROLSSTATE_FIELD_NUMBER: _ClassVar[int]
    getChargeState: GetChargeState
    getClimateState: GetClimateState
    getDriveState: GetDriveState
    getLocationState: GetLocationState
    getClosuresState: GetClosuresState
    getChargeScheduleState: GetChargeScheduleState
    getPreconditioningScheduleState: GetPreconditioningScheduleState
    getTirePressureState: GetTirePressureState
    getMediaState: GetMediaState
    getMediaDetailState: GetMediaDetailState
    getSoftwareUpdateState: GetSoftwareUpdateState
    getParentalControlsState: GetParentalControlsState

    def __init__(self, getChargeState: _Optional[_Union[GetChargeState, _Mapping]]=..., getClimateState: _Optional[_Union[GetClimateState, _Mapping]]=..., getDriveState: _Optional[_Union[GetDriveState, _Mapping]]=..., getLocationState: _Optional[_Union[GetLocationState, _Mapping]]=..., getClosuresState: _Optional[_Union[GetClosuresState, _Mapping]]=..., getChargeScheduleState: _Optional[_Union[GetChargeScheduleState, _Mapping]]=..., getPreconditioningScheduleState: _Optional[_Union[GetPreconditioningScheduleState, _Mapping]]=..., getTirePressureState: _Optional[_Union[GetTirePressureState, _Mapping]]=..., getMediaState: _Optional[_Union[GetMediaState, _Mapping]]=..., getMediaDetailState: _Optional[_Union[GetMediaDetailState, _Mapping]]=..., getSoftwareUpdateState: _Optional[_Union[GetSoftwareUpdateState, _Mapping]]=..., getParentalControlsState: _Optional[_Union[GetParentalControlsState, _Mapping]]=...) -> None:
        ...

class GetTirePressureState(_message.Message):
    __slots__ = ()

    def __init__(self) -> None:
        ...

class GetMediaState(_message.Message):
    __slots__ = ()

    def __init__(self) -> None:
        ...

class GetMediaDetailState(_message.Message):
    __slots__ = ()

    def __init__(self) -> None:
        ...

class GetSoftwareUpdateState(_message.Message):
    __slots__ = ()

    def __init__(self) -> None:
        ...

class GetChargeState(_message.Message):
    __slots__ = ()

    def __init__(self) -> None:
        ...

class GetClimateState(_message.Message):
    __slots__ = ()

    def __init__(self) -> None:
        ...

class GetDriveState(_message.Message):
    __slots__ = ()

    def __init__(self) -> None:
        ...

class GetLocationState(_message.Message):
    __slots__ = ()

    def __init__(self) -> None:
        ...

class GetClosuresState(_message.Message):
    __slots__ = ()

    def __init__(self) -> None:
        ...

class GetChargeScheduleState(_message.Message):
    __slots__ = ()

    def __init__(self) -> None:
        ...

class GetPreconditioningScheduleState(_message.Message):
    __slots__ = ()

    def __init__(self) -> None:
        ...

class GetParentalControlsState(_message.Message):
    __slots__ = ()

    def __init__(self) -> None:
        ...

class EraseUserDataAction(_message.Message):
    __slots__ = ('reason',)
    REASON_FIELD_NUMBER: _ClassVar[int]
    reason: str

    def __init__(self, reason: _Optional[str]=...) -> None:
        ...

class Response(_message.Message):
    __slots__ = ('actionStatus', 'vehicleData', 'getSessionInfoResponse', 'getNearbyChargingSites', 'ping')
    ACTIONSTATUS_FIELD_NUMBER: _ClassVar[int]
    VEHICLEDATA_FIELD_NUMBER: _ClassVar[int]
    GETSESSIONINFORESPONSE_FIELD_NUMBER: _ClassVar[int]
    GETNEARBYCHARGINGSITES_FIELD_NUMBER: _ClassVar[int]
    PING_FIELD_NUMBER: _ClassVar[int]
    actionStatus: ActionStatus
    vehicleData: _vehicle_pb2.VehicleData
    getSessionInfoResponse: _signatures_pb2.SessionInfo
    getNearbyChargingSites: NearbyChargingSites
    ping: Ping

    def __init__(self, actionStatus: _Optional[_Union[ActionStatus, _Mapping]]=..., vehicleData: _Optional[_Union[_vehicle_pb2.VehicleData, _Mapping]]=..., getSessionInfoResponse: _Optional[_Union[_signatures_pb2.SessionInfo, _Mapping]]=..., getNearbyChargingSites: _Optional[_Union[NearbyChargingSites, _Mapping]]=..., ping: _Optional[_Union[Ping, _Mapping]]=...) -> None:
        ...

class ActionStatus(_message.Message):
    __slots__ = ('result', 'result_reason')
    RESULT_FIELD_NUMBER: _ClassVar[int]
    RESULT_REASON_FIELD_NUMBER: _ClassVar[int]
    result: OperationStatus_E
    result_reason: ResultReason

    def __init__(self, result: _Optional[_Union[OperationStatus_E, str]]=..., result_reason: _Optional[_Union[ResultReason, _Mapping]]=...) -> None:
        ...

class ResultReason(_message.Message):
    __slots__ = ('plain_text',)
    PLAIN_TEXT_FIELD_NUMBER: _ClassVar[int]
    plain_text: str

    def __init__(self, plain_text: _Optional[str]=...) -> None:
        ...

class EncryptedData(_message.Message):
    __slots__ = ('field_number', 'ciphertext', 'tag')
    FIELD_NUMBER_FIELD_NUMBER: _ClassVar[int]
    CIPHERTEXT_FIELD_NUMBER: _ClassVar[int]
    TAG_FIELD_NUMBER: _ClassVar[int]
    field_number: int
    ciphertext: bytes
    tag: bytes

    def __init__(self, field_number: _Optional[int]=..., ciphertext: _Optional[bytes]=..., tag: _Optional[bytes]=...) -> None:
        ...

class ChargingSetLimitAction(_message.Message):
    __slots__ = ('percent',)
    PERCENT_FIELD_NUMBER: _ClassVar[int]
    percent: int

    def __init__(self, percent: _Optional[int]=...) -> None:
        ...

class ChargingStartStopAction(_message.Message):
    __slots__ = ('unknown', 'start', 'start_standard', 'start_max_range', 'stop')
    UNKNOWN_FIELD_NUMBER: _ClassVar[int]
    START_FIELD_NUMBER: _ClassVar[int]
    START_STANDARD_FIELD_NUMBER: _ClassVar[int]
    START_MAX_RANGE_FIELD_NUMBER: _ClassVar[int]
    STOP_FIELD_NUMBER: _ClassVar[int]
    unknown: _common_pb2.Void
    start: _common_pb2.Void
    start_standard: _common_pb2.Void
    start_max_range: _common_pb2.Void
    stop: _common_pb2.Void

    def __init__(self, unknown: _Optional[_Union[_common_pb2.Void, _Mapping]]=..., start: _Optional[_Union[_common_pb2.Void, _Mapping]]=..., start_standard: _Optional[_Union[_common_pb2.Void, _Mapping]]=..., start_max_range: _Optional[_Union[_common_pb2.Void, _Mapping]]=..., stop: _Optional[_Union[_common_pb2.Void, _Mapping]]=...) -> None:
        ...

class DrivingClearSpeedLimitPinAction(_message.Message):
    __slots__ = ('pin',)
    PIN_FIELD_NUMBER: _ClassVar[int]
    pin: str

    def __init__(self, pin: _Optional[str]=...) -> None:
        ...

class DrivingSetSpeedLimitAction(_message.Message):
    __slots__ = ('limit_mph',)
    LIMIT_MPH_FIELD_NUMBER: _ClassVar[int]
    limit_mph: float

    def __init__(self, limit_mph: _Optional[float]=...) -> None:
        ...

class DrivingSpeedLimitAction(_message.Message):
    __slots__ = ('activate', 'pin')
    ACTIVATE_FIELD_NUMBER: _ClassVar[int]
    PIN_FIELD_NUMBER: _ClassVar[int]
    activate: bool
    pin: str

    def __init__(self, activate: bool=..., pin: _Optional[str]=...) -> None:
        ...

class HvacAutoAction(_message.Message):
    __slots__ = ('power_on', 'manual_override')
    POWER_ON_FIELD_NUMBER: _ClassVar[int]
    MANUAL_OVERRIDE_FIELD_NUMBER: _ClassVar[int]
    power_on: bool
    manual_override: bool

    def __init__(self, power_on: bool=..., manual_override: bool=...) -> None:
        ...

class HvacSeatHeaterActions(_message.Message):
    __slots__ = ('hvacSeatHeaterAction',)

    class HvacSeatHeaterAction(_message.Message):
        __slots__ = ('SEAT_HEATER_UNKNOWN', 'SEAT_HEATER_OFF', 'SEAT_HEATER_LOW', 'SEAT_HEATER_MED', 'SEAT_HEATER_HIGH', 'CAR_SEAT_UNKNOWN', 'CAR_SEAT_FRONT_LEFT', 'CAR_SEAT_FRONT_RIGHT', 'CAR_SEAT_REAR_LEFT', 'CAR_SEAT_REAR_LEFT_BACK', 'CAR_SEAT_REAR_CENTER', 'CAR_SEAT_REAR_RIGHT', 'CAR_SEAT_REAR_RIGHT_BACK', 'CAR_SEAT_THIRD_ROW_LEFT', 'CAR_SEAT_THIRD_ROW_RIGHT')
        SEAT_HEATER_UNKNOWN_FIELD_NUMBER: _ClassVar[int]
        SEAT_HEATER_OFF_FIELD_NUMBER: _ClassVar[int]
        SEAT_HEATER_LOW_FIELD_NUMBER: _ClassVar[int]
        SEAT_HEATER_MED_FIELD_NUMBER: _ClassVar[int]
        SEAT_HEATER_HIGH_FIELD_NUMBER: _ClassVar[int]
        CAR_SEAT_UNKNOWN_FIELD_NUMBER: _ClassVar[int]
        CAR_SEAT_FRONT_LEFT_FIELD_NUMBER: _ClassVar[int]
        CAR_SEAT_FRONT_RIGHT_FIELD_NUMBER: _ClassVar[int]
        CAR_SEAT_REAR_LEFT_FIELD_NUMBER: _ClassVar[int]
        CAR_SEAT_REAR_LEFT_BACK_FIELD_NUMBER: _ClassVar[int]
        CAR_SEAT_REAR_CENTER_FIELD_NUMBER: _ClassVar[int]
        CAR_SEAT_REAR_RIGHT_FIELD_NUMBER: _ClassVar[int]
        CAR_SEAT_REAR_RIGHT_BACK_FIELD_NUMBER: _ClassVar[int]
        CAR_SEAT_THIRD_ROW_LEFT_FIELD_NUMBER: _ClassVar[int]
        CAR_SEAT_THIRD_ROW_RIGHT_FIELD_NUMBER: _ClassVar[int]
        SEAT_HEATER_UNKNOWN: _common_pb2.Void
        SEAT_HEATER_OFF: _common_pb2.Void
        SEAT_HEATER_LOW: _common_pb2.Void
        SEAT_HEATER_MED: _common_pb2.Void
        SEAT_HEATER_HIGH: _common_pb2.Void
        CAR_SEAT_UNKNOWN: _common_pb2.Void
        CAR_SEAT_FRONT_LEFT: _common_pb2.Void
        CAR_SEAT_FRONT_RIGHT: _common_pb2.Void
        CAR_SEAT_REAR_LEFT: _common_pb2.Void
        CAR_SEAT_REAR_LEFT_BACK: _common_pb2.Void
        CAR_SEAT_REAR_CENTER: _common_pb2.Void
        CAR_SEAT_REAR_RIGHT: _common_pb2.Void
        CAR_SEAT_REAR_RIGHT_BACK: _common_pb2.Void
        CAR_SEAT_THIRD_ROW_LEFT: _common_pb2.Void
        CAR_SEAT_THIRD_ROW_RIGHT: _common_pb2.Void

        def __init__(self, SEAT_HEATER_UNKNOWN: _Optional[_Union[_common_pb2.Void, _Mapping]]=..., SEAT_HEATER_OFF: _Optional[_Union[_common_pb2.Void, _Mapping]]=..., SEAT_HEATER_LOW: _Optional[_Union[_common_pb2.Void, _Mapping]]=..., SEAT_HEATER_MED: _Optional[_Union[_common_pb2.Void, _Mapping]]=..., SEAT_HEATER_HIGH: _Optional[_Union[_common_pb2.Void, _Mapping]]=..., CAR_SEAT_UNKNOWN: _Optional[_Union[_common_pb2.Void, _Mapping]]=..., CAR_SEAT_FRONT_LEFT: _Optional[_Union[_common_pb2.Void, _Mapping]]=..., CAR_SEAT_FRONT_RIGHT: _Optional[_Union[_common_pb2.Void, _Mapping]]=..., CAR_SEAT_REAR_LEFT: _Optional[_Union[_common_pb2.Void, _Mapping]]=..., CAR_SEAT_REAR_LEFT_BACK: _Optional[_Union[_common_pb2.Void, _Mapping]]=..., CAR_SEAT_REAR_CENTER: _Optional[_Union[_common_pb2.Void, _Mapping]]=..., CAR_SEAT_REAR_RIGHT: _Optional[_Union[_common_pb2.Void, _Mapping]]=..., CAR_SEAT_REAR_RIGHT_BACK: _Optional[_Union[_common_pb2.Void, _Mapping]]=..., CAR_SEAT_THIRD_ROW_LEFT: _Optional[_Union[_common_pb2.Void, _Mapping]]=..., CAR_SEAT_THIRD_ROW_RIGHT: _Optional[_Union[_common_pb2.Void, _Mapping]]=...) -> None:
            ...
    HVACSEATHEATERACTION_FIELD_NUMBER: _ClassVar[int]
    hvacSeatHeaterAction: _containers.RepeatedCompositeFieldContainer[HvacSeatHeaterActions.HvacSeatHeaterAction]

    def __init__(self, hvacSeatHeaterAction: _Optional[_Iterable[_Union[HvacSeatHeaterActions.HvacSeatHeaterAction, _Mapping]]]=...) -> None:
        ...

class HvacSeatCoolerActions(_message.Message):
    __slots__ = ('hvacSeatCoolerAction',)

    class HvacSeatCoolerLevel_E(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        HvacSeatCoolerLevel_Unknown: _ClassVar[HvacSeatCoolerActions.HvacSeatCoolerLevel_E]
        HvacSeatCoolerLevel_Off: _ClassVar[HvacSeatCoolerActions.HvacSeatCoolerLevel_E]
        HvacSeatCoolerLevel_Low: _ClassVar[HvacSeatCoolerActions.HvacSeatCoolerLevel_E]
        HvacSeatCoolerLevel_Med: _ClassVar[HvacSeatCoolerActions.HvacSeatCoolerLevel_E]
        HvacSeatCoolerLevel_High: _ClassVar[HvacSeatCoolerActions.HvacSeatCoolerLevel_E]
    HvacSeatCoolerLevel_Unknown: HvacSeatCoolerActions.HvacSeatCoolerLevel_E
    HvacSeatCoolerLevel_Off: HvacSeatCoolerActions.HvacSeatCoolerLevel_E
    HvacSeatCoolerLevel_Low: HvacSeatCoolerActions.HvacSeatCoolerLevel_E
    HvacSeatCoolerLevel_Med: HvacSeatCoolerActions.HvacSeatCoolerLevel_E
    HvacSeatCoolerLevel_High: HvacSeatCoolerActions.HvacSeatCoolerLevel_E

    class HvacSeatCoolerPosition_E(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        HvacSeatCoolerPosition_Unknown: _ClassVar[HvacSeatCoolerActions.HvacSeatCoolerPosition_E]
        HvacSeatCoolerPosition_FrontLeft: _ClassVar[HvacSeatCoolerActions.HvacSeatCoolerPosition_E]
        HvacSeatCoolerPosition_FrontRight: _ClassVar[HvacSeatCoolerActions.HvacSeatCoolerPosition_E]
    HvacSeatCoolerPosition_Unknown: HvacSeatCoolerActions.HvacSeatCoolerPosition_E
    HvacSeatCoolerPosition_FrontLeft: HvacSeatCoolerActions.HvacSeatCoolerPosition_E
    HvacSeatCoolerPosition_FrontRight: HvacSeatCoolerActions.HvacSeatCoolerPosition_E

    class HvacSeatCoolerAction(_message.Message):
        __slots__ = ('seat_cooler_level', 'seat_position')
        SEAT_COOLER_LEVEL_FIELD_NUMBER: _ClassVar[int]
        SEAT_POSITION_FIELD_NUMBER: _ClassVar[int]
        seat_cooler_level: HvacSeatCoolerActions.HvacSeatCoolerLevel_E
        seat_position: HvacSeatCoolerActions.HvacSeatCoolerPosition_E

        def __init__(self, seat_cooler_level: _Optional[_Union[HvacSeatCoolerActions.HvacSeatCoolerLevel_E, str]]=..., seat_position: _Optional[_Union[HvacSeatCoolerActions.HvacSeatCoolerPosition_E, str]]=...) -> None:
            ...
    HVACSEATCOOLERACTION_FIELD_NUMBER: _ClassVar[int]
    hvacSeatCoolerAction: _containers.RepeatedCompositeFieldContainer[HvacSeatCoolerActions.HvacSeatCoolerAction]

    def __init__(self, hvacSeatCoolerAction: _Optional[_Iterable[_Union[HvacSeatCoolerActions.HvacSeatCoolerAction, _Mapping]]]=...) -> None:
        ...

class HvacSetPreconditioningMaxAction(_message.Message):
    __slots__ = ('on', 'manual_override', 'manual_override_mode')

    class ManualOverrideMode_E(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DogMode: _ClassVar[HvacSetPreconditioningMaxAction.ManualOverrideMode_E]
        Soc: _ClassVar[HvacSetPreconditioningMaxAction.ManualOverrideMode_E]
        Doors: _ClassVar[HvacSetPreconditioningMaxAction.ManualOverrideMode_E]
    DogMode: HvacSetPreconditioningMaxAction.ManualOverrideMode_E
    Soc: HvacSetPreconditioningMaxAction.ManualOverrideMode_E
    Doors: HvacSetPreconditioningMaxAction.ManualOverrideMode_E
    ON_FIELD_NUMBER: _ClassVar[int]
    MANUAL_OVERRIDE_FIELD_NUMBER: _ClassVar[int]
    MANUAL_OVERRIDE_MODE_FIELD_NUMBER: _ClassVar[int]
    on: bool
    manual_override: bool
    manual_override_mode: _containers.RepeatedScalarFieldContainer[HvacSetPreconditioningMaxAction.ManualOverrideMode_E]

    def __init__(self, on: bool=..., manual_override: bool=..., manual_override_mode: _Optional[_Iterable[_Union[HvacSetPreconditioningMaxAction.ManualOverrideMode_E, str]]]=...) -> None:
        ...

class HvacSteeringWheelHeaterAction(_message.Message):
    __slots__ = ('power_on',)
    POWER_ON_FIELD_NUMBER: _ClassVar[int]
    power_on: bool

    def __init__(self, power_on: bool=...) -> None:
        ...

class HvacTemperatureAdjustmentAction(_message.Message):
    __slots__ = ('delta_celsius', 'delta_percent', 'absolute_celsius', 'level', 'hvac_temperature_zone', 'driver_temp_celsius', 'passenger_temp_celsius')

    class Temperature(_message.Message):
        __slots__ = ('TEMP_UNKNOWN', 'TEMP_MIN', 'TEMP_MAX')
        TEMP_UNKNOWN_FIELD_NUMBER: _ClassVar[int]
        TEMP_MIN_FIELD_NUMBER: _ClassVar[int]
        TEMP_MAX_FIELD_NUMBER: _ClassVar[int]
        TEMP_UNKNOWN: _common_pb2.Void
        TEMP_MIN: _common_pb2.Void
        TEMP_MAX: _common_pb2.Void

        def __init__(self, TEMP_UNKNOWN: _Optional[_Union[_common_pb2.Void, _Mapping]]=..., TEMP_MIN: _Optional[_Union[_common_pb2.Void, _Mapping]]=..., TEMP_MAX: _Optional[_Union[_common_pb2.Void, _Mapping]]=...) -> None:
            ...

    class HvacTemperatureZone(_message.Message):
        __slots__ = ('TEMP_ZONE_UNKNOWN', 'TEMP_ZONE_FRONT_LEFT', 'TEMP_ZONE_FRONT_RIGHT', 'TEMP_ZONE_REAR')
        TEMP_ZONE_UNKNOWN_FIELD_NUMBER: _ClassVar[int]
        TEMP_ZONE_FRONT_LEFT_FIELD_NUMBER: _ClassVar[int]
        TEMP_ZONE_FRONT_RIGHT_FIELD_NUMBER: _ClassVar[int]
        TEMP_ZONE_REAR_FIELD_NUMBER: _ClassVar[int]
        TEMP_ZONE_UNKNOWN: _common_pb2.Void
        TEMP_ZONE_FRONT_LEFT: _common_pb2.Void
        TEMP_ZONE_FRONT_RIGHT: _common_pb2.Void
        TEMP_ZONE_REAR: _common_pb2.Void

        def __init__(self, TEMP_ZONE_UNKNOWN: _Optional[_Union[_common_pb2.Void, _Mapping]]=..., TEMP_ZONE_FRONT_LEFT: _Optional[_Union[_common_pb2.Void, _Mapping]]=..., TEMP_ZONE_FRONT_RIGHT: _Optional[_Union[_common_pb2.Void, _Mapping]]=..., TEMP_ZONE_REAR: _Optional[_Union[_common_pb2.Void, _Mapping]]=...) -> None:
            ...
    DELTA_CELSIUS_FIELD_NUMBER: _ClassVar[int]
    DELTA_PERCENT_FIELD_NUMBER: _ClassVar[int]
    ABSOLUTE_CELSIUS_FIELD_NUMBER: _ClassVar[int]
    LEVEL_FIELD_NUMBER: _ClassVar[int]
    HVAC_TEMPERATURE_ZONE_FIELD_NUMBER: _ClassVar[int]
    DRIVER_TEMP_CELSIUS_FIELD_NUMBER: _ClassVar[int]
    PASSENGER_TEMP_CELSIUS_FIELD_NUMBER: _ClassVar[int]
    delta_celsius: float
    delta_percent: int
    absolute_celsius: float
    level: HvacTemperatureAdjustmentAction.Temperature
    hvac_temperature_zone: _containers.RepeatedCompositeFieldContainer[HvacTemperatureAdjustmentAction.HvacTemperatureZone]
    driver_temp_celsius: float
    passenger_temp_celsius: float

    def __init__(self, delta_celsius: _Optional[float]=..., delta_percent: _Optional[int]=..., absolute_celsius: _Optional[float]=..., level: _Optional[_Union[HvacTemperatureAdjustmentAction.Temperature, _Mapping]]=..., hvac_temperature_zone: _Optional[_Iterable[_Union[HvacTemperatureAdjustmentAction.HvacTemperatureZone, _Mapping]]]=..., driver_temp_celsius: _Optional[float]=..., passenger_temp_celsius: _Optional[float]=...) -> None:
        ...

class GetNearbyChargingSites(_message.Message):
    __slots__ = ('include_meta_data', 'radius', 'count')
    INCLUDE_META_DATA_FIELD_NUMBER: _ClassVar[int]
    RADIUS_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    include_meta_data: bool
    radius: int
    count: int

    def __init__(self, include_meta_data: bool=..., radius: _Optional[int]=..., count: _Optional[int]=...) -> None:
        ...

class NearbyChargingSites(_message.Message):
    __slots__ = ('timestamp', 'superchargers', 'congestion_sync_time_utc_secs')
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    SUPERCHARGERS_FIELD_NUMBER: _ClassVar[int]
    CONGESTION_SYNC_TIME_UTC_SECS_FIELD_NUMBER: _ClassVar[int]
    timestamp: _timestamp_pb2.Timestamp
    superchargers: _containers.RepeatedCompositeFieldContainer[Superchargers]
    congestion_sync_time_utc_secs: int

    def __init__(self, timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]]=..., superchargers: _Optional[_Iterable[_Union[Superchargers, _Mapping]]]=..., congestion_sync_time_utc_secs: _Optional[int]=...) -> None:
        ...

class Superchargers(_message.Message):
    __slots__ = ('id', 'amenities', 'available_stalls', 'billing_info', 'billing_time', 'city', 'country', 'distance_miles', 'district', 'location', 'name', 'postal_code', 'site_closed', 'state', 'street_address', 'total_stalls', 'within_range', 'max_power_kw', 'out_of_order_stalls_number', 'out_of_order_stalls_names')
    ID_FIELD_NUMBER: _ClassVar[int]
    AMENITIES_FIELD_NUMBER: _ClassVar[int]
    AVAILABLE_STALLS_FIELD_NUMBER: _ClassVar[int]
    BILLING_INFO_FIELD_NUMBER: _ClassVar[int]
    BILLING_TIME_FIELD_NUMBER: _ClassVar[int]
    CITY_FIELD_NUMBER: _ClassVar[int]
    COUNTRY_FIELD_NUMBER: _ClassVar[int]
    DISTANCE_MILES_FIELD_NUMBER: _ClassVar[int]
    DISTRICT_FIELD_NUMBER: _ClassVar[int]
    LOCATION_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    POSTAL_CODE_FIELD_NUMBER: _ClassVar[int]
    SITE_CLOSED_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    STREET_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_STALLS_FIELD_NUMBER: _ClassVar[int]
    WITHIN_RANGE_FIELD_NUMBER: _ClassVar[int]
    MAX_POWER_KW_FIELD_NUMBER: _ClassVar[int]
    OUT_OF_ORDER_STALLS_NUMBER_FIELD_NUMBER: _ClassVar[int]
    OUT_OF_ORDER_STALLS_NAMES_FIELD_NUMBER: _ClassVar[int]
    id: int
    amenities: str
    available_stalls: int
    billing_info: str
    billing_time: str
    city: str
    country: str
    distance_miles: float
    district: str
    location: _common_pb2.LatLong
    name: str
    postal_code: str
    site_closed: bool
    state: str
    street_address: str
    total_stalls: int
    within_range: bool
    max_power_kw: int
    out_of_order_stalls_number: int
    out_of_order_stalls_names: str

    def __init__(self, id: _Optional[int]=..., amenities: _Optional[str]=..., available_stalls: _Optional[int]=..., billing_info: _Optional[str]=..., billing_time: _Optional[str]=..., city: _Optional[str]=..., country: _Optional[str]=..., distance_miles: _Optional[float]=..., district: _Optional[str]=..., location: _Optional[_Union[_common_pb2.LatLong, _Mapping]]=..., name: _Optional[str]=..., postal_code: _Optional[str]=..., site_closed: bool=..., state: _Optional[str]=..., street_address: _Optional[str]=..., total_stalls: _Optional[int]=..., within_range: bool=..., max_power_kw: _Optional[int]=..., out_of_order_stalls_number: _Optional[int]=..., out_of_order_stalls_names: _Optional[str]=...) -> None:
        ...

class MediaPlayAction(_message.Message):
    __slots__ = ()

    def __init__(self) -> None:
        ...

class MediaUpdateVolume(_message.Message):
    __slots__ = ('volume_delta', 'volume_absolute_float')
    VOLUME_DELTA_FIELD_NUMBER: _ClassVar[int]
    VOLUME_ABSOLUTE_FLOAT_FIELD_NUMBER: _ClassVar[int]
    volume_delta: int
    volume_absolute_float: float

    def __init__(self, volume_delta: _Optional[int]=..., volume_absolute_float: _Optional[float]=...) -> None:
        ...

class MediaNextFavorite(_message.Message):
    __slots__ = ()

    def __init__(self) -> None:
        ...

class MediaPreviousFavorite(_message.Message):
    __slots__ = ()

    def __init__(self) -> None:
        ...

class MediaNextTrack(_message.Message):
    __slots__ = ()

    def __init__(self) -> None:
        ...

class MediaPreviousTrack(_message.Message):
    __slots__ = ()

    def __init__(self) -> None:
        ...

class VehicleControlCancelSoftwareUpdateAction(_message.Message):
    __slots__ = ()

    def __init__(self) -> None:
        ...

class VehicleControlFlashLightsAction(_message.Message):
    __slots__ = ()

    def __init__(self) -> None:
        ...

class VehicleControlHonkHornAction(_message.Message):
    __slots__ = ()

    def __init__(self) -> None:
        ...

class VehicleControlResetValetPinAction(_message.Message):
    __slots__ = ()

    def __init__(self) -> None:
        ...

class VehicleControlScheduleSoftwareUpdateAction(_message.Message):
    __slots__ = ('offset_sec',)
    OFFSET_SEC_FIELD_NUMBER: _ClassVar[int]
    offset_sec: int

    def __init__(self, offset_sec: _Optional[int]=...) -> None:
        ...

class VehicleControlSetSentryModeAction(_message.Message):
    __slots__ = ('on',)
    ON_FIELD_NUMBER: _ClassVar[int]
    on: bool

    def __init__(self, on: bool=...) -> None:
        ...

class VehicleControlSetValetModeAction(_message.Message):
    __slots__ = ('on', 'password')
    ON_FIELD_NUMBER: _ClassVar[int]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    on: bool
    password: str

    def __init__(self, on: bool=..., password: _Optional[str]=...) -> None:
        ...

class VehicleControlSunroofOpenCloseAction(_message.Message):
    __slots__ = ('absolute_level', 'delta_level', 'vent', 'close', 'open')
    ABSOLUTE_LEVEL_FIELD_NUMBER: _ClassVar[int]
    DELTA_LEVEL_FIELD_NUMBER: _ClassVar[int]
    VENT_FIELD_NUMBER: _ClassVar[int]
    CLOSE_FIELD_NUMBER: _ClassVar[int]
    OPEN_FIELD_NUMBER: _ClassVar[int]
    absolute_level: int
    delta_level: int
    vent: _common_pb2.Void
    close: _common_pb2.Void
    open: _common_pb2.Void

    def __init__(self, absolute_level: _Optional[int]=..., delta_level: _Optional[int]=..., vent: _Optional[_Union[_common_pb2.Void, _Mapping]]=..., close: _Optional[_Union[_common_pb2.Void, _Mapping]]=..., open: _Optional[_Union[_common_pb2.Void, _Mapping]]=...) -> None:
        ...

class VehicleControlTriggerHomelinkAction(_message.Message):
    __slots__ = ('location', 'token')
    LOCATION_FIELD_NUMBER: _ClassVar[int]
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    location: _common_pb2.LatLong
    token: str

    def __init__(self, location: _Optional[_Union[_common_pb2.LatLong, _Mapping]]=..., token: _Optional[str]=...) -> None:
        ...

class VehicleControlWindowAction(_message.Message):
    __slots__ = ('unknown', 'vent', 'close')
    UNKNOWN_FIELD_NUMBER: _ClassVar[int]
    VENT_FIELD_NUMBER: _ClassVar[int]
    CLOSE_FIELD_NUMBER: _ClassVar[int]
    unknown: _common_pb2.Void
    vent: _common_pb2.Void
    close: _common_pb2.Void

    def __init__(self, unknown: _Optional[_Union[_common_pb2.Void, _Mapping]]=..., vent: _Optional[_Union[_common_pb2.Void, _Mapping]]=..., close: _Optional[_Union[_common_pb2.Void, _Mapping]]=...) -> None:
        ...

class HvacBioweaponModeAction(_message.Message):
    __slots__ = ('on', 'manual_override')
    ON_FIELD_NUMBER: _ClassVar[int]
    MANUAL_OVERRIDE_FIELD_NUMBER: _ClassVar[int]
    on: bool
    manual_override: bool

    def __init__(self, on: bool=..., manual_override: bool=...) -> None:
        ...

class AutoSeatClimateAction(_message.Message):
    __slots__ = ('carseat',)

    class AutoSeatPosition_E(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        AutoSeatPosition_Unknown: _ClassVar[AutoSeatClimateAction.AutoSeatPosition_E]
        AutoSeatPosition_FrontLeft: _ClassVar[AutoSeatClimateAction.AutoSeatPosition_E]
        AutoSeatPosition_FrontRight: _ClassVar[AutoSeatClimateAction.AutoSeatPosition_E]
    AutoSeatPosition_Unknown: AutoSeatClimateAction.AutoSeatPosition_E
    AutoSeatPosition_FrontLeft: AutoSeatClimateAction.AutoSeatPosition_E
    AutoSeatPosition_FrontRight: AutoSeatClimateAction.AutoSeatPosition_E

    class CarSeat(_message.Message):
        __slots__ = ('on', 'seat_position')
        ON_FIELD_NUMBER: _ClassVar[int]
        SEAT_POSITION_FIELD_NUMBER: _ClassVar[int]
        on: bool
        seat_position: AutoSeatClimateAction.AutoSeatPosition_E

        def __init__(self, on: bool=..., seat_position: _Optional[_Union[AutoSeatClimateAction.AutoSeatPosition_E, str]]=...) -> None:
            ...
    CARSEAT_FIELD_NUMBER: _ClassVar[int]
    carseat: _containers.RepeatedCompositeFieldContainer[AutoSeatClimateAction.CarSeat]

    def __init__(self, carseat: _Optional[_Iterable[_Union[AutoSeatClimateAction.CarSeat, _Mapping]]]=...) -> None:
        ...

class Ping(_message.Message):
    __slots__ = ('ping_id', 'local_timestamp', 'last_remote_timestamp')
    PING_ID_FIELD_NUMBER: _ClassVar[int]
    LOCAL_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    LAST_REMOTE_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    ping_id: int
    local_timestamp: _timestamp_pb2.Timestamp
    last_remote_timestamp: _timestamp_pb2.Timestamp

    def __init__(self, ping_id: _Optional[int]=..., local_timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]]=..., last_remote_timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]]=...) -> None:
        ...

class ScheduledChargingAction(_message.Message):
    __slots__ = ('enabled', 'charging_time')
    ENABLED_FIELD_NUMBER: _ClassVar[int]
    CHARGING_TIME_FIELD_NUMBER: _ClassVar[int]
    enabled: bool
    charging_time: int

    def __init__(self, enabled: bool=..., charging_time: _Optional[int]=...) -> None:
        ...

class ScheduledDepartureAction(_message.Message):
    __slots__ = ('enabled', 'departure_time', 'preconditioning_times', 'off_peak_charging_times', 'off_peak_hours_end_time')
    ENABLED_FIELD_NUMBER: _ClassVar[int]
    DEPARTURE_TIME_FIELD_NUMBER: _ClassVar[int]
    PRECONDITIONING_TIMES_FIELD_NUMBER: _ClassVar[int]
    OFF_PEAK_CHARGING_TIMES_FIELD_NUMBER: _ClassVar[int]
    OFF_PEAK_HOURS_END_TIME_FIELD_NUMBER: _ClassVar[int]
    enabled: bool
    departure_time: int
    preconditioning_times: _common_pb2.PreconditioningTimes
    off_peak_charging_times: _common_pb2.OffPeakChargingTimes
    off_peak_hours_end_time: int

    def __init__(self, enabled: bool=..., departure_time: _Optional[int]=..., preconditioning_times: _Optional[_Union[_common_pb2.PreconditioningTimes, _Mapping]]=..., off_peak_charging_times: _Optional[_Union[_common_pb2.OffPeakChargingTimes, _Mapping]]=..., off_peak_hours_end_time: _Optional[int]=...) -> None:
        ...

class HvacClimateKeeperAction(_message.Message):
    __slots__ = ('ClimateKeeperAction', 'manual_override')

    class ClimateKeeperAction_E(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        ClimateKeeperAction_Off: _ClassVar[HvacClimateKeeperAction.ClimateKeeperAction_E]
        ClimateKeeperAction_On: _ClassVar[HvacClimateKeeperAction.ClimateKeeperAction_E]
        ClimateKeeperAction_Dog: _ClassVar[HvacClimateKeeperAction.ClimateKeeperAction_E]
        ClimateKeeperAction_Camp: _ClassVar[HvacClimateKeeperAction.ClimateKeeperAction_E]
    ClimateKeeperAction_Off: HvacClimateKeeperAction.ClimateKeeperAction_E
    ClimateKeeperAction_On: HvacClimateKeeperAction.ClimateKeeperAction_E
    ClimateKeeperAction_Dog: HvacClimateKeeperAction.ClimateKeeperAction_E
    ClimateKeeperAction_Camp: HvacClimateKeeperAction.ClimateKeeperAction_E
    CLIMATEKEEPERACTION_FIELD_NUMBER: _ClassVar[int]
    MANUAL_OVERRIDE_FIELD_NUMBER: _ClassVar[int]
    ClimateKeeperAction: HvacClimateKeeperAction.ClimateKeeperAction_E
    manual_override: bool

    def __init__(self, ClimateKeeperAction: _Optional[_Union[HvacClimateKeeperAction.ClimateKeeperAction_E, str]]=..., manual_override: bool=...) -> None:
        ...

class SetChargingAmpsAction(_message.Message):
    __slots__ = ('charging_amps',)
    CHARGING_AMPS_FIELD_NUMBER: _ClassVar[int]
    charging_amps: int

    def __init__(self, charging_amps: _Optional[int]=...) -> None:
        ...

class RemoveChargeScheduleAction(_message.Message):
    __slots__ = ('id',)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: int

    def __init__(self, id: _Optional[int]=...) -> None:
        ...

class BatchRemoveChargeSchedulesAction(_message.Message):
    __slots__ = ('home', 'work', 'other')
    HOME_FIELD_NUMBER: _ClassVar[int]
    WORK_FIELD_NUMBER: _ClassVar[int]
    OTHER_FIELD_NUMBER: _ClassVar[int]
    home: bool
    work: bool
    other: bool

    def __init__(self, home: bool=..., work: bool=..., other: bool=...) -> None:
        ...

class BatchRemovePreconditionSchedulesAction(_message.Message):
    __slots__ = ('home', 'work', 'other')
    HOME_FIELD_NUMBER: _ClassVar[int]
    WORK_FIELD_NUMBER: _ClassVar[int]
    OTHER_FIELD_NUMBER: _ClassVar[int]
    home: bool
    work: bool
    other: bool

    def __init__(self, home: bool=..., work: bool=..., other: bool=...) -> None:
        ...

class RemovePreconditionScheduleAction(_message.Message):
    __slots__ = ('id',)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: int

    def __init__(self, id: _Optional[int]=...) -> None:
        ...

class SetCabinOverheatProtectionAction(_message.Message):
    __slots__ = ('on', 'fan_only')
    ON_FIELD_NUMBER: _ClassVar[int]
    FAN_ONLY_FIELD_NUMBER: _ClassVar[int]
    on: bool
    fan_only: bool

    def __init__(self, on: bool=..., fan_only: bool=...) -> None:
        ...

class SetVehicleNameAction(_message.Message):
    __slots__ = ('vehicleName',)
    VEHICLENAME_FIELD_NUMBER: _ClassVar[int]
    vehicleName: str

    def __init__(self, vehicleName: _Optional[str]=...) -> None:
        ...

class ChargePortDoorClose(_message.Message):
    __slots__ = ()

    def __init__(self) -> None:
        ...

class ChargePortDoorOpen(_message.Message):
    __slots__ = ()

    def __init__(self) -> None:
        ...

class SetCopTempAction(_message.Message):
    __slots__ = ('copActivationTemp',)
    COPACTIVATIONTEMP_FIELD_NUMBER: _ClassVar[int]
    copActivationTemp: _vehicle_pb2.ClimateState.CopActivationTemp

    def __init__(self, copActivationTemp: _Optional[_Union[_vehicle_pb2.ClimateState.CopActivationTemp, str]]=...) -> None:
        ...

class VehicleControlSetPinToDriveAction(_message.Message):
    __slots__ = ('on', 'password')
    ON_FIELD_NUMBER: _ClassVar[int]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    on: bool
    password: str

    def __init__(self, on: bool=..., password: _Optional[str]=...) -> None:
        ...

class VehicleControlResetPinToDriveAction(_message.Message):
    __slots__ = ()

    def __init__(self) -> None:
        ...