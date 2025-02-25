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

from tesla_fleet_api.tesla.vehicle.commands import Commands

from tesla_fleet_api.const import (
    LOGGER,
    BluetoothVehicleData
)
from tesla_fleet_api.exceptions import (
    MESSAGE_FAULTS,
    WHITELIST_OPERATION_STATUS,
    WhitelistOperationStatus,
    NotOnWhitelistFault,
)

# Protocol
from tesla_fleet_api.tesla.vehicle.proto.car_server_pb2 import (
    Action,
    VehicleAction,
    Response,
    GetVehicleData,
    GetChargeState,
    GetClimateState,
    GetDriveState,
    GetLocationState,
    GetClosuresState,
    GetChargeScheduleState,
    GetPreconditioningScheduleState,
    GetTirePressureState,
    GetMediaState,
    GetMediaDetailState,
    GetSoftwareUpdateState,
    GetParentalControlsState,
)
from tesla_fleet_api.tesla.vehicle.proto.signatures_pb2 import (
    SessionInfo,
    Session_Info_Status
)
from tesla_fleet_api.tesla.vehicle.proto.universal_message_pb2 import (
    Destination,
    Domain,
    RoutableMessage,
)
from tesla_fleet_api.tesla.vehicle.proto.vcsec_pb2 import (
    FromVCSECMessage,
    KeyFormFactor,
    KeyMetadata,
    PermissionChange,
    PublicKey,
    RKEAction_E,
    UnsignedMessage,
    WhitelistOperation,
)

SERVICE_UUID = "00000211-b2d1-43f0-9b88-960cebf8b91e"
WRITE_UUID = "00000212-b2d1-43f0-9b88-960cebf8b91e"
READ_UUID = "00000213-b2d1-43f0-9b88-960cebf8b91e"
VERSION_UUID = "00000214-b2d1-43f0-9b88-960cebf8b91e"

if TYPE_CHECKING:
    from tesla_fleet_api.tesla.tesla import Tesla

def prependLength(message: bytes) -> bytearray:
    """Prepend a 2-byte length to the payload."""
    return bytearray([len(message) >> 8, len(message) & 0xFF]) + message

