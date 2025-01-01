"""Generated protocol buffer code."""
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from . import vehicle_pb2 as vehicle__pb2
from . import signatures_pb2 as signatures__pb2
from . import common_pb2 as common__pb2
from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x10car_server.proto\x12\tCarServer\x1a\rvehicle.proto\x1a\x10signatures.proto\x1a\x0ccommon.proto\x1a\x1fgoogle/protobuf/timestamp.proto"O\n\x06Action\x121\n\rvehicleAction\x18\x02 \x01(\x0b2\x18.CarServer.VehicleActionH\x00B\x0c\n\naction_msgJ\x04\x08\x03\x10\x06"\x97\x1e\n\rVehicleAction\x123\n\x0egetVehicleData\x18\x01 \x01(\x0b2\x19.CarServer.GetVehicleDataH\x00\x12C\n\x16chargingSetLimitAction\x18\x05 \x01(\x0b2!.CarServer.ChargingSetLimitActionH\x00\x12E\n\x17chargingStartStopAction\x18\x06 \x01(\x0b2".CarServer.ChargingStartStopActionH\x00\x12U\n\x1fdrivingClearSpeedLimitPinAction\x18\x07 \x01(\x0b2*.CarServer.DrivingClearSpeedLimitPinActionH\x00\x12K\n\x1adrivingSetSpeedLimitAction\x18\x08 \x01(\x0b2%.CarServer.DrivingSetSpeedLimitActionH\x00\x12E\n\x17drivingSpeedLimitAction\x18\t \x01(\x0b2".CarServer.DrivingSpeedLimitActionH\x00\x123\n\x0ehvacAutoAction\x18\n \x01(\x0b2\x19.CarServer.HvacAutoActionH\x00\x12U\n\x1fhvacSetPreconditioningMaxAction\x18\x0c \x01(\x0b2*.CarServer.HvacSetPreconditioningMaxActionH\x00\x12Q\n\x1dhvacSteeringWheelHeaterAction\x18\r \x01(\x0b2(.CarServer.HvacSteeringWheelHeaterActionH\x00\x12U\n\x1fhvacTemperatureAdjustmentAction\x18\x0e \x01(\x0b2*.CarServer.HvacTemperatureAdjustmentActionH\x00\x125\n\x0fmediaPlayAction\x18\x0f \x01(\x0b2\x1a.CarServer.MediaPlayActionH\x00\x129\n\x11mediaUpdateVolume\x18\x10 \x01(\x0b2\x1c.CarServer.MediaUpdateVolumeH\x00\x129\n\x11mediaNextFavorite\x18\x11 \x01(\x0b2\x1c.CarServer.MediaNextFavoriteH\x00\x12A\n\x15mediaPreviousFavorite\x18\x12 \x01(\x0b2 .CarServer.MediaPreviousFavoriteH\x00\x123\n\x0emediaNextTrack\x18\x13 \x01(\x0b2\x19.CarServer.MediaNextTrackH\x00\x12;\n\x12mediaPreviousTrack\x18\x14 \x01(\x0b2\x1d.CarServer.MediaPreviousTrackH\x00\x12C\n\x16getNearbyChargingSites\x18\x17 \x01(\x0b2!.CarServer.GetNearbyChargingSitesH\x00\x12g\n(vehicleControlCancelSoftwareUpdateAction\x18\x19 \x01(\x0b23.CarServer.VehicleControlCancelSoftwareUpdateActionH\x00\x12U\n\x1fvehicleControlFlashLightsAction\x18\x1a \x01(\x0b2*.CarServer.VehicleControlFlashLightsActionH\x00\x12O\n\x1cvehicleControlHonkHornAction\x18\x1b \x01(\x0b2\'.CarServer.VehicleControlHonkHornActionH\x00\x12Y\n!vehicleControlResetValetPinAction\x18\x1c \x01(\x0b2,.CarServer.VehicleControlResetValetPinActionH\x00\x12k\n*vehicleControlScheduleSoftwareUpdateAction\x18\x1d \x01(\x0b25.CarServer.VehicleControlScheduleSoftwareUpdateActionH\x00\x12Y\n!vehicleControlSetSentryModeAction\x18\x1e \x01(\x0b2,.CarServer.VehicleControlSetSentryModeActionH\x00\x12W\n vehicleControlSetValetModeAction\x18\x1f \x01(\x0b2+.CarServer.VehicleControlSetValetModeActionH\x00\x12_\n$vehicleControlSunroofOpenCloseAction\x18  \x01(\x0b2/.CarServer.VehicleControlSunroofOpenCloseActionH\x00\x12]\n#vehicleControlTriggerHomelinkAction\x18! \x01(\x0b2..CarServer.VehicleControlTriggerHomelinkActionH\x00\x12K\n\x1avehicleControlWindowAction\x18" \x01(\x0b2%.CarServer.VehicleControlWindowActionH\x00\x12E\n\x17hvacBioweaponModeAction\x18# \x01(\x0b2".CarServer.HvacBioweaponModeActionH\x00\x12A\n\x15hvacSeatHeaterActions\x18$ \x01(\x0b2 .CarServer.HvacSeatHeaterActionsH\x00\x12E\n\x17scheduledChargingAction\x18) \x01(\x0b2".CarServer.ScheduledChargingActionH\x00\x12G\n\x18scheduledDepartureAction\x18* \x01(\x0b2#.CarServer.ScheduledDepartureActionH\x00\x12A\n\x15setChargingAmpsAction\x18+ \x01(\x0b2 .CarServer.SetChargingAmpsActionH\x00\x12E\n\x17hvacClimateKeeperAction\x18, \x01(\x0b2".CarServer.HvacClimateKeeperActionH\x00\x12\x1f\n\x04ping\x18. \x01(\x0b2\x0f.CarServer.PingH\x00\x12A\n\x15autoSeatClimateAction\x180 \x01(\x0b2 .CarServer.AutoSeatClimateActionH\x00\x12A\n\x15hvacSeatCoolerActions\x181 \x01(\x0b2 .CarServer.HvacSeatCoolerActionsH\x00\x12W\n setCabinOverheatProtectionAction\x182 \x01(\x0b2+.CarServer.SetCabinOverheatProtectionActionH\x00\x12?\n\x14setVehicleNameAction\x186 \x01(\x0b2\x1f.CarServer.SetVehicleNameActionH\x00\x12=\n\x13chargePortDoorClose\x18= \x01(\x0b2\x1e.CarServer.ChargePortDoorCloseH\x00\x12;\n\x12chargePortDoorOpen\x18> \x01(\x0b2\x1d.CarServer.ChargePortDoorOpenH\x00\x12<\n\x0fguestModeAction\x18A \x01(\x0b2!.CarServer.VehicleState.GuestModeH\x00\x127\n\x10setCopTempAction\x18B \x01(\x0b2\x1b.CarServer.SetCopTempActionH\x00\x12=\n\x13eraseUserDataAction\x18H \x01(\x0b2\x1e.CarServer.EraseUserDataActionH\x00\x12Y\n!vehicleControlSetPinToDriveAction\x18M \x01(\x0b2,.CarServer.VehicleControlSetPinToDriveActionH\x00\x12]\n#vehicleControlResetPinToDriveAction\x18N \x01(\x0b2..CarServer.VehicleControlResetPinToDriveActionH\x00\x12<\n\x17addChargeScheduleAction\x18a \x01(\x0b2\x19.CarServer.ChargeScheduleH\x00\x12K\n\x1aremoveChargeScheduleAction\x18b \x01(\x0b2%.CarServer.RemoveChargeScheduleActionH\x00\x12H\n\x1daddPreconditionScheduleAction\x18c \x01(\x0b2\x1f.CarServer.PreconditionScheduleH\x00\x12W\n removePreconditionScheduleAction\x18d \x01(\x0b2+.CarServer.RemovePreconditionScheduleActionH\x00\x12c\n&batchRemovePreconditionSchedulesAction\x18k \x01(\x0b21.CarServer.BatchRemovePreconditionSchedulesActionH\x00\x12W\n batchRemoveChargeSchedulesAction\x18l \x01(\x0b2+.CarServer.BatchRemoveChargeSchedulesActionH\x00B\x14\n\x12vehicle_action_msgJ\x04\x08\x0b\x10\x0cJ\x04\x08<\x10=J\x04\x08L\x10M"\xfe\x05\n\x0eGetVehicleData\x121\n\x0egetChargeState\x18\x02 \x01(\x0b2\x19.CarServer.GetChargeState\x123\n\x0fgetClimateState\x18\x03 \x01(\x0b2\x1a.CarServer.GetClimateState\x12/\n\rgetDriveState\x18\x04 \x01(\x0b2\x18.CarServer.GetDriveState\x125\n\x10getLocationState\x18\x07 \x01(\x0b2\x1b.CarServer.GetLocationState\x125\n\x10getClosuresState\x18\x08 \x01(\x0b2\x1b.CarServer.GetClosuresState\x12A\n\x16getChargeScheduleState\x18\n \x01(\x0b2!.CarServer.GetChargeScheduleState\x12S\n\x1fgetPreconditioningScheduleState\x18\x0b \x01(\x0b2*.CarServer.GetPreconditioningScheduleState\x12=\n\x14getTirePressureState\x18\x0e \x01(\x0b2\x1f.CarServer.GetTirePressureState\x12/\n\rgetMediaState\x18\x0f \x01(\x0b2\x18.CarServer.GetMediaState\x12;\n\x13getMediaDetailState\x18\x10 \x01(\x0b2\x1e.CarServer.GetMediaDetailState\x12A\n\x16getSoftwareUpdateState\x18\x11 \x01(\x0b2!.CarServer.GetSoftwareUpdateState\x12E\n\x18getParentalControlsState\x18\x13 \x01(\x0b2#.CarServer.GetParentalControlsStateJ\x04\x08\x05\x10\x06J\x04\x08\x06\x10\x07J\x04\x08\x0c\x10\rJ\x04\x08\r\x10\x0e"\x16\n\x14GetTirePressureState"\x0f\n\rGetMediaState"\x15\n\x13GetMediaDetailState"\x18\n\x16GetSoftwareUpdateState"\x10\n\x0eGetChargeState"\x11\n\x0fGetClimateState"\x0f\n\rGetDriveState"\x12\n\x10GetLocationState"\x12\n\x10GetClosuresState"\x18\n\x16GetChargeScheduleState"!\n\x1fGetPreconditioningScheduleState"\x1a\n\x18GetParentalControlsState"%\n\x13EraseUserDataAction\x12\x0e\n\x06reason\x18\x01 \x01(\t"\x96\x02\n\x08Response\x12-\n\x0cactionStatus\x18\x01 \x01(\x0b2\x17.CarServer.ActionStatus\x12-\n\x0bvehicleData\x18\x02 \x01(\x0b2\x16.CarServer.VehicleDataH\x00\x129\n\x16getSessionInfoResponse\x18\x03 \x01(\x0b2\x17.Signatures.SessionInfoH\x00\x12@\n\x16getNearbyChargingSites\x18\x05 \x01(\x0b2\x1e.CarServer.NearbyChargingSitesH\x00\x12\x1f\n\x04ping\x18\t \x01(\x0b2\x0f.CarServer.PingH\x00B\x0e\n\x0cresponse_msg"l\n\x0cActionStatus\x12,\n\x06result\x18\x01 \x01(\x0e2\x1c.CarServer.OperationStatus_E\x12.\n\rresult_reason\x18\x02 \x01(\x0b2\x17.CarServer.ResultReason".\n\x0cResultReason\x12\x14\n\nplain_text\x18\x01 \x01(\tH\x00B\x08\n\x06reason"F\n\rEncryptedData\x12\x14\n\x0cfield_number\x18\x01 \x01(\x05\x12\x12\n\nciphertext\x18\x02 \x01(\x0c\x12\x0b\n\x03tag\x18\x03 \x01(\x0c")\n\x16ChargingSetLimitAction\x12\x0f\n\x07percent\x18\x01 \x01(\x05"\xea\x01\n\x17ChargingStartStopAction\x12"\n\x07unknown\x18\x01 \x01(\x0b2\x0f.CarServer.VoidH\x00\x12 \n\x05start\x18\x02 \x01(\x0b2\x0f.CarServer.VoidH\x00\x12)\n\x0estart_standard\x18\x03 \x01(\x0b2\x0f.CarServer.VoidH\x00\x12*\n\x0fstart_max_range\x18\x04 \x01(\x0b2\x0f.CarServer.VoidH\x00\x12\x1f\n\x04stop\x18\x05 \x01(\x0b2\x0f.CarServer.VoidH\x00B\x11\n\x0fcharging_action".\n\x1fDrivingClearSpeedLimitPinAction\x12\x0b\n\x03pin\x18\x01 \x01(\t"/\n\x1aDrivingSetSpeedLimitAction\x12\x11\n\tlimit_mph\x18\x01 \x01(\x01"8\n\x17DrivingSpeedLimitAction\x12\x10\n\x08activate\x18\x01 \x01(\x08\x12\x0b\n\x03pin\x18\x02 \x01(\t";\n\x0eHvacAutoAction\x12\x10\n\x08power_on\x18\x01 \x01(\x08\x12\x17\n\x0fmanual_override\x18\x02 \x01(\x08"\xfc\x06\n\x15HvacSeatHeaterActions\x12S\n\x14hvacSeatHeaterAction\x18\x01 \x03(\x0b25.CarServer.HvacSeatHeaterActions.HvacSeatHeaterAction\x1a\x8d\x06\n\x14HvacSeatHeaterAction\x12.\n\x13SEAT_HEATER_UNKNOWN\x18\x01 \x01(\x0b2\x0f.CarServer.VoidH\x00\x12*\n\x0fSEAT_HEATER_OFF\x18\x02 \x01(\x0b2\x0f.CarServer.VoidH\x00\x12*\n\x0fSEAT_HEATER_LOW\x18\x03 \x01(\x0b2\x0f.CarServer.VoidH\x00\x12*\n\x0fSEAT_HEATER_MED\x18\x04 \x01(\x0b2\x0f.CarServer.VoidH\x00\x12+\n\x10SEAT_HEATER_HIGH\x18\x05 \x01(\x0b2\x0f.CarServer.VoidH\x00\x12+\n\x10CAR_SEAT_UNKNOWN\x18\x06 \x01(\x0b2\x0f.CarServer.VoidH\x01\x12.\n\x13CAR_SEAT_FRONT_LEFT\x18\x07 \x01(\x0b2\x0f.CarServer.VoidH\x01\x12/\n\x14CAR_SEAT_FRONT_RIGHT\x18\x08 \x01(\x0b2\x0f.CarServer.VoidH\x01\x12-\n\x12CAR_SEAT_REAR_LEFT\x18\t \x01(\x0b2\x0f.CarServer.VoidH\x01\x122\n\x17CAR_SEAT_REAR_LEFT_BACK\x18\n \x01(\x0b2\x0f.CarServer.VoidH\x01\x12/\n\x14CAR_SEAT_REAR_CENTER\x18\x0b \x01(\x0b2\x0f.CarServer.VoidH\x01\x12.\n\x13CAR_SEAT_REAR_RIGHT\x18\x0c \x01(\x0b2\x0f.CarServer.VoidH\x01\x123\n\x18CAR_SEAT_REAR_RIGHT_BACK\x18\r \x01(\x0b2\x0f.CarServer.VoidH\x01\x122\n\x17CAR_SEAT_THIRD_ROW_LEFT\x18\x0e \x01(\x0b2\x0f.CarServer.VoidH\x01\x123\n\x18CAR_SEAT_THIRD_ROW_RIGHT\x18\x0f \x01(\x0b2\x0f.CarServer.VoidH\x01B\x13\n\x11seat_heater_levelB\x0f\n\rseat_position"\xe8\x04\n\x15HvacSeatCoolerActions\x12S\n\x14hvacSeatCoolerAction\x18\x01 \x03(\x0b25.CarServer.HvacSeatCoolerActions.HvacSeatCoolerAction\x1a\xbb\x01\n\x14HvacSeatCoolerAction\x12Q\n\x11seat_cooler_level\x18\x01 \x01(\x0e26.CarServer.HvacSeatCoolerActions.HvacSeatCoolerLevel_E\x12P\n\rseat_position\x18\x02 \x01(\x0e29.CarServer.HvacSeatCoolerActions.HvacSeatCoolerPosition_E"\xad\x01\n\x15HvacSeatCoolerLevel_E\x12\x1f\n\x1bHvacSeatCoolerLevel_Unknown\x10\x00\x12\x1b\n\x17HvacSeatCoolerLevel_Off\x10\x01\x12\x1b\n\x17HvacSeatCoolerLevel_Low\x10\x02\x12\x1b\n\x17HvacSeatCoolerLevel_Med\x10\x03\x12\x1c\n\x18HvacSeatCoolerLevel_High\x10\x04"\x8b\x01\n\x18HvacSeatCoolerPosition_E\x12"\n\x1eHvacSeatCoolerPosition_Unknown\x10\x00\x12$\n HvacSeatCoolerPosition_FrontLeft\x10\x01\x12%\n!HvacSeatCoolerPosition_FrontRight\x10\x02"\xde\x01\n\x1fHvacSetPreconditioningMaxAction\x12\n\n\x02on\x18\x01 \x01(\x08\x12\x17\n\x0fmanual_override\x18\x02 \x01(\x08\x12]\n\x14manual_override_mode\x18\x03 \x03(\x0e2?.CarServer.HvacSetPreconditioningMaxAction.ManualOverrideMode_E"7\n\x14ManualOverrideMode_E\x12\x0b\n\x07DogMode\x10\x00\x12\x07\n\x03Soc\x10\x01\x12\t\n\x05Doors\x10\x02"1\n\x1dHvacSteeringWheelHeaterAction\x12\x10\n\x08power_on\x18\x01 \x01(\x08"\xb3\x05\n\x1fHvacTemperatureAdjustmentAction\x12\x15\n\rdelta_celsius\x18\x01 \x01(\x02\x12\x15\n\rdelta_percent\x18\x02 \x01(\x11\x12\x18\n\x10absolute_celsius\x18\x03 \x01(\x02\x12E\n\x05level\x18\x05 \x01(\x0b26.CarServer.HvacTemperatureAdjustmentAction.Temperature\x12]\n\x15hvac_temperature_zone\x18\x04 \x03(\x0b2>.CarServer.HvacTemperatureAdjustmentAction.HvacTemperatureZone\x12\x1b\n\x13driver_temp_celsius\x18\x06 \x01(\x02\x12\x1e\n\x16passenger_temp_celsius\x18\x07 \x01(\x02\x1a\x88\x01\n\x0bTemperature\x12\'\n\x0cTEMP_UNKNOWN\x18\x01 \x01(\x0b2\x0f.CarServer.VoidH\x00\x12#\n\x08TEMP_MIN\x18\x02 \x01(\x0b2\x0f.CarServer.VoidH\x00\x12#\n\x08TEMP_MAX\x18\x03 \x01(\x0b2\x0f.CarServer.VoidH\x00B\x06\n\x04type\x1a\xd9\x01\n\x13HvacTemperatureZone\x12,\n\x11TEMP_ZONE_UNKNOWN\x18\x01 \x01(\x0b2\x0f.CarServer.VoidH\x00\x12/\n\x14TEMP_ZONE_FRONT_LEFT\x18\x02 \x01(\x0b2\x0f.CarServer.VoidH\x00\x120\n\x15TEMP_ZONE_FRONT_RIGHT\x18\x03 \x01(\x0b2\x0f.CarServer.VoidH\x00\x12)\n\x0eTEMP_ZONE_REAR\x18\x04 \x01(\x0b2\x0f.CarServer.VoidH\x00B\x06\n\x04type"R\n\x16GetNearbyChargingSites\x12\x19\n\x11include_meta_data\x18\x01 \x01(\x08\x12\x0e\n\x06radius\x18\x02 \x01(\x05\x12\r\n\x05count\x18\x03 \x01(\x05"\x9c\x01\n\x13NearbyChargingSites\x12-\n\ttimestamp\x18\x01 \x01(\x0b2\x1a.google.protobuf.Timestamp\x12/\n\rsuperchargers\x18\x03 \x03(\x0b2\x18.CarServer.Superchargers\x12%\n\x1dcongestion_sync_time_utc_secs\x18\x04 \x01(\x03"\xcb\x03\n\rSuperchargers\x12\n\n\x02id\x18\x01 \x01(\x03\x12\x11\n\tamenities\x18\x02 \x01(\t\x12\x18\n\x10available_stalls\x18\x03 \x01(\x05\x12\x14\n\x0cbilling_info\x18\x04 \x01(\t\x12\x14\n\x0cbilling_time\x18\x05 \x01(\t\x12\x0c\n\x04city\x18\x06 \x01(\t\x12\x0f\n\x07country\x18\x07 \x01(\t\x12\x16\n\x0edistance_miles\x18\x08 \x01(\x02\x12\x10\n\x08district\x18\t \x01(\t\x12$\n\x08location\x18\n \x01(\x0b2\x12.CarServer.LatLong\x12\x0c\n\x04name\x18\x0b \x01(\t\x12\x13\n\x0bpostal_code\x18\x0c \x01(\t\x12\x13\n\x0bsite_closed\x18\r \x01(\x08\x12\r\n\x05state\x18\x0e \x01(\t\x12\x16\n\x0estreet_address\x18\x0f \x01(\t\x12\x14\n\x0ctotal_stalls\x18\x10 \x01(\x05\x12\x14\n\x0cwithin_range\x18\x11 \x01(\x08\x12\x14\n\x0cmax_power_kw\x18\x12 \x01(\x05\x12"\n\x1aout_of_order_stalls_number\x18\x13 \x01(\x05\x12!\n\x19out_of_order_stalls_names\x18\x14 \x01(\t"\x11\n\x0fMediaPlayAction"b\n\x11MediaUpdateVolume\x12\x16\n\x0cvolume_delta\x18\x01 \x01(\x11H\x00\x12\x1f\n\x15volume_absolute_float\x18\x03 \x01(\x02H\x00B\x0e\n\x0cmedia_volumeJ\x04\x08\x02\x10\x03"\x13\n\x11MediaNextFavorite"\x17\n\x15MediaPreviousFavorite"\x10\n\x0eMediaNextTrack"\x14\n\x12MediaPreviousTrack"*\n(VehicleControlCancelSoftwareUpdateAction"!\n\x1fVehicleControlFlashLightsAction"\x1e\n\x1cVehicleControlHonkHornAction"#\n!VehicleControlResetValetPinAction"@\n*VehicleControlScheduleSoftwareUpdateAction\x12\x12\n\noffset_sec\x18\x01 \x01(\x05"/\n!VehicleControlSetSentryModeAction\x12\n\n\x02on\x18\x01 \x01(\x08"@\n VehicleControlSetValetModeAction\x12\n\n\x02on\x18\x01 \x01(\x08\x12\x10\n\x08password\x18\x02 \x01(\t"\xd6\x01\n$VehicleControlSunroofOpenCloseAction\x12\x18\n\x0eabsolute_level\x18\x01 \x01(\x05H\x00\x12\x15\n\x0bdelta_level\x18\x02 \x01(\x11H\x00\x12\x1f\n\x04vent\x18\x03 \x01(\x0b2\x0f.CarServer.VoidH\x01\x12 \n\x05close\x18\x04 \x01(\x0b2\x0f.CarServer.VoidH\x01\x12\x1f\n\x04open\x18\x05 \x01(\x0b2\x0f.CarServer.VoidH\x01B\x0f\n\rsunroof_levelB\x08\n\x06action"Z\n#VehicleControlTriggerHomelinkAction\x12$\n\x08location\x18\x01 \x01(\x0b2\x12.CarServer.LatLong\x12\r\n\x05token\x18\x02 \x01(\t"\x93\x01\n\x1aVehicleControlWindowAction\x12"\n\x07unknown\x18\x02 \x01(\x0b2\x0f.CarServer.VoidH\x00\x12\x1f\n\x04vent\x18\x03 \x01(\x0b2\x0f.CarServer.VoidH\x00\x12 \n\x05close\x18\x04 \x01(\x0b2\x0f.CarServer.VoidH\x00B\x08\n\x06actionJ\x04\x08\x01\x10\x02">\n\x17HvacBioweaponModeAction\x12\n\n\x02on\x18\x01 \x01(\x08\x12\x17\n\x0fmanual_override\x18\x02 \x01(\x08"\xaa\x02\n\x15AutoSeatClimateAction\x129\n\x07carseat\x18\x01 \x03(\x0b2(.CarServer.AutoSeatClimateAction.CarSeat\x1aa\n\x07CarSeat\x12\n\n\x02on\x18\x01 \x01(\x08\x12J\n\rseat_position\x18\x02 \x01(\x0e23.CarServer.AutoSeatClimateAction.AutoSeatPosition_E"s\n\x12AutoSeatPosition_E\x12\x1c\n\x18AutoSeatPosition_Unknown\x10\x00\x12\x1e\n\x1aAutoSeatPosition_FrontLeft\x10\x01\x12\x1f\n\x1bAutoSeatPosition_FrontRight\x10\x02"\x87\x01\n\x04Ping\x12\x0f\n\x07ping_id\x18\x01 \x01(\x05\x123\n\x0flocal_timestamp\x18\x02 \x01(\x0b2\x1a.google.protobuf.Timestamp\x129\n\x15last_remote_timestamp\x18\x03 \x01(\x0b2\x1a.google.protobuf.Timestamp"A\n\x17ScheduledChargingAction\x12\x0f\n\x07enabled\x18\x01 \x01(\x08\x12\x15\n\rcharging_time\x18\x02 \x01(\x05"\xe6\x01\n\x18ScheduledDepartureAction\x12\x0f\n\x07enabled\x18\x01 \x01(\x08\x12\x16\n\x0edeparture_time\x18\x02 \x01(\x05\x12>\n\x15preconditioning_times\x18\x03 \x01(\x0b2\x1f.CarServer.PreconditioningTimes\x12@\n\x17off_peak_charging_times\x18\x04 \x01(\x0b2\x1f.CarServer.OffPeakChargingTimes\x12\x1f\n\x17off_peak_hours_end_time\x18\x05 \x01(\x05"\x97\x02\n\x17HvacClimateKeeperAction\x12U\n\x13ClimateKeeperAction\x18\x01 \x01(\x0e28.CarServer.HvacClimateKeeperAction.ClimateKeeperAction_E\x12\x17\n\x0fmanual_override\x18\x02 \x01(\x08"\x8b\x01\n\x15ClimateKeeperAction_E\x12\x1b\n\x17ClimateKeeperAction_Off\x10\x00\x12\x1a\n\x16ClimateKeeperAction_On\x10\x01\x12\x1b\n\x17ClimateKeeperAction_Dog\x10\x02\x12\x1c\n\x18ClimateKeeperAction_Camp\x10\x03".\n\x15SetChargingAmpsAction\x12\x15\n\rcharging_amps\x18\x01 \x01(\x05"(\n\x1aRemoveChargeScheduleAction\x12\n\n\x02id\x18\x01 \x01(\x04"M\n BatchRemoveChargeSchedulesAction\x12\x0c\n\x04home\x18\x01 \x01(\x08\x12\x0c\n\x04work\x18\x02 \x01(\x08\x12\r\n\x05other\x18\x03 \x01(\x08"S\n&BatchRemovePreconditionSchedulesAction\x12\x0c\n\x04home\x18\x01 \x01(\x08\x12\x0c\n\x04work\x18\x02 \x01(\x08\x12\r\n\x05other\x18\x03 \x01(\x08".\n RemovePreconditionScheduleAction\x12\n\n\x02id\x18\x01 \x01(\x04"@\n SetCabinOverheatProtectionAction\x12\n\n\x02on\x18\x01 \x01(\x08\x12\x10\n\x08fan_only\x18\x02 \x01(\x08"+\n\x14SetVehicleNameAction\x12\x13\n\x0bvehicleName\x18\x01 \x01(\t"\x15\n\x13ChargePortDoorClose"\x14\n\x12ChargePortDoorOpen"X\n\x10SetCopTempAction\x12D\n\x11copActivationTemp\x18\x01 \x01(\x0e2).CarServer.ClimateState.CopActivationTemp"A\n!VehicleControlSetPinToDriveAction\x12\n\n\x02on\x18\x01 \x01(\x08\x12\x10\n\x08password\x18\x02 \x01(\t"%\n#VehicleControlResetPinToDriveAction*F\n\x11OperationStatus_E\x12\x16\n\x12OPERATIONSTATUS_OK\x10\x00\x12\x19\n\x15OPERATIONSTATUS_ERROR\x10\x01Bn\n$com.tesla.generated.carserver.serverZFgithub.com/teslamotors/vehicle-command/pkg/protocol/protobuf/carserverb\x06proto3')
_OPERATIONSTATUS_E = DESCRIPTOR.enum_types_by_name['OperationStatus_E']
OperationStatus_E = enum_type_wrapper.EnumTypeWrapper(_OPERATIONSTATUS_E)
OPERATIONSTATUS_OK = 0
OPERATIONSTATUS_ERROR = 1
_ACTION = DESCRIPTOR.message_types_by_name['Action']
_VEHICLEACTION = DESCRIPTOR.message_types_by_name['VehicleAction']
_GETVEHICLEDATA = DESCRIPTOR.message_types_by_name['GetVehicleData']
_GETTIREPRESSURESTATE = DESCRIPTOR.message_types_by_name['GetTirePressureState']
_GETMEDIASTATE = DESCRIPTOR.message_types_by_name['GetMediaState']
_GETMEDIADETAILSTATE = DESCRIPTOR.message_types_by_name['GetMediaDetailState']
_GETSOFTWAREUPDATESTATE = DESCRIPTOR.message_types_by_name['GetSoftwareUpdateState']
_GETCHARGESTATE = DESCRIPTOR.message_types_by_name['GetChargeState']
_GETCLIMATESTATE = DESCRIPTOR.message_types_by_name['GetClimateState']
_GETDRIVESTATE = DESCRIPTOR.message_types_by_name['GetDriveState']
_GETLOCATIONSTATE = DESCRIPTOR.message_types_by_name['GetLocationState']
_GETCLOSURESSTATE = DESCRIPTOR.message_types_by_name['GetClosuresState']
_GETCHARGESCHEDULESTATE = DESCRIPTOR.message_types_by_name['GetChargeScheduleState']
_GETPRECONDITIONINGSCHEDULESTATE = DESCRIPTOR.message_types_by_name['GetPreconditioningScheduleState']
_GETPARENTALCONTROLSSTATE = DESCRIPTOR.message_types_by_name['GetParentalControlsState']
_ERASEUSERDATAACTION = DESCRIPTOR.message_types_by_name['EraseUserDataAction']
_RESPONSE = DESCRIPTOR.message_types_by_name['Response']
_ACTIONSTATUS = DESCRIPTOR.message_types_by_name['ActionStatus']
_RESULTREASON = DESCRIPTOR.message_types_by_name['ResultReason']
_ENCRYPTEDDATA = DESCRIPTOR.message_types_by_name['EncryptedData']
_CHARGINGSETLIMITACTION = DESCRIPTOR.message_types_by_name['ChargingSetLimitAction']
_CHARGINGSTARTSTOPACTION = DESCRIPTOR.message_types_by_name['ChargingStartStopAction']
_DRIVINGCLEARSPEEDLIMITPINACTION = DESCRIPTOR.message_types_by_name['DrivingClearSpeedLimitPinAction']
_DRIVINGSETSPEEDLIMITACTION = DESCRIPTOR.message_types_by_name['DrivingSetSpeedLimitAction']
_DRIVINGSPEEDLIMITACTION = DESCRIPTOR.message_types_by_name['DrivingSpeedLimitAction']
_HVACAUTOACTION = DESCRIPTOR.message_types_by_name['HvacAutoAction']
_HVACSEATHEATERACTIONS = DESCRIPTOR.message_types_by_name['HvacSeatHeaterActions']
_HVACSEATHEATERACTIONS_HVACSEATHEATERACTION = _HVACSEATHEATERACTIONS.nested_types_by_name['HvacSeatHeaterAction']
_HVACSEATCOOLERACTIONS = DESCRIPTOR.message_types_by_name['HvacSeatCoolerActions']
_HVACSEATCOOLERACTIONS_HVACSEATCOOLERACTION = _HVACSEATCOOLERACTIONS.nested_types_by_name['HvacSeatCoolerAction']
_HVACSETPRECONDITIONINGMAXACTION = DESCRIPTOR.message_types_by_name['HvacSetPreconditioningMaxAction']
_HVACSTEERINGWHEELHEATERACTION = DESCRIPTOR.message_types_by_name['HvacSteeringWheelHeaterAction']
_HVACTEMPERATUREADJUSTMENTACTION = DESCRIPTOR.message_types_by_name['HvacTemperatureAdjustmentAction']
_HVACTEMPERATUREADJUSTMENTACTION_TEMPERATURE = _HVACTEMPERATUREADJUSTMENTACTION.nested_types_by_name['Temperature']
_HVACTEMPERATUREADJUSTMENTACTION_HVACTEMPERATUREZONE = _HVACTEMPERATUREADJUSTMENTACTION.nested_types_by_name['HvacTemperatureZone']
_GETNEARBYCHARGINGSITES = DESCRIPTOR.message_types_by_name['GetNearbyChargingSites']
_NEARBYCHARGINGSITES = DESCRIPTOR.message_types_by_name['NearbyChargingSites']
_SUPERCHARGERS = DESCRIPTOR.message_types_by_name['Superchargers']
_MEDIAPLAYACTION = DESCRIPTOR.message_types_by_name['MediaPlayAction']
_MEDIAUPDATEVOLUME = DESCRIPTOR.message_types_by_name['MediaUpdateVolume']
_MEDIANEXTFAVORITE = DESCRIPTOR.message_types_by_name['MediaNextFavorite']
_MEDIAPREVIOUSFAVORITE = DESCRIPTOR.message_types_by_name['MediaPreviousFavorite']
_MEDIANEXTTRACK = DESCRIPTOR.message_types_by_name['MediaNextTrack']
_MEDIAPREVIOUSTRACK = DESCRIPTOR.message_types_by_name['MediaPreviousTrack']
_VEHICLECONTROLCANCELSOFTWAREUPDATEACTION = DESCRIPTOR.message_types_by_name['VehicleControlCancelSoftwareUpdateAction']
_VEHICLECONTROLFLASHLIGHTSACTION = DESCRIPTOR.message_types_by_name['VehicleControlFlashLightsAction']
_VEHICLECONTROLHONKHORNACTION = DESCRIPTOR.message_types_by_name['VehicleControlHonkHornAction']
_VEHICLECONTROLRESETVALETPINACTION = DESCRIPTOR.message_types_by_name['VehicleControlResetValetPinAction']
_VEHICLECONTROLSCHEDULESOFTWAREUPDATEACTION = DESCRIPTOR.message_types_by_name['VehicleControlScheduleSoftwareUpdateAction']
_VEHICLECONTROLSETSENTRYMODEACTION = DESCRIPTOR.message_types_by_name['VehicleControlSetSentryModeAction']
_VEHICLECONTROLSETVALETMODEACTION = DESCRIPTOR.message_types_by_name['VehicleControlSetValetModeAction']
_VEHICLECONTROLSUNROOFOPENCLOSEACTION = DESCRIPTOR.message_types_by_name['VehicleControlSunroofOpenCloseAction']
_VEHICLECONTROLTRIGGERHOMELINKACTION = DESCRIPTOR.message_types_by_name['VehicleControlTriggerHomelinkAction']
_VEHICLECONTROLWINDOWACTION = DESCRIPTOR.message_types_by_name['VehicleControlWindowAction']
_HVACBIOWEAPONMODEACTION = DESCRIPTOR.message_types_by_name['HvacBioweaponModeAction']
_AUTOSEATCLIMATEACTION = DESCRIPTOR.message_types_by_name['AutoSeatClimateAction']
_AUTOSEATCLIMATEACTION_CARSEAT = _AUTOSEATCLIMATEACTION.nested_types_by_name['CarSeat']
_PING = DESCRIPTOR.message_types_by_name['Ping']
_SCHEDULEDCHARGINGACTION = DESCRIPTOR.message_types_by_name['ScheduledChargingAction']
_SCHEDULEDDEPARTUREACTION = DESCRIPTOR.message_types_by_name['ScheduledDepartureAction']
_HVACCLIMATEKEEPERACTION = DESCRIPTOR.message_types_by_name['HvacClimateKeeperAction']
_SETCHARGINGAMPSACTION = DESCRIPTOR.message_types_by_name['SetChargingAmpsAction']
_REMOVECHARGESCHEDULEACTION = DESCRIPTOR.message_types_by_name['RemoveChargeScheduleAction']
_BATCHREMOVECHARGESCHEDULESACTION = DESCRIPTOR.message_types_by_name['BatchRemoveChargeSchedulesAction']
_BATCHREMOVEPRECONDITIONSCHEDULESACTION = DESCRIPTOR.message_types_by_name['BatchRemovePreconditionSchedulesAction']
_REMOVEPRECONDITIONSCHEDULEACTION = DESCRIPTOR.message_types_by_name['RemovePreconditionScheduleAction']
_SETCABINOVERHEATPROTECTIONACTION = DESCRIPTOR.message_types_by_name['SetCabinOverheatProtectionAction']
_SETVEHICLENAMEACTION = DESCRIPTOR.message_types_by_name['SetVehicleNameAction']
_CHARGEPORTDOORCLOSE = DESCRIPTOR.message_types_by_name['ChargePortDoorClose']
_CHARGEPORTDOOROPEN = DESCRIPTOR.message_types_by_name['ChargePortDoorOpen']
_SETCOPTEMPACTION = DESCRIPTOR.message_types_by_name['SetCopTempAction']
_VEHICLECONTROLSETPINTODRIVEACTION = DESCRIPTOR.message_types_by_name['VehicleControlSetPinToDriveAction']
_VEHICLECONTROLRESETPINTODRIVEACTION = DESCRIPTOR.message_types_by_name['VehicleControlResetPinToDriveAction']
_HVACSEATCOOLERACTIONS_HVACSEATCOOLERLEVEL_E = _HVACSEATCOOLERACTIONS.enum_types_by_name['HvacSeatCoolerLevel_E']
_HVACSEATCOOLERACTIONS_HVACSEATCOOLERPOSITION_E = _HVACSEATCOOLERACTIONS.enum_types_by_name['HvacSeatCoolerPosition_E']
_HVACSETPRECONDITIONINGMAXACTION_MANUALOVERRIDEMODE_E = _HVACSETPRECONDITIONINGMAXACTION.enum_types_by_name['ManualOverrideMode_E']
_AUTOSEATCLIMATEACTION_AUTOSEATPOSITION_E = _AUTOSEATCLIMATEACTION.enum_types_by_name['AutoSeatPosition_E']
_HVACCLIMATEKEEPERACTION_CLIMATEKEEPERACTION_E = _HVACCLIMATEKEEPERACTION.enum_types_by_name['ClimateKeeperAction_E']
Action = _reflection.GeneratedProtocolMessageType('Action', (_message.Message,), {'DESCRIPTOR': _ACTION, '__module__': 'car_server_pb2'})
_sym_db.RegisterMessage(Action)
VehicleAction = _reflection.GeneratedProtocolMessageType('VehicleAction', (_message.Message,), {'DESCRIPTOR': _VEHICLEACTION, '__module__': 'car_server_pb2'})
_sym_db.RegisterMessage(VehicleAction)
GetVehicleData = _reflection.GeneratedProtocolMessageType('GetVehicleData', (_message.Message,), {'DESCRIPTOR': _GETVEHICLEDATA, '__module__': 'car_server_pb2'})
_sym_db.RegisterMessage(GetVehicleData)
GetTirePressureState = _reflection.GeneratedProtocolMessageType('GetTirePressureState', (_message.Message,), {'DESCRIPTOR': _GETTIREPRESSURESTATE, '__module__': 'car_server_pb2'})
_sym_db.RegisterMessage(GetTirePressureState)
GetMediaState = _reflection.GeneratedProtocolMessageType('GetMediaState', (_message.Message,), {'DESCRIPTOR': _GETMEDIASTATE, '__module__': 'car_server_pb2'})
_sym_db.RegisterMessage(GetMediaState)
GetMediaDetailState = _reflection.GeneratedProtocolMessageType('GetMediaDetailState', (_message.Message,), {'DESCRIPTOR': _GETMEDIADETAILSTATE, '__module__': 'car_server_pb2'})
_sym_db.RegisterMessage(GetMediaDetailState)
GetSoftwareUpdateState = _reflection.GeneratedProtocolMessageType('GetSoftwareUpdateState', (_message.Message,), {'DESCRIPTOR': _GETSOFTWAREUPDATESTATE, '__module__': 'car_server_pb2'})
_sym_db.RegisterMessage(GetSoftwareUpdateState)
GetChargeState = _reflection.GeneratedProtocolMessageType('GetChargeState', (_message.Message,), {'DESCRIPTOR': _GETCHARGESTATE, '__module__': 'car_server_pb2'})
_sym_db.RegisterMessage(GetChargeState)
GetClimateState = _reflection.GeneratedProtocolMessageType('GetClimateState', (_message.Message,), {'DESCRIPTOR': _GETCLIMATESTATE, '__module__': 'car_server_pb2'})
_sym_db.RegisterMessage(GetClimateState)
GetDriveState = _reflection.GeneratedProtocolMessageType('GetDriveState', (_message.Message,), {'DESCRIPTOR': _GETDRIVESTATE, '__module__': 'car_server_pb2'})
_sym_db.RegisterMessage(GetDriveState)
GetLocationState = _reflection.GeneratedProtocolMessageType('GetLocationState', (_message.Message,), {'DESCRIPTOR': _GETLOCATIONSTATE, '__module__': 'car_server_pb2'})
_sym_db.RegisterMessage(GetLocationState)
GetClosuresState = _reflection.GeneratedProtocolMessageType('GetClosuresState', (_message.Message,), {'DESCRIPTOR': _GETCLOSURESSTATE, '__module__': 'car_server_pb2'})
_sym_db.RegisterMessage(GetClosuresState)
GetChargeScheduleState = _reflection.GeneratedProtocolMessageType('GetChargeScheduleState', (_message.Message,), {'DESCRIPTOR': _GETCHARGESCHEDULESTATE, '__module__': 'car_server_pb2'})
_sym_db.RegisterMessage(GetChargeScheduleState)
GetPreconditioningScheduleState = _reflection.GeneratedProtocolMessageType('GetPreconditioningScheduleState', (_message.Message,), {'DESCRIPTOR': _GETPRECONDITIONINGSCHEDULESTATE, '__module__': 'car_server_pb2'})
_sym_db.RegisterMessage(GetPreconditioningScheduleState)
GetParentalControlsState = _reflection.GeneratedProtocolMessageType('GetParentalControlsState', (_message.Message,), {'DESCRIPTOR': _GETPARENTALCONTROLSSTATE, '__module__': 'car_server_pb2'})
_sym_db.RegisterMessage(GetParentalControlsState)
EraseUserDataAction = _reflection.GeneratedProtocolMessageType('EraseUserDataAction', (_message.Message,), {'DESCRIPTOR': _ERASEUSERDATAACTION, '__module__': 'car_server_pb2'})
_sym_db.RegisterMessage(EraseUserDataAction)
Response = _reflection.GeneratedProtocolMessageType('Response', (_message.Message,), {'DESCRIPTOR': _RESPONSE, '__module__': 'car_server_pb2'})
_sym_db.RegisterMessage(Response)
ActionStatus = _reflection.GeneratedProtocolMessageType('ActionStatus', (_message.Message,), {'DESCRIPTOR': _ACTIONSTATUS, '__module__': 'car_server_pb2'})
_sym_db.RegisterMessage(ActionStatus)
ResultReason = _reflection.GeneratedProtocolMessageType('ResultReason', (_message.Message,), {'DESCRIPTOR': _RESULTREASON, '__module__': 'car_server_pb2'})
_sym_db.RegisterMessage(ResultReason)
EncryptedData = _reflection.GeneratedProtocolMessageType('EncryptedData', (_message.Message,), {'DESCRIPTOR': _ENCRYPTEDDATA, '__module__': 'car_server_pb2'})
_sym_db.RegisterMessage(EncryptedData)
ChargingSetLimitAction = _reflection.GeneratedProtocolMessageType('ChargingSetLimitAction', (_message.Message,), {'DESCRIPTOR': _CHARGINGSETLIMITACTION, '__module__': 'car_server_pb2'})
_sym_db.RegisterMessage(ChargingSetLimitAction)
ChargingStartStopAction = _reflection.GeneratedProtocolMessageType('ChargingStartStopAction', (_message.Message,), {'DESCRIPTOR': _CHARGINGSTARTSTOPACTION, '__module__': 'car_server_pb2'})
_sym_db.RegisterMessage(ChargingStartStopAction)
DrivingClearSpeedLimitPinAction = _reflection.GeneratedProtocolMessageType('DrivingClearSpeedLimitPinAction', (_message.Message,), {'DESCRIPTOR': _DRIVINGCLEARSPEEDLIMITPINACTION, '__module__': 'car_server_pb2'})
_sym_db.RegisterMessage(DrivingClearSpeedLimitPinAction)
DrivingSetSpeedLimitAction = _reflection.GeneratedProtocolMessageType('DrivingSetSpeedLimitAction', (_message.Message,), {'DESCRIPTOR': _DRIVINGSETSPEEDLIMITACTION, '__module__': 'car_server_pb2'})
_sym_db.RegisterMessage(DrivingSetSpeedLimitAction)
DrivingSpeedLimitAction = _reflection.GeneratedProtocolMessageType('DrivingSpeedLimitAction', (_message.Message,), {'DESCRIPTOR': _DRIVINGSPEEDLIMITACTION, '__module__': 'car_server_pb2'})
_sym_db.RegisterMessage(DrivingSpeedLimitAction)
HvacAutoAction = _reflection.GeneratedProtocolMessageType('HvacAutoAction', (_message.Message,), {'DESCRIPTOR': _HVACAUTOACTION, '__module__': 'car_server_pb2'})
_sym_db.RegisterMessage(HvacAutoAction)
HvacSeatHeaterActions = _reflection.GeneratedProtocolMessageType('HvacSeatHeaterActions', (_message.Message,), {'HvacSeatHeaterAction': _reflection.GeneratedProtocolMessageType('HvacSeatHeaterAction', (_message.Message,), {'DESCRIPTOR': _HVACSEATHEATERACTIONS_HVACSEATHEATERACTION, '__module__': 'car_server_pb2'}), 'DESCRIPTOR': _HVACSEATHEATERACTIONS, '__module__': 'car_server_pb2'})
_sym_db.RegisterMessage(HvacSeatHeaterActions)
_sym_db.RegisterMessage(HvacSeatHeaterActions.HvacSeatHeaterAction)
HvacSeatCoolerActions = _reflection.GeneratedProtocolMessageType('HvacSeatCoolerActions', (_message.Message,), {'HvacSeatCoolerAction': _reflection.GeneratedProtocolMessageType('HvacSeatCoolerAction', (_message.Message,), {'DESCRIPTOR': _HVACSEATCOOLERACTIONS_HVACSEATCOOLERACTION, '__module__': 'car_server_pb2'}), 'DESCRIPTOR': _HVACSEATCOOLERACTIONS, '__module__': 'car_server_pb2'})
_sym_db.RegisterMessage(HvacSeatCoolerActions)
_sym_db.RegisterMessage(HvacSeatCoolerActions.HvacSeatCoolerAction)
HvacSetPreconditioningMaxAction = _reflection.GeneratedProtocolMessageType('HvacSetPreconditioningMaxAction', (_message.Message,), {'DESCRIPTOR': _HVACSETPRECONDITIONINGMAXACTION, '__module__': 'car_server_pb2'})
_sym_db.RegisterMessage(HvacSetPreconditioningMaxAction)
HvacSteeringWheelHeaterAction = _reflection.GeneratedProtocolMessageType('HvacSteeringWheelHeaterAction', (_message.Message,), {'DESCRIPTOR': _HVACSTEERINGWHEELHEATERACTION, '__module__': 'car_server_pb2'})
_sym_db.RegisterMessage(HvacSteeringWheelHeaterAction)
HvacTemperatureAdjustmentAction = _reflection.GeneratedProtocolMessageType('HvacTemperatureAdjustmentAction', (_message.Message,), {'Temperature': _reflection.GeneratedProtocolMessageType('Temperature', (_message.Message,), {'DESCRIPTOR': _HVACTEMPERATUREADJUSTMENTACTION_TEMPERATURE, '__module__': 'car_server_pb2'}), 'HvacTemperatureZone': _reflection.GeneratedProtocolMessageType('HvacTemperatureZone', (_message.Message,), {'DESCRIPTOR': _HVACTEMPERATUREADJUSTMENTACTION_HVACTEMPERATUREZONE, '__module__': 'car_server_pb2'}), 'DESCRIPTOR': _HVACTEMPERATUREADJUSTMENTACTION, '__module__': 'car_server_pb2'})
_sym_db.RegisterMessage(HvacTemperatureAdjustmentAction)
_sym_db.RegisterMessage(HvacTemperatureAdjustmentAction.Temperature)
_sym_db.RegisterMessage(HvacTemperatureAdjustmentAction.HvacTemperatureZone)
GetNearbyChargingSites = _reflection.GeneratedProtocolMessageType('GetNearbyChargingSites', (_message.Message,), {'DESCRIPTOR': _GETNEARBYCHARGINGSITES, '__module__': 'car_server_pb2'})
_sym_db.RegisterMessage(GetNearbyChargingSites)
NearbyChargingSites = _reflection.GeneratedProtocolMessageType('NearbyChargingSites', (_message.Message,), {'DESCRIPTOR': _NEARBYCHARGINGSITES, '__module__': 'car_server_pb2'})
_sym_db.RegisterMessage(NearbyChargingSites)
Superchargers = _reflection.GeneratedProtocolMessageType('Superchargers', (_message.Message,), {'DESCRIPTOR': _SUPERCHARGERS, '__module__': 'car_server_pb2'})
_sym_db.RegisterMessage(Superchargers)
MediaPlayAction = _reflection.GeneratedProtocolMessageType('MediaPlayAction', (_message.Message,), {'DESCRIPTOR': _MEDIAPLAYACTION, '__module__': 'car_server_pb2'})
_sym_db.RegisterMessage(MediaPlayAction)
MediaUpdateVolume = _reflection.GeneratedProtocolMessageType('MediaUpdateVolume', (_message.Message,), {'DESCRIPTOR': _MEDIAUPDATEVOLUME, '__module__': 'car_server_pb2'})
_sym_db.RegisterMessage(MediaUpdateVolume)
MediaNextFavorite = _reflection.GeneratedProtocolMessageType('MediaNextFavorite', (_message.Message,), {'DESCRIPTOR': _MEDIANEXTFAVORITE, '__module__': 'car_server_pb2'})
_sym_db.RegisterMessage(MediaNextFavorite)
MediaPreviousFavorite = _reflection.GeneratedProtocolMessageType('MediaPreviousFavorite', (_message.Message,), {'DESCRIPTOR': _MEDIAPREVIOUSFAVORITE, '__module__': 'car_server_pb2'})
_sym_db.RegisterMessage(MediaPreviousFavorite)
MediaNextTrack = _reflection.GeneratedProtocolMessageType('MediaNextTrack', (_message.Message,), {'DESCRIPTOR': _MEDIANEXTTRACK, '__module__': 'car_server_pb2'})
_sym_db.RegisterMessage(MediaNextTrack)
MediaPreviousTrack = _reflection.GeneratedProtocolMessageType('MediaPreviousTrack', (_message.Message,), {'DESCRIPTOR': _MEDIAPREVIOUSTRACK, '__module__': 'car_server_pb2'})
_sym_db.RegisterMessage(MediaPreviousTrack)
VehicleControlCancelSoftwareUpdateAction = _reflection.GeneratedProtocolMessageType('VehicleControlCancelSoftwareUpdateAction', (_message.Message,), {'DESCRIPTOR': _VEHICLECONTROLCANCELSOFTWAREUPDATEACTION, '__module__': 'car_server_pb2'})
_sym_db.RegisterMessage(VehicleControlCancelSoftwareUpdateAction)
VehicleControlFlashLightsAction = _reflection.GeneratedProtocolMessageType('VehicleControlFlashLightsAction', (_message.Message,), {'DESCRIPTOR': _VEHICLECONTROLFLASHLIGHTSACTION, '__module__': 'car_server_pb2'})
_sym_db.RegisterMessage(VehicleControlFlashLightsAction)
VehicleControlHonkHornAction = _reflection.GeneratedProtocolMessageType('VehicleControlHonkHornAction', (_message.Message,), {'DESCRIPTOR': _VEHICLECONTROLHONKHORNACTION, '__module__': 'car_server_pb2'})
_sym_db.RegisterMessage(VehicleControlHonkHornAction)
VehicleControlResetValetPinAction = _reflection.GeneratedProtocolMessageType('VehicleControlResetValetPinAction', (_message.Message,), {'DESCRIPTOR': _VEHICLECONTROLRESETVALETPINACTION, '__module__': 'car_server_pb2'})
_sym_db.RegisterMessage(VehicleControlResetValetPinAction)
VehicleControlScheduleSoftwareUpdateAction = _reflection.GeneratedProtocolMessageType('VehicleControlScheduleSoftwareUpdateAction', (_message.Message,), {'DESCRIPTOR': _VEHICLECONTROLSCHEDULESOFTWAREUPDATEACTION, '__module__': 'car_server_pb2'})
_sym_db.RegisterMessage(VehicleControlScheduleSoftwareUpdateAction)
VehicleControlSetSentryModeAction = _reflection.GeneratedProtocolMessageType('VehicleControlSetSentryModeAction', (_message.Message,), {'DESCRIPTOR': _VEHICLECONTROLSETSENTRYMODEACTION, '__module__': 'car_server_pb2'})
_sym_db.RegisterMessage(VehicleControlSetSentryModeAction)
VehicleControlSetValetModeAction = _reflection.GeneratedProtocolMessageType('VehicleControlSetValetModeAction', (_message.Message,), {'DESCRIPTOR': _VEHICLECONTROLSETVALETMODEACTION, '__module__': 'car_server_pb2'})
_sym_db.RegisterMessage(VehicleControlSetValetModeAction)
VehicleControlSunroofOpenCloseAction = _reflection.GeneratedProtocolMessageType('VehicleControlSunroofOpenCloseAction', (_message.Message,), {'DESCRIPTOR': _VEHICLECONTROLSUNROOFOPENCLOSEACTION, '__module__': 'car_server_pb2'})
_sym_db.RegisterMessage(VehicleControlSunroofOpenCloseAction)
VehicleControlTriggerHomelinkAction = _reflection.GeneratedProtocolMessageType('VehicleControlTriggerHomelinkAction', (_message.Message,), {'DESCRIPTOR': _VEHICLECONTROLTRIGGERHOMELINKACTION, '__module__': 'car_server_pb2'})
_sym_db.RegisterMessage(VehicleControlTriggerHomelinkAction)
VehicleControlWindowAction = _reflection.GeneratedProtocolMessageType('VehicleControlWindowAction', (_message.Message,), {'DESCRIPTOR': _VEHICLECONTROLWINDOWACTION, '__module__': 'car_server_pb2'})
_sym_db.RegisterMessage(VehicleControlWindowAction)
HvacBioweaponModeAction = _reflection.GeneratedProtocolMessageType('HvacBioweaponModeAction', (_message.Message,), {'DESCRIPTOR': _HVACBIOWEAPONMODEACTION, '__module__': 'car_server_pb2'})
_sym_db.RegisterMessage(HvacBioweaponModeAction)
AutoSeatClimateAction = _reflection.GeneratedProtocolMessageType('AutoSeatClimateAction', (_message.Message,), {'CarSeat': _reflection.GeneratedProtocolMessageType('CarSeat', (_message.Message,), {'DESCRIPTOR': _AUTOSEATCLIMATEACTION_CARSEAT, '__module__': 'car_server_pb2'}), 'DESCRIPTOR': _AUTOSEATCLIMATEACTION, '__module__': 'car_server_pb2'})
_sym_db.RegisterMessage(AutoSeatClimateAction)
_sym_db.RegisterMessage(AutoSeatClimateAction.CarSeat)
Ping = _reflection.GeneratedProtocolMessageType('Ping', (_message.Message,), {'DESCRIPTOR': _PING, '__module__': 'car_server_pb2'})
_sym_db.RegisterMessage(Ping)
ScheduledChargingAction = _reflection.GeneratedProtocolMessageType('ScheduledChargingAction', (_message.Message,), {'DESCRIPTOR': _SCHEDULEDCHARGINGACTION, '__module__': 'car_server_pb2'})
_sym_db.RegisterMessage(ScheduledChargingAction)
ScheduledDepartureAction = _reflection.GeneratedProtocolMessageType('ScheduledDepartureAction', (_message.Message,), {'DESCRIPTOR': _SCHEDULEDDEPARTUREACTION, '__module__': 'car_server_pb2'})
_sym_db.RegisterMessage(ScheduledDepartureAction)
HvacClimateKeeperAction = _reflection.GeneratedProtocolMessageType('HvacClimateKeeperAction', (_message.Message,), {'DESCRIPTOR': _HVACCLIMATEKEEPERACTION, '__module__': 'car_server_pb2'})
_sym_db.RegisterMessage(HvacClimateKeeperAction)
SetChargingAmpsAction = _reflection.GeneratedProtocolMessageType('SetChargingAmpsAction', (_message.Message,), {'DESCRIPTOR': _SETCHARGINGAMPSACTION, '__module__': 'car_server_pb2'})
_sym_db.RegisterMessage(SetChargingAmpsAction)
RemoveChargeScheduleAction = _reflection.GeneratedProtocolMessageType('RemoveChargeScheduleAction', (_message.Message,), {'DESCRIPTOR': _REMOVECHARGESCHEDULEACTION, '__module__': 'car_server_pb2'})
_sym_db.RegisterMessage(RemoveChargeScheduleAction)
BatchRemoveChargeSchedulesAction = _reflection.GeneratedProtocolMessageType('BatchRemoveChargeSchedulesAction', (_message.Message,), {'DESCRIPTOR': _BATCHREMOVECHARGESCHEDULESACTION, '__module__': 'car_server_pb2'})
_sym_db.RegisterMessage(BatchRemoveChargeSchedulesAction)
BatchRemovePreconditionSchedulesAction = _reflection.GeneratedProtocolMessageType('BatchRemovePreconditionSchedulesAction', (_message.Message,), {'DESCRIPTOR': _BATCHREMOVEPRECONDITIONSCHEDULESACTION, '__module__': 'car_server_pb2'})
_sym_db.RegisterMessage(BatchRemovePreconditionSchedulesAction)
RemovePreconditionScheduleAction = _reflection.GeneratedProtocolMessageType('RemovePreconditionScheduleAction', (_message.Message,), {'DESCRIPTOR': _REMOVEPRECONDITIONSCHEDULEACTION, '__module__': 'car_server_pb2'})
_sym_db.RegisterMessage(RemovePreconditionScheduleAction)
SetCabinOverheatProtectionAction = _reflection.GeneratedProtocolMessageType('SetCabinOverheatProtectionAction', (_message.Message,), {'DESCRIPTOR': _SETCABINOVERHEATPROTECTIONACTION, '__module__': 'car_server_pb2'})
_sym_db.RegisterMessage(SetCabinOverheatProtectionAction)
SetVehicleNameAction = _reflection.GeneratedProtocolMessageType('SetVehicleNameAction', (_message.Message,), {'DESCRIPTOR': _SETVEHICLENAMEACTION, '__module__': 'car_server_pb2'})
_sym_db.RegisterMessage(SetVehicleNameAction)
ChargePortDoorClose = _reflection.GeneratedProtocolMessageType('ChargePortDoorClose', (_message.Message,), {'DESCRIPTOR': _CHARGEPORTDOORCLOSE, '__module__': 'car_server_pb2'})
_sym_db.RegisterMessage(ChargePortDoorClose)
ChargePortDoorOpen = _reflection.GeneratedProtocolMessageType('ChargePortDoorOpen', (_message.Message,), {'DESCRIPTOR': _CHARGEPORTDOOROPEN, '__module__': 'car_server_pb2'})
_sym_db.RegisterMessage(ChargePortDoorOpen)
SetCopTempAction = _reflection.GeneratedProtocolMessageType('SetCopTempAction', (_message.Message,), {'DESCRIPTOR': _SETCOPTEMPACTION, '__module__': 'car_server_pb2'})
_sym_db.RegisterMessage(SetCopTempAction)
VehicleControlSetPinToDriveAction = _reflection.GeneratedProtocolMessageType('VehicleControlSetPinToDriveAction', (_message.Message,), {'DESCRIPTOR': _VEHICLECONTROLSETPINTODRIVEACTION, '__module__': 'car_server_pb2'})
_sym_db.RegisterMessage(VehicleControlSetPinToDriveAction)
VehicleControlResetPinToDriveAction = _reflection.GeneratedProtocolMessageType('VehicleControlResetPinToDriveAction', (_message.Message,), {'DESCRIPTOR': _VEHICLECONTROLRESETPINTODRIVEACTION, '__module__': 'car_server_pb2'})
_sym_db.RegisterMessage(VehicleControlResetPinToDriveAction)
if _descriptor._USE_C_DESCRIPTORS == False:
    DESCRIPTOR._options = None
    DESCRIPTOR._serialized_options = b'\n$com.tesla.generated.carserver.serverZFgithub.com/teslamotors/vehicle-command/pkg/protocol/protobuf/carserver'
    _OPERATIONSTATUS_E._serialized_start = 12067
    _OPERATIONSTATUS_E._serialized_end = 12137
    _ACTION._serialized_start = 111
    _ACTION._serialized_end = 190
    _VEHICLEACTION._serialized_start = 193
    _VEHICLEACTION._serialized_end = 4056
    _GETVEHICLEDATA._serialized_start = 4059
    _GETVEHICLEDATA._serialized_end = 4825
    _GETTIREPRESSURESTATE._serialized_start = 4827
    _GETTIREPRESSURESTATE._serialized_end = 4849
    _GETMEDIASTATE._serialized_start = 4851
    _GETMEDIASTATE._serialized_end = 4866
    _GETMEDIADETAILSTATE._serialized_start = 4868
    _GETMEDIADETAILSTATE._serialized_end = 4889
    _GETSOFTWAREUPDATESTATE._serialized_start = 4891
    _GETSOFTWAREUPDATESTATE._serialized_end = 4915
    _GETCHARGESTATE._serialized_start = 4917
    _GETCHARGESTATE._serialized_end = 4933
    _GETCLIMATESTATE._serialized_start = 4935
    _GETCLIMATESTATE._serialized_end = 4952
    _GETDRIVESTATE._serialized_start = 4954
    _GETDRIVESTATE._serialized_end = 4969
    _GETLOCATIONSTATE._serialized_start = 4971
    _GETLOCATIONSTATE._serialized_end = 4989
    _GETCLOSURESSTATE._serialized_start = 4991
    _GETCLOSURESSTATE._serialized_end = 5009
    _GETCHARGESCHEDULESTATE._serialized_start = 5011
    _GETCHARGESCHEDULESTATE._serialized_end = 5035
    _GETPRECONDITIONINGSCHEDULESTATE._serialized_start = 5037
    _GETPRECONDITIONINGSCHEDULESTATE._serialized_end = 5070
    _GETPARENTALCONTROLSSTATE._serialized_start = 5072
    _GETPARENTALCONTROLSSTATE._serialized_end = 5098
    _ERASEUSERDATAACTION._serialized_start = 5100
    _ERASEUSERDATAACTION._serialized_end = 5137
    _RESPONSE._serialized_start = 5140
    _RESPONSE._serialized_end = 5418
    _ACTIONSTATUS._serialized_start = 5420
    _ACTIONSTATUS._serialized_end = 5528
    _RESULTREASON._serialized_start = 5530
    _RESULTREASON._serialized_end = 5576
    _ENCRYPTEDDATA._serialized_start = 5578
    _ENCRYPTEDDATA._serialized_end = 5648
    _CHARGINGSETLIMITACTION._serialized_start = 5650
    _CHARGINGSETLIMITACTION._serialized_end = 5691
    _CHARGINGSTARTSTOPACTION._serialized_start = 5694
    _CHARGINGSTARTSTOPACTION._serialized_end = 5928
    _DRIVINGCLEARSPEEDLIMITPINACTION._serialized_start = 5930
    _DRIVINGCLEARSPEEDLIMITPINACTION._serialized_end = 5976
    _DRIVINGSETSPEEDLIMITACTION._serialized_start = 5978
    _DRIVINGSETSPEEDLIMITACTION._serialized_end = 6025
    _DRIVINGSPEEDLIMITACTION._serialized_start = 6027
    _DRIVINGSPEEDLIMITACTION._serialized_end = 6083
    _HVACAUTOACTION._serialized_start = 6085
    _HVACAUTOACTION._serialized_end = 6144
    _HVACSEATHEATERACTIONS._serialized_start = 6147
    _HVACSEATHEATERACTIONS._serialized_end = 7039
    _HVACSEATHEATERACTIONS_HVACSEATHEATERACTION._serialized_start = 6258
    _HVACSEATHEATERACTIONS_HVACSEATHEATERACTION._serialized_end = 7039
    _HVACSEATCOOLERACTIONS._serialized_start = 7042
    _HVACSEATCOOLERACTIONS._serialized_end = 7658
    _HVACSEATCOOLERACTIONS_HVACSEATCOOLERACTION._serialized_start = 7153
    _HVACSEATCOOLERACTIONS_HVACSEATCOOLERACTION._serialized_end = 7340
    _HVACSEATCOOLERACTIONS_HVACSEATCOOLERLEVEL_E._serialized_start = 7343
    _HVACSEATCOOLERACTIONS_HVACSEATCOOLERLEVEL_E._serialized_end = 7516
    _HVACSEATCOOLERACTIONS_HVACSEATCOOLERPOSITION_E._serialized_start = 7519
    _HVACSEATCOOLERACTIONS_HVACSEATCOOLERPOSITION_E._serialized_end = 7658
    _HVACSETPRECONDITIONINGMAXACTION._serialized_start = 7661
    _HVACSETPRECONDITIONINGMAXACTION._serialized_end = 7883
    _HVACSETPRECONDITIONINGMAXACTION_MANUALOVERRIDEMODE_E._serialized_start = 7828
    _HVACSETPRECONDITIONINGMAXACTION_MANUALOVERRIDEMODE_E._serialized_end = 7883
    _HVACSTEERINGWHEELHEATERACTION._serialized_start = 7885
    _HVACSTEERINGWHEELHEATERACTION._serialized_end = 7934
    _HVACTEMPERATUREADJUSTMENTACTION._serialized_start = 7937
    _HVACTEMPERATUREADJUSTMENTACTION._serialized_end = 8628
    _HVACTEMPERATUREADJUSTMENTACTION_TEMPERATURE._serialized_start = 8272
    _HVACTEMPERATUREADJUSTMENTACTION_TEMPERATURE._serialized_end = 8408
    _HVACTEMPERATUREADJUSTMENTACTION_HVACTEMPERATUREZONE._serialized_start = 8411
    _HVACTEMPERATUREADJUSTMENTACTION_HVACTEMPERATUREZONE._serialized_end = 8628
    _GETNEARBYCHARGINGSITES._serialized_start = 8630
    _GETNEARBYCHARGINGSITES._serialized_end = 8712
    _NEARBYCHARGINGSITES._serialized_start = 8715
    _NEARBYCHARGINGSITES._serialized_end = 8871
    _SUPERCHARGERS._serialized_start = 8874
    _SUPERCHARGERS._serialized_end = 9333
    _MEDIAPLAYACTION._serialized_start = 9335
    _MEDIAPLAYACTION._serialized_end = 9352
    _MEDIAUPDATEVOLUME._serialized_start = 9354
    _MEDIAUPDATEVOLUME._serialized_end = 9452
    _MEDIANEXTFAVORITE._serialized_start = 9454
    _MEDIANEXTFAVORITE._serialized_end = 9473
    _MEDIAPREVIOUSFAVORITE._serialized_start = 9475
    _MEDIAPREVIOUSFAVORITE._serialized_end = 9498
    _MEDIANEXTTRACK._serialized_start = 9500
    _MEDIANEXTTRACK._serialized_end = 9516
    _MEDIAPREVIOUSTRACK._serialized_start = 9518
    _MEDIAPREVIOUSTRACK._serialized_end = 9538
    _VEHICLECONTROLCANCELSOFTWAREUPDATEACTION._serialized_start = 9540
    _VEHICLECONTROLCANCELSOFTWAREUPDATEACTION._serialized_end = 9582
    _VEHICLECONTROLFLASHLIGHTSACTION._serialized_start = 9584
    _VEHICLECONTROLFLASHLIGHTSACTION._serialized_end = 9617
    _VEHICLECONTROLHONKHORNACTION._serialized_start = 9619
    _VEHICLECONTROLHONKHORNACTION._serialized_end = 9649
    _VEHICLECONTROLRESETVALETPINACTION._serialized_start = 9651
    _VEHICLECONTROLRESETVALETPINACTION._serialized_end = 9686
    _VEHICLECONTROLSCHEDULESOFTWAREUPDATEACTION._serialized_start = 9688
    _VEHICLECONTROLSCHEDULESOFTWAREUPDATEACTION._serialized_end = 9752
    _VEHICLECONTROLSETSENTRYMODEACTION._serialized_start = 9754
    _VEHICLECONTROLSETSENTRYMODEACTION._serialized_end = 9801
    _VEHICLECONTROLSETVALETMODEACTION._serialized_start = 9803
    _VEHICLECONTROLSETVALETMODEACTION._serialized_end = 9867
    _VEHICLECONTROLSUNROOFOPENCLOSEACTION._serialized_start = 9870
    _VEHICLECONTROLSUNROOFOPENCLOSEACTION._serialized_end = 10084
    _VEHICLECONTROLTRIGGERHOMELINKACTION._serialized_start = 10086
    _VEHICLECONTROLTRIGGERHOMELINKACTION._serialized_end = 10176
    _VEHICLECONTROLWINDOWACTION._serialized_start = 10179
    _VEHICLECONTROLWINDOWACTION._serialized_end = 10326
    _HVACBIOWEAPONMODEACTION._serialized_start = 10328
    _HVACBIOWEAPONMODEACTION._serialized_end = 10390
    _AUTOSEATCLIMATEACTION._serialized_start = 10393
    _AUTOSEATCLIMATEACTION._serialized_end = 10691
    _AUTOSEATCLIMATEACTION_CARSEAT._serialized_start = 10477
    _AUTOSEATCLIMATEACTION_CARSEAT._serialized_end = 10574
    _AUTOSEATCLIMATEACTION_AUTOSEATPOSITION_E._serialized_start = 10576
    _AUTOSEATCLIMATEACTION_AUTOSEATPOSITION_E._serialized_end = 10691
    _PING._serialized_start = 10694
    _PING._serialized_end = 10829
    _SCHEDULEDCHARGINGACTION._serialized_start = 10831
    _SCHEDULEDCHARGINGACTION._serialized_end = 10896
    _SCHEDULEDDEPARTUREACTION._serialized_start = 10899
    _SCHEDULEDDEPARTUREACTION._serialized_end = 11129
    _HVACCLIMATEKEEPERACTION._serialized_start = 11132
    _HVACCLIMATEKEEPERACTION._serialized_end = 11411
    _HVACCLIMATEKEEPERACTION_CLIMATEKEEPERACTION_E._serialized_start = 11272
    _HVACCLIMATEKEEPERACTION_CLIMATEKEEPERACTION_E._serialized_end = 11411
    _SETCHARGINGAMPSACTION._serialized_start = 11413
    _SETCHARGINGAMPSACTION._serialized_end = 11459
    _REMOVECHARGESCHEDULEACTION._serialized_start = 11461
    _REMOVECHARGESCHEDULEACTION._serialized_end = 11501
    _BATCHREMOVECHARGESCHEDULESACTION._serialized_start = 11503
    _BATCHREMOVECHARGESCHEDULESACTION._serialized_end = 11580
    _BATCHREMOVEPRECONDITIONSCHEDULESACTION._serialized_start = 11582
    _BATCHREMOVEPRECONDITIONSCHEDULESACTION._serialized_end = 11665
    _REMOVEPRECONDITIONSCHEDULEACTION._serialized_start = 11667
    _REMOVEPRECONDITIONSCHEDULEACTION._serialized_end = 11713
    _SETCABINOVERHEATPROTECTIONACTION._serialized_start = 11715
    _SETCABINOVERHEATPROTECTIONACTION._serialized_end = 11779
    _SETVEHICLENAMEACTION._serialized_start = 11781
    _SETVEHICLENAMEACTION._serialized_end = 11824
    _CHARGEPORTDOORCLOSE._serialized_start = 11826
    _CHARGEPORTDOORCLOSE._serialized_end = 11847
    _CHARGEPORTDOOROPEN._serialized_start = 11849
    _CHARGEPORTDOOROPEN._serialized_end = 11869
    _SETCOPTEMPACTION._serialized_start = 11871
    _SETCOPTEMPACTION._serialized_end = 11959
    _VEHICLECONTROLSETPINTODRIVEACTION._serialized_start = 11961
    _VEHICLECONTROLSETPINTODRIVEACTION._serialized_end = 12026
    _VEHICLECONTROLRESETPINTODRIVEACTION._serialized_start = 12028
    _VEHICLECONTROLRESETPINTODRIVEACTION._serialized_end = 12065