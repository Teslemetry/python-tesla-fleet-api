"""Tests for the persistent BLE broadcast listener API (``BroadcastListeners``).

Fans unsolicited VCSEC status broadcasts out to typed per-field listeners
plus a generic per-domain listener, reusing the exact same ``_on_message``
routing path as the one-shot confirmation-ladder watcher - no second
notification subscription. Broadcasts are injected directly via
``vehicle._on_message``, matching ``test_ble_broadcast_confirmation.py``.
"""

from __future__ import annotations

import asyncio
from typing import Any, cast
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, MagicMock

from cryptography.hazmat.primitives.asymmetric import ec

from tesla_fleet_api.exceptions import BluetoothTimeout
from tesla_fleet_api.tesla.vehicle.bluetooth import VehicleBluetooth
from tesla_protocol.command.universal_message_pb2 import (
    Destination,
    Domain,
    RoutableMessage,
)
from tesla_protocol.command.vcsec_pb2 import (
    ClosureState_E,
    ClosureStatuses,
    CommandStatus,
    DetailedClosureStatus,
    FromVCSECMessage,
    Gear_E,
    OperationStatus_E,
    UIDesire_E,
    UserPresence_E,
    VehicleLockState_E,
    VehicleSleepStatus_E,
    VehicleStatus,
)

VIN = "5YJXCAE43LF123456"
DOMAIN = Domain.DOMAIN_VEHICLE_SECURITY


def _make_vehicle(**kwargs: Any) -> VehicleBluetooth[Any]:
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


def _status_broadcast(status: VehicleStatus) -> RoutableMessage:
    """An unsolicited (unaddressed) VCSEC status broadcast."""
    body = FromVCSECMessage(vehicleStatus=status)
    return RoutableMessage(
        from_destination=Destination(domain=DOMAIN),
        protobuf_message_as_bytes=body.SerializeToString(),
    )


def _command_status_broadcast() -> RoutableMessage:
    """A non-``VehicleStatus`` VCSEC broadcast.

    ``_decode_vcsec_status`` only decodes the ``vehicleStatus`` oneof member,
    so this is invisible to every typed listener - exactly the "rest" the
    generic listener exists for.
    """
    body = FromVCSECMessage(
        commandStatus=CommandStatus(
            operationStatus=OperationStatus_E.OPERATIONSTATUS_OK
        )
    )
    return RoutableMessage(
        from_destination=Destination(domain=DOMAIN),
        protobuf_message_as_bytes=body.SerializeToString(),
    )


def _addressed_status(
    vehicle: VehicleBluetooth[Any], status: VehicleStatus
) -> RoutableMessage:
    """An addressed (non-broadcast) VCSEC status reply - must not reach listeners."""
    body = FromVCSECMessage(vehicleStatus=status)
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
    """Block until the one-shot confirmation ladder has armed its watcher."""

    async def poll() -> None:
        while domain not in vehicle._broadcast_watchers:
            await asyncio.sleep(0)

    await asyncio.wait_for(poll(), timeout=timeout)


