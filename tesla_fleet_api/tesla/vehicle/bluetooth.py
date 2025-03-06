from __future__ import annotations

import hashlib
import asyncio
import struct
from typing import TYPE_CHECKING, Callable, Any
from google.protobuf.message import DecodeError
from bleak_retry_connector import establish_connection, MAX_CONNECT_ATTEMPTS
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
    WHITELIST_OPERATION_STATUS,
    WhitelistOperationStatus,
)

# Protocol
from tesla_fleet_api.tesla.vehicle.proto.car_server_pb2 import (
    Action,
    VehicleAction,
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
from tesla_fleet_api.tesla.vehicle.proto.universal_message_pb2 import (
    Destination,
    Domain,
    RoutableMessage,
)
from tesla_fleet_api.tesla.vehicle.proto.vcsec_pb2 import (
    FromVCSECMessage,
    InformationRequest,
    InformationRequestType,
    KeyFormFactor,
    KeyMetadata,
    PermissionChange,
    PublicKey,
    RKEAction_E,
    UnsignedMessage,
    VehicleStatus,
    WhitelistOperation,
)
from tesla_fleet_api.tesla.vehicle.proto.vehicle_pb2 import ChargeScheduleState, ChargeState, ClimateState, ClosuresState, DriveState, LocationState, MediaDetailState, MediaState, ParentalControlsState, PreconditioningScheduleState, SoftwareUpdateState, TirePressureState, VehicleData

SERVICE_UUID = "00000211-b2d1-43f0-9b88-960cebf8b91e"
WRITE_UUID = "00000212-b2d1-43f0-9b88-960cebf8b91e"
READ_UUID = "00000213-b2d1-43f0-9b88-960cebf8b91e"
VERSION_UUID = "00000214-b2d1-43f0-9b88-960cebf8b91e"
NAME_UUID = "00002a00-0000-1000-8000-00805f9b34fb"
APPEARANCE_UUID = "00002a01-0000-1000-8000-00805f9b34fb"

if TYPE_CHECKING:
    from tesla_fleet_api.tesla.tesla import Tesla

def prependLength(message: bytes) -> bytearray:
    """Prepend a 2-byte length to the payload."""
    return bytearray([len(message) >> 8, len(message) & 0xFF]) + message

class ReassemblingBuffer:
    """
    Reassembles bytearray streams where the first two bytes indicate the length of the message.
    Handles potential packet corruption by discarding *entire* packets and retrying.
    Uses a callback to process parsed messages.
    """

    def __init__(self, callback: Callable[[RoutableMessage], None]):
        """
        Initializes the buffer.

        Args:
            message_type: The protobuf message type (e.g., RoutableMessage) to parse the assembled data.
            callback: A function that will be called with each parsed message.
        """
        self.buffer = bytearray()
        self.expected_length = None
        self.packet_starts = []
        self.callback = callback

    def receive_data(self, data: bytearray):
        """
        Receives a chunk of bytearray data and attempts to assemble a complete message.

        Args:
            data: The received bytearray data.
        """
        self.packet_starts.append(len(self.buffer))
        self.buffer.extend(data)

        while True:
            if self.expected_length is None and len(self.buffer) >= 2:
                self.expected_length = struct.unpack(">H", self.buffer[:2])[0] + 2

            LOGGER.info(f"Buffer length: {len(self.buffer)}, Packet starts: {self.packet_starts}, Expected length: {self.expected_length}")

            if self.expected_length is not None and self.expected_length > 1024:
                LOGGER.warning(f"Expected length too large: {self.expected_length}")
                self.discard_packet()

            elif self.expected_length is not None and len(self.buffer) >= self.expected_length:
                try:
                    message = RoutableMessage()
                    message.ParseFromString(bytes(self.buffer[2:self.expected_length]))
                    self.buffer = self.buffer[self.expected_length:]
                    self.packet_starts = [x - self.expected_length for x in self.packet_starts if x >= self.expected_length]
                    self.expected_length = None
                    self.callback(message)  # Call the callback with the parsed message

                except DecodeError:
                    self.discard_packet()
            else:
                return

    def discard_packet(self):
        self.packet_starts.pop(0)
        if len(self.packet_starts) > 0:
            self.buffer = self.buffer[self.packet_starts[0]:]
            self.packet_starts = [x - self.packet_starts[0] for x in self.packet_starts]
        else:
            self.buffer = bytearray()
            self.packet_starts = []
        self.expected_length = None

class VehicleBluetooth(Commands):
    """Class describing the Tesla Fleet API vehicle endpoints and commands for a specific vehicle with command signing."""

    ble_name: str
    device: BLEDevice | None = None
    client: BleakClient | None = None
    _queues: dict[Domain, asyncio.Queue]
    _ekey: ec.EllipticCurvePublicKey
    _buffer: ReassemblingBuffer
    _auth_method = "aes"

    def __init__(
        self, parent: Tesla, vin: str, key: ec.EllipticCurvePrivateKey | None = None, device: BLEDevice | None = None
    ):
        super().__init__(parent, vin, key)
        self.ble_name = "S" + hashlib.sha1(vin.encode('utf-8')).hexdigest()[:16] + "C"
        self._queues = {
            Domain.DOMAIN_VEHICLE_SECURITY: asyncio.Queue(),
            Domain.DOMAIN_INFOTAINMENT: asyncio.Queue(),
        }
        self.device = device
        self._connect_lock = asyncio.Lock()
        self._buffer = ReassemblingBuffer(self._on_message)

    async def find_vehicle(self, name: str | None = None, address: str | None = None, scanner: BleakScanner | None = None) -> BLEDevice:
        """Find the Tesla BLE device."""

        if scanner is None:
            scanner = BleakScanner(service_uuids=[SERVICE_UUID])

        if address is not None:
            device = await scanner.find_device_by_address(address)
        elif name is not None:
            device = await scanner.find_device_by_name(name)
        else:
            device = await scanner.find_device_by_name(self.ble_name)
        if not device:
            raise ValueError(f"Device {self.ble_name} not found")
        self.device = device
        return self.device

    def set_device(self, device: BLEDevice) -> None:
        self.device = device

    def get_device(self) -> BLEDevice | None:
        return self.device

    async def connect(self, max_attempts: int = MAX_CONNECT_ATTEMPTS) -> None:
        """Connect to the Tesla BLE device."""
        if not self.device:
            raise ValueError(f"BLEDevice {self.ble_name} has not been found or set")
        self.client = await establish_connection(
            BleakClient,
            self.device,
            self.vin,
            max_attempts=max_attempts,
            #ble_device_callback=self.get_device,
            services=[SERVICE_UUID]
        )
        await self.client.start_notify(READ_UUID, self._on_notify)

    async def disconnect(self) -> bool:
        """Disconnect from the Tesla BLE device."""
        if not self.client:
            return False
        return await self.client.disconnect()

    async def connect_if_needed(self, max_attempts: int = MAX_CONNECT_ATTEMPTS) -> None:
        """Connect to the Tesla BLE device if not already connected."""
        async with self._connect_lock:
            if not self.client or not self.client.is_connected:
                LOGGER.info(f"Reconnecting to {self.ble_name}")
                await self.connect(max_attempts=max_attempts)

    async def __aenter__(self) -> VehicleBluetooth:
        """Enter the async context."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit the async context."""
        await self.disconnect()

    def _on_notify(self,sender: BleakGATTCharacteristic, data: bytearray) -> None:
        """Receive data from the Tesla BLE device."""
        if sender.uuid != READ_UUID:
            LOGGER.error(f"Unexpected sender: {sender}")
            return
        self._buffer.receive_data(data)

    def _on_message(self, msg: RoutableMessage) -> None:
        """Receive messages from the Tesla BLE data."""

        if(msg.to_destination.routing_address != self._from_destination):
            # Ignore ephemeral key broadcasts
            return

        LOGGER.info(f"Received response: {msg}")
        self._queues[msg.from_destination.domain].put_nowait(msg)

    async def _send(self, msg: RoutableMessage, requires: str, timeout: int = 5) -> RoutableMessage:
        """Serialize a message and send to the vehicle and wait for a response."""

        domain = msg.to_destination.domain
        async with self._sessions[domain].lock:
            LOGGER.info(f"Sending message {msg}")

            payload = prependLength(msg.SerializeToString())

            # Empty the queue before sending the message
            while not self._queues[domain].empty():
                msg = await self._queues[domain].get()
                LOGGER.warning(f"Discarded message {msg}")

            await self.connect_if_needed()
            assert self.client is not None
            await self.client.write_gatt_char(WRITE_UUID, payload, True)

            # Process the response
            async with asyncio.timeout(timeout):
                LOGGER.info(f"Waiting for response with {requires}")
                while True:
                    resp = await self._queues[domain].get()
                    LOGGER.debug(f"Received message {resp}")

                    self.validate_msg(resp)

                    if resp.HasField(requires):
                        return resp
                    else:
                        LOGGER.warning(f"Ignoring message since it does not contain the required field {requires}, {resp.HasField(requires)}")

    async def query_display_name(self, max_attempts=5) -> str | None:
        """Read the device name via GATT characteristic if available"""
        for i in range(max_attempts):
            try:
                # Standard GATT Device Name characteristic (0x2A00)
                await self.connect_if_needed()
                assert self.client
                device_name = (await self.client.read_gatt_char(NAME_UUID)).decode('utf-8')
                if device_name.startswith("🔑 "):
                    return device_name.replace("🔑 ","")
                await asyncio.sleep(1)
                LOGGER.debug(f"Attempt {i+1} to query display name failed, {device_name}")
            except Exception as e:
                LOGGER.error(f"Failed to read device name: {e}")

    async def query_appearance(self) -> bytearray | None:
        """Read the device appearance via GATT characteristic if available"""
        try:
            # Standard GATT Appearance characteristic (0x2A01)
            await self.connect_if_needed()
            assert self.client
            return await self.client.read_gatt_char(APPEARANCE_UUID)
        except Exception as e:
            LOGGER.error(f"Failed to read device appearance: {e}")
            return None

    async def query_version(self) -> int | None:
        """Read the device version via GATT characteristic if available"""
        try:
            # Custom GATT Version characteristic (0x2A02)
            await self.connect_if_needed()
            assert self.client
            device_version = await self.client.read_gatt_char(VERSION_UUID)
            # Convert the bytes to an integer
            if device_version and len(device_version) > 0:
                return int.from_bytes(device_version, byteorder='big')
        except Exception as e:
            LOGGER.error(f"Failed to read device version: {e}")
        return None

    async def _command(self, domain: Domain, command: bytes, attempt: int = 0) -> dict[str, Any]:
        """Serialize a message and send to the signed command endpoint."""
        await self.connect_if_needed()
        return await super()._command(domain, command, attempt)

    async def pair(self, role: Role = Role.ROLE_OWNER, form: KeyFormFactor = KeyFormFactor.KEY_FORM_FACTOR_CLOUD_KEY, timeout: int = 60):
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
        resp = await self._send(msg, "protobuf_message_as_bytes", timeout)
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

    async def vehicle_data(self, endpoints: list[BluetoothVehicleData]) -> VehicleData:
        """Get vehicle data."""
        return await self._getInfotainment(
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

    async def charge_state(self) -> ChargeState:
        return (await self._getInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    getVehicleData=GetVehicleData(
                        getChargeState=GetChargeState()
                    )
                )
            )
        )).charge_state

    async def climate_state(self) -> ClimateState:
        return (await self._getInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    getVehicleData=GetVehicleData(
                        getClimateState=GetClimateState()
                    )
                )
            )
        )).climate_state

    async def drive_state(self) -> DriveState:
        return (await self._getInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    getVehicleData=GetVehicleData(
                        getDriveState=GetDriveState()
                    )
                )
            )
        )).drive_state

    async def location_state(self) -> LocationState:
        return (await self._getInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    getVehicleData=GetVehicleData(
                        getLocationState=GetLocationState()
                    )
                )
            )
        )).location_state

    async def closures_state(self) -> ClosuresState:
        return (await self._getInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    getVehicleData=GetVehicleData(
                        getClosuresState=GetClosuresState()
                    )
                )
            )
        )).closures_state

    async def charge_schedule_state(self) -> ChargeScheduleState:
        return (await self._getInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    getVehicleData=GetVehicleData(
                        getChargeScheduleState=GetChargeScheduleState()
                    )
                )
            )
        )).charge_schedule_state

    async def preconditioning_schedule_state(self) -> PreconditioningScheduleState:
        return (await self._getInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    getVehicleData=GetVehicleData(
                        getPreconditioningScheduleState=GetPreconditioningScheduleState()
                    )
                )
            )
        )).preconditioning_schedule_state

    async def tire_pressure_state(self) -> TirePressureState:
        return (await self._getInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    getVehicleData=GetVehicleData(
                        getTirePressureState=GetTirePressureState()
                    )
                )
            )
        )).tire_pressure_state

    async def media_state(self) -> MediaState:
        return (await self._getInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    getVehicleData=GetVehicleData(
                        getMediaState=GetMediaState()
                    )
                )
            )
        )).media_state

    async def media_detail_state(self) -> MediaDetailState:
        return (await self._getInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    getVehicleData=GetVehicleData(
                        getMediaDetailState=GetMediaDetailState()
                    )
                )
            )
        )).media_detail_state

    async def software_update_state(self) -> SoftwareUpdateState:
        return (await self._getInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    getVehicleData=GetVehicleData(
                        getSoftwareUpdateState=GetSoftwareUpdateState()
                    )
                )
            )
        )).software_update_state

    async def parental_controls_state(self) -> ParentalControlsState:
        return (await self._getInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    getVehicleData=GetVehicleData(
                        getParentalControlsState=GetParentalControlsState()
                    )
                )
            )
        )).parental_controls_state

    async def vehicle_state(self) -> VehicleStatus:
        return await self._getVehicleSecurity(
            UnsignedMessage(
                InformationRequest=InformationRequest(
                    informationRequestType=InformationRequestType.INFORMATION_REQUEST_TYPE_GET_STATUS
                )
            )
        )
