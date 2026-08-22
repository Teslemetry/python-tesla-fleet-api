"""Observation funnel: many push sources, one listener per field.

A field bound to a single source disappears whenever that source is
unavailable. Every publisher attached here feeds the same listeners, so a
field survives the loss of any one source. Nothing in this module chooses
between sources: unavailability is a value a source reports, never something
the funnel infers from a link dropping.

The funnel is a pure consumer of observations pushed to it. It is entirely
synchronous and holds no request callable, polling loop, HTTP/BLE read, or
scheduling task: a source the funnel could drive is a source it could be made
to poll.
"""

from __future__ import annotations

import time
from collections.abc import Mapping
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable, Iterator, Protocol, TypeVar

from tesla_fleet_api.const import LOGGER, StrEnum
from tesla_protocol.command.vcsec_pb2 import (
    ClosureState_E,
    VehicleLockState_E,
)

if TYPE_CHECKING:
    from tesla_fleet_api.tesla.vehicle.bluetooth import VehicleBluetooth

Unsubscribe = Callable[[], None]
Clock = Callable[[], float]

# A reading, or None for a source reporting the field itself as unavailable.
Value = bool | None

T = TypeVar("T")

_FATAL_CALLBACK_ERRORS = (KeyboardInterrupt, SystemExit)


class FieldPath(StrEnum):
    """A canonical routable field, valued to match its public signal name.

    A compound signal is split into one path per facet, because a broadcast and
    a ``vehicle_data`` result each expose individual leaves.
    """

    LOCKED = "Locked"
    CHARGE_PORT_DOOR_OPEN = "ChargePortDoorOpen"
    DOOR_STATE_TRUNK_FRONT = "DoorState.TrunkFront"


@dataclass(frozen=True, slots=True)
class Observation:
    """One timestamped value for one field."""

    path: FieldPath
    value: Value
    # Seconds off one monotonic clock shared by every publisher on a funnel;
    # observations from different sources are ordered against each other.
    observed_at: float


class ObservationSink(Protocol):
    """The handle a publisher is given to feed the funnel."""

    def publish(self, observation: Observation) -> None: ...


class Publisher(Protocol):
    """A source of observations for one or more canonical fields."""

    @property
    def paths(self) -> frozenset[FieldPath]: ...

    def attach(self, sink: ObservationSink) -> Unsubscribe: ...

    def request(self, paths: frozenset[FieldPath]) -> None:
        """Begin supplying ``paths``: subscription accounting, not a data request."""

    def release(self, paths: frozenset[FieldPath]) -> None:
        """Stop supplying ``paths``."""


def _dispatch(callback: Callable[[T], None], value: T) -> None:
    try:
        callback(value)
    except _FATAL_CALLBACK_ERRORS:
        raise
    except BaseException:
        LOGGER.exception("observation funnel listener callback failed")


def _noop() -> None:
    return None


@dataclass(eq=False)
class _Attached:
    publisher: Publisher
    detach: Unsubscribe


@dataclass(eq=False)
class _DemandObserver:
    paths: frozenset[FieldPath]
    callback: Callable[[bool], None]
    active: bool


