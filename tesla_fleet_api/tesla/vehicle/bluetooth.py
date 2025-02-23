from __future__ import annotations

import hashlib
from asyncio import Future, get_running_loop
from typing import TYPE_CHECKING
from google.protobuf.message import DecodeError

from bleak import BleakClient, BleakScanner
from bleak.backends.characteristic import BleakGATTCharacteristic
from bleak.backends.device import BLEDevice
from cryptography.hazmat.primitives.asymmetric import ec

from tesla_fleet_api.tesla.vehicle.proto.keys_pb2 import Role

from .commands import Commands

from ...const import (
    LOGGER,
)
from ...exceptions import (
    MESSAGE_FAULTS,
    WHITELIST_OPERATION_STATUS,
)

# Protocol
from .proto.car_server_pb2 import (
    Response,
)
from .proto.signatures_pb2 import (
    SessionInfo,
)
from .proto.universal_message_pb2 import (
    Destination,
    Domain,
    RoutableMessage,
)
from .proto.vcsec_pb2 import (
    FromVCSECMessage,
    KeyFormFactor,
    KeyMetadata,
    PermissionChange,
    PublicKey,
    UnsignedMessage,
    WhitelistOperation,

)

SERVICE_UUID = "00000211-b2d1-43f0-9b88-960cebf8b91e"
WRITE_UUID = "00000212-b2d1-43f0-9b88-960cebf8b91e"
READ_UUID = "00000213-b2d1-43f0-9b88-960cebf8b91e"
VERSION_UUID = "00000214-b2d1-43f0-9b88-960cebf8b91e"

if TYPE_CHECKING:
    from ..tesla import Tesla

def prependLength(message: bytes) -> bytearray:
    """Prepend a 2-byte length to the payload."""
    return bytearray([len(message) >> 8, len(message) & 0xFF]) + message