class TypedFieldListenerTests(IsolatedAsyncioTestCase):
    async def test_lock_state_listener_fires_with_typed_value(self) -> None:
        vehicle = _make_vehicle()
        seen: list[Any] = []
        vehicle.listen_vehicle_lock_state(seen.append)

        vehicle._on_message(
            _status_broadcast(
                VehicleStatus(
                    vehicleLockState=VehicleLockState_E.VEHICLELOCKSTATE_LOCKED
                )
            )
        )

        self.assertEqual(seen, [VehicleLockState_E.VEHICLELOCKSTATE_LOCKED])

    async def test_sleep_status_listener_fires(self) -> None:
        vehicle = _make_vehicle()
        seen: list[Any] = []
        vehicle.listen_vehicle_sleep_status(seen.append)

        vehicle._on_message(
            _status_broadcast(
                VehicleStatus(
                    vehicleSleepStatus=VehicleSleepStatus_E.VEHICLE_SLEEP_STATUS_ASLEEP
                )
            )
        )

        self.assertEqual(seen, [VehicleSleepStatus_E.VEHICLE_SLEEP_STATUS_ASLEEP])

    async def test_user_presence_listener_fires(self) -> None:
        vehicle = _make_vehicle()
        seen: list[Any] = []
        vehicle.listen_user_presence(seen.append)

        vehicle._on_message(
            _status_broadcast(
                VehicleStatus(userPresence=UserPresence_E.VEHICLE_USER_PRESENCE_PRESENT)
            )
        )

        self.assertEqual(seen, [UserPresence_E.VEHICLE_USER_PRESENCE_PRESENT])

    async def test_multiple_field_listeners_fire_from_one_broadcast(self) -> None:
        vehicle = _make_vehicle()
        lock_seen: list[Any] = []
        presence_seen: list[Any] = []
        vehicle.listen_vehicle_lock_state(lock_seen.append)
        vehicle.listen_user_presence(presence_seen.append)

        vehicle._on_message(
            _status_broadcast(
                VehicleStatus(
                    vehicleLockState=VehicleLockState_E.VEHICLELOCKSTATE_UNLOCKED,
                    userPresence=UserPresence_E.VEHICLE_USER_PRESENCE_PRESENT,
                )
            )
        )

        self.assertEqual(lock_seen, [VehicleLockState_E.VEHICLELOCKSTATE_UNLOCKED])
        self.assertEqual(presence_seen, [UserPresence_E.VEHICLE_USER_PRESENCE_PRESENT])

    async def test_gear_listener_fires_with_typed_value(self) -> None:
        vehicle = _make_vehicle()
        seen: list[Any] = []
        vehicle.listen_gear(seen.append)

        vehicle._on_message(_status_broadcast(VehicleStatus(gear=Gear_E.GEAR_DRIVE)))

        self.assertEqual(seen, [Gear_E.GEAR_DRIVE])

    async def test_gear_listener_fires_with_default_when_absent(self) -> None:
        # gear is a scalar proto3 field, so it has no HasField presence -
        # a broadcast that never sets it still fires with the 0 default.
        vehicle = _make_vehicle()
        seen: list[Any] = []
        vehicle.listen_gear(seen.append)

        vehicle._on_message(
            _status_broadcast(
                VehicleStatus(
                    vehicleLockState=VehicleLockState_E.VEHICLELOCKSTATE_LOCKED
                )
            )
        )

        self.assertEqual(seen, [Gear_E.GEAR_UNKNOWN])

    async def test_ui_desire_listener_fires_with_typed_value(self) -> None:
        vehicle = _make_vehicle()
        seen: list[Any] = []
        vehicle.listen_ui_desire(seen.append)

        vehicle._on_message(
            _status_broadcast(VehicleStatus(uiDesire=UIDesire_E.UI_DESIRE_HAS_DATA))
        )

        self.assertEqual(seen, [UIDesire_E.UI_DESIRE_HAS_DATA])

    async def test_ui_desire_listener_fires_with_default_when_absent(self) -> None:
        # uiDesire is a scalar proto3 field, so it has no HasField presence -
        # a broadcast that never sets it still fires with the 0 default.
        vehicle = _make_vehicle()
        seen: list[Any] = []
        vehicle.listen_ui_desire(seen.append)

        vehicle._on_message(
            _status_broadcast(
                VehicleStatus(
                    vehicleLockState=VehicleLockState_E.VEHICLELOCKSTATE_LOCKED
                )
            )
        )

        self.assertEqual(seen, [UIDesire_E.UI_DESIRE_NONE])