class ObservationFunnel:
    """Funnels observations from every attached publisher into one listener set.

    Many to one: a listener registered for a field receives what any publisher
    reports for it, in arrival order. There is no source selection, ranking, or
    health model here, and detaching or silencing a publisher produces no value
    of its own.
    """

    def __init__(self) -> None:
        self._publishers: list[_Attached] = []
        self._listeners: dict[FieldPath, list[Callable[[Value], None]]] = {}
        self._demand_observers: list[_DemandObserver] = []
        self._observed: dict[FieldPath, Observation] = {}

    # -- Publishers --------------------------------------------------------

    def attach(self, publisher: Publisher) -> Unsubscribe:
        """Attach ``publisher`` and return its detach closure."""
        attached = _Attached(publisher=publisher, detach=_noop)
        # Registered before attaching so a publisher that reports an
        # observation synchronously is not discarded as unknown.
        self._publishers.append(attached)
        attached.detach = publisher.attach(self)
        active = self._active_paths(publisher)
        if active:
            publisher.request(active)

        def detach() -> None:
            if attached not in self._publishers:
                return
            self._publishers.remove(attached)
            active = self._active_paths(publisher)
            if active:
                publisher.release(active)
            attached.detach()

        return detach

    def _active_paths(self, publisher: Publisher) -> frozenset[FieldPath]:
        return frozenset(p for p in publisher.paths if self._listeners.get(p))

    # -- Sink ---------------------------------------------------------------

    def publish(self, observation: Observation) -> None:
        """Accept one observation from any publisher and fan it out."""
        path = observation.path
        previous = self._observed.get(path)
        if previous is not None and observation.observed_at < previous.observed_at:
            # A later reading of this field already stands.
            return
        self._observed[path] = observation
        if previous is not None and previous.value == observation.value:
            return
        for callback in list(self._listeners.get(path, ())):
            # A callback may publish, and that nested update has already given
            # every listener the newer value; continuing here would leave the
            # rest holding a value the funnel no longer holds.
            if self._observed[path] is not observation:
                return
            _dispatch(callback, observation.value)

    # -- Values and listeners -----------------------------------------------

    def value(self, path: FieldPath) -> Value:
        """The last value observed for ``path``.

        ``None`` means there is no reading: either nothing has ever been
        observed, or a source reported the field as unavailable.
        """
        observation = self._observed.get(path)
        return None if observation is None else observation.value

    def listen(self, path: FieldPath, callback: Callable[[Value], None]) -> Unsubscribe:
        """Register a listener for ``path``, called on each changed value.

        The first listener for a path activates it on every capable publisher;
        the last one to leave releases it. Registration dispatches nothing;
        the value standing at that moment is :meth:`value`.
        """
        listeners = self._listeners.setdefault(path, [])
        listeners.append(callback)
        if len(listeners) == 1:
            paths = frozenset({path})
            for attached in list(self._publishers):
                if path in attached.publisher.paths:
                    attached.publisher.request(paths)
        self._notify_demand()

        released = False

        def unsubscribe() -> None:
            # Guarded per registration: the same callback may be registered
            # twice, and a repeated release must not drop the other one.
            nonlocal released
            if released:
                return
            released = True
            try:
                listeners.remove(callback)
            except ValueError:
                return
            if not listeners:
                paths = frozenset({path})
                for attached in list(self._publishers):
                    if path in attached.publisher.paths:
                        attached.publisher.release(paths)
            self._notify_demand()

        return unsubscribe

    # -- Demand -------------------------------------------------------------

    def listen_demand(
        self, paths: frozenset[FieldPath], callback: Callable[[bool], None]
    ) -> Unsubscribe:
        """Observe whether any of ``paths`` has at least one live listener.

        Derived from the activation counts the funnel already keeps. It
        reports; it never starts work of its own.
        """
        observer = _DemandObserver(
            paths=paths, callback=callback, active=self._demand(paths)
        )
        self._demand_observers.append(observer)
        _dispatch(callback, observer.active)

        released = False

        def unsubscribe() -> None:
            nonlocal released
            if released:
                return
            released = True
            try:
                self._demand_observers.remove(observer)
            except ValueError:
                pass

        return unsubscribe

    def _demand(self, paths: frozenset[FieldPath]) -> bool:
        return any(self._listeners.get(p) for p in paths)

    def _notify_demand(self) -> None:
        for observer in list(self._demand_observers):
            active = self._demand(observer.paths)
            if active != observer.active:
                observer.active = active
                _dispatch(observer.callback, active)


# -- Bluetooth broadcast publisher -----------------------------------------

# UNLOCKED is 0 and the enum has no proto3 presence, so every status broadcast
# reports a lock state and the funnel deduplicates the repeats.
#
# INTERNAL_LOCKED and SELECTIVE_UNLOCKED are deliberately unmapped: reducing
# either to one boolean is unvalidated against live frames, and emitting
# nothing keeps the last confirmed value instead of guessing.
_LOCK_STATES: Mapping[int, bool] = {
    VehicleLockState_E.VEHICLELOCKSTATE_LOCKED: True,
    VehicleLockState_E.VEHICLELOCKSTATE_UNLOCKED: False,
}

# UNKNOWN and FAILED_UNLATCH are unmapped for the same reason.
_CLOSURE_STATES: Mapping[int, bool] = {
    ClosureState_E.CLOSURESTATE_CLOSED: False,
    ClosureState_E.CLOSURESTATE_OPEN: True,
    ClosureState_E.CLOSURESTATE_AJAR: True,
    ClosureState_E.CLOSURESTATE_OPENING: True,
    ClosureState_E.CLOSURESTATE_CLOSING: True,
}

_BROADCAST_MAPS: Mapping[FieldPath, Mapping[int, bool]] = {
    FieldPath.LOCKED: _LOCK_STATES,
    FieldPath.CHARGE_PORT_DOOR_OPEN: _CLOSURE_STATES,
    FieldPath.DOOR_STATE_TRUNK_FRONT: _CLOSURE_STATES,
}

_BROADCAST_PATHS = frozenset(_BROADCAST_MAPS)


