"""Tests for BleBroadcastPublisher over a real VehicleBluetooth's listener seams.

Broadcasts are injected through ``vehicle._on_message``, the same routing path
the vehicle uses in production, so the publisher is exercised against the real
``BroadcastListeners`` registries rather than a stand-in. No BLE connection,
GATT traffic, or event loop is involved.
"""

from __future__ import annotations

from typing import Any
from unittest import TestCase
from unittest.mock import AsyncMock, MagicMock

from cryptography.hazmat.primitives.asymmetric import ec

from tesla_fleet_api.funnel import (
    BleBroadcastPublisher,
    FieldPath,
    Observation,
    ObservationFunnel,
    Value,
    VehicleDataResultPublisher,
)
from tesla_fleet_api.tesla.vehicle.bluetooth import VehicleBluetooth
from tesla_protocol.command.universal_message_pb2 import (
    Destination,
    Domain,
    RoutableMessage,
)
from tesla_protocol.command.vcsec_pb2 import (
    ClosureState_E,
    ClosureStatuses,
    FromVCSECMessage,
    VehicleLockState_E,
    VehicleStatus,
)

VIN = "5YJXCAE43LF123456"
DOMAIN = Domain.DOMAIN_VEHICLE_SECURITY


class _Clock:
    def __init__(self, now: float = 0.0) -> None:
        self.now = now

    def __call__(self) -> float:
        return self.now


def _make_vehicle(*, connected: bool = True) -> VehicleBluetooth[Any]:
    parent = MagicMock()
    parent.private_key = ec.generate_private_key(ec.SECP256R1())
    vehicle = VehicleBluetooth(parent, VIN)
    vehicle.connect_if_needed = AsyncMock()  # type: ignore[method-assign]
    vehicle.connect = AsyncMock()  # type: ignore[method-assign]
    vehicle.client = MagicMock()
    vehicle.client.is_connected = connected
    vehicle.client.write_gatt_char = AsyncMock()
    return vehicle


def _broadcast(status: VehicleStatus) -> RoutableMessage:
    """An unsolicited (unaddressed) VCSEC status broadcast."""
    return RoutableMessage(
        from_destination=Destination(domain=DOMAIN),
        protobuf_message_as_bytes=FromVCSECMessage(
            vehicleStatus=status
        ).SerializeToString(),
    )


def _lock(state: VehicleLockState_E) -> RoutableMessage:
    return _broadcast(VehicleStatus(vehicleLockState=state))


def _closures(**kwargs: ClosureState_E) -> RoutableMessage:
    return _broadcast(VehicleStatus(closureStatuses=ClosureStatuses(**kwargs)))


CLOSURE_PATHS = frozenset(
    {FieldPath.CHARGE_PORT_DOOR_OPEN, FieldPath.DOOR_STATE_TRUNK_FRONT}
)


class _Sink:
    """Collects observations straight off the publisher."""

    def __init__(self) -> None:
        self.observations: list[Observation] = []

    def publish(self, observation: Observation) -> None:
        self.observations.append(observation)


def _attached(
    vehicle: VehicleBluetooth[Any], *, paths: frozenset[FieldPath] | None = None
) -> tuple[BleBroadcastPublisher, _Sink]:
    publisher = BleBroadcastPublisher(vehicle, clock=_Clock())
    sink = _Sink()
    publisher.attach(sink)
    publisher.request(frozenset(FieldPath) if paths is None else paths)
    return publisher, sink


