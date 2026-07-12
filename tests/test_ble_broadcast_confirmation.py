"""Tests for broadcast-as-confirmation: racing a VCSEC actuation's addressed
ack against a matching unsolicited status broadcast on the same subscription.

Unlike the other BLE command tests, these drive the real (unmocked) ``_send``
send/wait state machine - only the GATT client is faked - so the actual
asyncio race between the addressed-reply queue and the broadcast watcher runs
for real. Broadcasts are injected with ``vehicle._on_message(...)``, exactly
as ``_on_notify``/the reassembling buffer would deliver them from a real
notification.
"""

from __future__ import annotations

import asyncio
from typing import Any, cast
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, MagicMock

from bleak.exc import BleakError
from cryptography.hazmat.primitives.asymmetric import ec

from tesla_fleet_api.exceptions import (
    BluetoothCommandFailed,
    BluetoothTimeout,
    BluetoothUnconfirmedCommand,
)
from tesla_fleet_api.tesla.vehicle.bluetooth import VehicleBluetooth
from tesla_fleet_api.tesla.vehicle.proto.errors_pb2 import GenericError_E, NominalError
from tesla_fleet_api.tesla.vehicle.proto.universal_message_pb2 import (
    Destination,
    Domain,
    RoutableMessage,
)
from tesla_fleet_api.tesla.vehicle.proto.vcsec_pb2 import (
    CommandStatus,
    FromVCSECMessage,
    OperationStatus_E,
    VehicleLockState_E,
    VehicleStatus,
)

VIN = "5YJXCAE43LF123456"
DOMAIN = Domain.DOMAIN_VEHICLE_SECURITY


def _make_vehicle(**kwargs: Any) -> VehicleBluetooth[Any]:
    """A VehicleBluetooth with real send/race logic but a faked GATT client."""
    parent = MagicMock()
    parent.private_key = ec.generate_private_key(ec.SECP256R1())
    vehicle = VehicleBluetooth(parent, VIN, **kwargs)
    vehicle.connect_if_needed = AsyncMock()  # type: ignore[method-assign]
    vehicle.client = MagicMock()
    vehicle.client.write_gatt_char = AsyncMock()

    # Mark both signed-command sessions ready so _command skips the
    # handshake round-trip (which would otherwise also go through _send).
    sessions = cast("dict[int, Any]", getattr(vehicle, "_sessions"))
    for session in sessions.values():
        session.epoch = b"\x00" * 16
        session.hmac = b"\x00" * 32
        session.delta = 0
        session.sharedKey = b"\x00" * 16
    return vehicle


def _status_broadcast(lock_state: "VehicleLockState_E.ValueType") -> RoutableMessage:
    """An unsolicited VCSEC status broadcast, not addressed to us."""
    body = FromVCSECMessage(vehicleStatus=VehicleStatus(vehicleLockState=lock_state))
    return RoutableMessage(
        from_destination=Destination(domain=DOMAIN),
        protobuf_message_as_bytes=body.SerializeToString(),
    )


def _locked_broadcast() -> RoutableMessage:
    return _status_broadcast(VehicleLockState_E.VEHICLELOCKSTATE_LOCKED)


def _unlocked_broadcast() -> RoutableMessage:
    return _status_broadcast(VehicleLockState_E.VEHICLELOCKSTATE_UNLOCKED)


def _addressed_ok_ack(vehicle: VehicleBluetooth[Any]) -> RoutableMessage:
    """An addressed VCSEC actuation ack reporting success."""
    body = FromVCSECMessage(
        commandStatus=CommandStatus(
            operationStatus=OperationStatus_E.OPERATIONSTATUS_OK
        )
    )
    return RoutableMessage(
        to_destination=Destination(
            domain=DOMAIN, routing_address=vehicle._from_destination
        ),
        from_destination=Destination(domain=DOMAIN),
        protobuf_message_as_bytes=body.SerializeToString(),
    )


