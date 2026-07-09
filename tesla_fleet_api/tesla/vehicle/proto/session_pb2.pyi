import datetime

from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SessionStore(_message.Message):
    __slots__ = ("public_key", "epoch", "delta", "lock")
    PUBLIC_KEY_FIELD_NUMBER: _ClassVar[int]
    EPOCH_FIELD_NUMBER: _ClassVar[int]
    DELTA_FIELD_NUMBER: _ClassVar[int]
    LOCK_FIELD_NUMBER: _ClassVar[int]
    public_key: bytes
    epoch: bytes
    delta: int
    lock: _timestamp_pb2.Timestamp
    def __init__(self, public_key: _Optional[bytes] = ..., epoch: _Optional[bytes] = ..., delta: _Optional[int] = ..., lock: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...
