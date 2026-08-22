"""Read router: per-field arbitration of pushed vehicle observations.

A field bound to a single source disappears whenever that source is
unavailable. This router keeps a canonical field alive while any attached
source can still supply it, and reports transport loss as availability rather
than as a data value.

The router is a pure consumer of observations pushed to it. It is entirely
synchronous and holds no request callable, polling loop, HTTP/BLE read,
scheduling task, or cost policy: a source the router could drive is a source
it could be made to poll.
"""

from __future__ import annotations

import time
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable, Iterator, NamedTuple, Protocol, TypeVar

from tesla_fleet_api.const import LOGGER, StrEnum
from tesla_protocol.command.vcsec_pb2 import (
    ClosureState_E,
    VehicleLockState_E,
)

if TYPE_CHECKING:
    from tesla_fleet_api.tesla.vehicle.bluetooth import VehicleBluetooth

Unsubscribe = Callable[[], None]
Clock = Callable[[], float]

T = TypeVar("T")

_FATAL_CALLBACK_ERRORS = (KeyboardInterrupt, SystemExit)

# Last-known data is retained this long after the last source able to supply a
# field drops out, before the field is reported unavailable.
DEFAULT_GRACE = 300.0

# A source that regains health must hold it this long before it can take a
# field back off a working standby.
DEFAULT_FAILBACK_DELAY = 5.0

# A supplied result is a point-in-time snapshot, so it expires by age.
DEFAULT_RESULT_MAX_AGE = 300.0

# Publisher priority, lower wins. A local-first consumer may override any
# publisher's priority.
PRIORITY_STREAM = 10
PRIORITY_BLE_PUSH = 20
PRIORITY_BROADCAST = 30
PRIORITY_SUPPLIED_RESULT = 40


class FieldPath(StrEnum):
    """A canonical routable field, valued to match its public signal name.

    A compound signal is split into one path per facet, because a broadcast and
    a ``vehicle_data`` result each expose individual leaves and selection is
    per facet.
    """

    LOCKED = "Locked"
    CHARGE_PORT_DOOR_OPEN = "ChargePortDoorOpen"
    DOOR_STATE_TRUNK_FRONT = "DoorState.TrunkFront"


class Delivery(StrEnum):
    """How a publisher delivers a field."""

    ON_CHANGE = "on_change"
    CADENCED_PUSH = "cadenced_push"
    PASSIVE_RESULT = "passive_result"


class Fidelity(StrEnum):
    """How faithfully a publisher's translation preserves the field."""

    EXACT = "exact"
    LOSSY = "lossy"


@dataclass(frozen=True, slots=True)
class Capability:
    """What one publisher can supply for one field path."""

    path: FieldPath
    delivery: Delivery
    fidelity: Fidelity = Fidelity.EXACT
    # None is connection-bound: silence from an on-change source is not
    # staleness, only loss of health is.
    max_age: float | None = None


@dataclass(frozen=True, slots=True)
class Observation:
    """One timestamped value for one field, from one source."""

    path: FieldPath
    value: bool
    observed_at: float
    source_id: str
    source_sequence: int | None = None


class PublisherSink(Protocol):
    """The handle a publisher is given to feed the router.

    Health is a separate channel from data so that transport loss can never
    reach a listener as a value.
    """

    def publish(self, observation: Observation) -> None: ...

    def set_health(self, source_id: str, healthy: bool) -> None: ...


class Publisher(Protocol):
    """A source of observations for one or more canonical fields."""

    source_id: str
    priority: int

    @property
    def capabilities(self) -> tuple[Capability, ...]: ...

    def attach(self, sink: PublisherSink) -> Unsubscribe: ...

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
        LOGGER.exception("stream router listener callback failed")


@dataclass
class _SourceState:
    publisher: Publisher
    capabilities: dict[FieldPath, Capability]
    detach: Unsubscribe
    healthy: bool = False
    has_been_healthy: bool = False
    # Set only when health returns after a loss, which is the only case the
    # failback delay guards against.
    recovered_at: float | None = None
    observations: dict[FieldPath, Observation] = field(
        default_factory=dict[FieldPath, Observation]
    )


class _Candidate(NamedTuple):
    state: _SourceState
    observation: Observation
    capability: Capability


