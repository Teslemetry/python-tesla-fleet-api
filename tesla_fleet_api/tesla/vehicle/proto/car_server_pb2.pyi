import common_pb2 as _common_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
import signatures_pb2 as _signatures_pb2
import vehicle_pb2 as _vehicle_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union
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
    __slots__ = ('getVehicleData', 'remoteStartDrive', 'createStreamSession', 'streamMessage', 'chargingSetLimitAction', 'chargingStartStopAction', 'drivingClearSpeedLimitPinAction', 'drivingSetSpeedLimitAction', 'drivingSpeedLimitAction', 'hvacAutoAction', 'hvacSetPreconditioningMaxAction', 'hvacSteeringWheelHeaterAction', 'hvacTemperatureAdjustmentAction', 'mediaPlayAction', 'mediaUpdateVolume', 'mediaNextFavorite', 'mediaPreviousFavorite', 'mediaNextTrack', 'mediaPreviousTrack', 'navigationRequest', 'navigationSuperchargerRequest', 'getNearbyChargingSites', 'uiSetUpcomingCalendarEntries', 'vehicleControlCancelSoftwareUpdateAction', 'vehicleControlFlashLightsAction', 'vehicleControlHonkHornAction', 'vehicleControlResetValetPinAction', 'vehicleControlScheduleSoftwareUpdateAction', 'vehicleControlSetSentryModeAction', 'vehicleControlSetValetModeAction', 'vehicleControlSunroofOpenCloseAction', 'vehicleControlTriggerHomelinkAction', 'vehicleControlWindowAction', 'hvacBioweaponModeAction', 'hvacSeatHeaterActions', 'vehicleDataSubscription', 'vehicleDataAck', 'vitalsSubscription', 'vitalsAck', 'scheduledChargingAction', 'scheduledDepartureAction', 'setChargingAmpsAction', 'hvacClimateKeeperAction', 'hvacRecirculationAction', 'ping', 'dashcamSaveClipAction', 'autoSeatClimateAction', 'hvacSeatCoolerActions', 'setCabinOverheatProtectionAction', 'piiKeyRequest', 'pseudonymSyncRequest', 'navigationGpsRequest', 'setVehicleNameAction', 'setRateTariffRequest', 'getRateTariffRequest', 'videoRequestAction', 'takeDrivenoteAction', 'chargePortDoorClose', 'chargePortDoorOpen', 'bluetoothClassicPairingRequest', 'boomboxAction', 'guestModeAction', 'setCopTempAction', 'addManagedChargingSiteRequest', 'removeManagedChargingSiteRequest', 'navigationRouteAction', 'autoStwHeatAction', 'stwHeatLevelAction', 'eraseUserDataAction', 'getManagedChargingSitesRequest', 'updateChargeOnSolarFeatureRequest', 'getChargeOnSolarFeatureRequest', 'vehicleControlSetPinToDriveAction', 'vehicleControlResetPinToDriveAction', 'drivingClearSpeedLimitPinAdminAction', 'setOutletsOnOffAction', 'setOutletTimerAction', 'setOutletSocLimitAction', 'setPowerFeedOnOffAction', 'setPowerFeedTimerAction', 'setPowerFeedSocLimitAction', 'setTrailerLightTestStartStopAction', 'setTruckBedLightAutoStateAction', 'setTruckBedLightBrightnessAction', 'vehicleControlResetPinToDriveAdminAction', 'navigationWaypointsRequest', 'setPowershareFeatureAction', 'setPowershareDischargeLimitAction', 'setPowershareRequestAction', 'setTentModeRequestAction', 'setFrontZoneLightRequestAction', 'setRearZoneLightRequestAction', 'addChargeScheduleAction', 'removeChargeScheduleAction', 'addPreconditionScheduleAction', 'removePreconditionScheduleAction', 'setLightbarBrightnessAction', 'setLightbarMiddleAction', 'setLightbarDitchAction', 'getMessagesAction', 'teslaAuthResponseAction', 'navigationGpsDestinationRequest', 'batchRemovePreconditionSchedulesAction', 'batchRemoveChargeSchedulesAction', 'parentalControlsClearPinAction', 'parentalControlsClearPinAdminAction', 'parentalControlsAction', 'parentalControlsEnableSettingsAction', 'parentalControlsSetSpeedLimitAction', 'cancelSohTestAction', 'stopLightShowAction', 'startLightShowAction', 'setSuspensionLevelAction')
    GETVEHICLEDATA_FIELD_NUMBER: _ClassVar[int]
    REMOTESTARTDRIVE_FIELD_NUMBER: _ClassVar[int]
    CREATESTREAMSESSION_FIELD_NUMBER: _ClassVar[int]
    STREAMMESSAGE_FIELD_NUMBER: _ClassVar[int]
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
    NAVIGATIONREQUEST_FIELD_NUMBER: _ClassVar[int]
    NAVIGATIONSUPERCHARGERREQUEST_FIELD_NUMBER: _ClassVar[int]
    GETNEARBYCHARGINGSITES_FIELD_NUMBER: _ClassVar[int]
    UISETUPCOMINGCALENDARENTRIES_FIELD_NUMBER: _ClassVar[int]
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
    VEHICLEDATASUBSCRIPTION_FIELD_NUMBER: _ClassVar[int]
    VEHICLEDATAACK_FIELD_NUMBER: _ClassVar[int]
    VITALSSUBSCRIPTION_FIELD_NUMBER: _ClassVar[int]
    VITALSACK_FIELD_NUMBER: _ClassVar[int]
    SCHEDULEDCHARGINGACTION_FIELD_NUMBER: _ClassVar[int]
    SCHEDULEDDEPARTUREACTION_FIELD_NUMBER: _ClassVar[int]
    SETCHARGINGAMPSACTION_FIELD_NUMBER: _ClassVar[int]
    HVACCLIMATEKEEPERACTION_FIELD_NUMBER: _ClassVar[int]
    HVACRECIRCULATIONACTION_FIELD_NUMBER: _ClassVar[int]
    PING_FIELD_NUMBER: _ClassVar[int]
    DASHCAMSAVECLIPACTION_FIELD_NUMBER: _ClassVar[int]
    AUTOSEATCLIMATEACTION_FIELD_NUMBER: _ClassVar[int]
    HVACSEATCOOLERACTIONS_FIELD_NUMBER: _ClassVar[int]
    SETCABINOVERHEATPROTECTIONACTION_FIELD_NUMBER: _ClassVar[int]
    PIIKEYREQUEST_FIELD_NUMBER: _ClassVar[int]
    PSEUDONYMSYNCREQUEST_FIELD_NUMBER: _ClassVar[int]
    NAVIGATIONGPSREQUEST_FIELD_NUMBER: _ClassVar[int]
    SETVEHICLENAMEACTION_FIELD_NUMBER: _ClassVar[int]
    SETRATETARIFFREQUEST_FIELD_NUMBER: _ClassVar[int]
    GETRATETARIFFREQUEST_FIELD_NUMBER: _ClassVar[int]
    VIDEOREQUESTACTION_FIELD_NUMBER: _ClassVar[int]
    TAKEDRIVENOTEACTION_FIELD_NUMBER: _ClassVar[int]
    CHARGEPORTDOORCLOSE_FIELD_NUMBER: _ClassVar[int]
    CHARGEPORTDOOROPEN_FIELD_NUMBER: _ClassVar[int]
    BLUETOOTHCLASSICPAIRINGREQUEST_FIELD_NUMBER: _ClassVar[int]
    BOOMBOXACTION_FIELD_NUMBER: _ClassVar[int]
    GUESTMODEACTION_FIELD_NUMBER: _ClassVar[int]
    SETCOPTEMPACTION_FIELD_NUMBER: _ClassVar[int]
    ADDMANAGEDCHARGINGSITEREQUEST_FIELD_NUMBER: _ClassVar[int]
    REMOVEMANAGEDCHARGINGSITEREQUEST_FIELD_NUMBER: _ClassVar[int]
    NAVIGATIONROUTEACTION_FIELD_NUMBER: _ClassVar[int]
    AUTOSTWHEATACTION_FIELD_NUMBER: _ClassVar[int]
    STWHEATLEVELACTION_FIELD_NUMBER: _ClassVar[int]
    ERASEUSERDATAACTION_FIELD_NUMBER: _ClassVar[int]
    GETMANAGEDCHARGINGSITESREQUEST_FIELD_NUMBER: _ClassVar[int]
    UPDATECHARGEONSOLARFEATUREREQUEST_FIELD_NUMBER: _ClassVar[int]
    GETCHARGEONSOLARFEATUREREQUEST_FIELD_NUMBER: _ClassVar[int]
    VEHICLECONTROLSETPINTODRIVEACTION_FIELD_NUMBER: _ClassVar[int]
    VEHICLECONTROLRESETPINTODRIVEACTION_FIELD_NUMBER: _ClassVar[int]
    DRIVINGCLEARSPEEDLIMITPINADMINACTION_FIELD_NUMBER: _ClassVar[int]
    SETOUTLETSONOFFACTION_FIELD_NUMBER: _ClassVar[int]
    SETOUTLETTIMERACTION_FIELD_NUMBER: _ClassVar[int]
    SETOUTLETSOCLIMITACTION_FIELD_NUMBER: _ClassVar[int]
    SETPOWERFEEDONOFFACTION_FIELD_NUMBER: _ClassVar[int]
    SETPOWERFEEDTIMERACTION_FIELD_NUMBER: _ClassVar[int]
    SETPOWERFEEDSOCLIMITACTION_FIELD_NUMBER: _ClassVar[int]
    SETTRAILERLIGHTTESTSTARTSTOPACTION_FIELD_NUMBER: _ClassVar[int]
    SETTRUCKBEDLIGHTAUTOSTATEACTION_FIELD_NUMBER: _ClassVar[int]
    SETTRUCKBEDLIGHTBRIGHTNESSACTION_FIELD_NUMBER: _ClassVar[int]
    VEHICLECONTROLRESETPINTODRIVEADMINACTION_FIELD_NUMBER: _ClassVar[int]
    NAVIGATIONWAYPOINTSREQUEST_FIELD_NUMBER: _ClassVar[int]
    SETPOWERSHAREFEATUREACTION_FIELD_NUMBER: _ClassVar[int]
    SETPOWERSHAREDISCHARGELIMITACTION_FIELD_NUMBER: _ClassVar[int]
    SETPOWERSHAREREQUESTACTION_FIELD_NUMBER: _ClassVar[int]
    SETTENTMODEREQUESTACTION_FIELD_NUMBER: _ClassVar[int]
    SETFRONTZONELIGHTREQUESTACTION_FIELD_NUMBER: _ClassVar[int]
    SETREARZONELIGHTREQUESTACTION_FIELD_NUMBER: _ClassVar[int]
    ADDCHARGESCHEDULEACTION_FIELD_NUMBER: _ClassVar[int]
    REMOVECHARGESCHEDULEACTION_FIELD_NUMBER: _ClassVar[int]
    ADDPRECONDITIONSCHEDULEACTION_FIELD_NUMBER: _ClassVar[int]
    REMOVEPRECONDITIONSCHEDULEACTION_FIELD_NUMBER: _ClassVar[int]
    SETLIGHTBARBRIGHTNESSACTION_FIELD_NUMBER: _ClassVar[int]
    SETLIGHTBARMIDDLEACTION_FIELD_NUMBER: _ClassVar[int]
    SETLIGHTBARDITCHACTION_FIELD_NUMBER: _ClassVar[int]
    GETMESSAGESACTION_FIELD_NUMBER: _ClassVar[int]
    TESLAAUTHRESPONSEACTION_FIELD_NUMBER: _ClassVar[int]
    NAVIGATIONGPSDESTINATIONREQUEST_FIELD_NUMBER: _ClassVar[int]
    BATCHREMOVEPRECONDITIONSCHEDULESACTION_FIELD_NUMBER: _ClassVar[int]
    BATCHREMOVECHARGESCHEDULESACTION_FIELD_NUMBER: _ClassVar[int]
    PARENTALCONTROLSCLEARPINACTION_FIELD_NUMBER: _ClassVar[int]
    PARENTALCONTROLSCLEARPINADMINACTION_FIELD_NUMBER: _ClassVar[int]
    PARENTALCONTROLSACTION_FIELD_NUMBER: _ClassVar[int]
    PARENTALCONTROLSENABLESETTINGSACTION_FIELD_NUMBER: _ClassVar[int]
    PARENTALCONTROLSSETSPEEDLIMITACTION_FIELD_NUMBER: _ClassVar[int]
    CANCELSOHTESTACTION_FIELD_NUMBER: _ClassVar[int]
    STOPLIGHTSHOWACTION_FIELD_NUMBER: _ClassVar[int]
    STARTLIGHTSHOWACTION_FIELD_NUMBER: _ClassVar[int]
    SETSUSPENSIONLEVELACTION_FIELD_NUMBER: _ClassVar[int]
    getVehicleData: GetVehicleData
    remoteStartDrive: RemoteStartDrive
    createStreamSession: CreateStreamSession
    streamMessage: StreamMessage
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
    navigationRequest: NavigationRequest
    navigationSuperchargerRequest: NavigationSuperchargerRequest
    getNearbyChargingSites: GetNearbyChargingSites
    uiSetUpcomingCalendarEntries: UiSetUpcomingCalendarEntries
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
    vehicleDataSubscription: VehicleDataSubscription
    vehicleDataAck: VehicleDataAck
    vitalsSubscription: VitalsSubscription
    vitalsAck: VitalsAck
    scheduledChargingAction: ScheduledChargingAction
    scheduledDepartureAction: ScheduledDepartureAction
    setChargingAmpsAction: SetChargingAmpsAction
    hvacClimateKeeperAction: HvacClimateKeeperAction
    hvacRecirculationAction: HvacRecirculationAction
    ping: Ping
    dashcamSaveClipAction: DashcamSaveClipAction
    autoSeatClimateAction: AutoSeatClimateAction
    hvacSeatCoolerActions: HvacSeatCoolerActions
    setCabinOverheatProtectionAction: SetCabinOverheatProtectionAction
    piiKeyRequest: PiiKeyRequest
    pseudonymSyncRequest: PseudonymSyncRequest
    navigationGpsRequest: NavigationGpsRequest
    setVehicleNameAction: SetVehicleNameAction
    setRateTariffRequest: SetRateTariffRequest
    getRateTariffRequest: GetRateTariffRequest
    videoRequestAction: VideoRequestAction
    takeDrivenoteAction: TakeDrivenoteAction
    chargePortDoorClose: ChargePortDoorClose
    chargePortDoorOpen: ChargePortDoorOpen
    bluetoothClassicPairingRequest: BluetoothClassicPairingRequest
    boomboxAction: BoomboxAction
    guestModeAction: _vehicle_pb2.VehicleState.GuestMode
    setCopTempAction: SetCopTempAction
    addManagedChargingSiteRequest: AddManagedChargingSiteRequest
    removeManagedChargingSiteRequest: RemoveManagedChargingSiteRequest
    navigationRouteAction: NavigationRouteAction
    autoStwHeatAction: AutoStwHeatAction
    stwHeatLevelAction: StwHeatLevelAction
    eraseUserDataAction: EraseUserDataAction
    getManagedChargingSitesRequest: GetManagedChargingSitesRequest
    updateChargeOnSolarFeatureRequest: UpdateChargeOnSolarFeatureRequest
    getChargeOnSolarFeatureRequest: GetChargeOnSolarFeatureRequest
    vehicleControlSetPinToDriveAction: VehicleControlSetPinToDriveAction
    vehicleControlResetPinToDriveAction: VehicleControlResetPinToDriveAction
    drivingClearSpeedLimitPinAdminAction: DrivingClearSpeedLimitPinAdminAction
    setOutletsOnOffAction: SetOutletsOnOffAction
    setOutletTimerAction: SetOutletTimerAction
    setOutletSocLimitAction: SetOutletSocLimitAction
    setPowerFeedOnOffAction: SetPowerFeedOnOffAction
    setPowerFeedTimerAction: SetPowerFeedTimerAction
    setPowerFeedSocLimitAction: SetPowerFeedSocLimitAction
    setTrailerLightTestStartStopAction: SetTrailerLightTestStartStopAction
    setTruckBedLightAutoStateAction: SetTruckBedLightAutoStateAction
    setTruckBedLightBrightnessAction: SetTruckBedLightBrightnessAction
    vehicleControlResetPinToDriveAdminAction: VehicleControlResetPinToDriveAdminAction
    navigationWaypointsRequest: NavigationWaypointsRequest
    setPowershareFeatureAction: SetPowershareFeatureAction
    setPowershareDischargeLimitAction: SetPowershareDischargeLimitAction
    setPowershareRequestAction: SetPowershareRequestAction
    setTentModeRequestAction: SetTentModeRequestAction
    setFrontZoneLightRequestAction: SetZoneLightRequestAction
    setRearZoneLightRequestAction: SetZoneLightRequestAction
    addChargeScheduleAction: _common_pb2.ChargeSchedule
    removeChargeScheduleAction: RemoveChargeScheduleAction
    addPreconditionScheduleAction: _common_pb2.PreconditionSchedule
    removePreconditionScheduleAction: RemovePreconditionScheduleAction
    setLightbarBrightnessAction: SetLightbarBrightnessAction
    setLightbarMiddleAction: SetLightbarMiddleAction
    setLightbarDitchAction: SetLightbarDitchAction
    getMessagesAction: GetMessagesAction
    teslaAuthResponseAction: TeslaAuthResponseAction
    navigationGpsDestinationRequest: NavigationGpsDestinationRequest
    batchRemovePreconditionSchedulesAction: BatchRemovePreconditionSchedulesAction
    batchRemoveChargeSchedulesAction: BatchRemoveChargeSchedulesAction
    parentalControlsClearPinAction: ParentalControlsClearPinAction
    parentalControlsClearPinAdminAction: ParentalControlsClearPinAdminAction
    parentalControlsAction: ParentalControlsAction
    parentalControlsEnableSettingsAction: ParentalControlsEnableSettingsAction
    parentalControlsSetSpeedLimitAction: ParentalControlsSetSpeedLimitAction
    cancelSohTestAction: CancelSohTestAction
    stopLightShowAction: StopLightShowAction
    startLightShowAction: StartLightShowAction
    setSuspensionLevelAction: SetSuspensionLevelAction

    def __init__(self, getVehicleData: _Optional[_Union[GetVehicleData, _Mapping]]=..., remoteStartDrive: _Optional[_Union[RemoteStartDrive, _Mapping]]=..., createStreamSession: _Optional[_Union[CreateStreamSession, _Mapping]]=..., streamMessage: _Optional[_Union[StreamMessage, _Mapping]]=..., chargingSetLimitAction: _Optional[_Union[ChargingSetLimitAction, _Mapping]]=..., chargingStartStopAction: _Optional[_Union[ChargingStartStopAction, _Mapping]]=..., drivingClearSpeedLimitPinAction: _Optional[_Union[DrivingClearSpeedLimitPinAction, _Mapping]]=..., drivingSetSpeedLimitAction: _Optional[_Union[DrivingSetSpeedLimitAction, _Mapping]]=..., drivingSpeedLimitAction: _Optional[_Union[DrivingSpeedLimitAction, _Mapping]]=..., hvacAutoAction: _Optional[_Union[HvacAutoAction, _Mapping]]=..., hvacSetPreconditioningMaxAction: _Optional[_Union[HvacSetPreconditioningMaxAction, _Mapping]]=..., hvacSteeringWheelHeaterAction: _Optional[_Union[HvacSteeringWheelHeaterAction, _Mapping]]=..., hvacTemperatureAdjustmentAction: _Optional[_Union[HvacTemperatureAdjustmentAction, _Mapping]]=..., mediaPlayAction: _Optional[_Union[MediaPlayAction, _Mapping]]=..., mediaUpdateVolume: _Optional[_Union[MediaUpdateVolume, _Mapping]]=..., mediaNextFavorite: _Optional[_Union[MediaNextFavorite, _Mapping]]=..., mediaPreviousFavorite: _Optional[_Union[MediaPreviousFavorite, _Mapping]]=..., mediaNextTrack: _Optional[_Union[MediaNextTrack, _Mapping]]=..., mediaPreviousTrack: _Optional[_Union[MediaPreviousTrack, _Mapping]]=..., navigationRequest: _Optional[_Union[NavigationRequest, _Mapping]]=..., navigationSuperchargerRequest: _Optional[_Union[NavigationSuperchargerRequest, _Mapping]]=..., getNearbyChargingSites: _Optional[_Union[GetNearbyChargingSites, _Mapping]]=..., uiSetUpcomingCalendarEntries: _Optional[_Union[UiSetUpcomingCalendarEntries, _Mapping]]=..., vehicleControlCancelSoftwareUpdateAction: _Optional[_Union[VehicleControlCancelSoftwareUpdateAction, _Mapping]]=..., vehicleControlFlashLightsAction: _Optional[_Union[VehicleControlFlashLightsAction, _Mapping]]=..., vehicleControlHonkHornAction: _Optional[_Union[VehicleControlHonkHornAction, _Mapping]]=..., vehicleControlResetValetPinAction: _Optional[_Union[VehicleControlResetValetPinAction, _Mapping]]=..., vehicleControlScheduleSoftwareUpdateAction: _Optional[_Union[VehicleControlScheduleSoftwareUpdateAction, _Mapping]]=..., vehicleControlSetSentryModeAction: _Optional[_Union[VehicleControlSetSentryModeAction, _Mapping]]=..., vehicleControlSetValetModeAction: _Optional[_Union[VehicleControlSetValetModeAction, _Mapping]]=..., vehicleControlSunroofOpenCloseAction: _Optional[_Union[VehicleControlSunroofOpenCloseAction, _Mapping]]=..., vehicleControlTriggerHomelinkAction: _Optional[_Union[VehicleControlTriggerHomelinkAction, _Mapping]]=..., vehicleControlWindowAction: _Optional[_Union[VehicleControlWindowAction, _Mapping]]=..., hvacBioweaponModeAction: _Optional[_Union[HvacBioweaponModeAction, _Mapping]]=..., hvacSeatHeaterActions: _Optional[_Union[HvacSeatHeaterActions, _Mapping]]=..., vehicleDataSubscription: _Optional[_Union[VehicleDataSubscription, _Mapping]]=..., vehicleDataAck: _Optional[_Union[VehicleDataAck, _Mapping]]=..., vitalsSubscription: _Optional[_Union[VitalsSubscription, _Mapping]]=..., vitalsAck: _Optional[_Union[VitalsAck, _Mapping]]=..., scheduledChargingAction: _Optional[_Union[ScheduledChargingAction, _Mapping]]=..., scheduledDepartureAction: _Optional[_Union[ScheduledDepartureAction, _Mapping]]=..., setChargingAmpsAction: _Optional[_Union[SetChargingAmpsAction, _Mapping]]=..., hvacClimateKeeperAction: _Optional[_Union[HvacClimateKeeperAction, _Mapping]]=..., hvacRecirculationAction: _Optional[_Union[HvacRecirculationAction, _Mapping]]=..., ping: _Optional[_Union[Ping, _Mapping]]=..., dashcamSaveClipAction: _Optional[_Union[DashcamSaveClipAction, _Mapping]]=..., autoSeatClimateAction: _Optional[_Union[AutoSeatClimateAction, _Mapping]]=..., hvacSeatCoolerActions: _Optional[_Union[HvacSeatCoolerActions, _Mapping]]=..., setCabinOverheatProtectionAction: _Optional[_Union[SetCabinOverheatProtectionAction, _Mapping]]=..., piiKeyRequest: _Optional[_Union[PiiKeyRequest, _Mapping]]=..., pseudonymSyncRequest: _Optional[_Union[PseudonymSyncRequest, _Mapping]]=..., navigationGpsRequest: _Optional[_Union[NavigationGpsRequest, _Mapping]]=..., setVehicleNameAction: _Optional[_Union[SetVehicleNameAction, _Mapping]]=..., setRateTariffRequest: _Optional[_Union[SetRateTariffRequest, _Mapping]]=..., getRateTariffRequest: _Optional[_Union[GetRateTariffRequest, _Mapping]]=..., videoRequestAction: _Optional[_Union[VideoRequestAction, _Mapping]]=..., takeDrivenoteAction: _Optional[_Union[TakeDrivenoteAction, _Mapping]]=..., chargePortDoorClose: _Optional[_Union[ChargePortDoorClose, _Mapping]]=..., chargePortDoorOpen: _Optional[_Union[ChargePortDoorOpen, _Mapping]]=..., bluetoothClassicPairingRequest: _Optional[_Union[BluetoothClassicPairingRequest, _Mapping]]=..., boomboxAction: _Optional[_Union[BoomboxAction, _Mapping]]=..., guestModeAction: _Optional[_Union[_vehicle_pb2.VehicleState.GuestMode, _Mapping]]=..., setCopTempAction: _Optional[_Union[SetCopTempAction, _Mapping]]=..., addManagedChargingSiteRequest: _Optional[_Union[AddManagedChargingSiteRequest, _Mapping]]=..., removeManagedChargingSiteRequest: _Optional[_Union[RemoveManagedChargingSiteRequest, _Mapping]]=..., navigationRouteAction: _Optional[_Union[NavigationRouteAction, _Mapping]]=..., autoStwHeatAction: _Optional[_Union[AutoStwHeatAction, _Mapping]]=..., stwHeatLevelAction: _Optional[_Union[StwHeatLevelAction, _Mapping]]=..., eraseUserDataAction: _Optional[_Union[EraseUserDataAction, _Mapping]]=..., getManagedChargingSitesRequest: _Optional[_Union[GetManagedChargingSitesRequest, _Mapping]]=..., updateChargeOnSolarFeatureRequest: _Optional[_Union[UpdateChargeOnSolarFeatureRequest, _Mapping]]=..., getChargeOnSolarFeatureRequest: _Optional[_Union[GetChargeOnSolarFeatureRequest, _Mapping]]=..., vehicleControlSetPinToDriveAction: _Optional[_Union[VehicleControlSetPinToDriveAction, _Mapping]]=..., vehicleControlResetPinToDriveAction: _Optional[_Union[VehicleControlResetPinToDriveAction, _Mapping]]=..., drivingClearSpeedLimitPinAdminAction: _Optional[_Union[DrivingClearSpeedLimitPinAdminAction, _Mapping]]=..., setOutletsOnOffAction: _Optional[_Union[SetOutletsOnOffAction, _Mapping]]=..., setOutletTimerAction: _Optional[_Union[SetOutletTimerAction, _Mapping]]=..., setOutletSocLimitAction: _Optional[_Union[SetOutletSocLimitAction, _Mapping]]=..., setPowerFeedOnOffAction: _Optional[_Union[SetPowerFeedOnOffAction, _Mapping]]=..., setPowerFeedTimerAction: _Optional[_Union[SetPowerFeedTimerAction, _Mapping]]=..., setPowerFeedSocLimitAction: _Optional[_Union[SetPowerFeedSocLimitAction, _Mapping]]=..., setTrailerLightTestStartStopAction: _Optional[_Union[SetTrailerLightTestStartStopAction, _Mapping]]=..., setTruckBedLightAutoStateAction: _Optional[_Union[SetTruckBedLightAutoStateAction, _Mapping]]=..., setTruckBedLightBrightnessAction: _Optional[_Union[SetTruckBedLightBrightnessAction, _Mapping]]=..., vehicleControlResetPinToDriveAdminAction: _Optional[_Union[VehicleControlResetPinToDriveAdminAction, _Mapping]]=..., navigationWaypointsRequest: _Optional[_Union[NavigationWaypointsRequest, _Mapping]]=..., setPowershareFeatureAction: _Optional[_Union[SetPowershareFeatureAction, _Mapping]]=..., setPowershareDischargeLimitAction: _Optional[_Union[SetPowershareDischargeLimitAction, _Mapping]]=..., setPowershareRequestAction: _Optional[_Union[SetPowershareRequestAction, _Mapping]]=..., setTentModeRequestAction: _Optional[_Union[SetTentModeRequestAction, _Mapping]]=..., setFrontZoneLightRequestAction: _Optional[_Union[SetZoneLightRequestAction, _Mapping]]=..., setRearZoneLightRequestAction: _Optional[_Union[SetZoneLightRequestAction, _Mapping]]=..., addChargeScheduleAction: _Optional[_Union[_common_pb2.ChargeSchedule, _Mapping]]=..., removeChargeScheduleAction: _Optional[_Union[RemoveChargeScheduleAction, _Mapping]]=..., addPreconditionScheduleAction: _Optional[_Union[_common_pb2.PreconditionSchedule, _Mapping]]=..., removePreconditionScheduleAction: _Optional[_Union[RemovePreconditionScheduleAction, _Mapping]]=..., setLightbarBrightnessAction: _Optional[_Union[SetLightbarBrightnessAction, _Mapping]]=..., setLightbarMiddleAction: _Optional[_Union[SetLightbarMiddleAction, _Mapping]]=..., setLightbarDitchAction: _Optional[_Union[SetLightbarDitchAction, _Mapping]]=..., getMessagesAction: _Optional[_Union[GetMessagesAction, _Mapping]]=..., teslaAuthResponseAction: _Optional[_Union[TeslaAuthResponseAction, _Mapping]]=..., navigationGpsDestinationRequest: _Optional[_Union[NavigationGpsDestinationRequest, _Mapping]]=..., batchRemovePreconditionSchedulesAction: _Optional[_Union[BatchRemovePreconditionSchedulesAction, _Mapping]]=..., batchRemoveChargeSchedulesAction: _Optional[_Union[BatchRemoveChargeSchedulesAction, _Mapping]]=..., parentalControlsClearPinAction: _Optional[_Union[ParentalControlsClearPinAction, _Mapping]]=..., parentalControlsClearPinAdminAction: _Optional[_Union[ParentalControlsClearPinAdminAction, _Mapping]]=..., parentalControlsAction: _Optional[_Union[ParentalControlsAction, _Mapping]]=..., parentalControlsEnableSettingsAction: _Optional[_Union[ParentalControlsEnableSettingsAction, _Mapping]]=..., parentalControlsSetSpeedLimitAction: _Optional[_Union[ParentalControlsSetSpeedLimitAction, _Mapping]]=..., cancelSohTestAction: _Optional[_Union[CancelSohTestAction, _Mapping]]=..., stopLightShowAction: _Optional[_Union[StopLightShowAction, _Mapping]]=..., startLightShowAction: _Optional[_Union[StartLightShowAction, _Mapping]]=..., setSuspensionLevelAction: _Optional[_Union[SetSuspensionLevelAction, _Mapping]]=...) -> None:
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

    def __init__(self, timestamp: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]]=..., superchargers: _Optional[_Iterable[_Union[Superchargers, _Mapping]]]=..., congestion_sync_time_utc_secs: _Optional[int]=...) -> None:
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

    def __init__(self, ping_id: _Optional[int]=..., local_timestamp: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]]=..., last_remote_timestamp: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]]=...) -> None:
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

