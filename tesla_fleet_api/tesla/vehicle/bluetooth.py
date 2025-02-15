from __future__ import annotations

import hashlib
import hmac
import struct
from asyncio import sleep
from random import randbytes
from typing import TYPE_CHECKING, Any

from bleak import BleakClient, BleakScanner
from bleak.backends.device import BLEDevice
from cryptography.hazmat.primitives.asymmetric import ec

from proto.errors_pb2 import GenericError_E
from tesla_fleet_api.tesla.vehicle.commands import Commands

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
    OPERATIONSTATUS_OK,
    FromVCSECMessage,
)

SERVICE_UUID = "00000211-b2d1-43f0-9b88-960cebf8b91e"
WRITE_UUID = "00000212-b2d1-43f0-9b88-960cebf8b91e"
READ_UUID = "00000213-b2d1-43f0-9b88-960cebf8b91e"
VERSION_UUID = "00000214-b2d1-43f0-9b88-960cebf8b91e"

if TYPE_CHECKING:
    from ..tesla import TeslaFleetApi

class VehicleBluetooth(Commands):
    """Class describing the Tesla Fleet API vehicle endpoints and commands for a specific vehicle with command signing."""

    _ble_name: str
    _device: BLEDevice
    _client: BleakClient

    def __init__(
        self, parent: TeslaFleetApi, vin: str, key: ec.EllipticCurvePrivateKey | None = None
    ):
        super().__init__(parent, vin, key)
        self._ble_name = "S" + hashlib.sha1(vin.encode('utf-8')).hexdigest()[:16] + "C"

    async def _discover(self, scanner: BleakScanner = BleakScanner()):
        """Connect to the Tesla BLE device."""
        devices = await scanner.discover()
        for device in devices:
            if device.name == self._ble_name:
                self._device = device
                self._client = BleakClient(self._device)
                await self._client.connect()
                break
        else:
            raise Exception(f"Could not find Tesla device with name {self._ble_name}")

    async def _send(self, msg: RoutableMessage) -> RoutableMessage:
        """Serialize a message and send to the signed command endpoint."""

        async with self._sessions[msg.to_destination.domain].lock:
            resp = await self._client.write_gatt_char(WRITE_UUID, msg.SerializeToString(), True)
            print(resp)

            resp_msg = RoutableMessage.FromString(resp)

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
        """Send an encrypted message to the vehicle over Bluetooth."""
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
