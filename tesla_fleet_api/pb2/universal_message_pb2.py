"""Generated protocol buffer code."""
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from . import signatures_pb2 as signatures__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x17universal_message.proto\x12\x10UniversalMessage\x1a\x10signatures.proto"g\n\x0bDestination\x12*\n\x06domain\x18\x01 \x01(\x0e2\x18.UniversalMessage.DomainH\x00\x12\x19\n\x0frouting_address\x18\x02 \x01(\x0cH\x00B\x11\n\x0fsub_destination"\x8e\x01\n\rMessageStatus\x12=\n\x10operation_status\x18\x01 \x01(\x0e2#.UniversalMessage.OperationStatus_E\x12>\n\x14signed_message_fault\x18\x02 \x01(\x0e2 .UniversalMessage.MessageFault_E";\n\x12SessionInfoRequest\x12\x12\n\npublic_key\x18\x01 \x01(\x0c\x12\x11\n\tchallenge\x18\x02 \x01(\x0c"\xd6\x03\n\x0fRoutableMessage\x125\n\x0eto_destination\x18\x06 \x01(\x0b2\x1d.UniversalMessage.Destination\x127\n\x10from_destination\x18\x07 \x01(\x0b2\x1d.UniversalMessage.Destination\x12#\n\x19protobuf_message_as_bytes\x18\n \x01(\x0cH\x00\x12D\n\x14session_info_request\x18\x0e \x01(\x0b2$.UniversalMessage.SessionInfoRequestH\x00\x12\x16\n\x0csession_info\x18\x0f \x01(\x0cH\x00\x123\n\x0esignature_data\x18\r \x01(\x0b2\x19.Signatures.SignatureDataH\x01\x12<\n\x13signedMessageStatus\x18\x0c \x01(\x0b2\x1f.UniversalMessage.MessageStatus\x12\x14\n\x0crequest_uuid\x182 \x01(\x0c\x12\x0c\n\x04uuid\x183 \x01(\x0c\x12\r\n\x05flags\x184 \x01(\rB\t\n\x07payloadB\r\n\x0bsub_sigDataJ\x04\x08\x01\x10\x06J\x04\x08\x10\x10)J\x04\x08\x0b\x10\x0c*T\n\x06Domain\x12\x14\n\x10DOMAIN_BROADCAST\x10\x00\x12\x1b\n\x17DOMAIN_VEHICLE_SECURITY\x10\x02\x12\x17\n\x13DOMAIN_INFOTAINMENT\x10\x03*`\n\x11OperationStatus_E\x12\x16\n\x12OPERATIONSTATUS_OK\x10\x00\x12\x18\n\x14OPERATIONSTATUS_WAIT\x10\x01\x12\x19\n\x15OPERATIONSTATUS_ERROR\x10\x02*\x80\x08\n\x0eMessageFault_E\x12\x1b\n\x17MESSAGEFAULT_ERROR_NONE\x10\x00\x12\x1b\n\x17MESSAGEFAULT_ERROR_BUSY\x10\x01\x12\x1e\n\x1aMESSAGEFAULT_ERROR_TIMEOUT\x10\x02\x12%\n!MESSAGEFAULT_ERROR_UNKNOWN_KEY_ID\x10\x03\x12#\n\x1fMESSAGEFAULT_ERROR_INACTIVE_KEY\x10\x04\x12(\n$MESSAGEFAULT_ERROR_INVALID_SIGNATURE\x10\x05\x12/\n+MESSAGEFAULT_ERROR_INVALID_TOKEN_OR_COUNTER\x10\x06\x12.\n*MESSAGEFAULT_ERROR_INSUFFICIENT_PRIVILEGES\x10\x07\x12&\n"MESSAGEFAULT_ERROR_INVALID_DOMAINS\x10\x08\x12&\n"MESSAGEFAULT_ERROR_INVALID_COMMAND\x10\t\x12\x1f\n\x1bMESSAGEFAULT_ERROR_DECODING\x10\n\x12\x1f\n\x1bMESSAGEFAULT_ERROR_INTERNAL\x10\x0b\x12,\n(MESSAGEFAULT_ERROR_WRONG_PERSONALIZATION\x10\x0c\x12$\n MESSAGEFAULT_ERROR_BAD_PARAMETER\x10\r\x12\'\n#MESSAGEFAULT_ERROR_KEYCHAIN_IS_FULL\x10\x0e\x12&\n"MESSAGEFAULT_ERROR_INCORRECT_EPOCH\x10\x0f\x12*\n&MESSAGEFAULT_ERROR_IV_INCORRECT_LENGTH\x10\x10\x12#\n\x1fMESSAGEFAULT_ERROR_TIME_EXPIRED\x10\x11\x124\n0MESSAGEFAULT_ERROR_NOT_PROVISIONED_WITH_IDENTITY\x10\x12\x12.\n*MESSAGEFAULT_ERROR_COULD_NOT_HASH_METADATA\x10\x13\x12,\n(MESSAGEFAULT_ERROR_TIME_TO_LIVE_TOO_LONG\x10\x14\x12-\n)MESSAGEFAULT_ERROR_REMOTE_ACCESS_DISABLED\x10\x15\x125\n1MESSAGEFAULT_ERROR_REMOTE_SERVICE_ACCESS_DISABLED\x10\x16\x12;\n7MESSAGEFAULT_ERROR_COMMAND_REQUIRES_ACCOUNT_CREDENTIALS\x10\x17*\x1e\n\x05Flags\x12\x15\n\x11FLAG_USER_COMMAND\x10\x00Bu\n$com.tesla.generated.universalmessageZMgithub.com/teslamotors/vehicle-command/pkg/protocol/protobuf/universalmessageb\x06proto3')
_DOMAIN = DESCRIPTOR.enum_types_by_name['Domain']
Domain = enum_type_wrapper.EnumTypeWrapper(_DOMAIN)
_OPERATIONSTATUS_E = DESCRIPTOR.enum_types_by_name['OperationStatus_E']
OperationStatus_E = enum_type_wrapper.EnumTypeWrapper(_OPERATIONSTATUS_E)
_MESSAGEFAULT_E = DESCRIPTOR.enum_types_by_name['MessageFault_E']
MessageFault_E = enum_type_wrapper.EnumTypeWrapper(_MESSAGEFAULT_E)
_FLAGS = DESCRIPTOR.enum_types_by_name['Flags']
Flags = enum_type_wrapper.EnumTypeWrapper(_FLAGS)
DOMAIN_BROADCAST = 0
DOMAIN_VEHICLE_SECURITY = 2
DOMAIN_INFOTAINMENT = 3
OPERATIONSTATUS_OK = 0
OPERATIONSTATUS_WAIT = 1
OPERATIONSTATUS_ERROR = 2
MESSAGEFAULT_ERROR_NONE = 0
MESSAGEFAULT_ERROR_BUSY = 1
MESSAGEFAULT_ERROR_TIMEOUT = 2
MESSAGEFAULT_ERROR_UNKNOWN_KEY_ID = 3
MESSAGEFAULT_ERROR_INACTIVE_KEY = 4
MESSAGEFAULT_ERROR_INVALID_SIGNATURE = 5
MESSAGEFAULT_ERROR_INVALID_TOKEN_OR_COUNTER = 6
MESSAGEFAULT_ERROR_INSUFFICIENT_PRIVILEGES = 7
MESSAGEFAULT_ERROR_INVALID_DOMAINS = 8
MESSAGEFAULT_ERROR_INVALID_COMMAND = 9
MESSAGEFAULT_ERROR_DECODING = 10
MESSAGEFAULT_ERROR_INTERNAL = 11
MESSAGEFAULT_ERROR_WRONG_PERSONALIZATION = 12
MESSAGEFAULT_ERROR_BAD_PARAMETER = 13
MESSAGEFAULT_ERROR_KEYCHAIN_IS_FULL = 14
MESSAGEFAULT_ERROR_INCORRECT_EPOCH = 15
MESSAGEFAULT_ERROR_IV_INCORRECT_LENGTH = 16
MESSAGEFAULT_ERROR_TIME_EXPIRED = 17
MESSAGEFAULT_ERROR_NOT_PROVISIONED_WITH_IDENTITY = 18
MESSAGEFAULT_ERROR_COULD_NOT_HASH_METADATA = 19
MESSAGEFAULT_ERROR_TIME_TO_LIVE_TOO_LONG = 20
MESSAGEFAULT_ERROR_REMOTE_ACCESS_DISABLED = 21
MESSAGEFAULT_ERROR_REMOTE_SERVICE_ACCESS_DISABLED = 22
MESSAGEFAULT_ERROR_COMMAND_REQUIRES_ACCOUNT_CREDENTIALS = 23
FLAG_USER_COMMAND = 0
_DESTINATION = DESCRIPTOR.message_types_by_name['Destination']
_MESSAGESTATUS = DESCRIPTOR.message_types_by_name['MessageStatus']
_SESSIONINFOREQUEST = DESCRIPTOR.message_types_by_name['SessionInfoRequest']
_ROUTABLEMESSAGE = DESCRIPTOR.message_types_by_name['RoutableMessage']
Destination = _reflection.GeneratedProtocolMessageType('Destination', (_message.Message,), {'DESCRIPTOR': _DESTINATION, '__module__': 'universal_message_pb2'})
_sym_db.RegisterMessage(Destination)
MessageStatus = _reflection.GeneratedProtocolMessageType('MessageStatus', (_message.Message,), {'DESCRIPTOR': _MESSAGESTATUS, '__module__': 'universal_message_pb2'})
_sym_db.RegisterMessage(MessageStatus)
SessionInfoRequest = _reflection.GeneratedProtocolMessageType('SessionInfoRequest', (_message.Message,), {'DESCRIPTOR': _SESSIONINFOREQUEST, '__module__': 'universal_message_pb2'})
_sym_db.RegisterMessage(SessionInfoRequest)
RoutableMessage = _reflection.GeneratedProtocolMessageType('RoutableMessage', (_message.Message,), {'DESCRIPTOR': _ROUTABLEMESSAGE, '__module__': 'universal_message_pb2'})
_sym_db.RegisterMessage(RoutableMessage)
if _descriptor._USE_C_DESCRIPTORS == False:
    DESCRIPTOR._options = None
    DESCRIPTOR._serialized_options = b'\n$com.tesla.generated.universalmessageZMgithub.com/teslamotors/vehicle-command/pkg/protocol/protobuf/universalmessage'
    _DOMAIN._serialized_start = 847
    _DOMAIN._serialized_end = 931
    _OPERATIONSTATUS_E._serialized_start = 933
    _OPERATIONSTATUS_E._serialized_end = 1029
    _MESSAGEFAULT_E._serialized_start = 1032
    _MESSAGEFAULT_E._serialized_end = 2056
    _FLAGS._serialized_start = 2058
    _FLAGS._serialized_end = 2088
    _DESTINATION._serialized_start = 63
    _DESTINATION._serialized_end = 166
    _MESSAGESTATUS._serialized_start = 169
    _MESSAGESTATUS._serialized_end = 311
    _SESSIONINFOREQUEST._serialized_start = 313
    _SESSIONINFOREQUEST._serialized_end = 372
    _ROUTABLEMESSAGE._serialized_start = 375
    _ROUTABLEMESSAGE._serialized_end = 845