class HvacRecirculationAction(_message.Message):
    __slots__ = ('on',)
    ON_FIELD_NUMBER: _ClassVar[int]
    on: bool

    def __init__(self, on: bool=...) -> None:
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

class BoomboxAction(_message.Message):
    __slots__ = ('sound',)
    SOUND_FIELD_NUMBER: _ClassVar[int]
    sound: int

    def __init__(self, sound: _Optional[int]=...) -> None:
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

class RemoteStartDrive(_message.Message):
    __slots__ = ()

    def __init__(self) -> None:
        ...

class CreateStreamSession(_message.Message):
    __slots__ = ('session_id',)
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str

    def __init__(self, session_id: _Optional[str]=...) -> None:
        ...

class StreamMessage(_message.Message):
    __slots__ = ('session_id', 'data')
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    data: bytes

    def __init__(self, session_id: _Optional[str]=..., data: _Optional[bytes]=...) -> None:
        ...

class NavigationRequest(_message.Message):
    __slots__ = ('destination', 'order')
    DESTINATION_FIELD_NUMBER: _ClassVar[int]
    ORDER_FIELD_NUMBER: _ClassVar[int]
    destination: str
    order: int

    def __init__(self, destination: _Optional[str]=..., order: _Optional[int]=...) -> None:
        ...

