"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x16managed_charging.proto\x12\x0fManagedCharging*\xc7\x02\n\x1bChargeOnSolarNoChargeReason\x12,\n(CHARGE_ON_SOLAR_NO_CHARGE_REASON_INVALID\x10\x00\x12>\n:CHARGE_ON_SOLAR_NO_CHARGE_REASON_POWERWALL_CHARGE_PRIORITY\x10\x01\x127\n3CHARGE_ON_SOLAR_NO_CHARGE_REASON_INSUFFICIENT_SOLAR\x10\x02\x129\n5CHARGE_ON_SOLAR_NO_CHARGE_REASON_GRID_EXPORT_PRIORITY\x10\x03\x12F\nBCHARGE_ON_SOLAR_NO_CHARGE_REASON_ALTERNATE_VEHICLE_CHARGE_PRIORITY\x10\x04BNZLgithub.com/teslamotors/vehicle-command/pkg/protocol/protobuf/managedchargingb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'managed_charging_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    _globals['DESCRIPTOR']._options = None
    _globals['DESCRIPTOR']._serialized_options = b'ZLgithub.com/teslamotors/vehicle-command/pkg/protocol/protobuf/managedcharging'
    _globals['_CHARGEONSOLARNOCHARGEREASON']._serialized_start = 44
    _globals['_CHARGEONSOLARNOCHARGEREASON']._serialized_end = 371