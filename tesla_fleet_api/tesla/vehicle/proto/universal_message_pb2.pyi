import signatures_pb2 as _signatures_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union
DESCRIPTOR: _descriptor.FileDescriptor

class Domain(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    DOMAIN_BROADCAST: _ClassVar[Domain]
    DOMAIN_VEHICLE_SECURITY: _ClassVar[Domain]
    DOMAIN_INFOTAINMENT: _ClassVar[Domain]

class OperationStatus_E(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    OPERATIONSTATUS_OK: _ClassVar[OperationStatus_E]
    OPERATIONSTATUS_WAIT: _ClassVar[OperationStatus_E]
    OPERATIONSTATUS_ERROR: _ClassVar[OperationStatus_E]

class MessageFault_E(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    MESSAGEFAULT_ERROR_NONE: _ClassVar[MessageFault_E]
    MESSAGEFAULT_ERROR_BUSY: _ClassVar[MessageFault_E]
    MESSAGEFAULT_ERROR_TIMEOUT: _ClassVar[MessageFault_E]
    MESSAGEFAULT_ERROR_UNKNOWN_KEY_ID: _ClassVar[MessageFault_E]
    MESSAGEFAULT_ERROR_INACTIVE_KEY: _ClassVar[MessageFault_E]
    MESSAGEFAULT_ERROR_INVALID_SIGNATURE: _ClassVar[MessageFault_E]
    MESSAGEFAULT_ERROR_INVALID_TOKEN_OR_COUNTER: _ClassVar[MessageFault_E]
    MESSAGEFAULT_ERROR_INSUFFICIENT_PRIVILEGES: _ClassVar[MessageFault_E]
    MESSAGEFAULT_ERROR_INVALID_DOMAINS: _ClassVar[MessageFault_E]
    MESSAGEFAULT_ERROR_INVALID_COMMAND: _ClassVar[MessageFault_E]
    MESSAGEFAULT_ERROR_DECODING: _ClassVar[MessageFault_E]
    MESSAGEFAULT_ERROR_INTERNAL: _ClassVar[MessageFault_E]
    MESSAGEFAULT_ERROR_WRONG_PERSONALIZATION: _ClassVar[MessageFault_E]
    MESSAGEFAULT_ERROR_BAD_PARAMETER: _ClassVar[MessageFault_E]
    MESSAGEFAULT_ERROR_KEYCHAIN_IS_FULL: _ClassVar[MessageFault_E]
    MESSAGEFAULT_ERROR_INCORRECT_EPOCH: _ClassVar[MessageFault_E]
    MESSAGEFAULT_ERROR_IV_INCORRECT_LENGTH: _ClassVar[MessageFault_E]
    MESSAGEFAULT_ERROR_TIME_EXPIRED: _ClassVar[MessageFault_E]
    MESSAGEFAULT_ERROR_NOT_PROVISIONED_WITH_IDENTITY: _ClassVar[MessageFault_E]
    MESSAGEFAULT_ERROR_COULD_NOT_HASH_METADATA: _ClassVar[MessageFault_E]
    MESSAGEFAULT_ERROR_TIME_TO_LIVE_TOO_LONG: _ClassVar[MessageFault_E]
    MESSAGEFAULT_ERROR_REMOTE_ACCESS_DISABLED: _ClassVar[MessageFault_E]
    MESSAGEFAULT_ERROR_REMOTE_SERVICE_ACCESS_DISABLED: _ClassVar[MessageFault_E]
    MESSAGEFAULT_ERROR_COMMAND_REQUIRES_ACCOUNT_CREDENTIALS: _ClassVar[MessageFault_E]
    MESSAGEFAULT_ERROR_REQUEST_MTU_EXCEEDED: _ClassVar[MessageFault_E]
    MESSAGEFAULT_ERROR_RESPONSE_MTU_EXCEEDED: _ClassVar[MessageFault_E]
    MESSAGEFAULT_ERROR_REPEATED_COUNTER: _ClassVar[MessageFault_E]
    MESSAGEFAULT_ERROR_INVALID_KEY_HANDLE: _ClassVar[MessageFault_E]
    MESSAGEFAULT_ERROR_REQUIRES_RESPONSE_ENCRYPTION: _ClassVar[MessageFault_E]

class Flags(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    FLAG_USER_COMMAND: _ClassVar[Flags]
    FLAG_ENCRYPT_RESPONSE: _ClassVar[Flags]
DOMAIN_BROADCAST: Domain
DOMAIN_VEHICLE_SECURITY: Domain
DOMAIN_INFOTAINMENT: Domain
OPERATIONSTATUS_OK: OperationStatus_E
OPERATIONSTATUS_WAIT: OperationStatus_E
OPERATIONSTATUS_ERROR: OperationStatus_E
MESSAGEFAULT_ERROR_NONE: MessageFault_E
MESSAGEFAULT_ERROR_BUSY: MessageFault_E
MESSAGEFAULT_ERROR_TIMEOUT: MessageFault_E
MESSAGEFAULT_ERROR_UNKNOWN_KEY_ID: MessageFault_E
MESSAGEFAULT_ERROR_INACTIVE_KEY: MessageFault_E
MESSAGEFAULT_ERROR_INVALID_SIGNATURE: MessageFault_E
MESSAGEFAULT_ERROR_INVALID_TOKEN_OR_COUNTER: MessageFault_E
MESSAGEFAULT_ERROR_INSUFFICIENT_PRIVILEGES: MessageFault_E
MESSAGEFAULT_ERROR_INVALID_DOMAINS: MessageFault_E
MESSAGEFAULT_ERROR_INVALID_COMMAND: MessageFault_E
MESSAGEFAULT_ERROR_DECODING: MessageFault_E
MESSAGEFAULT_ERROR_INTERNAL: MessageFault_E
MESSAGEFAULT_ERROR_WRONG_PERSONALIZATION: MessageFault_E
MESSAGEFAULT_ERROR_BAD_PARAMETER: MessageFault_E
MESSAGEFAULT_ERROR_KEYCHAIN_IS_FULL: MessageFault_E
MESSAGEFAULT_ERROR_INCORRECT_EPOCH: MessageFault_E
MESSAGEFAULT_ERROR_IV_INCORRECT_LENGTH: MessageFault_E
MESSAGEFAULT_ERROR_TIME_EXPIRED: MessageFault_E
MESSAGEFAULT_ERROR_NOT_PROVISIONED_WITH_IDENTITY: MessageFault_E
MESSAGEFAULT_ERROR_COULD_NOT_HASH_METADATA: MessageFault_E
MESSAGEFAULT_ERROR_TIME_TO_LIVE_TOO_LONG: MessageFault_E
MESSAGEFAULT_ERROR_REMOTE_ACCESS_DISABLED: MessageFault_E
MESSAGEFAULT_ERROR_REMOTE_SERVICE_ACCESS_DISABLED: MessageFault_E
MESSAGEFAULT_ERROR_COMMAND_REQUIRES_ACCOUNT_CREDENTIALS: MessageFault_E
MESSAGEFAULT_ERROR_REQUEST_MTU_EXCEEDED: MessageFault_E
MESSAGEFAULT_ERROR_RESPONSE_MTU_EXCEEDED: MessageFault_E
MESSAGEFAULT_ERROR_REPEATED_COUNTER: MessageFault_E
MESSAGEFAULT_ERROR_INVALID_KEY_HANDLE: MessageFault_E
MESSAGEFAULT_ERROR_REQUIRES_RESPONSE_ENCRYPTION: MessageFault_E
FLAG_USER_COMMAND: Flags
FLAG_ENCRYPT_RESPONSE: Flags

class Destination(_message.Message):
    __slots__ = ('domain', 'routing_address')
    DOMAIN_FIELD_NUMBER: _ClassVar[int]
    ROUTING_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    domain: Domain
    routing_address: bytes

    def __init__(self, domain: _Optional[_Union[Domain, str]]=..., routing_address: _Optional[bytes]=...) -> None:
        ...

class MessageStatus(_message.Message):
    __slots__ = ('operation_status', 'signed_message_fault')
    OPERATION_STATUS_FIELD_NUMBER: _ClassVar[int]
    SIGNED_MESSAGE_FAULT_FIELD_NUMBER: _ClassVar[int]
    operation_status: OperationStatus_E
    signed_message_fault: MessageFault_E

    def __init__(self, operation_status: _Optional[_Union[OperationStatus_E, str]]=..., signed_message_fault: _Optional[_Union[MessageFault_E, str]]=...) -> None:
        ...

class SessionInfoRequest(_message.Message):
    __slots__ = ('public_key', 'challenge')
    PUBLIC_KEY_FIELD_NUMBER: _ClassVar[int]
    CHALLENGE_FIELD_NUMBER: _ClassVar[int]
    public_key: bytes
    challenge: bytes

    def __init__(self, public_key: _Optional[bytes]=..., challenge: _Optional[bytes]=...) -> None:
        ...

class RoutableMessage(_message.Message):
    __slots__ = ('to_destination', 'from_destination', 'protobuf_message_as_bytes', 'session_info_request', 'session_info', 'signature_data', 'signedMessageStatus', 'request_uuid', 'uuid', 'flags')
    TO_DESTINATION_FIELD_NUMBER: _ClassVar[int]
    FROM_DESTINATION_FIELD_NUMBER: _ClassVar[int]
    PROTOBUF_MESSAGE_AS_BYTES_FIELD_NUMBER: _ClassVar[int]
    SESSION_INFO_REQUEST_FIELD_NUMBER: _ClassVar[int]
    SESSION_INFO_FIELD_NUMBER: _ClassVar[int]
    SIGNATURE_DATA_FIELD_NUMBER: _ClassVar[int]
    SIGNEDMESSAGESTATUS_FIELD_NUMBER: _ClassVar[int]
    REQUEST_UUID_FIELD_NUMBER: _ClassVar[int]
    UUID_FIELD_NUMBER: _ClassVar[int]
    FLAGS_FIELD_NUMBER: _ClassVar[int]
    to_destination: Destination
    from_destination: Destination
    protobuf_message_as_bytes: bytes
    session_info_request: SessionInfoRequest
    session_info: bytes
    signature_data: _signatures_pb2.SignatureData
    signedMessageStatus: MessageStatus
    request_uuid: bytes
    uuid: bytes
    flags: int

    def __init__(self, to_destination: _Optional[_Union[Destination, _Mapping]]=..., from_destination: _Optional[_Union[Destination, _Mapping]]=..., protobuf_message_as_bytes: _Optional[bytes]=..., session_info_request: _Optional[_Union[SessionInfoRequest, _Mapping]]=..., session_info: _Optional[bytes]=..., signature_data: _Optional[_Union[_signatures_pb2.SignatureData, _Mapping]]=..., signedMessageStatus: _Optional[_Union[MessageStatus, _Mapping]]=..., request_uuid: _Optional[bytes]=..., uuid: _Optional[bytes]=..., flags: _Optional[int]=...) -> None:
        ...