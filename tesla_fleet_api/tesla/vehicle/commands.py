from __future__ import annotations
from abc import ABC, abstractmethod

import struct
from random import randbytes
from typing import (
    Any,
    TYPE_CHECKING,
    Callable,
    ClassVar,
    Generic,
    Literal,
    TypeVar,
    cast,
)
import time
import hmac
import hashlib
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import PublicFormat, Encoding
from cryptography.hazmat.primitives.hashes import Hash, SHA256
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from asyncio import Lock, sleep

from tesla_fleet_api.exceptions import (
    MESSAGE_FAULTS,
    SIGNED_MESSAGE_INFORMATION_FAULTS,
    NotOnWhitelistFault,
    SessionInfoAuthenticationFault,
    SignedCommandResponseReplayed,
    TeslaFleetError,
    # TeslaFleetMessageFaultInvalidSignature,
    TeslaFleetMessageFaultIncorrectEpoch,
    TeslaFleetMessageFaultInvalidTokenOrCounter,
)

from tesla_fleet_api.tesla.vehicle.vehicle import Vehicle


from tesla_fleet_api.const import (
    LOGGER,
    AutoSeat,
    Trunk,
    ClimateKeeperMode,
    CabinOverheatProtectionTemp,
    SunRoofCommand,
    WindowCommand,
    TemperatureUnit,
    DistanceUnit,
    TimeDisplayFormat,
    TirePressureUnit,
    EnergyDisplayFormat,
    PhoneFontSize,
)

# Protocol
from tesla_protocol.command.errors_pb2 import GenericError_E
from tesla_protocol.command.car_server_pb2 import (
    AutoStwHeatAction,
    BoomboxAction,
    DrivingClearSpeedLimitPinAdminAction,
    Response,
)
from tesla_protocol.command.signatures_pb2 import (
    Session_Info_Status,
    SignatureType,
    Tag,
    AES_GCM_Personalized_Signature_Data,
    KeyIdentity,
    SessionInfo,
    SignatureData,
)
from tesla_protocol.command.universal_message_pb2 import (
    OperationStatus_E,
    Destination,
    Domain,
    RoutableMessage,
    SessionInfoRequest,
    Flags,
)
from tesla_protocol.command.vcsec_pb2 import (
    FromVCSECMessage,
    VehicleStatus,
)
from tesla_protocol.command.car_server_pb2 import (
    Action,
    MediaPlayAction,
    VehicleAction,
    VehicleControlFlashLightsAction,
    ChargingStartStopAction,
    ChargingSetLimitAction,
    EraseUserDataAction,
    DrivingClearSpeedLimitPinAction,
    DrivingSetSpeedLimitAction,
    DrivingSpeedLimitAction,
    HvacAutoAction,
    HvacSeatHeaterActions,
    HvacSeatCoolerActions,
    HvacSetPreconditioningMaxAction,
    HvacSteeringWheelHeaterAction,
    HvacTemperatureAdjustmentAction,
    GetNearbyChargingSites,
    VehicleControlCancelSoftwareUpdateAction,
    VehicleControlHonkHornAction,
    VehicleControlResetValetPinAction,
    VehicleControlScheduleSoftwareUpdateAction,
    VehicleControlSetSentryModeAction,
    VehicleControlSetValetModeAction,
    VehicleControlSunroofOpenCloseAction,
    VehicleControlTriggerHomelinkAction,
    VehicleControlWindowAction,
    HvacBioweaponModeAction,
    AutoSeatClimateAction,
    Ping,
    ScheduledChargingAction,
    ScheduledDepartureAction,
    HvacClimateKeeperAction,
    SetChargingAmpsAction,
    SetCabinOverheatProtectionAction,
    SetVehicleNameAction,
    SetCopTempAction,
    VehicleControlSetPinToDriveAction,
    VehicleControlResetPinToDriveAction,
    MediaNextTrack,
    MediaNextFavorite,
    MediaUpdateVolume,
    MediaPreviousTrack,
    MediaPreviousFavorite,
    NavigationGpsRequest,
    NavigationRequest,
    NavigationSuperchargerRequest,
    NavigationWaypointsRequest,
    StwHeatLevelAction,
    HvacRecirculationAction,
    DashcamSaveClipAction,
    SetSuspensionLevelAction,
    StartLightShowAction,
    StopLightShowAction,
    CancelSohTestAction,
    RemoveChargeScheduleAction,
    RemovePreconditionScheduleAction,
    BatchRemoveChargeSchedulesAction,
    BatchRemovePreconditionSchedulesAction,
    SetPowershareFeatureAction,
    SetPowershareRequestAction,
    SetPowershareDischargeLimitAction,
    SetOutletsOnOffAction,
    SetOutletTimerAction,
    SetOutletSocLimitAction,
    SetPowerFeedOnOffAction,
    SetPowerFeedTimerAction,
    SetPowerFeedSocLimitAction,
    SetLightbarBrightnessAction,
    SetLightbarMiddleAction,
    SetLightbarDitchAction,
    SetZoneLightRequestAction,
    SetTrailerLightTestStartStopAction,
    SetTruckBedLightAutoStateAction,
    SetTruckBedLightBrightnessAction,
    SetTentModeRequestAction,
    ParentalControlsAction,
    ParentalControlsClearPinAction,
    ParentalControlsClearPinAdminAction,
    ParentalControlsEnableSettingsAction,
    ParentalControlsSetSpeedLimitAction,
    UpdateChargeOnSolarFeatureRequest,
    GetChargeOnSolarFeatureRequest,
    ChargeOnSolarFeature,
    NavigationGpsDestinationRequest,
    VehicleControlResetPinToDriveAdminAction,
    SetLowPowerModeAction,
    SetKeepAccessoryPowerModeAction,
    PiiKeyRequest,
    PseudonymSyncRequest,
    TeslaAuthResponseAction,
    SetupCloudProfileWithLocalProfileUuidAction,
    GetLocalProfilesForVaultUuidAction,
    DeleteDashcamClipsAction,
    FormatUSBAction,
    SetTemperatureUnitAction,
    SetDistanceUnitAction,
    SetTimeDisplayFormatAction,
    SetTirePressureUnitAction,
    SetEnergyDisplayFormatAction,
    SetPhoneSettingPreferencesAction,
    PhoneUnitPreferences,
    UiSetUpcomingCalendarEntries,
    TakeDrivenoteAction,
    VideoRequestAction,
    NavigationRouteAction,
    GetMessagesAction,
    SetRateTariffRequest,
    GetRateTariffRequest,
    AddManagedChargingSiteRequest,
    RemoveManagedChargingSiteRequest,
    GetManagedChargingSitesRequest,
    SetDischargeLimitAction,
    ManagedChargingSite,
    ManagerType,
    SiteController,
    BluetoothClassicPairingRequest,
    BandwidthTest,
    FetchKeysInfoAction,
)
from google.protobuf.timestamp_pb2 import Timestamp
from tesla_protocol.command.vehicle_pb2 import (
    VehicleData,
    VehicleState,
    ClimateState,
)
from tesla_protocol.command.vcsec_pb2 import (
    UnsignedMessage,
    RKEAction_E,
    ClosureMoveRequest,
    ClosureMoveType_E,
)
from tesla_protocol.command.signatures_pb2 import (
    HMAC_Personalized_Signature_Data,
)
from tesla_protocol.command.common_pb2 import (
    LatLong,
    Void,
    PreconditioningTimes,
    OffPeakChargingTimes,
    StwHeatLevel,
    ChargeSchedule,
    PreconditionSchedule,
)

if TYPE_CHECKING:
    from tesla_fleet_api.tesla.tesla import Tesla

CommandParentT = TypeVar("CommandParentT", bound="Tesla")

# ENUMs to convert ints to proto typed ints
HvacSeatCoolerLevels = (
    HvacSeatCoolerActions.HvacSeatCoolerLevel_Off,
    HvacSeatCoolerActions.HvacSeatCoolerLevel_Low,
    HvacSeatCoolerActions.HvacSeatCoolerLevel_Med,
    HvacSeatCoolerActions.HvacSeatCoolerLevel_High,
)

HvacSeatCoolerPositions = (
    HvacSeatCoolerActions.HvacSeatCoolerPosition_FrontLeft,
    HvacSeatCoolerActions.HvacSeatCoolerPosition_FrontRight,
)

HvacClimateKeeperActions = (
    HvacClimateKeeperAction.ClimateKeeperAction_Off,
    HvacClimateKeeperAction.ClimateKeeperAction_On,
    HvacClimateKeeperAction.ClimateKeeperAction_Dog,
    HvacClimateKeeperAction.ClimateKeeperAction_Camp,
)

CopActivationTemps = (
    ClimateState.CopActivationTemp.CopActivationTempLow,
    ClimateState.CopActivationTemp.CopActivationTempMedium,
    ClimateState.CopActivationTemp.CopActivationTempHigh,
)

StwHeatLevels = (
    StwHeatLevel.StwHeatLevel_Off,
    StwHeatLevel.StwHeatLevel_Low,
    StwHeatLevel.StwHeatLevel_High,
)


def vcsec_command_name(command: UnsignedMessage) -> str:
    """Derive a short debug-log command name from a VCSEC UnsignedMessage's populated field."""
    field = command.WhichOneof("sub_message")
    if field == "RKEAction":
        return RKEAction_E.Name(command.RKEAction)
    return field or "unknown"


def infotainment_command_name(command: Action) -> str:
    """Derive a short debug-log command name from an infotainment Action's populated field."""
    return command.vehicleAction.WhichOneof("vehicle_action_msg") or "unknown"


def _log_command_result(name: str, transport: str, result: dict[str, Any]) -> None:
    """Log the terminal outcome of one signed command at debug level."""
    response = result.get("response")
    if isinstance(response, dict):
        response_dict = cast("dict[str, Any]", response)
        LOGGER.debug(
            "command=%s transport=%s result=%s reason=%s",
            name,
            transport,
            response_dict.get("result"),
            response_dict.get("reason"),
        )
    else:
        LOGGER.debug("command=%s transport=%s result=success", name, transport)


def _log_command_error(name: str, transport: str, exc: BaseException) -> None:
    """Log a signed command failure at debug level; the exception type carries the ack-vs-timeout distinction."""
    LOGGER.debug(
        "command=%s transport=%s result=error error=%s: %s",
        name,
        transport,
        type(exc).__name__,
        exc,
    )


