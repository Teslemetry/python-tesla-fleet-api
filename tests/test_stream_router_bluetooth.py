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

from tesla_fleet_api.router import (
    BleBroadcastPublisher,
    FieldPath,
    Observation,
    StreamRouter,
)
from tesla_fleet_api.router.stream import PRIORITY_BROADCAST, PRIORITY_STREAM
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
    """Collects observations and health straight off the publisher."""

    def __init__(self) -> None:
        self.observations: list[Observation] = []
        self.health: list[tuple[str, bool]] = []

    def publish(self, observation: Observation) -> None:
        self.observations.append(observation)

    def set_health(self, source_id: str, healthy: bool) -> None:
        self.health.append((source_id, healthy))


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
        """proto3 tracks presence for the submessage, so absence is not CLOSED."""
        vehicle = _make_vehicle()
        _, sink = _attached(vehicle)

        vehicle._on_message(_lock(VehicleLockState_E.VEHICLELOCKSTATE_LOCKED))

        self.assertEqual([o.path for o in sink.observations], [FieldPath.LOCKED])

    def test_every_status_broadcast_carries_a_lock_state(self) -> None:
        """UNLOCKED is 0, so the wire cannot distinguish it from an absent field.

        A closure-only broadcast therefore still reports the lock state, and
        the router deduplicates the repeat rather than the publisher guessing.
        """
        vehicle = _make_vehicle()
        _, sink = _attached(vehicle, paths=frozenset({FieldPath.LOCKED}))

        vehicle._on_message(_closures(chargePort=ClosureState_E.CLOSURESTATE_OPEN))

        self.assertEqual(
            [(o.path, o.value) for o in sink.observations],
            [(FieldPath.LOCKED, False)],
        )


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
        _, sink = _attached(vehicle, paths=frozenset({FieldPath.CHARGE_PORT_DOOR_OPEN}))

        vehicle._on_message(
            _closures(
                chargePort=ClosureState_E.CLOSURESTATE_OPEN,
                frontTrunk=ClosureState_E.CLOSURESTATE_OPEN,
            )
        )
        self.assertEqual(
            [(o.path, o.value) for o in sink.observations],
            [(FieldPath.CHARGE_PORT_DOOR_OPEN, True)],
        )

    def test_detach_drops_every_subscription(self) -> None:
        vehicle = _make_vehicle()
        publisher = BleBroadcastPublisher(vehicle, clock=_Clock())
        sink = _Sink()
        detach = publisher.attach(sink)
        publisher.request(frozenset(FieldPath))
        detach()

        vehicle._on_message(_lock(VehicleLockState_E.VEHICLELOCKSTATE_LOCKED))
        self.assertEqual(sink.observations, [])

    def test_health_follows_the_existing_connection_status_seam(self) -> None:
        vehicle = _make_vehicle(connected=False)
        publisher = BleBroadcastPublisher(vehicle, clock=_Clock())
        sink = _Sink()
        publisher.attach(sink)
        self.assertEqual(sink.health, [("ble-broadcast", False)])

        vehicle._set_connected(True)
        vehicle._set_connected(False)
        self.assertEqual(
            sink.health,
            [
                ("ble-broadcast", False),
                ("ble-broadcast", True),
                ("ble-broadcast", False),
            ],
        )

    def test_a_session_already_up_at_attach_is_reported_healthy(self) -> None:
        """listen_connection_status only fires on transitions."""
        vehicle = _make_vehicle(connected=True)
        publisher = BleBroadcastPublisher(vehicle, clock=_Clock())
        sink = _Sink()
        publisher.attach(sink)
        self.assertEqual(sink.health, [("ble-broadcast", True)])

    def test_the_publisher_never_drives_the_transport(self) -> None:
        vehicle = _make_vehicle()
        publisher, _ = _attached(vehicle)
        vehicle._on_message(_lock(VehicleLockState_E.VEHICLELOCKSTATE_LOCKED))
        publisher.release(frozenset(FieldPath))

        vehicle.connect.assert_not_awaited()  # type: ignore[attr-defined]
        vehicle.connect_if_needed.assert_not_awaited()  # type: ignore[attr-defined]
        vehicle.client.write_gatt_char.assert_not_awaited()


