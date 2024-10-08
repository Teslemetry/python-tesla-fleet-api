"""Generated protocol buffer code."""
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from . import keys_pb2 as keys__pb2
from . import errors_pb2 as errors__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0bvcsec.proto\x12\x05VCSEC\x1a\nkeys.proto\x1a\x0cerrors.proto"\\\n\rSignedMessage\x12\x1e\n\x16protobufMessageAsBytes\x18\x02 \x01(\x0c\x12+\n\rsignatureType\x18\x03 \x01(\x0e2\x14.VCSEC.SignatureType"=\n\x0eToVCSECMessage\x12+\n\rsignedMessage\x18\x01 \x01(\x0b2\x14.VCSEC.SignedMessage"&\n\rKeyIdentifier\x12\x15\n\rpublicKeySHA1\x18\x01 \x01(\x0c":\n\x0bKeyMetadata\x12+\n\rkeyFormFactor\x18\x01 \x01(\x0e2\x14.VCSEC.KeyFormFactor"!\n\tPublicKey\x12\x14\n\x0cPublicKeyRaw\x18\x01 \x01(\x0c"j\n\rWhitelistInfo\x12\x17\n\x0fnumberOfEntries\x18\x01 \x01(\r\x12.\n\x10whitelistEntries\x18\x02 \x03(\x0b2\x14.VCSEC.KeyIdentifier\x12\x10\n\x08slotMask\x18\x03 \x01(\r"\xb5\x01\n\x12WhitelistEntryInfo\x12#\n\x05keyId\x18\x01 \x01(\x0b2\x14.VCSEC.KeyIdentifier\x12#\n\tpublicKey\x18\x02 \x01(\x0b2\x10.VCSEC.PublicKey\x12*\n\x0emetadataForKey\x18\x04 \x01(\x0b2\x12.VCSEC.KeyMetadata\x12\x0c\n\x04slot\x18\x06 \x01(\r\x12\x1b\n\x07keyRole\x18\x07 \x01(\x0e2\n.Keys.Role"\xa6\x01\n\x12InformationRequest\x12=\n\x16informationRequestType\x18\x01 \x01(\x0e2\x1d.VCSEC.InformationRequestType\x12%\n\x05keyId\x18\x02 \x01(\x0b2\x14.VCSEC.KeyIdentifierH\x00\x12\x13\n\tpublicKey\x18\x03 \x01(\x0cH\x00\x12\x0e\n\x04slot\x18\x04 \x01(\rH\x00B\x05\n\x03key"\x98\x03\n\x12ClosureMoveRequest\x121\n\x0ffrontDriverDoor\x18\x01 \x01(\x0e2\x18.VCSEC.ClosureMoveType_E\x124\n\x12frontPassengerDoor\x18\x02 \x01(\x0e2\x18.VCSEC.ClosureMoveType_E\x120\n\x0erearDriverDoor\x18\x03 \x01(\x0e2\x18.VCSEC.ClosureMoveType_E\x123\n\x11rearPassengerDoor\x18\x04 \x01(\x0e2\x18.VCSEC.ClosureMoveType_E\x12+\n\trearTrunk\x18\x05 \x01(\x0e2\x18.VCSEC.ClosureMoveType_E\x12,\n\nfrontTrunk\x18\x06 \x01(\x0e2\x18.VCSEC.ClosureMoveType_E\x12,\n\nchargePort\x18\x07 \x01(\x0e2\x18.VCSEC.ClosureMoveType_E\x12)\n\x07tonneau\x18\x08 \x01(\x0e2\x18.VCSEC.ClosureMoveType_E"i\n\x10PermissionChange\x12\x1d\n\x03key\x18\x01 \x01(\x0b2\x10.VCSEC.PublicKey\x12\x19\n\x11secondsToBeActive\x18\x03 \x01(\r\x12\x1b\n\x07keyRole\x18\x04 \x01(\x0e2\n.Keys.Role"\xbb\x01\n\nReplaceKey\x12.\n\x12publicKeyToReplace\x18\x01 \x01(\x0b2\x10.VCSEC.PublicKeyH\x00\x12\x17\n\rslotToReplace\x18\x02 \x01(\rH\x00\x12"\n\x08keyToAdd\x18\x03 \x01(\x0b2\x10.VCSEC.PublicKey\x12\x1b\n\x07keyRole\x18\x04 \x01(\x0e2\n.Keys.Role\x12\x13\n\x0bimpermanent\x18\x05 \x01(\x08B\x0e\n\x0ckeyToReplace"\x8c\x05\n\x12WhitelistOperation\x123\n\x17addPublicKeyToWhitelist\x18\x01 \x01(\x0b2\x10.VCSEC.PublicKeyH\x00\x128\n\x1cremovePublicKeyFromWhitelist\x18\x02 \x01(\x0b2\x10.VCSEC.PublicKeyH\x00\x12<\n\x19addPermissionsToPublicKey\x18\x03 \x01(\x0b2\x17.VCSEC.PermissionChangeH\x00\x12A\n\x1eremovePermissionsFromPublicKey\x18\x04 \x01(\x0b2\x17.VCSEC.PermissionChangeH\x00\x12E\n"addKeyToWhitelistAndAddPermissions\x18\x05 \x01(\x0b2\x17.VCSEC.PermissionChangeH\x00\x12:\n\x17updateKeyAndPermissions\x18\x07 \x01(\x0b2\x17.VCSEC.PermissionChangeH\x00\x124\n\x11addImpermanentKey\x18\x08 \x01(\x0b2\x17.VCSEC.PermissionChangeH\x00\x12E\n"addImpermanentKeyAndRemoveExisting\x18\t \x01(\x0b2\x17.VCSEC.PermissionChangeH\x00\x12"\n\x18removeAllImpermanentKeys\x18\x10 \x01(\x08H\x00\x12\'\n\nreplaceKey\x18\x11 \x01(\x0b2\x11.VCSEC.ReplaceKeyH\x00\x12*\n\x0emetadataForKey\x18\x06 \x01(\x0b2\x12.VCSEC.KeyMetadataB\r\n\x0bsub_message"\xcf\x01\n\x19WhitelistOperation_status\x12N\n\x1dwhitelistOperationInformation\x18\x01 \x01(\x0e2\'.VCSEC.WhitelistOperation_information_E\x12/\n\x11signerOfOperation\x18\x02 \x01(\x0b2\x14.VCSEC.KeyIdentifier\x121\n\x0foperationStatus\x18\x03 \x01(\x0e2\x18.VCSEC.OperationStatus_E"m\n\x14SignedMessage_status\x12\x0f\n\x07counter\x18\x01 \x01(\r\x12D\n\x18signedMessageInformation\x18\x02 \x01(\x0e2".VCSEC.SignedMessage_information_E"\xd3\x01\n\rCommandStatus\x121\n\x0foperationStatus\x18\x01 \x01(\x0e2\x18.VCSEC.OperationStatus_E\x12:\n\x13signedMessageStatus\x18\x02 \x01(\x0b2\x1b.VCSEC.SignedMessage_statusH\x00\x12D\n\x18whitelistOperationStatus\x18\x03 \x01(\x0b2 .VCSEC.WhitelistOperation_statusH\x00B\r\n\x0bsub_message"\x92\x02\n\x0fUnsignedMessage\x127\n\x12InformationRequest\x18\x01 \x01(\x0b2\x19.VCSEC.InformationRequestH\x00\x12\'\n\tRKEAction\x18\x02 \x01(\x0e2\x12.VCSEC.RKEAction_EH\x00\x127\n\x12closureMoveRequest\x18\x04 \x01(\x0b2\x19.VCSEC.ClosureMoveRequestH\x00\x127\n\x12WhitelistOperation\x18\x10 \x01(\x0b2\x19.VCSEC.WhitelistOperationH\x00B\r\n\x0bsub_messageJ\x04\x08\x06\x10\x07J\x04\x08\x07\x10\x08J\x04\x08\n\x10\x0bJ\x04\x08\x0c\x10\rJ\x04\x08\r\x10\x0e"\xfd\x02\n\x0fClosureStatuses\x12.\n\x0ffrontDriverDoor\x18\x01 \x01(\x0e2\x15.VCSEC.ClosureState_E\x121\n\x12frontPassengerDoor\x18\x02 \x01(\x0e2\x15.VCSEC.ClosureState_E\x12-\n\x0erearDriverDoor\x18\x03 \x01(\x0e2\x15.VCSEC.ClosureState_E\x120\n\x11rearPassengerDoor\x18\x04 \x01(\x0e2\x15.VCSEC.ClosureState_E\x12(\n\trearTrunk\x18\x05 \x01(\x0e2\x15.VCSEC.ClosureState_E\x12)\n\nfrontTrunk\x18\x06 \x01(\x0e2\x15.VCSEC.ClosureState_E\x12)\n\nchargePort\x18\x07 \x01(\x0e2\x15.VCSEC.ClosureState_E\x12&\n\x07tonneau\x18\x08 \x01(\x0e2\x15.VCSEC.ClosureState_E"3\n\x15DetailedClosureStatus\x12\x1a\n\x12tonneauPercentOpen\x18\x01 \x01(\r"\x98\x02\n\rVehicleStatus\x12/\n\x0fclosureStatuses\x18\x01 \x01(\x0b2\x16.VCSEC.ClosureStatuses\x123\n\x10vehicleLockState\x18\x02 \x01(\x0e2\x19.VCSEC.VehicleLockState_E\x127\n\x12vehicleSleepStatus\x18\x03 \x01(\x0e2\x1b.VCSEC.VehicleSleepStatus_E\x12+\n\x0cuserPresence\x18\x04 \x01(\x0e2\x15.VCSEC.UserPresence_E\x12;\n\x15detailedClosureStatus\x18\x05 \x01(\x0b2\x1c.VCSEC.DetailedClosureStatus"\x9b\x02\n\x10FromVCSECMessage\x12-\n\rvehicleStatus\x18\x01 \x01(\x0b2\x14.VCSEC.VehicleStatusH\x00\x12-\n\rcommandStatus\x18\x04 \x01(\x0b2\x14.VCSEC.CommandStatusH\x00\x12-\n\rwhitelistInfo\x18\x10 \x01(\x0b2\x14.VCSEC.WhitelistInfoH\x00\x127\n\x12whitelistEntryInfo\x18\x11 \x01(\x0b2\x19.VCSEC.WhitelistEntryInfoH\x00\x12,\n\x0cnominalError\x18. \x01(\x0b2\x14.Errors.NominalErrorH\x00B\r\n\x0bsub_messageJ\x04\x08\x06\x10\x0b*H\n\rSignatureType\x12\x17\n\x13SIGNATURE_TYPE_NONE\x10\x00\x12\x1e\n\x1aSIGNATURE_TYPE_PRESENT_KEY\x10\x02*\xad\x01\n\rKeyFormFactor\x12\x1b\n\x17KEY_FORM_FACTOR_UNKNOWN\x10\x00\x12\x1c\n\x18KEY_FORM_FACTOR_NFC_CARD\x10\x01\x12\x1e\n\x1aKEY_FORM_FACTOR_IOS_DEVICE\x10\x06\x12"\n\x1eKEY_FORM_FACTOR_ANDROID_DEVICE\x10\x07\x12\x1d\n\x19KEY_FORM_FACTOR_CLOUD_KEY\x10\t*\xa9\x01\n\x16InformationRequestType\x12\'\n#INFORMATION_REQUEST_TYPE_GET_STATUS\x10\x00\x12/\n+INFORMATION_REQUEST_TYPE_GET_WHITELIST_INFO\x10\x05\x125\n1INFORMATION_REQUEST_TYPE_GET_WHITELIST_ENTRY_INFO\x10\x06*\x97\x01\n\x0bRKEAction_E\x12\x15\n\x11RKE_ACTION_UNLOCK\x10\x00\x12\x13\n\x0fRKE_ACTION_LOCK\x10\x01\x12\x1b\n\x17RKE_ACTION_REMOTE_DRIVE\x10\x14\x12"\n\x1eRKE_ACTION_AUTO_SECURE_VEHICLE\x10\x1d\x12\x1b\n\x17RKE_ACTION_WAKE_VEHICLE\x10\x1e*\xa0\x01\n\x11ClosureMoveType_E\x12\x1a\n\x16CLOSURE_MOVE_TYPE_NONE\x10\x00\x12\x1a\n\x16CLOSURE_MOVE_TYPE_MOVE\x10\x01\x12\x1a\n\x16CLOSURE_MOVE_TYPE_STOP\x10\x02\x12\x1a\n\x16CLOSURE_MOVE_TYPE_OPEN\x10\x03\x12\x1b\n\x17CLOSURE_MOVE_TYPE_CLOSE\x10\x04*`\n\x11OperationStatus_E\x12\x16\n\x12OPERATIONSTATUS_OK\x10\x00\x12\x18\n\x14OPERATIONSTATUS_WAIT\x10\x01\x12\x19\n\x15OPERATIONSTATUS_ERROR\x10\x02*\xf3\x08\n\x1bSignedMessage_information_E\x12"\n\x1eSIGNEDMESSAGE_INFORMATION_NONE\x10\x00\x12+\n\'SIGNEDMESSAGE_INFORMATION_FAULT_UNKNOWN\x10\x01\x124\n0SIGNEDMESSAGE_INFORMATION_FAULT_NOT_ON_WHITELIST\x10\x02\x12<\n8SIGNEDMESSAGE_INFORMATION_FAULT_IV_SMALLER_THAN_EXPECTED\x10\x03\x121\n-SIGNEDMESSAGE_INFORMATION_FAULT_INVALID_TOKEN\x10\x04\x12=\n9SIGNEDMESSAGE_INFORMATION_FAULT_TOKEN_AND_COUNTER_INVALID\x10\x05\x124\n0SIGNEDMESSAGE_INFORMATION_FAULT_AES_DECRYPT_AUTH\x10\x06\x12/\n+SIGNEDMESSAGE_INFORMATION_FAULT_ECDSA_INPUT\x10\x07\x123\n/SIGNEDMESSAGE_INFORMATION_FAULT_ECDSA_SIGNATURE\x10\x08\x126\n2SIGNEDMESSAGE_INFORMATION_FAULT_LOCAL_ENTITY_START\x10\t\x127\n3SIGNEDMESSAGE_INFORMATION_FAULT_LOCAL_ENTITY_RESULT\x10\n\x12:\n6SIGNEDMESSAGE_INFORMATION_FAULT_COULD_NOT_RETRIEVE_KEY\x10\x0b\x12<\n8SIGNEDMESSAGE_INFORMATION_FAULT_COULD_NOT_RETRIEVE_TOKEN\x10\x0c\x127\n3SIGNEDMESSAGE_INFORMATION_FAULT_SIGNATURE_TOO_SHORT\x10\r\x12=\n9SIGNEDMESSAGE_INFORMATION_FAULT_TOKEN_IS_INCORRECT_LENGTH\x10\x0e\x123\n/SIGNEDMESSAGE_INFORMATION_FAULT_INCORRECT_EPOCH\x10\x0f\x127\n3SIGNEDMESSAGE_INFORMATION_FAULT_IV_INCORRECT_LENGTH\x10\x10\x120\n,SIGNEDMESSAGE_INFORMATION_FAULT_TIME_EXPIRED\x10\x11\x12A\n=SIGNEDMESSAGE_INFORMATION_FAULT_NOT_PROVISIONED_WITH_IDENTITY\x10\x12\x12;\n7SIGNEDMESSAGE_INFORMATION_FAULT_COULD_NOT_HASH_METADATA\x10\x13*\xc3\x0c\n WhitelistOperation_information_E\x12\'\n#WHITELISTOPERATION_INFORMATION_NONE\x10\x00\x125\n1WHITELISTOPERATION_INFORMATION_UNDOCUMENTED_ERROR\x10\x01\x12B\n>WHITELISTOPERATION_INFORMATION_NO_PERMISSION_TO_REMOVE_ONESELF\x10\x02\x124\n0WHITELISTOPERATION_INFORMATION_KEYFOB_SLOTS_FULL\x10\x03\x121\n-WHITELISTOPERATION_INFORMATION_WHITELIST_FULL\x10\x04\x127\n3WHITELISTOPERATION_INFORMATION_NO_PERMISSION_TO_ADD\x10\x05\x125\n1WHITELISTOPERATION_INFORMATION_INVALID_PUBLIC_KEY\x10\x06\x12:\n6WHITELISTOPERATION_INFORMATION_NO_PERMISSION_TO_REMOVE\x10\x07\x12F\nBWHITELISTOPERATION_INFORMATION_NO_PERMISSION_TO_CHANGE_PERMISSIONS\x10\x08\x12L\nHWHITELISTOPERATION_INFORMATION_ATTEMPTING_TO_ELEVATE_OTHER_ABOVE_ONESELF\x10\t\x12K\nGWHITELISTOPERATION_INFORMATION_ATTEMPTING_TO_DEMOTE_SUPERIOR_TO_ONESELF\x10\n\x12G\nCWHITELISTOPERATION_INFORMATION_ATTEMPTING_TO_REMOVE_OWN_PERMISSIONS\x10\x0b\x12>\n:WHITELISTOPERATION_INFORMATION_PUBLIC_KEY_NOT_ON_WHITELIST\x10\x0c\x12Y\nUWHITELISTOPERATION_INFORMATION_ATTEMPTING_TO_ADD_KEY_THAT_IS_ALREADY_ON_THE_WHITELIST\x10\r\x12F\nBWHITELISTOPERATION_INFORMATION_NOT_ALLOWED_TO_ADD_UNLESS_ON_READER\x10\x0e\x12A\n=WHITELISTOPERATION_INFORMATION_FM_MODIFYING_OUTSIDE_OF_F_MODE\x10\x0f\x12E\nAWHITELISTOPERATION_INFORMATION_FM_ATTEMPTING_TO_ADD_PERMANENT_KEY\x10\x10\x12H\nDWHITELISTOPERATION_INFORMATION_FM_ATTEMPTING_TO_REMOVE_PERMANENT_KEY\x10\x11\x129\n5WHITELISTOPERATION_INFORMATION_KEYCHAIN_WHILE_FS_FULL\x10\x12\x12E\nAWHITELISTOPERATION_INFORMATION_ATTEMPTING_TO_ADD_KEY_WITHOUT_ROLE\x10\x13\x12J\nFWHITELISTOPERATION_INFORMATION_ATTEMPTING_TO_ADD_KEY_WITH_SERVICE_ROLE\x10\x14\x12Q\nMWHITELISTOPERATION_INFORMATION_NON_SERVICE_KEY_ATTEMPTING_TO_ADD_SERVICE_TECH\x10\x15\x12b\n^WHITELISTOPERATION_INFORMATION_SERVICE_KEY_ATTEMPTING_TO_ADD_SERVICE_TECH_OUTSIDE_SERVICE_MODE\x10\x16*\xc6\x01\n\x0eClosureState_E\x12\x17\n\x13CLOSURESTATE_CLOSED\x10\x00\x12\x15\n\x11CLOSURESTATE_OPEN\x10\x01\x12\x15\n\x11CLOSURESTATE_AJAR\x10\x02\x12\x18\n\x14CLOSURESTATE_UNKNOWN\x10\x03\x12\x1f\n\x1bCLOSURESTATE_FAILED_UNLATCH\x10\x04\x12\x18\n\x14CLOSURESTATE_OPENING\x10\x05\x12\x18\n\x14CLOSURESTATE_CLOSING\x10\x06*\x9f\x01\n\x12VehicleLockState_E\x12\x1d\n\x19VEHICLELOCKSTATE_UNLOCKED\x10\x00\x12\x1b\n\x17VEHICLELOCKSTATE_LOCKED\x10\x01\x12$\n VEHICLELOCKSTATE_INTERNAL_LOCKED\x10\x02\x12\'\n#VEHICLELOCKSTATE_SELECTIVE_UNLOCKED\x10\x03*y\n\x14VehicleSleepStatus_E\x12 \n\x1cVEHICLE_SLEEP_STATUS_UNKNOWN\x10\x00\x12\x1e\n\x1aVEHICLE_SLEEP_STATUS_AWAKE\x10\x01\x12\x1f\n\x1bVEHICLE_SLEEP_STATUS_ASLEEP\x10\x02*}\n\x0eUserPresence_E\x12!\n\x1dVEHICLE_USER_PRESENCE_UNKNOWN\x10\x00\x12%\n!VEHICLE_USER_PRESENCE_NOT_PRESENT\x10\x01\x12!\n\x1dVEHICLE_USER_PRESENCE_PRESENT\x10\x02B_\n\x19com.tesla.generated.vcsecZBgithub.com/teslamotors/vehicle-command/pkg/protocol/protobuf/vcsecb\x06proto3')
_SIGNATURETYPE = DESCRIPTOR.enum_types_by_name['SignatureType']
SignatureType = enum_type_wrapper.EnumTypeWrapper(_SIGNATURETYPE)
_KEYFORMFACTOR = DESCRIPTOR.enum_types_by_name['KeyFormFactor']
KeyFormFactor = enum_type_wrapper.EnumTypeWrapper(_KEYFORMFACTOR)
_INFORMATIONREQUESTTYPE = DESCRIPTOR.enum_types_by_name['InformationRequestType']
InformationRequestType = enum_type_wrapper.EnumTypeWrapper(_INFORMATIONREQUESTTYPE)
_RKEACTION_E = DESCRIPTOR.enum_types_by_name['RKEAction_E']
RKEAction_E = enum_type_wrapper.EnumTypeWrapper(_RKEACTION_E)
_CLOSUREMOVETYPE_E = DESCRIPTOR.enum_types_by_name['ClosureMoveType_E']
ClosureMoveType_E = enum_type_wrapper.EnumTypeWrapper(_CLOSUREMOVETYPE_E)
_OPERATIONSTATUS_E = DESCRIPTOR.enum_types_by_name['OperationStatus_E']
OperationStatus_E = enum_type_wrapper.EnumTypeWrapper(_OPERATIONSTATUS_E)
_SIGNEDMESSAGE_INFORMATION_E = DESCRIPTOR.enum_types_by_name['SignedMessage_information_E']
SignedMessage_information_E = enum_type_wrapper.EnumTypeWrapper(_SIGNEDMESSAGE_INFORMATION_E)
_WHITELISTOPERATION_INFORMATION_E = DESCRIPTOR.enum_types_by_name['WhitelistOperation_information_E']
WhitelistOperation_information_E = enum_type_wrapper.EnumTypeWrapper(_WHITELISTOPERATION_INFORMATION_E)
_CLOSURESTATE_E = DESCRIPTOR.enum_types_by_name['ClosureState_E']
ClosureState_E = enum_type_wrapper.EnumTypeWrapper(_CLOSURESTATE_E)
_VEHICLELOCKSTATE_E = DESCRIPTOR.enum_types_by_name['VehicleLockState_E']
VehicleLockState_E = enum_type_wrapper.EnumTypeWrapper(_VEHICLELOCKSTATE_E)
_VEHICLESLEEPSTATUS_E = DESCRIPTOR.enum_types_by_name['VehicleSleepStatus_E']
VehicleSleepStatus_E = enum_type_wrapper.EnumTypeWrapper(_VEHICLESLEEPSTATUS_E)
_USERPRESENCE_E = DESCRIPTOR.enum_types_by_name['UserPresence_E']
UserPresence_E = enum_type_wrapper.EnumTypeWrapper(_USERPRESENCE_E)
SIGNATURE_TYPE_NONE = 0
SIGNATURE_TYPE_PRESENT_KEY = 2
KEY_FORM_FACTOR_UNKNOWN = 0
KEY_FORM_FACTOR_NFC_CARD = 1
KEY_FORM_FACTOR_IOS_DEVICE = 6
KEY_FORM_FACTOR_ANDROID_DEVICE = 7
KEY_FORM_FACTOR_CLOUD_KEY = 9
INFORMATION_REQUEST_TYPE_GET_STATUS = 0
INFORMATION_REQUEST_TYPE_GET_WHITELIST_INFO = 5
INFORMATION_REQUEST_TYPE_GET_WHITELIST_ENTRY_INFO = 6
RKE_ACTION_UNLOCK = 0
RKE_ACTION_LOCK = 1
RKE_ACTION_REMOTE_DRIVE = 20
RKE_ACTION_AUTO_SECURE_VEHICLE = 29
RKE_ACTION_WAKE_VEHICLE = 30
CLOSURE_MOVE_TYPE_NONE = 0
CLOSURE_MOVE_TYPE_MOVE = 1
CLOSURE_MOVE_TYPE_STOP = 2
CLOSURE_MOVE_TYPE_OPEN = 3
CLOSURE_MOVE_TYPE_CLOSE = 4
OPERATIONSTATUS_OK = 0
OPERATIONSTATUS_WAIT = 1
OPERATIONSTATUS_ERROR = 2
SIGNEDMESSAGE_INFORMATION_NONE = 0
SIGNEDMESSAGE_INFORMATION_FAULT_UNKNOWN = 1
SIGNEDMESSAGE_INFORMATION_FAULT_NOT_ON_WHITELIST = 2
SIGNEDMESSAGE_INFORMATION_FAULT_IV_SMALLER_THAN_EXPECTED = 3
SIGNEDMESSAGE_INFORMATION_FAULT_INVALID_TOKEN = 4
SIGNEDMESSAGE_INFORMATION_FAULT_TOKEN_AND_COUNTER_INVALID = 5
SIGNEDMESSAGE_INFORMATION_FAULT_AES_DECRYPT_AUTH = 6
SIGNEDMESSAGE_INFORMATION_FAULT_ECDSA_INPUT = 7
SIGNEDMESSAGE_INFORMATION_FAULT_ECDSA_SIGNATURE = 8
SIGNEDMESSAGE_INFORMATION_FAULT_LOCAL_ENTITY_START = 9
SIGNEDMESSAGE_INFORMATION_FAULT_LOCAL_ENTITY_RESULT = 10
SIGNEDMESSAGE_INFORMATION_FAULT_COULD_NOT_RETRIEVE_KEY = 11
SIGNEDMESSAGE_INFORMATION_FAULT_COULD_NOT_RETRIEVE_TOKEN = 12
SIGNEDMESSAGE_INFORMATION_FAULT_SIGNATURE_TOO_SHORT = 13
SIGNEDMESSAGE_INFORMATION_FAULT_TOKEN_IS_INCORRECT_LENGTH = 14
SIGNEDMESSAGE_INFORMATION_FAULT_INCORRECT_EPOCH = 15
SIGNEDMESSAGE_INFORMATION_FAULT_IV_INCORRECT_LENGTH = 16
SIGNEDMESSAGE_INFORMATION_FAULT_TIME_EXPIRED = 17
SIGNEDMESSAGE_INFORMATION_FAULT_NOT_PROVISIONED_WITH_IDENTITY = 18
SIGNEDMESSAGE_INFORMATION_FAULT_COULD_NOT_HASH_METADATA = 19
WHITELISTOPERATION_INFORMATION_NONE = 0
WHITELISTOPERATION_INFORMATION_UNDOCUMENTED_ERROR = 1
WHITELISTOPERATION_INFORMATION_NO_PERMISSION_TO_REMOVE_ONESELF = 2
WHITELISTOPERATION_INFORMATION_KEYFOB_SLOTS_FULL = 3
WHITELISTOPERATION_INFORMATION_WHITELIST_FULL = 4
WHITELISTOPERATION_INFORMATION_NO_PERMISSION_TO_ADD = 5
WHITELISTOPERATION_INFORMATION_INVALID_PUBLIC_KEY = 6
WHITELISTOPERATION_INFORMATION_NO_PERMISSION_TO_REMOVE = 7
WHITELISTOPERATION_INFORMATION_NO_PERMISSION_TO_CHANGE_PERMISSIONS = 8
WHITELISTOPERATION_INFORMATION_ATTEMPTING_TO_ELEVATE_OTHER_ABOVE_ONESELF = 9
WHITELISTOPERATION_INFORMATION_ATTEMPTING_TO_DEMOTE_SUPERIOR_TO_ONESELF = 10
WHITELISTOPERATION_INFORMATION_ATTEMPTING_TO_REMOVE_OWN_PERMISSIONS = 11
WHITELISTOPERATION_INFORMATION_PUBLIC_KEY_NOT_ON_WHITELIST = 12
WHITELISTOPERATION_INFORMATION_ATTEMPTING_TO_ADD_KEY_THAT_IS_ALREADY_ON_THE_WHITELIST = 13
WHITELISTOPERATION_INFORMATION_NOT_ALLOWED_TO_ADD_UNLESS_ON_READER = 14
WHITELISTOPERATION_INFORMATION_FM_MODIFYING_OUTSIDE_OF_F_MODE = 15
WHITELISTOPERATION_INFORMATION_FM_ATTEMPTING_TO_ADD_PERMANENT_KEY = 16
WHITELISTOPERATION_INFORMATION_FM_ATTEMPTING_TO_REMOVE_PERMANENT_KEY = 17
WHITELISTOPERATION_INFORMATION_KEYCHAIN_WHILE_FS_FULL = 18
WHITELISTOPERATION_INFORMATION_ATTEMPTING_TO_ADD_KEY_WITHOUT_ROLE = 19
WHITELISTOPERATION_INFORMATION_ATTEMPTING_TO_ADD_KEY_WITH_SERVICE_ROLE = 20
WHITELISTOPERATION_INFORMATION_NON_SERVICE_KEY_ATTEMPTING_TO_ADD_SERVICE_TECH = 21
WHITELISTOPERATION_INFORMATION_SERVICE_KEY_ATTEMPTING_TO_ADD_SERVICE_TECH_OUTSIDE_SERVICE_MODE = 22
CLOSURESTATE_CLOSED = 0
CLOSURESTATE_OPEN = 1
CLOSURESTATE_AJAR = 2
CLOSURESTATE_UNKNOWN = 3
CLOSURESTATE_FAILED_UNLATCH = 4
CLOSURESTATE_OPENING = 5
CLOSURESTATE_CLOSING = 6
VEHICLELOCKSTATE_UNLOCKED = 0
VEHICLELOCKSTATE_LOCKED = 1
VEHICLELOCKSTATE_INTERNAL_LOCKED = 2
VEHICLELOCKSTATE_SELECTIVE_UNLOCKED = 3
VEHICLE_SLEEP_STATUS_UNKNOWN = 0
VEHICLE_SLEEP_STATUS_AWAKE = 1
VEHICLE_SLEEP_STATUS_ASLEEP = 2
VEHICLE_USER_PRESENCE_UNKNOWN = 0
VEHICLE_USER_PRESENCE_NOT_PRESENT = 1
VEHICLE_USER_PRESENCE_PRESENT = 2
_SIGNEDMESSAGE = DESCRIPTOR.message_types_by_name['SignedMessage']
_TOVCSECMESSAGE = DESCRIPTOR.message_types_by_name['ToVCSECMessage']
_KEYIDENTIFIER = DESCRIPTOR.message_types_by_name['KeyIdentifier']
_KEYMETADATA = DESCRIPTOR.message_types_by_name['KeyMetadata']
_PUBLICKEY = DESCRIPTOR.message_types_by_name['PublicKey']
_WHITELISTINFO = DESCRIPTOR.message_types_by_name['WhitelistInfo']
_WHITELISTENTRYINFO = DESCRIPTOR.message_types_by_name['WhitelistEntryInfo']
_INFORMATIONREQUEST = DESCRIPTOR.message_types_by_name['InformationRequest']
_CLOSUREMOVEREQUEST = DESCRIPTOR.message_types_by_name['ClosureMoveRequest']
_PERMISSIONCHANGE = DESCRIPTOR.message_types_by_name['PermissionChange']
_REPLACEKEY = DESCRIPTOR.message_types_by_name['ReplaceKey']
_WHITELISTOPERATION = DESCRIPTOR.message_types_by_name['WhitelistOperation']
_WHITELISTOPERATION_STATUS = DESCRIPTOR.message_types_by_name['WhitelistOperation_status']
_SIGNEDMESSAGE_STATUS = DESCRIPTOR.message_types_by_name['SignedMessage_status']
_COMMANDSTATUS = DESCRIPTOR.message_types_by_name['CommandStatus']
_UNSIGNEDMESSAGE = DESCRIPTOR.message_types_by_name['UnsignedMessage']
_CLOSURESTATUSES = DESCRIPTOR.message_types_by_name['ClosureStatuses']
_DETAILEDCLOSURESTATUS = DESCRIPTOR.message_types_by_name['DetailedClosureStatus']
_VEHICLESTATUS = DESCRIPTOR.message_types_by_name['VehicleStatus']
_FROMVCSECMESSAGE = DESCRIPTOR.message_types_by_name['FromVCSECMessage']
SignedMessage = _reflection.GeneratedProtocolMessageType('SignedMessage', (_message.Message,), {'DESCRIPTOR': _SIGNEDMESSAGE, '__module__': 'vcsec_pb2'})
_sym_db.RegisterMessage(SignedMessage)
ToVCSECMessage = _reflection.GeneratedProtocolMessageType('ToVCSECMessage', (_message.Message,), {'DESCRIPTOR': _TOVCSECMESSAGE, '__module__': 'vcsec_pb2'})
_sym_db.RegisterMessage(ToVCSECMessage)
KeyIdentifier = _reflection.GeneratedProtocolMessageType('KeyIdentifier', (_message.Message,), {'DESCRIPTOR': _KEYIDENTIFIER, '__module__': 'vcsec_pb2'})
_sym_db.RegisterMessage(KeyIdentifier)
KeyMetadata = _reflection.GeneratedProtocolMessageType('KeyMetadata', (_message.Message,), {'DESCRIPTOR': _KEYMETADATA, '__module__': 'vcsec_pb2'})
_sym_db.RegisterMessage(KeyMetadata)
PublicKey = _reflection.GeneratedProtocolMessageType('PublicKey', (_message.Message,), {'DESCRIPTOR': _PUBLICKEY, '__module__': 'vcsec_pb2'})
_sym_db.RegisterMessage(PublicKey)
WhitelistInfo = _reflection.GeneratedProtocolMessageType('WhitelistInfo', (_message.Message,), {'DESCRIPTOR': _WHITELISTINFO, '__module__': 'vcsec_pb2'})
_sym_db.RegisterMessage(WhitelistInfo)
WhitelistEntryInfo = _reflection.GeneratedProtocolMessageType('WhitelistEntryInfo', (_message.Message,), {'DESCRIPTOR': _WHITELISTENTRYINFO, '__module__': 'vcsec_pb2'})
_sym_db.RegisterMessage(WhitelistEntryInfo)
InformationRequest = _reflection.GeneratedProtocolMessageType('InformationRequest', (_message.Message,), {'DESCRIPTOR': _INFORMATIONREQUEST, '__module__': 'vcsec_pb2'})
_sym_db.RegisterMessage(InformationRequest)
ClosureMoveRequest = _reflection.GeneratedProtocolMessageType('ClosureMoveRequest', (_message.Message,), {'DESCRIPTOR': _CLOSUREMOVEREQUEST, '__module__': 'vcsec_pb2'})
_sym_db.RegisterMessage(ClosureMoveRequest)
PermissionChange = _reflection.GeneratedProtocolMessageType('PermissionChange', (_message.Message,), {'DESCRIPTOR': _PERMISSIONCHANGE, '__module__': 'vcsec_pb2'})
_sym_db.RegisterMessage(PermissionChange)
ReplaceKey = _reflection.GeneratedProtocolMessageType('ReplaceKey', (_message.Message,), {'DESCRIPTOR': _REPLACEKEY, '__module__': 'vcsec_pb2'})
_sym_db.RegisterMessage(ReplaceKey)
WhitelistOperation = _reflection.GeneratedProtocolMessageType('WhitelistOperation', (_message.Message,), {'DESCRIPTOR': _WHITELISTOPERATION, '__module__': 'vcsec_pb2'})
_sym_db.RegisterMessage(WhitelistOperation)
WhitelistOperation_status = _reflection.GeneratedProtocolMessageType('WhitelistOperation_status', (_message.Message,), {'DESCRIPTOR': _WHITELISTOPERATION_STATUS, '__module__': 'vcsec_pb2'})
_sym_db.RegisterMessage(WhitelistOperation_status)
SignedMessage_status = _reflection.GeneratedProtocolMessageType('SignedMessage_status', (_message.Message,), {'DESCRIPTOR': _SIGNEDMESSAGE_STATUS, '__module__': 'vcsec_pb2'})
_sym_db.RegisterMessage(SignedMessage_status)
CommandStatus = _reflection.GeneratedProtocolMessageType('CommandStatus', (_message.Message,), {'DESCRIPTOR': _COMMANDSTATUS, '__module__': 'vcsec_pb2'})
_sym_db.RegisterMessage(CommandStatus)
UnsignedMessage = _reflection.GeneratedProtocolMessageType('UnsignedMessage', (_message.Message,), {'DESCRIPTOR': _UNSIGNEDMESSAGE, '__module__': 'vcsec_pb2'})
_sym_db.RegisterMessage(UnsignedMessage)
ClosureStatuses = _reflection.GeneratedProtocolMessageType('ClosureStatuses', (_message.Message,), {'DESCRIPTOR': _CLOSURESTATUSES, '__module__': 'vcsec_pb2'})
_sym_db.RegisterMessage(ClosureStatuses)
DetailedClosureStatus = _reflection.GeneratedProtocolMessageType('DetailedClosureStatus', (_message.Message,), {'DESCRIPTOR': _DETAILEDCLOSURESTATUS, '__module__': 'vcsec_pb2'})
_sym_db.RegisterMessage(DetailedClosureStatus)
VehicleStatus = _reflection.GeneratedProtocolMessageType('VehicleStatus', (_message.Message,), {'DESCRIPTOR': _VEHICLESTATUS, '__module__': 'vcsec_pb2'})
_sym_db.RegisterMessage(VehicleStatus)
FromVCSECMessage = _reflection.GeneratedProtocolMessageType('FromVCSECMessage', (_message.Message,), {'DESCRIPTOR': _FROMVCSECMESSAGE, '__module__': 'vcsec_pb2'})
_sym_db.RegisterMessage(FromVCSECMessage)
if _descriptor._USE_C_DESCRIPTORS == False:
    DESCRIPTOR._options = None
    DESCRIPTOR._serialized_options = b'\n\x19com.tesla.generated.vcsecZBgithub.com/teslamotors/vehicle-command/pkg/protocol/protobuf/vcsec'
    _SIGNATURETYPE._serialized_start = 3982
    _SIGNATURETYPE._serialized_end = 4054
    _KEYFORMFACTOR._serialized_start = 4057
    _KEYFORMFACTOR._serialized_end = 4230
    _INFORMATIONREQUESTTYPE._serialized_start = 4233
    _INFORMATIONREQUESTTYPE._serialized_end = 4402
    _RKEACTION_E._serialized_start = 4405
    _RKEACTION_E._serialized_end = 4556
    _CLOSUREMOVETYPE_E._serialized_start = 4559
    _CLOSUREMOVETYPE_E._serialized_end = 4719
    _OPERATIONSTATUS_E._serialized_start = 4721
    _OPERATIONSTATUS_E._serialized_end = 4817
    _SIGNEDMESSAGE_INFORMATION_E._serialized_start = 4820
    _SIGNEDMESSAGE_INFORMATION_E._serialized_end = 5959
    _WHITELISTOPERATION_INFORMATION_E._serialized_start = 5962
    _WHITELISTOPERATION_INFORMATION_E._serialized_end = 7565
    _CLOSURESTATE_E._serialized_start = 7568
    _CLOSURESTATE_E._serialized_end = 7766
    _VEHICLELOCKSTATE_E._serialized_start = 7769
    _VEHICLELOCKSTATE_E._serialized_end = 7928
    _VEHICLESLEEPSTATUS_E._serialized_start = 7930
    _VEHICLESLEEPSTATUS_E._serialized_end = 8051
    _USERPRESENCE_E._serialized_start = 8053
    _USERPRESENCE_E._serialized_end = 8178
    _SIGNEDMESSAGE._serialized_start = 48
    _SIGNEDMESSAGE._serialized_end = 140
    _TOVCSECMESSAGE._serialized_start = 142
    _TOVCSECMESSAGE._serialized_end = 203
    _KEYIDENTIFIER._serialized_start = 205
    _KEYIDENTIFIER._serialized_end = 243
    _KEYMETADATA._serialized_start = 245
    _KEYMETADATA._serialized_end = 303
    _PUBLICKEY._serialized_start = 305
    _PUBLICKEY._serialized_end = 338
    _WHITELISTINFO._serialized_start = 340
    _WHITELISTINFO._serialized_end = 446
    _WHITELISTENTRYINFO._serialized_start = 449
    _WHITELISTENTRYINFO._serialized_end = 630
    _INFORMATIONREQUEST._serialized_start = 633
    _INFORMATIONREQUEST._serialized_end = 799
    _CLOSUREMOVEREQUEST._serialized_start = 802
    _CLOSUREMOVEREQUEST._serialized_end = 1210
    _PERMISSIONCHANGE._serialized_start = 1212
    _PERMISSIONCHANGE._serialized_end = 1317
    _REPLACEKEY._serialized_start = 1320
    _REPLACEKEY._serialized_end = 1507
    _WHITELISTOPERATION._serialized_start = 1510
    _WHITELISTOPERATION._serialized_end = 2162
    _WHITELISTOPERATION_STATUS._serialized_start = 2165
    _WHITELISTOPERATION_STATUS._serialized_end = 2372
    _SIGNEDMESSAGE_STATUS._serialized_start = 2374
    _SIGNEDMESSAGE_STATUS._serialized_end = 2483
    _COMMANDSTATUS._serialized_start = 2486
    _COMMANDSTATUS._serialized_end = 2697
    _UNSIGNEDMESSAGE._serialized_start = 2700
    _UNSIGNEDMESSAGE._serialized_end = 2974
    _CLOSURESTATUSES._serialized_start = 2977
    _CLOSURESTATUSES._serialized_end = 3358
    _DETAILEDCLOSURESTATUS._serialized_start = 3360
    _DETAILEDCLOSURESTATUS._serialized_end = 3411
    _VEHICLESTATUS._serialized_start = 3414
    _VEHICLESTATUS._serialized_end = 3694
    _FROMVCSECMESSAGE._serialized_start = 3697
    _FROMVCSECMESSAGE._serialized_end = 3980