class NavigationSuperchargerRequest(_message.Message):
    __slots__ = ('order',)
    ORDER_FIELD_NUMBER: _ClassVar[int]
    order: int

    def __init__(self, order: _Optional[int]=...) -> None:
        ...

class UiSetUpcomingCalendarEntries(_message.Message):
    __slots__ = ('calendar_data',)
    CALENDAR_DATA_FIELD_NUMBER: _ClassVar[int]
    calendar_data: str

    def __init__(self, calendar_data: _Optional[str]=...) -> None:
        ...

class VehicleDataSubscription(_message.Message):
    __slots__ = ('pii_key_request', 'subscription_duration_s', 'subscription_ping_s', 'gui_settings_max_update_rate_ms', 'charge_state_max_update_rate_ms', 'climate_state_max_update_rate_ms', 'drive_state_max_update_rate_ms', 'vehicle_state_max_update_rate_ms', 'vehicle_config_max_update_rate_ms', 'location_state_max_update_rate_ms', 'closures_state_max_update_rate_ms', 'parked_accessory_state_max_update_rate_ms', 'charge_schedule_state_max_update_rate_ms', 'preconditioning_schedule_state_max_update_rate_ms', 'alert_state_max_update_rate_ms', 'suspension_state_max_update_rate_ms')

    class PiiKeyRequest(_message.Message):
        __slots__ = ('subscriber_public_key',)
        SUBSCRIBER_PUBLIC_KEY_FIELD_NUMBER: _ClassVar[int]
        subscriber_public_key: str

        def __init__(self, subscriber_public_key: _Optional[str]=...) -> None:
            ...
    PII_KEY_REQUEST_FIELD_NUMBER: _ClassVar[int]
    SUBSCRIPTION_DURATION_S_FIELD_NUMBER: _ClassVar[int]
    SUBSCRIPTION_PING_S_FIELD_NUMBER: _ClassVar[int]
    GUI_SETTINGS_MAX_UPDATE_RATE_MS_FIELD_NUMBER: _ClassVar[int]
    CHARGE_STATE_MAX_UPDATE_RATE_MS_FIELD_NUMBER: _ClassVar[int]
    CLIMATE_STATE_MAX_UPDATE_RATE_MS_FIELD_NUMBER: _ClassVar[int]
    DRIVE_STATE_MAX_UPDATE_RATE_MS_FIELD_NUMBER: _ClassVar[int]
    VEHICLE_STATE_MAX_UPDATE_RATE_MS_FIELD_NUMBER: _ClassVar[int]
    VEHICLE_CONFIG_MAX_UPDATE_RATE_MS_FIELD_NUMBER: _ClassVar[int]
    LOCATION_STATE_MAX_UPDATE_RATE_MS_FIELD_NUMBER: _ClassVar[int]
    CLOSURES_STATE_MAX_UPDATE_RATE_MS_FIELD_NUMBER: _ClassVar[int]
    PARKED_ACCESSORY_STATE_MAX_UPDATE_RATE_MS_FIELD_NUMBER: _ClassVar[int]
    CHARGE_SCHEDULE_STATE_MAX_UPDATE_RATE_MS_FIELD_NUMBER: _ClassVar[int]
    PRECONDITIONING_SCHEDULE_STATE_MAX_UPDATE_RATE_MS_FIELD_NUMBER: _ClassVar[int]
    ALERT_STATE_MAX_UPDATE_RATE_MS_FIELD_NUMBER: _ClassVar[int]
    SUSPENSION_STATE_MAX_UPDATE_RATE_MS_FIELD_NUMBER: _ClassVar[int]
    pii_key_request: VehicleDataSubscription.PiiKeyRequest
    subscription_duration_s: int
    subscription_ping_s: int
    gui_settings_max_update_rate_ms: int
    charge_state_max_update_rate_ms: int
    climate_state_max_update_rate_ms: int
    drive_state_max_update_rate_ms: int
    vehicle_state_max_update_rate_ms: int
    vehicle_config_max_update_rate_ms: int
    location_state_max_update_rate_ms: int
    closures_state_max_update_rate_ms: int
    parked_accessory_state_max_update_rate_ms: int
    charge_schedule_state_max_update_rate_ms: int
    preconditioning_schedule_state_max_update_rate_ms: int
    alert_state_max_update_rate_ms: int
    suspension_state_max_update_rate_ms: int

    def __init__(self, pii_key_request: _Optional[_Union[VehicleDataSubscription.PiiKeyRequest, _Mapping]]=..., subscription_duration_s: _Optional[int]=..., subscription_ping_s: _Optional[int]=..., gui_settings_max_update_rate_ms: _Optional[int]=..., charge_state_max_update_rate_ms: _Optional[int]=..., climate_state_max_update_rate_ms: _Optional[int]=..., drive_state_max_update_rate_ms: _Optional[int]=..., vehicle_state_max_update_rate_ms: _Optional[int]=..., vehicle_config_max_update_rate_ms: _Optional[int]=..., location_state_max_update_rate_ms: _Optional[int]=..., closures_state_max_update_rate_ms: _Optional[int]=..., parked_accessory_state_max_update_rate_ms: _Optional[int]=..., charge_schedule_state_max_update_rate_ms: _Optional[int]=..., preconditioning_schedule_state_max_update_rate_ms: _Optional[int]=..., alert_state_max_update_rate_ms: _Optional[int]=..., suspension_state_max_update_rate_ms: _Optional[int]=...) -> None:
        ...