class Session(Generic[CommandParentT]):
    """A connect to a domain"""

    def __init__(self, parent: Commands[CommandParentT], domain: Domain):
        self.parent: Commands[CommandParentT] = parent
        self.domain: Domain = domain
        self.counter: int = 0
        self.epoch: bytes | None = None
        self.delta: int | None = None
        self.sharedKey: bytes | None = None
        self.hmac: bytes | None = None
        self.publicKey: bytes | None = None
        self.session_info_key: bytes | None = None
        self.last_response_counter: int | None = None
        self._last_authenticated_clock_time: int | None = None
        self.lock: Lock = Lock()

    @property
    def ready(self) -> bool:
        """Return whether the session has the handshake material needed to send commands."""
        return (
            self.epoch is not None and self.hmac is not None and self.delta is not None
        )

    def keys_for(self, vehicle_public_key: bytes) -> tuple[bytes, bytes, bytes]:
        """Derive (shared_key, command_hmac_key, session_info_key) for a candidate vehicle public key.

        Pure and side-effect free - it does not touch any session state, so a
        caller must authenticate a reply against the returned keys before
        deciding whether to commit them via ``commit()``.
        """
        shared_key = self.parent.shared_key(vehicle_public_key)
        hmac_key = hmac.new(
            shared_key, "authenticated command".encode(), hashlib.sha256
        ).digest()
        session_info_key = hmac.new(
            shared_key, "session info".encode(), hashlib.sha256
        ).digest()
        return shared_key, hmac_key, session_info_key

    def commit(
        self,
        session_info: SessionInfo,
        shared_key: bytes,
        hmac_key: bytes,
        session_info_key: bytes,
    ) -> bool:
        """Commit an already-authenticated SessionInfo plus its ``keys_for`` result.

        The anti-replay counter never rolls back within the same epoch, and a
        clock time that regresses within the same epoch marks the reply as
        stale/replayed - returns False without mutating any state so the
        caller can discard it.
        """
        same_epoch = self.epoch is not None and self.epoch == session_info.epoch
        if (
            same_epoch
            and self._last_authenticated_clock_time is not None
            and session_info.clock_time < self._last_authenticated_clock_time
        ):
            return False

        self.counter = (
            max(self.counter, session_info.counter)
            if same_epoch
            else session_info.counter
        )
        self.epoch = session_info.epoch
        self.delta = int(time.time()) - session_info.clock_time
        self._last_authenticated_clock_time = session_info.clock_time
        self.publicKey = session_info.publicKey
        self.sharedKey = shared_key
        self.hmac = hmac_key
        self.session_info_key = session_info_key
        if not same_epoch:
            self.last_response_counter = None
        return True

    def hmac_personalized(self) -> HMAC_Personalized_Signature_Data:
        """Sign a command and return session metadata"""
        assert self.delta is not None
        self.counter += 1
        return HMAC_Personalized_Signature_Data(
            epoch=self.epoch,
            counter=self.counter,
            # Expire command in 10 seconds
            expires_at=int(time.time()) - self.delta + 10,
        )

    def aes_gcm_personalized(self) -> AES_GCM_Personalized_Signature_Data:
        """Sign a command and return session metadata"""
        assert self.delta is not None
        self.counter += 1
        return AES_GCM_Personalized_Signature_Data(
            epoch=self.epoch,
            nonce=randbytes(12),
            counter=self.counter,
            # Expire command in 30 seconds (BLE can be slow)
            expires_at=int(time.time()) - self.delta + 30,
        )