class TestRegressionWalkthrough(TestCase):
    """The captain's 6.1.1 failure: Bluetooth cannot connect, the stream can.

    Charge port, front trunk and lock must stay available with real values
    rather than going unavailable because a source they were bound to is down.
    """

    def _router_with_stream_and_ble(
        self, vehicle: VehicleBluetooth[Any], clock: _Clock
    ) -> tuple[StreamRouter, _StubStreamPublisher]:
        router = StreamRouter(clock=clock)
        stream = _StubStreamPublisher(clock)
        router.attach(stream)
        router.attach(
            BleBroadcastPublisher(vehicle, priority=PRIORITY_BROADCAST, clock=clock)
        )
        return router, stream

    def test_unavailable_bluetooth_does_not_blank_streamed_fields(self) -> None:
        clock = _Clock()
        vehicle = _make_vehicle(connected=False)
        router, stream = self._router_with_stream_and_ble(vehicle, clock)

        seen: dict[FieldPath, list[Any]] = {p: [] for p in FieldPath}
        for path in FieldPath:
            router.listen(path, seen[path].append)

        stream.emit(FieldPath.CHARGE_PORT_DOOR_OPEN, False)
        stream.emit(FieldPath.DOOR_STATE_TRUNK_FRONT, False)
        stream.emit(FieldPath.LOCKED, True)

        self.assertEqual(seen[FieldPath.CHARGE_PORT_DOOR_OPEN], [False])
        self.assertEqual(seen[FieldPath.DOOR_STATE_TRUNK_FRONT], [False])
        self.assertEqual(seen[FieldPath.LOCKED], [True])
        for path in FieldPath:
            self.assertTrue(router.is_available(path), msg=str(path))
            self.assertNotIn(None, seen[path])

    def test_ble_takes_over_when_the_stream_drops_then_hands_back(self) -> None:
        clock = _Clock()
        vehicle = _make_vehicle(connected=True)
        router, stream = self._router_with_stream_and_ble(vehicle, clock)

        seen: list[Any] = []
        available: list[Any] = []
        router.listen(FieldPath.LOCKED, seen.append)
        router.listen_availability(FieldPath.LOCKED, available.append)

        stream.emit(FieldPath.LOCKED, True)
        vehicle._on_message(_lock(VehicleLockState_E.VEHICLELOCKSTATE_LOCKED))
        self.assertEqual(seen, [True])

        clock.now = 10.0
        stream.set_health(False)
        vehicle._on_message(_lock(VehicleLockState_E.VEHICLELOCKSTATE_UNLOCKED))
        self.assertEqual(seen, [True, False])

        # The stream must hold health for the failback delay before it takes
        # the field back off a working Bluetooth session.
        clock.now = 100.0
        stream.set_health(True)
        stream.emit(FieldPath.LOCKED, True)
        self.assertEqual(seen, [True, False])

        clock.now = 200.0
        stream.emit(FieldPath.LOCKED, True)
        self.assertEqual(seen, [True, False, True])

        self.assertNotIn(None, seen)
        self.assertEqual(available, [False, True])


class _StubStreamPublisher:
    """Stands in for the stream library's SSE adapter, which is a later slice."""

    def __init__(self, clock: _Clock) -> None:
        self.source_id = "stream"
        self.priority = PRIORITY_STREAM
        self._clock = clock
        self._sink: Any = None

    @property
    def capabilities(self) -> tuple[Any, ...]:
        from tesla_fleet_api.router.stream import Capability, Delivery

        return tuple(
            Capability(path=path, delivery=Delivery.ON_CHANGE) for path in FieldPath
        )

    def attach(self, sink: Any) -> Any:
        self._sink = sink
        sink.set_health(self.source_id, True)
        return lambda: None

    def request(self, paths: frozenset[FieldPath]) -> None:
        return None

    def release(self, paths: frozenset[FieldPath]) -> None:
        return None

    def emit(self, path: FieldPath, value: bool) -> None:
        self._sink.publish(
            Observation(
                path=path,
                value=value,
                observed_at=self._clock(),
                source_id=self.source_id,
            )
        )

    def set_health(self, healthy: bool) -> None:
        self._sink.set_health(self.source_id, healthy)
