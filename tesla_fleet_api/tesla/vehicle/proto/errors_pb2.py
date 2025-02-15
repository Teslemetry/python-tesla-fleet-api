"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0cerrors.proto\x12\x06Errors"<\n\x0cNominalError\x12,\n\x0cgenericError\x18\x01 \x01(\x0e2\x16.Errors.GenericError_E*\x9c\x02\n\x0eGenericError_E\x12\x15\n\x11GENERICERROR_NONE\x10\x00\x12\x18\n\x14GENERICERROR_UNKNOWN\x10\x01\x12\x1e\n\x1aGENERICERROR_CLOSURES_OPEN\x10\x02\x12\x1b\n\x17GENERICERROR_ALREADY_ON\x10\x03\x12*\n&GENERICERROR_DISABLED_FOR_USER_COMMAND\x10\x04\x12$\n GENERICERROR_VEHICLE_NOT_IN_PARK\x10\x05\x12\x1d\n\x19GENERICERROR_UNAUTHORIZED\x10\x06\x12+\n\'GENERICERROR_NOT_ALLOWED_OVER_TRANSPORT\x10\x07Ba\n\x1acom.tesla.generated.errorsZCgithub.com/teslamotors/vehicle-command/pkg/protocol/protobuf/errorsb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'errors_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'\n\x1acom.tesla.generated.errorsZCgithub.com/teslamotors/vehicle-command/pkg/protocol/protobuf/errors'
    _globals['_GENERICERROR_E']._serialized_start = 87
    _globals['_GENERICERROR_E']._serialized_end = 371
    _globals['_NOMINALERROR']._serialized_start = 24
    _globals['_NOMINALERROR']._serialized_end = 84