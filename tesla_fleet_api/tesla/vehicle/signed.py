from __future__ import annotations

import base64
import hashlib
import hmac
import struct
from asyncio import sleep
from random import randbytes
from typing import TYPE_CHECKING, Any

from tesla_fleet_api.tesla.vehicle.fleet import VehicleFleet

from ...const import (
    LOGGER,
)
from ...exceptions import (
    MESSAGE_FAULTS,
    SIGNED_MESSAGE_INFORMATION_FAULTS,
    TeslaFleetMessageFaultIncorrectEpoch,
    TeslaFleetMessageFaultInvalidTokenOrCounter,
)
from .proto.car_server_pb2 import (
    Response,
)
from .proto.errors_pb2 import GenericError_E
from .proto.signatures_pb2 import (
    SIGNATURE_TYPE_HMAC_PERSONALIZED,
    TAG_COUNTER,
    TAG_DOMAIN,
    TAG_END,
    TAG_EPOCH,
    TAG_EXPIRES_AT,
    TAG_PERSONALIZATION,
    TAG_SIGNATURE_TYPE,
    SessionInfo,
)
from .proto.universal_message_pb2 import (
    DOMAIN_INFOTAINMENT,
    DOMAIN_VEHICLE_SECURITY,
    OPERATIONSTATUS_ERROR,
    OPERATIONSTATUS_WAIT,
    Domain,
    RoutableMessage,
)
from .proto.vcsec_pb2 import (
    # SignedMessage_information_E,
    OPERATIONSTATUS_OK,
    FromVCSECMessage,
)

if TYPE_CHECKING:
    from ..tesla import TeslaFleetApi


from .commands import Commands


class VehicleSigned(VehicleFleet, Commands):
    """Class describing the Tesla Fleet API vehicle endpoints and commands for a specific vehicle with command signing."""

    def __init__(self, parent: TeslaFleetApi, vin: str):
        """Initialize the VehicleSigned class."""
        super().__init__(parent, vin)
        super(Commands, self).__init__(parent, vin)


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

    async def _command(
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
            return await self._command(domain, command, attempt)

        if resp.signedMessageStatus.operation_status == OPERATIONSTATUS_WAIT:
            attempt += 1
            if attempt > 3:
                # We tried 3 times, give up, raise the error
                return {"response": {"result": False, "reason": "Too many retries"}}
            async with session.lock:
                await sleep(2)
            return await self._command(domain, command, attempt)

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
                    return await self._command(domain, command, attempt)
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
