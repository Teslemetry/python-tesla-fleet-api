from __future__ import annotations

import asyncio
import hashlib
import struct
import time
import warnings
from random import randbytes
from typing import TYPE_CHECKING, Any, Callable, Generic, TypeVar

from bleak import BleakClient, BleakScanner
from bleak.backends.characteristic import BleakGATTCharacteristic
from bleak.backends.device import BLEDevice
from bleak.exc import BleakError
from bleak_retry_connector import MAX_CONNECT_ATTEMPTS, establish_connection
from cryptography.hazmat.primitives.asymmetric import ec
from google.protobuf.message import DecodeError

from tesla_fleet_api.const import BluetoothConfirmation, BluetoothVehicleData, LOGGER
from tesla_fleet_api.exceptions import (
    WHITELIST_OPERATION_STATUS,
    BluetoothCommandFailed,
    BluetoothTimeout,
    BluetoothTransportError,
    BluetoothUnconfirmedCommand,
    TeslaFleetError,
    WhitelistOperationStatus,
)
from tesla_fleet_api.tesla.vehicle.commands import (
    Commands,
    infotainment_command_name,
    vcsec_command_name,
)

# Protocol
from tesla_fleet_api.tesla.vehicle.proto.car_server_pb2 import (
    Action,
    GetChargeScheduleState,
    GetChargeState,
    GetClimateState,
    GetClosuresState,
    GetDriveState,
    GetLocationState,
    GetMediaDetailState,
    GetMediaState,
    GetParentalControlsState,
    GetPreconditioningScheduleState,
    GetSoftwareUpdateState,
    GetTirePressureState,
    GetVehicleData,
    VehicleAction,
)
from tesla_fleet_api.tesla.vehicle.proto.keys_pb2 import Role
from tesla_fleet_api.tesla.vehicle.proto.universal_message_pb2 import (
    Destination,
    Domain,
    RoutableMessage,
)
from tesla_fleet_api.tesla.vehicle.proto.vcsec_pb2 import (
    ClosureMoveRequest,
    ClosureMoveType_E,
    FromVCSECMessage,
    InformationRequest,
    InformationRequestType,
    KeyFormFactor,
    KeyMetadata,
    PermissionChange,
    PublicKey,
    RKEAction_E,
    UnsignedMessage,
    VehicleLockState_E,
    VehicleStatus,
    WhitelistOperation,
)
from tesla_fleet_api.tesla.vehicle.proto.vehicle_pb2 import (
    ChargeScheduleState,
    ChargeState,
    ClimateState,
    ClosuresState,
    DriveState,
    LocationState,
    MediaDetailState,
    MediaState,
    ParentalControlsState,
    PreconditioningScheduleState,
    SoftwareUpdateState,
    TirePressureState,
    VehicleData,
)

SERVICE_UUID = "00000211-b2d1-43f0-9b88-960cebf8b91e"
WRITE_UUID = "00000212-b2d1-43f0-9b88-960cebf8b91e"
READ_UUID = "00000213-b2d1-43f0-9b88-960cebf8b91e"
VERSION_UUID = "00000214-b2d1-43f0-9b88-960cebf8b91e"
NAME_UUID = "00002a00-0000-1000-8000-00805f9b34fb"
APPEARANCE_UUID = "00002a01-0000-1000-8000-00805f9b34fb"

# An idle held BLE link to the vehicle drops at ~42s mean; a trivial GATT read
# every 20s keeps it alive ~10x longer. See AGENTS.md for the measured evidence.
DEFAULT_KEEPALIVE_INTERVAL = 20.0

if TYPE_CHECKING:
    from tesla_fleet_api.tesla.tesla import Tesla

BluetoothParentT = TypeVar("BluetoothParentT", bound="Tesla")


def prependLength(message: bytes) -> bytearray:
    """Prepend a 2-byte length to the payload."""
    return bytearray([len(message) >> 8, len(message) & 0xFF]) + message


# A chunk arriving after this much silence means the prior partial frame was
# abandoned mid-flight, not merely delayed.
STALE_CHUNK_TIMEOUT = 1.0


class ReassemblingBuffer:
    """
    Reassembles BLE notification chunks into length-prefixed RoutableMessages.

    Each message starts with a 2-byte length. One notification can contain part
    of a message, exactly one message, or multiple messages. If a message cannot
    be decoded, the buffer drops the current physical packet and resynchronizes
    at the next recorded packet boundary. A partial message is also discarded if
    the next chunk doesn't arrive within ``STALE_CHUNK_TIMEOUT``.
    """

    def __init__(self, callback: Callable[[RoutableMessage], None]):
        """
        Initializes the buffer.

        Args:
            callback: A function that will be called with each parsed message.
        """
        self.buffer: bytearray = bytearray()
        self.expected_length: int | None = None
        self.packet_starts: list[int] = []
        self.callback = callback
        self._last_chunk_time: float | None = None

    def receive_data(self, data: bytearray):
        """
        Receive one BLE notification chunk and emit any complete messages.

        Args:
            data: The received bytearray data.
        """
        now = time.monotonic()
        if (
            self.buffer
            and self._last_chunk_time is not None
            and now - self._last_chunk_time > STALE_CHUNK_TIMEOUT
        ):
            self.buffer = bytearray()
            self.expected_length = None
            self.packet_starts = []
        self._last_chunk_time = now

        self.packet_starts.append(len(self.buffer))
        self.buffer.extend(data)

        while True:
            if self.expected_length is None and len(self.buffer) >= 2:
                self.expected_length = struct.unpack(">H", self.buffer[:2])[0] + 2

            LOGGER.debug(
                f"Buffer length: {len(self.buffer)}, Packet starts: {self.packet_starts}, Expected length: {self.expected_length}"
            )

            if self.expected_length is not None and self.expected_length > 1024:
                LOGGER.warning(f"Expected length too large: {self.expected_length}")
                self.discard_packet()

            elif (
                self.expected_length is not None
                and len(self.buffer) >= self.expected_length
            ):
                try:
                    message = RoutableMessage()
                    message.ParseFromString(
                        bytes(self.buffer[2 : self.expected_length])
                    )
                    self.buffer = self.buffer[self.expected_length :]
                    self.packet_starts = [
                        x - self.expected_length
                        for x in self.packet_starts
                        if x >= self.expected_length
                    ]
                    self.expected_length = None
                    self.callback(message)  # Call the callback with the parsed message

                except DecodeError:
                    self.discard_packet()
            else:
                return

    def discard_packet(self):
        """Drop the current packet and resynchronize on the next candidate start byte."""
        self.packet_starts.pop(0)
        if len(self.packet_starts) > 0:
            self.buffer = self.buffer[self.packet_starts[0] :]
            self.packet_starts = [x - self.packet_starts[0] for x in self.packet_starts]
        else:
            self.buffer = bytearray()
            self.packet_starts = []
        self.expected_length = None


