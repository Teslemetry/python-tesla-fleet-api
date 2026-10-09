"""Charge-port readiness and physical confirmation through real command encoding.

Only the message transport boundary is replaced. ACKs and live state replies go through the
production signing, decoding and router paths. No vehicle is actuated here.
"""

from __future__ import annotations

import asyncio
import hashlib
import struct
from typing import Any
from unittest.mock import AsyncMock, MagicMock

from bleak.exc import BleakError
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.exceptions import InvalidTag
from google.protobuf.message import DecodeError
from tesla_protocol.command.signatures_pb2 import SessionInfo, SignatureType, Tag
from tesla_protocol.command.car_server_pb2 import Action
from tesla_protocol.command.universal_message_pb2 import (
    Domain,
    RoutableMessage,
    MessageFault_E,
)
from tesla_protocol.command.vcsec_pb2 import (
    ClosureMoveType_E,
    CommandStatus,
    FromVCSECMessage,
    OperationStatus_E,
    RKEAction_E,
    UnsignedMessage,
    VehicleSleepStatus_E,
    VehicleStatus,
)
from tesla_protocol.command.vehicle_pb2 import ChargeState, VehicleData

from tesla_fleet_api.const import Trunk
from tesla_fleet_api.exceptions import (
    BluetoothCommandFailed,
    BluetoothTimeout,
    BluetoothTransportError,
    BluetoothUnconfirmedCommand,
    SessionInfoAuthenticationFault,
    SignedCommandResponseReplayed,
    TeslaFleetMessageFaultResponseSizeExceedsMTU,
)
from tesla_fleet_api.router import VehicleRouter
from tesla_fleet_api.tesla.vehicle.bluetooth import WRITE_UUID

import test_session_info_authentication as handshake_fixtures

from ble_mocked_transport import (
    MockedBleTransportTestCase,
    decrypt_sent_command,
    infotainment_vehicle_data_reply,
    vcsec_ok_reply,
    vcsec_vehicle_status_reply,
)

ASLEEP = VehicleSleepStatus_E.VEHICLE_SLEEP_STATUS_ASLEEP
AWAKE = VehicleSleepStatus_E.VEHICLE_SLEEP_STATUS_AWAKE


def charge(
    *,
    cable: str | None = "IEC",
    charging: str | None = "Stopped",
    latch: str | None = "Engaged",
    flap: bool | None = True,
    unlatched: bool = False,
) -> ChargeState:
    """Build charge data with explicit oneof values or deliberately absent fields."""
    state = ChargeState(charge_cable_unlatched=unlatched)
    if cable is not None:
        getattr(state.conn_charge_cable, cable).SetInParent()
    if charging is not None:
        getattr(state.charging_state, charging).SetInParent()
    if latch is not None:
        getattr(state.charge_port_latch, latch).SetInParent()
    if flap is not None:
        state.charge_port_door_open = flap
    return state


def encrypted_ack(vehicle: Any, msg: RoutableMessage, *, corrupt=False, replay=False):
    """Build a request-bound encrypted reply, optionally damage its authentication."""
    domain = Domain.DOMAIN_VEHICLE_SECURITY
    session = vehicle._sessions[domain]
    request_hash = (
        bytes([SignatureType.SIGNATURE_TYPE_AES_GCM_PERSONALIZED])
        + msg.signature_data.AES_GCM_Personalized_data.tag
    )
    counter = 17
    metadata = bytes(
        [
            Tag.TAG_SIGNATURE_TYPE,
            1,
            SignatureType.SIGNATURE_TYPE_AES_GCM_RESPONSE,
            Tag.TAG_DOMAIN,
            1,
            domain,
            Tag.TAG_PERSONALIZATION,
            17,
            *vehicle.vin.encode(),
            Tag.TAG_COUNTER,
            4,
            *struct.pack(">I", counter),
            Tag.TAG_FLAGS,
            4,
            *struct.pack(">I", 0),
            Tag.TAG_REQUEST_HASH,
            17,
            *request_hash,
            Tag.TAG_FAULT,
            4,
            *struct.pack(">I", 0),
            Tag.TAG_END,
        ]
    )
    reply = vcsec_ok_reply()
    nonce = b"\x07" * 12
    ciphertext = AESGCM(session.sharedKey).encrypt(
        nonce, reply.protobuf_message_as_bytes, hashlib.sha256(metadata).digest()
    )
    reply.protobuf_message_as_bytes = ciphertext[:-16]
    signature = reply.signature_data.AES_GCM_Response_data
    signature.nonce = nonce
    signature.counter = counter
    signature.tag = b"\x00" * 16 if corrupt else ciphertext[-16:]
    if replay:
        assert session.record_response_counter(request_hash, counter)
    return reply