class Commands(ABC, Vehicle[CommandParentT], Generic[CommandParentT]):
    """Class describing the Tesla Fleet API vehicle endpoints and commands for a specific vehicle with command signing."""

    private_key: ec.EllipticCurvePrivateKey
    _public_key: bytes
    _from_destination: bytes
    _sessions: dict[int, Session[CommandParentT]]
    _auth_method: ClassVar[Literal["hmac", "aes"]]
    # Transport identity for debug logging; set per concrete subclass.
    _transport_name: ClassVar[str]

    def __init__(
        self,
        parent: CommandParentT,
        vin: str,
        private_key: ec.EllipticCurvePrivateKey | None = None,
        public_key: bytes | None = None,
    ):
        super().__init__(parent, vin)

        self._from_destination = randbytes(16)
        self._sessions = {
            Domain.DOMAIN_VEHICLE_SECURITY: Session(
                self, Domain.DOMAIN_VEHICLE_SECURITY
            ),
            Domain.DOMAIN_INFOTAINMENT: Session(self, Domain.DOMAIN_INFOTAINMENT),
        }

        if private_key:
            self.private_key = private_key
        elif parent.private_key:
            self.private_key = parent.private_key
        else:
            raise ValueError("No private key.")

        self._public_key = public_key or self.private_key.public_key().public_bytes(
            encoding=Encoding.X962, format=PublicFormat.UncompressedPoint
        )

    def shared_key(self, vehicleKey: bytes) -> bytes:
        """Derive the 16-byte shared key used for signed-command session encryption."""
        exchange = self.private_key.exchange(
            ec.ECDH(),
            ec.EllipticCurvePublicKey.from_encoded_point(ec.SECP256R1(), vehicleKey),
        )
        return hashlib.sha1(exchange).digest()[:16]

    @abstractmethod
    async def _send(
        self,
        msg: RoutableMessage,
        requires: str,
        expects_data: bool = True,
        *,
        confirm_broadcast: Callable[[VehicleStatus], bool] | None = None,
    ) -> RoutableMessage:
        """Transmit the message to the vehicle.

        ``expects_data`` is False when the reply is a single terminal ack with
        no following data frame (a VCSEC actuation), letting a framing
        transport return on that ack instead of waiting out a data follow-up.
        ``confirm_broadcast``, when given, lets a transport that also observes
        unsolicited state broadcasts (BLE) treat a matching broadcast as an
        alternate confirmation alongside the addressed ack - transports with no
        such side channel (e.g. Fleet API) ignore it.
        """
        raise NotImplementedError

    def validate_msg(self, msg: RoutableMessage, request_uuid: bytes) -> None:
        """Validate the message.

        ``request_uuid`` is the uuid of the outstanding request ``msg``
        answers; it authenticates any piggy-backed ``session_info`` as the
        TAG_CHALLENGE bound into that reply's HMAC tag before any field of it
        is trusted.
        """
        if msg.session_info:
            self._authenticate_session_info(msg, request_uuid)

        if msg.signedMessageStatus.signed_message_fault > 0:
            exception = MESSAGE_FAULTS[msg.signedMessageStatus.signed_message_fault]
            if exception:
                raise exception

    def _authenticate_session_info(
        self, msg: RoutableMessage, request_uuid: bytes
    ) -> None:
        """Authenticate and commit a piggy-backed ``SessionInfo`` reply.

        A ``SessionInfo`` is untrusted wire data until its ``session_info_tag``
        is verified: the tag is an HMAC over the exact bytes received, keyed
        by a key derived from the *candidate* vehicle public key carried
        inside that same ``SessionInfo``, and bound to this request's
        ``request_uuid`` as a challenge - so a captured older reply can't be
        replayed against a newer request. Only once that tag checks out do we
        act on anything the message claims, including its own whitelist
        status, and even then ``Session.commit`` still refuses a clock time
        that regresses within the same epoch.

        VCSEC typically leaves the wire-level ``request_uuid`` field empty on
        real hardware (memory constraints) - its absence must never be
        treated as a rejection. Only cross-check the echo when the vehicle
        chose to populate it.
        """
        if msg.request_uuid and msg.request_uuid != request_uuid:
            raise SessionInfoAuthenticationFault(
                "Session info reply does not match an outstanding request."
            )

        session = self._sessions[msg.from_destination.domain]
        info = SessionInfo.FromString(msg.session_info)
        shared_key, hmac_key, session_info_key = session.keys_for(info.publicKey)

        tag = msg.signature_data.session_info_tag.tag
        if not tag:
            raise SessionInfoAuthenticationFault(
                "Session info reply is missing its authentication tag."
            )

        metadata = bytes(
            [
                Tag.TAG_SIGNATURE_TYPE,
                1,
                SignatureType.SIGNATURE_TYPE_HMAC,
                Tag.TAG_PERSONALIZATION,
                17,
                *self.vin.encode(),
                Tag.TAG_CHALLENGE,
                len(request_uuid),
                *request_uuid,
                Tag.TAG_END,
            ]
        )
        expected_tag = hmac.new(
            session_info_key, metadata + msg.session_info, hashlib.sha256
        ).digest()
        if not hmac.compare_digest(expected_tag, tag):
            raise SessionInfoAuthenticationFault(
                "Session info reply failed authentication (invalid tag)."
            )

        if info.status == Session_Info_Status.SESSION_INFO_STATUS_KEY_NOT_ON_WHITELIST:
            raise NotOnWhitelistFault

        if not session.commit(info, shared_key, hmac_key, session_info_key):
            raise SessionInfoAuthenticationFault(
                "Session info reply is stale (clock regressed within the same epoch)."
            )

    async def _command(
        self,
        domain: Domain,
        command: bytes,
        attempt: int = 0,
        expects_data: bool = True,
        confirm_broadcast: Callable[[VehicleStatus], bool] | None = None,
    ) -> dict[str, Any]:
        """Serialize a message and send to the signed command endpoint.

        On a WAIT status or an epoch/token fault, this re-signs and re-sends
        the identical command (bounded at 3 attempts) - for a non-idempotent
        command that window can apply it twice if the first attempt actually
        executed despite the WAIT/fault reply.

        ``expects_data`` is threaded to ``_send`` and every retry; it is False
        for a VCSEC actuation, whose reply is a bare terminal ack.
        ``confirm_broadcast`` is threaded the same way; a transport with no
        broadcast side channel simply ignores it.
        """
        session = self._sessions[domain]
        if not session.ready:
            await self._handshake(domain)

        async with session.lock:
            if self._auth_method == "hmac":
                msg = await self._commandHmac(session, command)
            elif self._auth_method == "aes":
                msg = await self._commandAes(session, command)
            else:
                raise ValueError(f"Unknown auth method: {self._auth_method}")

        try:
            resp = await self._send(
                msg,
                "protobuf_message_as_bytes",
                expects_data=expects_data,
                confirm_broadcast=confirm_broadcast,
            )
        except (
            # TeslaFleetMessageFaultInvalidSignature,
            TeslaFleetMessageFaultIncorrectEpoch,
            TeslaFleetMessageFaultInvalidTokenOrCounter,
        ) as e:
            attempt += 1
            if attempt > 3:
                # We tried 3 times, give up, raise the error
                raise e
            return await self._command(
                domain,
                command,
                attempt,
                expects_data=expects_data,
                confirm_broadcast=confirm_broadcast,
            )

        if (
            resp.signedMessageStatus.operation_status
            == OperationStatus_E.OPERATIONSTATUS_WAIT
        ):
            attempt += 1
            if attempt > 3:
                # We tried 3 times, give up, raise the error
                return {"response": {"result": False, "reason": "Too many retries"}}
            async with session.lock:
                await sleep(2)
            return await self._command(
                domain,
                command,
                attempt,
                expects_data=expects_data,
                confirm_broadcast=confirm_broadcast,
            )

        if resp.HasField("protobuf_message_as_bytes"):
            # decrypt
            if resp.signature_data.HasField("AES_GCM_Response_data"):
                if msg.signature_data.HasField("AES_GCM_Personalized_data"):
                    request_hash = (
                        bytes([SignatureType.SIGNATURE_TYPE_AES_GCM_PERSONALIZED])
                        + msg.signature_data.AES_GCM_Personalized_data.tag
                    )
                elif msg.signature_data.HasField("HMAC_Personalized_data"):
                    request_hash = (
                        bytes([SignatureType.SIGNATURE_TYPE_HMAC_PERSONALIZED])
                        + msg.signature_data.HMAC_Personalized_data.tag
                    )
                    if session.domain == Domain.DOMAIN_VEHICLE_SECURITY:
                        request_hash = request_hash[:17]
                else:
                    raise ValueError("Invalid request signature data")

                response_counter = resp.signature_data.AES_GCM_Response_data.counter
                if (
                    session.last_response_counter is not None
                    and response_counter <= session.last_response_counter
                ):
                    raise SignedCommandResponseReplayed

                metadata = bytes(
                    [
                        Tag.TAG_SIGNATURE_TYPE,
                        1,
                        SignatureType.SIGNATURE_TYPE_AES_GCM_RESPONSE,
                        Tag.TAG_DOMAIN,
                        1,
                        resp.from_destination.domain,
                        Tag.TAG_PERSONALIZATION,
                        17,
                        *self.vin.encode(),
                        Tag.TAG_COUNTER,
                        4,
                        *struct.pack(
                            ">I", resp.signature_data.AES_GCM_Response_data.counter
                        ),
                        Tag.TAG_FLAGS,
                        4,
                        *struct.pack(">I", resp.flags),
                        Tag.TAG_REQUEST_HASH,
                        17,
                        *request_hash,
                        Tag.TAG_FAULT,
                        4,
                        *struct.pack(
                            ">I", resp.signedMessageStatus.signed_message_fault
                        ),
                        Tag.TAG_END,
                    ]
                )

                aad = Hash(SHA256())
                aad.update(metadata)
                if session.sharedKey is None:
                    raise ValueError("Session shared key is missing")
                aesgcm = AESGCM(session.sharedKey)
                resp.protobuf_message_as_bytes = aesgcm.decrypt(
                    resp.signature_data.AES_GCM_Response_data.nonce,
                    resp.protobuf_message_as_bytes
                    + resp.signature_data.AES_GCM_Response_data.tag,
                    aad.finalize(),
                )
                session.last_response_counter = response_counter

            if resp.from_destination.domain == Domain.DOMAIN_VEHICLE_SECURITY:
                try:
                    vcsec = FromVCSECMessage.FromString(resp.protobuf_message_as_bytes)
                except Exception as e:
                    LOGGER.error("Failed to parse VCSEC message: %s %s", e, resp)
                    raise e
                LOGGER.debug("VCSEC Response: %s", vcsec)
                if vcsec.HasField("nominalError"):
                    LOGGER.error(
                        "Command failed with reason: %s",
                        vcsec.nominalError.genericError,
                    )
                    return {
                        "response": {
                            "result": False,
                            "reason": GenericError_E.Name(
                                vcsec.nominalError.genericError
                            ),
                        }
                    }
                elif vcsec.HasField("vehicleStatus"):
                    if not expects_data:
                        # An actuation has no data reply of its own; a
                        # populated vehicleStatus here is our own broadcast
                        # substitution for a lost ack (see _send), not a
                        # requested read - report it as an actuation success.
                        return {"response": {"result": True, "reason": ""}}
                    return {"response": vcsec.vehicleStatus}
                elif (
                    vcsec.commandStatus.operationStatus
                    == OperationStatus_E.OPERATIONSTATUS_OK
                ):
                    return {"response": {"result": True, "reason": ""}}
                elif (
                    vcsec.commandStatus.operationStatus
                    == OperationStatus_E.OPERATIONSTATUS_WAIT
                ):
                    attempt += 1
                    if attempt > 3:
                        # We tried 3 times, give up, raise the error
                        return {
                            "response": {"result": False, "reason": "Too many retries"}
                        }
                    async with session.lock:
                        await sleep(2)
                    return await self._command(
                        domain,
                        command,
                        attempt,
                        expects_data=expects_data,
                        confirm_broadcast=confirm_broadcast,
                    )
                elif (
                    vcsec.commandStatus.operationStatus
                    == OperationStatus_E.OPERATIONSTATUS_ERROR
                ):
                    if resp.HasField("signedMessageStatus"):
                        exception = SIGNED_MESSAGE_INFORMATION_FAULTS[
                            vcsec.commandStatus.signedMessageStatus.signedMessageInformation
                        ]
                        if exception:
                            raise exception

            elif resp.from_destination.domain == Domain.DOMAIN_INFOTAINMENT:
                try:
                    response = Response.FromString(resp.protobuf_message_as_bytes)
                except Exception as e:
                    LOGGER.error(
                        "Failed to parse Infotainment Response: %s %s", e, resp
                    )
                    raise e
                LOGGER.debug("Infotainment Response: %s", response)
                if response.HasField("ping"):
                    return {
                        "response": {
                            "result": True,
                            "reason": response.ping.local_timestamp,
                        }
                    }
                if response.HasField("vehicleData"):
                    return {"response": response.vehicleData}
                if response.HasField("actionStatus"):
                    return {
                        "response": {
                            "result": response.actionStatus.result
                            == OperationStatus_E.OPERATIONSTATUS_OK,
                            "reason": response.actionStatus.result_reason.plain_text
                            or "",
                        }
                    }

        return {"response": {"result": True, "reason": ""}}

    async def _commandHmac(
        self, session: Session[CommandParentT], command: bytes, attempt: int = 1
    ) -> RoutableMessage:
        """Create a signed message."""
        LOGGER.debug(f"Sending HMAC to domain {Domain.Name(session.domain)}")

        hmac_personalized = session.hmac_personalized()

        metadata = bytes(
            [
                Tag.TAG_SIGNATURE_TYPE,
                1,
                SignatureType.SIGNATURE_TYPE_HMAC_PERSONALIZED,
                Tag.TAG_DOMAIN,
                1,
                session.domain,
                Tag.TAG_PERSONALIZATION,
                17,
                *self.vin.encode(),
                Tag.TAG_EPOCH,
                len(hmac_personalized.epoch),
                *hmac_personalized.epoch,
                Tag.TAG_EXPIRES_AT,
                4,
                *struct.pack(">I", hmac_personalized.expires_at),
                Tag.TAG_COUNTER,
                4,
                *struct.pack(">I", hmac_personalized.counter),
                Tag.TAG_END,
            ]
        )

        if session.hmac is None:
            raise ValueError("Session HMAC is missing")

        hmac_personalized.tag = hmac.new(
            session.hmac, metadata + command, hashlib.sha256
        ).digest()

        return RoutableMessage(
            to_destination=Destination(
                domain=session.domain,
            ),
            from_destination=Destination(routing_address=self._from_destination),
            protobuf_message_as_bytes=command,
            uuid=randbytes(16),
            signature_data=SignatureData(
                signer_identity=KeyIdentity(public_key=self._public_key),
                HMAC_Personalized_data=hmac_personalized,
            ),
        )

    async def _commandAes(
        self, session: Session[CommandParentT], command: bytes, attempt: int = 1
    ) -> RoutableMessage:
        """Create an encrypted message."""
        LOGGER.debug(f"Sending AES to domain {Domain.Name(session.domain)}")

        aes_personalized = session.aes_gcm_personalized()
        flags = 1 << Flags.FLAG_ENCRYPT_RESPONSE

        metadata = bytes(
            [
                Tag.TAG_SIGNATURE_TYPE,
                1,
                SignatureType.SIGNATURE_TYPE_AES_GCM_PERSONALIZED,
                Tag.TAG_DOMAIN,
                1,
                session.domain,
                Tag.TAG_PERSONALIZATION,
                17,
                *self.vin.encode(),
                Tag.TAG_EPOCH,
                len(aes_personalized.epoch),
                *aes_personalized.epoch,
                Tag.TAG_EXPIRES_AT,
                4,
                *struct.pack(">I", aes_personalized.expires_at),
                Tag.TAG_COUNTER,
                4,
                *struct.pack(">I", aes_personalized.counter),
                Tag.TAG_FLAGS,
                4,
                *struct.pack(">I", flags),
                Tag.TAG_END,
            ]
        )

        aad = Hash(SHA256())
        aad.update(metadata)
        if session.sharedKey is None:
            raise ValueError("Session shared key is missing")
        aesgcm = AESGCM(session.sharedKey)
        ct = aesgcm.encrypt(aes_personalized.nonce, command, aad.finalize())

        aes_personalized.tag = ct[-16:]

        return RoutableMessage(
            to_destination=Destination(
                domain=session.domain,
            ),
            from_destination=Destination(routing_address=self._from_destination),
            protobuf_message_as_bytes=ct[:-16],
            uuid=randbytes(16),
            signature_data=SignatureData(
                signer_identity=KeyIdentity(public_key=self._public_key),
                AES_GCM_Personalized_data=aes_personalized,
            ),
            flags=flags,
        )

    async def _sendVehicleSecurity(
        self,
        command: UnsignedMessage,
        *,
        confirm_broadcast: Callable[[VehicleStatus], bool] | None = None,
    ) -> dict[str, Any]:
        """Sign and send an actuation to the Vehicle Security computer.

        A VCSEC actuation replies with a single terminal ack and no data frame,
        so ``expects_data=False`` lets ``_send`` return on that ack.
        ``confirm_broadcast`` is passed through to ``_send``; only a transport
        with a broadcast side channel (BLE) acts on it.
        """
        name = vcsec_command_name(command)
        try:
            result = await self._command(
                Domain.DOMAIN_VEHICLE_SECURITY,
                command.SerializeToString(),
                expects_data=False,
                confirm_broadcast=confirm_broadcast,
            )
        except (Exception, TeslaFleetError) as e:
            _log_command_error(name, self._transport_name, e)
            raise
        _log_command_result(name, self._transport_name, result)
        return result

    async def _getVehicleSecurity(self, command: UnsignedMessage) -> VehicleStatus:
        """Sign and send a read request to the Vehicle Security computer."""
        name = vcsec_command_name(command)
        try:
            reply = await self._command(
                Domain.DOMAIN_VEHICLE_SECURITY, command.SerializeToString()
            )
        except (Exception, TeslaFleetError) as e:
            _log_command_error(name, self._transport_name, e)
            raise
        _log_command_result(name, self._transport_name, reply)
        return reply["response"]

    async def _sendInfotainment(
        self, command: Action, *, mutating: bool = True
    ) -> dict[str, Any]:
        """Sign and send a message to Infotainment computer."""
        name = infotainment_command_name(command)
        try:
            result = await self._command(
                Domain.DOMAIN_INFOTAINMENT, command.SerializeToString()
            )
        except (Exception, TeslaFleetError) as e:
            _log_command_error(name, self._transport_name, e)
            raise
        _log_command_result(name, self._transport_name, result)
        return result

    async def _getInfotainment(self, command: Action) -> VehicleData:
        """Sign and send a message to Infotainment computer."""
        name = infotainment_command_name(command)
        try:
            reply = await self._command(
                Domain.DOMAIN_INFOTAINMENT, command.SerializeToString()
            )
        except (Exception, TeslaFleetError) as e:
            _log_command_error(name, self._transport_name, e)
            raise
        _log_command_result(name, self._transport_name, reply)
        return reply["response"]

    async def handshakeVehicleSecurity(self) -> None:
        """Perform a handshake with the vehicle security domain."""
        await self._handshake(Domain.DOMAIN_VEHICLE_SECURITY)

    async def handshakeInfotainment(self) -> None:
        """Perform a handshake with the infotainment domain."""
        await self._handshake(Domain.DOMAIN_INFOTAINMENT)

    async def _handshake(self, domain: Domain) -> bool:
        """Perform a handshake with the vehicle."""

        LOGGER.debug(f"Handshake with domain {Domain.Name(domain)}")
        msg = RoutableMessage(
            to_destination=Destination(
                domain=domain,
            ),
            from_destination=Destination(routing_address=self._from_destination),
            session_info_request=SessionInfoRequest(public_key=self._public_key),
            uuid=randbytes(16),
        )

        await self._send(msg, "session_info")
        return self._sessions[domain].ready

    async def ping(self) -> dict[str, Any]:
        """Ping the vehicle."""
        return await self._sendInfotainment(
            Action(vehicleAction=VehicleAction(ping=Ping(ping_id=0))),
            mutating=False,
        )

    async def actuate_trunk(self, which_trunk: Trunk | str) -> dict[str, Any]:
        """Controls the front or rear trunk."""
        if which_trunk == Trunk.FRONT:
            return await self._sendVehicleSecurity(
                UnsignedMessage(
                    closureMoveRequest=ClosureMoveRequest(
                        frontTrunk=ClosureMoveType_E.CLOSURE_MOVE_TYPE_MOVE
                    )
                )
            )
        if which_trunk == Trunk.REAR:
            return await self._sendVehicleSecurity(
                UnsignedMessage(
                    closureMoveRequest=ClosureMoveRequest(
                        rearTrunk=ClosureMoveType_E.CLOSURE_MOVE_TYPE_MOVE
                    )
                )
            )
        raise ValueError("Invalid trunk.")

    async def adjust_volume(self, volume: float) -> dict[str, Any]:
        """Adjusts vehicle media playback volume from 0.0 to 11.0."""
        if volume < 0.0 or volume > 11.0:
            raise ValueError("Volume must a number from 0.0 to 11.0")
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    mediaUpdateVolume=MediaUpdateVolume(volume_absolute_float=volume)
                )
            )
        )

    async def auto_conditioning_start(self) -> dict[str, Any]:
        """Starts climate preconditioning."""
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    hvacAutoAction=HvacAutoAction(power_on=True)
                )
            )
        )

    async def auto_conditioning_stop(self) -> dict[str, Any]:
        """Stops climate preconditioning."""
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    hvacAutoAction=HvacAutoAction(power_on=False)
                )
            )
        )

    async def cancel_software_update(self) -> dict[str, Any]:
        """Cancels the countdown to install the vehicle software update."""
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    vehicleControlCancelSoftwareUpdateAction=VehicleControlCancelSoftwareUpdateAction()
                )
            )
        )

    async def charge_max_range(self) -> dict[str, Any]:
        """Charges in max range mode -- we recommend limiting the use of this mode to long trips."""
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    chargingStartStopAction=ChargingStartStopAction(
                        start_max_range=Void()
                    )
                )
            )
        )

    async def charge_port_door_close(self) -> dict[str, Any]:
        """Closes the charge port door."""
        return await self._sendVehicleSecurity(
            UnsignedMessage(
                closureMoveRequest=ClosureMoveRequest(
                    chargePort=ClosureMoveType_E.CLOSURE_MOVE_TYPE_CLOSE
                )
            )
        )

    async def charge_port_door_open(self) -> dict[str, Any]:
        """Opens the charge port door."""
        return await self._sendVehicleSecurity(
            UnsignedMessage(
                closureMoveRequest=ClosureMoveRequest(
                    chargePort=ClosureMoveType_E.CLOSURE_MOVE_TYPE_OPEN
                )
            )
        )

    async def charge_standard(self) -> dict[str, Any]:
        """Charges in Standard mode.

        Some vehicles reject this command with ``already_standard`` when the
        current charge limit already equals ``charge_limit_soc_std``.
        """
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    chargingStartStopAction=ChargingStartStopAction(
                        start_standard=Void()
                    )
                )
            )
        )

    async def charge_start(self) -> dict[str, Any]:
        """Starts charging the vehicle."""
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    chargingStartStopAction=ChargingStartStopAction(start=Void())
                )
            )
        )

    async def charge_stop(self) -> dict[str, Any]:
        """Stops charging the vehicle."""
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    chargingStartStopAction=ChargingStartStopAction(stop=Void())
                )
            )
        )

    async def clear_pin_to_drive_admin(self, pin: str | None = None) -> dict[str, Any]:
        """Deactivates PIN to Drive and resets the associated PIN for vehicles running firmware versions 2023.44+. This command is only accessible to fleet managers or owners.

        ``pin`` is accepted for cross-transport signature parity with the
        cloud REST endpoint, but the signed ``VehicleControlResetPinToDriveAdminAction``
        has no pin field, so it is not sent (same pattern as other documented
        cross-transport form gaps - see CLAUDE.md). Live-verified: the
        previous implementation built ``DrivingClearSpeedLimitPinAction``,
        the Speed-Limit-Mode pin clear, not a PIN-to-Drive action at all -
        confirmed by the vehicle itself rejecting a live call with reason
        ``speed_limit_mode_active``, a condition meaningful only to Speed
        Limit Mode. This action requires proof of Tesla account credentials
        (fleet-manager/owner tier) - calling it over raw BLE signing (no
        OAuth session) always raises ``TeslaFleetMessageFaultCommandRequiresAccountCredentials``;
        use the Fleet-API-relayed ``VehicleSigned`` transport instead.
        """
        return await self.reset_pin_to_drive_admin()

    async def door_lock(self) -> dict[str, Any]:
        """Locks the vehicle."""
        return await self._sendVehicleSecurity(
            UnsignedMessage(RKEAction=RKEAction_E.RKE_ACTION_LOCK)
        )

    async def door_unlock(self) -> dict[str, Any]:
        """Unlocks the vehicle."""
        return await self._sendVehicleSecurity(
            UnsignedMessage(RKEAction=RKEAction_E.RKE_ACTION_UNLOCK)
        )

    async def erase_user_data(self) -> dict[str, Any]:
        """Erases user's data from the user interface. Requires the vehicle to be in park."""
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(eraseUserDataAction=EraseUserDataAction())
            )
        )

    async def flash_lights(self) -> dict[str, Any]:
        """Briefly flashes the vehicle headlights. Requires the vehicle to be in park."""
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    vehicleControlFlashLightsAction=VehicleControlFlashLightsAction()
                )
            )
        )

    async def guest_mode(self, enable: bool) -> dict[str, Any]:
        """Restricts certain vehicle UI functionality from guest users"""
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    guestModeAction=VehicleState.GuestMode(GuestModeActive=enable)
                )
            )
        )

    async def honk_horn(self) -> dict[str, Any]:
        """Honks the vehicle horn. Requires the vehicle to be in park."""
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    vehicleControlHonkHornAction=VehicleControlHonkHornAction()
                )
            )
        )

    async def media_next_fav(self) -> dict[str, Any]:
        """Advances media player to next favorite track."""
        return await self._sendInfotainment(
            Action(vehicleAction=VehicleAction(mediaNextFavorite=MediaNextFavorite()))
        )

    async def media_next_track(self) -> dict[str, Any]:
        """Advances media player to next track."""
        return await self._sendInfotainment(
            Action(vehicleAction=VehicleAction(mediaNextTrack=MediaNextTrack()))
        )

    async def media_prev_fav(self) -> dict[str, Any]:
        """Advances media player to previous favorite track."""
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    mediaPreviousFavorite=MediaPreviousFavorite()
                )
            )
        )

    async def media_prev_track(self) -> dict[str, Any]:
        """Advances media player to previous track."""
        return await self._sendInfotainment(
            Action(vehicleAction=VehicleAction(mediaPreviousTrack=MediaPreviousTrack()))
        )

    async def media_toggle_playback(self) -> dict[str, Any]:
        """Toggles current play/pause state."""
        return await self._sendInfotainment(
            Action(vehicleAction=VehicleAction(mediaPlayAction=MediaPlayAction()))
        )

    async def media_volume_down(self) -> dict[str, Any]:
        """Turns the volume down by one."""
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    mediaUpdateVolume=MediaUpdateVolume(volume_delta=-1)
                )
            )
        )

    # This one is new
    async def media_volume_up(self) -> dict[str, Any]:
        """Turns the volume up by one."""
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    mediaUpdateVolume=MediaUpdateVolume(volume_delta=1)
                )
            )
        )

    async def navigation_gps_request(
        self, lat: float, lon: float, order: int = 0
    ) -> dict[str, Any]:
        """Start navigation to coordinates.

        ``order`` is the Tesla/protobuf remote-nav order integer: 1 replaces
        the trip, 2 prepends a stop, and 3 appends a stop. Defaults to 0
        (``REMOTE_NAV_TRIP_ORDER_UNKNOWN``) when omitted, matching the cloud path.
        """
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    navigationGpsRequest=NavigationGpsRequest(
                        lat=lat,
                        lon=lon,
                        order=order,  # pyright: ignore[reportArgumentType]
                    )
                )
            )
        )

    async def navigation_request(self, value: str) -> dict[str, Any]:
        """Sends a location to the in-vehicle navigation system."""
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    navigationRequest=NavigationRequest(destination=value)
                )
            )
        )

    async def navigation_sc_request(self, order: int) -> dict[str, Any]:
        """Start navigation to a supercharger."""
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    navigationSuperchargerRequest=NavigationSuperchargerRequest(
                        order=order
                    )
                )
            )
        )

    async def navigation_waypoints_request(self, waypoints: str) -> dict[str, Any]:
        """Sends a list of waypoints to the vehicle's navigation system."""
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    navigationWaypointsRequest=NavigationWaypointsRequest(
                        waypoints=waypoints
                    )
                )
            )
        )

    async def remote_auto_seat_climate_request(
        self, auto_seat_position: int | AutoSeat, auto_climate_on: bool
    ) -> dict[str, Any]:
        """Sets automatic seat heating and cooling.

        ``auto_seat_position`` is 1-indexed (``AutoSeat.FRONT_LEFT`` == 1),
        matching Tesla's wire values and the proto ``AutoSeatPosition_*`` enum.
        The vehicle can reject remote comfort commands when
        ``climate_state().remote_heater_control_enabled`` is false.
        """
        # AutoSeatPosition_FrontLeft = 1;
        # AutoSeatPosition_FrontRight = 2;
        # AutoSeat's 1-indexed values equal the proto AutoSeatPosition_* values,
        # so the int maps directly onto the proto enum (protobuf accepts the
        # raw int for enum fields).
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    autoSeatClimateAction=AutoSeatClimateAction(
                        carseat=[
                            AutoSeatClimateAction.CarSeat(
                                on=auto_climate_on,
                                seat_position=cast(
                                    "AutoSeatClimateAction.AutoSeatPosition_E",
                                    auto_seat_position,
                                ),
                            )
                        ]
                    )
                )
            )
        )

    async def remote_auto_steering_wheel_heat_climate_request(
        self, on: bool
    ) -> dict[str, Any]:
        """Sets automatic steering wheel heating on/off.

        The vehicle can reject remote comfort commands when
        ``climate_state().remote_heater_control_enabled`` is false.
        """
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    autoStwHeatAction=AutoStwHeatAction(
                        on=on,
                    )
                )
            )
        )

    async def remote_boombox(
        self,
        sound: int = 0,
    ) -> dict[str, Any]:
        """Plays a sound through the vehicle external speaker."""
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    boomboxAction=BoomboxAction(
                        sound=sound,
                    )
                )
            )
        )

    async def remote_seat_cooler_request(
        self, seat_position: int, seat_cooler_level: int
    ) -> dict[str, Any]:
        """Sets seat cooling."""
        # HvacSeatCoolerLevel_Unknown = 0;
        # HvacSeatCoolerLevel_Off = 1;
        # HvacSeatCoolerLevel_Low = 2;
        # HvacSeatCoolerLevel_Med = 3;
        # HvacSeatCoolerLevel_High = 4;
        # HvacSeatCoolerPosition_Unknown = 0;
        # HvacSeatCoolerPosition_FrontLeft = 1;
        # HvacSeatCoolerPosition_FrontRight = 2;
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    hvacSeatCoolerActions=HvacSeatCoolerActions(
                        hvacSeatCoolerAction=[
                            HvacSeatCoolerActions.HvacSeatCoolerAction(
                                seat_cooler_level=HvacSeatCoolerLevels[
                                    seat_cooler_level
                                ],
                                seat_position=HvacSeatCoolerPositions[seat_position],
                            )
                        ]
                    )
                )
            )
        )

    async def remote_seat_heater_request(
        self, seat_position: int, seat_heater_level: int
    ) -> dict[str, Any]:
        """Sets seat heating.

        The vehicle can reject remote comfort commands when
        ``climate_state().remote_heater_control_enabled`` is false.
        """
        # Void SEAT_HEATER_UNKNOWN = 1;
        # Void SEAT_HEATER_OFF = 2;
        # Void SEAT_HEATER_LOW = 3;
        # Void SEAT_HEATER_MED = 4;
        # Void SEAT_HEATER_HIGH = 5;
        # Void CAR_SEAT_UNKNOWN = 6;
        # Void CAR_SEAT_FRONT_LEFT = 7;
        # Void CAR_SEAT_FRONT_RIGHT = 8;
        # Void CAR_SEAT_REAR_LEFT = 9;
        # Void CAR_SEAT_REAR_LEFT_BACK = 10;
        # Void CAR_SEAT_REAR_CENTER = 11;
        # Void CAR_SEAT_REAR_RIGHT = 12;
        # Void CAR_SEAT_REAR_RIGHT_BACK = 13;
        # Void CAR_SEAT_THIRD_ROW_LEFT = 14;
        # Void CAR_SEAT_THIRD_ROW_RIGHT = 15;

        heater_action_dict = {}
        match seat_position:
            case 0:
                heater_action_dict["CAR_SEAT_FRONT_LEFT"] = Void()
            case 1:
                heater_action_dict["CAR_SEAT_FRONT_RIGHT"] = Void()
            case 2:
                heater_action_dict["CAR_SEAT_REAR_LEFT"] = Void()
            case 3:
                heater_action_dict["CAR_SEAT_REAR_LEFT_BACK"] = Void()
            case 4:
                heater_action_dict["CAR_SEAT_REAR_CENTER"] = Void()
            case 5:
                heater_action_dict["CAR_SEAT_REAR_RIGHT"] = Void()
            case 6:
                heater_action_dict["CAR_SEAT_REAR_RIGHT_BACK"] = Void()
            case 7:
                heater_action_dict["CAR_SEAT_THIRD_ROW_LEFT"] = Void()
            case 8:
                heater_action_dict["CAR_SEAT_THIRD_ROW_RIGHT"] = Void()
            case _:
                raise ValueError(f"Invalid seat position: {seat_position}")
        match seat_heater_level:
            case 0:
                heater_action_dict["SEAT_HEATER_OFF"] = Void()
            case 1:
                heater_action_dict["SEAT_HEATER_LOW"] = Void()
            case 2:
                heater_action_dict["SEAT_HEATER_MED"] = Void()
            case 3:
                heater_action_dict["SEAT_HEATER_HIGH"] = Void()
            case _:
                raise ValueError(f"Invalid seat heater level: {seat_heater_level}")

        heater_action = HvacSeatHeaterActions.HvacSeatHeaterAction(**heater_action_dict)  # pyright: ignore[reportUnknownArgumentType]
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    hvacSeatHeaterActions=HvacSeatHeaterActions(
                        hvacSeatHeaterAction=[heater_action]
                    )
                )
            )
        )

    async def remote_start_drive(self) -> dict[str, Any]:
        """Starts the vehicle remotely. Requires keyless driving to be enabled."""
        return await self._sendVehicleSecurity(
            UnsignedMessage(RKEAction=RKEAction_E.RKE_ACTION_REMOTE_DRIVE)
        )

    async def remote_steering_wheel_heat_level_request(
        self, level: int
    ) -> dict[str, Any]:
        """Sets steering wheel heat level.

        The vehicle can reject remote comfort commands when
        ``climate_state().remote_heater_control_enabled`` is false.
        """
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    stwHeatLevelAction=StwHeatLevelAction(
                        stw_heat_level=StwHeatLevels[level]
                    )
                )
            )
        )

    async def remote_steering_wheel_heater_request(self, on: bool) -> dict[str, Any]:
        """Sets steering wheel heating on/off.

        For vehicles that do not support auto steering wheel heat. The vehicle
        can reject remote comfort commands when
        ``climate_state().remote_heater_control_enabled`` is false.
        """
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    hvacSteeringWheelHeaterAction=HvacSteeringWheelHeaterAction(
                        power_on=on
                    )
                )
            )
        )

    async def reset_pin_to_drive_pin(self) -> dict[str, Any]:
        """Removes PIN to Drive. Requires the car to be in Pin to Drive mode and not in Valet mode. Note that this only works if PIN to Drive is not active. This command also requires the Tesla Vehicle Command Protocol - for more information, please see refer to the documentation here."""
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    vehicleControlResetPinToDriveAction=VehicleControlResetPinToDriveAction()
                )
            )
        )

    async def reset_valet_pin(self) -> dict[str, Any]:
        """Removes PIN for Valet Mode."""
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    vehicleControlResetValetPinAction=VehicleControlResetValetPinAction()
                )
            )
        )

    async def schedule_software_update(self, offset_sec: int) -> dict[str, Any]:
        """Schedules a vehicle software update (over the air "OTA") to be installed in the future."""
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    vehicleControlScheduleSoftwareUpdateAction=VehicleControlScheduleSoftwareUpdateAction(
                        offset_sec=offset_sec
                    )
                )
            )
        )

    async def set_bioweapon_mode(
        self, on: bool, manual_override: bool
    ) -> dict[str, Any]:
        """Turns Bioweapon Defense Mode on and off."""
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    hvacBioweaponModeAction=HvacBioweaponModeAction(
                        on=on, manual_override=manual_override
                    )
                )
            )
        )

    async def set_cabin_overheat_protection(
        self, on: bool, fan_only: bool
    ) -> dict[str, Any]:
        """Sets the vehicle overheat protection."""
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    setCabinOverheatProtectionAction=SetCabinOverheatProtectionAction(
                        on=on, fan_only=fan_only
                    )
                )
            )
        )

    async def set_charge_limit(self, percent: int) -> dict[str, Any]:
        """Sets the vehicle charge limit."""
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    chargingSetLimitAction=ChargingSetLimitAction(percent=percent)
                )
            )
        )

    async def set_charging_amps(self, charging_amps: int) -> dict[str, Any]:
        """Sets the vehicle charging amps."""
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    setChargingAmpsAction=SetChargingAmpsAction(
                        charging_amps=charging_amps
                    )
                )
            )
        )

    async def set_climate_keeper_mode(
        self, climate_keeper_mode: ClimateKeeperMode | int
    ) -> dict[str, Any]:
        """Enables climate keeper mode."""
        if isinstance(climate_keeper_mode, ClimateKeeperMode):
            climate_keeper_mode = climate_keeper_mode.value

        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    hvacClimateKeeperAction=HvacClimateKeeperAction(
                        ClimateKeeperAction=HvacClimateKeeperActions[
                            climate_keeper_mode
                        ],
                        # manual_override
                    )
                )
            )
        )

    async def set_cop_temp(
        self, cop_temp: CabinOverheatProtectionTemp | int
    ) -> dict[str, Any]:
        """Adjusts the Cabin Overheat Protection temperature (COP)."""
        if isinstance(cop_temp, CabinOverheatProtectionTemp):
            cop_temp = cop_temp.value
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    setCopTempAction=SetCopTempAction(
                        copActivationTemp=CopActivationTemps[cop_temp]
                    )
                )
            )
        )

    async def set_keep_accessory_power_mode(self, on: bool) -> dict[str, Any]:
        """Turns Keep Accessory Power mode on and off, keeping 12V accessory power available while the vehicle is parked."""
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    setKeepAccessoryPowerModeAction=SetKeepAccessoryPowerModeAction(
                        keep_accessory_power_mode=on
                    )
                )
            )
        )

    async def set_low_power_mode(self, on: bool) -> dict[str, Any]:
        """Turns Low Power mode on and off, reducing standby power consumption while the vehicle is parked."""
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    setLowPowerModeAction=SetLowPowerModeAction(low_power_mode=on)
                )
            )
        )

    async def set_pin_to_drive(self, on: bool, password: str | int) -> dict[str, Any]:
        """Sets a four-digit passcode for PIN to Drive. This PIN must then be entered before the vehicle can be driven."""
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    vehicleControlSetPinToDriveAction=VehicleControlSetPinToDriveAction(
                        on=on, password=str(password)
                    )
                )
            )
        )

    async def set_preconditioning_max(
        self, on: bool, manual_override: bool
    ) -> dict[str, Any]:
        """Sets an override for preconditioning — it should default to empty if no override is used."""
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    hvacSetPreconditioningMaxAction=HvacSetPreconditioningMaxAction(
                        on=on,
                        manual_override=manual_override,
                        # manual_override_mode
                    )
                )
            )
        )

    async def set_scheduled_charging(self, enable: bool, time: int) -> dict[str, Any]:
        """Sets the scheduled charging start time.

        ``time`` is minutes after midnight in vehicle-local time. This command
        and ``set_scheduled_departure`` both update the vehicle's shared
        ``scheduled_charging_mode``; disabling one while the other is active can
        turn scheduling off entirely.
        """
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    scheduledChargingAction=ScheduledChargingAction(
                        enabled=enable, charging_time=time
                    )
                )
            )
        )

    async def set_scheduled_departure(
        self,
        enable: bool = True,
        preconditioning_enabled: bool = False,
        preconditioning_weekdays_only: bool = False,
        departure_time: int = 0,
        off_peak_charging_enabled: bool = False,
        off_peak_charging_weekdays_only: bool = False,
        end_off_peak_time: int = 0,
    ) -> dict[str, Any]:
        """Sets the scheduled departure time.

        ``departure_time`` and ``end_off_peak_time`` are minutes after midnight
        in vehicle-local time. This command and ``set_scheduled_charging`` both
        update the vehicle's shared ``scheduled_charging_mode``; disabling one
        while the other is active can turn scheduling off entirely.

        ``preconditioning_enabled`` and ``off_peak_charging_enabled`` are
        accepted by the Python signature for compatibility but the signed
        command protobuf has no fields for them, so they are not sent.
        """

        if preconditioning_weekdays_only:
            preconditioning_times = PreconditioningTimes(weekdays=Void())
        else:
            preconditioning_times = PreconditioningTimes(all_week=Void())

        if off_peak_charging_weekdays_only:
            off_peak_charging_times = OffPeakChargingTimes(weekdays=Void())
        else:
            off_peak_charging_times = OffPeakChargingTimes(all_week=Void())

        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    scheduledDepartureAction=ScheduledDepartureAction(
                        enabled=enable,
                        departure_time=departure_time,
                        preconditioning_times=preconditioning_times,
                        off_peak_charging_times=off_peak_charging_times,
                        off_peak_hours_end_time=end_off_peak_time,
                    )
                )
            )
        )

    async def set_sentry_mode(self, on: bool) -> dict[str, Any]:
        """Enables and disables Sentry Mode. Sentry Mode allows customers to watch the vehicle cameras live from the mobile app, as well as record sentry events."""
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    vehicleControlSetSentryModeAction=VehicleControlSetSentryModeAction(
                        on=on
                    )
                )
            )
        )

    async def set_temps(
        self, driver_temp: float, passenger_temp: float
    ) -> dict[str, Any]:
        """Sets the driver and/or passenger-side cabin temperature (and other zones if sync is enabled)."""
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    hvacTemperatureAdjustmentAction=HvacTemperatureAdjustmentAction(
                        driver_temp_celsius=driver_temp,
                        passenger_temp_celsius=passenger_temp,
                    )
                )
            )
        )

    async def set_valet_mode(
        self, on: bool, password: str | int | None = None
    ) -> dict[str, Any]:
        """Turns on Valet Mode and sets a four-digit passcode that must then be entered to disable Valet Mode."""
        action = VehicleControlSetValetModeAction(on=on)
        if password is not None:
            action.password = str(password)

        return await self._sendInfotainment(
            Action(vehicleAction=VehicleAction(vehicleControlSetValetModeAction=action))
        )

    async def set_vehicle_name(self, vehicle_name: str) -> dict[str, Any]:
        """Changes the name of a vehicle. This command also requires the Tesla Vehicle Command Protocol - for more information, please see refer to the documentation here."""
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    setVehicleNameAction=SetVehicleNameAction(vehicleName=vehicle_name)
                )
            )
        )

    async def speed_limit_activate(self, pin: str | int) -> dict[str, Any]:
        """Activates Speed Limit Mode with a four-digit PIN."""
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    drivingSpeedLimitAction=DrivingSpeedLimitAction(
                        activate=True, pin=str(pin)
                    )
                )
            )
        )

    async def speed_limit_clear_pin(self, pin: str | int) -> dict[str, Any]:
        """Deactivates Speed Limit Mode and resets the associated PIN."""
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    drivingClearSpeedLimitPinAction=DrivingClearSpeedLimitPinAction(
                        pin=str(pin)
                    )
                )
            )
        )

    async def speed_limit_clear_pin_admin(self) -> dict[str, Any]:
        """Deactivates Speed Limit Mode and resets the associated PIN."""
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    drivingClearSpeedLimitPinAdminAction=DrivingClearSpeedLimitPinAdminAction()
                )
            )
        )

    async def speed_limit_deactivate(self, pin: str | int) -> dict[str, Any]:
        """Deactivates Speed Limit Mode."""
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    drivingSpeedLimitAction=DrivingSpeedLimitAction(
                        activate=False, pin=str(pin)
                    )
                )
            )
        )

    async def speed_limit_set_limit(self, limit_mph: int) -> dict[str, Any]:
        """Sets the maximum speed allowed when Speed Limit Mode is active."""
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    drivingSetSpeedLimitAction=DrivingSetSpeedLimitAction(
                        limit_mph=limit_mph
                    )
                )
            )
        )

    async def sun_roof_control(self, state: str | SunRoofCommand) -> dict[str, Any]:
        """Controls the panoramic sunroof on the Model S."""
        if isinstance(state, SunRoofCommand):
            state = state.value
        action = VehicleControlSunroofOpenCloseAction()
        match state:
            case "vent":
                action = VehicleControlSunroofOpenCloseAction(vent=Void())
            case "open":
                action = VehicleControlSunroofOpenCloseAction(open=Void())
            case "close":
                action = VehicleControlSunroofOpenCloseAction(close=Void())
            case _:
                raise ValueError(f"Invalid sunroof state: {state}")

        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(vehicleControlSunroofOpenCloseAction=action)
            )
        )

    # take_drivenote doesnt require signing

    async def trigger_homelink(
        self,
        token: str | None = None,
        lat: float | None = None,
        lon: float | None = None,
    ) -> dict[str, Any]:
        """Turns on HomeLink (used to open and close garage doors)."""
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    vehicleControlTriggerHomelinkAction=VehicleControlTriggerHomelinkAction(
                        location=LatLong(latitude=lat, longitude=lon)
                        if lat is not None and lon is not None
                        else None,
                        token=token,
                    )
                )
            )
        )

    # upcoming_calendar_entries doesnt require signing

    async def window_control(
        self,
        command: str | WindowCommand,
        lat: float | None = None,
        lon: float | None = None,
    ) -> dict[str, Any]:
        """Control the windows of a parked vehicle. Supported commands: vent and close. When closing, specify lat and lon of user to ensure they are within range of vehicle (unless this is an M3 platform vehicle)."""
        if isinstance(command, WindowCommand):
            command = command.value

        if command == "vent":
            action = VehicleControlWindowAction(vent=Void())
        elif command == "close":
            action = VehicleControlWindowAction(close=Void())
        else:
            raise ValueError(f"Invalid window command: {command}")

        return await self._sendInfotainment(
            Action(vehicleAction=VehicleAction(vehicleControlWindowAction=action))
        )

    # drivers doesnt require signing
    # drivers_remove doesnt require signing
    # mobile_enabled

    async def nearby_charging_sites(
        self,
        count: int | None = None,
        radius: int | None = None,
        detail: bool | None = None,
    ) -> dict[str, Any]:
        """Returns the charging sites near the current location of the vehicle."""
        action = GetNearbyChargingSites()
        if count is not None:
            action.count = count
        if radius is not None:
            action.radius = radius
        if detail is not None:
            action.include_meta_data = detail

        return await self._sendInfotainment(
            Action(vehicleAction=VehicleAction(getNearbyChargingSites=action)),
            mutating=False,
        )

    # options doesnt require signing
    # recent_alerts doesnt require signing
    # release_notes doesnt require signing
    # service_data doesnt require signing
    # share_invites doesnt require signing
    # share_invites_create doesnt require signing
    # share_invites_redeem doesnt require signing
    # share_invites_revoke doesnt require signing
    # signed command doesnt require signing
    # vehicle doesnt require signing
    # vehicle_data doesnt require signing
    # wake_up doesnt require signing
    # warranty_details doesnt require signing
    # fleet_status doesnt require signing

    async def fleet_telemetry_config_create(
        self, config: dict[str, Any]
    ) -> dict[str, Any]:
        """Configures fleet telemetry."""
        raise NotImplementedError

    # fleet_telemetry_config_get doesnt require signing
    # fleet_telemetry_config_delete doesnt require signing

    async def set_recirculation(self, on: bool) -> dict[str, Any]:
        """Sets HVAC recirculation mode on/off."""
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    hvacRecirculationAction=HvacRecirculationAction(on=on)
                )
            )
        )

    async def dashcam_save_clip(self) -> dict[str, Any]:
        """Saves a dashcam clip."""
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    dashcamSaveClipAction=DashcamSaveClipAction()
                )
            )
        )

    async def set_suspension_level(self, level: int) -> dict[str, Any]:
        """Sets the vehicle suspension level (1=entry, 2=low, 3=medium, 4=high, 5=very_high, 6=extract)."""
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    setSuspensionLevelAction=SetSuspensionLevelAction(
                        suspension_level=level  # pyright: ignore[reportArgumentType]
                    )
                )
            )
        )

    async def start_light_show(
        self,
        show_index: int = 0,
        start_time: int = 0,
        volume: float = 0.0,
        dance_moves: bool = False,
    ) -> dict[str, Any]:
        """Starts a light show."""
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    startLightShowAction=StartLightShowAction(
                        show_index=show_index,
                        start_time=start_time,
                        volume=volume,
                        dance_moves=dance_moves,
                    )
                )
            )
        )

    async def stop_light_show(self) -> dict[str, Any]:
        """Stops the current light show."""
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(stopLightShowAction=StopLightShowAction())
            )
        )

    async def cancel_soh_test(self) -> dict[str, Any]:
        """Cancels a State of Health test."""
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(cancelSohTestAction=CancelSohTestAction())
            )
        )

    async def add_charge_schedule(
        self,
        days_of_week: str | int,
        enabled: bool,
        lat: float,
        lon: float,
        start_time: int | None = None,
        end_time: int | None = None,
        one_time: bool | None = None,
        id: int | None = None,
        name: str | None = None,
    ) -> dict[str, Any]:
        """Add a schedule for vehicle charging."""
        if not start_time and not end_time:
            raise ValueError("Either start_time or end_time or both must be provided")
        schedule = ChargeSchedule(
            days_of_week=int(days_of_week),
            enabled=enabled,
            start_enabled=start_time is not None,
            end_enabled=end_time is not None,
            latitude=lat,
            longitude=lon,
        )
        if start_time is not None:
            schedule.start_time = start_time
        if end_time is not None:
            schedule.end_time = end_time
        if one_time is not None:
            schedule.one_time = one_time
        if id is not None:
            schedule.id = id
        if name is not None:
            schedule.name = name
        return await self._sendInfotainment(
            Action(vehicleAction=VehicleAction(addChargeScheduleAction=schedule))
        )

    async def remove_charge_schedule(self, id: int) -> dict[str, Any]:
        """Removes the scheduled charging settings."""
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    removeChargeScheduleAction=RemoveChargeScheduleAction(id=id)
                )
            )
        )

    async def add_precondition_schedule(
        self,
        days_of_week: str | int,
        enabled: bool,
        lat: float,
        lon: float,
        precondition_time: int,
        id: int | None = None,
        one_time: bool | None = None,
        name: str | None = None,
    ) -> dict[str, Any]:
        """Add or modify a preconditioning schedule."""
        schedule = PreconditionSchedule(
            days_of_week=int(days_of_week),
            enabled=enabled,
            precondition_time=precondition_time,
            latitude=lat,
            longitude=lon,
        )
        if one_time is not None:
            schedule.one_time = one_time
        if id is not None:
            schedule.id = id
        if name is not None:
            schedule.name = name
        return await self._sendInfotainment(
            Action(vehicleAction=VehicleAction(addPreconditionScheduleAction=schedule))
        )

    async def remove_precondition_schedule(self, id: int) -> dict[str, Any]:
        """Removes the scheduled precondition settings."""
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    removePreconditionScheduleAction=RemovePreconditionScheduleAction(
                        id=id
                    )
                )
            )
        )

    async def batch_remove_charge_schedules(
        self, home: bool, work: bool, other: bool
    ) -> dict[str, Any]:
        """Batch removes charge schedules by location type."""
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    batchRemoveChargeSchedulesAction=BatchRemoveChargeSchedulesAction(
                        home=home, work=work, other=other
                    )
                )
            )
        )

    async def batch_remove_precondition_schedules(
        self, home: bool, work: bool, other: bool
    ) -> dict[str, Any]:
        """Batch removes precondition schedules by location type."""
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    batchRemovePreconditionSchedulesAction=BatchRemovePreconditionSchedulesAction(
                        home=home, work=work, other=other
                    )
                )
            )
        )

    async def set_powershare_feature(self, on: bool) -> dict[str, Any]:
        """Enables or disables the Powershare feature."""
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    setPowershareFeatureAction=SetPowershareFeatureAction(
                        powershare_feature_request=(
                            SetPowershareFeatureAction.POWERSHARE_FEATURE_REQUEST_ON
                            if on
                            else SetPowershareFeatureAction.POWERSHARE_FEATURE_REQUEST_OFF
                        )
                    )
                )
            )
        )

    async def set_powershare_request(self, on: bool) -> dict[str, Any]:
        """Enables or disables powershare."""
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    setPowershareRequestAction=SetPowershareRequestAction(
                        powershare_request=(
                            SetPowershareRequestAction.POWERSHARE_REQUEST_ON
                            if on
                            else SetPowershareRequestAction.POWERSHARE_REQUEST_OFF
                        )
                    )
                )
            )
        )

    async def set_powershare_discharge_limit(self, percent: int) -> dict[str, Any]:
        """Sets the Powershare discharge limit percentage."""
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    setPowershareDischargeLimitAction=SetPowershareDischargeLimitAction(
                        powershare_discharge_limit=percent
                    )
                )
            )
        )

    async def set_outlets(self, request: int) -> dict[str, Any]:
        """Sets outlets on/off (0=off, 1=cabin+bed, 2=cabin)."""
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    setOutletsOnOffAction=SetOutletsOnOffAction(outlet_request=request)  # pyright: ignore[reportArgumentType]
                )
            )
        )

    async def set_outlet_timer(self, num_minutes: int) -> dict[str, Any]:
        """Sets the outlet timer in minutes."""
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    setOutletTimerAction=SetOutletTimerAction(num_minutes=num_minutes)
                )
            )
        )

    async def set_outlet_soc_limit(self, percent: int) -> dict[str, Any]:
        """Sets the outlet SOC limit percentage."""
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    setOutletSocLimitAction=SetOutletSocLimitAction(percent=percent)
                )
            )
        )

    async def set_power_feed(self, request: int) -> dict[str, Any]:
        """Sets power feed on/off (0=off, 1=feed1, 2=feed2, 3=both)."""
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    setPowerFeedOnOffAction=SetPowerFeedOnOffAction(
                        power_feed_request=request  # pyright: ignore[reportArgumentType]
                    )
                )
            )
        )

    async def set_power_feed_timer(self, num_minutes: int) -> dict[str, Any]:
        """Sets the power feed timer in minutes."""
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    setPowerFeedTimerAction=SetPowerFeedTimerAction(
                        num_minutes=num_minutes
                    )
                )
            )
        )

    async def set_power_feed_soc_limit(self, percent: int) -> dict[str, Any]:
        """Sets the power feed SOC limit percentage."""
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    setPowerFeedSocLimitAction=SetPowerFeedSocLimitAction(
                        percent=percent
                    )
                )
            )
        )

    async def set_lightbar_brightness(self, brightness: int) -> dict[str, Any]:
        """Sets the lightbar brightness."""
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    setLightbarBrightnessAction=SetLightbarBrightnessAction(
                        brightness_request=brightness
                    )
                )
            )
        )

    async def set_lightbar_middle(self, on: bool) -> dict[str, Any]:
        """Enables or disables the lightbar middle light."""
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    setLightbarMiddleAction=SetLightbarMiddleAction(
                        middle_light_request=on
                    )
                )
            )
        )

    async def set_lightbar_ditch(self, on: bool) -> dict[str, Any]:
        """Enables or disables the ditch lights."""
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    setLightbarDitchAction=SetLightbarDitchAction(
                        ditch_lights_request=on
                    )
                )
            )
        )

    async def set_front_zone_lights(self, level: int) -> dict[str, Any]:
        """Sets front zone light level (0=off, 1=low, 2=med, 3=high)."""
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    setFrontZoneLightRequestAction=SetZoneLightRequestAction(
                        zone_light_request=level  # pyright: ignore[reportArgumentType]
                    )
                )
            )
        )

    async def set_rear_zone_lights(self, level: int) -> dict[str, Any]:
        """Sets rear zone light level (0=off, 1=low, 2=med, 3=high)."""
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    setRearZoneLightRequestAction=SetZoneLightRequestAction(
                        zone_light_request=level  # pyright: ignore[reportArgumentType]
                    )
                )
            )
        )

    async def set_trailer_light_test(self, on: bool) -> dict[str, Any]:
        """Starts or stops trailer light test."""
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    setTrailerLightTestStartStopAction=SetTrailerLightTestStartStopAction(
                        start_stop=on
                    )
                )
            )
        )

    async def set_truck_bed_light_auto(self, on: bool) -> dict[str, Any]:
        """Sets truck bed light auto state."""
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    setTruckBedLightAutoStateAction=SetTruckBedLightAutoStateAction(
                        power_state=on
                    )
                )
            )
        )

    async def set_truck_bed_light_brightness(self, brightness: int) -> dict[str, Any]:
        """Sets truck bed light brightness."""
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    setTruckBedLightBrightnessAction=SetTruckBedLightBrightnessAction(
                        brightness=brightness
                    )
                )
            )
        )

    async def set_tent_mode(self, on: bool) -> dict[str, Any]:
        """Enables or disables tent mode."""
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    setTentModeRequestAction=SetTentModeRequestAction(on=on)
                )
            )
        )

    async def parental_controls(self, activate: bool, pin: str) -> dict[str, Any]:
        """Activates or deactivates parental controls with PIN."""
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    parentalControlsAction=ParentalControlsAction(
                        activate=activate, pin=pin
                    )
                )
            )
        )

    async def parental_controls_clear_pin(self, pin: str) -> dict[str, Any]:
        """Clears the parental controls PIN."""
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    parentalControlsClearPinAction=ParentalControlsClearPinAction(
                        pin=pin
                    )
                )
            )
        )

    async def parental_controls_clear_pin_admin(self) -> dict[str, Any]:
        """Clears the parental controls PIN as admin (fleet manager/owner)."""
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    parentalControlsClearPinAdminAction=ParentalControlsClearPinAdminAction()
                )
            )
        )

    async def parental_controls_enable_setting(
        self, setting: int, enable: bool
    ) -> dict[str, Any]:
        """Enables or disables a parental controls setting (1=speed_limit, 2=acceleration, 3=safety_features, 4=curfew)."""
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    parentalControlsEnableSettingsAction=ParentalControlsEnableSettingsAction(
                        setting=setting,  # pyright: ignore[reportArgumentType]
                        enable=enable,
                    )
                )
            )
        )

    async def parental_controls_set_speed_limit(
        self, limit_mph: float
    ) -> dict[str, Any]:
        """Sets the parental controls speed limit."""
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    parentalControlsSetSpeedLimitAction=ParentalControlsSetSpeedLimitAction(
                        limit_mph=limit_mph
                    )
                )
            )
        )

    async def update_charge_on_solar(
        self, enabled: bool, lower_charge_limit: float, upper_charge_limit: float
    ) -> dict[str, Any]:
        """Updates charge on solar feature settings."""
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    updateChargeOnSolarFeatureRequest=UpdateChargeOnSolarFeatureRequest(
                        charge_on_solar=ChargeOnSolarFeature(
                            enabled=enabled,
                            lower_charge_limit=lower_charge_limit,
                            upper_charge_limit=upper_charge_limit,
                        )
                    )
                )
            )
        )

    async def get_charge_on_solar(self) -> dict[str, Any]:
        """Gets charge on solar feature settings."""
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    getChargeOnSolarFeatureRequest=GetChargeOnSolarFeatureRequest()
                )
            ),
            mutating=False,
        )

    async def navigation_gps_destination_request(
        self, lat: float, lon: float, destination: str, order: int
    ) -> dict[str, Any]:
        """Navigate to coordinates with a named destination string.

        ``order`` is the Tesla/protobuf remote-nav order integer: 1 replaces
        the trip, 2 prepends a stop, and 3 appends a stop.
        """
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    navigationGpsDestinationRequest=NavigationGpsDestinationRequest(
                        lat=lat,
                        lon=lon,
                        destination=destination,
                        order=order,  # pyright: ignore[reportArgumentType]
                    )
                )
            )
        )

    async def reset_pin_to_drive_admin(self) -> dict[str, Any]:
        """Resets PIN to Drive as admin (fleet manager/owner). Requires firmware 2023.44+."""
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    vehicleControlResetPinToDriveAdminAction=VehicleControlResetPinToDriveAdminAction()
                )
            )
        )

    async def open_tonneau(self) -> dict[str, Any]:
        """Opens the tonneau cover."""
        return await self._sendVehicleSecurity(
            UnsignedMessage(
                closureMoveRequest=ClosureMoveRequest(
                    tonneau=ClosureMoveType_E.CLOSURE_MOVE_TYPE_OPEN
                )
            )
        )

    async def close_tonneau(self) -> dict[str, Any]:
        """Closes the tonneau cover."""
        return await self._sendVehicleSecurity(
            UnsignedMessage(
                closureMoveRequest=ClosureMoveRequest(
                    tonneau=ClosureMoveType_E.CLOSURE_MOVE_TYPE_CLOSE
                )
            )
        )

    async def stop_tonneau(self) -> dict[str, Any]:
        """Stops the tonneau cover."""
        return await self._sendVehicleSecurity(
            UnsignedMessage(
                closureMoveRequest=ClosureMoveRequest(
                    tonneau=ClosureMoveType_E.CLOSURE_MOVE_TYPE_STOP
                )
            )
        )

    async def auto_secure_vehicle(self) -> dict[str, Any]:
        """Auto secures the vehicle (locks, closes windows, etc.)."""
        return await self._sendVehicleSecurity(
            UnsignedMessage(RKEAction=RKEAction_E.RKE_ACTION_AUTO_SECURE_VEHICLE)
        )

    #
    # Included per the captain's full-proto-coverage directive; each has no
    # known third-party consumer use case today, unlike every other command
    # in this file. See AGENTS.md for detail on why each is niche.

    async def pii_key_request(
        self, subscriber_public_key: str, pii_key_expiration: int
    ) -> dict[str, Any]:
        """Requests a PII (privacy/telemetry pseudonymization) key.

        ``pii_key_expiration`` is a Unix timestamp in seconds.
        """
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    piiKeyRequest=PiiKeyRequest(
                        subscriber_public_key=subscriber_public_key,
                        pii_key_expiration=Timestamp(seconds=pii_key_expiration),
                    )
                )
            )
        )

    async def pseudonym_sync_request(
        self, last_known_pseudonym_hashed: bytes
    ) -> dict[str, Any]:
        """Syncs the vehicle's privacy/telemetry pseudonym with a previously known hashed value."""
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    pseudonymSyncRequest=PseudonymSyncRequest(
                        last_known_pseudonym_hashed=last_known_pseudonym_hashed
                    )
                )
            )
        )

    async def tesla_auth_response(
        self,
        client_id: str,
        scope: str,
        access_token: str,
        refresh_token: str,
        expiry_timestamp: int,
        error: str = "",
        scoped_token: str = "",
    ) -> dict[str, Any]:
        """Passes a completed "Sign in with Tesla" OAuth response to the vehicle screen.

        This is a pass-through: the caller must already have a completed OAuth
        response from elsewhere in their own auth flow; the library cannot
        originate these fields itself.
        """
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    teslaAuthResponseAction=TeslaAuthResponseAction(
                        client_id=client_id,
                        scope=scope,
                        access_token=access_token,
                        refresh_token=refresh_token,
                        expiry_timestamp=expiry_timestamp,
                        error=error,
                        scoped_token=scoped_token,
                    )
                )
            )
        )

    async def setup_cloud_profile_with_local_profile_uuid(
        self,
        cloud_vault_uuid: str,
        local_profile_uuid: str,
        delete_local_profile_after_setup: bool = False,
    ) -> dict[str, Any]:
        """Links a local Tesla profile to a cloud vault profile UUID."""
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    setupCloudProfileWithLocalProfileUuidAction=SetupCloudProfileWithLocalProfileUuidAction(
                        cloud_vault_uuid=cloud_vault_uuid,
                        local_profile_uuid=local_profile_uuid,
                        delete_local_profile_after_setup=delete_local_profile_after_setup,
                    )
                )
            )
        )

    async def get_local_profiles_for_vault_uuid(
        self, vault_uuid: str
    ) -> dict[str, Any]:
        """Gets local Tesla profiles associated with a cloud vault UUID."""
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    getLocalProfilesForVaultUuidAction=GetLocalProfilesForVaultUuidAction(
                        vault_uuid=vault_uuid
                    )
                )
            ),
            mutating=False,
        )

    # No confirmation guard, matching the existing erase_user_data()
    # precedent: this library exposes the signed command as-is and leaves
    # any confirmation UX to the caller.

    async def format_usb(self) -> dict[str, Any]:
        """Formats the USB drive connected to the vehicle, erasing all files on it. Irreversible."""
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    formatUsbAction=FormatUSBAction(format_usb=True)
                )
            )
        )

    async def delete_dashcam_clips(self) -> dict[str, Any]:
        """Deletes all dashcam clips stored on the vehicle. Irreversible."""
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    deleteDashcamClipsAction=DeleteDashcamClipsAction(delete_clips=True)
                )
            )
        )

    async def set_temperature_unit(self, unit: TemperatureUnit | int) -> dict[str, Any]:
        """Sets the vehicle's displayed temperature unit."""
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    setTemperatureUnitAction=SetTemperatureUnitAction(
                        unit=unit  # pyright: ignore[reportArgumentType]
                    )
                )
            )
        )

    async def set_distance_unit(self, unit: DistanceUnit | int) -> dict[str, Any]:
        """Sets the vehicle's displayed distance unit."""
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    setDistanceUnitAction=SetDistanceUnitAction(
                        unit=unit  # pyright: ignore[reportArgumentType]
                    )
                )
            )
        )

    async def set_time_display_format(
        self, format: TimeDisplayFormat | int
    ) -> dict[str, Any]:
        """Sets the vehicle's displayed clock format (12h/24h)."""
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    setTimeDisplayFormatAction=SetTimeDisplayFormatAction(
                        format=format  # pyright: ignore[reportArgumentType]
                    )
                )
            )
        )

    async def set_tire_pressure_unit(
        self, unit: TirePressureUnit | int
    ) -> dict[str, Any]:
        """Sets the vehicle's displayed tire pressure unit."""
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    setTirePressureUnitAction=SetTirePressureUnitAction(
                        unit=unit  # pyright: ignore[reportArgumentType]
                    )
                )
            )
        )

    async def set_energy_display_format(
        self, format: EnergyDisplayFormat | int
    ) -> dict[str, Any]:
        """Sets the vehicle's displayed energy/range unit (percentage/distance)."""
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    setEnergyDisplayFormatAction=SetEnergyDisplayFormatAction(
                        format=format  # pyright: ignore[reportArgumentType]
                    )
                )
            )
        )

    async def set_phone_setting_preferences(
        self,
        font_size: PhoneFontSize | int = PhoneFontSize.STANDARD,
        *,
        distance_unit: DistanceUnit | int | None = None,
        temperature_unit: TemperatureUnit | int | None = None,
    ) -> dict[str, Any]:
        """Sets paired-phone display preferences: font size and, optionally, distance/temperature units."""
        action = SetPhoneSettingPreferencesAction(
            font_size=font_size  # pyright: ignore[reportArgumentType]
        )
        if distance_unit is not None or temperature_unit is not None:
            unit_kwargs: dict[str, Any] = {}
            if distance_unit is not None:
                unit_kwargs["distance_unit"] = distance_unit
            if temperature_unit is not None:
                unit_kwargs["temperature_unit"] = temperature_unit
            action.unit_preferences.CopyFrom(PhoneUnitPreferences(**unit_kwargs))
        return await self._sendInfotainment(
            Action(vehicleAction=VehicleAction(setPhoneSettingPreferencesAction=action))
        )

    async def upcoming_calendar_entries(self, calendar_data: str) -> dict[str, Any]:
        """Sends upcoming calendar entries to the vehicle.

        Signed-command sibling of the REST-only ``VehicleFleet.upcoming_calendar_entries``.
        """
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    uiSetUpcomingCalendarEntries=UiSetUpcomingCalendarEntries(
                        calendar_data=calendar_data
                    )
                )
            )
        )

    async def take_drivenote(self, note: str) -> dict[str, Any]:
        """Records a drive note.

        Signed-command sibling of the REST-only ``VehicleFleet.take_drivenote``.
        """
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    takeDrivenoteAction=TakeDrivenoteAction(note=note)
                )
            )
        )

    async def video_request(self, url: str) -> dict[str, Any]:
        """Requests the vehicle open a video stream from the given URL (e.g. sentry/dashcam viewer)."""
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    videoRequestAction=VideoRequestAction(url=url)
                )
            )
        )

    async def navigation_route(self) -> dict[str, Any]:
        """Triggers vehicle route navigation."""
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    navigationRouteAction=NavigationRouteAction()
                )
            )
        )

    async def get_messages(self) -> dict[str, Any]:
        """Gets vehicle in-car messages."""
        return await self._sendInfotainment(
            Action(vehicleAction=VehicleAction(getMessagesAction=GetMessagesAction())),
            mutating=False,
        )

    async def set_rate_tariff(
        self,
        seasons: SetRateTariffRequest.Seasons,
        tariff: SetRateTariffRequest.Tariff | None = None,
    ) -> dict[str, Any]:
        """Sets a time-of-use rate tariff schedule for charge-on-solar-style optimization.

        ``seasons``/``tariff`` are ``tesla_protocol`` message types
        (``SetRateTariffRequest.Seasons``/``.Tariff``) - the tariff schedule is
        deeply nested (up to 5 named seasons, each with 4 time-of-use period
        types), so construct them directly rather than through a parallel
        flattened API.
        """
        action = SetRateTariffRequest(seasons=seasons)
        if tariff is not None:
            action.tariff.CopyFrom(tariff)
        return await self._sendInfotainment(
            Action(vehicleAction=VehicleAction(setRateTariffRequest=action))
        )

    async def get_rate_tariff(self) -> dict[str, Any]:
        """Gets the current time-of-use rate tariff schedule."""
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(getRateTariffRequest=GetRateTariffRequest())
            ),
            mutating=False,
        )

    async def add_managed_charging_site(
        self, public_key: str, lat: float, lon: float
    ) -> dict[str, Any]:
        """Registers a managed charging site (utility managed-charging program) for this vehicle."""
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    addManagedChargingSiteRequest=AddManagedChargingSiteRequest(
                        site=ManagedChargingSite(
                            public_key=public_key,
                            manager_type=ManagerType(site_controller=SiteController()),
                            lat_lon=LatLong(latitude=lat, longitude=lon),
                        )
                    )
                )
            )
        )

    async def remove_managed_charging_site(self, public_key: str) -> dict[str, Any]:
        """Removes a previously-registered managed charging site by its public key."""
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    removeManagedChargingSiteRequest=RemoveManagedChargingSiteRequest(
                        public_key=public_key
                    )
                )
            )
        )

    async def get_managed_charging_sites(self) -> dict[str, Any]:
        """Gets the list of registered managed charging sites."""
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    getManagedChargingSitesRequest=GetManagedChargingSitesRequest()
                )
            ),
            mutating=False,
        )

    async def set_discharge_limit(self, discharge_limit: int) -> dict[str, Any]:
        """Sets the vehicle's general discharge limit.

        Not the same feature as ``set_powershare_discharge_limit``
        (``SetPowershareDischargeLimitAction``, a distinct proto message).
        """
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    setDischargeLimitAction=SetDischargeLimitAction(
                        discharge_limit=discharge_limit
                    )
                )
            )
        )

    async def bluetooth_classic_pairing_request(
        self, name: str, mac_address: bytes
    ) -> dict[str, Any]:
        """Requests Bluetooth Classic (not BLE) pairing with a phone for calls/audio."""
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    bluetoothClassicPairingRequest=BluetoothClassicPairingRequest(
                        utf8_name=name,
                        mac_address=mac_address,
                    )
                )
            )
        )

    async def bandwidth_test(self, requested_size: int) -> dict[str, Any]:
        """Runs a diagnostic bandwidth test of the given size in bytes."""
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    bandwidthTest=BandwidthTest(requested_size=requested_size)
                )
            )
        )

    async def fetch_keys_info(self) -> dict[str, Any]:
        """Gets information about keys paired with the vehicle."""
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(fetchKeysInfoAction=FetchKeysInfoAction())
            ),
            mutating=False,
        )
