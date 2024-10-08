"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\rvehicle.proto\x12\tCarServer"j\n\x0cVehicleState\x124\n\tguestMode\x18J \x01(\x0b2!.CarServer.VehicleState.GuestMode\x1a$\n\tGuestMode\x12\x17\n\x0fGuestModeActive\x18\x01 \x01(\x08"\x98\x01\n\x0cClimateState"\x87\x01\n\x11CopActivationTemp\x12 \n\x1cCopActivationTempUnspecified\x10\x00\x12\x18\n\x14CopActivationTempLow\x10\x01\x12\x1b\n\x17CopActivationTempMedium\x10\x02\x12\x19\n\x15CopActivationTempHigh\x10\x03Bx\n%com.tesla.generated.carserver.vehicleB\x07VehicleZFgithub.com/teslamotors/vehicle-command/pkg/protocol/protobuf/carserverb\x06proto3')
_VEHICLESTATE = DESCRIPTOR.message_types_by_name['VehicleState']
_VEHICLESTATE_GUESTMODE = _VEHICLESTATE.nested_types_by_name['GuestMode']
_CLIMATESTATE = DESCRIPTOR.message_types_by_name['ClimateState']
_CLIMATESTATE_COPACTIVATIONTEMP = _CLIMATESTATE.enum_types_by_name['CopActivationTemp']
VehicleState = _reflection.GeneratedProtocolMessageType('VehicleState', (_message.Message,), {'GuestMode': _reflection.GeneratedProtocolMessageType('GuestMode', (_message.Message,), {'DESCRIPTOR': _VEHICLESTATE_GUESTMODE, '__module__': 'vehicle_pb2'}), 'DESCRIPTOR': _VEHICLESTATE, '__module__': 'vehicle_pb2'})
_sym_db.RegisterMessage(VehicleState)
_sym_db.RegisterMessage(VehicleState.GuestMode)
ClimateState = _reflection.GeneratedProtocolMessageType('ClimateState', (_message.Message,), {'DESCRIPTOR': _CLIMATESTATE, '__module__': 'vehicle_pb2'})
_sym_db.RegisterMessage(ClimateState)
if _descriptor._USE_C_DESCRIPTORS == False:
    DESCRIPTOR._options = None
    DESCRIPTOR._serialized_options = b'\n%com.tesla.generated.carserver.vehicleB\x07VehicleZFgithub.com/teslamotors/vehicle-command/pkg/protocol/protobuf/carserver'
    _VEHICLESTATE._serialized_start = 28
    _VEHICLESTATE._serialized_end = 134
    _VEHICLESTATE_GUESTMODE._serialized_start = 98
    _VEHICLESTATE_GUESTMODE._serialized_end = 134
    _CLIMATESTATE._serialized_start = 137
    _CLIMATESTATE._serialized_end = 289
    _CLIMATESTATE_COPACTIVATIONTEMP._serialized_start = 154
    _CLIMATESTATE_COPACTIVATIONTEMP._serialized_end = 289