class VehicleBluetooth(Commands):
    """Class describing the Tesla Fleet API vehicle endpoints and commands for a specific vehicle with command signing."""

    ble_name: str
    client: BleakClient
    _device: BLEDevice
    _futures: dict[Domain, Future]
    _ekey: ec.EllipticCurvePublicKey
    _recv: bytearray = bytearray()
    _recv_len: int = 0
    _auth_method = "aes"

    def __init__(
        self, parent: Tesla, vin: str, key: ec.EllipticCurvePrivateKey | None = None
    ):
        super().__init__(parent, vin, key)
        self.ble_name = "S" + hashlib.sha1(vin.encode('utf-8')).hexdigest()[:16] + "C"
        self._futures = {}

    async def discover(self, scanner: BleakScanner = BleakScanner()) -> BleakClient:
        """Find the Tesla BLE device."""

        device = await scanner.find_device_by_name(self.ble_name)
        if not device:
            raise ValueError(f"Device {self.ble_name} not found")
        self._device = device
        self.client = BleakClient(self._device, services=[SERVICE_UUID])
        LOGGER.info(f"Discovered device {self._device.name} {self._device.address}")
        return self.client

    async def connect(self, mac:str | None = None) -> None:
        """Connect to the Tesla BLE device."""
        if mac is not None:
            self.client = BleakClient(mac, services=[SERVICE_UUID])
        await self.client.connect()
        await self.client.start_notify(READ_UUID, self._on_notify)

    async def disconnect(self) -> bool:
        """Disconnect from the Tesla BLE device."""
        return await self.client.disconnect()

    def _on_notify(self,sender: BleakGATTCharacteristic,data : bytearray):
        """Receive data from the Tesla BLE device."""
        if self._recv_len:
            self._recv += data
        else:
            self._recv_len = int.from_bytes(data[:2], 'big')
            self._recv = data[2:]
        LOGGER.debug(f"Received {len(self._recv)} of {self._recv_len} bytes")
        while len(self._recv) > self._recv_len:
            LOGGER.warn(f"Received more data than expected: {len(self._recv)} > {self._recv_len}")
            self._on_message(bytes(self._recv[:self._recv_len]))
            self._recv_len = int.from_bytes(self._recv[self._recv_len:self._recv_len+2], 'big')
            self._recv = self._recv[self._recv_len+2:]
            continue
        if len(self._recv) == self._recv_len:
            self._on_message(bytes(self._recv))
            self._recv = bytearray()
            self._recv_len = 0

    def _on_message(self, data:bytes):
        """Receive messages from the Tesla BLE data."""
        try:
            msg = RoutableMessage.FromString(data)
        except DecodeError as e:
            LOGGER.error(f"Error parsing message: {e}")
            return

        # Update Session
        if(msg.session_info):
            info = SessionInfo.FromString(msg.session_info)
            LOGGER.debug(f"Received session info: {info}")
            self._sessions[msg.from_destination.domain].update(info)

        if(msg.to_destination.routing_address != self._from_destination):
            # Get the ephemeral key here and save to self._ekey
            return

        if msg.from_destination.domain == Domain.DOMAIN_VEHICLE_SECURITY:
            submsg = FromVCSECMessage.FromString(msg.protobuf_message_as_bytes)
            print(submsg)
        elif msg.from_destination.domain == Domain.DOMAIN_INFOTAINMENT:
            submsg = Response.FromString(msg.protobuf_message_as_bytes)
            print(submsg)

        if(self._futures[msg.from_destination.domain]):
            LOGGER.debug(f"Received response for request {msg.request_uuid}")
            self._futures[msg.from_destination.domain].set_result(msg)
            return

    async def _create_future(self, domain: Domain) -> Future:
        if(not self._sessions[domain].lock.locked):
            raise ValueError("Session is not locked")
        self._futures[domain] = get_running_loop().create_future()
        return self._futures[domain]

    async def _send(self, msg: RoutableMessage) -> RoutableMessage:
        """Serialize a message and send to the vehicle and wait for a response."""
        domain = msg.to_destination.domain
        async with self._sessions[domain].lock:
            LOGGER.info(f"Sending message {msg}")
            future = await self._create_future(domain)
            payload = prependLength(msg.SerializeToString())
            LOGGER.info(f"Payload: {payload}")

            await self.client.write_gatt_char(WRITE_UUID, payload, True)

            resp = await future
            LOGGER.info(f"Received message {resp}")

            if resp.signedMessageStatus.signed_message_fault:
                raise MESSAGE_FAULTS[resp.signedMessageStatus.signed_message_fault]

            return resp

    async def pair(self, role: Role = Role.ROLE_OWNER, form: KeyFormFactor = KeyFormFactor.KEY_FORM_FACTOR_CLOUD_KEY):
        """Pair the key."""

        request = UnsignedMessage(
            WhitelistOperation=WhitelistOperation(
                addKeyToWhitelistAndAddPermissions=PermissionChange(
                    key=PublicKey(PublicKeyRaw=self._public_key),
                    keyRole=role
                ),
                metadataForKey=KeyMetadata(
                    keyFormFactor=form
                )
            )
        )
        msg = RoutableMessage(
            to_destination=Destination(
                domain=Domain.DOMAIN_VEHICLE_SECURITY
            ),
            from_destination=Destination(
                routing_address=self._from_destination
            ),
            protobuf_message_as_bytes=request.SerializeToString(),
        )
        resp = await self._send(msg)
        respMsg = FromVCSECMessage.FromString(resp.protobuf_message_as_bytes)
        print(respMsg)
        if(respMsg.commandStatus.whitelistOperationStatus.whitelistOperationInformation):
            if(respMsg.commandStatus.whitelistOperationStatus.whitelistOperationInformation < len(WHITELIST_OPERATION_STATUS)):
                raise WHITELIST_OPERATION_STATUS[respMsg.commandStatus.whitelistOperationStatus.whitelistOperationInformation]
            else:
                raise ValueError(f"Unknown whitelist operation status: {respMsg.commandStatus.whitelistOperationStatus.whitelistOperationInformation}")
        return
