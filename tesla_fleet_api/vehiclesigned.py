from __future__ import annotations
import base64
from random import randbytes
from typing import Any, TYPE_CHECKING
import time
import struct
import hmac
import hashlib
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import PublicFormat, Encoding
from asyncio import Lock, sleep

from tesla_fleet_api.pb2.errors_pb2 import GenericError_E

from .exceptions import MESSAGE_FAULTS, SIGNED_MESSAGE_INFORMATION_FAULTS, TeslaFleetMessageFaultIncorrectEpoch, TeslaFleetMessageFaultInvalidTokenOrCounter

from .const import (
    LOGGER,
    Trunk,
    ClimateKeeperMode,
    CabinOverheatProtectionTemp,
    SunRoofCommand,
    WindowCommand,
)
from .vehiclespecific import VehicleSpecific

from .pb2.universal_message_pb2 import (
    OPERATIONSTATUS_WAIT,
    OPERATIONSTATUS_ERROR,
    DOMAIN_VEHICLE_SECURITY,
    DOMAIN_INFOTAINMENT,
    Domain,
    RoutableMessage,
)
from .pb2.car_server_pb2 import (
    Response,
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
    # NearbyChargingSites,
    # Superchargers,
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
    # Ping,
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
)
from .pb2.vehicle_pb2 import VehicleState
from .pb2.vcsec_pb2 import (
    # SignedMessage_information_E,
    OPERATIONSTATUS_OK,
    FromVCSECMessage,
    UnsignedMessage,
    RKEAction_E,
    ClosureMoveRequest,
    ClosureMoveType_E,
)
from .pb2.signatures_pb2 import (
    SIGNATURE_TYPE_HMAC_PERSONALIZED,
    TAG_DOMAIN,
    TAG_SIGNATURE_TYPE,
    SessionInfo,
    HMAC_Personalized_Signature_Data,
    TAG_PERSONALIZATION,
    TAG_EPOCH,
    TAG_EXPIRES_AT,
    TAG_COUNTER,
    TAG_END,
)
from .pb2.common_pb2 import (
    Void,
    PreconditioningTimes,
    OffPeakChargingTimes,
    # ChargeSchedule,
    # PreconditionSchedule,
)

if TYPE_CHECKING:
    from .vehicle import Vehicle


class Session:
    """A connect to a domain"""

    key: bytes
    counter: int
    epoch: bytes
    delta: int
    hmac: bytes
    publicKey: bytes
    lock: Lock

    def __init__(self):
        self.lock = Lock()
        self.counter = 0

    def update(self, sessionInfo: SessionInfo, privateKey: ec.EllipticCurvePrivateKey):
        """Update the session with new information"""
        self.counter = sessionInfo.counter
        self.epoch = sessionInfo.epoch
        self.delta = int(time.time()) - sessionInfo.clock_time
        if (self.publicKey != sessionInfo.publicKey):
            self.publicKey = sessionInfo.publicKey
            self.key = hashlib.sha1(
                privateKey.exchange(
                    ec.ECDH(),
                    ec.EllipticCurvePublicKey.from_encoded_point(
                        ec.SECP256R1(), self.publicKey
                    ),
                ),
            ).digest()[:16]
            self.hmac = hmac.new(
                self.key, "authenticated command".encode(), hashlib.sha256
            ).digest()

    def get(self) -> HMAC_Personalized_Signature_Data:
        """Sign a command and return session metadata"""
        self.counter = self.counter+1
        return HMAC_Personalized_Signature_Data(
            epoch=self.epoch,
            counter=self.counter,
            expires_at=int(time.time()) - self.delta + 10,
        )