# Optional post-timeout command verification.
#
# A lost ack from a mutating BLE command is inconclusive: the vehicle may have
# executed it anyway. When ``verify_commands`` is on, a timed-out mutation whose
# outcome can be derived from its own arguments is confirmed by reading the
# mapped state instead of surfacing the ambiguous unconfirmed timeout. A verify
# "plan" pairs the state reader to call with a predicate that checks the
# observed state against the requested value. Commands absent from these tables
# - true toggles, relative steps, and ack-only actions whose outcome cannot be
# derived from the request - have no plan and raise the unconfirmed timeout.
VerifyPlan = tuple[str, Callable[[Any], bool]]


def _decode_vcsec_status(msg: RoutableMessage) -> VehicleStatus | None:
    """Decode a broadcast frame's VCSEC status payload, if it carries one.

    Broadcasts are unsigned - they have no ``signature_data`` and need no
    session decrypt, unlike an addressed reply to our own signed request.
    """
    if not msg.HasField("protobuf_message_as_bytes"):
        return None
    try:
        vcsec = FromVCSECMessage.FromString(msg.protobuf_message_as_bytes)
    except DecodeError:
        return None
    if vcsec.HasField("vehicleStatus"):
        return vcsec.vehicleStatus
    return None


def _vcsec_verify_plan(command: UnsignedMessage) -> VerifyPlan | None:
    """Derive a VCSEC verify plan (read ``vehicle_state``) from a lost actuation."""
    if command.WhichOneof("sub_message") != "RKEAction":
        return None
    if command.RKEAction == RKEAction_E.RKE_ACTION_LOCK:
        return "vehicle_state", (
            lambda s: s.vehicleLockState == VehicleLockState_E.VEHICLELOCKSTATE_LOCKED
        )
    if command.RKEAction == RKEAction_E.RKE_ACTION_UNLOCK:
        return "vehicle_state", (
            lambda s: s.vehicleLockState == VehicleLockState_E.VEHICLELOCKSTATE_UNLOCKED
        )
    return None


def _plan_charge_limit(action: VehicleAction) -> VerifyPlan | None:
    percent = action.chargingSetLimitAction.percent
    return "charge_state", lambda s: s.charge_limit_soc == percent


def _plan_charging_amps(action: VehicleAction) -> VerifyPlan | None:
    amps = action.setChargingAmpsAction.charging_amps
    return "charge_state", lambda s: s.charging_amps == amps


def _plan_volume(action: VehicleAction) -> VerifyPlan | None:
    # A relative volume step is not derivable without a pre-read, so only the
    # absolute set is verifiable.
    if action.mediaUpdateVolume.WhichOneof("media_volume") != "volume_absolute_float":
        return None
    target = action.mediaUpdateVolume.volume_absolute_float
    return "media_state", lambda s: s.audio_volume == target


def _plan_temps(action: VehicleAction) -> VerifyPlan | None:
    driver = action.hvacTemperatureAdjustmentAction.driver_temp_celsius
    passenger = action.hvacTemperatureAdjustmentAction.passenger_temp_celsius
    return "climate_state", (
        lambda s: (
            s.driver_temp_setting == driver and s.passenger_temp_setting == passenger
        )
    )


def _plan_auto_conditioning(action: VehicleAction) -> VerifyPlan | None:
    power_on = action.hvacAutoAction.power_on
    return "climate_state", lambda s: s.is_climate_on == power_on


# Keyed by the ``VehicleAction`` oneof field an infotainment mutation sets.
_INFOTAINMENT_VERIFY_PLANS: dict[str, Callable[[VehicleAction], VerifyPlan | None]] = {
    "chargingSetLimitAction": _plan_charge_limit,
    "setChargingAmpsAction": _plan_charging_amps,
    "mediaUpdateVolume": _plan_volume,
    "hvacTemperatureAdjustmentAction": _plan_temps,
    "hvacAutoAction": _plan_auto_conditioning,
}


