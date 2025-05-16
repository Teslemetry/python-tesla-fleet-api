from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union
DESCRIPTOR: _descriptor.FileDescriptor

class Invalid(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    INVALID: _ClassVar[Invalid]

class MediaPlaybackStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    Stopped: _ClassVar[MediaPlaybackStatus]
    Playing: _ClassVar[MediaPlaybackStatus]
    Paused: _ClassVar[MediaPlaybackStatus]

class StwHeatLevel(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    StwHeatLevel_Unknown: _ClassVar[StwHeatLevel]
    StwHeatLevel_Off: _ClassVar[StwHeatLevel]
    StwHeatLevel_Low: _ClassVar[StwHeatLevel]
    StwHeatLevel_High: _ClassVar[StwHeatLevel]
INVALID: Invalid
Stopped: MediaPlaybackStatus
Playing: MediaPlaybackStatus
Paused: MediaPlaybackStatus
StwHeatLevel_Unknown: StwHeatLevel
StwHeatLevel_Off: StwHeatLevel
StwHeatLevel_Low: StwHeatLevel
StwHeatLevel_High: StwHeatLevel

class Void(_message.Message):
    __slots__ = ()

    def __init__(self) -> None:
        ...

class LatLong(_message.Message):
    __slots__ = ('latitude', 'longitude')
    LATITUDE_FIELD_NUMBER: _ClassVar[int]
    LONGITUDE_FIELD_NUMBER: _ClassVar[int]
    latitude: float
    longitude: float

    def __init__(self, latitude: _Optional[float]=..., longitude: _Optional[float]=...) -> None:
        ...

class ChargePortLatchState(_message.Message):
    __slots__ = ('SNA', 'Disengaged', 'Engaged', 'Blocking')
    SNA_FIELD_NUMBER: _ClassVar[int]
    DISENGAGED_FIELD_NUMBER: _ClassVar[int]
    ENGAGED_FIELD_NUMBER: _ClassVar[int]
    BLOCKING_FIELD_NUMBER: _ClassVar[int]
    SNA: Void
    Disengaged: Void
    Engaged: Void
    Blocking: Void

    def __init__(self, SNA: _Optional[_Union[Void, _Mapping]]=..., Disengaged: _Optional[_Union[Void, _Mapping]]=..., Engaged: _Optional[_Union[Void, _Mapping]]=..., Blocking: _Optional[_Union[Void, _Mapping]]=...) -> None:
        ...

class PreconditioningTimes(_message.Message):
    __slots__ = ('all_week', 'weekdays')
    ALL_WEEK_FIELD_NUMBER: _ClassVar[int]
    WEEKDAYS_FIELD_NUMBER: _ClassVar[int]
    all_week: Void
    weekdays: Void

    def __init__(self, all_week: _Optional[_Union[Void, _Mapping]]=..., weekdays: _Optional[_Union[Void, _Mapping]]=...) -> None:
        ...

class OffPeakChargingTimes(_message.Message):
    __slots__ = ('all_week', 'weekdays')
    ALL_WEEK_FIELD_NUMBER: _ClassVar[int]
    WEEKDAYS_FIELD_NUMBER: _ClassVar[int]
    all_week: Void
    weekdays: Void

    def __init__(self, all_week: _Optional[_Union[Void, _Mapping]]=..., weekdays: _Optional[_Union[Void, _Mapping]]=...) -> None:
        ...

class ChargeSchedule(_message.Message):
    __slots__ = ('id', 'name', 'days_of_week', 'start_enabled', 'start_time', 'end_enabled', 'end_time', 'one_time', 'enabled', 'latitude', 'longitude')
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DAYS_OF_WEEK_FIELD_NUMBER: _ClassVar[int]
    START_ENABLED_FIELD_NUMBER: _ClassVar[int]
    START_TIME_FIELD_NUMBER: _ClassVar[int]
    END_ENABLED_FIELD_NUMBER: _ClassVar[int]
    END_TIME_FIELD_NUMBER: _ClassVar[int]
    ONE_TIME_FIELD_NUMBER: _ClassVar[int]
    ENABLED_FIELD_NUMBER: _ClassVar[int]
    LATITUDE_FIELD_NUMBER: _ClassVar[int]
    LONGITUDE_FIELD_NUMBER: _ClassVar[int]
    id: int
    name: str
    days_of_week: int
    start_enabled: bool
    start_time: int
    end_enabled: bool
    end_time: int
    one_time: bool
    enabled: bool
    latitude: float
    longitude: float

    def __init__(self, id: _Optional[int]=..., name: _Optional[str]=..., days_of_week: _Optional[int]=..., start_enabled: bool=..., start_time: _Optional[int]=..., end_enabled: bool=..., end_time: _Optional[int]=..., one_time: bool=..., enabled: bool=..., latitude: _Optional[float]=..., longitude: _Optional[float]=...) -> None:
        ...

class PreconditionSchedule(_message.Message):
    __slots__ = ('id', 'name', 'days_of_week', 'precondition_time', 'one_time', 'enabled', 'latitude', 'longitude')
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DAYS_OF_WEEK_FIELD_NUMBER: _ClassVar[int]
    PRECONDITION_TIME_FIELD_NUMBER: _ClassVar[int]
    ONE_TIME_FIELD_NUMBER: _ClassVar[int]
    ENABLED_FIELD_NUMBER: _ClassVar[int]
    LATITUDE_FIELD_NUMBER: _ClassVar[int]
    LONGITUDE_FIELD_NUMBER: _ClassVar[int]
    id: int
    name: str
    days_of_week: int
    precondition_time: int
    one_time: bool
    enabled: bool
    latitude: float
    longitude: float

    def __init__(self, id: _Optional[int]=..., name: _Optional[str]=..., days_of_week: _Optional[int]=..., precondition_time: _Optional[int]=..., one_time: bool=..., enabled: bool=..., latitude: _Optional[float]=..., longitude: _Optional[float]=...) -> None:
        ...