def _rank(candidate: _Candidate) -> tuple[int, int]:
    """Lower sorts better: exact translations first, then source priority."""
    return (
        0 if candidate.capability.fidelity is Fidelity.EXACT else 1,
        candidate.state.publisher.priority,
    )


@dataclass
class _DemandObserver:
    paths: frozenset[FieldPath]
    callback: Callable[[bool], None]
    active: bool


class StreamRouter:
    """Arbitrates canonical field observations across attached publishers.

    Every value reaches a listener through selection here; a publisher never
    calls a public listener directly, so one source can never bypass another's
    arbitration.
    """

    def __init__(
        self,
        *,
        grace: float = DEFAULT_GRACE,
        failback_delay: float = DEFAULT_FAILBACK_DELAY,
        clock: Clock = time.monotonic,
    ) -> None:
        self._clock = clock
        self._grace = grace
        self._failback_delay = failback_delay
        self._sources: dict[str, _SourceState] = {}
        self._listeners: dict[FieldPath, list[Callable[[bool], None]]] = {}
        self._availability_listeners: dict[FieldPath, list[Callable[[bool], None]]] = {}
        self._demand_observers: list[_DemandObserver] = []
        self._selected: dict[FieldPath, str] = {}
        self._values: dict[FieldPath, bool] = {}
        self._observed_at: dict[FieldPath, float] = {}
        self._announced_availability: dict[FieldPath, bool] = {}

    # -- Publishers --------------------------------------------------------

    def attach(self, publisher: Publisher) -> Unsubscribe:
        """Attach ``publisher`` and return its detach closure."""
        source_id = publisher.source_id
        if source_id in self._sources:
            raise ValueError(f"source_id {source_id!r} is already attached")

        capabilities = {c.path: c for c in publisher.capabilities}
        state = _SourceState(
            publisher=publisher, capabilities=capabilities, detach=_noop
        )
        # Registered before attaching so a publisher that reports health or an
        # observation synchronously is not discarded as unknown.
        self._sources[source_id] = state
        state.detach = publisher.attach(self)

        active = self._active_paths(capabilities)
        if active:
            publisher.request(active)
        return lambda: self._detach(source_id, state)

    def _detach(self, source_id: str, state: _SourceState) -> None:
        if self._sources.get(source_id) is not state:
            return
        del self._sources[source_id]
        active = self._active_paths(state.capabilities)
        if active:
            state.publisher.release(active)
        state.detach()
        for path in state.capabilities:
            self._reselect(path)

    def _active_paths(
        self, capabilities: Mapping[FieldPath, Capability]
    ) -> frozenset[FieldPath]:
        return frozenset(p for p in capabilities if self._listeners.get(p))

    # -- Sink ---------------------------------------------------------------

    def publish(self, observation: Observation) -> None:
        """Accept one observation from an attached publisher."""
        state = self._sources.get(observation.source_id)
        if state is None or observation.path not in state.capabilities:
            return
        previous = state.observations.get(observation.path)
        if previous is not None and previous.observed_at > observation.observed_at:
            return
        state.observations[observation.path] = observation
        self._reselect(observation.path)

    def set_health(self, source_id: str, healthy: bool) -> None:
        """Record a source's transport health."""
        state = self._sources.get(source_id)
        if state is None or state.healthy == healthy:
            return
        state.healthy = healthy
        if healthy:
            state.recovered_at = self._clock() if state.has_been_healthy else None
            state.has_been_healthy = True
        else:
            # A lost transport cannot vouch for what it last reported, so its
            # readings are dropped rather than allowed to win on reconnect.
            state.observations.clear()
        for path in state.capabilities:
            self._reselect(path)

    # -- Selection ----------------------------------------------------------

    def _candidates(self, path: FieldPath) -> list[_Candidate]:
        now = self._clock()
        candidates: list[_Candidate] = []
        for state in self._sources.values():
            capability = state.capabilities.get(path)
            if capability is None or not state.healthy:
                continue
            observation = state.observations.get(path)
            if observation is None:
                continue
            if (
                capability.max_age is not None
                and now - observation.observed_at > capability.max_age
            ):
                continue
            candidates.append(_Candidate(state, observation, capability))
        return candidates

    def _reselect(self, path: FieldPath) -> None:
        candidates = self._candidates(path)
        if not candidates:
            self._selected.pop(path, None)
            self._announce_availability(path)
            return

        selected_id = self._selected.get(path)
        current = next(
            (c for c in candidates if c.state.publisher.source_id == selected_id), None
        )
        best_rank = min(_rank(c) for c in candidates)
        if current is not None and _rank(current) == best_rank:
            # Stickiness within a tier: an equally ranked source does not
            # displace the one already selected.
            chosen = current
        else:
            better = [c for c in candidates if _rank(c) == best_rank]
            if current is not None:
                # A source that just regained health holds it briefly before it
                # can take the field back off a working standby.
                now = self._clock()
                better = [
                    c
                    for c in better
                    if c.state.recovered_at is None
                    or now - c.state.recovered_at >= self._failback_delay
                ]
            chosen = (
                max(better, key=lambda c: c.observation.observed_at)
                if better
                else current
            )

        if chosen is None:
            self._selected.pop(path, None)
            self._announce_availability(path)
            return

        self._selected[path] = chosen.state.publisher.source_id
        self._observed_at[path] = chosen.observation.observed_at
        changed = (
            path not in self._values or self._values[path] != chosen.observation.value
        )
        self._values[path] = chosen.observation.value
        self._announce_availability(path)
        if changed:
            for callback in list(self._listeners.get(path, ())):
                _dispatch(callback, chosen.observation.value)

    # -- Values and availability --------------------------------------------

    def value(self, path: FieldPath) -> bool | None:
        """The last known value for ``path``, or ``None`` if never observed.

        ``None`` here means no source has ever reported the field; it is never
        produced by transport loss, which shows up in :meth:`is_available`.
        """
        return self._values.get(path)

    def is_available(self, path: FieldPath) -> bool:
        """Whether ``path`` has a usable source, or last-known data still in grace.

        Freshness is recomputed here rather than read off the last selection, so
        an expiry that had no event to fire on is still reported honestly.
        """
        if self._candidates(path):
            return True
        if path not in self._values:
            return False
        return self._clock() - self._observed_at[path] <= self._grace

    def _announce_availability(self, path: FieldPath) -> None:
        available = self.is_available(path)
        if self._announced_availability.get(path) == available:
            return
        self._announced_availability[path] = available
        for callback in list(self._availability_listeners.get(path, ())):
            _dispatch(callback, available)

    # -- Public listeners ---------------------------------------------------

    def listen(self, path: FieldPath, callback: Callable[[bool], None]) -> Unsubscribe:
        """Register a value listener for ``path``.

        The first listener for a path activates it on every capable publisher;
        the last one to leave releases it.
        """
        listeners = self._listeners.setdefault(path, [])
        listeners.append(callback)
        if len(listeners) == 1:
            paths = frozenset({path})
            for state in list(self._sources.values()):
                if path in state.capabilities:
                    state.publisher.request(paths)
        self._notify_demand()

        released = False

        def unsubscribe() -> None:
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
                for state in list(self._sources.values()):
                    if path in state.capabilities:
                        state.publisher.release(paths)
            self._notify_demand()

        return unsubscribe

    def listen_availability(
        self, path: FieldPath, callback: Callable[[bool], None]
    ) -> Unsubscribe:
        """Register an availability listener for ``path``.

        Fires with the current state at registration and then on transitions
        caused by an event. Grace expiry has no event to fire on, so a consumer
        that must observe it reads :meth:`is_available`.
        """
        listeners = self._availability_listeners.setdefault(path, [])
        listeners.append(callback)
        available = self.is_available(path)
        self._announced_availability.setdefault(path, available)
        _dispatch(callback, available)

        def unsubscribe() -> None:
            try:
                listeners.remove(callback)
            except ValueError:
                pass

        return unsubscribe

    # -- Demand -------------------------------------------------------------

    def listen_demand(
        self, paths: frozenset[FieldPath], callback: Callable[[bool], None]
    ) -> Unsubscribe:
        """Observe whether any of ``paths`` has at least one live value listener.

        Derived from the activation counts the router already keeps. It reports;
        it never starts work of its own.
        """
        observer = _DemandObserver(
            paths=paths, callback=callback, active=self._demand(paths)
        )
        self._demand_observers.append(observer)
        _dispatch(callback, observer.active)

        def unsubscribe() -> None:
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