class ClosureListenerTests(IsolatedAsyncioTestCase):
    async def test_all_eight_closure_listeners_read_their_own_field(self) -> None:
        vehicle = _make_vehicle()
        results: dict[str, Any] = {}
        for name in [
            "front_driver_door",
            "front_passenger_door",
            "rear_driver_door",
            "rear_passenger_door",
            "front_trunk",
            "rear_trunk",
            "charge_port",
            "tonneau",
        ]:
            listener = getattr(vehicle, f"listen_{name}")
            listener(lambda value, name=name: results.__setitem__(name, value))

        status = VehicleStatus(
            closureStatuses=ClosureStatuses(
                frontDriverDoor=ClosureState_E.CLOSURESTATE_OPEN,
                frontPassengerDoor=ClosureState_E.CLOSURESTATE_AJAR,
                rearDriverDoor=ClosureState_E.CLOSURESTATE_CLOSED,
                rearPassengerDoor=ClosureState_E.CLOSURESTATE_CLOSING,
                frontTrunk=ClosureState_E.CLOSURESTATE_OPENING,
                rearTrunk=ClosureState_E.CLOSURESTATE_FAILED_UNLATCH,
                chargePort=ClosureState_E.CLOSURESTATE_OPEN,
                tonneau=ClosureState_E.CLOSURESTATE_UNKNOWN,
            )
        )
        vehicle._on_message(_status_broadcast(status))

        self.assertEqual(results["front_driver_door"], ClosureState_E.CLOSURESTATE_OPEN)
        self.assertEqual(
            results["front_passenger_door"], ClosureState_E.CLOSURESTATE_AJAR
        )
        self.assertEqual(
            results["rear_driver_door"], ClosureState_E.CLOSURESTATE_CLOSED
        )
        self.assertEqual(
            results["rear_passenger_door"], ClosureState_E.CLOSURESTATE_CLOSING
        )
        self.assertEqual(results["front_trunk"], ClosureState_E.CLOSURESTATE_OPENING)
        self.assertEqual(
            results["rear_trunk"], ClosureState_E.CLOSURESTATE_FAILED_UNLATCH
        )
        self.assertEqual(results["charge_port"], ClosureState_E.CLOSURESTATE_OPEN)
        self.assertEqual(results["tonneau"], ClosureState_E.CLOSURESTATE_UNKNOWN)

    async def test_closure_listener_does_not_fire_without_closure_statuses(
        self,
    ) -> None:
        vehicle = _make_vehicle()
        seen: list[Any] = []
        vehicle.listen_front_driver_door(seen.append)

        # A status broadcast that carries only vehicleLockState has no
        # closureStatuses submessage - proto3 tracks presence for it.
        vehicle._on_message(
            _status_broadcast(
                VehicleStatus(
                    vehicleLockState=VehicleLockState_E.VEHICLELOCKSTATE_LOCKED
                )
            )
        )

        self.assertEqual(seen, [])


class TonneauPercentOpenTests(IsolatedAsyncioTestCase):
    async def test_fires_when_detailed_closure_status_present(self) -> None:
        vehicle = _make_vehicle()
        seen: list[int] = []
        vehicle.listen_tonneau_percent_open(seen.append)

        status = VehicleStatus(
            detailedClosureStatus=DetailedClosureStatus(tonneauPercentOpen=42)
        )
        vehicle._on_message(_status_broadcast(status))

        self.assertEqual(seen, [42])

    async def test_does_not_fire_without_detailed_closure_status(self) -> None:
        vehicle = _make_vehicle()
        seen: list[int] = []
        vehicle.listen_tonneau_percent_open(seen.append)

        vehicle._on_message(
            _status_broadcast(
                VehicleStatus(
                    vehicleLockState=VehicleLockState_E.VEHICLELOCKSTATE_LOCKED
                )
            )
        )

        self.assertEqual(seen, [])