def _addressed_status_reply(
    vehicle: VehicleBluetooth[Any], lock_state: "VehicleLockState_E.ValueType"
) -> RoutableMessage:
    """An addressed reply to a state read (e.g. the ``verify_commands`` prober)."""
    body = FromVCSECMessage(vehicleStatus=VehicleStatus(vehicleLockState=lock_state))
    return RoutableMessage(
        to_destination=Destination(
            domain=DOMAIN, routing_address=vehicle._from_destination
        ),
        from_destination=Destination(domain=DOMAIN),
        protobuf_message_as_bytes=body.SerializeToString(),
    )


def _addressed_rejection_ack(vehicle: VehicleBluetooth[Any]) -> RoutableMessage:
    """An addressed VCSEC reply carrying a car-side rejection."""
    body = FromVCSECMessage(
        nominalError=NominalError(
            genericError=GenericError_E.GENERICERROR_VEHICLE_NOT_IN_PARK
        )
    )
    return RoutableMessage(
        to_destination=Destination(
            domain=DOMAIN, routing_address=vehicle._from_destination
        ),
        from_destination=Destination(domain=DOMAIN),
        protobuf_message_as_bytes=body.SerializeToString(),
    )


async def _wait_until_watching(
    vehicle: VehicleBluetooth[Any], domain: Domain, timeout: float = 1.0
) -> None:
    """Block until the broadcast race has armed its watcher for ``domain``."""

    async def poll() -> None:
        while domain not in cast(
            "dict[Any, Any]", getattr(vehicle, "_broadcast_watchers")
        ):
            await asyncio.sleep(0)

    await asyncio.wait_for(poll(), timeout=timeout)


class BroadcastConfirmsBeforeAckTests(IsolatedAsyncioTestCase):
    async def test_broadcast_arriving_during_gatt_write_confirms_lock(self) -> None:
        vehicle = _make_vehicle()
        vehicle._actuation_timeout = 5.0

        async def write_then_broadcast(*_: Any) -> None:
            vehicle._on_message(_locked_broadcast())
            await asyncio.sleep(0)

        vehicle.client.write_gatt_char = AsyncMock(side_effect=write_then_broadcast)

        result = await asyncio.wait_for(vehicle.door_lock(), timeout=0.5)

        self.assertEqual(result, {"response": {"result": True, "reason": ""}})

    async def test_broadcast_confirms_lock_before_actuation_timeout(self) -> None:
        vehicle = _make_vehicle()
        vehicle._actuation_timeout = 5.0  # generous ceiling the broadcast must beat

        task = asyncio.ensure_future(vehicle.door_lock())
        await _wait_until_watching(vehicle, DOMAIN)
        vehicle._on_message(_locked_broadcast())

        # No ack is ever delivered; a well-under-ceiling completion proves the
        # broadcast - not a fallback timeout - resolved the call.
        result = await asyncio.wait_for(task, timeout=0.5)

        self.assertEqual(result, {"response": {"result": True, "reason": ""}})

    async def test_broadcast_confirms_unlock(self) -> None:
        vehicle = _make_vehicle()
        vehicle._actuation_timeout = 5.0

        task = asyncio.ensure_future(vehicle.door_unlock())
        await _wait_until_watching(vehicle, DOMAIN)
        vehicle._on_message(_unlocked_broadcast())

        result = await asyncio.wait_for(task, timeout=0.5)

        self.assertEqual(result, {"response": {"result": True, "reason": ""}})


class AckRejectionWinsTests(IsolatedAsyncioTestCase):
    async def test_ack_rejection_surfaces_despite_mismatched_broadcasts(self) -> None:
        vehicle = _make_vehicle()

        task = asyncio.ensure_future(vehicle.door_lock())
        await _wait_until_watching(vehicle, DOMAIN)
        # A broadcast showing the wrong state must not confirm and must not
        # block the addressed rejection from winning the race.
        vehicle._on_message(_unlocked_broadcast())
        vehicle._on_message(_addressed_rejection_ack(vehicle))

        result = await asyncio.wait_for(task, timeout=1.0)

        self.assertEqual(result["response"]["result"], False)

    async def test_ack_success_wins_over_no_broadcast(self) -> None:
        vehicle = _make_vehicle()

        task = asyncio.ensure_future(vehicle.door_lock())
        await _wait_until_watching(vehicle, DOMAIN)
        vehicle._on_message(_addressed_ok_ack(vehicle))

        result = await asyncio.wait_for(task, timeout=1.0)

        self.assertEqual(result, {"response": {"result": True, "reason": ""}})


