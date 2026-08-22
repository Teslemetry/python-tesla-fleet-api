"""Unit tests for the ObservationFunnel core: fan-in, dedup, activation, demand.

Uses plain fake publishers so no BLE hardware, network access, or event loop is
involved; the funnel is synchronous by construction.
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Any
from unittest import TestCase

from tesla_fleet_api.funnel import (
    FieldPath,
    Observation,
    ObservationFunnel,
    ObservationSink,
    Unsubscribe,
    Value,
)

ALL_PATHS = frozenset(FieldPath)
LOCKED = FieldPath.LOCKED
CHARGE_PORT = FieldPath.CHARGE_PORT_DOOR_OPEN
TRUNK = FieldPath.DOOR_STATE_TRUNK_FRONT


class _FakePublisher:
    """A publisher a test drives directly, recording activation accounting."""

    def __init__(self, paths: frozenset[FieldPath] = ALL_PATHS) -> None:
        self.requested: list[frozenset[FieldPath]] = []
        self.released: list[frozenset[FieldPath]] = []
        self.detached = 0
        self._paths = paths
        self._sink: ObservationSink | None = None

    @property
    def paths(self) -> frozenset[FieldPath]:
        return self._paths

    def attach(self, sink: ObservationSink) -> Unsubscribe:
        self._sink = sink

        def detach() -> None:
            self.detached += 1
            self._sink = None

        return detach

    def request(self, paths: frozenset[FieldPath]) -> None:
        self.requested.append(paths)

    def release(self, paths: frozenset[FieldPath]) -> None:
        self.released.append(paths)

    # -- test driver -------------------------------------------------------

    def emit(self, path: FieldPath, value: Value, observed_at: float) -> None:
        assert self._sink is not None
        self._sink.publish(Observation(path=path, value=value, observed_at=observed_at))


class TestFanIn(TestCase):
    """Many publishers, one listener: nothing here chooses between sources."""

    def test_both_sources_reach_the_same_listener_with_no_transient_none(self) -> None:
        """The bug this exists to prevent: a field blanking when one source drops.

        Both publishers feed the same listener. The stream carries the field,
        then goes away entirely and Bluetooth carries it, then Bluetooth goes
        away and the stream carries it again. Nothing the funnel emits across
        the whole run is ``None``, because no source ever reported one.
        """
        funnel = ObservationFunnel()
        stream = _FakePublisher()
        ble = _FakePublisher()
        detach_stream = funnel.attach(stream)
        detach_ble = funnel.attach(ble)

        seen: list[Value] = []
        funnel.listen(LOCKED, seen.append)

        stream.emit(LOCKED, True, 1.0)
        self.assertEqual(seen, [True])

        # Stream to Bluetooth: the source is gone, not the field.
        detach_stream()
        self.assertEqual(seen, [True])
        self.assertIs(funnel.value(LOCKED), True)

        ble.emit(LOCKED, False, 2.0)
        ble.emit(LOCKED, True, 3.0)
        self.assertEqual(seen, [True, False, True])

        # Bluetooth back to stream, the other direction.
        detach_ble()
        detach_stream = funnel.attach(stream)
        stream.emit(LOCKED, False, 4.0)

        self.assertEqual(seen, [True, False, True, False])
        self.assertNotIn(None, seen)
        self.assertIs(funnel.value(LOCKED), False)

    def test_both_sources_stay_live_together_and_interleave(self) -> None:
        """Neither source is a standby: both are heard, in arrival order."""
        funnel = ObservationFunnel()
        stream = _FakePublisher()
        ble = _FakePublisher()
        funnel.attach(stream)
        funnel.attach(ble)

        seen: list[Value] = []
        funnel.listen(CHARGE_PORT, seen.append)

        stream.emit(CHARGE_PORT, True, 1.0)
        ble.emit(CHARGE_PORT, False, 2.0)
        stream.emit(CHARGE_PORT, True, 3.0)

        self.assertEqual(seen, [True, False, True])

    def test_detaching_every_publisher_emits_nothing(self) -> None:
        """Transport loss is not a reading, so the funnel asserts nothing."""
        funnel = ObservationFunnel()
        stream = _FakePublisher()
        ble = _FakePublisher()
        detach_stream = funnel.attach(stream)
        detach_ble = funnel.attach(ble)

        seen: list[Value] = []
        funnel.listen(TRUNK, seen.append)
        stream.emit(TRUNK, True, 1.0)

        detach_stream()
        detach_ble()

        self.assertEqual(seen, [True])
        self.assertIs(funnel.value(TRUNK), True)

    def test_a_reported_unavailable_value_is_delivered_as_such(self) -> None:
        """Unavailability is a value a source reports, and it is passed through."""
        funnel = ObservationFunnel()
        publisher = _FakePublisher()
        funnel.attach(publisher)

        seen: list[Value] = []
        funnel.listen(LOCKED, seen.append)

        publisher.emit(LOCKED, True, 1.0)
        publisher.emit(LOCKED, None, 2.0)
        publisher.emit(LOCKED, True, 3.0)

        self.assertEqual(seen, [True, None, True])

    def test_detaching_twice_is_idempotent(self) -> None:
        funnel = ObservationFunnel()
        publisher = _FakePublisher()
        detach = funnel.attach(publisher)
        funnel.listen(LOCKED, lambda _: None)

        detach()
        detach()

        self.assertEqual(publisher.detached, 1)
        self.assertEqual(publisher.released, [frozenset({LOCKED})])


class TestSurvivingLogic(TestCase):
    """The only arbitration left: drop the out-of-order, drop the unchanged."""

    def test_an_observation_older_than_the_last_one_is_ignored(self) -> None:
        funnel = ObservationFunnel()
        stream = _FakePublisher()
        ble = _FakePublisher()
        funnel.attach(stream)
        funnel.attach(ble)

        seen: list[Value] = []
        funnel.listen(LOCKED, seen.append)

        stream.emit(LOCKED, True, 10.0)
        ble.emit(LOCKED, False, 5.0)

        self.assertEqual(seen, [True])
        self.assertIs(funnel.value(LOCKED), True)

    def test_a_stale_frame_cannot_win_by_repeating_after_a_newer_one(self) -> None:
        """A skipped repeat still advances the clock it is compared against."""
        funnel = ObservationFunnel()
        publisher = _FakePublisher()
        funnel.attach(publisher)

        seen: list[Value] = []
        funnel.listen(LOCKED, seen.append)

        publisher.emit(LOCKED, True, 10.0)
        publisher.emit(LOCKED, True, 20.0)  # unchanged, not re-dispatched
        publisher.emit(LOCKED, False, 15.0)  # older than the 20.0 reading

        self.assertEqual(seen, [True])

    def test_an_unchanged_value_is_not_re_dispatched(self) -> None:
        funnel = ObservationFunnel()
        stream = _FakePublisher()
        ble = _FakePublisher()
        funnel.attach(stream)
        funnel.attach(ble)

        seen: list[Value] = []
        funnel.listen(LOCKED, seen.append)

        stream.emit(LOCKED, True, 1.0)
        stream.emit(LOCKED, True, 2.0)
        ble.emit(LOCKED, True, 3.0)
        ble.emit(LOCKED, False, 4.0)
        stream.emit(LOCKED, False, 5.0)

        self.assertEqual(seen, [True, False])

    def test_a_repeated_unavailable_value_is_also_deduplicated(self) -> None:
        funnel = ObservationFunnel()
        publisher = _FakePublisher()
        funnel.attach(publisher)

        seen: list[Value] = []
        funnel.listen(LOCKED, seen.append)

        publisher.emit(LOCKED, None, 1.0)
        publisher.emit(LOCKED, None, 2.0)

        self.assertEqual(seen, [None])

    def test_an_equal_timestamp_is_not_treated_as_older(self) -> None:
        funnel = ObservationFunnel()
        publisher = _FakePublisher()
        funnel.attach(publisher)

        seen: list[Value] = []
        funnel.listen(LOCKED, seen.append)

        publisher.emit(LOCKED, True, 1.0)
        publisher.emit(LOCKED, False, 1.0)

        self.assertEqual(seen, [True, False])

    def test_fields_are_ordered_independently(self) -> None:
        funnel = ObservationFunnel()
        publisher = _FakePublisher()
        funnel.attach(publisher)

        locked: list[Value] = []
        trunk: list[Value] = []
        funnel.listen(LOCKED, locked.append)
        funnel.listen(TRUNK, trunk.append)

        publisher.emit(LOCKED, True, 10.0)
        publisher.emit(TRUNK, True, 5.0)

        self.assertEqual(locked, [True])
        self.assertEqual(trunk, [True])


class TestValues(TestCase):
    def test_an_unobserved_field_has_no_value(self) -> None:
        funnel = ObservationFunnel()
        for path in FieldPath:
            self.assertIsNone(funnel.value(path))

    def test_registration_dispatches_nothing(self) -> None:
        funnel = ObservationFunnel()
        publisher = _FakePublisher()
        funnel.attach(publisher)
        funnel.listen(LOCKED, lambda _: None)
        publisher.emit(LOCKED, True, 1.0)

        late: list[Value] = []
        funnel.listen(LOCKED, late.append)

        self.assertEqual(late, [])
        self.assertIs(funnel.value(LOCKED), True)


class TestActivation(TestCase):
    def test_first_listener_activates_and_last_releases_exactly_once(self) -> None:
        funnel = ObservationFunnel()
        publisher = _FakePublisher()
        funnel.attach(publisher)

        first = funnel.listen(LOCKED, lambda _: None)
        second = funnel.listen(LOCKED, lambda _: None)
        self.assertEqual(publisher.requested, [frozenset({LOCKED})])

        first()
        self.assertEqual(publisher.released, [])
        second()
        self.assertEqual(publisher.released, [frozenset({LOCKED})])

        # A repeated release must not double-count either.
        second()
        self.assertEqual(publisher.released, [frozenset({LOCKED})])

    def test_the_same_callback_twice_needs_two_releases(self) -> None:
        funnel = ObservationFunnel()
        publisher = _FakePublisher()
        funnel.attach(publisher)

        def callback(_: Value) -> None:
            return None

        first = funnel.listen(LOCKED, callback)
        second = funnel.listen(LOCKED, callback)
        first()
        self.assertEqual(publisher.released, [])
        second()
        self.assertEqual(publisher.released, [frozenset({LOCKED})])

    def test_activation_is_per_path(self) -> None:
        funnel = ObservationFunnel()
        publisher = _FakePublisher()
        funnel.attach(publisher)

        funnel.listen(LOCKED, lambda _: None)
        funnel.listen(TRUNK, lambda _: None)

        self.assertEqual(publisher.requested, [frozenset({LOCKED}), frozenset({TRUNK})])

    def test_a_publisher_is_asked_only_for_paths_it_supplies(self) -> None:
        funnel = ObservationFunnel()
        publisher = _FakePublisher(paths=frozenset({LOCKED}))
        funnel.attach(publisher)

        funnel.listen(TRUNK, lambda _: None)
        self.assertEqual(publisher.requested, [])

        funnel.listen(LOCKED, lambda _: None)
        self.assertEqual(publisher.requested, [frozenset({LOCKED})])

    def test_a_publisher_attached_later_is_asked_for_active_paths(self) -> None:
        funnel = ObservationFunnel()
        funnel.listen(LOCKED, lambda _: None)

        publisher = _FakePublisher()
        funnel.attach(publisher)

        self.assertEqual(publisher.requested, [frozenset({LOCKED})])

    def test_detaching_releases_the_active_paths(self) -> None:
        funnel = ObservationFunnel()
        publisher = _FakePublisher()
        detach = funnel.attach(publisher)
        funnel.listen(LOCKED, lambda _: None)

        detach()

        self.assertEqual(publisher.released, [frozenset({LOCKED})])
        self.assertEqual(publisher.detached, 1)


class TestDispatchSafety(TestCase):
    def test_a_callback_that_publishes_leaves_no_listener_on_the_old_value(
        self,
    ) -> None:
        funnel = ObservationFunnel()
        publisher = _FakePublisher()
        funnel.attach(publisher)

        first: list[Value] = []
        second: list[Value] = []

        def republish(value: Value) -> None:
            first.append(value)
            if value is True:
                publisher.emit(LOCKED, False, 2.0)

        funnel.listen(LOCKED, republish)
        funnel.listen(LOCKED, second.append)

        publisher.emit(LOCKED, True, 1.0)

        self.assertEqual(first, [True, False])
        # The second listener saw only the value that still stands.
        self.assertEqual(second, [False])
        self.assertIs(funnel.value(LOCKED), False)

    def test_a_listener_exception_does_not_stop_later_listeners(self) -> None:
        funnel = ObservationFunnel()
        publisher = _FakePublisher()
        funnel.attach(publisher)

        def explode(_: Value) -> None:
            raise RuntimeError("listener failed")

        seen: list[Value] = []
        funnel.listen(LOCKED, explode)
        funnel.listen(LOCKED, seen.append)

        with self.assertLogs("tesla_fleet_api", level="ERROR"):
            publisher.emit(LOCKED, True, 1.0)

        self.assertEqual(seen, [True])


class TestDemand(TestCase):
    def test_demand_reports_initial_state_then_only_aggregate_edges(self) -> None:
        funnel = ObservationFunnel()
        seen: list[bool] = []
        funnel.listen_demand(ALL_PATHS, seen.append)
        self.assertEqual(seen, [False])

        locked = funnel.listen(LOCKED, lambda _: None)
        self.assertEqual(seen, [False, True])

        # Still demanded: a second path rising is not an aggregate edge.
        trunk = funnel.listen(TRUNK, lambda _: None)
        self.assertEqual(seen, [False, True])

        locked()
        self.assertEqual(seen, [False, True])
        trunk()
        self.assertEqual(seen, [False, True, False])

    def test_demand_starts_true_when_a_listener_already_exists(self) -> None:
        funnel = ObservationFunnel()
        funnel.listen(LOCKED, lambda _: None)

        seen: list[bool] = []
        funnel.listen_demand(ALL_PATHS, seen.append)
        self.assertEqual(seen, [True])

    def test_demand_ignores_listeners_outside_its_path_set(self) -> None:
        funnel = ObservationFunnel()
        seen: list[bool] = []
        funnel.listen_demand(frozenset({LOCKED}), seen.append)

        funnel.listen(TRUNK, lambda _: None)
        self.assertEqual(seen, [False])

        funnel.listen(LOCKED, lambda _: None)
        self.assertEqual(seen, [False, True])

    def test_unsubscribe_removes_only_that_observer(self) -> None:
        funnel = ObservationFunnel()
        kept: list[bool] = []
        dropped: list[bool] = []
        funnel.listen_demand(ALL_PATHS, kept.append)
        release = funnel.listen_demand(ALL_PATHS, dropped.append)

        release()
        release()
        funnel.listen(LOCKED, lambda _: None)

        self.assertEqual(kept, [False, True])
        self.assertEqual(dropped, [False])

    def test_releasing_one_of_two_identical_registrations_keeps_the_other(
        self,
    ) -> None:
        funnel = ObservationFunnel()
        seen: list[bool] = []
        funnel.listen_demand(ALL_PATHS, seen.append)
        release = funnel.listen_demand(ALL_PATHS, seen.append)

        release()
        funnel.listen(LOCKED, lambda _: None)

        self.assertEqual(seen, [False, False, True])


class TestFunnelCannotOriginateWork(TestCase):
    """The load-bearing invariant: the funnel is structurally unable to poll.

    Asserted against the module's own syntax tree rather than its behaviour,
    because a request path that exists but is merely unused would still be a
    request path.
    """

    tree: ast.Module

    @classmethod
    def setUpClass(cls) -> None:
        import tesla_fleet_api.funnel as module

        source = Path(module.__file__).read_text(encoding="utf-8")
        cls.tree = ast.parse(source)

    def test_the_module_is_entirely_synchronous(self) -> None:
        for node in ast.walk(self.tree):
            self.assertNotIsInstance(node, ast.AsyncFunctionDef)
            self.assertNotIsInstance(node, ast.Await)
            self.assertNotIsInstance(node, ast.AsyncFor)
            self.assertNotIsInstance(node, ast.AsyncWith)

    def test_the_module_imports_no_transport_or_scheduling_machinery(self) -> None:
        forbidden = {
            "asyncio",
            "aiohttp",
            "aiofiles",
            "bleak",
            "threading",
            "sched",
            "requests",
            "urllib",
            "socket",
        }
        imported: set[str] = set()
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".")[0])
        self.assertEqual(imported & forbidden, set())

    def test_the_module_calls_nothing_that_could_originate_a_request(self) -> None:
        forbidden = {
            "sleep",
            "create_task",
            "ensure_future",
            "run_coroutine_threadsafe",
            "call_later",
            "call_soon",
            "vehicle_data",
            "charge_state",
            "vehicle_state",
            "connect",
            "connect_if_needed",
            "wake_up",
            "_send",
            "_request",
            "_getVehicleSecurity",
            "_getInfotainment",
            "Thread",
            "Timer",
        }
        called: set[str] = set()
        for node in ast.walk(self.tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            if isinstance(func, ast.Name):
                called.add(func.id)
            elif isinstance(func, ast.Attribute):
                called.add(func.attr)
        self.assertEqual(called & forbidden, set())

    def test_the_funnel_exposes_no_awaitable_member(self) -> None:
        import inspect

        funnel: Any = ObservationFunnel()
        for name, member in inspect.getmembers(funnel):
            self.assertFalse(
                inspect.iscoroutinefunction(member),
                msg=f"{name} is a coroutine function",
            )