class VehicleBluetooth(Commands):
    """Class describing the Tesla Fleet API vehicle endpoints and commands for a specific vehicle with command signing."""

    ble_name: str
    client: BleakClient
    _futures: dict[Domain, Future]
    _ekey: ec.EllipticCurvePublicKey
    _recv: bytearray = bytearray()
    _recv_len: int = 0
    _auth_method = "aes"

    def __init__(
        self, parent: Tesla, vin: str, key: ec.EllipticCurvePrivateKey | None = None, device: None | str | BLEDevice = None
    ):
        super().__init__(parent, vin, key)
        self.ble_name = "S" + hashlib.sha1(vin.encode('utf-8')).hexdigest()[:16] + "C"
        self._futures = {}
        if device is not None:
            self.client = BleakClient(device, services=[SERVICE_UUID])

    async def find_client(self, scanner: BleakScanner = BleakScanner()) -> BleakClient:
        """Find the Tesla BLE device."""

        device = await scanner.find_device_by_name(self.ble_name)
        if not device:
            raise ValueError(f"Device {self.ble_name} not found")
        self.client = BleakClient(device, services=[SERVICE_UUID])
        LOGGER.debug(f"Discovered device {device.name} {device.address}")
        return self.client

    def create_client(self, device: str|BLEDevice) -> BleakClient:
        """Create a client using a MAC address or Bleak Device."""
        self.client = BleakClient(device, services=[SERVICE_UUID])
        return self.client

    async def connect(self, device: str|BLEDevice | None = None) -> None:
        """Connect to the Tesla BLE device."""
        if device is not None:
            self.create_client(device)
        await self.client.connect()
        await self.client.start_notify(READ_UUID, self._on_notify)

    async def disconnect(self) -> bool:
        """Disconnect from the Tesla BLE device."""
        return await self.client.disconnect()

    async def __aenter__(self) -> VehicleBluetooth:
        """Enter the async context."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit the async context."""
        await self.disconnect()

    def _on_notify(self,sender: BleakGATTCharacteristic,data : bytearray) -> None:
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

    def _on_message(self, data:bytes) -> None:
        """Receive messages from the Tesla BLE data."""
        try:
            msg = RoutableMessage.FromString(data)
        except DecodeError as e:
            LOGGER.error(f"Error parsing message: {e}")
            self._recv = bytearray()
            self._recv_len = 0
            return

        # Update Session
        if(msg.session_info):
            info = SessionInfo.FromString(msg.session_info)
            # maybe dont?
            if(info.status == Session_Info_Status.SESSION_INFO_STATUS_KEY_NOT_ON_WHITELIST):
                 self._futures[msg.from_destination.domain].set_exception(NotOnWhitelistFault())
                 return
            self._sessions[msg.from_destination.domain].update(info)

        if(msg.to_destination.routing_address != self._from_destination):
            # Get the ephemeral key here and save to self._ekey
            return

        if(self._futures[msg.from_destination.domain]):
            LOGGER.debug(f"Received response for request {msg.request_uuid}")
            self._futures[msg.from_destination.domain].set_result(msg)
            return

        if msg.from_destination.domain == Domain.DOMAIN_VEHICLE_SECURITY:
            submsg = FromVCSECMessage.FromString(msg.protobuf_message_as_bytes)
            LOGGER.warning(f"Received orphaned VCSEC response: {submsg}")
        elif msg.from_destination.domain == Domain.DOMAIN_INFOTAINMENT:
            submsg = Response.FromString(msg.protobuf_message_as_bytes)
            LOGGER.warning(f"Received orphaned INFOTAINMENT response: {submsg}")
        else:
            LOGGER.warning(f"Received orphaned response: {msg}")

    async def _create_future(self, domain: Domain) -> Future:
        if(not self._sessions[domain].lock.locked):
            raise ValueError("Session is not locked")
        self._futures[domain] = get_running_loop().create_future()
        return self._futures[domain]

    async def _send(self, msg: RoutableMessage) -> RoutableMessage:
        """Serialize a message and send to the vehicle and wait for a response."""
        domain = msg.to_destination.domain
        async with self._sessions[domain].lock:
            LOGGER.debug(f"Sending message {msg}")
            future = await self._create_future(domain)
            payload = prependLength(msg.SerializeToString())

            await self.client.write_gatt_char(WRITE_UUID, payload, True)

            resp = await future
            LOGGER.debug(f"Received message {resp}")

            if resp.signedMessageStatus.signed_message_fault > 0:
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
        if(respMsg.commandStatus.whitelistOperationStatus.whitelistOperationInformation):
            if(respMsg.commandStatus.whitelistOperationStatus.whitelistOperationInformation < len(WHITELIST_OPERATION_STATUS)):
                raise WHITELIST_OPERATION_STATUS[respMsg.commandStatus.whitelistOperationStatus.whitelistOperationInformation]
            else:
                raise WhitelistOperationStatus(f"Unknown whitelist operation failure: {respMsg.commandStatus.whitelistOperationStatus.whitelistOperationInformation}")
        return

    async def wake_up(self):
        """Wake up the vehicle."""
        return await self._sendVehicleSecurity(
            UnsignedMessage(RKEAction=RKEAction_E.RKE_ACTION_WAKE_VEHICLE)
        )

    async def vehicle_data(self, endpoints: list[BluetoothVehicleData]):
        """Get vehicle data."""
        return await self._sendInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    getVehicleData=GetVehicleData(
                        getChargeState = GetChargeState() if BluetoothVehicleData.CHARGE_STATE in endpoints else None,
                        getClimateState = GetClimateState() if BluetoothVehicleData.CLIMATE_STATE in endpoints else None,
                        getDriveState = GetDriveState() if BluetoothVehicleData.DRIVE_STATE in endpoints else None,
                        getLocationState = GetLocationState() if BluetoothVehicleData.LOCATION_STATE in endpoints else None,
                        getClosuresState = GetClosuresState() if BluetoothVehicleData.CLOSURES_STATE in endpoints else None,
                        getChargeScheduleState = GetChargeScheduleState() if BluetoothVehicleData.CHARGE_SCHEDULE_STATE in endpoints else None,
                        getPreconditioningScheduleState = GetPreconditioningScheduleState() if BluetoothVehicleData.PRECONDITIONING_SCHEDULE_STATE in endpoints else None,
                        getTirePressureState = GetTirePressureState() if BluetoothVehicleData.TIRE_PRESSURE_STATE in endpoints else None,
                        getMediaState = GetMediaState() if BluetoothVehicleData.MEDIA_STATE in endpoints else None,
                        getMediaDetailState = GetMediaDetailState() if BluetoothVehicleData.MEDIA_DETAIL_STATE in endpoints else None,
                        getSoftwareUpdateState = GetSoftwareUpdateState() if BluetoothVehicleData.SOFTWARE_UPDATE_STATE in endpoints else None,
                        getParentalControlsState = GetParentalControlsState() if BluetoothVehicleData.PARENTAL_CONTROLS_STATE in endpoints else None,
                    )
                )
            )
        )