class StatelessCommandUnaffectedTests(IsolatedAsyncioTestCase):
    async def test_command_without_a_plan_never_arms_a_broadcast_watcher(self) -> None:
        # charge_port_door_open has no derivable expected end state, so it
        # must not race broadcasts at all - a broadcast arriving during its
        # wait is simply irrelevant, exactly as before this feature existed.
        vehicle = _make_vehicle(raise_unconfirmed=True)
        vehicle._actuation_timeout = 0.05

        task = asyncio.ensure_future(vehicle.charge_port_door_open())
        await asyncio.sleep(0.01)
        self.assertNotIn(
            DOMAIN, cast("dict[Any, Any]", getattr(vehicle, "_broadcast_watchers"))
        )
        vehicle._on_message(_locked_broadcast())

        with self.assertRaises(BluetoothUnconfirmedCommand):
            await asyncio.wait_for(task, timeout=1.0)


class MismatchedBroadcastTests(IsolatedAsyncioTestCase):
    async def test_prewrite_stale_mismatch_stays_unconfirmed(self) -> None:
        vehicle = _make_vehicle(raise_unconfirmed=True)
        vehicle._actuation_timeout = 0.05

        async def write_after_stale_broadcast(*_: Any) -> None:
            vehicle._on_message(_unlocked_broadcast())
            await asyncio.sleep(0)

        vehicle.client.write_gatt_char = AsyncMock(
            side_effect=write_after_stale_broadcast
        )

        with self.assertRaises(BluetoothUnconfirmedCommand):
            await asyncio.wait_for(vehicle.door_lock(), timeout=1.0)

    async def test_mismatch_standing_at_window_end_raises_command_failed(self) -> None:
        # If the whole window elapses with a mismatching broadcast as the
        # last word and nothing else confirming, that is now-final proof the
        # command did not apply - a distinct, fail-over-safe signal, not the
        # ambiguous BluetoothUnconfirmedCommand a total silence would raise.
        vehicle = _make_vehicle(raise_unconfirmed=True)
        vehicle._actuation_timeout = 0.05

        task = asyncio.ensure_future(vehicle.door_lock())
        await _wait_until_watching(vehicle, DOMAIN)
        vehicle._on_message(_unlocked_broadcast())

        with self.assertRaises(BluetoothCommandFailed):
            await asyncio.wait_for(task, timeout=1.0)

    async def test_total_silence_still_raises_unconfirmed_not_command_failed(
        self,
    ) -> None:
        # Contrast: with no broadcast at all (not even a mismatching one),
        # the outcome stays the ambiguous BluetoothUnconfirmedCommand - only
        # an actual observed mismatch upgrades to BluetoothCommandFailed.
        vehicle = _make_vehicle(raise_unconfirmed=True)
        vehicle._actuation_timeout = 0.05

        with self.assertRaises(BluetoothUnconfirmedCommand):
            await asyncio.wait_for(vehicle.door_lock(), timeout=1.0)


class SimultaneousCompletionTests(IsolatedAsyncioTestCase):
    async def test_successful_broadcast_wins_over_simultaneous_response_timeout(
        self,
    ) -> None:
        vehicle = _make_vehicle()
        broadcast_future = asyncio.get_running_loop().create_future()
        broadcast = _locked_broadcast()
        broadcast_future.set_result(broadcast)

        async def response_timeout(*_: Any) -> RoutableMessage:
            raise BluetoothTimeout()

        vehicle._await_response = response_timeout  # type: ignore[method-assign]

        result = await vehicle._await_response_or_broadcast(
            DOMAIN,
            RoutableMessage(),
            "protobuf_message_as_bytes",
            False,
            0.0,
            broadcast_future,
            None,
            [],
        )

        self.assertIs(result, broadcast)