class BleBroadcastPublisher:
    """Publishes VCSEC status broadcasts from an existing BLE session.

    Registration only: it subscribes to the broadcast listeners a
    ``VehicleBluetooth`` already fans out, and never connects, reads, or
    commands. A dropped BLE session ends the broadcasts and says nothing about
    the fields themselves, so it publishes nothing.
    """

    def __init__(
        self,
        vehicle: VehicleBluetooth[Any],
        *,
        clock: Clock = time.monotonic,
    ) -> None:
        self._vehicle = vehicle
        self._clock = clock
        self._sink: ObservationSink | None = None
        self._subscriptions: dict[FieldPath, Unsubscribe] = {}

    @property
    def paths(self) -> frozenset[FieldPath]:
        return _BROADCAST_PATHS

    def attach(self, sink: ObservationSink) -> Unsubscribe:
        self._sink = sink

        def detach() -> None:
            self.release(frozenset(self._subscriptions))
            self._sink = None

        return detach

    def request(self, paths: frozenset[FieldPath]) -> None:
        for path in paths:
            if path in self._subscriptions or path not in _BROADCAST_MAPS:
                continue
            self._subscriptions[path] = _LISTENER_FOR[path](
                self._vehicle, self._observer(path)
            )

    def release(self, paths: frozenset[FieldPath]) -> None:
        for path in paths:
            unsubscribe = self._subscriptions.pop(path, None)
            if unsubscribe is not None:
                unsubscribe()

    def _observer(self, path: FieldPath) -> Callable[[int], None]:
        states = _BROADCAST_MAPS[path]

        def on_broadcast(raw: int) -> None:
            sink = self._sink
            if sink is None or raw not in states:
                return
            sink.publish(
                Observation(path=path, value=states[raw], observed_at=self._clock())
            )

        return on_broadcast


_LISTENER_FOR: Mapping[
    FieldPath, Callable[["VehicleBluetooth[Any]", Callable[[int], None]], Unsubscribe]
] = {
    FieldPath.LOCKED: lambda vehicle, cb: vehicle.listen_vehicle_lock_state(cb),
    FieldPath.CHARGE_PORT_DOOR_OPEN: lambda vehicle, cb: vehicle.listen_charge_port(cb),
    FieldPath.DOOR_STATE_TRUNK_FRONT: lambda vehicle, cb: vehicle.listen_front_trunk(
        cb
    ),
}


# -- Supplied vehicle_data result publisher ---------------------------------

_ABSENT = object()


def _leaf(section: object, key: str) -> object:
    """A present leaf, or ``_ABSENT``: a missing key is not a null reading."""
    if isinstance(section, Mapping) and key in section:
        return section[key]  # pyright: ignore[reportUnknownVariableType]
    return _ABSENT


def _int_code(value: object) -> int | None:
    """A JSON integer code, rejecting ``bool`` so ``False`` cannot pass as 0."""
    if isinstance(value, bool) or not isinstance(value, int):
        return None
    return value


class VehicleDataResultPublisher:
    """Translates a caller-supplied ``vehicle_data`` result into observations.

    The result is an argument. This class holds no client, session, endpoint,
    or callable able to obtain one, so nothing here can originate a request or
    cause a refresh.
    """

    def __init__(self, *, clock: Clock = time.monotonic) -> None:
        self._clock = clock
        self._sink: ObservationSink | None = None

    @property
    def paths(self) -> frozenset[FieldPath]:
        return frozenset(FieldPath)

    def attach(self, sink: ObservationSink) -> Unsubscribe:
        self._sink = sink

        def detach() -> None:
            self._sink = None

        return detach

    def request(self, paths: frozenset[FieldPath]) -> None:
        """Passive source: activation subscribes to nothing."""

    def release(self, paths: frozenset[FieldPath]) -> None:
        """Passive source: activation subscribes to nothing."""

    def publish_result(
        self, result: Mapping[str, Any], *, observed_at: float | None = None
    ) -> tuple[Observation, ...]:
        """Translate a supplied result and feed the audited leaves to the sink."""
        at = self._clock() if observed_at is None else observed_at
        observations = tuple(self._translate(result, at))
        sink = self._sink
        if sink is not None:
            for observation in observations:
                sink.publish(observation)
        return observations

    def _translate(
        self, result: Mapping[str, Any], observed_at: float
    ) -> Iterator[Observation]:
        payload: Mapping[str, Any] = result
        response = _leaf(payload, "response")
        if isinstance(response, Mapping):
            payload = response  # pyright: ignore[reportUnknownVariableType]

        vehicle_state = _leaf(payload, "vehicle_state")
        charge_state = _leaf(payload, "charge_state")

        # An explicit null is the vehicle reporting the field unavailable; an
        # absent or unrecognised leaf is no reading at all.
        locked = _leaf(vehicle_state, "locked")
        if locked is None or isinstance(locked, bool):
            yield Observation(FieldPath.LOCKED, locked, observed_at)

        charge_port = _leaf(charge_state, "charge_port_door_open")
        if charge_port is None or isinstance(charge_port, bool):
            yield Observation(FieldPath.CHARGE_PORT_DOOR_OPEN, charge_port, observed_at)

        front_trunk = _leaf(vehicle_state, "ft")
        if front_trunk is None:
            yield Observation(FieldPath.DOOR_STATE_TRUNK_FRONT, None, observed_at)
        # ``ft`` is an ajar/open code, and only 0 and 1 have a documented
        # boolean meaning.
        elif (code := _int_code(front_trunk)) in (0, 1):
            yield Observation(FieldPath.DOOR_STATE_TRUNK_FRONT, code == 1, observed_at)