def _noop() -> None:
    return None


# -- Bluetooth broadcast publisher -----------------------------------------

# UNLOCKED is 0 and the enum has no proto3 presence, so every status broadcast
# reports a lock state and the router deduplicates the repeats.
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

_BROADCAST_CAPABILITIES = tuple(
    Capability(path=path, delivery=Delivery.ON_CHANGE, fidelity=Fidelity.EXACT)
    for path in _BROADCAST_MAPS
)


class BleBroadcastPublisher:
    """Publishes VCSEC status broadcasts from an existing BLE session.

    Registration only: it subscribes to the broadcast and connection-status
    listeners a ``VehicleBluetooth`` already fans out, and never connects,
    reads, or commands.
    """

    def __init__(
        self,
        vehicle: VehicleBluetooth[Any],
        *,
        source_id: str = "ble-broadcast",
        priority: int = PRIORITY_BROADCAST,
        clock: Clock = time.monotonic,
    ) -> None:
        self._vehicle = vehicle
        self._clock = clock
        self._sink: PublisherSink | None = None
        self._subscriptions: dict[FieldPath, Unsubscribe] = {}
        self.source_id = source_id
        self.priority = priority

    @property
    def capabilities(self) -> tuple[Capability, ...]:
        return _BROADCAST_CAPABILITIES

    def attach(self, sink: PublisherSink) -> Unsubscribe:
        self._sink = sink
        unsubscribe_health = self._vehicle.listen_connection_status(
            lambda connected: sink.set_health(self.source_id, connected)
        )
        # listen_connection_status only fires on transitions, so the session
        # already in progress at attach time has to be reported here.
        client = self._vehicle.client
        sink.set_health(self.source_id, bool(client and client.is_connected))

        def detach() -> None:
            unsubscribe_health()
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
                Observation(
                    path=path,
                    value=states[raw],
                    observed_at=self._clock(),
                    source_id=self.source_id,
                )
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


