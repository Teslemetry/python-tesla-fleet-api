from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union
DESCRIPTOR: _descriptor.FileDescriptor

class GenericError_E(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    GENERICERROR_NONE: _ClassVar[GenericError_E]
    GENERICERROR_UNKNOWN: _ClassVar[GenericError_E]
    GENERICERROR_CLOSURES_OPEN: _ClassVar[GenericError_E]
    GENERICERROR_ALREADY_ON: _ClassVar[GenericError_E]
    GENERICERROR_DISABLED_FOR_USER_COMMAND: _ClassVar[GenericError_E]
    GENERICERROR_VEHICLE_NOT_IN_PARK: _ClassVar[GenericError_E]
    GENERICERROR_UNAUTHORIZED: _ClassVar[GenericError_E]
    GENERICERROR_NOT_ALLOWED_OVER_TRANSPORT: _ClassVar[GenericError_E]
GENERICERROR_NONE: GenericError_E
GENERICERROR_UNKNOWN: GenericError_E
GENERICERROR_CLOSURES_OPEN: GenericError_E
GENERICERROR_ALREADY_ON: GenericError_E
GENERICERROR_DISABLED_FOR_USER_COMMAND: GenericError_E
GENERICERROR_VEHICLE_NOT_IN_PARK: GenericError_E
GENERICERROR_UNAUTHORIZED: GenericError_E
GENERICERROR_NOT_ALLOWED_OVER_TRANSPORT: GenericError_E

class NominalError(_message.Message):
    __slots__ = ('genericError',)
    GENERICERROR_FIELD_NUMBER: _ClassVar[int]
    genericError: GenericError_E

    def __init__(self, genericError: _Optional[_Union[GenericError_E, str]]=...) -> None:
        ...