class VehicleDataAck(_message.Message):
    __slots__ = ('charge_state_timestamp', 'climate_state_timestamp', 'closures_state_timestamp', 'drive_state_timestamp', 'gui_settings_timestamp', 'location_state_timestamp', 'vehicle_config_timestamp', 'vehicle_state_timestamp', 'parked_accessory_state_timestamp', 'charge_schedule_state_timestamp', 'preconditioning_schedule_state_timestamp', 'alert_state_timestamp', 'suspension_state_timestamp', 'decryption_error_field')
    CHARGE_STATE_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    CLIMATE_STATE_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    CLOSURES_STATE_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    DRIVE_STATE_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    GUI_SETTINGS_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    LOCATION_STATE_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    VEHICLE_CONFIG_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    VEHICLE_STATE_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    PARKED_ACCESSORY_STATE_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    CHARGE_SCHEDULE_STATE_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    PRECONDITIONING_SCHEDULE_STATE_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    ALERT_STATE_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    SUSPENSION_STATE_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    DECRYPTION_ERROR_FIELD_FIELD_NUMBER: _ClassVar[int]
    charge_state_timestamp: _timestamp_pb2.Timestamp
    climate_state_timestamp: _timestamp_pb2.Timestamp
    closures_state_timestamp: _timestamp_pb2.Timestamp
    drive_state_timestamp: _timestamp_pb2.Timestamp
    gui_settings_timestamp: _timestamp_pb2.Timestamp
    location_state_timestamp: _timestamp_pb2.Timestamp
    vehicle_config_timestamp: _timestamp_pb2.Timestamp
    vehicle_state_timestamp: _timestamp_pb2.Timestamp
    parked_accessory_state_timestamp: _timestamp_pb2.Timestamp
    charge_schedule_state_timestamp: _timestamp_pb2.Timestamp
    preconditioning_schedule_state_timestamp: _timestamp_pb2.Timestamp
    alert_state_timestamp: _timestamp_pb2.Timestamp
    suspension_state_timestamp: _timestamp_pb2.Timestamp
    decryption_error_field: _containers.RepeatedScalarFieldContainer[int]

    def __init__(self, charge_state_timestamp: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]]=..., climate_state_timestamp: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]]=..., closures_state_timestamp: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]]=..., drive_state_timestamp: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]]=..., gui_settings_timestamp: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]]=..., location_state_timestamp: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]]=..., vehicle_config_timestamp: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]]=..., vehicle_state_timestamp: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]]=..., parked_accessory_state_timestamp: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]]=..., charge_schedule_state_timestamp: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]]=..., preconditioning_schedule_state_timestamp: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]]=..., alert_state_timestamp: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]]=..., suspension_state_timestamp: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]]=..., decryption_error_field: _Optional[_Iterable[int]]=...) -> None:
        ...

