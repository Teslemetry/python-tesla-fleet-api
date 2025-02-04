import keys_pb2 as _keys_pb2
import errors_pb2 as _errors_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union
DESCRIPTOR: _descriptor.FileDescriptor

class SignatureType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SIGNATURE_TYPE_NONE: _ClassVar[SignatureType]
    SIGNATURE_TYPE_PRESENT_KEY: _ClassVar[SignatureType]

class KeyFormFactor(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    KEY_FORM_FACTOR_UNKNOWN: _ClassVar[KeyFormFactor]
    KEY_FORM_FACTOR_NFC_CARD: _ClassVar[KeyFormFactor]
    KEY_FORM_FACTOR_IOS_DEVICE: _ClassVar[KeyFormFactor]
    KEY_FORM_FACTOR_ANDROID_DEVICE: _ClassVar[KeyFormFactor]
    KEY_FORM_FACTOR_CLOUD_KEY: _ClassVar[KeyFormFactor]

class InformationRequestType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    INFORMATION_REQUEST_TYPE_GET_STATUS: _ClassVar[InformationRequestType]
    INFORMATION_REQUEST_TYPE_GET_WHITELIST_INFO: _ClassVar[InformationRequestType]
    INFORMATION_REQUEST_TYPE_GET_WHITELIST_ENTRY_INFO: _ClassVar[InformationRequestType]

class RKEAction_E(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    RKE_ACTION_UNLOCK: _ClassVar[RKEAction_E]
    RKE_ACTION_LOCK: _ClassVar[RKEAction_E]
    RKE_ACTION_REMOTE_DRIVE: _ClassVar[RKEAction_E]
    RKE_ACTION_AUTO_SECURE_VEHICLE: _ClassVar[RKEAction_E]
    RKE_ACTION_WAKE_VEHICLE: _ClassVar[RKEAction_E]

class ClosureMoveType_E(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CLOSURE_MOVE_TYPE_NONE: _ClassVar[ClosureMoveType_E]
    CLOSURE_MOVE_TYPE_MOVE: _ClassVar[ClosureMoveType_E]
    CLOSURE_MOVE_TYPE_STOP: _ClassVar[ClosureMoveType_E]
    CLOSURE_MOVE_TYPE_OPEN: _ClassVar[ClosureMoveType_E]
    CLOSURE_MOVE_TYPE_CLOSE: _ClassVar[ClosureMoveType_E]

class OperationStatus_E(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    OPERATIONSTATUS_OK: _ClassVar[OperationStatus_E]
    OPERATIONSTATUS_WAIT: _ClassVar[OperationStatus_E]
    OPERATIONSTATUS_ERROR: _ClassVar[OperationStatus_E]

class SignedMessage_information_E(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SIGNEDMESSAGE_INFORMATION_NONE: _ClassVar[SignedMessage_information_E]
    SIGNEDMESSAGE_INFORMATION_FAULT_UNKNOWN: _ClassVar[SignedMessage_information_E]
    SIGNEDMESSAGE_INFORMATION_FAULT_NOT_ON_WHITELIST: _ClassVar[SignedMessage_information_E]
    SIGNEDMESSAGE_INFORMATION_FAULT_IV_SMALLER_THAN_EXPECTED: _ClassVar[SignedMessage_information_E]
    SIGNEDMESSAGE_INFORMATION_FAULT_INVALID_TOKEN: _ClassVar[SignedMessage_information_E]
    SIGNEDMESSAGE_INFORMATION_FAULT_TOKEN_AND_COUNTER_INVALID: _ClassVar[SignedMessage_information_E]
    SIGNEDMESSAGE_INFORMATION_FAULT_AES_DECRYPT_AUTH: _ClassVar[SignedMessage_information_E]
    SIGNEDMESSAGE_INFORMATION_FAULT_ECDSA_INPUT: _ClassVar[SignedMessage_information_E]
    SIGNEDMESSAGE_INFORMATION_FAULT_ECDSA_SIGNATURE: _ClassVar[SignedMessage_information_E]
    SIGNEDMESSAGE_INFORMATION_FAULT_LOCAL_ENTITY_START: _ClassVar[SignedMessage_information_E]
    SIGNEDMESSAGE_INFORMATION_FAULT_LOCAL_ENTITY_RESULT: _ClassVar[SignedMessage_information_E]
    SIGNEDMESSAGE_INFORMATION_FAULT_COULD_NOT_RETRIEVE_KEY: _ClassVar[SignedMessage_information_E]
    SIGNEDMESSAGE_INFORMATION_FAULT_COULD_NOT_RETRIEVE_TOKEN: _ClassVar[SignedMessage_information_E]
    SIGNEDMESSAGE_INFORMATION_FAULT_SIGNATURE_TOO_SHORT: _ClassVar[SignedMessage_information_E]
    SIGNEDMESSAGE_INFORMATION_FAULT_TOKEN_IS_INCORRECT_LENGTH: _ClassVar[SignedMessage_information_E]
    SIGNEDMESSAGE_INFORMATION_FAULT_INCORRECT_EPOCH: _ClassVar[SignedMessage_information_E]
    SIGNEDMESSAGE_INFORMATION_FAULT_IV_INCORRECT_LENGTH: _ClassVar[SignedMessage_information_E]
    SIGNEDMESSAGE_INFORMATION_FAULT_TIME_EXPIRED: _ClassVar[SignedMessage_information_E]
    SIGNEDMESSAGE_INFORMATION_FAULT_NOT_PROVISIONED_WITH_IDENTITY: _ClassVar[SignedMessage_information_E]
    SIGNEDMESSAGE_INFORMATION_FAULT_COULD_NOT_HASH_METADATA: _ClassVar[SignedMessage_information_E]

class WhitelistOperation_information_E(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    WHITELISTOPERATION_INFORMATION_NONE: _ClassVar[WhitelistOperation_information_E]
    WHITELISTOPERATION_INFORMATION_UNDOCUMENTED_ERROR: _ClassVar[WhitelistOperation_information_E]
    WHITELISTOPERATION_INFORMATION_NO_PERMISSION_TO_REMOVE_ONESELF: _ClassVar[WhitelistOperation_information_E]
    WHITELISTOPERATION_INFORMATION_KEYFOB_SLOTS_FULL: _ClassVar[WhitelistOperation_information_E]
    WHITELISTOPERATION_INFORMATION_WHITELIST_FULL: _ClassVar[WhitelistOperation_information_E]
    WHITELISTOPERATION_INFORMATION_NO_PERMISSION_TO_ADD: _ClassVar[WhitelistOperation_information_E]
    WHITELISTOPERATION_INFORMATION_INVALID_PUBLIC_KEY: _ClassVar[WhitelistOperation_information_E]
    WHITELISTOPERATION_INFORMATION_NO_PERMISSION_TO_REMOVE: _ClassVar[WhitelistOperation_information_E]
    WHITELISTOPERATION_INFORMATION_NO_PERMISSION_TO_CHANGE_PERMISSIONS: _ClassVar[WhitelistOperation_information_E]
    WHITELISTOPERATION_INFORMATION_ATTEMPTING_TO_ELEVATE_OTHER_ABOVE_ONESELF: _ClassVar[WhitelistOperation_information_E]
    WHITELISTOPERATION_INFORMATION_ATTEMPTING_TO_DEMOTE_SUPERIOR_TO_ONESELF: _ClassVar[WhitelistOperation_information_E]
    WHITELISTOPERATION_INFORMATION_ATTEMPTING_TO_REMOVE_OWN_PERMISSIONS: _ClassVar[WhitelistOperation_information_E]
    WHITELISTOPERATION_INFORMATION_PUBLIC_KEY_NOT_ON_WHITELIST: _ClassVar[WhitelistOperation_information_E]
    WHITELISTOPERATION_INFORMATION_ATTEMPTING_TO_ADD_KEY_THAT_IS_ALREADY_ON_THE_WHITELIST: _ClassVar[WhitelistOperation_information_E]
    WHITELISTOPERATION_INFORMATION_NOT_ALLOWED_TO_ADD_UNLESS_ON_READER: _ClassVar[WhitelistOperation_information_E]
    WHITELISTOPERATION_INFORMATION_FM_MODIFYING_OUTSIDE_OF_F_MODE: _ClassVar[WhitelistOperation_information_E]
    WHITELISTOPERATION_INFORMATION_FM_ATTEMPTING_TO_ADD_PERMANENT_KEY: _ClassVar[WhitelistOperation_information_E]
    WHITELISTOPERATION_INFORMATION_FM_ATTEMPTING_TO_REMOVE_PERMANENT_KEY: _ClassVar[WhitelistOperation_information_E]
    WHITELISTOPERATION_INFORMATION_KEYCHAIN_WHILE_FS_FULL: _ClassVar[WhitelistOperation_information_E]
    WHITELISTOPERATION_INFORMATION_ATTEMPTING_TO_ADD_KEY_WITHOUT_ROLE: _ClassVar[WhitelistOperation_information_E]
    WHITELISTOPERATION_INFORMATION_ATTEMPTING_TO_ADD_KEY_WITH_SERVICE_ROLE: _ClassVar[WhitelistOperation_information_E]
    WHITELISTOPERATION_INFORMATION_NON_SERVICE_KEY_ATTEMPTING_TO_ADD_SERVICE_TECH: _ClassVar[WhitelistOperation_information_E]
    WHITELISTOPERATION_INFORMATION_SERVICE_KEY_ATTEMPTING_TO_ADD_SERVICE_TECH_OUTSIDE_SERVICE_MODE: _ClassVar[WhitelistOperation_information_E]

class ClosureState_E(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CLOSURESTATE_CLOSED: _ClassVar[ClosureState_E]
    CLOSURESTATE_OPEN: _ClassVar[ClosureState_E]
    CLOSURESTATE_AJAR: _ClassVar[ClosureState_E]
    CLOSURESTATE_UNKNOWN: _ClassVar[ClosureState_E]
    CLOSURESTATE_FAILED_UNLATCH: _ClassVar[ClosureState_E]
    CLOSURESTATE_OPENING: _ClassVar[ClosureState_E]
    CLOSURESTATE_CLOSING: _ClassVar[ClosureState_E]

class VehicleLockState_E(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    VEHICLELOCKSTATE_UNLOCKED: _ClassVar[VehicleLockState_E]
    VEHICLELOCKSTATE_LOCKED: _ClassVar[VehicleLockState_E]
    VEHICLELOCKSTATE_INTERNAL_LOCKED: _ClassVar[VehicleLockState_E]
    VEHICLELOCKSTATE_SELECTIVE_UNLOCKED: _ClassVar[VehicleLockState_E]

class VehicleSleepStatus_E(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    VEHICLE_SLEEP_STATUS_UNKNOWN: _ClassVar[VehicleSleepStatus_E]
    VEHICLE_SLEEP_STATUS_AWAKE: _ClassVar[VehicleSleepStatus_E]
    VEHICLE_SLEEP_STATUS_ASLEEP: _ClassVar[VehicleSleepStatus_E]

class UserPresence_E(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    VEHICLE_USER_PRESENCE_UNKNOWN: _ClassVar[UserPresence_E]
    VEHICLE_USER_PRESENCE_NOT_PRESENT: _ClassVar[UserPresence_E]
    VEHICLE_USER_PRESENCE_PRESENT: _ClassVar[UserPresence_E]
SIGNATURE_TYPE_NONE: SignatureType
SIGNATURE_TYPE_PRESENT_KEY: SignatureType
KEY_FORM_FACTOR_UNKNOWN: KeyFormFactor
KEY_FORM_FACTOR_NFC_CARD: KeyFormFactor
KEY_FORM_FACTOR_IOS_DEVICE: KeyFormFactor
KEY_FORM_FACTOR_ANDROID_DEVICE: KeyFormFactor
KEY_FORM_FACTOR_CLOUD_KEY: KeyFormFactor
INFORMATION_REQUEST_TYPE_GET_STATUS: InformationRequestType
INFORMATION_REQUEST_TYPE_GET_WHITELIST_INFO: InformationRequestType
INFORMATION_REQUEST_TYPE_GET_WHITELIST_ENTRY_INFO: InformationRequestType
RKE_ACTION_UNLOCK: RKEAction_E
RKE_ACTION_LOCK: RKEAction_E
RKE_ACTION_REMOTE_DRIVE: RKEAction_E
RKE_ACTION_AUTO_SECURE_VEHICLE: RKEAction_E
RKE_ACTION_WAKE_VEHICLE: RKEAction_E
CLOSURE_MOVE_TYPE_NONE: ClosureMoveType_E
CLOSURE_MOVE_TYPE_MOVE: ClosureMoveType_E
CLOSURE_MOVE_TYPE_STOP: ClosureMoveType_E
CLOSURE_MOVE_TYPE_OPEN: ClosureMoveType_E
CLOSURE_MOVE_TYPE_CLOSE: ClosureMoveType_E
OPERATIONSTATUS_OK: OperationStatus_E
OPERATIONSTATUS_WAIT: OperationStatus_E
OPERATIONSTATUS_ERROR: OperationStatus_E
SIGNEDMESSAGE_INFORMATION_NONE: SignedMessage_information_E
SIGNEDMESSAGE_INFORMATION_FAULT_UNKNOWN: SignedMessage_information_E
SIGNEDMESSAGE_INFORMATION_FAULT_NOT_ON_WHITELIST: SignedMessage_information_E
SIGNEDMESSAGE_INFORMATION_FAULT_IV_SMALLER_THAN_EXPECTED: SignedMessage_information_E
SIGNEDMESSAGE_INFORMATION_FAULT_INVALID_TOKEN: SignedMessage_information_E
SIGNEDMESSAGE_INFORMATION_FAULT_TOKEN_AND_COUNTER_INVALID: SignedMessage_information_E
SIGNEDMESSAGE_INFORMATION_FAULT_AES_DECRYPT_AUTH: SignedMessage_information_E
SIGNEDMESSAGE_INFORMATION_FAULT_ECDSA_INPUT: SignedMessage_information_E
SIGNEDMESSAGE_INFORMATION_FAULT_ECDSA_SIGNATURE: SignedMessage_information_E
SIGNEDMESSAGE_INFORMATION_FAULT_LOCAL_ENTITY_START: SignedMessage_information_E
SIGNEDMESSAGE_INFORMATION_FAULT_LOCAL_ENTITY_RESULT: SignedMessage_information_E
SIGNEDMESSAGE_INFORMATION_FAULT_COULD_NOT_RETRIEVE_KEY: SignedMessage_information_E
SIGNEDMESSAGE_INFORMATION_FAULT_COULD_NOT_RETRIEVE_TOKEN: SignedMessage_information_E
SIGNEDMESSAGE_INFORMATION_FAULT_SIGNATURE_TOO_SHORT: SignedMessage_information_E
SIGNEDMESSAGE_INFORMATION_FAULT_TOKEN_IS_INCORRECT_LENGTH: SignedMessage_information_E
SIGNEDMESSAGE_INFORMATION_FAULT_INCORRECT_EPOCH: SignedMessage_information_E
SIGNEDMESSAGE_INFORMATION_FAULT_IV_INCORRECT_LENGTH: SignedMessage_information_E
SIGNEDMESSAGE_INFORMATION_FAULT_TIME_EXPIRED: SignedMessage_information_E
SIGNEDMESSAGE_INFORMATION_FAULT_NOT_PROVISIONED_WITH_IDENTITY: SignedMessage_information_E
SIGNEDMESSAGE_INFORMATION_FAULT_COULD_NOT_HASH_METADATA: SignedMessage_information_E
WHITELISTOPERATION_INFORMATION_NONE: WhitelistOperation_information_E
WHITELISTOPERATION_INFORMATION_UNDOCUMENTED_ERROR: WhitelistOperation_information_E
WHITELISTOPERATION_INFORMATION_NO_PERMISSION_TO_REMOVE_ONESELF: WhitelistOperation_information_E
WHITELISTOPERATION_INFORMATION_KEYFOB_SLOTS_FULL: WhitelistOperation_information_E
WHITELISTOPERATION_INFORMATION_WHITELIST_FULL: WhitelistOperation_information_E
WHITELISTOPERATION_INFORMATION_NO_PERMISSION_TO_ADD: WhitelistOperation_information_E
WHITELISTOPERATION_INFORMATION_INVALID_PUBLIC_KEY: WhitelistOperation_information_E
WHITELISTOPERATION_INFORMATION_NO_PERMISSION_TO_REMOVE: WhitelistOperation_information_E
WHITELISTOPERATION_INFORMATION_NO_PERMISSION_TO_CHANGE_PERMISSIONS: WhitelistOperation_information_E
WHITELISTOPERATION_INFORMATION_ATTEMPTING_TO_ELEVATE_OTHER_ABOVE_ONESELF: WhitelistOperation_information_E
WHITELISTOPERATION_INFORMATION_ATTEMPTING_TO_DEMOTE_SUPERIOR_TO_ONESELF: WhitelistOperation_information_E
WHITELISTOPERATION_INFORMATION_ATTEMPTING_TO_REMOVE_OWN_PERMISSIONS: WhitelistOperation_information_E
WHITELISTOPERATION_INFORMATION_PUBLIC_KEY_NOT_ON_WHITELIST: WhitelistOperation_information_E
WHITELISTOPERATION_INFORMATION_ATTEMPTING_TO_ADD_KEY_THAT_IS_ALREADY_ON_THE_WHITELIST: WhitelistOperation_information_E
WHITELISTOPERATION_INFORMATION_NOT_ALLOWED_TO_ADD_UNLESS_ON_READER: WhitelistOperation_information_E
WHITELISTOPERATION_INFORMATION_FM_MODIFYING_OUTSIDE_OF_F_MODE: WhitelistOperation_information_E
WHITELISTOPERATION_INFORMATION_FM_ATTEMPTING_TO_ADD_PERMANENT_KEY: WhitelistOperation_information_E
WHITELISTOPERATION_INFORMATION_FM_ATTEMPTING_TO_REMOVE_PERMANENT_KEY: WhitelistOperation_information_E
WHITELISTOPERATION_INFORMATION_KEYCHAIN_WHILE_FS_FULL: WhitelistOperation_information_E
WHITELISTOPERATION_INFORMATION_ATTEMPTING_TO_ADD_KEY_WITHOUT_ROLE: WhitelistOperation_information_E
WHITELISTOPERATION_INFORMATION_ATTEMPTING_TO_ADD_KEY_WITH_SERVICE_ROLE: WhitelistOperation_information_E
WHITELISTOPERATION_INFORMATION_NON_SERVICE_KEY_ATTEMPTING_TO_ADD_SERVICE_TECH: WhitelistOperation_information_E
WHITELISTOPERATION_INFORMATION_SERVICE_KEY_ATTEMPTING_TO_ADD_SERVICE_TECH_OUTSIDE_SERVICE_MODE: WhitelistOperation_information_E
CLOSURESTATE_CLOSED: ClosureState_E
CLOSURESTATE_OPEN: ClosureState_E
CLOSURESTATE_AJAR: ClosureState_E
CLOSURESTATE_UNKNOWN: ClosureState_E
CLOSURESTATE_FAILED_UNLATCH: ClosureState_E
CLOSURESTATE_OPENING: ClosureState_E
CLOSURESTATE_CLOSING: ClosureState_E
VEHICLELOCKSTATE_UNLOCKED: VehicleLockState_E
VEHICLELOCKSTATE_LOCKED: VehicleLockState_E
VEHICLELOCKSTATE_INTERNAL_LOCKED: VehicleLockState_E
VEHICLELOCKSTATE_SELECTIVE_UNLOCKED: VehicleLockState_E
VEHICLE_SLEEP_STATUS_UNKNOWN: VehicleSleepStatus_E
VEHICLE_SLEEP_STATUS_AWAKE: VehicleSleepStatus_E
VEHICLE_SLEEP_STATUS_ASLEEP: VehicleSleepStatus_E
VEHICLE_USER_PRESENCE_UNKNOWN: UserPresence_E
VEHICLE_USER_PRESENCE_NOT_PRESENT: UserPresence_E
VEHICLE_USER_PRESENCE_PRESENT: UserPresence_E

class SignedMessage(_message.Message):
    __slots__ = ('protobufMessageAsBytes', 'signatureType')
    PROTOBUFMESSAGEASBYTES_FIELD_NUMBER: _ClassVar[int]
    SIGNATURETYPE_FIELD_NUMBER: _ClassVar[int]
    protobufMessageAsBytes: bytes
    signatureType: SignatureType

    def __init__(self, protobufMessageAsBytes: _Optional[bytes]=..., signatureType: _Optional[_Union[SignatureType, str]]=...) -> None:
        ...

class ToVCSECMessage(_message.Message):
    __slots__ = ('signedMessage',)
    SIGNEDMESSAGE_FIELD_NUMBER: _ClassVar[int]
    signedMessage: SignedMessage

    def __init__(self, signedMessage: _Optional[_Union[SignedMessage, _Mapping]]=...) -> None:
        ...

class KeyIdentifier(_message.Message):
    __slots__ = ('publicKeySHA1',)
    PUBLICKEYSHA1_FIELD_NUMBER: _ClassVar[int]
    publicKeySHA1: bytes

    def __init__(self, publicKeySHA1: _Optional[bytes]=...) -> None:
        ...

class KeyMetadata(_message.Message):
    __slots__ = ('keyFormFactor',)
    KEYFORMFACTOR_FIELD_NUMBER: _ClassVar[int]
    keyFormFactor: KeyFormFactor

    def __init__(self, keyFormFactor: _Optional[_Union[KeyFormFactor, str]]=...) -> None:
        ...

class PublicKey(_message.Message):
    __slots__ = ('PublicKeyRaw',)
    PUBLICKEYRAW_FIELD_NUMBER: _ClassVar[int]
    PublicKeyRaw: bytes

    def __init__(self, PublicKeyRaw: _Optional[bytes]=...) -> None:
        ...

class WhitelistInfo(_message.Message):
    __slots__ = ('numberOfEntries', 'whitelistEntries', 'slotMask')
    NUMBEROFENTRIES_FIELD_NUMBER: _ClassVar[int]
    WHITELISTENTRIES_FIELD_NUMBER: _ClassVar[int]
    SLOTMASK_FIELD_NUMBER: _ClassVar[int]
    numberOfEntries: int
    whitelistEntries: _containers.RepeatedCompositeFieldContainer[KeyIdentifier]
    slotMask: int

    def __init__(self, numberOfEntries: _Optional[int]=..., whitelistEntries: _Optional[_Iterable[_Union[KeyIdentifier, _Mapping]]]=..., slotMask: _Optional[int]=...) -> None:
        ...

class WhitelistEntryInfo(_message.Message):
    __slots__ = ('keyId', 'publicKey', 'metadataForKey', 'slot', 'keyRole')
    KEYID_FIELD_NUMBER: _ClassVar[int]
    PUBLICKEY_FIELD_NUMBER: _ClassVar[int]
    METADATAFORKEY_FIELD_NUMBER: _ClassVar[int]
    SLOT_FIELD_NUMBER: _ClassVar[int]
    KEYROLE_FIELD_NUMBER: _ClassVar[int]
    keyId: KeyIdentifier
    publicKey: PublicKey
    metadataForKey: KeyMetadata
    slot: int
    keyRole: _keys_pb2.Role

    def __init__(self, keyId: _Optional[_Union[KeyIdentifier, _Mapping]]=..., publicKey: _Optional[_Union[PublicKey, _Mapping]]=..., metadataForKey: _Optional[_Union[KeyMetadata, _Mapping]]=..., slot: _Optional[int]=..., keyRole: _Optional[_Union[_keys_pb2.Role, str]]=...) -> None:
        ...

class InformationRequest(_message.Message):
    __slots__ = ('informationRequestType', 'keyId', 'publicKey', 'slot')
    INFORMATIONREQUESTTYPE_FIELD_NUMBER: _ClassVar[int]
    KEYID_FIELD_NUMBER: _ClassVar[int]
    PUBLICKEY_FIELD_NUMBER: _ClassVar[int]
    SLOT_FIELD_NUMBER: _ClassVar[int]
    informationRequestType: InformationRequestType
    keyId: KeyIdentifier
    publicKey: bytes
    slot: int

    def __init__(self, informationRequestType: _Optional[_Union[InformationRequestType, str]]=..., keyId: _Optional[_Union[KeyIdentifier, _Mapping]]=..., publicKey: _Optional[bytes]=..., slot: _Optional[int]=...) -> None:
        ...

class ClosureMoveRequest(_message.Message):
    __slots__ = ('frontDriverDoor', 'frontPassengerDoor', 'rearDriverDoor', 'rearPassengerDoor', 'rearTrunk', 'frontTrunk', 'chargePort', 'tonneau')
    FRONTDRIVERDOOR_FIELD_NUMBER: _ClassVar[int]
    FRONTPASSENGERDOOR_FIELD_NUMBER: _ClassVar[int]
    REARDRIVERDOOR_FIELD_NUMBER: _ClassVar[int]
    REARPASSENGERDOOR_FIELD_NUMBER: _ClassVar[int]
    REARTRUNK_FIELD_NUMBER: _ClassVar[int]
    FRONTTRUNK_FIELD_NUMBER: _ClassVar[int]
    CHARGEPORT_FIELD_NUMBER: _ClassVar[int]
    TONNEAU_FIELD_NUMBER: _ClassVar[int]
    frontDriverDoor: ClosureMoveType_E
    frontPassengerDoor: ClosureMoveType_E
    rearDriverDoor: ClosureMoveType_E
    rearPassengerDoor: ClosureMoveType_E
    rearTrunk: ClosureMoveType_E
    frontTrunk: ClosureMoveType_E
    chargePort: ClosureMoveType_E
    tonneau: ClosureMoveType_E

    def __init__(self, frontDriverDoor: _Optional[_Union[ClosureMoveType_E, str]]=..., frontPassengerDoor: _Optional[_Union[ClosureMoveType_E, str]]=..., rearDriverDoor: _Optional[_Union[ClosureMoveType_E, str]]=..., rearPassengerDoor: _Optional[_Union[ClosureMoveType_E, str]]=..., rearTrunk: _Optional[_Union[ClosureMoveType_E, str]]=..., frontTrunk: _Optional[_Union[ClosureMoveType_E, str]]=..., chargePort: _Optional[_Union[ClosureMoveType_E, str]]=..., tonneau: _Optional[_Union[ClosureMoveType_E, str]]=...) -> None:
        ...

class PermissionChange(_message.Message):
    __slots__ = ('key', 'secondsToBeActive', 'keyRole')
    KEY_FIELD_NUMBER: _ClassVar[int]
    SECONDSTOBEACTIVE_FIELD_NUMBER: _ClassVar[int]
    KEYROLE_FIELD_NUMBER: _ClassVar[int]
    key: PublicKey
    secondsToBeActive: int
    keyRole: _keys_pb2.Role

    def __init__(self, key: _Optional[_Union[PublicKey, _Mapping]]=..., secondsToBeActive: _Optional[int]=..., keyRole: _Optional[_Union[_keys_pb2.Role, str]]=...) -> None:
        ...

class ReplaceKey(_message.Message):
    __slots__ = ('publicKeyToReplace', 'slotToReplace', 'keyToAdd', 'keyRole', 'impermanent')
    PUBLICKEYTOREPLACE_FIELD_NUMBER: _ClassVar[int]
    SLOTTOREPLACE_FIELD_NUMBER: _ClassVar[int]
    KEYTOADD_FIELD_NUMBER: _ClassVar[int]
    KEYROLE_FIELD_NUMBER: _ClassVar[int]
    IMPERMANENT_FIELD_NUMBER: _ClassVar[int]
    publicKeyToReplace: PublicKey
    slotToReplace: int
    keyToAdd: PublicKey
    keyRole: _keys_pb2.Role
    impermanent: bool

    def __init__(self, publicKeyToReplace: _Optional[_Union[PublicKey, _Mapping]]=..., slotToReplace: _Optional[int]=..., keyToAdd: _Optional[_Union[PublicKey, _Mapping]]=..., keyRole: _Optional[_Union[_keys_pb2.Role, str]]=..., impermanent: bool=...) -> None:
        ...

class WhitelistOperation(_message.Message):
    __slots__ = ('addPublicKeyToWhitelist', 'removePublicKeyFromWhitelist', 'addPermissionsToPublicKey', 'removePermissionsFromPublicKey', 'addKeyToWhitelistAndAddPermissions', 'updateKeyAndPermissions', 'addImpermanentKey', 'addImpermanentKeyAndRemoveExisting', 'removeAllImpermanentKeys', 'replaceKey', 'metadataForKey')
    ADDPUBLICKEYTOWHITELIST_FIELD_NUMBER: _ClassVar[int]
    REMOVEPUBLICKEYFROMWHITELIST_FIELD_NUMBER: _ClassVar[int]
    ADDPERMISSIONSTOPUBLICKEY_FIELD_NUMBER: _ClassVar[int]
    REMOVEPERMISSIONSFROMPUBLICKEY_FIELD_NUMBER: _ClassVar[int]
    ADDKEYTOWHITELISTANDADDPERMISSIONS_FIELD_NUMBER: _ClassVar[int]
    UPDATEKEYANDPERMISSIONS_FIELD_NUMBER: _ClassVar[int]
    ADDIMPERMANENTKEY_FIELD_NUMBER: _ClassVar[int]
    ADDIMPERMANENTKEYANDREMOVEEXISTING_FIELD_NUMBER: _ClassVar[int]
    REMOVEALLIMPERMANENTKEYS_FIELD_NUMBER: _ClassVar[int]
    REPLACEKEY_FIELD_NUMBER: _ClassVar[int]
    METADATAFORKEY_FIELD_NUMBER: _ClassVar[int]
    addPublicKeyToWhitelist: PublicKey
    removePublicKeyFromWhitelist: PublicKey
    addPermissionsToPublicKey: PermissionChange
    removePermissionsFromPublicKey: PermissionChange
    addKeyToWhitelistAndAddPermissions: PermissionChange
    updateKeyAndPermissions: PermissionChange
    addImpermanentKey: PermissionChange
    addImpermanentKeyAndRemoveExisting: PermissionChange
    removeAllImpermanentKeys: bool
    replaceKey: ReplaceKey
    metadataForKey: KeyMetadata

    def __init__(self, addPublicKeyToWhitelist: _Optional[_Union[PublicKey, _Mapping]]=..., removePublicKeyFromWhitelist: _Optional[_Union[PublicKey, _Mapping]]=..., addPermissionsToPublicKey: _Optional[_Union[PermissionChange, _Mapping]]=..., removePermissionsFromPublicKey: _Optional[_Union[PermissionChange, _Mapping]]=..., addKeyToWhitelistAndAddPermissions: _Optional[_Union[PermissionChange, _Mapping]]=..., updateKeyAndPermissions: _Optional[_Union[PermissionChange, _Mapping]]=..., addImpermanentKey: _Optional[_Union[PermissionChange, _Mapping]]=..., addImpermanentKeyAndRemoveExisting: _Optional[_Union[PermissionChange, _Mapping]]=..., removeAllImpermanentKeys: bool=..., replaceKey: _Optional[_Union[ReplaceKey, _Mapping]]=..., metadataForKey: _Optional[_Union[KeyMetadata, _Mapping]]=...) -> None:
        ...

class WhitelistOperation_status(_message.Message):
    __slots__ = ('whitelistOperationInformation', 'signerOfOperation', 'operationStatus')
    WHITELISTOPERATIONINFORMATION_FIELD_NUMBER: _ClassVar[int]
    SIGNEROFOPERATION_FIELD_NUMBER: _ClassVar[int]
    OPERATIONSTATUS_FIELD_NUMBER: _ClassVar[int]
    whitelistOperationInformation: WhitelistOperation_information_E
    signerOfOperation: KeyIdentifier
    operationStatus: OperationStatus_E

    def __init__(self, whitelistOperationInformation: _Optional[_Union[WhitelistOperation_information_E, str]]=..., signerOfOperation: _Optional[_Union[KeyIdentifier, _Mapping]]=..., operationStatus: _Optional[_Union[OperationStatus_E, str]]=...) -> None:
        ...

class SignedMessage_status(_message.Message):
    __slots__ = ('counter', 'signedMessageInformation')
    COUNTER_FIELD_NUMBER: _ClassVar[int]
    SIGNEDMESSAGEINFORMATION_FIELD_NUMBER: _ClassVar[int]
    counter: int
    signedMessageInformation: SignedMessage_information_E

    def __init__(self, counter: _Optional[int]=..., signedMessageInformation: _Optional[_Union[SignedMessage_information_E, str]]=...) -> None:
        ...

class CommandStatus(_message.Message):
    __slots__ = ('operationStatus', 'signedMessageStatus', 'whitelistOperationStatus')
    OPERATIONSTATUS_FIELD_NUMBER: _ClassVar[int]
    SIGNEDMESSAGESTATUS_FIELD_NUMBER: _ClassVar[int]
    WHITELISTOPERATIONSTATUS_FIELD_NUMBER: _ClassVar[int]
    operationStatus: OperationStatus_E
    signedMessageStatus: SignedMessage_status
    whitelistOperationStatus: WhitelistOperation_status

    def __init__(self, operationStatus: _Optional[_Union[OperationStatus_E, str]]=..., signedMessageStatus: _Optional[_Union[SignedMessage_status, _Mapping]]=..., whitelistOperationStatus: _Optional[_Union[WhitelistOperation_status, _Mapping]]=...) -> None:
        ...

class UnsignedMessage(_message.Message):
    __slots__ = ('InformationRequest', 'RKEAction', 'closureMoveRequest', 'WhitelistOperation')
    INFORMATIONREQUEST_FIELD_NUMBER: _ClassVar[int]
    RKEACTION_FIELD_NUMBER: _ClassVar[int]
    CLOSUREMOVEREQUEST_FIELD_NUMBER: _ClassVar[int]
    WHITELISTOPERATION_FIELD_NUMBER: _ClassVar[int]
    InformationRequest: InformationRequest
    RKEAction: RKEAction_E
    closureMoveRequest: ClosureMoveRequest
    WhitelistOperation: WhitelistOperation

    def __init__(self, InformationRequest: _Optional[_Union[InformationRequest, _Mapping]]=..., RKEAction: _Optional[_Union[RKEAction_E, str]]=..., closureMoveRequest: _Optional[_Union[ClosureMoveRequest, _Mapping]]=..., WhitelistOperation: _Optional[_Union[WhitelistOperation, _Mapping]]=...) -> None:
        ...

class ClosureStatuses(_message.Message):
    __slots__ = ('frontDriverDoor', 'frontPassengerDoor', 'rearDriverDoor', 'rearPassengerDoor', 'rearTrunk', 'frontTrunk', 'chargePort', 'tonneau')
    FRONTDRIVERDOOR_FIELD_NUMBER: _ClassVar[int]
    FRONTPASSENGERDOOR_FIELD_NUMBER: _ClassVar[int]
    REARDRIVERDOOR_FIELD_NUMBER: _ClassVar[int]
    REARPASSENGERDOOR_FIELD_NUMBER: _ClassVar[int]
    REARTRUNK_FIELD_NUMBER: _ClassVar[int]
    FRONTTRUNK_FIELD_NUMBER: _ClassVar[int]
    CHARGEPORT_FIELD_NUMBER: _ClassVar[int]
    TONNEAU_FIELD_NUMBER: _ClassVar[int]
    frontDriverDoor: ClosureState_E
    frontPassengerDoor: ClosureState_E
    rearDriverDoor: ClosureState_E
    rearPassengerDoor: ClosureState_E
    rearTrunk: ClosureState_E
    frontTrunk: ClosureState_E
    chargePort: ClosureState_E
    tonneau: ClosureState_E

    def __init__(self, frontDriverDoor: _Optional[_Union[ClosureState_E, str]]=..., frontPassengerDoor: _Optional[_Union[ClosureState_E, str]]=..., rearDriverDoor: _Optional[_Union[ClosureState_E, str]]=..., rearPassengerDoor: _Optional[_Union[ClosureState_E, str]]=..., rearTrunk: _Optional[_Union[ClosureState_E, str]]=..., frontTrunk: _Optional[_Union[ClosureState_E, str]]=..., chargePort: _Optional[_Union[ClosureState_E, str]]=..., tonneau: _Optional[_Union[ClosureState_E, str]]=...) -> None:
        ...

class DetailedClosureStatus(_message.Message):
    __slots__ = ('tonneauPercentOpen',)
    TONNEAUPERCENTOPEN_FIELD_NUMBER: _ClassVar[int]
    tonneauPercentOpen: int

    def __init__(self, tonneauPercentOpen: _Optional[int]=...) -> None:
        ...

class VehicleStatus(_message.Message):
    __slots__ = ('closureStatuses', 'vehicleLockState', 'vehicleSleepStatus', 'userPresence', 'detailedClosureStatus')
    CLOSURESTATUSES_FIELD_NUMBER: _ClassVar[int]
    VEHICLELOCKSTATE_FIELD_NUMBER: _ClassVar[int]
    VEHICLESLEEPSTATUS_FIELD_NUMBER: _ClassVar[int]
    USERPRESENCE_FIELD_NUMBER: _ClassVar[int]
    DETAILEDCLOSURESTATUS_FIELD_NUMBER: _ClassVar[int]
    closureStatuses: ClosureStatuses
    vehicleLockState: VehicleLockState_E
    vehicleSleepStatus: VehicleSleepStatus_E
    userPresence: UserPresence_E
    detailedClosureStatus: DetailedClosureStatus

    def __init__(self, closureStatuses: _Optional[_Union[ClosureStatuses, _Mapping]]=..., vehicleLockState: _Optional[_Union[VehicleLockState_E, str]]=..., vehicleSleepStatus: _Optional[_Union[VehicleSleepStatus_E, str]]=..., userPresence: _Optional[_Union[UserPresence_E, str]]=..., detailedClosureStatus: _Optional[_Union[DetailedClosureStatus, _Mapping]]=...) -> None:
        ...

class FromVCSECMessage(_message.Message):
    __slots__ = ('vehicleStatus', 'commandStatus', 'whitelistInfo', 'whitelistEntryInfo', 'nominalError')
    VEHICLESTATUS_FIELD_NUMBER: _ClassVar[int]
    COMMANDSTATUS_FIELD_NUMBER: _ClassVar[int]
    WHITELISTINFO_FIELD_NUMBER: _ClassVar[int]
    WHITELISTENTRYINFO_FIELD_NUMBER: _ClassVar[int]
    NOMINALERROR_FIELD_NUMBER: _ClassVar[int]
    vehicleStatus: VehicleStatus
    commandStatus: CommandStatus
    whitelistInfo: WhitelistInfo
    whitelistEntryInfo: WhitelistEntryInfo
    nominalError: _errors_pb2.NominalError

    def __init__(self, vehicleStatus: _Optional[_Union[VehicleStatus, _Mapping]]=..., commandStatus: _Optional[_Union[CommandStatus, _Mapping]]=..., whitelistInfo: _Optional[_Union[WhitelistInfo, _Mapping]]=..., whitelistEntryInfo: _Optional[_Union[WhitelistEntryInfo, _Mapping]]=..., nominalError: _Optional[_Union[_errors_pb2.NominalError, _Mapping]]=...) -> None:
        ...