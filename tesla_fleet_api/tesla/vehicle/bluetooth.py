from __future__ import annotations

import hashlib
import asyncio
from typing import TYPE_CHECKING
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

if TYPE_CHECKING:
    from tesla_fleet_api.tesla.tesla import Tesla

def prependLength(message: bytes) -> bytearray:
    """Prepend a 2-byte length to the payload."""
    return bytearray([len(message) >> 8, len(message) & 0xFF]) + message

class VehicleBluetooth(Commands):
    """Class describing the Tesla Fleet API vehicle endpoints and commands for a specific vehicle with command signing."""

    ble_name: str
    device: BLEDevice
    client: BleakClient
    _queues: dict[Domain, asyncio.Queue]
    _ekey: ec.EllipticCurvePublicKey
    _recv: bytearray = bytearray()
    _recv_len: int = 0
    _auth_method = "aes"

    def __init__(
        self, parent: Tesla, vin: str, key: ec.EllipticCurvePrivateKey | None = None, device: None | str | BLEDevice = None
    ):
        super().__init__(parent, vin, key)
        self.ble_name = "S" + hashlib.sha1(vin.encode('utf-8')).hexdigest()[:16] + "C"
        self._queues = {
            Domain.DOMAIN_VEHICLE_SECURITY: asyncio.Queue(),
            Domain.DOMAIN_INFOTAINMENT: asyncio.Queue(),
        }
        if device is not None:
            self.client = BleakClient(device, services=[SERVICE_UUID])

    async def find_vehicle(self, name: str | None = None, address: str | None = None, scanner: BleakScanner = BleakScanner()) -> BLEDevice:
        """Find the Tesla BLE device."""
        if name is not None:
            device = await scanner.find_device_by_name(name)
        elif address is not None:
            device = await scanner.find_device_by_address(address)
        else:
            device = await scanner.find_device_by_name(self.ble_name)
        if not device:
            raise ValueError(f"Device {self.ble_name} not found")
        self.device = device
        return self.device

    def set_device(self, device: BLEDevice) -> None:
        self.device = device

    def get_device(self) -> BLEDevice:
        return self.device

    async def connect(self, device: BLEDevice | None = None, max_attempts: int = MAX_CONNECT_ATTEMPTS) -> None:
        """Connect to the Tesla BLE device."""
        self.client = await establish_connection(BleakClient, self.device, self.vin, max_attempts=max_attempts, ble_device_callback=self.get_device)
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

    async def _on_notify(self,sender: BleakGATTCharacteristic,data : bytearray) -> None:
        """Receive data from the Tesla BLE device."""
        if self._recv_len:
            self._recv += data
        else:
            self._recv_len = int.from_bytes(data[:2], 'big')
            self._recv = data[2:]
        LOGGER.debug(f"Received {len(self._recv)} of {self._recv_len} bytes")
        while len(self._recv) > self._recv_len:
            LOGGER.warn(f"Received more data than expected: {len(self._recv)} > {self._recv_len}")
            await self._on_message(bytes(self._recv[:self._recv_len]))
            self._recv_len = int.from_bytes(self._recv[self._recv_len:self._recv_len+2], 'big')
            self._recv = self._recv[self._recv_len+2:]
            continue
        if len(self._recv) == self._recv_len:
            await self._on_message(bytes(self._recv))
            self._recv = bytearray()
            self._recv_len = 0

    async def _on_message(self, data:bytes) -> None:
        """Receive messages from the Tesla BLE data."""
        try:
            msg = RoutableMessage.FromString(data)
        except DecodeError as e:
            LOGGER.error(f"Error parsing message: {e}")
            self._recv = bytearray()
            self._recv_len = 0
            return

        if(msg.to_destination.routing_address != self._from_destination):
            # Ignore ephemeral key broadcasts
            return

        LOGGER.info(f"Received response: {msg}")
        await self._queues[msg.from_destination.domain].put(msg)

    async def _send(self, msg: RoutableMessage, requires: str) -> RoutableMessage:
        """Serialize a message and send to the vehicle and wait for a response."""
        domain = msg.to_destination.domain
        async with self._sessions[domain].lock:
            LOGGER.debug(f"Sending message {msg}")

            payload = prependLength(msg.SerializeToString())

            # Empty the queue before sending the message
            while not self._queues[domain].empty():
                await self._queues[domain].get()
            await self.client.write_gatt_char(WRITE_UUID, payload, True)

            # Process the response
            async with asyncio.timeout(10):
                while True:
                    resp = await self._queues[domain].get()
                    LOGGER.debug(f"Received message {resp}")

                    self.validate_msg(resp)

                    if resp.HasField(requires):
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
