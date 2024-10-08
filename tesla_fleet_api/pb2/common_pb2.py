"""Generated protocol buffer code."""
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0ccommon.proto\x12\tCarServer"\x06\n\x04Void".\n\x07LatLong\x12\x10\n\x08latitude\x18\x01 \x01(\x02\x12\x11\n\tlongitude\x18\x02 \x01(\x02"i\n\x14PreconditioningTimes\x12#\n\x08all_week\x18\x01 \x01(\x0b2\x0f.CarServer.VoidH\x00\x12#\n\x08weekdays\x18\x02 \x01(\x0b2\x0f.CarServer.VoidH\x00B\x07\n\x05times"i\n\x14OffPeakChargingTimes\x12#\n\x08all_week\x18\x01 \x01(\x0b2\x0f.CarServer.VoidH\x00\x12#\n\x08weekdays\x18\x02 \x01(\x0b2\x0f.CarServer.VoidH\x00B\x07\n\x05times"\xda\x01\n\x0eChargeSchedule\x12\n\n\x02id\x18\x01 \x01(\x04\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\x14\n\x0cdays_of_week\x18\x03 \x01(\x05\x12\x15\n\rstart_enabled\x18\x04 \x01(\x08\x12\x12\n\nstart_time\x18\x05 \x01(\x05\x12\x13\n\x0bend_enabled\x18\x06 \x01(\x08\x12\x10\n\x08end_time\x18\x07 \x01(\x05\x12\x10\n\x08one_time\x18\x08 \x01(\x08\x12\x0f\n\x07enabled\x18\t \x01(\x08\x12\x10\n\x08latitude\x18\n \x01(\x02\x12\x11\n\tlongitude\x18\x0b \x01(\x02"\xa9\x01\n\x14PreconditionSchedule\x12\n\n\x02id\x18\x01 \x01(\x04\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\x14\n\x0cdays_of_week\x18\x03 \x01(\x05\x12\x19\n\x11precondition_time\x18\x04 \x01(\x05\x12\x10\n\x08one_time\x18\x05 \x01(\x08\x12\x0f\n\x07enabled\x18\x06 \x01(\x08\x12\x10\n\x08latitude\x18\x07 \x01(\x02\x12\x11\n\tlongitude\x18\x08 \x01(\x02*\x16\n\x07Invalid\x12\x0b\n\x07INVALID\x10\x00Bn\n$com.tesla.generated.carserver.commonZFgithub.com/teslamotors/vehicle-command/pkg/protocol/protobuf/carserverb\x06proto3')
_INVALID = DESCRIPTOR.enum_types_by_name['Invalid']
Invalid = enum_type_wrapper.EnumTypeWrapper(_INVALID)
INVALID = 0
_VOID = DESCRIPTOR.message_types_by_name['Void']
_LATLONG = DESCRIPTOR.message_types_by_name['LatLong']
_PRECONDITIONINGTIMES = DESCRIPTOR.message_types_by_name['PreconditioningTimes']
_OFFPEAKCHARGINGTIMES = DESCRIPTOR.message_types_by_name['OffPeakChargingTimes']
_CHARGESCHEDULE = DESCRIPTOR.message_types_by_name['ChargeSchedule']
_PRECONDITIONSCHEDULE = DESCRIPTOR.message_types_by_name['PreconditionSchedule']
Void = _reflection.GeneratedProtocolMessageType('Void', (_message.Message,), {'DESCRIPTOR': _VOID, '__module__': 'common_pb2'})
_sym_db.RegisterMessage(Void)
LatLong = _reflection.GeneratedProtocolMessageType('LatLong', (_message.Message,), {'DESCRIPTOR': _LATLONG, '__module__': 'common_pb2'})
_sym_db.RegisterMessage(LatLong)
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
    _INVALID._serialized_start = 690
    _INVALID._serialized_end = 712
    _VOID._serialized_start = 27
    _VOID._serialized_end = 33
    _LATLONG._serialized_start = 35
    _LATLONG._serialized_end = 81
    _PRECONDITIONINGTIMES._serialized_start = 83
    _PRECONDITIONINGTIMES._serialized_end = 188
    _OFFPEAKCHARGINGTIMES._serialized_start = 190
    _OFFPEAKCHARGINGTIMES._serialized_end = 295
    _CHARGESCHEDULE._serialized_start = 298
    _CHARGESCHEDULE._serialized_end = 516
    _PRECONDITIONSCHEDULE._serialized_start = 519
    _PRECONDITIONSCHEDULE._serialized_end = 688