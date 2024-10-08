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
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x10car_server.proto\x12\tCarServer\x1a\rvehicle.proto\x1a\x10signatures.proto\x1a\x0ccommon.proto\x1a\x1fgoogle/protobuf/timestamp.proto"O\n\x06Action\x121\n\rvehicleAction\x18\x02 \x01(\x0b2\x18.CarServer.VehicleActionH\x00B\x0c\n\naction_msgJ\x04\x08\x03\x10\x06"\xe2\x1d\n\rVehicleAction\x12C\n\x16chargingSetLimitAction\x18\x05 \x01(\x0b2!.CarServer.ChargingSetLimitActionH\x00\x12E\n\x17chargingStartStopAction\x18\x06 \x01(\x0b2".CarServer.ChargingStartStopActionH\x00\x12U\n\x1fdrivingClearSpeedLimitPinAction\x18\x07 \x01(\x0b2*.CarServer.DrivingClearSpeedLimitPinActionH\x00\x12K\n\x1adrivingSetSpeedLimitAction\x18\x08 \x01(\x0b2%.CarServer.DrivingSetSpeedLimitActionH\x00\x12E\n\x17drivingSpeedLimitAction\x18\t \x01(\x0b2".CarServer.DrivingSpeedLimitActionH\x00\x123\n\x0ehvacAutoAction\x18\n \x01(\x0b2\x19.CarServer.HvacAutoActionH\x00\x12U\n\x1fhvacSetPreconditioningMaxAction\x18\x0c \x01(\x0b2*.CarServer.HvacSetPreconditioningMaxActionH\x00\x12Q\n\x1dhvacSteeringWheelHeaterAction\x18\r \x01(\x0b2(.CarServer.HvacSteeringWheelHeaterActionH\x00\x12U\n\x1fhvacTemperatureAdjustmentAction\x18\x0e \x01(\x0b2*.CarServer.HvacTemperatureAdjustmentActionH\x00\x125\n\x0fmediaPlayAction\x18\x0f \x01(\x0b2\x1a.CarServer.MediaPlayActionH\x00\x129\n\x11mediaUpdateVolume\x18\x10 \x01(\x0b2\x1c.CarServer.MediaUpdateVolumeH\x00\x129\n\x11mediaNextFavorite\x18\x11 \x01(\x0b2\x1c.CarServer.MediaNextFavoriteH\x00\x12A\n\x15mediaPreviousFavorite\x18\x12 \x01(\x0b2 .CarServer.MediaPreviousFavoriteH\x00\x123\n\x0emediaNextTrack\x18\x13 \x01(\x0b2\x19.CarServer.MediaNextTrackH\x00\x12;\n\x12mediaPreviousTrack\x18\x14 \x01(\x0b2\x1d.CarServer.MediaPreviousTrackH\x00\x12C\n\x16getNearbyChargingSites\x18\x17 \x01(\x0b2!.CarServer.GetNearbyChargingSitesH\x00\x12g\n(vehicleControlCancelSoftwareUpdateAction\x18\x19 \x01(\x0b23.CarServer.VehicleControlCancelSoftwareUpdateActionH\x00\x12U\n\x1fvehicleControlFlashLightsAction\x18\x1a \x01(\x0b2*.CarServer.VehicleControlFlashLightsActionH\x00\x12O\n\x1cvehicleControlHonkHornAction\x18\x1b \x01(\x0b2\'.CarServer.VehicleControlHonkHornActionH\x00\x12Y\n!vehicleControlResetValetPinAction\x18\x1c \x01(\x0b2,.CarServer.VehicleControlResetValetPinActionH\x00\x12k\n*vehicleControlScheduleSoftwareUpdateAction\x18\x1d \x01(\x0b25.CarServer.VehicleControlScheduleSoftwareUpdateActionH\x00\x12Y\n!vehicleControlSetSentryModeAction\x18\x1e \x01(\x0b2,.CarServer.VehicleControlSetSentryModeActionH\x00\x12W\n vehicleControlSetValetModeAction\x18\x1f \x01(\x0b2+.CarServer.VehicleControlSetValetModeActionH\x00\x12_\n$vehicleControlSunroofOpenCloseAction\x18  \x01(\x0b2/.CarServer.VehicleControlSunroofOpenCloseActionH\x00\x12]\n#vehicleControlTriggerHomelinkAction\x18! \x01(\x0b2..CarServer.VehicleControlTriggerHomelinkActionH\x00\x12K\n\x1avehicleControlWindowAction\x18" \x01(\x0b2%.CarServer.VehicleControlWindowActionH\x00\x12E\n\x17hvacBioweaponModeAction\x18# \x01(\x0b2".CarServer.HvacBioweaponModeActionH\x00\x12A\n\x15hvacSeatHeaterActions\x18$ \x01(\x0b2 .CarServer.HvacSeatHeaterActionsH\x00\x12E\n\x17scheduledChargingAction\x18) \x01(\x0b2".CarServer.ScheduledChargingActionH\x00\x12G\n\x18scheduledDepartureAction\x18* \x01(\x0b2#.CarServer.ScheduledDepartureActionH\x00\x12A\n\x15setChargingAmpsAction\x18+ \x01(\x0b2 .CarServer.SetChargingAmpsActionH\x00\x12E\n\x17hvacClimateKeeperAction\x18, \x01(\x0b2".CarServer.HvacClimateKeeperActionH\x00\x12\x1f\n\x04ping\x18. \x01(\x0b2\x0f.CarServer.PingH\x00\x12A\n\x15autoSeatClimateAction\x180 \x01(\x0b2 .CarServer.AutoSeatClimateActionH\x00\x12A\n\x15hvacSeatCoolerActions\x181 \x01(\x0b2 .CarServer.HvacSeatCoolerActionsH\x00\x12W\n setCabinOverheatProtectionAction\x182 \x01(\x0b2+.CarServer.SetCabinOverheatProtectionActionH\x00\x12?\n\x14setVehicleNameAction\x186 \x01(\x0b2\x1f.CarServer.SetVehicleNameActionH\x00\x12=\n\x13chargePortDoorClose\x18= \x01(\x0b2\x1e.CarServer.ChargePortDoorCloseH\x00\x12;\n\x12chargePortDoorOpen\x18> \x01(\x0b2\x1d.CarServer.ChargePortDoorOpenH\x00\x12<\n\x0fguestModeAction\x18A \x01(\x0b2!.CarServer.VehicleState.GuestModeH\x00\x127\n\x10setCopTempAction\x18B \x01(\x0b2\x1b.CarServer.SetCopTempActionH\x00\x12=\n\x13eraseUserDataAction\x18H \x01(\x0b2\x1e.CarServer.EraseUserDataActionH\x00\x12Y\n!vehicleControlSetPinToDriveAction\x18M \x01(\x0b2,.CarServer.VehicleControlSetPinToDriveActionH\x00\x12]\n#vehicleControlResetPinToDriveAction\x18N \x01(\x0b2..CarServer.VehicleControlResetPinToDriveActionH\x00\x12<\n\x17addChargeScheduleAction\x18a \x01(\x0b2\x19.CarServer.ChargeScheduleH\x00\x12K\n\x1aremoveChargeScheduleAction\x18b \x01(\x0b2%.CarServer.RemoveChargeScheduleActionH\x00\x12H\n\x1daddPreconditionScheduleAction\x18c \x01(\x0b2\x1f.CarServer.PreconditionScheduleH\x00\x12W\n removePreconditionScheduleAction\x18d \x01(\x0b2+.CarServer.RemovePreconditionScheduleActionH\x00\x12c\n&batchRemovePreconditionSchedulesAction\x18k \x01(\x0b21.CarServer.BatchRemovePreconditionSchedulesActionH\x00\x12W\n batchRemoveChargeSchedulesAction\x18l \x01(\x0b2+.CarServer.BatchRemoveChargeSchedulesActionH\x00B\x14\n\x12vehicle_action_msgJ\x04\x08\x0b\x10\x0cJ\x04\x08<\x10=J\x04\x08L\x10M"%\n\x13EraseUserDataAction\x12\x0e\n\x06reason\x18\x01 \x01(\t"\xe7\x01\n\x08Response\x12-\n\x0cactionStatus\x18\x01 \x01(\x0b2\x17.CarServer.ActionStatus\x129\n\x16getSessionInfoResponse\x18\x03 \x01(\x0b2\x17.Signatures.SessionInfoH\x00\x12@\n\x16getNearbyChargingSites\x18\x05 \x01(\x0b2\x1e.CarServer.NearbyChargingSitesH\x00\x12\x1f\n\x04ping\x18\t \x01(\x0b2\x0f.CarServer.PingH\x00B\x0e\n\x0cresponse_msg"l\n\x0cActionStatus\x12,\n\x06result\x18\x01 \x01(\x0e2\x1c.CarServer.OperationStatus_E\x12.\n\rresult_reason\x18\x02 \x01(\x0b2\x17.CarServer.ResultReason".\n\x0cResultReason\x12\x14\n\nplain_text\x18\x01 \x01(\tH\x00B\x08\n\x06reason"F\n\rEncryptedData\x12\x14\n\x0cfield_number\x18\x01 \x01(\x05\x12\x12\n\nciphertext\x18\x02 \x01(\x0c\x12\x0b\n\x03tag\x18\x03 \x01(\x0c")\n\x16ChargingSetLimitAction\x12\x0f\n\x07percent\x18\x01 \x01(\x05"\xea\x01\n\x17ChargingStartStopAction\x12"\n\x07unknown\x18\x01 \x01(\x0b2\x0f.CarServer.VoidH\x00\x12 \n\x05start\x18\x02 \x01(\x0b2\x0f.CarServer.VoidH\x00\x12)\n\x0estart_standard\x18\x03 \x01(\x0b2\x0f.CarServer.VoidH\x00\x12*\n\x0fstart_max_range\x18\x04 \x01(\x0b2\x0f.CarServer.VoidH\x00\x12\x1f\n\x04stop\x18\x05 \x01(\x0b2\x0f.CarServer.VoidH\x00B\x11\n\x0fcharging_action".\n\x1fDrivingClearSpeedLimitPinAction\x12\x0b\n\x03pin\x18\x01 \x01(\t"/\n\x1aDrivingSetSpeedLimitAction\x12\x11\n\tlimit_mph\x18\x01 \x01(\x01"8\n\x17DrivingSpeedLimitAction\x12\x10\n\x08activate\x18\x01 \x01(\x08\x12\x0b\n\x03pin\x18\x02 \x01(\t";\n\x0eHvacAutoAction\x12\x10\n\x08power_on\x18\x01 \x01(\x08\x12\x17\n\x0fmanual_override\x18\x02 \x01(\x08"\xfc\x06\n\x15HvacSeatHeaterActions\x12S\n\x14hvacSeatHeaterAction\x18\x01 \x03(\x0b25.CarServer.HvacSeatHeaterActions.HvacSeatHeaterAction\x1a\x8d\x06\n\x14HvacSeatHeaterAction\x12.\n\x13SEAT_HEATER_UNKNOWN\x18\x01 \x01(\x0b2\x0f.CarServer.VoidH\x00\x12*\n\x0fSEAT_HEATER_OFF\x18\x02 \x01(\x0b2\x0f.CarServer.VoidH\x00\x12*\n\x0fSEAT_HEATER_LOW\x18\x03 \x01(\x0b2\x0f.CarServer.VoidH\x00\x12*\n\x0fSEAT_HEATER_MED\x18\x04 \x01(\x0b2\x0f.CarServer.VoidH\x00\x12+\n\x10SEAT_HEATER_HIGH\x18\x05 \x01(\x0b2\x0f.CarServer.VoidH\x00\x12+\n\x10CAR_SEAT_UNKNOWN\x18\x06 \x01(\x0b2\x0f.CarServer.VoidH\x01\x12.\n\x13CAR_SEAT_FRONT_LEFT\x18\x07 \x01(\x0b2\x0f.CarServer.VoidH\x01\x12/\n\x14CAR_SEAT_FRONT_RIGHT\x18\x08 \x01(\x0b2\x0f.CarServer.VoidH\x01\x12-\n\x12CAR_SEAT_REAR_LEFT\x18\t \x01(\x0b2\x0f.CarServer.VoidH\x01\x122\n\x17CAR_SEAT_REAR_LEFT_BACK\x18\n \x01(\x0b2\x0f.CarServer.VoidH\x01\x12/\n\x14CAR_SEAT_REAR_CENTER\x18\x0b \x01(\x0b2\x0f.CarServer.VoidH\x01\x12.\n\x13CAR_SEAT_REAR_RIGHT\x18\x0c \x01(\x0b2\x0f.CarServer.VoidH\x01\x123\n\x18CAR_SEAT_REAR_RIGHT_BACK\x18\r \x01(\x0b2\x0f.CarServer.VoidH\x01\x122\n\x17CAR_SEAT_THIRD_ROW_LEFT\x18\x0e \x01(\x0b2\x0f.CarServer.VoidH\x01\x123\n\x18CAR_SEAT_THIRD_ROW_RIGHT\x18\x0f \x01(\x0b2\x0f.CarServer.VoidH\x01B\x13\n\x11seat_heater_levelB\x0f\n\rseat_position"\xe8\x04\n\x15HvacSeatCoolerActions\x12S\n\x14hvacSeatCoolerAction\x18\x01 \x03(\x0b25.CarServer.HvacSeatCoolerActions.HvacSeatCoolerAction\x1a\xbb\x01\n\x14HvacSeatCoolerAction\x12Q\n\x11seat_cooler_level\x18\x01 \x01(\x0e26.CarServer.HvacSeatCoolerActions.HvacSeatCoolerLevel_E\x12P\n\rseat_position\x18\x02 \x01(\x0e29.CarServer.HvacSeatCoolerActions.HvacSeatCoolerPosition_E"\xad\x01\n\x15HvacSeatCoolerLevel_E\x12\x1f\n\x1bHvacSeatCoolerLevel_Unknown\x10\x00\x12\x1b\n\x17HvacSeatCoolerLevel_Off\x10\x01\x12\x1b\n\x17HvacSeatCoolerLevel_Low\x10\x02\x12\x1b\n\x17HvacSeatCoolerLevel_Med\x10\x03\x12\x1c\n\x18HvacSeatCoolerLevel_High\x10\x04"\x8b\x01\n\x18HvacSeatCoolerPosition_E\x12"\n\x1eHvacSeatCoolerPosition_Unknown\x10\x00\x12$\n HvacSeatCoolerPosition_FrontLeft\x10\x01\x12%\n!HvacSeatCoolerPosition_FrontRight\x10\x02"\xde\x01\n\x1fHvacSetPreconditioningMaxAction\x12\n\n\x02on\x18\x01 \x01(\x08\x12\x17\n\x0fmanual_override\x18\x02 \x01(\x08\x12]\n\x14manual_override_mode\x18\x03 \x03(\x0e2?.CarServer.HvacSetPreconditioningMaxAction.ManualOverrideMode_E"7\n\x14ManualOverrideMode_E\x12\x0b\n\x07DogMode\x10\x00\x12\x07\n\x03Soc\x10\x01\x12\t\n\x05Doors\x10\x02"1\n\x1dHvacSteeringWheelHeaterAction\x12\x10\n\x08power_on\x18\x01 \x01(\x08"\xb3\x05\n\x1fHvacTemperatureAdjustmentAction\x12\x15\n\rdelta_celsius\x18\x01 \x01(\x02\x12\x15\n\rdelta_percent\x18\x02 \x01(\x11\x12\x18\n\x10absolute_celsius\x18\x03 \x01(\x02\x12E\n\x05level\x18\x05 \x01(\x0b26.CarServer.HvacTemperatureAdjustmentAction.Temperature\x12]\n\x15hvac_temperature_zone\x18\x04 \x03(\x0b2>.CarServer.HvacTemperatureAdjustmentAction.HvacTemperatureZone\x12\x1b\n\x13driver_temp_celsius\x18\x06 \x01(\x02\x12\x1e\n\x16passenger_temp_celsius\x18\x07 \x01(\x02\x1a\x88\x01\n\x0bTemperature\x12\'\n\x0cTEMP_UNKNOWN\x18\x01 \x01(\x0b2\x0f.CarServer.VoidH\x00\x12#\n\x08TEMP_MIN\x18\x02 \x01(\x0b2\x0f.CarServer.VoidH\x00\x12#\n\x08TEMP_MAX\x18\x03 \x01(\x0b2\x0f.CarServer.VoidH\x00B\x06\n\x04type\x1a\xd9\x01\n\x13HvacTemperatureZone\x12,\n\x11TEMP_ZONE_UNKNOWN\x18\x01 \x01(\x0b2\x0f.CarServer.VoidH\x00\x12/\n\x14TEMP_ZONE_FRONT_LEFT\x18\x02 \x01(\x0b2\x0f.CarServer.VoidH\x00\x120\n\x15TEMP_ZONE_FRONT_RIGHT\x18\x03 \x01(\x0b2\x0f.CarServer.VoidH\x00\x12)\n\x0eTEMP_ZONE_REAR\x18\x04 \x01(\x0b2\x0f.CarServer.VoidH\x00B\x06\n\x04type"R\n\x16GetNearbyChargingSites\x12\x19\n\x11include_meta_data\x18\x01 \x01(\x08\x12\x0e\n\x06radius\x18\x02 \x01(\x05\x12\r\n\x05count\x18\x03 \x01(\x05"\x9c\x01\n\x13NearbyChargingSites\x12-\n\ttimestamp\x18\x01 \x01(\x0b2\x1a.google.protobuf.Timestamp\x12/\n\rsuperchargers\x18\x03 \x03(\x0b2\x18.CarServer.Superchargers\x12%\n\x1dcongestion_sync_time_utc_secs\x18\x04 \x01(\x03"\xcb\x03\n\rSuperchargers\x12\n\n\x02id\x18\x01 \x01(\x03\x12\x11\n\tamenities\x18\x02 \x01(\t\x12\x18\n\x10available_stalls\x18\x03 \x01(\x05\x12\x14\n\x0cbilling_info\x18\x04 \x01(\t\x12\x14\n\x0cbilling_time\x18\x05 \x01(\t\x12\x0c\n\x04city\x18\x06 \x01(\t\x12\x0f\n\x07country\x18\x07 \x01(\t\x12\x16\n\x0edistance_miles\x18\x08 \x01(\x02\x12\x10\n\x08district\x18\t \x01(\t\x12$\n\x08location\x18\n \x01(\x0b2\x12.CarServer.LatLong\x12\x0c\n\x04name\x18\x0b \x01(\t\x12\x13\n\x0bpostal_code\x18\x0c \x01(\t\x12\x13\n\x0bsite_closed\x18\r \x01(\x08\x12\r\n\x05state\x18\x0e \x01(\t\x12\x16\n\x0estreet_address\x18\x0f \x01(\t\x12\x14\n\x0ctotal_stalls\x18\x10 \x01(\x05\x12\x14\n\x0cwithin_range\x18\x11 \x01(\x08\x12\x14\n\x0cmax_power_kw\x18\x12 \x01(\x05\x12"\n\x1aout_of_order_stalls_number\x18\x13 \x01(\x05\x12!\n\x19out_of_order_stalls_names\x18\x14 \x01(\t"\x11\n\x0fMediaPlayAction"b\n\x11MediaUpdateVolume\x12\x16\n\x0cvolume_delta\x18\x01 \x01(\x11H\x00\x12\x1f\n\x15volume_absolute_float\x18\x03 \x01(\x02H\x00B\x0e\n\x0cmedia_volumeJ\x04\x08\x02\x10\x03"\x13\n\x11MediaNextFavorite"\x17\n\x15MediaPreviousFavorite"\x10\n\x0eMediaNextTrack"\x14\n\x12MediaPreviousTrack"*\n(VehicleControlCancelSoftwareUpdateAction"!\n\x1fVehicleControlFlashLightsAction"\x1e\n\x1cVehicleControlHonkHornAction"#\n!VehicleControlResetValetPinAction"@\n*VehicleControlScheduleSoftwareUpdateAction\x12\x12\n\noffset_sec\x18\x01 \x01(\x05"/\n!VehicleControlSetSentryModeAction\x12\n\n\x02on\x18\x01 \x01(\x08"@\n VehicleControlSetValetModeAction\x12\n\n\x02on\x18\x01 \x01(\x08\x12\x10\n\x08password\x18\x02 \x01(\t"\xd6\x01\n$VehicleControlSunroofOpenCloseAction\x12\x18\n\x0eabsolute_level\x18\x01 \x01(\x05H\x00\x12\x15\n\x0bdelta_level\x18\x02 \x01(\x11H\x00\x12\x1f\n\x04vent\x18\x03 \x01(\x0b2\x0f.CarServer.VoidH\x01\x12 \n\x05close\x18\x04 \x01(\x0b2\x0f.CarServer.VoidH\x01\x12\x1f\n\x04open\x18\x05 \x01(\x0b2\x0f.CarServer.VoidH\x01B\x0f\n\rsunroof_levelB\x08\n\x06action"Z\n#VehicleControlTriggerHomelinkAction\x12$\n\x08location\x18\x01 \x01(\x0b2\x12.CarServer.LatLong\x12\r\n\x05token\x18\x02 \x01(\t"\x93\x01\n\x1aVehicleControlWindowAction\x12"\n\x07unknown\x18\x02 \x01(\x0b2\x0f.CarServer.VoidH\x00\x12\x1f\n\x04vent\x18\x03 \x01(\x0b2\x0f.CarServer.VoidH\x00\x12 \n\x05close\x18\x04 \x01(\x0b2\x0f.CarServer.VoidH\x00B\x08\n\x06actionJ\x04\x08\x01\x10\x02">\n\x17HvacBioweaponModeAction\x12\n\n\x02on\x18\x01 \x01(\x08\x12\x17\n\x0fmanual_override\x18\x02 \x01(\x08"\xaa\x02\n\x15AutoSeatClimateAction\x129\n\x07carseat\x18\x01 \x03(\x0b2(.CarServer.AutoSeatClimateAction.CarSeat\x1aa\n\x07CarSeat\x12\n\n\x02on\x18\x01 \x01(\x08\x12J\n\rseat_position\x18\x02 \x01(\x0e23.CarServer.AutoSeatClimateAction.AutoSeatPosition_E"s\n\x12AutoSeatPosition_E\x12\x1c\n\x18AutoSeatPosition_Unknown\x10\x00\x12\x1e\n\x1aAutoSeatPosition_FrontLeft\x10\x01\x12\x1f\n\x1bAutoSeatPosition_FrontRight\x10\x02"\x87\x01\n\x04Ping\x12\x0f\n\x07ping_id\x18\x01 \x01(\x05\x123\n\x0flocal_timestamp\x18\x02 \x01(\x0b2\x1a.google.protobuf.Timestamp\x129\n\x15last_remote_timestamp\x18\x03 \x01(\x0b2\x1a.google.protobuf.Timestamp"A\n\x17ScheduledChargingAction\x12\x0f\n\x07enabled\x18\x01 \x01(\x08\x12\x15\n\rcharging_time\x18\x02 \x01(\x05"\xe6\x01\n\x18ScheduledDepartureAction\x12\x0f\n\x07enabled\x18\x01 \x01(\x08\x12\x16\n\x0edeparture_time\x18\x02 \x01(\x05\x12>\n\x15preconditioning_times\x18\x03 \x01(\x0b2\x1f.CarServer.PreconditioningTimes\x12@\n\x17off_peak_charging_times\x18\x04 \x01(\x0b2\x1f.CarServer.OffPeakChargingTimes\x12\x1f\n\x17off_peak_hours_end_time\x18\x05 \x01(\x05"\x97\x02\n\x17HvacClimateKeeperAction\x12U\n\x13ClimateKeeperAction\x18\x01 \x01(\x0e28.CarServer.HvacClimateKeeperAction.ClimateKeeperAction_E\x12\x17\n\x0fmanual_override\x18\x02 \x01(\x08"\x8b\x01\n\x15ClimateKeeperAction_E\x12\x1b\n\x17ClimateKeeperAction_Off\x10\x00\x12\x1a\n\x16ClimateKeeperAction_On\x10\x01\x12\x1b\n\x17ClimateKeeperAction_Dog\x10\x02\x12\x1c\n\x18ClimateKeeperAction_Camp\x10\x03".\n\x15SetChargingAmpsAction\x12\x15\n\rcharging_amps\x18\x01 \x01(\x05"(\n\x1aRemoveChargeScheduleAction\x12\n\n\x02id\x18\x01 \x01(\x04"M\n BatchRemoveChargeSchedulesAction\x12\x0c\n\x04home\x18\x01 \x01(\x08\x12\x0c\n\x04work\x18\x02 \x01(\x08\x12\r\n\x05other\x18\x03 \x01(\x08"S\n&BatchRemovePreconditionSchedulesAction\x12\x0c\n\x04home\x18\x01 \x01(\x08\x12\x0c\n\x04work\x18\x02 \x01(\x08\x12\r\n\x05other\x18\x03 \x01(\x08".\n RemovePreconditionScheduleAction\x12\n\n\x02id\x18\x01 \x01(\x04"@\n SetCabinOverheatProtectionAction\x12\n\n\x02on\x18\x01 \x01(\x08\x12\x10\n\x08fan_only\x18\x02 \x01(\x08"+\n\x14SetVehicleNameAction\x12\x13\n\x0bvehicleName\x18\x01 \x01(\t"\x15\n\x13ChargePortDoorClose"\x14\n\x12ChargePortDoorOpen"X\n\x10SetCopTempAction\x12D\n\x11copActivationTemp\x18\x01 \x01(\x0e2).CarServer.ClimateState.CopActivationTemp"A\n!VehicleControlSetPinToDriveAction\x12\n\n\x02on\x18\x01 \x01(\x08\x12\x10\n\x08password\x18\x02 \x01(\t"%\n#VehicleControlResetPinToDriveAction*F\n\x11OperationStatus_E\x12\x16\n\x12OPERATIONSTATUS_OK\x10\x00\x12\x19\n\x15OPERATIONSTATUS_ERROR\x10\x01Bn\n$com.tesla.generated.carserver.serverZFgithub.com/teslamotors/vehicle-command/pkg/protocol/protobuf/carserverb\x06proto3')
_OPERATIONSTATUS_E = DESCRIPTOR.enum_types_by_name['OperationStatus_E']
OperationStatus_E = enum_type_wrapper.EnumTypeWrapper(_OPERATIONSTATUS_E)
OPERATIONSTATUS_OK = 0
OPERATIONSTATUS_ERROR = 1
_ACTION = DESCRIPTOR.message_types_by_name['Action']
_VEHICLEACTION = DESCRIPTOR.message_types_by_name['VehicleAction']
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
    _OPERATIONSTATUS_E._serialized_start = 10925
    _OPERATIONSTATUS_E._serialized_end = 10995
    _ACTION._serialized_start = 111
    _ACTION._serialized_end = 190
    _VEHICLEACTION._serialized_start = 193
    _VEHICLEACTION._serialized_end = 4003
    _ERASEUSERDATAACTION._serialized_start = 4005
    _ERASEUSERDATAACTION._serialized_end = 4042
    _RESPONSE._serialized_start = 4045
    _RESPONSE._serialized_end = 4276
    _ACTIONSTATUS._serialized_start = 4278
    _ACTIONSTATUS._serialized_end = 4386
    _RESULTREASON._serialized_start = 4388
    _RESULTREASON._serialized_end = 4434
    _ENCRYPTEDDATA._serialized_start = 4436
    _ENCRYPTEDDATA._serialized_end = 4506
    _CHARGINGSETLIMITACTION._serialized_start = 4508
    _CHARGINGSETLIMITACTION._serialized_end = 4549
    _CHARGINGSTARTSTOPACTION._serialized_start = 4552
    _CHARGINGSTARTSTOPACTION._serialized_end = 4786
    _DRIVINGCLEARSPEEDLIMITPINACTION._serialized_start = 4788
    _DRIVINGCLEARSPEEDLIMITPINACTION._serialized_end = 4834
    _DRIVINGSETSPEEDLIMITACTION._serialized_start = 4836
    _DRIVINGSETSPEEDLIMITACTION._serialized_end = 4883
    _DRIVINGSPEEDLIMITACTION._serialized_start = 4885
    _DRIVINGSPEEDLIMITACTION._serialized_end = 4941
    _HVACAUTOACTION._serialized_start = 4943
    _HVACAUTOACTION._serialized_end = 5002
    _HVACSEATHEATERACTIONS._serialized_start = 5005
    _HVACSEATHEATERACTIONS._serialized_end = 5897
    _HVACSEATHEATERACTIONS_HVACSEATHEATERACTION._serialized_start = 5116
    _HVACSEATHEATERACTIONS_HVACSEATHEATERACTION._serialized_end = 5897
    _HVACSEATCOOLERACTIONS._serialized_start = 5900
    _HVACSEATCOOLERACTIONS._serialized_end = 6516
    _HVACSEATCOOLERACTIONS_HVACSEATCOOLERACTION._serialized_start = 6011
    _HVACSEATCOOLERACTIONS_HVACSEATCOOLERACTION._serialized_end = 6198
    _HVACSEATCOOLERACTIONS_HVACSEATCOOLERLEVEL_E._serialized_start = 6201
    _HVACSEATCOOLERACTIONS_HVACSEATCOOLERLEVEL_E._serialized_end = 6374
    _HVACSEATCOOLERACTIONS_HVACSEATCOOLERPOSITION_E._serialized_start = 6377
    _HVACSEATCOOLERACTIONS_HVACSEATCOOLERPOSITION_E._serialized_end = 6516
    _HVACSETPRECONDITIONINGMAXACTION._serialized_start = 6519
    _HVACSETPRECONDITIONINGMAXACTION._serialized_end = 6741
    _HVACSETPRECONDITIONINGMAXACTION_MANUALOVERRIDEMODE_E._serialized_start = 6686
    _HVACSETPRECONDITIONINGMAXACTION_MANUALOVERRIDEMODE_E._serialized_end = 6741
    _HVACSTEERINGWHEELHEATERACTION._serialized_start = 6743
    _HVACSTEERINGWHEELHEATERACTION._serialized_end = 6792
    _HVACTEMPERATUREADJUSTMENTACTION._serialized_start = 6795
    _HVACTEMPERATUREADJUSTMENTACTION._serialized_end = 7486
    _HVACTEMPERATUREADJUSTMENTACTION_TEMPERATURE._serialized_start = 7130
    _HVACTEMPERATUREADJUSTMENTACTION_TEMPERATURE._serialized_end = 7266
    _HVACTEMPERATUREADJUSTMENTACTION_HVACTEMPERATUREZONE._serialized_start = 7269
    _HVACTEMPERATUREADJUSTMENTACTION_HVACTEMPERATUREZONE._serialized_end = 7486
    _GETNEARBYCHARGINGSITES._serialized_start = 7488
    _GETNEARBYCHARGINGSITES._serialized_end = 7570
    _NEARBYCHARGINGSITES._serialized_start = 7573
    _NEARBYCHARGINGSITES._serialized_end = 7729
    _SUPERCHARGERS._serialized_start = 7732
    _SUPERCHARGERS._serialized_end = 8191
    _MEDIAPLAYACTION._serialized_start = 8193
    _MEDIAPLAYACTION._serialized_end = 8210
    _MEDIAUPDATEVOLUME._serialized_start = 8212
    _MEDIAUPDATEVOLUME._serialized_end = 8310
    _MEDIANEXTFAVORITE._serialized_start = 8312
    _MEDIANEXTFAVORITE._serialized_end = 8331
    _MEDIAPREVIOUSFAVORITE._serialized_start = 8333
    _MEDIAPREVIOUSFAVORITE._serialized_end = 8356
    _MEDIANEXTTRACK._serialized_start = 8358
    _MEDIANEXTTRACK._serialized_end = 8374
    _MEDIAPREVIOUSTRACK._serialized_start = 8376
    _MEDIAPREVIOUSTRACK._serialized_end = 8396
    _VEHICLECONTROLCANCELSOFTWAREUPDATEACTION._serialized_start = 8398
    _VEHICLECONTROLCANCELSOFTWAREUPDATEACTION._serialized_end = 8440
    _VEHICLECONTROLFLASHLIGHTSACTION._serialized_start = 8442
    _VEHICLECONTROLFLASHLIGHTSACTION._serialized_end = 8475
    _VEHICLECONTROLHONKHORNACTION._serialized_start = 8477
    _VEHICLECONTROLHONKHORNACTION._serialized_end = 8507
    _VEHICLECONTROLRESETVALETPINACTION._serialized_start = 8509
    _VEHICLECONTROLRESETVALETPINACTION._serialized_end = 8544
    _VEHICLECONTROLSCHEDULESOFTWAREUPDATEACTION._serialized_start = 8546
    _VEHICLECONTROLSCHEDULESOFTWAREUPDATEACTION._serialized_end = 8610
    _VEHICLECONTROLSETSENTRYMODEACTION._serialized_start = 8612
    _VEHICLECONTROLSETSENTRYMODEACTION._serialized_end = 8659
    _VEHICLECONTROLSETVALETMODEACTION._serialized_start = 8661
    _VEHICLECONTROLSETVALETMODEACTION._serialized_end = 8725
    _VEHICLECONTROLSUNROOFOPENCLOSEACTION._serialized_start = 8728
    _VEHICLECONTROLSUNROOFOPENCLOSEACTION._serialized_end = 8942
    _VEHICLECONTROLTRIGGERHOMELINKACTION._serialized_start = 8944
    _VEHICLECONTROLTRIGGERHOMELINKACTION._serialized_end = 9034
    _VEHICLECONTROLWINDOWACTION._serialized_start = 9037
    _VEHICLECONTROLWINDOWACTION._serialized_end = 9184
    _HVACBIOWEAPONMODEACTION._serialized_start = 9186
    _HVACBIOWEAPONMODEACTION._serialized_end = 9248
    _AUTOSEATCLIMATEACTION._serialized_start = 9251
    _AUTOSEATCLIMATEACTION._serialized_end = 9549
    _AUTOSEATCLIMATEACTION_CARSEAT._serialized_start = 9335
    _AUTOSEATCLIMATEACTION_CARSEAT._serialized_end = 9432
    _AUTOSEATCLIMATEACTION_AUTOSEATPOSITION_E._serialized_start = 9434
    _AUTOSEATCLIMATEACTION_AUTOSEATPOSITION_E._serialized_end = 9549
    _PING._serialized_start = 9552
    _PING._serialized_end = 9687
    _SCHEDULEDCHARGINGACTION._serialized_start = 9689
    _SCHEDULEDCHARGINGACTION._serialized_end = 9754
    _SCHEDULEDDEPARTUREACTION._serialized_start = 9757
    _SCHEDULEDDEPARTUREACTION._serialized_end = 9987
    _HVACCLIMATEKEEPERACTION._serialized_start = 9990
    _HVACCLIMATEKEEPERACTION._serialized_end = 10269
    _HVACCLIMATEKEEPERACTION_CLIMATEKEEPERACTION_E._serialized_start = 10130
    _HVACCLIMATEKEEPERACTION_CLIMATEKEEPERACTION_E._serialized_end = 10269
    _SETCHARGINGAMPSACTION._serialized_start = 10271
    _SETCHARGINGAMPSACTION._serialized_end = 10317
    _REMOVECHARGESCHEDULEACTION._serialized_start = 10319
    _REMOVECHARGESCHEDULEACTION._serialized_end = 10359
    _BATCHREMOVECHARGESCHEDULESACTION._serialized_start = 10361
    _BATCHREMOVECHARGESCHEDULESACTION._serialized_end = 10438
    _BATCHREMOVEPRECONDITIONSCHEDULESACTION._serialized_start = 10440
    _BATCHREMOVEPRECONDITIONSCHEDULESACTION._serialized_end = 10523
    _REMOVEPRECONDITIONSCHEDULEACTION._serialized_start = 10525
    _REMOVEPRECONDITIONSCHEDULEACTION._serialized_end = 10571
    _SETCABINOVERHEATPROTECTIONACTION._serialized_start = 10573
    _SETCABINOVERHEATPROTECTIONACTION._serialized_end = 10637
    _SETVEHICLENAMEACTION._serialized_start = 10639
    _SETVEHICLENAMEACTION._serialized_end = 10682
    _CHARGEPORTDOORCLOSE._serialized_start = 10684
    _CHARGEPORTDOORCLOSE._serialized_end = 10705
    _CHARGEPORTDOOROPEN._serialized_start = 10707
    _CHARGEPORTDOOROPEN._serialized_end = 10727
    _SETCOPTEMPACTION._serialized_start = 10729
    _SETCOPTEMPACTION._serialized_end = 10817
    _VEHICLECONTROLSETPINTODRIVEACTION._serialized_start = 10819
    _VEHICLECONTROLSETPINTODRIVEACTION._serialized_end = 10884
    _VEHICLECONTROLRESETPINTODRIVEACTION._serialized_start = 10886
    _VEHICLECONTROLRESETPINTODRIVEACTION._serialized_end = 10923