class VitalsSubscription(_message.Message):
    __slots__ = ('session_id',)
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: int

    def __init__(self, session_id: _Optional[int]=...) -> None:
        ...

class VitalsAck(_message.Message):
    __slots__ = ()

    def __init__(self) -> None:
        ...

class DashcamSaveClipAction(_message.Message):
    __slots__ = ()

    def __init__(self) -> None:
        ...

class PiiKeyRequest(_message.Message):
    __slots__ = ('subscriber_public_key', 'pii_key_expiration')
    SUBSCRIBER_PUBLIC_KEY_FIELD_NUMBER: _ClassVar[int]
    PII_KEY_EXPIRATION_FIELD_NUMBER: _ClassVar[int]
    subscriber_public_key: str
    pii_key_expiration: _timestamp_pb2.Timestamp

    def __init__(self, subscriber_public_key: _Optional[str]=..., pii_key_expiration: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]]=...) -> None:
        ...

class PseudonymSyncRequest(_message.Message):
    __slots__ = ('last_known_pseudonym_hashed',)
    LAST_KNOWN_PSEUDONYM_HASHED_FIELD_NUMBER: _ClassVar[int]
    last_known_pseudonym_hashed: bytes

    def __init__(self, last_known_pseudonym_hashed: _Optional[bytes]=...) -> None:
        ...