class TestBroadcastTranslation(TestCase):
    def test_ordinary_lock_states_map_to_booleans(self) -> None:
        vehicle = _make_vehicle()
        _, sink = _attached(vehicle)

        vehicle._on_message(_lock(VehicleLockState_E.VEHICLELOCKSTATE_LOCKED))
        vehicle._on_message(_lock(VehicleLockState_E.VEHICLELOCKSTATE_UNLOCKED))

        self.assertEqual(
            [(o.path, o.value) for o in sink.observations],
            [(FieldPath.LOCKED, True), (FieldPath.LOCKED, False)],
        )

    def test_unvalidated_lock_states_emit_no_observation(self) -> None:
        """An unmapped enum keeps the last confirmed value instead of guessing."""
        vehicle = _make_vehicle()
        _, sink = _attached(vehicle)

        vehicle._on_message(_lock(VehicleLockState_E.VEHICLELOCKSTATE_INTERNAL_LOCKED))
        vehicle._on_message(
            _lock(VehicleLockState_E.VEHICLELOCKSTATE_SELECTIVE_UNLOCKED)
        )

        self.assertEqual(sink.observations, [])

    def test_closure_states_map_to_booleans(self) -> None:
        vehicle = _make_vehicle()
        _, sink = _attached(vehicle, paths=CLOSURE_PATHS)

        for state, expected in (
            (ClosureState_E.CLOSURESTATE_CLOSED, False),
            (ClosureState_E.CLOSURESTATE_OPEN, True),
            (ClosureState_E.CLOSURESTATE_AJAR, True),
            (ClosureState_E.CLOSURESTATE_OPENING, True),
            (ClosureState_E.CLOSURESTATE_CLOSING, True),
        ):
            sink.observations.clear()
            vehicle._on_message(_closures(chargePort=state, frontTrunk=state))
            self.assertEqual(
                {(o.path, o.value) for o in sink.observations},
                {
                    (FieldPath.CHARGE_PORT_DOOR_OPEN, expected),
                    (FieldPath.DOOR_STATE_TRUNK_FRONT, expected),
                },
                msg=f"closure state {state}",
            )

    def test_ambiguous_closure_states_emit_no_observation(self) -> None:
        vehicle = _make_vehicle()
        _, sink = _attached(vehicle, paths=CLOSURE_PATHS)

        for state in (
            ClosureState_E.CLOSURESTATE_UNKNOWN,
            ClosureState_E.CLOSURESTATE_FAILED_UNLATCH,
        ):
            vehicle._on_message(_closures(chargePort=state, frontTrunk=state))

        self.assertEqual(sink.observations, [])

    def test_a_broadcast_without_closures_emits_no_closure_observation(self) -> None:
        """Closures have proto3 presence, so an absent submessage says nothing."""
        vehicle = _make_vehicle()
        _, sink = _attached(vehicle, paths=CLOSURE_PATHS)

        vehicle._on_message(_lock(VehicleLockState_E.VEHICLELOCKSTATE_LOCKED))

        self.assertEqual(sink.observations, [])

    def test_every_status_broadcast_carries_a_lock_state(self) -> None:
        """UNLOCKED is 0 with no presence, so the funnel dedupes the repeats."""
        vehicle = _make_vehicle()
        funnel = ObservationFunnel()
        publisher = BleBroadcastPublisher(vehicle, clock=_Clock(1.0))
        funnel.attach(publisher)

        seen: list[Value] = []
        funnel.listen(FieldPath.LOCKED, seen.append)

        # A closure-only broadcast still reports vehicleLockState = UNLOCKED.
        vehicle._on_message(_closures(frontTrunk=ClosureState_E.CLOSURESTATE_CLOSED))
        vehicle._on_message(_closures(frontTrunk=ClosureState_E.CLOSURESTATE_OPEN))

        self.assertEqual(seen, [False])


class TestBroadcastActivation(TestCase):
    def test_request_and_release_bracket_the_ble_listener(self) -> None:
        vehicle = _make_vehicle()
        publisher, sink = _attached(vehicle, paths=frozenset({FieldPath.LOCKED}))

        vehicle._on_message(_lock(VehicleLockState_E.VEHICLELOCKSTATE_LOCKED))
        self.assertEqual(len(sink.observations), 1)

        publisher.release(frozenset({FieldPath.LOCKED}))
        vehicle._on_message(_lock(VehicleLockState_E.VEHICLELOCKSTATE_UNLOCKED))
        self.assertEqual(len(sink.observations), 1)

    def test_only_requested_paths_are_subscribed(self) -> None:
        vehicle = _make_vehicle()
        _, sink = _attached(vehicle, paths=frozenset({FieldPath.LOCKED}))

        vehicle._on_message(
            _closures(
                chargePort=ClosureState_E.CLOSURESTATE_OPEN,
                frontTrunk=ClosureState_E.CLOSURESTATE_OPEN,
            )
        )

        self.assertEqual([o.path for o in sink.observations], [FieldPath.LOCKED])

    def test_detach_drops_every_subscription(self) -> None:
        vehicle = _make_vehicle()
        publisher = BleBroadcastPublisher(vehicle, clock=_Clock())
        sink = _Sink()
        detach = publisher.attach(sink)
        publisher.request(frozenset(FieldPath))

        detach()
        vehicle._on_message(_lock(VehicleLockState_E.VEHICLELOCKSTATE_LOCKED))

        self.assertEqual(sink.observations, [])

    def test_the_publisher_never_drives_the_transport(self) -> None:
        vehicle = _make_vehicle()
        publisher, _ = _attached(vehicle)
        publisher.release(frozenset(FieldPath))

        vehicle.connect.assert_not_awaited()  # type: ignore[attr-defined]
        vehicle.connect_if_needed.assert_not_awaited()  # type: ignore[attr-defined]
        vehicle.client.write_gatt_char.assert_not_awaited()

    def test_a_lost_session_publishes_nothing(self) -> None:
        """A dropped link ends the broadcasts; it is not a reading of the field."""
        vehicle = _make_vehicle()
        funnel = ObservationFunnel()
        detach = funnel.attach(BleBroadcastPublisher(vehicle, clock=_Clock(1.0)))

        seen: list[Value] = []
        funnel.listen(FieldPath.LOCKED, seen.append)
        vehicle._on_message(_lock(VehicleLockState_E.VEHICLELOCKSTATE_LOCKED))

        vehicle.client.is_connected = False
        detach()

        self.assertEqual(seen, [True])
        self.assertIs(funnel.value(FieldPath.LOCKED), True)


