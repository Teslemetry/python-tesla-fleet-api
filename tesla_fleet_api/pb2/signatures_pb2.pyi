from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union
DESCRIPTOR: _descriptor.FileDescriptor

class Tag(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    TAG_SIGNATURE_TYPE: _ClassVar[Tag]
    TAG_DOMAIN: _ClassVar[Tag]
    TAG_PERSONALIZATION: _ClassVar[Tag]
    TAG_EPOCH: _ClassVar[Tag]
    TAG_EXPIRES_AT: _ClassVar[Tag]
    TAG_COUNTER: _ClassVar[Tag]
    TAG_CHALLENGE: _ClassVar[Tag]
    TAG_FLAGS: _ClassVar[Tag]
    TAG_REQUEST_HASH: _ClassVar[Tag]
    TAG_FAULT: _ClassVar[Tag]
    TAG_END: _ClassVar[Tag]

class SignatureType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SIGNATURE_TYPE_AES_GCM: _ClassVar[SignatureType]
    SIGNATURE_TYPE_AES_GCM_PERSONALIZED: _ClassVar[SignatureType]
    SIGNATURE_TYPE_HMAC: _ClassVar[SignatureType]
    SIGNATURE_TYPE_HMAC_PERSONALIZED: _ClassVar[SignatureType]
    SIGNATURE_TYPE_AES_GCM_RESPONSE: _ClassVar[SignatureType]

class Session_Info_Status(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SESSION_INFO_STATUS_OK: _ClassVar[Session_Info_Status]
    SESSION_INFO_STATUS_KEY_NOT_ON_WHITELIST: _ClassVar[Session_Info_Status]
TAG_SIGNATURE_TYPE: Tag
TAG_DOMAIN: Tag
TAG_PERSONALIZATION: Tag
TAG_EPOCH: Tag
TAG_EXPIRES_AT: Tag
TAG_COUNTER: Tag
TAG_CHALLENGE: Tag
TAG_FLAGS: Tag
TAG_REQUEST_HASH: Tag
TAG_FAULT: Tag
TAG_END: Tag
SIGNATURE_TYPE_AES_GCM: SignatureType
SIGNATURE_TYPE_AES_GCM_PERSONALIZED: SignatureType
SIGNATURE_TYPE_HMAC: SignatureType
SIGNATURE_TYPE_HMAC_PERSONALIZED: SignatureType
SIGNATURE_TYPE_AES_GCM_RESPONSE: SignatureType
SESSION_INFO_STATUS_OK: Session_Info_Status
SESSION_INFO_STATUS_KEY_NOT_ON_WHITELIST: Session_Info_Status

class KeyIdentity(_message.Message):
    __slots__ = ('public_key', 'handle')
    PUBLIC_KEY_FIELD_NUMBER: _ClassVar[int]
    HANDLE_FIELD_NUMBER: _ClassVar[int]
    public_key: bytes
    handle: int

    def __init__(self, public_key: _Optional[bytes]=..., handle: _Optional[int]=...) -> None:
        ...

class AES_GCM_Personalized_Signature_Data(_message.Message):
    __slots__ = ('epoch', 'nonce', 'counter', 'expires_at', 'tag')
    EPOCH_FIELD_NUMBER: _ClassVar[int]
    NONCE_FIELD_NUMBER: _ClassVar[int]
    COUNTER_FIELD_NUMBER: _ClassVar[int]
    EXPIRES_AT_FIELD_NUMBER: _ClassVar[int]
    TAG_FIELD_NUMBER: _ClassVar[int]
    epoch: bytes
    nonce: bytes
    counter: int
    expires_at: int
    tag: bytes

    def __init__(self, epoch: _Optional[bytes]=..., nonce: _Optional[bytes]=..., counter: _Optional[int]=..., expires_at: _Optional[int]=..., tag: _Optional[bytes]=...) -> None:
        ...

class AES_GCM_Response_Signature_Data(_message.Message):
    __slots__ = ('nonce', 'counter', 'tag')
    NONCE_FIELD_NUMBER: _ClassVar[int]
    COUNTER_FIELD_NUMBER: _ClassVar[int]
    TAG_FIELD_NUMBER: _ClassVar[int]
    nonce: bytes
    counter: int
    tag: bytes

    def __init__(self, nonce: _Optional[bytes]=..., counter: _Optional[int]=..., tag: _Optional[bytes]=...) -> None:
        ...

class HMAC_Signature_Data(_message.Message):
    __slots__ = ('tag',)
    TAG_FIELD_NUMBER: _ClassVar[int]
    tag: bytes

    def __init__(self, tag: _Optional[bytes]=...) -> None:
        ...

class HMAC_Personalized_Signature_Data(_message.Message):
    __slots__ = ('epoch', 'counter', 'expires_at', 'tag')
    EPOCH_FIELD_NUMBER: _ClassVar[int]
    COUNTER_FIELD_NUMBER: _ClassVar[int]
    EXPIRES_AT_FIELD_NUMBER: _ClassVar[int]
    TAG_FIELD_NUMBER: _ClassVar[int]
    epoch: bytes
    counter: int
    expires_at: int
    tag: bytes

    def __init__(self, epoch: _Optional[bytes]=..., counter: _Optional[int]=..., expires_at: _Optional[int]=..., tag: _Optional[bytes]=...) -> None:
        ...

class SignatureData(_message.Message):
    __slots__ = ('signer_identity', 'AES_GCM_Personalized_data', 'session_info_tag', 'HMAC_Personalized_data', 'AES_GCM_Response_data')
    SIGNER_IDENTITY_FIELD_NUMBER: _ClassVar[int]
    AES_GCM_PERSONALIZED_DATA_FIELD_NUMBER: _ClassVar[int]
    SESSION_INFO_TAG_FIELD_NUMBER: _ClassVar[int]
    HMAC_PERSONALIZED_DATA_FIELD_NUMBER: _ClassVar[int]
    AES_GCM_RESPONSE_DATA_FIELD_NUMBER: _ClassVar[int]
    signer_identity: KeyIdentity
    AES_GCM_Personalized_data: AES_GCM_Personalized_Signature_Data
    session_info_tag: HMAC_Signature_Data
    HMAC_Personalized_data: HMAC_Personalized_Signature_Data
    AES_GCM_Response_data: AES_GCM_Response_Signature_Data

    def __init__(self, signer_identity: _Optional[_Union[KeyIdentity, _Mapping]]=..., AES_GCM_Personalized_data: _Optional[_Union[AES_GCM_Personalized_Signature_Data, _Mapping]]=..., session_info_tag: _Optional[_Union[HMAC_Signature_Data, _Mapping]]=..., HMAC_Personalized_data: _Optional[_Union[HMAC_Personalized_Signature_Data, _Mapping]]=..., AES_GCM_Response_data: _Optional[_Union[AES_GCM_Response_Signature_Data, _Mapping]]=...) -> None:
        ...

class GetSessionInfoRequest(_message.Message):
    __slots__ = ('key_identity',)
    KEY_IDENTITY_FIELD_NUMBER: _ClassVar[int]
    key_identity: KeyIdentity

    def __init__(self, key_identity: _Optional[_Union[KeyIdentity, _Mapping]]=...) -> None:
        ...

class SessionInfo(_message.Message):
    __slots__ = ('counter', 'publicKey', 'epoch', 'clock_time', 'status', 'handle')
    COUNTER_FIELD_NUMBER: _ClassVar[int]
    PUBLICKEY_FIELD_NUMBER: _ClassVar[int]
    EPOCH_FIELD_NUMBER: _ClassVar[int]
    CLOCK_TIME_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    HANDLE_FIELD_NUMBER: _ClassVar[int]
    counter: int
    publicKey: bytes
    epoch: bytes
    clock_time: int
    status: Session_Info_Status
    handle: int

    def __init__(self, counter: _Optional[int]=..., publicKey: _Optional[bytes]=..., epoch: _Optional[bytes]=..., clock_time: _Optional[int]=..., status: _Optional[_Union[Session_Info_Status, str]]=..., handle: _Optional[int]=...) -> None:
        ...