class NavigationGpsRequest(_message.Message):
    __slots__ = ('lat', 'lon', 'order')

    class RemoteNavTripOrder(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        REMOTE_NAV_TRIP_ORDER_UNKNOWN: _ClassVar[NavigationGpsRequest.RemoteNavTripOrder]
        REMOTE_NAV_TRIP_ORDER_REPLACE: _ClassVar[NavigationGpsRequest.RemoteNavTripOrder]
        REMOTE_NAV_TRIP_ORDER_PREPEND: _ClassVar[NavigationGpsRequest.RemoteNavTripOrder]
        REMOTE_NAV_TRIP_ORDER_APPEND: _ClassVar[NavigationGpsRequest.RemoteNavTripOrder]
    REMOTE_NAV_TRIP_ORDER_UNKNOWN: NavigationGpsRequest.RemoteNavTripOrder
    REMOTE_NAV_TRIP_ORDER_REPLACE: NavigationGpsRequest.RemoteNavTripOrder
    REMOTE_NAV_TRIP_ORDER_PREPEND: NavigationGpsRequest.RemoteNavTripOrder
    REMOTE_NAV_TRIP_ORDER_APPEND: NavigationGpsRequest.RemoteNavTripOrder
    LAT_FIELD_NUMBER: _ClassVar[int]
    LON_FIELD_NUMBER: _ClassVar[int]
    ORDER_FIELD_NUMBER: _ClassVar[int]
    lat: float
    lon: float
    order: NavigationGpsRequest.RemoteNavTripOrder

    def __init__(self, lat: _Optional[float]=..., lon: _Optional[float]=..., order: _Optional[_Union[NavigationGpsRequest.RemoteNavTripOrder, str]]=...) -> None:
        ...

class SetRateTariffRequest(_message.Message):
    __slots__ = ()

    def __init__(self) -> None:
        ...

class GetRateTariffRequest(_message.Message):
    __slots__ = ()

    def __init__(self) -> None:
        ...

class VideoRequestAction(_message.Message):
    __slots__ = ('url',)
    URL_FIELD_NUMBER: _ClassVar[int]
    url: str

    def __init__(self, url: _Optional[str]=...) -> None:
        ...

class TakeDrivenoteAction(_message.Message):
    __slots__ = ('note',)
    NOTE_FIELD_NUMBER: _ClassVar[int]
    note: str

    def __init__(self, note: _Optional[str]=...) -> None:
        ...

class BluetoothClassicPairingRequest(_message.Message):
    __slots__ = ('utf8_name', 'mac_address')
    UTF8_NAME_FIELD_NUMBER: _ClassVar[int]
    MAC_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    utf8_name: str
    mac_address: bytes

    def __init__(self, utf8_name: _Optional[str]=..., mac_address: _Optional[bytes]=...) -> None:
        ...

class AddManagedChargingSiteRequest(_message.Message):
    __slots__ = ()

    def __init__(self) -> None:
        ...

class RemoveManagedChargingSiteRequest(_message.Message):
    __slots__ = ('public_key',)
    PUBLIC_KEY_FIELD_NUMBER: _ClassVar[int]
    public_key: str

    def __init__(self, public_key: _Optional[str]=...) -> None:
        ...

class NavigationRouteAction(_message.Message):
    __slots__ = ()

    def __init__(self) -> None:
        ...

class AutoStwHeatAction(_message.Message):
    __slots__ = ('on',)
    ON_FIELD_NUMBER: _ClassVar[int]
    on: bool

    def __init__(self, on: bool=...) -> None:
        ...

class StwHeatLevelAction(_message.Message):
    __slots__ = ('stw_heat_level',)
    STW_HEAT_LEVEL_FIELD_NUMBER: _ClassVar[int]
    stw_heat_level: _common_pb2.StwHeatLevel

    def __init__(self, stw_heat_level: _Optional[_Union[_common_pb2.StwHeatLevel, str]]=...) -> None:
        ...

class GetManagedChargingSitesRequest(_message.Message):
    __slots__ = ()

    def __init__(self) -> None:
        ...

class UpdateChargeOnSolarFeatureRequest(_message.Message):
    __slots__ = ('charge_on_solar',)
    CHARGE_ON_SOLAR_FIELD_NUMBER: _ClassVar[int]
    charge_on_solar: ChargeOnSolarFeature

    def __init__(self, charge_on_solar: _Optional[_Union[ChargeOnSolarFeature, _Mapping]]=...) -> None:
        ...

class GetChargeOnSolarFeatureRequest(_message.Message):
    __slots__ = ()

    def __init__(self) -> None:
        ...

class ChargeOnSolarFeature(_message.Message):
    __slots__ = ('enabled', 'lower_charge_limit', 'upper_charge_limit')
    ENABLED_FIELD_NUMBER: _ClassVar[int]
    LOWER_CHARGE_LIMIT_FIELD_NUMBER: _ClassVar[int]
    UPPER_CHARGE_LIMIT_FIELD_NUMBER: _ClassVar[int]
    enabled: bool
    lower_charge_limit: float
    upper_charge_limit: float

    def __init__(self, enabled: bool=..., lower_charge_limit: _Optional[float]=..., upper_charge_limit: _Optional[float]=...) -> None:
        ...

class DrivingClearSpeedLimitPinAdminAction(_message.Message):
    __slots__ = ()

    def __init__(self) -> None:
        ...

class SetOutletsOnOffAction(_message.Message):
    __slots__ = ('outlet_request',)

    class OutletRequest(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        OUTLET_REQUEST_UNKNOWN: _ClassVar[SetOutletsOnOffAction.OutletRequest]
        OUTLET_REQUEST_OFF: _ClassVar[SetOutletsOnOffAction.OutletRequest]
        OUTLET_REQUEST_CABIN_AND_BED: _ClassVar[SetOutletsOnOffAction.OutletRequest]
        OUTLET_REQUEST_CABIN: _ClassVar[SetOutletsOnOffAction.OutletRequest]
    OUTLET_REQUEST_UNKNOWN: SetOutletsOnOffAction.OutletRequest
    OUTLET_REQUEST_OFF: SetOutletsOnOffAction.OutletRequest
    OUTLET_REQUEST_CABIN_AND_BED: SetOutletsOnOffAction.OutletRequest
    OUTLET_REQUEST_CABIN: SetOutletsOnOffAction.OutletRequest
    OUTLET_REQUEST_FIELD_NUMBER: _ClassVar[int]
    outlet_request: SetOutletsOnOffAction.OutletRequest

    def __init__(self, outlet_request: _Optional[_Union[SetOutletsOnOffAction.OutletRequest, str]]=...) -> None:
        ...

class SetOutletTimerAction(_message.Message):
    __slots__ = ('num_minutes',)
    NUM_MINUTES_FIELD_NUMBER: _ClassVar[int]
    num_minutes: int

    def __init__(self, num_minutes: _Optional[int]=...) -> None:
        ...

class SetOutletSocLimitAction(_message.Message):
    __slots__ = ('percent',)
    PERCENT_FIELD_NUMBER: _ClassVar[int]
    percent: int

    def __init__(self, percent: _Optional[int]=...) -> None:
        ...

class SetPowerFeedOnOffAction(_message.Message):
    __slots__ = ('power_feed_request',)

    class PowerFeedRequest(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        POWER_FEED_REQUEST_UNKNOWN: _ClassVar[SetPowerFeedOnOffAction.PowerFeedRequest]
        POWER_FEED_REQUEST_OFF: _ClassVar[SetPowerFeedOnOffAction.PowerFeedRequest]
        POWER_FEED_REQUEST_FEED_1: _ClassVar[SetPowerFeedOnOffAction.PowerFeedRequest]
        POWER_FEED_REQUEST_FEED_2: _ClassVar[SetPowerFeedOnOffAction.PowerFeedRequest]
        POWER_FEED_REQUEST_FEED_1_AND_FEED_2: _ClassVar[SetPowerFeedOnOffAction.PowerFeedRequest]
    POWER_FEED_REQUEST_UNKNOWN: SetPowerFeedOnOffAction.PowerFeedRequest
    POWER_FEED_REQUEST_OFF: SetPowerFeedOnOffAction.PowerFeedRequest
    POWER_FEED_REQUEST_FEED_1: SetPowerFeedOnOffAction.PowerFeedRequest
    POWER_FEED_REQUEST_FEED_2: SetPowerFeedOnOffAction.PowerFeedRequest
    POWER_FEED_REQUEST_FEED_1_AND_FEED_2: SetPowerFeedOnOffAction.PowerFeedRequest
    POWER_FEED_REQUEST_FIELD_NUMBER: _ClassVar[int]
    power_feed_request: SetPowerFeedOnOffAction.PowerFeedRequest

    def __init__(self, power_feed_request: _Optional[_Union[SetPowerFeedOnOffAction.PowerFeedRequest, str]]=...) -> None:
        ...

class SetPowerFeedTimerAction(_message.Message):
    __slots__ = ('num_minutes',)
    NUM_MINUTES_FIELD_NUMBER: _ClassVar[int]
    num_minutes: int

    def __init__(self, num_minutes: _Optional[int]=...) -> None:
        ...

class SetPowerFeedSocLimitAction(_message.Message):
    __slots__ = ('percent',)
    PERCENT_FIELD_NUMBER: _ClassVar[int]
    percent: int

    def __init__(self, percent: _Optional[int]=...) -> None:
        ...

class SetTrailerLightTestStartStopAction(_message.Message):
    __slots__ = ('start_stop',)
    START_STOP_FIELD_NUMBER: _ClassVar[int]
    start_stop: bool

    def __init__(self, start_stop: bool=...) -> None:
        ...

class SetTruckBedLightAutoStateAction(_message.Message):
    __slots__ = ('power_state',)
    POWER_STATE_FIELD_NUMBER: _ClassVar[int]
    power_state: bool

    def __init__(self, power_state: bool=...) -> None:
        ...

class SetTruckBedLightBrightnessAction(_message.Message):
    __slots__ = ('brightness',)
    BRIGHTNESS_FIELD_NUMBER: _ClassVar[int]
    brightness: int

    def __init__(self, brightness: _Optional[int]=...) -> None:
        ...

class VehicleControlResetPinToDriveAdminAction(_message.Message):
    __slots__ = ()

    def __init__(self) -> None:
        ...

class NavigationWaypointsRequest(_message.Message):
    __slots__ = ('waypoints', 'trip_plan_options')

    class TripPlanOptions(_message.Message):
        __slots__ = ('destination_start_soe', 'destination_arrival_soe')
        DESTINATION_START_SOE_FIELD_NUMBER: _ClassVar[int]
        DESTINATION_ARRIVAL_SOE_FIELD_NUMBER: _ClassVar[int]
        destination_start_soe: int
        destination_arrival_soe: int

        def __init__(self, destination_start_soe: _Optional[int]=..., destination_arrival_soe: _Optional[int]=...) -> None:
            ...
    WAYPOINTS_FIELD_NUMBER: _ClassVar[int]
    TRIP_PLAN_OPTIONS_FIELD_NUMBER: _ClassVar[int]
    waypoints: str
    trip_plan_options: NavigationWaypointsRequest.TripPlanOptions

    def __init__(self, waypoints: _Optional[str]=..., trip_plan_options: _Optional[_Union[NavigationWaypointsRequest.TripPlanOptions, _Mapping]]=...) -> None:
        ...

class SetPowershareFeatureAction(_message.Message):
    __slots__ = ('powershare_feature_request',)

    class PowershareFeatureRequest(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        POWERSHARE_FEATURE_REQUEST_UNKNOWN: _ClassVar[SetPowershareFeatureAction.PowershareFeatureRequest]
        POWERSHARE_FEATURE_REQUEST_OFF: _ClassVar[SetPowershareFeatureAction.PowershareFeatureRequest]
        POWERSHARE_FEATURE_REQUEST_ON: _ClassVar[SetPowershareFeatureAction.PowershareFeatureRequest]
    POWERSHARE_FEATURE_REQUEST_UNKNOWN: SetPowershareFeatureAction.PowershareFeatureRequest
    POWERSHARE_FEATURE_REQUEST_OFF: SetPowershareFeatureAction.PowershareFeatureRequest
    POWERSHARE_FEATURE_REQUEST_ON: SetPowershareFeatureAction.PowershareFeatureRequest
    POWERSHARE_FEATURE_REQUEST_FIELD_NUMBER: _ClassVar[int]
    powershare_feature_request: SetPowershareFeatureAction.PowershareFeatureRequest

    def __init__(self, powershare_feature_request: _Optional[_Union[SetPowershareFeatureAction.PowershareFeatureRequest, str]]=...) -> None:
        ...

class SetPowershareDischargeLimitAction(_message.Message):
    __slots__ = ('powershare_discharge_limit',)
    POWERSHARE_DISCHARGE_LIMIT_FIELD_NUMBER: _ClassVar[int]
    powershare_discharge_limit: int

    def __init__(self, powershare_discharge_limit: _Optional[int]=...) -> None:
        ...

class SetPowershareRequestAction(_message.Message):
    __slots__ = ('powershare_request',)

    class PowershareRequest(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        POWERSHARE_REQUEST_UNKNOWN: _ClassVar[SetPowershareRequestAction.PowershareRequest]
        POWERSHARE_REQUEST_OFF: _ClassVar[SetPowershareRequestAction.PowershareRequest]
        POWERSHARE_REQUEST_ON: _ClassVar[SetPowershareRequestAction.PowershareRequest]
    POWERSHARE_REQUEST_UNKNOWN: SetPowershareRequestAction.PowershareRequest
    POWERSHARE_REQUEST_OFF: SetPowershareRequestAction.PowershareRequest
    POWERSHARE_REQUEST_ON: SetPowershareRequestAction.PowershareRequest
    POWERSHARE_REQUEST_FIELD_NUMBER: _ClassVar[int]
    powershare_request: SetPowershareRequestAction.PowershareRequest

    def __init__(self, powershare_request: _Optional[_Union[SetPowershareRequestAction.PowershareRequest, str]]=...) -> None:
        ...

class SetTentModeRequestAction(_message.Message):
    __slots__ = ('on',)
    ON_FIELD_NUMBER: _ClassVar[int]
    on: bool

    def __init__(self, on: bool=...) -> None:
        ...

class SetZoneLightRequestAction(_message.Message):
    __slots__ = ('zone_light_request',)

    class ZoneLightRequest(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        ZONE_LIGHT_REQUEST_OFF: _ClassVar[SetZoneLightRequestAction.ZoneLightRequest]
        ZONE_LIGHT_REQUEST_LOW: _ClassVar[SetZoneLightRequestAction.ZoneLightRequest]
        ZONE_LIGHT_REQUEST_MED: _ClassVar[SetZoneLightRequestAction.ZoneLightRequest]
        ZONE_LIGHT_REQUEST_HIGH: _ClassVar[SetZoneLightRequestAction.ZoneLightRequest]
    ZONE_LIGHT_REQUEST_OFF: SetZoneLightRequestAction.ZoneLightRequest
    ZONE_LIGHT_REQUEST_LOW: SetZoneLightRequestAction.ZoneLightRequest
    ZONE_LIGHT_REQUEST_MED: SetZoneLightRequestAction.ZoneLightRequest
    ZONE_LIGHT_REQUEST_HIGH: SetZoneLightRequestAction.ZoneLightRequest
    ZONE_LIGHT_REQUEST_FIELD_NUMBER: _ClassVar[int]
    zone_light_request: SetZoneLightRequestAction.ZoneLightRequest

    def __init__(self, zone_light_request: _Optional[_Union[SetZoneLightRequestAction.ZoneLightRequest, str]]=...) -> None:
        ...

class SetLightbarBrightnessAction(_message.Message):
    __slots__ = ('brightness_request',)
    BRIGHTNESS_REQUEST_FIELD_NUMBER: _ClassVar[int]
    brightness_request: int

    def __init__(self, brightness_request: _Optional[int]=...) -> None:
        ...

class SetLightbarMiddleAction(_message.Message):
    __slots__ = ('middle_light_request',)
    MIDDLE_LIGHT_REQUEST_FIELD_NUMBER: _ClassVar[int]
    middle_light_request: bool

    def __init__(self, middle_light_request: bool=...) -> None:
        ...

class SetLightbarDitchAction(_message.Message):
    __slots__ = ('ditch_lights_request',)
    DITCH_LIGHTS_REQUEST_FIELD_NUMBER: _ClassVar[int]
    ditch_lights_request: bool

    def __init__(self, ditch_lights_request: bool=...) -> None:
        ...

class GetMessagesAction(_message.Message):
    __slots__ = ()

    def __init__(self) -> None:
        ...

class TeslaAuthResponseAction(_message.Message):
    __slots__ = ('client_id', 'scope', 'access_token', 'refresh_token', 'expiry_timestamp', 'error', 'scoped_token')
    CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
    SCOPE_FIELD_NUMBER: _ClassVar[int]
    ACCESS_TOKEN_FIELD_NUMBER: _ClassVar[int]
    REFRESH_TOKEN_FIELD_NUMBER: _ClassVar[int]
    EXPIRY_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    SCOPED_TOKEN_FIELD_NUMBER: _ClassVar[int]
    client_id: str
    scope: str
    access_token: str
    refresh_token: str
    expiry_timestamp: int
    error: str
    scoped_token: str

    def __init__(self, client_id: _Optional[str]=..., scope: _Optional[str]=..., access_token: _Optional[str]=..., refresh_token: _Optional[str]=..., expiry_timestamp: _Optional[int]=..., error: _Optional[str]=..., scoped_token: _Optional[str]=...) -> None:
        ...

class NavigationGpsDestinationRequest(_message.Message):
    __slots__ = ('lat', 'lon', 'destination', 'order')

    class RemoteNavTripOrder(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        REMOTE_NAV_TRIP_ORDER_UNKNOWN: _ClassVar[NavigationGpsDestinationRequest.RemoteNavTripOrder]
        REMOTE_NAV_TRIP_ORDER_REPLACE: _ClassVar[NavigationGpsDestinationRequest.RemoteNavTripOrder]
        REMOTE_NAV_TRIP_ORDER_PREPEND: _ClassVar[NavigationGpsDestinationRequest.RemoteNavTripOrder]
        REMOTE_NAV_TRIP_ORDER_APPEND: _ClassVar[NavigationGpsDestinationRequest.RemoteNavTripOrder]
    REMOTE_NAV_TRIP_ORDER_UNKNOWN: NavigationGpsDestinationRequest.RemoteNavTripOrder
    REMOTE_NAV_TRIP_ORDER_REPLACE: NavigationGpsDestinationRequest.RemoteNavTripOrder
    REMOTE_NAV_TRIP_ORDER_PREPEND: NavigationGpsDestinationRequest.RemoteNavTripOrder
    REMOTE_NAV_TRIP_ORDER_APPEND: NavigationGpsDestinationRequest.RemoteNavTripOrder
    LAT_FIELD_NUMBER: _ClassVar[int]
    LON_FIELD_NUMBER: _ClassVar[int]
    DESTINATION_FIELD_NUMBER: _ClassVar[int]
    ORDER_FIELD_NUMBER: _ClassVar[int]
    lat: float
    lon: float
    destination: str
    order: NavigationGpsDestinationRequest.RemoteNavTripOrder

    def __init__(self, lat: _Optional[float]=..., lon: _Optional[float]=..., destination: _Optional[str]=..., order: _Optional[_Union[NavigationGpsDestinationRequest.RemoteNavTripOrder, str]]=...) -> None:
        ...

class ParentalControlsClearPinAction(_message.Message):
    __slots__ = ('pin',)
    PIN_FIELD_NUMBER: _ClassVar[int]
    pin: str

    def __init__(self, pin: _Optional[str]=...) -> None:
        ...

class ParentalControlsClearPinAdminAction(_message.Message):
    __slots__ = ()

    def __init__(self) -> None:
        ...

class ParentalControlsAction(_message.Message):
    __slots__ = ('activate', 'pin')
    ACTIVATE_FIELD_NUMBER: _ClassVar[int]
    PIN_FIELD_NUMBER: _ClassVar[int]
    activate: bool
    pin: str

    def __init__(self, activate: bool=..., pin: _Optional[str]=...) -> None:
        ...

class ParentalControlsEnableSettingsAction(_message.Message):
    __slots__ = ('setting', 'enable')

    class ParentalControlsSetting(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        PARENTAL_CONTROLS_SETTING_UNKNOWN: _ClassVar[ParentalControlsEnableSettingsAction.ParentalControlsSetting]
        PARENTAL_CONTROLS_SETTING_SPEED_LIMIT: _ClassVar[ParentalControlsEnableSettingsAction.ParentalControlsSetting]
        PARENTAL_CONTROLS_SETTING_ACCELERATION: _ClassVar[ParentalControlsEnableSettingsAction.ParentalControlsSetting]
        PARENTAL_CONTROLS_SETTING_SAFETY_FEATURES: _ClassVar[ParentalControlsEnableSettingsAction.ParentalControlsSetting]
        PARENTAL_CONTROLS_SETTING_CURFEW: _ClassVar[ParentalControlsEnableSettingsAction.ParentalControlsSetting]
    PARENTAL_CONTROLS_SETTING_UNKNOWN: ParentalControlsEnableSettingsAction.ParentalControlsSetting
    PARENTAL_CONTROLS_SETTING_SPEED_LIMIT: ParentalControlsEnableSettingsAction.ParentalControlsSetting
    PARENTAL_CONTROLS_SETTING_ACCELERATION: ParentalControlsEnableSettingsAction.ParentalControlsSetting
    PARENTAL_CONTROLS_SETTING_SAFETY_FEATURES: ParentalControlsEnableSettingsAction.ParentalControlsSetting
    PARENTAL_CONTROLS_SETTING_CURFEW: ParentalControlsEnableSettingsAction.ParentalControlsSetting
    SETTING_FIELD_NUMBER: _ClassVar[int]
    ENABLE_FIELD_NUMBER: _ClassVar[int]
    setting: ParentalControlsEnableSettingsAction.ParentalControlsSetting
    enable: bool

    def __init__(self, setting: _Optional[_Union[ParentalControlsEnableSettingsAction.ParentalControlsSetting, str]]=..., enable: bool=...) -> None:
        ...

class ParentalControlsSetSpeedLimitAction(_message.Message):
    __slots__ = ('limit_mph',)
    LIMIT_MPH_FIELD_NUMBER: _ClassVar[int]
    limit_mph: float

    def __init__(self, limit_mph: _Optional[float]=...) -> None:
        ...

class CancelSohTestAction(_message.Message):
    __slots__ = ()

    def __init__(self) -> None:
        ...

class StopLightShowAction(_message.Message):
    __slots__ = ()

    def __init__(self) -> None:
        ...

class StartLightShowAction(_message.Message):
    __slots__ = ('show_index', 'start_time', 'volume', 'dance_moves')
    SHOW_INDEX_FIELD_NUMBER: _ClassVar[int]
    START_TIME_FIELD_NUMBER: _ClassVar[int]
    VOLUME_FIELD_NUMBER: _ClassVar[int]
    DANCE_MOVES_FIELD_NUMBER: _ClassVar[int]
    show_index: int
    start_time: int
    volume: float
    dance_moves: bool

    def __init__(self, show_index: _Optional[int]=..., start_time: _Optional[int]=..., volume: _Optional[float]=..., dance_moves: bool=...) -> None:
        ...

class SetSuspensionLevelAction(_message.Message):
    __slots__ = ('suspension_level',)

    class SuspensionLevel(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        SUSPENSION_LEVEL_INVALID: _ClassVar[SetSuspensionLevelAction.SuspensionLevel]
        SUSPENSION_LEVEL_ENTRY: _ClassVar[SetSuspensionLevelAction.SuspensionLevel]
        SUSPENSION_LEVEL_LOW: _ClassVar[SetSuspensionLevelAction.SuspensionLevel]
        SUSPENSION_LEVEL_MEDIUM: _ClassVar[SetSuspensionLevelAction.SuspensionLevel]
        SUSPENSION_LEVEL_HIGH: _ClassVar[SetSuspensionLevelAction.SuspensionLevel]
        SUSPENSION_LEVEL_VERY_HIGH: _ClassVar[SetSuspensionLevelAction.SuspensionLevel]
        SUSPENSION_LEVEL_EXTRACT: _ClassVar[SetSuspensionLevelAction.SuspensionLevel]
    SUSPENSION_LEVEL_INVALID: SetSuspensionLevelAction.SuspensionLevel
    SUSPENSION_LEVEL_ENTRY: SetSuspensionLevelAction.SuspensionLevel
    SUSPENSION_LEVEL_LOW: SetSuspensionLevelAction.SuspensionLevel
    SUSPENSION_LEVEL_MEDIUM: SetSuspensionLevelAction.SuspensionLevel
    SUSPENSION_LEVEL_HIGH: SetSuspensionLevelAction.SuspensionLevel
    SUSPENSION_LEVEL_VERY_HIGH: SetSuspensionLevelAction.SuspensionLevel
    SUSPENSION_LEVEL_EXTRACT: SetSuspensionLevelAction.SuspensionLevel
    SUSPENSION_LEVEL_FIELD_NUMBER: _ClassVar[int]
    suspension_level: SetSuspensionLevelAction.SuspensionLevel

    def __init__(self, suspension_level: _Optional[_Union[SetSuspensionLevelAction.SuspensionLevel, str]]=...) -> None:
        ...