class TestRegressionWalkthrough(TestCase):
    """The reported failure: lock, charge port and front trunk go unavailable.

    Firmware routed the three fields to Bluetooth broadcasts. With Bluetooth
    unreachable they had no other source, so the entities blanked. Here the
    same funnel is fed by both a supplied ``vehicle_data`` result and BLE
    broadcasts, and each field keeps a value whichever source is producing.
    """

    def _compose(
        self,
    ) -> tuple[
        ObservationFunnel,
        VehicleBluetooth[Any],
        VehicleDataResultPublisher,
        dict[FieldPath, list[Value]],
    ]:
        vehicle = _make_vehicle()
        funnel = ObservationFunnel()
        funnel.attach(BleBroadcastPublisher(vehicle, clock=_Clock(100.0)))
        result_publisher = VehicleDataResultPublisher(clock=_Clock(0.0))
        funnel.attach(result_publisher)

        seen: dict[FieldPath, list[Value]] = {path: [] for path in FieldPath}
        for path in FieldPath:
            funnel.listen(path, seen[path].append)
        return funnel, vehicle, result_publisher, seen

    def test_unreachable_bluetooth_does_not_blank_the_three_fields(self) -> None:
        funnel, _, result_publisher, seen = self._compose()

        # Bluetooth never connects, so it broadcasts nothing at all.
        result_publisher.publish_result(
            {
                "response": {
                    "vehicle_state": {"locked": True, "ft": 0},
                    "charge_state": {"charge_port_door_open": False},
                }
            },
            observed_at=1.0,
        )

        self.assertEqual(
            seen,
            {
                FieldPath.LOCKED: [True],
                FieldPath.CHARGE_PORT_DOOR_OPEN: [False],
                FieldPath.DOOR_STATE_TRUNK_FRONT: [False],
            },
        )
        for path in FieldPath:
            self.assertIsNotNone(funnel.value(path))

    def test_bluetooth_recovering_updates_the_same_listeners(self) -> None:
        funnel, vehicle, result_publisher, seen = self._compose()
        result_publisher.publish_result(
            {
                "response": {
                    "vehicle_state": {"locked": True, "ft": 0},
                    "charge_state": {"charge_port_door_open": False},
                }
            },
            observed_at=1.0,
        )

        # Bluetooth comes up and the vehicle is opened up.
        vehicle._on_message(_lock(VehicleLockState_E.VEHICLELOCKSTATE_UNLOCKED))
        vehicle._on_message(
            _closures(
                chargePort=ClosureState_E.CLOSURESTATE_OPEN,
                frontTrunk=ClosureState_E.CLOSURESTATE_OPEN,
            )
        )

        self.assertEqual(seen[FieldPath.LOCKED], [True, False])
        self.assertEqual(seen[FieldPath.CHARGE_PORT_DOOR_OPEN], [False, True])
        self.assertEqual(seen[FieldPath.DOOR_STATE_TRUNK_FRONT], [False, True])
        for values in seen.values():
            self.assertNotIn(None, values)