class Car:
    """Small stateful peer: decode requests and answer only the requested domain."""

    def __init__(self, vehicle: Any, before: ChargeState, after: list[Any]):
        """Set the baseline and post-command replies, with an awake peer by default."""
        self.vehicle = vehicle
        self.before = before
        self.after = after
        self.sleep = AWAKE
        self.events: list[str] = []
        self.open_requests: list[UnsignedMessage] = []
        self.ack: Any = vcsec_ok_reply()
        self.probe_failures = 0
        self.baseline_failures = 0
        self.probe_hangs = False
        self.read_hangs = False
        self.post_read_started = asyncio.Event()

    async def __call__(self, msg: RoutableMessage, *_: Any, **__: Any) -> Any:
        """Decode signed requests, record their order, and inject configured faults."""
        if msg.HasField("session_info_request"):
            assert msg.to_destination.domain == Domain.DOMAIN_INFOTAINMENT
            self.events.append("ready_probe")
            if self.probe_hangs:
                await asyncio.Future()
            if self.probe_failures:
                self.probe_failures -= 1
                raise BluetoothTimeout()
            return RoutableMessage()
        plaintext = decrypt_sent_command(self.vehicle, msg)
        if msg.to_destination.domain == Domain.DOMAIN_VEHICLE_SECURITY:
            command = UnsignedMessage.FromString(plaintext)
            kind = command.WhichOneof("sub_message")
            if kind == "InformationRequest":
                self.events.append("sleep_read")
                return vcsec_vehicle_status_reply(
                    VehicleStatus(vehicleSleepStatus=self.sleep)
                )
            if kind == "RKEAction":
                assert command.RKEAction == RKEAction_E.RKE_ACTION_WAKE_VEHICLE
                self.events.append("wake")
                self.sleep = AWAKE
                return vcsec_ok_reply()
            assert kind == "closureMoveRequest"
            self.open_requests.append(command)
            self.events.append("open")
            if isinstance(self.ack, BaseException):
                raise self.ack
            return self.ack(self.vehicle, msg) if callable(self.ack) else self.ack
        assert msg.to_destination.domain == Domain.DOMAIN_INFOTAINMENT
        action = Action.FromString(plaintext)
        assert action.vehicleAction.getVehicleData.HasField("getChargeState")
        if not self.open_requests:
            self.events.append("baseline")
            if self.baseline_failures:
                self.baseline_failures -= 1
                raise BluetoothTimeout()
            return infotainment_vehicle_data_reply(
                VehicleData(charge_state=self.before)
            )
        self.events.append("verify")
        self.post_read_started.set()
        if self.read_hangs:
            await asyncio.Future()
        state = self.after[0]
        if len(self.after) > 1:
            self.after.pop(0)
        if isinstance(state, BaseException):
            raise state
        return infotainment_vehicle_data_reply(VehicleData(charge_state=state))


class Cloud:
    def __init__(self, vin: str):
        """Expose a mock cloud command so tests can detect accidental fallback."""
        self.vin = vin
        self.charge_port_door_open = AsyncMock(
            return_value={"response": {"result": True, "reason": "cloud"}}
        )