def _leaf(section: object, key: str) -> object:
    """A present leaf, or ``None``: an absent key is not a falsy value."""
    if isinstance(section, Mapping) and key in section:
        return section[key]  # pyright: ignore[reportUnknownVariableType]
    return None


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

    def __init__(
        self,
        *,
        source_id: str = "vehicle-data",
        max_age: float = DEFAULT_RESULT_MAX_AGE,
        priority: int = PRIORITY_SUPPLIED_RESULT,
        clock: Clock = time.monotonic,
    ) -> None:
        self._clock = clock
        self._sink: PublisherSink | None = None
        self._capabilities = tuple(
            Capability(
                path=path,
                delivery=Delivery.PASSIVE_RESULT,
                fidelity=Fidelity.EXACT,
                max_age=max_age,
            )
            for path in FieldPath
        )
        self.source_id = source_id
        self.priority = priority

    @property
    def capabilities(self) -> tuple[Capability, ...]:
        return self._capabilities

    def attach(self, sink: PublisherSink) -> Unsubscribe:
        self._sink = sink
        # A supplied result carries its own freshness and there is no session
        # to lose, so the source is healthy for as long as it is attached.
        sink.set_health(self.source_id, True)

        def detach() -> None:
            sink.set_health(self.source_id, False)
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

        locked = _leaf(vehicle_state, "locked")
        if isinstance(locked, bool):
            yield self._observation(FieldPath.LOCKED, locked, observed_at)

        charge_port = _leaf(charge_state, "charge_port_door_open")
        if isinstance(charge_port, bool):
            yield self._observation(
                FieldPath.CHARGE_PORT_DOOR_OPEN, charge_port, observed_at
            )

        # ``ft`` is an ajar/open code, and only 0 and 1 have a documented
        # boolean meaning.
        front_trunk = _int_code(_leaf(vehicle_state, "ft"))
        if front_trunk in (0, 1):
            yield self._observation(
                FieldPath.DOOR_STATE_TRUNK_FRONT, front_trunk == 1, observed_at
            )

    def _observation(
        self, path: FieldPath, value: bool, observed_at: float
    ) -> Observation:
        return Observation(
            path=path, value=value, observed_at=observed_at, source_id=self.source_id
        )