class UnsubscribeTests(IsolatedAsyncioTestCase):
    async def test_unsubscribe_stops_delivery(self) -> None:
        vehicle = _make_vehicle()
        seen: list[Any] = []
        unsubscribe = vehicle.listen_vehicle_lock_state(seen.append)

        vehicle._on_message(
            _status_broadcast(
                VehicleStatus(
                    vehicleLockState=VehicleLockState_E.VEHICLELOCKSTATE_LOCKED
                )
            )
        )
        unsubscribe()
        vehicle._on_message(
            _status_broadcast(
                VehicleStatus(
                    vehicleLockState=VehicleLockState_E.VEHICLELOCKSTATE_UNLOCKED
                )
            )
        )

        self.assertEqual(seen, [VehicleLockState_E.VEHICLELOCKSTATE_LOCKED])

    async def test_double_unsubscribe_is_a_no_op(self) -> None:
        vehicle = _make_vehicle()
        unsubscribe = vehicle.listen_vehicle_lock_state(lambda _: None)
        unsubscribe()
        unsubscribe()  # must not raise

    async def test_unsubscribe_only_removes_its_own_listener(self) -> None:
        vehicle = _make_vehicle()
        seen_a: list[Any] = []
        seen_b: list[Any] = []
        unsubscribe_a = vehicle.listen_vehicle_lock_state(seen_a.append)
        vehicle.listen_vehicle_lock_state(seen_b.append)

        unsubscribe_a()
        vehicle._on_message(
            _status_broadcast(
                VehicleStatus(
                    vehicleLockState=VehicleLockState_E.VEHICLELOCKSTATE_LOCKED
                )
            )
        )

        self.assertEqual(seen_a, [])
        self.assertEqual(seen_b, [VehicleLockState_E.VEHICLELOCKSTATE_LOCKED])


class GenericBroadcastListenerTests(IsolatedAsyncioTestCase):
    async def test_generic_listener_receives_raw_message(self) -> None:
        vehicle = _make_vehicle()
        seen: list[RoutableMessage] = []
        vehicle.listen_broadcast(DOMAIN, seen.append)

        msg = _status_broadcast(
            VehicleStatus(vehicleLockState=VehicleLockState_E.VEHICLELOCKSTATE_LOCKED)
        )
        vehicle._on_message(msg)

        self.assertEqual(seen, [msg])

    async def test_generic_listener_covers_non_vehicle_status_payloads(self) -> None:
        vehicle = _make_vehicle()
        typed_seen: list[Any] = []
        raw_seen: list[RoutableMessage] = []
        vehicle.listen_vehicle_lock_state(typed_seen.append)
        vehicle.listen_broadcast(DOMAIN, raw_seen.append)

        vehicle._on_message(_command_status_broadcast())

        self.assertEqual(typed_seen, [])
        self.assertEqual(len(raw_seen), 1)

    async def test_generic_listener_scoped_to_its_domain(self) -> None:
        vehicle = _make_vehicle()
        seen: list[RoutableMessage] = []
        vehicle.listen_broadcast(Domain.DOMAIN_INFOTAINMENT, seen.append)

        vehicle._on_message(
            _status_broadcast(
                VehicleStatus(
                    vehicleLockState=VehicleLockState_E.VEHICLELOCKSTATE_LOCKED
                )
            )
        )

        self.assertEqual(seen, [])


class ListenerExceptionIsolationTests(IsolatedAsyncioTestCase):
    async def test_failing_generic_listener_does_not_block_later_listeners(
        self,
    ) -> None:
        vehicle = _make_vehicle()
        seen: list[RoutableMessage] = []

        def fail(_: RoutableMessage) -> None:
            raise RuntimeError("listener failed")

        vehicle.listen_broadcast(DOMAIN, fail)
        vehicle.listen_broadcast(DOMAIN, seen.append)

        msg = _status_broadcast(
            VehicleStatus(vehicleLockState=VehicleLockState_E.VEHICLELOCKSTATE_LOCKED)
        )
        vehicle._on_message(msg)

        self.assertEqual(seen, [msg])

    async def test_failing_typed_listener_does_not_block_later_listeners(self) -> None:
        vehicle = _make_vehicle()
        seen: list[Any] = []

        def fail(_: VehicleLockState_E) -> None:
            raise BluetoothTimeout()

        vehicle.listen_vehicle_lock_state(fail)
        vehicle.listen_vehicle_lock_state(seen.append)

        vehicle._on_message(
            _status_broadcast(
                VehicleStatus(
                    vehicleLockState=VehicleLockState_E.VEHICLELOCKSTATE_LOCKED
                )
            )
        )

        self.assertEqual(seen, [VehicleLockState_E.VEHICLELOCKSTATE_LOCKED])

    async def test_failing_listener_does_not_block_later_addressed_reply(
        self,
    ) -> None:
        vehicle = _make_vehicle()

        def fail(_: VehicleLockState_E) -> None:
            raise RuntimeError("listener failed")

        vehicle.listen_vehicle_lock_state(fail)
        vehicle._on_message(
            _status_broadcast(
                VehicleStatus(
                    vehicleLockState=VehicleLockState_E.VEHICLELOCKSTATE_LOCKED
                )
            )
        )

        reply = _addressed_status(
            vehicle,
            VehicleStatus(
                vehicleLockState=VehicleLockState_E.VEHICLELOCKSTATE_UNLOCKED
            ),
        )
        vehicle._on_message(reply)

        self.assertIs(vehicle._queues[DOMAIN].get_nowait(), reply)