class DefaultsAndFlagInterplayTests(IsolatedAsyncioTestCase):
    async def test_optimistic_never_arms_a_broadcast_watcher(self) -> None:
        vehicle = _make_vehicle(confirmation="optimistic")

        result = await asyncio.wait_for(vehicle.door_lock(), timeout=1.0)

        self.assertEqual(result, {"response": {"result": True, "reason": ""}})
        self.assertEqual(
            cast("dict[Any, Any]", getattr(vehicle, "_broadcast_watchers")), {}
        )

    async def test_raise_unconfirmed_false_best_effort_after_broadcast_miss(
        self,
    ) -> None:
        # raise_unconfirmed semantics are unchanged by broadcast confirmation
        # - it only makes the unconfirmed case rarer, never changes what
        # happens once the ladder is genuinely exhausted with no evidence
        # either way.
        vehicle = _make_vehicle(raise_unconfirmed=False)
        vehicle._actuation_timeout = 0.05

        task = asyncio.ensure_future(vehicle.charge_port_door_open())
        await asyncio.sleep(0.01)

        result = await asyncio.wait_for(task, timeout=1.0)

        self.assertEqual(result, {"response": {"result": True, "reason": ""}})

    async def test_verify_commands_runs_only_after_ack_and_broadcast_both_miss(
        self,
    ) -> None:
        vehicle = _make_vehicle(confirmation="verify")
        vehicle._actuation_timeout = 0.05

        task = asyncio.ensure_future(vehicle.door_lock())
        await _wait_until_watching(vehicle, DOMAIN)

        async def deliver_verify_read_reply() -> None:
            # Wait for the ack/broadcast window to elapse before answering
            # the post-timeout verify_commands read - if verify ran any
            # earlier than that, this reply would be consumed as the (wrong)
            # addressed ack for the original actuation instead. The verify
            # read waits on the addressed queue, not broadcasts.
            await asyncio.sleep(0.2)
            vehicle._on_message(
                _addressed_status_reply(
                    vehicle, VehicleLockState_E.VEHICLELOCKSTATE_LOCKED
                )
            )

        asyncio.ensure_future(deliver_verify_read_reply())

        result = await asyncio.wait_for(task, timeout=2.0)

        self.assertEqual(result, {"response": {"result": True, "reason": ""}})


class WriteFailureBroadcastRaceTests(IsolatedAsyncioTestCase):
    """A GATT write failure/timeout still lets an already-armed broadcast resolve it.

    The broadcast watcher is armed before ``write_gatt_char`` is even called,
    so a matching broadcast that arrives while (or shortly after)
    ``write_gatt_char`` raises must still confirm the command - the write
    failure doesn't prove the command never reached the vehicle.
    """

    async def test_broadcast_confirms_despite_write_failure(self) -> None:
        vehicle = _make_vehicle()
        vehicle._actuation_timeout = 5.0

        async def write_raises_then_broadcasts(*_: Any) -> None:
            vehicle._on_message(_locked_broadcast())
            await asyncio.sleep(0)
            raise BleakError("write failed")

        vehicle.client.write_gatt_char = AsyncMock(
            side_effect=write_raises_then_broadcasts
        )

        result = await asyncio.wait_for(vehicle.door_lock(), timeout=0.5)

        self.assertEqual(result, {"response": {"result": True, "reason": ""}})

    async def test_write_timeout_with_no_broadcast_raises_unconfirmed(self) -> None:
        vehicle = _make_vehicle(raise_unconfirmed=True)
        vehicle._actuation_timeout = 0.05

        vehicle.client.write_gatt_char = AsyncMock(
            side_effect=TimeoutError("write timed out")
        )

        with self.assertRaises(BluetoothUnconfirmedCommand):
            await asyncio.wait_for(vehicle.door_lock(), timeout=1.0)
