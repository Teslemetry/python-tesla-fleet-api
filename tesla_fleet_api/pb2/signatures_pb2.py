"""Generated protocol buffer code."""
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x10signatures.proto\x12\nSignatures"L\n\x0bKeyIdentity\x12\x14\n\npublic_key\x18\x01 \x01(\x0cH\x00\x12\x10\n\x06handle\x18\x03 \x01(\rH\x00B\x0f\n\ridentity_typeJ\x04\x08\x02\x10\x03"u\n#AES_GCM_Personalized_Signature_Data\x12\r\n\x05epoch\x18\x01 \x01(\x0c\x12\r\n\x05nonce\x18\x02 \x01(\x0c\x12\x0f\n\x07counter\x18\x03 \x01(\r\x12\x12\n\nexpires_at\x18\x04 \x01(\x07\x12\x0b\n\x03tag\x18\x05 \x01(\x0c""\n\x13HMAC_Signature_Data\x12\x0b\n\x03tag\x18\x01 \x01(\x0c"c\n HMAC_Personalized_Signature_Data\x12\r\n\x05epoch\x18\x01 \x01(\x0c\x12\x0f\n\x07counter\x18\x02 \x01(\r\x12\x12\n\nexpires_at\x18\x03 \x01(\x07\x12\x0b\n\x03tag\x18\x04 \x01(\x0c"\xb6\x02\n\rSignatureData\x120\n\x0fsigner_identity\x18\x01 \x01(\x0b2\x17.Signatures.KeyIdentity\x12T\n\x19AES_GCM_Personalized_data\x18\x05 \x01(\x0b2/.Signatures.AES_GCM_Personalized_Signature_DataH\x00\x12;\n\x10session_info_tag\x18\x06 \x01(\x0b2\x1f.Signatures.HMAC_Signature_DataH\x00\x12N\n\x16HMAC_Personalized_data\x18\x08 \x01(\x0b2,.Signatures.HMAC_Personalized_Signature_DataH\x00B\n\n\x08sig_typeJ\x04\x08\x07\x10\x08"F\n\x15GetSessionInfoRequest\x12-\n\x0ckey_identity\x18\x01 \x01(\x0b2\x17.Signatures.KeyIdentity"\x95\x01\n\x0bSessionInfo\x12\x0f\n\x07counter\x18\x01 \x01(\r\x12\x11\n\tpublicKey\x18\x02 \x01(\x0c\x12\r\n\x05epoch\x18\x03 \x01(\x0c\x12\x12\n\nclock_time\x18\x04 \x01(\x07\x12/\n\x06status\x18\x05 \x01(\x0e2\x1f.Signatures.Session_Info_Status\x12\x0e\n\x06handle\x18\x06 \x01(\r*\xaa\x01\n\x03Tag\x12\x16\n\x12TAG_SIGNATURE_TYPE\x10\x00\x12\x0e\n\nTAG_DOMAIN\x10\x01\x12\x17\n\x13TAG_PERSONALIZATION\x10\x02\x12\r\n\tTAG_EPOCH\x10\x03\x12\x12\n\x0eTAG_EXPIRES_AT\x10\x04\x12\x0f\n\x0bTAG_COUNTER\x10\x05\x12\x11\n\rTAG_CHALLENGE\x10\x06\x12\r\n\tTAG_FLAGS\x10\x07\x12\x0c\n\x07TAG_END\x10\xff\x01*\x99\x01\n\rSignatureType\x12\x1a\n\x16SIGNATURE_TYPE_AES_GCM\x10\x00\x12\'\n#SIGNATURE_TYPE_AES_GCM_PERSONALIZED\x10\x05\x12\x17\n\x13SIGNATURE_TYPE_HMAC\x10\x06\x12$\n SIGNATURE_TYPE_HMAC_PERSONALIZED\x10\x08"\x04\x08\x07\x10\x07*_\n\x13Session_Info_Status\x12\x1a\n\x16SESSION_INFO_STATUS_OK\x10\x00\x12,\n(SESSION_INFO_STATUS_KEY_NOT_ON_WHITELIST\x10\x01Bi\n\x1ecom.tesla.generated.signaturesZGgithub.com/teslamotors/vehicle-command/pkg/protocol/protobuf/signaturesb\x06proto3')
_TAG = DESCRIPTOR.enum_types_by_name['Tag']
Tag = enum_type_wrapper.EnumTypeWrapper(_TAG)
_SIGNATURETYPE = DESCRIPTOR.enum_types_by_name['SignatureType']
SignatureType = enum_type_wrapper.EnumTypeWrapper(_SIGNATURETYPE)
_SESSION_INFO_STATUS = DESCRIPTOR.enum_types_by_name['Session_Info_Status']
Session_Info_Status = enum_type_wrapper.EnumTypeWrapper(_SESSION_INFO_STATUS)
TAG_SIGNATURE_TYPE = 0
TAG_DOMAIN = 1
TAG_PERSONALIZATION = 2
TAG_EPOCH = 3
TAG_EXPIRES_AT = 4
TAG_COUNTER = 5
TAG_CHALLENGE = 6
TAG_FLAGS = 7
TAG_END = 255
SIGNATURE_TYPE_AES_GCM = 0
SIGNATURE_TYPE_AES_GCM_PERSONALIZED = 5
SIGNATURE_TYPE_HMAC = 6
SIGNATURE_TYPE_HMAC_PERSONALIZED = 8
SESSION_INFO_STATUS_OK = 0
SESSION_INFO_STATUS_KEY_NOT_ON_WHITELIST = 1
_KEYIDENTITY = DESCRIPTOR.message_types_by_name['KeyIdentity']
_AES_GCM_PERSONALIZED_SIGNATURE_DATA = DESCRIPTOR.message_types_by_name['AES_GCM_Personalized_Signature_Data']
_HMAC_SIGNATURE_DATA = DESCRIPTOR.message_types_by_name['HMAC_Signature_Data']
_HMAC_PERSONALIZED_SIGNATURE_DATA = DESCRIPTOR.message_types_by_name['HMAC_Personalized_Signature_Data']
_SIGNATUREDATA = DESCRIPTOR.message_types_by_name['SignatureData']
_GETSESSIONINFOREQUEST = DESCRIPTOR.message_types_by_name['GetSessionInfoRequest']
_SESSIONINFO = DESCRIPTOR.message_types_by_name['SessionInfo']
KeyIdentity = _reflection.GeneratedProtocolMessageType('KeyIdentity', (_message.Message,), {'DESCRIPTOR': _KEYIDENTITY, '__module__': 'signatures_pb2'})
_sym_db.RegisterMessage(KeyIdentity)
AES_GCM_Personalized_Signature_Data = _reflection.GeneratedProtocolMessageType('AES_GCM_Personalized_Signature_Data', (_message.Message,), {'DESCRIPTOR': _AES_GCM_PERSONALIZED_SIGNATURE_DATA, '__module__': 'signatures_pb2'})
_sym_db.RegisterMessage(AES_GCM_Personalized_Signature_Data)
HMAC_Signature_Data = _reflection.GeneratedProtocolMessageType('HMAC_Signature_Data', (_message.Message,), {'DESCRIPTOR': _HMAC_SIGNATURE_DATA, '__module__': 'signatures_pb2'})
_sym_db.RegisterMessage(HMAC_Signature_Data)
HMAC_Personalized_Signature_Data = _reflection.GeneratedProtocolMessageType('HMAC_Personalized_Signature_Data', (_message.Message,), {'DESCRIPTOR': _HMAC_PERSONALIZED_SIGNATURE_DATA, '__module__': 'signatures_pb2'})
_sym_db.RegisterMessage(HMAC_Personalized_Signature_Data)
SignatureData = _reflection.GeneratedProtocolMessageType('SignatureData', (_message.Message,), {'DESCRIPTOR': _SIGNATUREDATA, '__module__': 'signatures_pb2'})
_sym_db.RegisterMessage(SignatureData)
GetSessionInfoRequest = _reflection.GeneratedProtocolMessageType('GetSessionInfoRequest', (_message.Message,), {'DESCRIPTOR': _GETSESSIONINFOREQUEST, '__module__': 'signatures_pb2'})
_sym_db.RegisterMessage(GetSessionInfoRequest)
SessionInfo = _reflection.GeneratedProtocolMessageType('SessionInfo', (_message.Message,), {'DESCRIPTOR': _SESSIONINFO, '__module__': 'signatures_pb2'})
_sym_db.RegisterMessage(SessionInfo)
if _descriptor._USE_C_DESCRIPTORS == False:
    DESCRIPTOR._options = None
    DESCRIPTOR._serialized_options = b'\n\x1ecom.tesla.generated.signaturesZGgithub.com/teslamotors/vehicle-command/pkg/protocol/protobuf/signatures'
    _TAG._serialized_start = 904
    _TAG._serialized_end = 1074
    _SIGNATURETYPE._serialized_start = 1077
    _SIGNATURETYPE._serialized_end = 1230
    _SESSION_INFO_STATUS._serialized_start = 1232
    _SESSION_INFO_STATUS._serialized_end = 1327
    _KEYIDENTITY._serialized_start = 32
    _KEYIDENTITY._serialized_end = 108
    _AES_GCM_PERSONALIZED_SIGNATURE_DATA._serialized_start = 110
    _AES_GCM_PERSONALIZED_SIGNATURE_DATA._serialized_end = 227
    _HMAC_SIGNATURE_DATA._serialized_start = 229
    _HMAC_SIGNATURE_DATA._serialized_end = 263
    _HMAC_PERSONALIZED_SIGNATURE_DATA._serialized_start = 265
    _HMAC_PERSONALIZED_SIGNATURE_DATA._serialized_end = 364
    _SIGNATUREDATA._serialized_start = 367
    _SIGNATUREDATA._serialized_end = 677
    _GETSESSIONINFOREQUEST._serialized_start = 679
    _GETSESSIONINFOREQUEST._serialized_end = 749
    _SESSIONINFO._serialized_start = 752
    _SESSIONINFO._serialized_end = 901