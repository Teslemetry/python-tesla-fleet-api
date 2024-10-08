"""Generated protocol buffer code."""
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\nkeys.proto\x12\x04Keys*\x8a\x01\n\x04Role\x12\r\n\tROLE_NONE\x10\x00\x12\x10\n\x0cROLE_SERVICE\x10\x01\x12\x0e\n\nROLE_OWNER\x10\x02\x12\x0f\n\x0bROLE_DRIVER\x10\x03\x12\x0b\n\x07ROLE_FM\x10\x04\x12\x18\n\x14ROLE_VEHICLE_MONITOR\x10\x05\x12\x19\n\x15ROLE_CHARGING_MANAGER\x10\x06B]\n\x18com.tesla.generated.keysZAgithub.com/teslamotors/vehicle-command/pkg/protocol/protobuf/keysb\x06proto3')
_ROLE = DESCRIPTOR.enum_types_by_name['Role']
Role = enum_type_wrapper.EnumTypeWrapper(_ROLE)
ROLE_NONE = 0
ROLE_SERVICE = 1
ROLE_OWNER = 2
ROLE_DRIVER = 3
ROLE_FM = 4
ROLE_VEHICLE_MONITOR = 5
ROLE_CHARGING_MANAGER = 6
if _descriptor._USE_C_DESCRIPTORS == False:
    DESCRIPTOR._options = None
    DESCRIPTOR._serialized_options = b'\n\x18com.tesla.generated.keysZAgithub.com/teslamotors/vehicle-command/pkg/protocol/protobuf/keys'
    _ROLE._serialized_start = 21
    _ROLE._serialized_end = 159