class ChargePortVerificationTests(MockedBleTransportTestCase):
    def setup_car(
        self, before: ChargeState | None = None, after: list[Any] | None = None
    ):
        """Create a verify-mode vehicle and peer with short, bounded test deadlines."""
        vehicle, send = self.make_vehicle(
            confirmation="verify", raise_unconfirmed=False
        )
        vehicle._wake_timeout = 0.2
        vehicle._infotainment_boot_timeout = 0.1
        vehicle._charge_port_verify_timeout = 0.03
        vehicle._charge_port_verify_interval = 0.001
        car = Car(
            vehicle,
            before if before is not None else charge(),
            after if after is not None else [charge(latch="Disengaged")],
        )
        send.side_effect = car.__call__
        return vehicle, car

    async def test_asleep_wakes_and_waits_for_readiness_before_one_open(self):
        """Retry INFO readiness after waking, then send only the charge-port closure."""
        vehicle, car = self.setup_car()
        car.sleep = ASLEEP
        car.probe_failures = 2
        result = await vehicle.charge_port_door_open()
        self.assertTrue(result["response"]["result"])
        self.assertEqual(
            car.events,
            [
                "sleep_read",
                "wake",
                "ready_probe",
                "ready_probe",
                "ready_probe",
                "baseline",
                "open",
                "verify",
            ],
        )
        self.assertEqual(len(car.open_requests), 1)
        request = car.open_requests[0].closureMoveRequest
        self.assertEqual(request.chargePort, ClosureMoveType_E.CLOSURE_MOVE_TYPE_OPEN)
        self.assertEqual(
            [field.name for field, _ in request.ListFields()], ["chargePort"]
        )

    async def test_awake_still_probes_fresh_readiness_with_cached_session(self):
        """Require a fresh INFO probe despite an awake car and cached signed session."""
        vehicle, car = self.setup_car()
        await vehicle.charge_port_door_open()
        self.assertEqual(
            car.events, ["sleep_read", "ready_probe", "baseline", "open", "verify"]
        )

    async def test_ack_without_latch_release_never_succeeds_or_falls_back(self):
        """An ACK with the latch still engaged must remain unresolved on Bluetooth."""
        vehicle, car = self.setup_car(after=[charge()])
        cloud = Cloud(vehicle.vin)
        with self.assertRaises(BluetoothUnconfirmedCommand):
            await VehicleRouter(vehicle, cloud).charge_port_door_open()
        self.assertEqual(len(car.open_requests), 1)
        cloud.charge_port_door_open.assert_not_awaited()

    async def test_late_release_after_ack_is_confirmed_without_repeating_open(self):
        """Poll past engaged and blocking states without repeating the opening."""
        vehicle, car = self.setup_car(
            after=[charge(), charge(latch="Blocking"), charge(latch="Disengaged")]
        )
        self.assertTrue((await vehicle.charge_port_door_open())["response"]["result"])
        self.assertEqual(car.events.count("verify"), 3)
        self.assertEqual(len(car.open_requests), 1)

    async def test_lost_ack_can_be_confirmed_by_latch_without_cloud_replay(self):
        """Accept explicit latch release after a lost ACK for either strictness flag."""
        for raise_unconfirmed in (False, True):
            with self.subTest(raise_unconfirmed=raise_unconfirmed):
                vehicle, car = self.setup_car()
                vehicle.raise_unconfirmed = raise_unconfirmed
                car.ack = BluetoothTimeout()
                cloud = Cloud(vehicle.vin)
                result = await VehicleRouter(vehicle, cloud).charge_port_door_open()
                self.assertTrue(result["response"]["result"])
                self.assertEqual(len(car.open_requests), 1)
                cloud.charge_port_door_open.assert_not_awaited()
                self.assertEqual(vehicle.raise_unconfirmed, raise_unconfirmed)

    async def test_lost_ack_with_unknown_state_is_not_best_effort_success(self):
        """Missing state after a lost ACK must raise instead of succeeding or replaying."""
        vehicle, car = self.setup_car(after=[ChargeState()])
        car.ack = BluetoothTimeout()
        cloud = Cloud(vehicle.vin)
        with self.assertRaises(BluetoothUnconfirmedCommand):
            await VehicleRouter(vehicle, cloud).charge_port_door_open()
        cloud.charge_port_door_open.assert_not_awaited()
        self.assertEqual(len(car.open_requests), 1)

    async def test_missing_sna_and_blocking_latches_cannot_confirm(self):
        """Reject inconclusive latch values even when the legacy unlatched flag is true."""
        for latch in (None, "SNA", "Blocking", "Engaged"):
            with self.subTest(latch=latch):
                vehicle, car = self.setup_car(
                    after=[charge(latch=latch, unlatched=True)]
                )
                with self.assertRaises(BluetoothUnconfirmedCommand):
                    await vehicle.charge_port_door_open()
                self.assertEqual(len(car.open_requests), 1)

    async def test_explicit_disengaged_wins_over_false_unlatched_flag(self):
        """Use explicit latch release when the legacy unlatched flag disagrees."""
        vehicle, _ = self.setup_car(after=[charge(latch="Disengaged", unlatched=False)])
        self.assertTrue((await vehicle.charge_port_door_open())["response"]["result"])

    async def test_unplugged_requires_open_flap_not_disengaged_latch(self):
        """For a disconnected cable, require a present true flap field to confirm."""
        baseline = charge(
            cable="SNA", charging="Disconnected", latch="Disengaged", flap=False
        )
        for flap in (None, False, True):
            with self.subTest(flap=flap):
                vehicle, car = self.setup_car(
                    baseline,
                    [
                        charge(
                            cable="SNA",
                            charging="Disconnected",
                            latch="Disengaged",
                            flap=flap,
                        )
                    ],
                )
                if flap:
                    self.assertTrue(
                        (await vehicle.charge_port_door_open())["response"]["result"]
                    )
                else:
                    with self.assertRaises(BluetoothUnconfirmedCommand):
                        await vehicle.charge_port_door_open()
                self.assertEqual(len(car.open_requests), 1)

    async def test_missing_cable_type_with_explicit_disconnected_can_open_flap(self):
        """An explicit Disconnected state can select the flap goal without a cable type."""
        vehicle, _ = self.setup_car(
            charge(cable=None, charging="Disconnected", flap=False),
            [charge(cable=None, charging="Disconnected", flap=True)],
        )
        self.assertTrue((await vehicle.charge_port_door_open())["response"]["result"])

    async def test_unknown_or_conflicting_baseline_never_actuates_and_can_fail_over(
        self,
    ):
        """Allow cloud fallback for an ambiguous baseline before any opening is sent."""
        for before in (
            ChargeState(),
            charge(cable="SNA"),
            charge(cable=None),
            charge(charging="Disconnected"),
        ):
            with self.subTest(before=before):
                vehicle, car = self.setup_car(before)
                cloud = Cloud(vehicle.vin)
                result = await VehicleRouter(vehicle, cloud).charge_port_door_open()
                self.assertEqual(result["response"]["reason"], "cloud")
                self.assertEqual(car.open_requests, [])
                cloud.charge_port_door_open.assert_awaited_once()

    async def test_all_known_cable_types_require_latch_release(self):
        """Select latch verification for every supported positive cable type."""
        for cable in ("IEC", "SAE", "GB_AC", "GB_DC"):
            with self.subTest(cable=cable):
                vehicle, _ = self.setup_car(
                    charge(cable=cable), [charge(cable=cable, latch="Disengaged")]
                )
                self.assertTrue(
                    (await vehicle.charge_port_door_open())["response"]["result"]
                )

    async def test_removing_cable_does_not_replace_latch_goal_with_flap_goal(self):
        """Keep the original latch goal when later reads show an unplugged cable."""
        vehicle, car = self.setup_car(
            after=[charge(cable="SNA", charging="Disconnected", latch=None, flap=True)]
        )
        with self.assertRaises(BluetoothUnconfirmedCommand):
            await vehicle.charge_port_door_open()
        self.assertEqual(len(car.open_requests), 1)

    async def test_inserting_cable_cannot_confirm_original_flap_goal(self):
        """An inserted cable invalidates flap confirmation despite an open flap."""
        vehicle, _ = self.setup_car(
            charge(cable="SNA", charging="Disconnected", flap=False),
            [charge(latch="Disengaged", flap=True)],
        )
        with self.assertRaises(BluetoothUnconfirmedCommand):
            await vehicle.charge_port_door_open()

    async def test_disabled_wake_never_sends_open_or_wake_when_asleep(self):
        """Respect disabled wake by rejecting an asleep car before either actuation."""
        vehicle, car = self.setup_car()
        car.sleep = ASLEEP
        vehicle.wake_if_asleep = False
        with self.assertRaises(BluetoothCommandFailed):
            await vehicle.charge_port_door_open()
        self.assertEqual(car.events, ["sleep_read"])

    async def test_disabled_wake_allows_already_awake_vehicle(self):
        """Allow an awake car to complete verification without issuing a wake request."""
        vehicle, car = self.setup_car()
        vehicle.wake_if_asleep = False
        await vehicle.charge_port_door_open()
        self.assertNotIn("wake", car.events)

    async def test_readiness_deadline_prevents_open_and_allows_safe_cloud_fallback(
        self,
    ):
        """Bound a stalled INFO probe before opening for both asleep and awake cars."""
        for sleep in (ASLEEP, AWAKE):
            with self.subTest(sleep=sleep):
                vehicle, car = self.setup_car()
                car.sleep = sleep
                car.probe_hangs = True
                vehicle._wake_timeout = 0.02
                cloud = Cloud(vehicle.vin)
                result = await asyncio.wait_for(
                    VehicleRouter(vehicle, cloud).charge_port_door_open(), 0.5
                )
                self.assertEqual(result["response"]["reason"], "cloud")
                self.assertEqual(car.open_requests, [])
                cloud.charge_port_door_open.assert_awaited_once()

    async def test_hung_post_read_is_bounded_and_blocks_cloud_fallback(self):
        """Bound a stalled verification read while preserving the no-replay guarantee."""
        vehicle, car = self.setup_car()
        car.read_hangs = True
        cloud = Cloud(vehicle.vin)
        with self.assertRaises(BluetoothUnconfirmedCommand):
            await asyncio.wait_for(
                VehicleRouter(vehicle, cloud).charge_port_door_open(), 0.5
            )
        self.assertEqual(len(car.open_requests), 1)
        cloud.charge_port_door_open.assert_not_awaited()

    async def test_post_read_failures_remain_unconfirmed_not_replayable(self):
        """Wrap post-submission read and transport faults as unresolved outcomes."""
        for error in (
            BluetoothTimeout(),
            BluetoothTransportError(),
            TimeoutError(),
            BleakError("lost link"),
            ValueError("bad reply"),
        ):
            with self.subTest(error=type(error).__name__):
                vehicle, car = self.setup_car(after=[error])
                cloud = Cloud(vehicle.vin)
                with self.assertRaises(BluetoothUnconfirmedCommand):
                    await VehicleRouter(vehicle, cloud).charge_port_door_open()
                self.assertEqual(len(car.open_requests), 1)
                cloud.charge_port_door_open.assert_not_awaited()

    async def test_transient_read_failure_can_recover_without_resending(self):
        """Recover verification from a transient read timeout with no second opening."""
        vehicle, car = self.setup_car(
            after=[BluetoothTimeout(), charge(latch="Disengaged")]
        )
        self.assertTrue((await vehicle.charge_port_door_open())["response"]["result"])
        self.assertEqual(car.events.count("verify"), 2)
        self.assertEqual(len(car.open_requests), 1)

    async def test_pre_submission_transport_failure_can_fall_back(self):
        """Preserve cloud fallback for a write known to fail before submission."""
        vehicle, car = self.setup_car()
        car.ack = BluetoothTransportError()
        cloud = Cloud(vehicle.vin)
        result = await VehicleRouter(vehicle, cloud).charge_port_door_open()
        self.assertEqual(result["response"]["reason"], "cloud")
        self.assertNotIn("verify", car.events)
        cloud.charge_port_door_open.assert_awaited_once()

    async def test_ambiguous_backend_write_failure_never_replays(self):
        """Treat timeout and Bleak write faults as delivery-unknown, blocking replay."""
        for error in (TimeoutError(), BleakError("ambiguous write")):
            with self.subTest(error=type(error).__name__):
                vehicle, car = self.setup_car(after=[charge()])
                car.ack = error
                cloud = Cloud(vehicle.vin)
                with self.assertRaises(BluetoothUnconfirmedCommand):
                    await VehicleRouter(vehicle, cloud).charge_port_door_open()
                self.assertEqual(len(car.open_requests), 1)
                cloud.charge_port_door_open.assert_not_awaited()

    async def test_bad_actuation_replies_are_verified_without_cloud_replay(self):
        """Use latch evidence after decode, authentication, replay, or MTU faults."""
        malformed = vcsec_ok_reply()
        malformed.protobuf_message_as_bytes = b"\xff"
        for reply, error_type in (
            (malformed, DecodeError),
            (lambda v, m: encrypted_ack(v, m, corrupt=True), InvalidTag),
            (
                lambda v, m: encrypted_ack(v, m, replay=True),
                SignedCommandResponseReplayed,
            ),
            (SessionInfoAuthenticationFault(), SessionInfoAuthenticationFault),
            (
                TeslaFleetMessageFaultResponseSizeExceedsMTU(),
                TeslaFleetMessageFaultResponseSizeExceedsMTU,
            ),
        ):
            for latch in ("Engaged", "Disengaged"):
                with self.subTest(error=error_type.__name__, latch=latch):
                    vehicle, car = self.setup_car(after=[charge(latch=latch)])
                    car.ack = reply
                    cloud = Cloud(vehicle.vin)
                    if latch == "Disengaged":
                        self.assertTrue(
                            (
                                await VehicleRouter(
                                    vehicle, cloud
                                ).charge_port_door_open()
                            )["response"]["result"]
                        )
                    else:
                        with self.assertRaises(BluetoothUnconfirmedCommand) as caught:
                            await VehicleRouter(vehicle, cloud).charge_port_door_open()
                        self.assertIsInstance(caught.exception.__cause__, error_type)
                    self.assertEqual(len(car.open_requests), 1)
                    self.assertIn("verify", car.events)
                    cloud.charge_port_door_open.assert_not_awaited()

    async def test_valid_encrypted_ack_still_requires_physical_confirmation(self):
        """A valid authenticated ACK alone cannot prove an engaged latch released."""
        vehicle, car = self.setup_car(after=[charge()])
        car.ack = encrypted_ack
        with self.assertRaises(BluetoothUnconfirmedCommand) as caught:
            await vehicle.charge_port_door_open()
        self.assertIsNone(caught.exception.__cause__)
        self.assertEqual(len(car.open_requests), 1)

    async def test_transient_baseline_timeout_waits_before_actuating(self):
        """Retry baseline reads within preflight and open only after a valid response."""
        vehicle, car = self.setup_car()
        car.sleep = ASLEEP
        car.baseline_failures = 2
        await vehicle.charge_port_door_open()
        self.assertEqual(car.events.count("baseline"), 3)
        self.assertGreater(car.events.index("open"), car.events.index("baseline") + 2)
        self.assertEqual(len(car.open_requests), 1)

    async def test_baseline_read_timeouts_exhaust_preflight_without_opening(self):
        """Exhaust persistent baseline timeouts before any opening, allowing fallback."""
        vehicle, car = self.setup_car()
        car.baseline_failures = 10000
        vehicle._wake_timeout = 0.02
        cloud = Cloud(vehicle.vin)
        result = await asyncio.wait_for(
            VehicleRouter(vehicle, cloud).charge_port_door_open(), 0.5
        )
        self.assertEqual(result["response"]["reason"], "cloud")
        self.assertEqual(car.open_requests, [])
        cloud.charge_port_door_open.assert_awaited_once()

    async def test_logs_physical_outcome_after_ack(self):
        """Log the observed confirmation outcome rather than inferring it from an ACK."""
        for latch, outcome in (("Engaged", "unconfirmed"), ("Disengaged", "confirmed")):
            with self.subTest(latch=latch):
                vehicle, _ = self.setup_car(after=[charge(latch=latch)])
                with self.assertLogs("tesla_fleet_api", level="DEBUG") as logged:
                    if latch == "Disengaged":
                        await vehicle.charge_port_door_open()
                    else:
                        with self.assertRaises(BluetoothUnconfirmedCommand):
                            await vehicle.charge_port_door_open()
                self.assertTrue(
                    any(
                        f"physical_confirmation={outcome}" in line
                        for line in logged.output
                    )
                )

    async def test_explicit_rejection_is_not_overridden_by_already_released_latch(self):
        """Return an explicit VCSEC rejection without consulting the latch prover."""
        vehicle, car = self.setup_car()
        car.ack = vcsec_ok_reply()
        car.ack.protobuf_message_as_bytes = FromVCSECMessage(
            commandStatus=CommandStatus(
                operationStatus=OperationStatus_E.OPERATIONSTATUS_ERROR
            )
        ).SerializeToString()
        result = await vehicle.charge_port_door_open()
        self.assertFalse(result["response"]["result"])
        self.assertNotIn("verify", car.events)

    async def test_cancellation_propagates_without_cloud_replay(self):
        """Propagate cancellation during verification without replay or policy changes."""
        vehicle, car = self.setup_car()
        car.read_hangs = True
        cloud = Cloud(vehicle.vin)
        task = asyncio.create_task(
            VehicleRouter(vehicle, cloud).charge_port_door_open()
        )
        await asyncio.wait_for(car.post_read_started.wait(), 0.5)
        task.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await task
        cloud.charge_port_door_open.assert_not_awaited()
        self.assertFalse(vehicle.raise_unconfirmed)
        self.assertEqual(vehicle.confirmation, "verify")

    async def test_real_transport_with_cold_info_session_and_bare_ack(self):
        """Exercise cold INFO authentication and ambiguous actuation via real queues."""
        # Keep real domain locks, request/response queues, handshake validation,
        # command signing and response decoding. Only GATT I/O is replaced.
        for latch in ("Engaged", "Disengaged"):
            for reply_kind in ("bare_ack", "write_timeout", "response_mtu"):
                with self.subTest(latch=latch, reply_kind=reply_kind):
                    vehicle, car = self.setup_car(after=[charge(latch=latch)])
                    del vehicle._send
                    car.sleep = ASLEEP
                    info = vehicle._sessions[Domain.DOMAIN_INFOTAINMENT]
                    info.epoch = None
                    self.assertFalse(info.ready)
                    vehicle._default_timeout = 0.6
                    vehicle._actuation_timeout = 0.01
                    vehicle._ack_followup_timeout = 1
                    vehicle.client = MagicMock(is_connected=True)
                    server_key = ec.generate_private_key(ec.SECP256R1())
                    session_info = SessionInfo(
                        publicKey=handshake_fixtures._public_key_bytes(server_key),
                        epoch=b"\x42" * 16,
                        clock_time=100,
                        counter=0,
                    )

                    async def write(uuid, payload, response):
                        """Authenticate INFO and inject bare ACK, write timeout, or MTU replies."""
                        self.assertEqual(uuid, WRITE_UUID)
                        self.assertTrue(response)
                        msg = RoutableMessage.FromString(payload[2:])
                        if msg.HasField("session_info_request"):
                            self.assertEqual(
                                msg.to_destination.domain, Domain.DOMAIN_INFOTAINMENT
                            )
                            car.events.append("ready_probe")
                            reply = handshake_fixtures._session_info_reply(
                                vehicle,
                                Domain.DOMAIN_INFOTAINMENT,
                                session_info,
                                msg.uuid,
                            )
                        else:
                            prior_opens = len(car.open_requests)
                            reply = await car(msg)
                            if len(car.open_requests) > prior_opens:
                                if reply_kind == "write_timeout":
                                    raise TimeoutError("ESPHome write outcome unknown")
                                # A bare ACK has no commandStatus/protobuf body.
                                reply = RoutableMessage(request_uuid=msg.uuid)
                                reply.from_destination.domain = (
                                    Domain.DOMAIN_VEHICLE_SECURITY
                                )
                                if reply_kind == "response_mtu":
                                    reply.signedMessageStatus.signed_message_fault = MessageFault_E.MESSAGEFAULT_ERROR_RESPONSE_MTU_EXCEEDED
                        reply.to_destination.routing_address = vehicle._from_destination
                        vehicle._on_message(reply)

                    vehicle.client.write_gatt_char = AsyncMock(side_effect=write)
                    cloud = Cloud(vehicle.vin)
                    if latch == "Disengaged":
                        result = await asyncio.wait_for(
                            VehicleRouter(vehicle, cloud).charge_port_door_open(), 0.5
                        )
                        self.assertTrue(result["response"]["result"])
                    else:
                        with self.assertRaises(BluetoothUnconfirmedCommand):
                            await asyncio.wait_for(
                                VehicleRouter(vehicle, cloud).charge_port_door_open(),
                                0.5,
                            )
                    self.assertTrue(info.ready)
                    self.assertEqual(len(car.open_requests), 1)
                    self.assertIn("verify", car.events)
                    self.assertEqual(
                        car.events[:5],
                        ["sleep_read", "wake", "ready_probe", "baseline", "open"],
                    )
                    cloud.charge_port_door_open.assert_not_awaited()
                    self.assertTrue(
                        all(queue.empty() for queue in vehicle._queues.values())
                    )
                    self.assertTrue(
                        all(
                            not session.lock.locked()
                            for session in vehicle._sessions.values()
                        )
                    )

    async def test_other_confirmation_modes_keep_ack_or_write_only_contract(self):
        """Leave ack and optimistic modes on their existing single-send paths."""
        for mode in ("ack", "optimistic"):
            with self.subTest(mode=mode):
                vehicle, send = self.make_vehicle(confirmation=mode)
                send.return_value = vcsec_ok_reply()
                self.assertTrue(
                    (await vehicle.charge_port_door_open())["response"]["result"]
                )
                self.assertEqual(send.await_count, 1)

    async def test_frunk_boot_and_port_close_do_not_gain_readiness_or_verification(
        self,
    ):
        """Keep frunk, boot, and port closing outside charge-port-specific preflight."""
        for action, args in (
            ("actuate_trunk", (Trunk.FRONT,)),
            ("actuate_trunk", (Trunk.REAR,)),
            ("charge_port_door_close", ()),
        ):
            with self.subTest(action=action, args=args):
                vehicle, send = self.make_vehicle(confirmation="verify")
                send.return_value = vcsec_ok_reply()
                self.assertTrue(
                    (await getattr(vehicle, action)(*args))["response"]["result"]
                )
                self.assertEqual(send.await_count, 1)
