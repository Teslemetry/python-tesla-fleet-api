"""Generated protocol buffer code."""
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0cerrors.proto\x12\x06Errors"<\n\x0cNominalError\x12,\n\x0cgenericError\x18\x01 \x01(\x0e2\x16.Errors.GenericError_E*\x9c\x02\n\x0eGenericError_E\x12\x15\n\x11GENERICERROR_NONE\x10\x00\x12\x18\n\x14GENERICERROR_UNKNOWN\x10\x01\x12\x1e\n\x1aGENERICERROR_CLOSURES_OPEN\x10\x02\x12\x1b\n\x17GENERICERROR_ALREADY_ON\x10\x03\x12*\n&GENERICERROR_DISABLED_FOR_USER_COMMAND\x10\x04\x12$\n GENERICERROR_VEHICLE_NOT_IN_PARK\x10\x05\x12\x1d\n\x19GENERICERROR_UNAUTHORIZED\x10\x06\x12+\n\'GENERICERROR_NOT_ALLOWED_OVER_TRANSPORT\x10\x07Ba\n\x1acom.tesla.generated.errorsZCgithub.com/teslamotors/vehicle-command/pkg/protocol/protobuf/errorsb\x06proto3')
_GENERICERROR_E = DESCRIPTOR.enum_types_by_name['GenericError_E']
GenericError_E = enum_type_wrapper.EnumTypeWrapper(_GENERICERROR_E)
GENERICERROR_NONE = 0
GENERICERROR_UNKNOWN = 1
GENERICERROR_CLOSURES_OPEN = 2
GENERICERROR_ALREADY_ON = 3
GENERICERROR_DISABLED_FOR_USER_COMMAND = 4
GENERICERROR_VEHICLE_NOT_IN_PARK = 5
GENERICERROR_UNAUTHORIZED = 6
GENERICERROR_NOT_ALLOWED_OVER_TRANSPORT = 7
_NOMINALERROR = DESCRIPTOR.message_types_by_name['NominalError']
NominalError = _reflection.GeneratedProtocolMessageType('NominalError', (_message.Message,), {'DESCRIPTOR': _NOMINALERROR, '__module__': 'errors_pb2'})
_sym_db.RegisterMessage(NominalError)
if _descriptor._USE_C_DESCRIPTORS == False:
    DESCRIPTOR._options = None
    DESCRIPTOR._serialized_options = b'\n\x1acom.tesla.generated.errorsZCgithub.com/teslamotors/vehicle-command/pkg/protocol/protobuf/errors'
    _GENERICERROR_E._serialized_start = 87
    _GENERICERROR_E._serialized_end = 371
    _NOMINALERROR._serialized_start = 24
    _NOMINALERROR._serialized_end = 84