class VehicleSigned(VehicleSpecific):
    """Class describing the Tesla Fleet API vehicle endpoints and commands for a specific vehicle with command signing."""

    private_key: ec.EllipticCurvePrivateKey
    _public_key: bytes
    _from_destination: bytes
    _sessions: dict[int, Session]

    def __init__(
        self, parent: Vehicle, vin: str, key: ec.EllipticCurvePrivateKey | None = None
    ):
        super().__init__(parent, vin)
        if key:
            self.private_key = key
        elif parent._parent.private_key:
            self.private_key = parent._parent.private_key
        else:
            raise ValueError("No private key.")

        self._public_key = self.private_key.public_key().public_bytes(
            encoding=Encoding.X962, format=PublicFormat.UncompressedPoint
        )
        self._from_destination = randbytes(16)
        self._sessions = {}

    async def _send(self, msg: RoutableMessage) -> RoutableMessage:
        """Serialize a message and send to the signed command endpoint."""

        async with self._sessions[msg.to_destination.domain].lock:
            resp = await self.signed_command(
                base64.b64encode(msg.SerializeToString()).decode()
            )

            resp_msg = RoutableMessage.FromString(base64.b64decode(resp["response"]))

            # Check UUID?
            # Check RoutingAdress?

            if resp_msg.session_info:
                self._sessions[resp_msg.from_destination.domain].update(
                    SessionInfo.FromString(resp_msg.session_info), self.private_key
                )

            if resp_msg.signedMessageStatus.signed_message_fault:
                raise MESSAGE_FAULTS[resp_msg.signedMessageStatus.signed_message_fault]

            return resp_msg

    async def _handshake(self, domain: Domain) -> Session:
        """Perform a handshake with the vehicle."""
        if session := self._sessions.get(domain):
            return session
        self._sessions[domain] = Session()

        LOGGER.debug(f"Handshake with domain {Domain.Name(domain)}")
        msg = RoutableMessage()
        msg.to_destination.domain = domain
        msg.from_destination.routing_address = self._from_destination
        msg.session_info_request.public_key = self._public_key
        msg.uuid = randbytes(16)

        # Send handshake message
        await self._send(msg)

        return self._sessions[domain]

    async def _sendVehicleSecurity(self, command: UnsignedMessage) -> dict[str, Any]:
        """Sign and send a message to Infotainment computer."""
        return await self._sign(DOMAIN_VEHICLE_SECURITY, command.SerializeToString())

    async def _sendInfotainment(self, command: Action) -> dict[str, Any]:
        """Sign and send a message to Infotainment computer."""
        return await self._sign(DOMAIN_INFOTAINMENT, command.SerializeToString())

    async def _sign(
        self, domain: Domain, command: bytes, attempt: int = 1
    ) -> dict[str, Any]:
        """Send a signed message to the vehicle."""
        LOGGER.debug(f"Sending to domain {Domain.Name(domain)}")

        session = await self._handshake(domain)
        hmac_personalized = session.get()

        msg = RoutableMessage()
        msg.to_destination.domain = domain
        msg.from_destination.routing_address = self._from_destination
        msg.protobuf_message_as_bytes = command
        msg.uuid = randbytes(16)

        metadata = bytes([
            TAG_SIGNATURE_TYPE,
            1,
            SIGNATURE_TYPE_HMAC_PERSONALIZED,
            TAG_DOMAIN,
            1,
            domain,
            TAG_PERSONALIZATION,
            17,
            *self.vin.encode(),
            TAG_EPOCH,
            len(hmac_personalized.epoch),
            *hmac_personalized.epoch,
            TAG_EXPIRES_AT,
            4,
            *struct.pack(">I", hmac_personalized.expires_at),
            TAG_COUNTER,
            4,
            *struct.pack(">I", hmac_personalized.counter),
            TAG_END,
        ])

        hmac_personalized.tag = hmac.new(
            session.hmac, metadata + command, hashlib.sha256
        ).digest()

        # I think this whole section could be improved
        msg.signature_data.HMAC_Personalized_data.CopyFrom(hmac_personalized)
        msg.signature_data.signer_identity.public_key = self._public_key

        try:
            resp = await self._send(msg)
        except (
            TeslaFleetMessageFaultIncorrectEpoch,
            TeslaFleetMessageFaultInvalidTokenOrCounter,
        ) as e:
            attempt += 1
            if attempt > 3:
                # We tried 3 times, give up, raise the error
                raise e
            return await self._sign(domain, command, attempt)

        if resp.signedMessageStatus.operation_status == OPERATIONSTATUS_WAIT:
            attempt += 1
            if attempt > 3:
                # We tried 3 times, give up, raise the error
                return {"response": {"result": False, "reason": "Too many retries"}}
            async with session.lock:
                await sleep(2)
            return await self._sign(domain, command, attempt)

        if resp.HasField("protobuf_message_as_bytes"):
            if(resp.from_destination.domain == DOMAIN_VEHICLE_SECURITY):
                vcsec = FromVCSECMessage.FromString(resp.protobuf_message_as_bytes)
                LOGGER.debug("VCSEC Response: %s", vcsec)
                if vcsec.HasField("nominalError"):
                    LOGGER.error("Command failed with reason: %s", vcsec.nominalError.genericError)
                    return {
                        "response": {
                            "result": False,
                            "reason": GenericError_E.Name(vcsec.nominalError.genericError)
                        }
                    }
                elif vcsec.commandStatus.operationStatus == OPERATIONSTATUS_OK:
                    return {"response": {"result": True, "reason": ""}}
                elif vcsec.commandStatus.operationStatus == OPERATIONSTATUS_WAIT:
                    attempt += 1
                    if attempt > 3:
                        # We tried 3 times, give up, raise the error
                        return {"response": {"result": False, "reason": "Too many retries"}}
                    async with session.lock:
                        await sleep(2)
                    return await self._sign(domain, command, attempt)
                elif vcsec.commandStatus.operationStatus == OPERATIONSTATUS_ERROR:
                    if(resp.HasField("signedMessageStatus")):
                        raise SIGNED_MESSAGE_INFORMATION_FAULTS[vcsec.commandStatus.signedMessageStatus.signedMessageInformation]

            elif(resp.from_destination.domain == DOMAIN_INFOTAINMENT):
                response = Response.FromString(resp.protobuf_message_as_bytes)
                LOGGER.debug("Infotainment Response: %s", response)
                if (response.HasField("ping")):
                    print(response.ping)
                    return {
                        "response": {
                            "result": True,
                            "reason": response.ping.local_timestamp
                        }
                    }
                if response.HasField("actionStatus"):
                    return {
                        "response": {
                            "result": response.actionStatus.result == OPERATIONSTATUS_OK,
                            "reason": response.actionStatus.result_reason.plain_text or ""
                            }
                        }

        return {"response": {"result": True, "reason": ""}}

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

    async def adjust_volume(self, volume: float) -> dict[str, Any]:
        """Adjusts vehicle media playback volume."""
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
        """Charges in Standard mode."""
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

    async def clear_pin_to_drive_admin(self, pin: str):
        """Deactivates PIN to Drive and resets the associated PIN for vehicles running firmware versions 2023.44+. This command is only accessible to fleet managers or owners."""
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    drivingClearSpeedLimitPinAction=DrivingClearSpeedLimitPinAction(
                        pin=pin
                    )
                )
            )
        )

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

    # navigation_gps_request doesnt require signing
    # navigation_request doesnt require signing
    # navigation_sc_request doesnt require signing

    async def remote_auto_seat_climate_request(
        self, auto_seat_position: int, auto_climate_on: bool
    ) -> dict[str, Any]:
        """Sets automatic seat heating and cooling."""
        # AutoSeatPosition_FrontLeft = 1;
        # AutoSeatPosition_FrontRight = 2;
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    autoSeatClimateAction=AutoSeatClimateAction(
                        carseat=[
                            AutoSeatClimateAction.CarSeat(
                                on=auto_climate_on, seat_position=auto_seat_position
                            )
                        ]
                    )
                )
            )
        )

    # remote_auto_steering_wheel_heat_climate_request has no protobuf

    # remote_boombox not implemented

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
                                seat_cooler_level=seat_cooler_level + 1,
                                seat_position=seat_position,
                            )
                        ]
                    )
                )
            )
        )

    async def remote_seat_heater_request(
        self, seat_position: int, seat_heater_level: int
    ) -> dict[str, Any]:
        """Sets seat heating."""
        # HvacSeatCoolerLevel_Unknown = 0;
        # HvacSeatCoolerLevel_Off = 1;
        # HvacSeatCoolerLevel_Low = 2;
        # HvacSeatCoolerLevel_Med = 3;
        # HvacSeatCoolerLevel_High = 4;
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
                heater_action_dict["SEAT_HEATER_MEDIUM"] = Void()
            case 3:
                heater_action_dict["SEAT_HEATER_HIGH"] = Void()
            case _:
                raise ValueError(f"Invalid seat heater level: {seat_heater_level}")

        heater_action = HvacSeatHeaterActions.HvacSeatHeaterAction(**heater_action_dict)
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
        """Sets steering wheel heat level."""
        raise NotImplementedError()

    async def remote_steering_wheel_heater_request(self, on: bool) -> dict[str, Any]:
        """Sets steering wheel heating on/off. For vehicles that do not support auto steering wheel heat."""
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
                        ClimateKeeperAction=climate_keeper_mode,
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
                    setCopTempAction=SetCopTempAction(copActivationTemp=cop_temp + 1)
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
        """Sets a time at which charging should be completed. The time parameter is minutes after midnight (e.g: time=120 schedules charging for 2:00am vehicle local time)."""
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    scheduledChargingAction=ScheduledChargingAction(
                        enable=enable, charging_time=time
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
        """Sets a time at which departure should be completed. The time parameter is minutes after midnight (e.g: time=120 schedules departure for 2:00am vehicle local time)."""

        if preconditioning_weekdays_only:
            preconditioning_times = PreconditioningTimes(weekdays=Void)
        else:
            preconditioning_times = PreconditioningTimes(all_week=Void)

        if off_peak_charging_weekdays_only:
            off_peak_charging_times = OffPeakChargingTimes(weekdays=Void)
        else:
            off_peak_charging_times = OffPeakChargingTimes(all_week=Void)

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

    async def set_valet_mode(self, on: bool, password: str | int) -> dict[str, Any]:
        """Turns on Valet Mode and sets a four-digit passcode that must then be entered to disable Valet Mode."""
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    vehicleControlSetValetModeAction=VehicleControlSetValetModeAction(
                        on=on, password=str(password)
                    )
                )
            )
        )

    async def set_vehicle_name(self, vehicle_name: str) -> dict[str, Any]:
        """Changes the name of a vehicle. This command also requires the Tesla Vehicle Command Protocol - for more information, please see refer to the documentation here."""
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    setVehicleNameAction=SetVehicleNameAction(vehicle_name=vehicle_name)
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

    # speed_limit_clear_pin_admin doesnt require signing

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

        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    vehicleControlSunroofOpenCloseAction=action
                )
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
        action = VehicleControlTriggerHomelinkAction()
        if lat is not None and lon is not None:
            action.location.latitude = lat
            action.location.longitude = lon
        if token is not None:
            action.token = token

        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(vehicleControlTriggerHomelinkAction=action)
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
            Action(vehicleAction=VehicleAction(getNearbyChargingSites=action))
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
