"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\nkeys.proto\x12\x04Keys*\x8a\x01\n\x04Role\x12\r\n\tROLE_NONE\x10\x00\x12\x10\n\x0cROLE_SERVICE\x10\x01\x12\x0e\n\nROLE_OWNER\x10\x02\x12\x0f\n\x0bROLE_DRIVER\x10\x03\x12\x0b\n\x07ROLE_FM\x10\x04\x12\x18\n\x14ROLE_VEHICLE_MONITOR\x10\x05\x12\x19\n\x15ROLE_CHARGING_MANAGER\x10\x06B]\n\x18com.tesla.generated.keysZAgithub.com/teslamotors/vehicle-command/pkg/protocol/protobuf/keysb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'keys_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'\n\x18com.tesla.generated.keysZAgithub.com/teslamotors/vehicle-command/pkg/protocol/protobuf/keys'
    _globals['_ROLE']._serialized_start = 21
    _globals['_ROLE']._serialized_end = 159