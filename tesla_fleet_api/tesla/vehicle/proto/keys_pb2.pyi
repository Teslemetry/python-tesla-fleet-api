from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from typing import ClassVar as _ClassVar
DESCRIPTOR: _descriptor.FileDescriptor

class Role(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ROLE_NONE: _ClassVar[Role]
    ROLE_SERVICE: _ClassVar[Role]
    ROLE_OWNER: _ClassVar[Role]
    ROLE_DRIVER: _ClassVar[Role]
    ROLE_FM: _ClassVar[Role]
    ROLE_VEHICLE_MONITOR: _ClassVar[Role]
    ROLE_CHARGING_MANAGER: _ClassVar[Role]
ROLE_NONE: Role
ROLE_SERVICE: Role
ROLE_OWNER: Role
ROLE_DRIVER: Role
ROLE_FM: Role
ROLE_VEHICLE_MONITOR: Role
ROLE_CHARGING_MANAGER: Role