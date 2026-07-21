from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

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

class ChargingAlertType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    INVALID_ALERT_TYPE: _ClassVar[ChargingAlertType]
    WARNING: _ClassVar[ChargingAlertType]
    NOTIFICATION: _ClassVar[ChargingAlertType]

class ChargingAlertName(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    INVALID_ALERT_NAME: _ClassVar[ChargingAlertName]
    BMS_a007_SW_Slowed_Chg_Batt_Cold_OBSOLETE: _ClassVar[ChargingAlertName]
    BMS_a076_SW_Dch_While_Charging: _ClassVar[ChargingAlertName]
    CC_a001_gndMonIntrptLineSide: _ClassVar[ChargingAlertName]
    CC_a002_gndMonIntrptLoadSide: _ClassVar[ChargingAlertName]
    CC_a003_CCIDTripped: _ClassVar[ChargingAlertName]
    CC_a004_CCIDSelfTestFault: _ClassVar[ChargingAlertName]
    CC_a005_groundedNeutral: _ClassVar[ChargingAlertName]
    CC_a006_inputOverCurrent: _ClassVar[ChargingAlertName]
    CC_a007_inputOverVoltage: _ClassVar[ChargingAlertName]
    CC_a008_inputUnderVoltage: _ClassVar[ChargingAlertName]
    CC_a009_inputMiswired: _ClassVar[ChargingAlertName]
    CC_a010_contactorWelded: _ClassVar[ChargingAlertName]
    CC_a011_ambientOT: _ClassVar[ChargingAlertName]
    CC_a012_wallPlugOT: _ClassVar[ChargingAlertName]
    CC_a013_vehConnOT: _ClassVar[ChargingAlertName]
    CC_a014_mcuSelfTestFault: _ClassVar[ChargingAlertName]
    CC_a015_PilotAFault: _ClassVar[ChargingAlertName]
    CC_a016_PilotBFault: _ClassVar[ChargingAlertName]
    CC_a017_PilotCFault: _ClassVar[ChargingAlertName]
    CC_a018_PilotDFault: _ClassVar[ChargingAlertName]
    CC_a019_proxDisconnected: _ClassVar[ChargingAlertName]
    CC_a020_3vRailIncorrect: _ClassVar[ChargingAlertName]
    CC_a021_CB_noMaster: _ClassVar[ChargingAlertName]
    CC_a022_CB_tooManyMasters: _ClassVar[ChargingAlertName]
    CC_a023_CB_tooManySlaves: _ClassVar[ChargingAlertName]
    CC_a024_CB_masterISetTooLow: _ClassVar[ChargingAlertName]
    CC_a025_evseTemp: _ClassVar[ChargingAlertName]
    CC_a026_wallPlugTemp: _ClassVar[ChargingAlertName]
    CC_a027_vehicleHandleTemp: _ClassVar[ChargingAlertName]
    CC_a028_CB_rotarySelect: _ClassVar[ChargingAlertName]
    CC_a029_PilotFFault: _ClassVar[ChargingAlertName]
    CC_a030_masterSlaveMismatch: _ClassVar[ChargingAlertName]
    CC_a041_inputWiringFoldback: _ClassVar[ChargingAlertName]
    CC_a042_pcbaTempFoldback: _ClassVar[ChargingAlertName]
    CC_a043_configurationRequired: _ClassVar[ChargingAlertName]
    CP_a004_proximityRationality: _ClassVar[ChargingAlertName]
    CP_a010_pilotRationality: _ClassVar[ChargingAlertName]
    CP_a046_lostCommsEVSE: _ClassVar[ChargingAlertName]
    CP_a049_multipleCablesDetected: _ClassVar[ChargingAlertName]
    CP_a052_chademoNotSupported: _ClassVar[ChargingAlertName]
    CP_a053_proxLatchedNoPilot: _ClassVar[ChargingAlertName]
    CP_a055_chargeStoppedNoPilot: _ClassVar[ChargingAlertName]
    CP_a058_acChargingBlocked: _ClassVar[ChargingAlertName]
    CP_a062_scOutOfService: _ClassVar[ChargingAlertName]
    CP_a063_scUpdateInProgress: _ClassVar[ChargingAlertName]
    CP_a064_superchargingBlocked: _ClassVar[ChargingAlertName]
    CP_a066_proxLatchedIdlePilot: _ClassVar[ChargingAlertName]
    CP_a067_gbdcConnFault: _ClassVar[ChargingAlertName]
    CP_a074_failedToEstablishV2gComm: _ClassVar[ChargingAlertName]
    CP_a091_wrongSuperchargerHandle: _ClassVar[ChargingAlertName]
    CP_a101_wcFoldbackActive: _ClassVar[ChargingAlertName]
    CP_a102_wcOvertempFault: _ClassVar[ChargingAlertName]
    CP_a108_chademoOvertempFault: _ClassVar[ChargingAlertName]
    CP_a110_thermalVelocityHigh: _ClassVar[ChargingAlertName]
    CP_a120_comboAdapterFoldback: _ClassVar[ChargingAlertName]
    CP_a131_evseCommTimeout: _ClassVar[ChargingAlertName]
    CP_a132_contractAuthTimeout: _ClassVar[ChargingAlertName]
    CP_a133_proxNeverLatched: _ClassVar[ChargingAlertName]
    CP_a135_sdpAttemptsFailed: _ClassVar[ChargingAlertName]
    CP_a139_pilotFaulted: _ClassVar[ChargingAlertName]
    CP_a140_superchargerFaulted: _ClassVar[ChargingAlertName]
    CP_a141_chademoAdapterFault: _ClassVar[ChargingAlertName]
    CP_a142_gbdcScConnFault: _ClassVar[ChargingAlertName]
    CP_a143_unsupportedChargeAdapter: _ClassVar[ChargingAlertName]
    CP_a146_ccsEvseMalfunction: _ClassVar[ChargingAlertName]
    CP_a151_badPilotDiodeDetected: _ClassVar[ChargingAlertName]
    CP_a152_pilotEdgeDetectionFailed: _ClassVar[ChargingAlertName]
    FC_a141_CA_vehConn_OT: _ClassVar[ChargingAlertName]
    FC_a142_CA_evseConn_OT: _ClassVar[ChargingAlertName]
    FC_a143_CA_pcb_OT: _ClassVar[ChargingAlertName]
    FC_a151_CA_vehToEvseDeltaLo: _ClassVar[ChargingAlertName]
    FC_a154_CA_vehToPcbDeltaLo: _ClassVar[ChargingAlertName]
    FC_a161_CA_vehTempHiFoldBk: _ClassVar[ChargingAlertName]
    FC_a162_CA_evseTempHiFoldBk: _ClassVar[ChargingAlertName]
    FC_a163_CA_pcbTempHiFoldBk: _ClassVar[ChargingAlertName]
    FC_a266_GB_negPin_OT: _ClassVar[ChargingAlertName]
    FC_a267_GB_posPin_OT: _ClassVar[ChargingAlertName]
    FC_a268_GB_pcb_OT: _ClassVar[ChargingAlertName]
    FC_a272_GB_negToPosDeltaHi: _ClassVar[ChargingAlertName]
    FC_a273_GB_negToPosDeltaLo: _ClassVar[ChargingAlertName]
    FC_a274_GB_negToPcbDeltaHi: _ClassVar[ChargingAlertName]
    FC_a282_GB_negTempHiFoldBk: _ClassVar[ChargingAlertName]
    FC_a283_GB_posTempHiFoldBk: _ClassVar[ChargingAlertName]
    FC_a284_GB_pcbTempHiFoldBk: _ClassVar[ChargingAlertName]
    FC_a286_GB_evseConnUnlocked: _ClassVar[ChargingAlertName]
    PCS_a007_chgPhaseTempHot: _ClassVar[ChargingAlertName]
    PCS_a016_chgAllPhasesFaulted: _ClassVar[ChargingAlertName]
    PCS_a017_chgWallPowerRemoval: _ClassVar[ChargingAlertName]
    PCS_a019_acChargePowerLimited: _ClassVar[ChargingAlertName]
    PCS_a032_excessiveGridTransientsDetected: _ClassVar[ChargingAlertName]
    PCS_a052_acVoltageNotPresent: _ClassVar[ChargingAlertName]
    PCS_a053_chgInputVDropHigh: _ClassVar[ChargingAlertName]
    PCS_a054_chgInputVDropTooHigh: _ClassVar[ChargingAlertName]
    PCS_a055_chgLineImpedanceHigh: _ClassVar[ChargingAlertName]
    PCS_a056_chgLineImpedanceTooHigh: _ClassVar[ChargingAlertName]
    PCS_a059_chgInputOvRms: _ClassVar[ChargingAlertName]
    PCS_a073_unexpectedAcInputVoltage: _ClassVar[ChargingAlertName]
    PCS_a078_chgStopDcdcTooHot: _ClassVar[ChargingAlertName]
    PCS_a088_gridFreqDroopDetected: _ClassVar[ChargingAlertName]
    PCS_a090_expectedAcVoltageSourceMissing: _ClassVar[ChargingAlertName]
    PCS_a096_microGridOverLoaded: _ClassVar[ChargingAlertName]
    PCS2_a019_DcacADcTempTooHigh: _ClassVar[ChargingAlertName]
    PCS2_a020_DcacBDcTempTooHigh: _ClassVar[ChargingAlertName]
    PCS2_a024_DcacATxTempTooHigh: _ClassVar[ChargingAlertName]
    PCS2_a025_DcacBTxTempTooHigh: _ClassVar[ChargingAlertName]
    PCS2_a062_acVoltageNotPresent: _ClassVar[ChargingAlertName]
    PCS2_a063_chgUnknownGridConfig: _ClassVar[ChargingAlertName]
    PCS2_a112_chgInputVDropTooHigh: _ClassVar[ChargingAlertName]
    PCS2_a115_chgWallPowerRemoval: _ClassVar[ChargingAlertName]
    PCS2_a116_chgPersistentFault: _ClassVar[ChargingAlertName]
    UMC_a001_gndMonIntrptLineSide: _ClassVar[ChargingAlertName]
    UMC_a002_GFCITripped: _ClassVar[ChargingAlertName]
    UMC_a003_GFCISelfTestFault: _ClassVar[ChargingAlertName]
    UMC_a004_inputOverVoltage: _ClassVar[ChargingAlertName]
    UMC_a005_inputUnderVoltage: _ClassVar[ChargingAlertName]
    UMC_a006_contactorWelded: _ClassVar[ChargingAlertName]
    UMC_a007_pcbaOT: _ClassVar[ChargingAlertName]
    UMC_a008_wallPlugOT: _ClassVar[ChargingAlertName]
    UMC_a009_vehConnOT: _ClassVar[ChargingAlertName]
    UMC_a010_inputOT: _ClassVar[ChargingAlertName]
    UMC_a011_proxDisconnected: _ClassVar[ChargingAlertName]
    UMC_a012_pilotFault: _ClassVar[ChargingAlertName]
    UMC_a013_SA_Temperature: _ClassVar[ChargingAlertName]
    UMC_a014_SA_Genealogy: _ClassVar[ChargingAlertName]
    UMC_a015_SA_Connection: _ClassVar[ChargingAlertName]
    UMC_a016_pcbaOTFoldback: _ClassVar[ChargingAlertName]
    UMC_a017_wallPlugOTFoldback: _ClassVar[ChargingAlertName]
    UMC_a018_vehConnOTFoldback: _ClassVar[ChargingAlertName]
    UMC_a019_inputOTFoldback: _ClassVar[ChargingAlertName]

class ChassisType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ChassisTypeModel3: _ClassVar[ChassisType]
    ChassisTypeModelY: _ClassVar[ChassisType]
    ChassisTypeModelYLongWheelBase: _ClassVar[ChassisType]

class FasciaType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    FasciaTypeOriginal: _ClassVar[FasciaType]
    FasciaTypeBasePoppyseed: _ClassVar[FasciaType]
    FasciaTypePerformancePoppyseed: _ClassVar[FasciaType]
    FasciaTypeBaseBayberry: _ClassVar[FasciaType]
    FasciaTypePerformanceBayberry: _ClassVar[FasciaType]
    FasciaTypeP3S: _ClassVar[FasciaType]
    FasciaTypeE41Bayberry: _ClassVar[FasciaType]
    FasciaTypeD50Poppyseed: _ClassVar[FasciaType]

class GtwDiagLevel(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    GtwDiagLevelFactory: _ClassVar[GtwDiagLevel]
    GtwDiagLevelDiagLinkActive: _ClassVar[GtwDiagLevel]
    GtwDiagLevelService: _ClassVar[GtwDiagLevel]
    GtwDiagLevelServiceDrive: _ClassVar[GtwDiagLevel]
    GtwDiagLevelPark: _ClassVar[GtwDiagLevel]
    GtwDiagLevelNormalOperation: _ClassVar[GtwDiagLevel]
    GtwDiagLevelParkRobotaxi: _ClassVar[GtwDiagLevel]

class RearSeatHeaterType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    RearSeatHeaterTypeInvalid: _ClassVar[RearSeatHeaterType]
    ThreeSeatsKongsberg: _ClassVar[RearSeatHeaterType]
    LeftRightOnlyKongsberg: _ClassVar[RearSeatHeaterType]

class AccessoryLightbarType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    AccessoryLightbarTypeNone: _ClassVar[AccessoryLightbarType]
    AccessoryLightbarTypeHella: _ClassVar[AccessoryLightbarType]

class SuspensionActuationState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    INVALID_SUSPENSION_ACTION: _ClassVar[SuspensionActuationState]
    NONE: _ClassVar[SuspensionActuationState]
    RAISING: _ClassVar[SuspensionActuationState]
    LOWERING: _ClassVar[SuspensionActuationState]

class SuspensionLevel(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    INVALID_SUSPENSION_LEVEL: _ClassVar[SuspensionLevel]
    ENTRY: _ClassVar[SuspensionLevel]
    LOW: _ClassVar[SuspensionLevel]
    MEDIUM: _ClassVar[SuspensionLevel]
    HIGH: _ClassVar[SuspensionLevel]
    VERY_HIGH: _ClassVar[SuspensionLevel]
    EXTRACT: _ClassVar[SuspensionLevel]

class ZoneLightRequest(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ZoneLightRequestOff: _ClassVar[ZoneLightRequest]
    ZoneLightRequestLow: _ClassVar[ZoneLightRequest]
    ZoneLightRequestMedium: _ClassVar[ZoneLightRequest]
    ZoneLightRequestHigh: _ClassVar[ZoneLightRequest]
INVALID: Invalid
Stopped: MediaPlaybackStatus
Playing: MediaPlaybackStatus
Paused: MediaPlaybackStatus
StwHeatLevel_Unknown: StwHeatLevel
StwHeatLevel_Off: StwHeatLevel
StwHeatLevel_Low: StwHeatLevel
StwHeatLevel_High: StwHeatLevel
INVALID_ALERT_TYPE: ChargingAlertType
WARNING: ChargingAlertType
NOTIFICATION: ChargingAlertType
INVALID_ALERT_NAME: ChargingAlertName
BMS_a007_SW_Slowed_Chg_Batt_Cold_OBSOLETE: ChargingAlertName
BMS_a076_SW_Dch_While_Charging: ChargingAlertName
CC_a001_gndMonIntrptLineSide: ChargingAlertName
CC_a002_gndMonIntrptLoadSide: ChargingAlertName
CC_a003_CCIDTripped: ChargingAlertName
CC_a004_CCIDSelfTestFault: ChargingAlertName
CC_a005_groundedNeutral: ChargingAlertName
CC_a006_inputOverCurrent: ChargingAlertName
CC_a007_inputOverVoltage: ChargingAlertName
CC_a008_inputUnderVoltage: ChargingAlertName
CC_a009_inputMiswired: ChargingAlertName
CC_a010_contactorWelded: ChargingAlertName
CC_a011_ambientOT: ChargingAlertName
CC_a012_wallPlugOT: ChargingAlertName
CC_a013_vehConnOT: ChargingAlertName
CC_a014_mcuSelfTestFault: ChargingAlertName
CC_a015_PilotAFault: ChargingAlertName
CC_a016_PilotBFault: ChargingAlertName
CC_a017_PilotCFault: ChargingAlertName
CC_a018_PilotDFault: ChargingAlertName
CC_a019_proxDisconnected: ChargingAlertName
CC_a020_3vRailIncorrect: ChargingAlertName
CC_a021_CB_noMaster: ChargingAlertName
CC_a022_CB_tooManyMasters: ChargingAlertName
CC_a023_CB_tooManySlaves: ChargingAlertName
CC_a024_CB_masterISetTooLow: ChargingAlertName
CC_a025_evseTemp: ChargingAlertName
CC_a026_wallPlugTemp: ChargingAlertName
CC_a027_vehicleHandleTemp: ChargingAlertName
CC_a028_CB_rotarySelect: ChargingAlertName
CC_a029_PilotFFault: ChargingAlertName
CC_a030_masterSlaveMismatch: ChargingAlertName
CC_a041_inputWiringFoldback: ChargingAlertName
CC_a042_pcbaTempFoldback: ChargingAlertName
CC_a043_configurationRequired: ChargingAlertName
CP_a004_proximityRationality: ChargingAlertName
CP_a010_pilotRationality: ChargingAlertName
CP_a046_lostCommsEVSE: ChargingAlertName
CP_a049_multipleCablesDetected: ChargingAlertName
CP_a052_chademoNotSupported: ChargingAlertName
CP_a053_proxLatchedNoPilot: ChargingAlertName
CP_a055_chargeStoppedNoPilot: ChargingAlertName
CP_a058_acChargingBlocked: ChargingAlertName
CP_a062_scOutOfService: ChargingAlertName
CP_a063_scUpdateInProgress: ChargingAlertName
CP_a064_superchargingBlocked: ChargingAlertName
CP_a066_proxLatchedIdlePilot: ChargingAlertName
CP_a067_gbdcConnFault: ChargingAlertName
CP_a074_failedToEstablishV2gComm: ChargingAlertName
CP_a091_wrongSuperchargerHandle: ChargingAlertName
CP_a101_wcFoldbackActive: ChargingAlertName
CP_a102_wcOvertempFault: ChargingAlertName
CP_a108_chademoOvertempFault: ChargingAlertName
CP_a110_thermalVelocityHigh: ChargingAlertName
CP_a120_comboAdapterFoldback: ChargingAlertName
CP_a131_evseCommTimeout: ChargingAlertName
CP_a132_contractAuthTimeout: ChargingAlertName
CP_a133_proxNeverLatched: ChargingAlertName
CP_a135_sdpAttemptsFailed: ChargingAlertName
CP_a139_pilotFaulted: ChargingAlertName
CP_a140_superchargerFaulted: ChargingAlertName
CP_a141_chademoAdapterFault: ChargingAlertName
CP_a142_gbdcScConnFault: ChargingAlertName
CP_a143_unsupportedChargeAdapter: ChargingAlertName
CP_a146_ccsEvseMalfunction: ChargingAlertName
CP_a151_badPilotDiodeDetected: ChargingAlertName
CP_a152_pilotEdgeDetectionFailed: ChargingAlertName
FC_a141_CA_vehConn_OT: ChargingAlertName
FC_a142_CA_evseConn_OT: ChargingAlertName
FC_a143_CA_pcb_OT: ChargingAlertName
FC_a151_CA_vehToEvseDeltaLo: ChargingAlertName
FC_a154_CA_vehToPcbDeltaLo: ChargingAlertName
FC_a161_CA_vehTempHiFoldBk: ChargingAlertName
FC_a162_CA_evseTempHiFoldBk: ChargingAlertName
FC_a163_CA_pcbTempHiFoldBk: ChargingAlertName
FC_a266_GB_negPin_OT: ChargingAlertName
FC_a267_GB_posPin_OT: ChargingAlertName
FC_a268_GB_pcb_OT: ChargingAlertName
FC_a272_GB_negToPosDeltaHi: ChargingAlertName
FC_a273_GB_negToPosDeltaLo: ChargingAlertName
FC_a274_GB_negToPcbDeltaHi: ChargingAlertName
FC_a282_GB_negTempHiFoldBk: ChargingAlertName
FC_a283_GB_posTempHiFoldBk: ChargingAlertName
FC_a284_GB_pcbTempHiFoldBk: ChargingAlertName
FC_a286_GB_evseConnUnlocked: ChargingAlertName
PCS_a007_chgPhaseTempHot: ChargingAlertName
PCS_a016_chgAllPhasesFaulted: ChargingAlertName
PCS_a017_chgWallPowerRemoval: ChargingAlertName
PCS_a019_acChargePowerLimited: ChargingAlertName
PCS_a032_excessiveGridTransientsDetected: ChargingAlertName
PCS_a052_acVoltageNotPresent: ChargingAlertName
PCS_a053_chgInputVDropHigh: ChargingAlertName
PCS_a054_chgInputVDropTooHigh: ChargingAlertName
PCS_a055_chgLineImpedanceHigh: ChargingAlertName
PCS_a056_chgLineImpedanceTooHigh: ChargingAlertName
PCS_a059_chgInputOvRms: ChargingAlertName
PCS_a073_unexpectedAcInputVoltage: ChargingAlertName
PCS_a078_chgStopDcdcTooHot: ChargingAlertName
PCS_a088_gridFreqDroopDetected: ChargingAlertName
PCS_a090_expectedAcVoltageSourceMissing: ChargingAlertName
PCS_a096_microGridOverLoaded: ChargingAlertName
PCS2_a019_DcacADcTempTooHigh: ChargingAlertName
PCS2_a020_DcacBDcTempTooHigh: ChargingAlertName
PCS2_a024_DcacATxTempTooHigh: ChargingAlertName
PCS2_a025_DcacBTxTempTooHigh: ChargingAlertName
PCS2_a062_acVoltageNotPresent: ChargingAlertName
PCS2_a063_chgUnknownGridConfig: ChargingAlertName
PCS2_a112_chgInputVDropTooHigh: ChargingAlertName
PCS2_a115_chgWallPowerRemoval: ChargingAlertName
PCS2_a116_chgPersistentFault: ChargingAlertName
UMC_a001_gndMonIntrptLineSide: ChargingAlertName
UMC_a002_GFCITripped: ChargingAlertName
UMC_a003_GFCISelfTestFault: ChargingAlertName
UMC_a004_inputOverVoltage: ChargingAlertName
UMC_a005_inputUnderVoltage: ChargingAlertName
UMC_a006_contactorWelded: ChargingAlertName
UMC_a007_pcbaOT: ChargingAlertName
UMC_a008_wallPlugOT: ChargingAlertName
UMC_a009_vehConnOT: ChargingAlertName
UMC_a010_inputOT: ChargingAlertName
UMC_a011_proxDisconnected: ChargingAlertName
UMC_a012_pilotFault: ChargingAlertName
UMC_a013_SA_Temperature: ChargingAlertName
UMC_a014_SA_Genealogy: ChargingAlertName
UMC_a015_SA_Connection: ChargingAlertName
UMC_a016_pcbaOTFoldback: ChargingAlertName
UMC_a017_wallPlugOTFoldback: ChargingAlertName
UMC_a018_vehConnOTFoldback: ChargingAlertName
UMC_a019_inputOTFoldback: ChargingAlertName
ChassisTypeModel3: ChassisType
ChassisTypeModelY: ChassisType
ChassisTypeModelYLongWheelBase: ChassisType
FasciaTypeOriginal: FasciaType
FasciaTypeBasePoppyseed: FasciaType
FasciaTypePerformancePoppyseed: FasciaType
FasciaTypeBaseBayberry: FasciaType
FasciaTypePerformanceBayberry: FasciaType
FasciaTypeP3S: FasciaType
FasciaTypeE41Bayberry: FasciaType
FasciaTypeD50Poppyseed: FasciaType
GtwDiagLevelFactory: GtwDiagLevel
GtwDiagLevelDiagLinkActive: GtwDiagLevel
GtwDiagLevelService: GtwDiagLevel
GtwDiagLevelServiceDrive: GtwDiagLevel
GtwDiagLevelPark: GtwDiagLevel
GtwDiagLevelNormalOperation: GtwDiagLevel
GtwDiagLevelParkRobotaxi: GtwDiagLevel
RearSeatHeaterTypeInvalid: RearSeatHeaterType
ThreeSeatsKongsberg: RearSeatHeaterType
LeftRightOnlyKongsberg: RearSeatHeaterType
AccessoryLightbarTypeNone: AccessoryLightbarType
AccessoryLightbarTypeHella: AccessoryLightbarType
INVALID_SUSPENSION_ACTION: SuspensionActuationState
NONE: SuspensionActuationState
RAISING: SuspensionActuationState
LOWERING: SuspensionActuationState
INVALID_SUSPENSION_LEVEL: SuspensionLevel
ENTRY: SuspensionLevel
LOW: SuspensionLevel
MEDIUM: SuspensionLevel
HIGH: SuspensionLevel
VERY_HIGH: SuspensionLevel
EXTRACT: SuspensionLevel
ZoneLightRequestOff: ZoneLightRequest
ZoneLightRequestLow: ZoneLightRequest
ZoneLightRequestMedium: ZoneLightRequest
ZoneLightRequestHigh: ZoneLightRequest

class Void(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class LatLong(_message.Message):
    __slots__ = ("latitude", "longitude")
    LATITUDE_FIELD_NUMBER: _ClassVar[int]
    LONGITUDE_FIELD_NUMBER: _ClassVar[int]
    latitude: float
    longitude: float
    def __init__(self, latitude: _Optional[float] = ..., longitude: _Optional[float] = ...) -> None: ...

class ChargePortLatchState(_message.Message):
    __slots__ = ("SNA", "Disengaged", "Engaged", "Blocking")
    SNA_FIELD_NUMBER: _ClassVar[int]
    DISENGAGED_FIELD_NUMBER: _ClassVar[int]
    ENGAGED_FIELD_NUMBER: _ClassVar[int]
    BLOCKING_FIELD_NUMBER: _ClassVar[int]
    SNA: Void
    Disengaged: Void
    Engaged: Void
    Blocking: Void
    def __init__(self, SNA: _Optional[_Union[Void, _Mapping]] = ..., Disengaged: _Optional[_Union[Void, _Mapping]] = ..., Engaged: _Optional[_Union[Void, _Mapping]] = ..., Blocking: _Optional[_Union[Void, _Mapping]] = ...) -> None: ...

class PreconditioningTimes(_message.Message):
    __slots__ = ("all_week", "weekdays")
    ALL_WEEK_FIELD_NUMBER: _ClassVar[int]
    WEEKDAYS_FIELD_NUMBER: _ClassVar[int]
    all_week: Void
    weekdays: Void
    def __init__(self, all_week: _Optional[_Union[Void, _Mapping]] = ..., weekdays: _Optional[_Union[Void, _Mapping]] = ...) -> None: ...

class OffPeakChargingTimes(_message.Message):
    __slots__ = ("all_week", "weekdays")
    ALL_WEEK_FIELD_NUMBER: _ClassVar[int]
    WEEKDAYS_FIELD_NUMBER: _ClassVar[int]
    all_week: Void
    weekdays: Void
    def __init__(self, all_week: _Optional[_Union[Void, _Mapping]] = ..., weekdays: _Optional[_Union[Void, _Mapping]] = ...) -> None: ...

class ChargeSchedule(_message.Message):
    __slots__ = ("id", "name", "days_of_week", "start_enabled", "start_time", "end_enabled", "end_time", "one_time", "enabled", "latitude", "longitude")
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
    def __init__(self, id: _Optional[int] = ..., name: _Optional[str] = ..., days_of_week: _Optional[int] = ..., start_enabled: _Optional[bool] = ..., start_time: _Optional[int] = ..., end_enabled: _Optional[bool] = ..., end_time: _Optional[int] = ..., one_time: _Optional[bool] = ..., enabled: _Optional[bool] = ..., latitude: _Optional[float] = ..., longitude: _Optional[float] = ...) -> None: ...

class PreconditionSchedule(_message.Message):
    __slots__ = ("id", "name", "days_of_week", "precondition_time", "one_time", "enabled", "latitude", "longitude")
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
    def __init__(self, id: _Optional[int] = ..., name: _Optional[str] = ..., days_of_week: _Optional[int] = ..., precondition_time: _Optional[int] = ..., one_time: _Optional[bool] = ..., enabled: _Optional[bool] = ..., latitude: _Optional[float] = ..., longitude: _Optional[float] = ...) -> None: ...

class ChargingAlert(_message.Message):
    __slots__ = ("alert_name", "alert_type")
    ALERT_NAME_FIELD_NUMBER: _ClassVar[int]
    ALERT_TYPE_FIELD_NUMBER: _ClassVar[int]
    alert_name: ChargingAlertName
    alert_type: ChargingAlertType
    def __init__(self, alert_name: _Optional[_Union[ChargingAlertName, str]] = ..., alert_type: _Optional[_Union[ChargingAlertType, str]] = ...) -> None: ...