class VehicleBluetooth(Commands[BluetoothParentT], Generic[BluetoothParentT]):
    """Class describing the Tesla Fleet API vehicle endpoints and commands for a specific vehicle with command signing.

    Callers can catch failures from this class with a single ``TeslaFleetError``,
    but distinct outcomes hide behind that base: a connect/notify/write
    transport failure before any command reached the vehicle
    (``BluetoothTransportError``), an ack-wait timeout for a *mutating*
    command that was already written to the vehicle and whose outcome is
    genuinely unresolved (``BluetoothUnconfirmedCommand``), a mutating command
    *proven* not to have taken effect (``BluetoothCommandFailed``), and a
    plain response-wait timeout for anything else, e.g. a state read
    (``BluetoothTimeout``). Each preserves the underlying failure in its cause
    chain when one exists.

    A ``BluetoothUnconfirmedCommand`` (RKE/closure actions, HVAC/media/charging
    commands, ``wake_up``) means the vehicle can have executed the command
    without its ack reaching the client - it is unconfirmed, not failed.
    Callers must snapshot state before acting and verify the outcome with a
    follow-up state read after any such timeout, and must never blind-retry a
    non-idempotent command (toggles, volume steps, schedule add/remove) on a
    timeout alone, nor replay it on a fallback transport. The inherited
    WAIT/fault retry (``Commands._command``) can also re-send an
    already-executed command. Because it subclasses ``BluetoothTimeout``,
    existing ``except BluetoothTimeout`` handling still catches it.
    ``BluetoothCommandFailed`` deliberately does *not* subclass either - it
    means a state check actively contradicted the request, not that the
    outcome is unknown, so replaying the command on a fallback transport is
    safe and a router fails over on it normally (see below).

    ``confirmation`` sets how hard a mutating command tries to confirm itself
    before returning; it is a single ladder-depth choice, not an independent
    flag per rung:

    - ``"optimistic"``: return success as soon as the GATT write is confirmed,
      consulting nothing else. Only a write/transport failure
      (``BluetoothTransportError``) still raises. Pure speed mode - the caller
      owns any state verification it wants afterward.
    - ``"ack"`` (default): wait for the addressed ack. For a VCSEC actuation
      with a derivable expected end state (currently lock/unlock only), the
      wait also races a matching status broadcast against the ack: the vehicle
      keeps emitting unsolicited VCSEC status broadcasts on the same
      notification subscription even when it emits no addressed ack for the
      actuation, so a broadcast already showing the requested state confirms
      success without waiting out the ack timeout. A broadcast that shows a
      different state does not fail fast - it may simply predate the vehicle
      finishing the actuation, and a later broadcast in the same window could
      still confirm success - but if the whole window elapses with such a
      mismatch as the last word and nothing else confirming, that is
      now-final proof the command did not apply, raising
      ``BluetoothCommandFailed`` rather than the ambiguous timeout. An
      addressed ack, if it arrives first, still wins and still raises a real
      car-side rejection. A command with no derivable end state - true
      toggles, relative steps, and ack-only actions - has no broadcast to
      race and simply waits for the ack, raising ``BluetoothUnconfirmedCommand``
      on timeout.
    - ``"verify"``: same as ``"ack"``, plus one more rung - an ack/broadcast
      timeout for a command whose expected post-state is derivable from its
      arguments reads the mapped prover state over the same held connection
      and either returns a normal success result (the command executed),
      raises ``BluetoothCommandFailed`` (the read proves it did not), or
      re-raises ``BluetoothUnconfirmedCommand`` (the read itself could not be
      attempted, e.g. an INFO-domain prover needs the car awake). Commands
      with no derivable prover raise the unconfirmed timeout exactly as under
      ``"ack"``.

    Both rungs above derive their expected-end-state predicate from the same
    per-command table (one source of truth), just applied to a broadcast frame
    or a follow-up read respectively.

    ``raise_unconfirmed`` (default ``False``) is the orthogonal question of what
    to do once a ladder genuinely cannot resolve - the ack/broadcast wait
    (and, under ``"verify"``, the prover read) neither confirmed nor
    contradicted the request. Default ``False`` resolves that case as a
    best-effort success; ``True`` raises ``BluetoothUnconfirmedCommand``
    instead. It is moot under ``confirmation="optimistic"``, which is never
    inconclusive. A car-side rejection carried in an ack, any proven
    non-application (``BluetoothCommandFailed``), and write failures are
    unaffected by this flag and always raise - it only converts the "could not
    determine what happened" outcome.

    ``keepalive_interval`` (default ~20s, ``None``/``0`` disables) keeps an
    otherwise idle held connection from dropping: after that many seconds with
    no real GATT traffic, a minimal passive characteristic read is issued to
    reset the link supervision timer. It is idle-triggered - any real send or
    received frame resets the timer, so an active session pays nothing - and it
    is bounded and best-effort: a failed read (e.g. against a sleeping car) is
    swallowed and never raises into caller code or forces a reconnect; the
    existing reconnect machinery owns link recovery. Note the tradeoff: these
    reads keep an *awake* car awake and so defer vehicle sleep. Callers that
    want the car to sleep should disable keepalive or disconnect when idle.
    """

    ble_name: str
    confirmation: BluetoothConfirmation
    raise_unconfirmed: bool
    keepalive_interval: float | None
    device: BLEDevice | None = None
    client: BleakClient | None = None
    _queues: dict[Domain, asyncio.Queue[RoutableMessage]]
    _broadcast_watchers: dict[Domain, Callable[[RoutableMessage], None]]
    _ekey: ec.EllipticCurvePublicKey
    _buffer: ReassemblingBuffer
    _auth_method = "aes"
    _transport_name = "bluetooth"
    _ack_followup_timeout: float = 2
    _default_timeout: float = 5
    # A lost actuation ack is inconclusive; the contract is verify-by-state, so
    # a shorter wait than a data read's before raising loses nothing.
    _actuation_timeout: float = 2
    # Bounded so a keepalive read against a sleeping car can never hang the loop.
    _keepalive_timeout: float = 2
    _keepalive_task: asyncio.Task[None] | None = None
    _last_activity: float = 0.0

    def __init__(
        self,
        parent: BluetoothParentT,
        vin: str,
        key: ec.EllipticCurvePrivateKey | None = None,
        device: BLEDevice | None = None,
        confirmation: BluetoothConfirmation = "ack",
        keepalive_interval: float | None = DEFAULT_KEEPALIVE_INTERVAL,
        raise_unconfirmed: bool = False,
        *,
        verify_commands: bool | None = None,
        optimistic: bool | None = None,
    ):
        """Initialize a BLE-connected vehicle.

        ``verify_commands`` and ``optimistic`` are deprecated keyword-only
        aliases for ``confirmation="verify"``/``confirmation="optimistic"``
        respectively; passing either emits a ``DeprecationWarning`` and maps
        onto ``confirmation``, overriding any value passed there (a ``True``
        ``optimistic`` wins over a ``True`` ``verify_commands`` if both are
        somehow passed, matching the old dominance order).
        """
        super().__init__(parent, vin, key)
        if verify_commands is not None:
            warnings.warn(
                'verify_commands is deprecated; pass confirmation="verify" instead.',
                DeprecationWarning,
                stacklevel=2,
            )
            if verify_commands:
                confirmation = "verify"
        if optimistic is not None:
            warnings.warn(
                'optimistic is deprecated; pass confirmation="optimistic" instead.',
                DeprecationWarning,
                stacklevel=2,
            )
            if optimistic:
                confirmation = "optimistic"
        self.confirmation = confirmation
        self.keepalive_interval = keepalive_interval
        self.raise_unconfirmed = raise_unconfirmed
        self.ble_name = "S" + hashlib.sha1(vin.encode("utf-8")).hexdigest()[:16] + "C"
        self._queues = {
            Domain.DOMAIN_VEHICLE_SECURITY: asyncio.Queue(),
            Domain.DOMAIN_INFOTAINMENT: asyncio.Queue(),
        }
        self._broadcast_watchers = {}
        self.device = device
        self._connect_lock = asyncio.Lock()
        self._buffer = ReassemblingBuffer(self._on_message)

    @property
    def optimistic(self) -> bool:
        """Deprecated read-only view of ``confirmation == "optimistic"``."""
        return self.confirmation == "optimistic"

    @property
    def verify_commands(self) -> bool:
        """Deprecated read-only view of ``confirmation == "verify"``."""
        return self.confirmation == "verify"

    async def find_vehicle(
        self,
        name: str | None = None,
        address: str | None = None,
        scanner: BleakScanner | None = None,
    ) -> BLEDevice:
        """Find the Tesla BLE device."""

        if scanner is None:
            # No service_uuids filter: the vehicle advertises no service UUID
            # (SERVICE_UUID is GATT-only, post-connect); active scan is needed
            # since the name lives in the scan response, not the advertisement.
            scanner = BleakScanner(scanning_mode="active")

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
        """Assign the BLE device that should be used for subsequent connections."""
        self.device = device

    def get_device(self) -> BLEDevice | None:
        """Return the currently assigned BLE device, if one has been discovered."""
        return self.device

    async def connect(self, max_attempts: int = MAX_CONNECT_ATTEMPTS) -> None:
        """Connect to the Tesla BLE device."""
        if not self.device:
            raise ValueError(f"BLEDevice {self.ble_name} has not been found or set")
        try:
            self.client = await establish_connection(
                BleakClient,
                self.device,
                self.vin,
                max_attempts=max_attempts,
                # ble_device_callback=self.get_device,
                services=[SERVICE_UUID],
            )
            await self.client.start_notify(READ_UUID, self._on_notify)
            await self._start_keepalive()
        # bleak-esphome converts an aioesphomeapi transport timeout into a
        # builtin TimeoutError, not a BleakError, so catch both to keep every
        # connect transport failure within TeslaFleetError.
        except (BleakError, TimeoutError) as e:
            client = self.client
            self.client = None
            if client:
                try:
                    await client.disconnect()
                except (BleakError, TimeoutError):
                    pass
            raise BluetoothTransportError from e

    async def disconnect(self) -> bool:
        """Disconnect from the Tesla BLE device."""
        await self._stop_keepalive()
        if not self.client:
            return False
        await self.client.disconnect()
        return True

    async def connect_if_needed(self, max_attempts: int = MAX_CONNECT_ATTEMPTS) -> None:
        """Connect to the Tesla BLE device if not already connected."""
        async with self._connect_lock:
            if not self.client or not self.client.is_connected:
                LOGGER.info(f"Reconnecting to {self.ble_name}")
                await self.connect(max_attempts=max_attempts)

    async def _start_keepalive(self) -> None:
        """Start the idle keepalive task for this connection, if enabled."""
        await self._stop_keepalive()
        if not self.keepalive_interval:
            return
        self._last_activity = time.monotonic()
        self._keepalive_task = asyncio.ensure_future(self._keepalive_loop())

    async def _stop_keepalive(self) -> None:
        """Cancel and await the keepalive task so it never outlives the link."""
        task = self._keepalive_task
        self._keepalive_task = None
        if task is None:
            return
        task.cancel()
        try:
            await task
        except (asyncio.CancelledError, Exception):
            pass

    async def _keepalive_loop(self) -> None:
        """Read a trivial characteristic after each span of GATT idleness."""
        assert self.keepalive_interval is not None
        while True:
            idle_for = time.monotonic() - self._last_activity
            wait = self.keepalive_interval - idle_for
            if wait > 0:
                await asyncio.sleep(wait)
                continue
            await self._keepalive_read()
            # The read itself is activity, so the next span starts from now.
            self._last_activity = time.monotonic()

    async def _keepalive_read(self) -> None:
        """Issue one bounded passive read; swallow every failure.

        A keepalive failure must never surface to callers or trigger reconnects
        - link recovery is owned by ``connect_if_needed`` - and a sleeping car
        must stay detectable, so a read that cannot complete is simply dropped.
        """
        client = self.client
        if client is None or not client.is_connected:
            return
        try:
            async with asyncio.timeout(self._keepalive_timeout):
                await client.read_gatt_char(VERSION_UUID)
        except Exception as e:
            LOGGER.debug(f"Keepalive read failed: {e}")

    async def __aenter__(self) -> VehicleBluetooth[BluetoothParentT]:
        """Enter the async context."""
        await self.connect()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> None:
        """Exit the async context."""
        await self.disconnect()

    def _on_notify(self, sender: BleakGATTCharacteristic, data: bytearray) -> None:
        """Receive data from the Tesla BLE device."""
        if sender.uuid != READ_UUID:
            LOGGER.error(f"Unexpected sender: {sender}")
            return
        self._last_activity = time.monotonic()
        self._buffer.receive_data(data)

    def _on_message(self, msg: RoutableMessage) -> None:
        """Route addressed BLE replies into the per-domain response queue."""

        if msg.to_destination.routing_address != self._from_destination:
            LOGGER.debug("Ignoring broadcast message (not addressed to us)")
            watcher = self._broadcast_watchers.get(msg.from_destination.domain)
            if watcher is not None:
                watcher(msg)
            return

        queue = self._queues.get(msg.from_destination.domain)
        if queue is None:
            # Domain enum has values (e.g. DOMAIN_BROADCAST, DOMAIN_AUTHD) with
            # no session/queue of our own; indexing _queues directly would
            # raise KeyError and abort the reassembly loop mid-buffer.
            LOGGER.debug(
                f"Ignoring message from unhandled domain {msg.from_destination.domain}"
            )
            return

        LOGGER.debug(f"Received response: {msg}")
        queue.put_nowait(msg)

    async def _send(
        self,
        msg: RoutableMessage,
        requires: str,
        expects_data: bool = True,
        *,
        timeout: float | None = None,
        optimistic: bool = False,
        confirm_broadcast: Callable[[VehicleStatus], bool] | None = None,
    ) -> RoutableMessage:
        """Serialize a message and send to the vehicle and wait for a response.

        When ``expects_data`` is False the reply is a single terminal ack (a
        VCSEC actuation, no data frame follows), so the ack is returned as soon
        as it arrives and a shorter total timeout applies. ``optimistic`` skips
        waiting for any reply at all - once the GATT write is confirmed, an
        empty ``RoutableMessage`` is returned immediately. ``confirm_broadcast``
        races the addressed-reply wait against a matching unsolicited state
        broadcast on the same domain, returning on whichever arrives first.
        """

        if timeout is None:
            timeout = self._default_timeout if expects_data else self._actuation_timeout

        domain = msg.to_destination.domain
        async with self._sessions[domain].lock:
            LOGGER.debug(f"Sending message {msg}")

            payload = prependLength(msg.SerializeToString())

            # Empty the queue before sending the message
            while not self._queues[domain].empty():
                discarded = await self._queues[domain].get()
                LOGGER.warning(f"Discarded message {discarded}")

            await self.connect_if_needed()
            assert self.client is not None
            try:
                await self.client.write_gatt_char(WRITE_UUID, payload, True)
                self._last_activity = time.monotonic()
            # bleak-esphome converts an aioesphomeapi write timeout into a
            # builtin TimeoutError, not a BleakError, so catch both to keep the
            # GATT-write transport failure within TeslaFleetError.
            except (BleakError, TimeoutError) as e:
                raise BluetoothTransportError from e

            if optimistic:
                return RoutableMessage()

            if confirm_broadcast is None:
                return await self._await_response(
                    domain, msg, requires, expects_data, timeout
                )
            return await self._await_response_or_broadcast(
                domain, msg, requires, expects_data, timeout, confirm_broadcast
            )

    async def _await_response(
        self,
        domain: Domain,
        msg: RoutableMessage,
        requires: str,
        expects_data: bool,
        timeout: float,
    ) -> RoutableMessage:
        """Wait for the addressed reply carrying ``requires`` or our ack."""
        try:
            async with asyncio.timeout(timeout):
                LOGGER.debug(f"Waiting for response with {requires}")
                while True:
                    resp = await self._queues[domain].get()
                    LOGGER.debug(f"Received message {resp}")

                    self.validate_msg(resp)

                    if resp.HasField(requires):
                        return resp

                    # ACK response: has our request_uuid but not the required field.
                    # Some commands (e.g. RKE wake/lock) only return an ACK with no data.
                    # Wait briefly for a follow-up data response before returning the ACK.
                    if msg.uuid and resp.request_uuid == msg.uuid:
                        if not expects_data:
                            # A VCSEC actuation's ack is terminal; no data
                            # frame follows, so return without the wait.
                            return resp
                        LOGGER.debug(
                            "Received ACK for our request, waiting briefly for data follow-up"
                        )
                        try:
                            async with asyncio.timeout(self._ack_followup_timeout):
                                while True:
                                    resp2 = await self._queues[domain].get()
                                    LOGGER.debug(f"Received follow-up message {resp2}")
                                    self.validate_msg(resp2)
                                    if resp2.HasField(requires):
                                        return resp2
                        except TimeoutError:
                            LOGGER.debug("No data follow-up, returning ACK response")
                            return resp

                    LOGGER.debug(f"Ignoring message without required field {requires}")
        except TimeoutError as e:
            raise BluetoothTimeout from e

    async def _await_response_or_broadcast(
        self,
        domain: Domain,
        msg: RoutableMessage,
        requires: str,
        expects_data: bool,
        timeout: float,
        confirm_broadcast: Callable[[VehicleStatus], bool],
    ) -> RoutableMessage:
        """Race the addressed reply against a matching state broadcast.

        A broadcast that decodes but does not satisfy ``confirm_broadcast`` is
        tracked, not treated as an immediate failure - it may simply predate
        the vehicle finishing the actuation, and a later broadcast in the same
        window could still confirm success. Only the addressed-reply path can
        raise a rejection while the race is live. If the whole window elapses
        with neither an ack nor a confirming broadcast, but at least one
        mismatching broadcast was observed, that mismatch is now-final proof
        the command did not reach the requested state:
        ``BluetoothCommandFailed`` is raised instead of the ambiguous
        ``BluetoothTimeout``/``BluetoothUnconfirmedCommand``, so a fallback
        transport can fail over safely instead of risking a double-apply on a
        genuinely unresolved ack.
        """
        mismatches: list[VehicleStatus] = []
        response_task = asyncio.ensure_future(
            self._await_response(domain, msg, requires, expects_data, timeout)
        )
        broadcast_task = asyncio.ensure_future(
            self._await_broadcast_confirmation(domain, confirm_broadcast, mismatches)
        )
        try:
            done, _ = await asyncio.wait(
                {response_task, broadcast_task}, return_when=asyncio.FIRST_COMPLETED
            )
            if response_task in done:
                return response_task.result()
            return broadcast_task.result()
        except BluetoothTimeout as timeout_exc:
            if mismatches:
                raise BluetoothCommandFailed(
                    timeout_exc.data, timeout_exc.status
                ) from timeout_exc
            raise
        finally:
            for task in (response_task, broadcast_task):
                if not task.done():
                    task.cancel()
            await asyncio.gather(response_task, broadcast_task, return_exceptions=True)

    async def _await_broadcast_confirmation(
        self,
        domain: Domain,
        confirm_broadcast: Callable[[VehicleStatus], bool],
        mismatches: list[VehicleStatus],
    ) -> RoutableMessage:
        """Wait for a broadcast whose decoded VCSEC status satisfies ``confirm_broadcast``.

        Live-verified: a VCSEC actuation's addressed ack can be lost while the
        vehicle keeps emitting its status broadcast on the same notification
        subscription, carrying the very state change the actuation caused. A
        broadcast that decodes but doesn't match is appended to ``mismatches``
        instead of resolving anything here - the caller only treats it as
        proof of failure once the whole wait window elapses with nothing else
        confirming.
        """
        future: asyncio.Future[RoutableMessage] = (
            asyncio.get_running_loop().create_future()
        )

        def on_broadcast(broadcast: RoutableMessage) -> None:
            if future.done():
                return
            status = _decode_vcsec_status(broadcast)
            if status is None:
                return
            if confirm_broadcast(status):
                future.set_result(broadcast)
            else:
                mismatches.append(status)

        self._broadcast_watchers[domain] = on_broadcast
        try:
            return await future
        finally:
            if self._broadcast_watchers.get(domain) is on_broadcast:
                del self._broadcast_watchers[domain]

    # Group 12: VCSEC closures (Bluetooth-only for individual doors)

    async def open_front_driver_door(self) -> dict[str, Any]:
        """Unlatches/opens the front driver door."""
        return await self._sendVehicleSecurity(
            UnsignedMessage(
                closureMoveRequest=ClosureMoveRequest(
                    frontDriverDoor=ClosureMoveType_E.CLOSURE_MOVE_TYPE_OPEN
                )
            )
        )

    async def close_front_driver_door(self) -> dict[str, Any]:
        """Requests front driver door close; OK ack may not mean physically latched."""
        return await self._sendVehicleSecurity(
            UnsignedMessage(
                closureMoveRequest=ClosureMoveRequest(
                    frontDriverDoor=ClosureMoveType_E.CLOSURE_MOVE_TYPE_CLOSE
                )
            )
        )

    async def open_front_passenger_door(self) -> dict[str, Any]:
        """Unlatches/opens the front passenger door."""
        return await self._sendVehicleSecurity(
            UnsignedMessage(
                closureMoveRequest=ClosureMoveRequest(
                    frontPassengerDoor=ClosureMoveType_E.CLOSURE_MOVE_TYPE_OPEN
                )
            )
        )

    async def close_front_passenger_door(self) -> dict[str, Any]:
        """Requests front passenger door close; OK ack may not mean physically latched."""
        return await self._sendVehicleSecurity(
            UnsignedMessage(
                closureMoveRequest=ClosureMoveRequest(
                    frontPassengerDoor=ClosureMoveType_E.CLOSURE_MOVE_TYPE_CLOSE
                )
            )
        )

    async def open_rear_driver_door(self) -> dict[str, Any]:
        """Unlatches/opens the rear driver door."""
        return await self._sendVehicleSecurity(
            UnsignedMessage(
                closureMoveRequest=ClosureMoveRequest(
                    rearDriverDoor=ClosureMoveType_E.CLOSURE_MOVE_TYPE_OPEN
                )
            )
        )

    async def close_rear_driver_door(self) -> dict[str, Any]:
        """Requests rear driver door close; OK ack may not mean physically latched."""
        return await self._sendVehicleSecurity(
            UnsignedMessage(
                closureMoveRequest=ClosureMoveRequest(
                    rearDriverDoor=ClosureMoveType_E.CLOSURE_MOVE_TYPE_CLOSE
                )
            )
        )

    async def open_rear_passenger_door(self) -> dict[str, Any]:
        """Unlatches/opens the rear passenger door."""
        return await self._sendVehicleSecurity(
            UnsignedMessage(
                closureMoveRequest=ClosureMoveRequest(
                    rearPassengerDoor=ClosureMoveType_E.CLOSURE_MOVE_TYPE_OPEN
                )
            )
        )

    async def close_rear_passenger_door(self) -> dict[str, Any]:
        """Requests rear passenger door close; OK ack may not mean physically latched."""
        return await self._sendVehicleSecurity(
            UnsignedMessage(
                closureMoveRequest=ClosureMoveRequest(
                    rearPassengerDoor=ClosureMoveType_E.CLOSURE_MOVE_TYPE_CLOSE
                )
            )
        )

    async def query_display_name(self, max_attempts: int = 5) -> str | None:
        """Read the device name via GATT characteristic if available"""
        for i in range(max_attempts):
            try:
                # Standard GATT Device Name characteristic (0x2A00)
                await self.connect_if_needed()
                assert self.client
                device_name = (await self.client.read_gatt_char(NAME_UUID)).decode(
                    "utf-8"
                )
                if device_name.startswith("🔑 "):
                    return device_name.replace("🔑 ", "")
                await asyncio.sleep(1)
                LOGGER.debug(
                    f"Attempt {i + 1} to query display name failed, {device_name}"
                )
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
                return int.from_bytes(device_version, byteorder="big")
        except Exception as e:
            LOGGER.error(f"Failed to read device version: {e}")
        return None

    async def _command(
        self,
        domain: Domain,
        command: bytes,
        attempt: int = 0,
        expects_data: bool = True,
        confirm_broadcast: Callable[[VehicleStatus], bool] | None = None,
    ) -> dict[str, Any]:
        """Serialize a message and send to the signed command endpoint."""
        await self.connect_if_needed()
        return await super()._command(
            domain,
            command,
            attempt,
            expects_data=expects_data,
            confirm_broadcast=confirm_broadcast,
        )

    async def _ensure_handshake(self, domain: Domain) -> None:
        if not self._sessions[domain].ready:
            await self._handshake(domain)
        if not self._sessions[domain].ready:
            raise BluetoothTimeout()

    async def _send_optimistic(self, domain: Domain, command: bytes) -> dict[str, Any]:
        """Sign and write a mutating command without waiting for any reply.

        Only a write/transport failure (``BluetoothTransportError``) raises;
        the caller owns any state verification it wants afterward.
        """
        session = self._sessions[domain]
        async with session.lock:
            if self._auth_method == "hmac":
                msg = await self._commandHmac(session, command)
            else:
                msg = await self._commandAes(session, command)
        await self._send(msg, "protobuf_message_as_bytes", optimistic=True)
        return {"response": {"result": True, "reason": ""}}

    def _unconfirmed_outcome(
        self,
        name: str,
        unconfirmed: BluetoothUnconfirmedCommand,
        *,
        cause: BaseException,
    ) -> dict[str, Any]:
        """Resolve an exhausted confirmation ladder per ``raise_unconfirmed``.

        Reached only once nothing could determine what happened - verification
        is off, has no plan for this command, or its read could not complete.
        Proven non-application - a verify-read mismatch, or a mismatching
        broadcast still standing once the whole wait window elapsed - is
        unambiguous negative evidence and raises ``BluetoothCommandFailed``
        directly from the caller, never routed through here.
        """
        if self.raise_unconfirmed:
            raise unconfirmed from cause
        LOGGER.debug(
            "command=%s transport=%s raise_unconfirmed=False result=success (best-effort)",
            name,
            self._transport_name,
        )
        return {"response": {"result": True, "reason": ""}}

    async def _sendVehicleSecurity(
        self,
        command: UnsignedMessage,
        *,
        confirm_broadcast: Callable[[VehicleStatus], bool] | None = None,
    ) -> dict[str, Any]:
        """Send a VCSEC actuation.

        ``confirm_broadcast`` is accepted only for signature compatibility
        with ``Commands._sendVehicleSecurity``; this override always derives
        its own predicate from ``command`` (see ``plan`` below) and ignores
        any value passed here.

        A lost ack after the write reached the vehicle is unconfirmed, not
        failed, so a timed-out wait raises ``BluetoothUnconfirmedCommand``
        rather than plain ``BluetoothTimeout`` - see that exception's
        docstring. For a command with a verify plan (lock/unlock), the same
        wait window also races a matching VCSEC status broadcast against the
        ack - live-verified, the vehicle keeps broadcasting status on the same
        subscription even when it emits no addressed ack, so a broadcast
        showing the requested end state confirms success before the ack
        timeout is ever reached. If the window instead elapses with a
        mismatching broadcast as the last word (see
        ``_await_response_or_broadcast``) or, with ``confirmation="verify"``, a
        post-timeout read that contradicts the request, that is proven
        non-application and raises ``BluetoothCommandFailed`` - not the
        ambiguous ``BluetoothUnconfirmedCommand`` - since a fallback router
        can safely fail over on a command proven not to have applied. With
        ``confirmation="optimistic"``, the write itself is the whole outcome
        and none of this ladder runs. With ``raise_unconfirmed`` off, only a
        ladder that is still genuinely unresolved resolves as a best-effort
        success instead of raising - see the class docstring.
        """
        await self._ensure_handshake(Domain.DOMAIN_VEHICLE_SECURITY)
        if self.confirmation == "optimistic":
            return await self._send_optimistic(
                Domain.DOMAIN_VEHICLE_SECURITY, command.SerializeToString()
            )
        plan = _vcsec_verify_plan(command)
        try:
            return await super()._sendVehicleSecurity(
                command, confirm_broadcast=plan[1] if plan else None
            )
        except BluetoothTimeout as timeout:
            unconfirmed = BluetoothUnconfirmedCommand(timeout.data, timeout.status)
            name = vcsec_command_name(command)
            if self.confirmation == "verify":
                result = await self._resolve_timeout(plan, unconfirmed)
                if result is not None:
                    LOGGER.debug(
                        "command=%s transport=%s verify_commands=resolved result=%s",
                        name,
                        self._transport_name,
                        result.get("response", {}).get("result"),
                    )
                    return result
                LOGGER.debug(
                    "command=%s transport=%s verify_commands=unresolved",
                    name,
                    self._transport_name,
                )
            return self._unconfirmed_outcome(name, unconfirmed, cause=timeout)

    async def _sendInfotainment(
        self, command: Action, *, mutating: bool = True
    ) -> dict[str, Any]:
        """Send an infotainment command.

        Same unconfirmed-ack, ``confirmation``, and ``raise_unconfirmed``
        semantics as ``_sendVehicleSecurity`` - see there. ``mutating=False``
        (``ping()`` only) is exempt from all three: it always waits for its
        real reply.
        """
        await self._ensure_handshake(Domain.DOMAIN_INFOTAINMENT)
        if self.confirmation == "optimistic" and mutating:
            return await self._send_optimistic(
                Domain.DOMAIN_INFOTAINMENT, command.SerializeToString()
            )
        try:
            return await super()._sendInfotainment(command)
        except BluetoothTimeout as timeout:
            if not mutating:
                raise
            unconfirmed = BluetoothUnconfirmedCommand(timeout.data, timeout.status)
            name = infotainment_command_name(command)
            if self.confirmation == "verify":
                resolver = _INFOTAINMENT_VERIFY_PLANS.get(
                    command.vehicleAction.WhichOneof("vehicle_action_msg")
                )
                plan = resolver(command.vehicleAction) if resolver else None
                result = await self._resolve_timeout(plan, unconfirmed)
                if result is not None:
                    LOGGER.debug(
                        "command=%s transport=%s verify_commands=resolved result=%s",
                        name,
                        self._transport_name,
                        result.get("response", {}).get("result"),
                    )
                    return result
                LOGGER.debug(
                    "command=%s transport=%s verify_commands=unresolved",
                    name,
                    self._transport_name,
                )
            return self._unconfirmed_outcome(name, unconfirmed, cause=timeout)

    async def _resolve_timeout(
        self, plan: VerifyPlan | None, timeout: BluetoothTimeout
    ) -> dict[str, Any] | None:
        """Confirm a timed-out mutation by state.

        Returns the confirmed success result, or ``None`` if verification
        could not even be attempted - no plan for this command, or the prover
        read itself failed (an INFO-domain prover needs the vehicle awake; a
        ``TeslaFleetError`` from a sleeping car is not woken just to verify).
        ``None`` leaves the caller to resolve the outcome via
        ``raise_unconfirmed``. A verify mismatch - the read completed and does
        not show the requested value - is unambiguous proof the command did
        not apply, so it raises ``BluetoothCommandFailed`` instead of the
        ambiguous ``timeout``, regardless of ``raise_unconfirmed``: a fallback
        router may safely fail over on proven non-application, unlike on an
        unresolved timeout where a replay could double-execute the command.
        """
        if plan is None:
            return None
        reader_name, executed = plan
        try:
            state = await getattr(self, reader_name)()
        except TeslaFleetError:
            return None
        if executed(state):
            return {"response": {"result": True, "reason": ""}}
        raise BluetoothCommandFailed(timeout.data, timeout.status) from timeout

    async def pair(
        self,
        role: Role = Role.ROLE_OWNER,
        form: KeyFormFactor = KeyFormFactor.KEY_FORM_FACTOR_CLOUD_KEY,
        timeout: float = 300,
        poll_interval: float = 5,
    ):
        """Pair the key, confirming completion by reply or by key-state polling.

        The whitelist-operation success is a single VCSEC frame. If the BLE
        session cycles while the user walks to the vehicle to approve, that
        frame can land on a dead session and be lost, hanging a plain one-shot
        wait. The reply stays the fast path when it survives, but completion is
        also confirmed by polling whether our public key is now whitelisted - a
        VCSEC handshake with our own key succeeds only once it is. The whitelist
        op is written exactly once; it is never re-sent, which would re-prompt
        the user, and the poll re-handshakes on a fresh connection so it
        survives mid-wait reconnects. Raises ``BluetoothTimeout`` if neither
        path confirms before ``timeout`` seconds elapse.
        """

        if poll_interval <= 0:
            raise ValueError("poll_interval must be greater than 0")

        request = UnsignedMessage(
            WhitelistOperation=WhitelistOperation(
                addKeyToWhitelistAndAddPermissions=PermissionChange(
                    key=PublicKey(PublicKeyRaw=self._public_key), keyRole=role
                ),
                metadataForKey=KeyMetadata(keyFormFactor=form),
            )
        )
        msg = RoutableMessage(
            to_destination=Destination(domain=Domain.DOMAIN_VEHICLE_SECURITY),
            from_destination=Destination(routing_address=self._from_destination),
            protobuf_message_as_bytes=request.SerializeToString(),
            uuid=randbytes(16),
        )

        deadline = time.monotonic() + timeout

        # Fast path: write the op once and wait one interval for its one-shot
        # reply. A lost reply falls through to polling rather than re-sending.
        try:
            resp = await self._send(
                msg,
                "protobuf_message_as_bytes",
                timeout=max(0.0, min(poll_interval, deadline - time.monotonic())),
            )
            self._raise_for_whitelist_reply(resp)
            return
        except BluetoothTimeout:
            pass

        # Slow path: poll whether our key became effective on the vehicle.
        while time.monotonic() < deadline:
            if self._consume_late_whitelist_reply():
                return
            if await self._pair_probe():
                return
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                break
            await asyncio.sleep(min(poll_interval, remaining))

        if self._consume_late_whitelist_reply():
            return
        if await self._pair_probe():
            return

        raise BluetoothTimeout

    async def _pair_probe(self) -> bool:
        """Return True once our public key is whitelisted on the vehicle.

        A VCSEC handshake with our own public key completes only when that key
        is on the vehicle's whitelist; until pairing is approved it faults with
        ``NotOnWhitelistFault``. Any transport failure mid-poll (a dropped
        session) is treated as 'not yet' so polling keeps running across
        reconnects rather than aborting.
        """
        try:
            return await self._handshake(Domain.DOMAIN_VEHICLE_SECURITY)
        except TeslaFleetError:
            return False

    def _consume_late_whitelist_reply(self) -> bool:
        queue = self._queues[Domain.DOMAIN_VEHICLE_SECURITY]
        deferred: list[RoutableMessage] = []
        try:
            while True:
                resp = queue.get_nowait()
                try:
                    respMsg = FromVCSECMessage.FromString(
                        resp.protobuf_message_as_bytes
                    )
                except DecodeError:
                    deferred.append(resp)
                    continue
                if respMsg.HasField("commandStatus") and respMsg.commandStatus.HasField(
                    "whitelistOperationStatus"
                ):
                    self._raise_for_whitelist_reply(resp)
                    return True
                deferred.append(resp)
        except asyncio.QueueEmpty:
            return False
        finally:
            for resp in deferred:
                queue.put_nowait(resp)

    def _raise_for_whitelist_reply(self, resp: RoutableMessage) -> None:
        """Raise the mapped fault if a whitelist-op reply reports one."""
        respMsg = FromVCSECMessage.FromString(resp.protobuf_message_as_bytes)
        info = (
            respMsg.commandStatus.whitelistOperationStatus.whitelistOperationInformation
        )
        if not info:
            return
        if info < len(WHITELIST_OPERATION_STATUS):
            exception = WHITELIST_OPERATION_STATUS[info]
            if exception:
                raise exception
        else:
            raise WhitelistOperationStatus(
                f"Unknown whitelist operation failure: {info}"
            )

    async def wake_up(self):
        """Wake up the vehicle security computer.

        A ``BluetoothUnconfirmedCommand`` from this command can be a false
        negative even when the vehicle wakes successfully, so callers should
        treat wake as best-effort and confirm readiness with a retried
        INFO-domain read. The infotainment computer may still need a short
        delay before it can complete signed-command handshakes, so callers that
        issue INFO-domain reads immediately after waking should retry
        ``BluetoothTimeout`` with backoff.
        """
        return await self._sendVehicleSecurity(
            UnsignedMessage(RKEAction=RKEAction_E.RKE_ACTION_WAKE_VEHICLE)
        )

    async def vehicle_data(self, endpoints: list[BluetoothVehicleData]) -> VehicleData:
        """Get vehicle data over the BLE infotainment channel.

        This is a BLE-specific method, not a re-implementation of the cloud
        one, and it diverges from ``VehicleFleet.vehicle_data()`` in ways a
        cloud user porting to BLE should not be surprised by:

        - ``endpoints`` takes ``BluetoothVehicleData`` (proto request names
          like ``"GetChargeState"``), not the cloud ``VehicleDataEndpoint``
          (REST names like ``"charge_state"``) - the two enums are not
          interchangeable.
        - The return type is the ``VehicleData`` protobuf message built from
          the signed-command reply, not a REST JSON ``dict``. Use
          ``tesla_fleet_api.tesla.bluetooth.toDict``/``toJson`` to convert it
          if a dict is needed.
        - Unlike the cloud method, ``endpoints`` has no "all endpoints"
          default: requesting more than one sub-state in a single call risks
          exceeding the vehicle's signed-command response-size cap, raised as
          ``TeslaFleetMessageFaultResponseSizeExceedsMTU`` - observed live
          with as few as two endpoints requested together. The individual
          state readers (``charge_state()``, ``climate_state()``, etc.) each
          issue their own single-endpoint request and are not subject to
          this cap; prefer them, or a narrow explicit ``endpoints`` subset,
          over a large composite call. A future enhancement could split a
          multi-endpoint request into multiple under-the-cap round trips and
          merge the replies, but that auto-chunking is not implemented here.
        """
        return await self._getInfotainment(
            Action(
                vehicleAction=VehicleAction(
                    getVehicleData=GetVehicleData(
                        getChargeState=GetChargeState()
                        if BluetoothVehicleData.CHARGE_STATE in endpoints
                        else None,
                        getClimateState=GetClimateState()
                        if BluetoothVehicleData.CLIMATE_STATE in endpoints
                        else None,
                        getDriveState=GetDriveState()
                        if BluetoothVehicleData.DRIVE_STATE in endpoints
                        else None,
                        getLocationState=GetLocationState()
                        if BluetoothVehicleData.LOCATION_STATE in endpoints
                        else None,
                        getClosuresState=GetClosuresState()
                        if BluetoothVehicleData.CLOSURES_STATE in endpoints
                        else None,
                        getChargeScheduleState=GetChargeScheduleState()
                        if BluetoothVehicleData.CHARGE_SCHEDULE_STATE in endpoints
                        else None,
                        getPreconditioningScheduleState=GetPreconditioningScheduleState()
                        if BluetoothVehicleData.PRECONDITIONING_SCHEDULE_STATE
                        in endpoints
                        else None,
                        getTirePressureState=GetTirePressureState()
                        if BluetoothVehicleData.TIRE_PRESSURE_STATE in endpoints
                        else None,
                        getMediaState=GetMediaState()
                        if BluetoothVehicleData.MEDIA_STATE in endpoints
                        else None,
                        getMediaDetailState=GetMediaDetailState()
                        if BluetoothVehicleData.MEDIA_DETAIL_STATE in endpoints
                        else None,
                        getSoftwareUpdateState=GetSoftwareUpdateState()
                        if BluetoothVehicleData.SOFTWARE_UPDATE_STATE in endpoints
                        else None,
                        getParentalControlsState=GetParentalControlsState()
                        if BluetoothVehicleData.PARENTAL_CONTROLS_STATE in endpoints
                        else None,
                    )
                )
            )
        )

    async def charge_state(self) -> ChargeState:
        """Return the current charging state over the BLE vehicle data channel."""
        return (
            await self._getInfotainment(
                Action(
                    vehicleAction=VehicleAction(
                        getVehicleData=GetVehicleData(getChargeState=GetChargeState())
                    )
                )
            )
        ).charge_state

    async def climate_state(self) -> ClimateState:
        """Return the current HVAC and cabin climate state over BLE."""
        return (
            await self._getInfotainment(
                Action(
                    vehicleAction=VehicleAction(
                        getVehicleData=GetVehicleData(getClimateState=GetClimateState())
                    )
                )
            )
        ).climate_state

    async def drive_state(self) -> DriveState:
        """Return the current drive state, including gear and motion-related fields."""
        return (
            await self._getInfotainment(
                Action(
                    vehicleAction=VehicleAction(
                        getVehicleData=GetVehicleData(getDriveState=GetDriveState())
                    )
                )
            )
        ).drive_state

    async def location_state(self) -> LocationState:
        """Return the current location state reported over BLE."""
        return (
            await self._getInfotainment(
                Action(
                    vehicleAction=VehicleAction(
                        getVehicleData=GetVehicleData(
                            getLocationState=GetLocationState()
                        )
                    )
                )
            )
        ).location_state

    async def closures_state(self) -> ClosuresState:
        """Return the current closures state for doors, trunks, and windows over BLE."""
        return (
            await self._getInfotainment(
                Action(
                    vehicleAction=VehicleAction(
                        getVehicleData=GetVehicleData(
                            getClosuresState=GetClosuresState()
                        )
                    )
                )
            )
        ).closures_state

    async def charge_schedule_state(self) -> ChargeScheduleState:
        """Return the current scheduled charging configuration over BLE."""
        return (
            await self._getInfotainment(
                Action(
                    vehicleAction=VehicleAction(
                        getVehicleData=GetVehicleData(
                            getChargeScheduleState=GetChargeScheduleState()
                        )
                    )
                )
            )
        ).charge_schedule_state

    async def preconditioning_schedule_state(self) -> PreconditioningScheduleState:
        """Return the current preconditioning schedule configuration over BLE."""
        return (
            await self._getInfotainment(
                Action(
                    vehicleAction=VehicleAction(
                        getVehicleData=GetVehicleData(
                            getPreconditioningScheduleState=GetPreconditioningScheduleState()
                        )
                    )
                )
            )
        ).preconditioning_schedule_state

    async def tire_pressure_state(self) -> TirePressureState:
        """Return the current tire pressure state over BLE."""
        return (
            await self._getInfotainment(
                Action(
                    vehicleAction=VehicleAction(
                        getVehicleData=GetVehicleData(
                            getTirePressureState=GetTirePressureState()
                        )
                    )
                )
            )
        ).tire_pressure_state

    async def media_state(self) -> MediaState:
        """Return the current media playback state over BLE."""
        return (
            await self._getInfotainment(
                Action(
                    vehicleAction=VehicleAction(
                        getVehicleData=GetVehicleData(getMediaState=GetMediaState())
                    )
                )
            )
        ).media_state

    async def media_detail_state(self) -> MediaDetailState:
        """Return detailed media metadata, such as track and source information, over BLE."""
        return (
            await self._getInfotainment(
                Action(
                    vehicleAction=VehicleAction(
                        getVehicleData=GetVehicleData(
                            getMediaDetailState=GetMediaDetailState()
                        )
                    )
                )
            )
        ).media_detail_state

    async def software_update_state(self) -> SoftwareUpdateState:
        """Return the current software update status over BLE."""
        return (
            await self._getInfotainment(
                Action(
                    vehicleAction=VehicleAction(
                        getVehicleData=GetVehicleData(
                            getSoftwareUpdateState=GetSoftwareUpdateState()
                        )
                    )
                )
            )
        ).software_update_state

    async def parental_controls_state(self) -> ParentalControlsState:
        """Return the current parental controls state over BLE."""
        return (
            await self._getInfotainment(
                Action(
                    vehicleAction=VehicleAction(
                        getVehicleData=GetVehicleData(
                            getParentalControlsState=GetParentalControlsState()
                        )
                    )
                )
            )
        ).parental_controls_state

    async def vehicle_state(self) -> VehicleStatus:
        """Return the vehicle security-domain status over BLE."""
        return await self._getVehicleSecurity(
            UnsignedMessage(
                InformationRequest=InformationRequest(
                    informationRequestType=InformationRequestType.INFORMATION_REQUEST_TYPE_GET_STATUS
                )
            )
        )
