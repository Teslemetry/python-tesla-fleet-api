"""Generated protocol buffer code."""
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0ccommon.proto\x12\tCarServer"\x06\n\x04Void".\n\x07LatLong\x12\x10\n\x08latitude\x18\x01 \x01(\x02\x12\x11\n\tlongitude\x18\x02 \x01(\x02"\xae\x01\n\x14ChargePortLatchState\x12\x1e\n\x03SNA\x18\x01 \x01(\x0b2\x0f.CarServer.VoidH\x00\x12%\n\nDisengaged\x18\x02 \x01(\x0b2\x0f.CarServer.VoidH\x00\x12"\n\x07Engaged\x18\x03 \x01(\x0b2\x0f.CarServer.VoidH\x00\x12#\n\x08Blocking\x18\x04 \x01(\x0b2\x0f.CarServer.VoidH\x00B\x06\n\x04type"i\n\x14PreconditioningTimes\x12#\n\x08all_week\x18\x01 \x01(\x0b2\x0f.CarServer.VoidH\x00\x12#\n\x08weekdays\x18\x02 \x01(\x0b2\x0f.CarServer.VoidH\x00B\x07\n\x05times"i\n\x14OffPeakChargingTimes\x12#\n\x08all_week\x18\x01 \x01(\x0b2\x0f.CarServer.VoidH\x00\x12#\n\x08weekdays\x18\x02 \x01(\x0b2\x0f.CarServer.VoidH\x00B\x07\n\x05times"\xda\x01\n\x0eChargeSchedule\x12\n\n\x02id\x18\x01 \x01(\x04\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\x14\n\x0cdays_of_week\x18\x03 \x01(\x05\x12\x15\n\rstart_enabled\x18\x04 \x01(\x08\x12\x12\n\nstart_time\x18\x05 \x01(\x05\x12\x13\n\x0bend_enabled\x18\x06 \x01(\x08\x12\x10\n\x08end_time\x18\x07 \x01(\x05\x12\x10\n\x08one_time\x18\x08 \x01(\x08\x12\x0f\n\x07enabled\x18\t \x01(\x08\x12\x10\n\x08latitude\x18\n \x01(\x02\x12\x11\n\tlongitude\x18\x0b \x01(\x02"\xa9\x01\n\x14PreconditionSchedule\x12\n\n\x02id\x18\x01 \x01(\x04\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\x14\n\x0cdays_of_week\x18\x03 \x01(\x05\x12\x19\n\x11precondition_time\x18\x04 \x01(\x05\x12\x10\n\x08one_time\x18\x05 \x01(\x08\x12\x0f\n\x07enabled\x18\x06 \x01(\x08\x12\x10\n\x08latitude\x18\x07 \x01(\x02\x12\x11\n\tlongitude\x18\x08 \x01(\x02*\x16\n\x07Invalid\x12\x0b\n\x07INVALID\x10\x00*;\n\x13MediaPlaybackStatus\x12\x0b\n\x07Stopped\x10\x00\x12\x0b\n\x07Playing\x10\x01\x12\n\n\x06Paused\x10\x02*k\n\x0cStwHeatLevel\x12\x18\n\x14StwHeatLevel_Unknown\x10\x00\x12\x14\n\x10StwHeatLevel_Off\x10\x01\x12\x14\n\x10StwHeatLevel_Low\x10\x02\x12\x15\n\x11StwHeatLevel_High\x10\x03Bn\n$com.tesla.generated.carserver.commonZFgithub.com/teslamotors/vehicle-command/pkg/protocol/protobuf/carserverb\x06proto3')
_INVALID = DESCRIPTOR.enum_types_by_name['Invalid']
Invalid = enum_type_wrapper.EnumTypeWrapper(_INVALID)
_MEDIAPLAYBACKSTATUS = DESCRIPTOR.enum_types_by_name['MediaPlaybackStatus']
MediaPlaybackStatus = enum_type_wrapper.EnumTypeWrapper(_MEDIAPLAYBACKSTATUS)
_STWHEATLEVEL = DESCRIPTOR.enum_types_by_name['StwHeatLevel']
StwHeatLevel = enum_type_wrapper.EnumTypeWrapper(_STWHEATLEVEL)
INVALID = 0
Stopped = 0
Playing = 1
Paused = 2
StwHeatLevel_Unknown = 0
StwHeatLevel_Off = 1
StwHeatLevel_Low = 2
StwHeatLevel_High = 3
_VOID = DESCRIPTOR.message_types_by_name['Void']
_LATLONG = DESCRIPTOR.message_types_by_name['LatLong']
_CHARGEPORTLATCHSTATE = DESCRIPTOR.message_types_by_name['ChargePortLatchState']
_PRECONDITIONINGTIMES = DESCRIPTOR.message_types_by_name['PreconditioningTimes']
_OFFPEAKCHARGINGTIMES = DESCRIPTOR.message_types_by_name['OffPeakChargingTimes']
_CHARGESCHEDULE = DESCRIPTOR.message_types_by_name['ChargeSchedule']
_PRECONDITIONSCHEDULE = DESCRIPTOR.message_types_by_name['PreconditionSchedule']
Void = _reflection.GeneratedProtocolMessageType('Void', (_message.Message,), {'DESCRIPTOR': _VOID, '__module__': 'common_pb2'})
_sym_db.RegisterMessage(Void)
LatLong = _reflection.GeneratedProtocolMessageType('LatLong', (_message.Message,), {'DESCRIPTOR': _LATLONG, '__module__': 'common_pb2'})
_sym_db.RegisterMessage(LatLong)
ChargePortLatchState = _reflection.GeneratedProtocolMessageType('ChargePortLatchState', (_message.Message,), {'DESCRIPTOR': _CHARGEPORTLATCHSTATE, '__module__': 'common_pb2'})
_sym_db.RegisterMessage(ChargePortLatchState)
PreconditioningTimes = _reflection.GeneratedProtocolMessageType('PreconditioningTimes', (_message.Message,), {'DESCRIPTOR': _PRECONDITIONINGTIMES, '__module__': 'common_pb2'})
_sym_db.RegisterMessage(PreconditioningTimes)
OffPeakChargingTimes = _reflection.GeneratedProtocolMessageType('OffPeakChargingTimes', (_message.Message,), {'DESCRIPTOR': _OFFPEAKCHARGINGTIMES, '__module__': 'common_pb2'})
_sym_db.RegisterMessage(OffPeakChargingTimes)
ChargeSchedule = _reflection.GeneratedProtocolMessageType('ChargeSchedule', (_message.Message,), {'DESCRIPTOR': _CHARGESCHEDULE, '__module__': 'common_pb2'})
_sym_db.RegisterMessage(ChargeSchedule)
PreconditionSchedule = _reflection.GeneratedProtocolMessageType('PreconditionSchedule', (_message.Message,), {'DESCRIPTOR': _PRECONDITIONSCHEDULE, '__module__': 'common_pb2'})
_sym_db.RegisterMessage(PreconditionSchedule)
if _descriptor._USE_C_DESCRIPTORS == False:
    DESCRIPTOR._options = None
    DESCRIPTOR._serialized_options = b'\n$com.tesla.generated.carserver.commonZFgithub.com/teslamotors/vehicle-command/pkg/protocol/protobuf/carserver'
    _INVALID._serialized_start = 867
    _INVALID._serialized_end = 889
    _MEDIAPLAYBACKSTATUS._serialized_start = 891
    _MEDIAPLAYBACKSTATUS._serialized_end = 950
    _STWHEATLEVEL._serialized_start = 952
    _STWHEATLEVEL._serialized_end = 1059
    _VOID._serialized_start = 27
    _VOID._serialized_end = 33
    _LATLONG._serialized_start = 35
    _LATLONG._serialized_end = 81
    _CHARGEPORTLATCHSTATE._serialized_start = 84
    _CHARGEPORTLATCHSTATE._serialized_end = 258
    _PRECONDITIONINGTIMES._serialized_start = 260
    _PRECONDITIONINGTIMES._serialized_end = 365
    _OFFPEAKCHARGINGTIMES._serialized_start = 367
    _OFFPEAKCHARGINGTIMES._serialized_end = 472
    _CHARGESCHEDULE._serialized_start = 475
    _CHARGESCHEDULE._serialized_end = 693
    _PRECONDITIONSCHEDULE._serialized_start = 696
    _PRECONDITIONSCHEDULE._serialized_end = 865