class AddressedMessagesNeverReachListenersTests(IsolatedAsyncioTestCase):
    async def test_addressed_reply_does_not_fire_listeners(self) -> None:
        vehicle = _make_vehicle()
        typed_seen: list[Any] = []
        raw_seen: list[RoutableMessage] = []
        vehicle.listen_vehicle_lock_state(typed_seen.append)
        vehicle.listen_broadcast(DOMAIN, raw_seen.append)

        vehicle._on_message(
            _addressed_status(
                vehicle,
                VehicleStatus(
                    vehicleLockState=VehicleLockState_E.VEHICLELOCKSTATE_LOCKED
                ),
            )
        )

        self.assertEqual(typed_seen, [])
        self.assertEqual(raw_seen, [])


class CoexistsWithConfirmationLadderTests(IsolatedAsyncioTestCase):
    async def test_persistent_listener_fires_alongside_one_shot_watcher(self) -> None:
        """A broadcast resolving an in-flight command's confirmation ladder
        must still reach a persistent listener registered separately - the
        two mechanisms share ``_on_message`` but must not clobber each other.
        """
        vehicle = _make_vehicle()
        vehicle._actuation_timeout = 5.0
        seen: list[Any] = []
        vehicle.listen_vehicle_lock_state(seen.append)

        task = asyncio.ensure_future(vehicle.door_lock())
        await _wait_until_watching(vehicle, DOMAIN)
        vehicle._on_message(
            _status_broadcast(
                VehicleStatus(
                    vehicleLockState=VehicleLockState_E.VEHICLELOCKSTATE_LOCKED
                )
            )
        )

        result = await asyncio.wait_for(task, timeout=1.0)

        self.assertEqual(result, {"response": {"result": True, "reason": ""}})
        self.assertEqual(seen, [VehicleLockState_E.VEHICLELOCKSTATE_LOCKED])


class ListenerLifecycleTests(IsolatedAsyncioTestCase):
    async def test_listeners_survive_disconnect(self) -> None:
        vehicle = _make_vehicle()
        vehicle.client.disconnect = AsyncMock()
        seen: list[Any] = []
        vehicle.listen_vehicle_lock_state(seen.append)

        await vehicle.disconnect()
        vehicle._on_message(
            _status_broadcast(
                VehicleStatus(
                    vehicleLockState=VehicleLockState_E.VEHICLELOCKSTATE_LOCKED
                )
            )
        )

        self.assertEqual(seen, [VehicleLockState_E.VEHICLELOCKSTATE_LOCKED])

    async def test_registries_are_not_shared_across_vehicle_instances(self) -> None:
        vehicle_a = _make_vehicle()
        vehicle_b = _make_vehicle()
        seen_a: list[Any] = []
        vehicle_a.listen_vehicle_lock_state(seen_a.append)

        vehicle_b._on_message(
            _status_broadcast(
                VehicleStatus(
                    vehicleLockState=VehicleLockState_E.VEHICLELOCKSTATE_LOCKED
                )
            )
        )

        self.assertEqual(seen_a, [])
