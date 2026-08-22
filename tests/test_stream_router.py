"""Unit tests for the StreamRouter core: selection, freshness, activation, demand.

Uses plain fake publishers so no BLE hardware, network access, or event loop is
involved; the router is synchronous by construction.
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Any
from unittest import TestCase

from tesla_fleet_api.router import (
    Capability,
    Delivery,
    FieldPath,
    Fidelity,
    Observation,
    PublisherSink,
    StreamRouter,
)
from tesla_fleet_api.router.stream import (
    PRIORITY_BLE_PUSH,
    PRIORITY_BROADCAST,
    PRIORITY_STREAM,
    PRIORITY_SUPPLIED_RESULT,
    Unsubscribe,
)

ALL_PATHS = frozenset(FieldPath)


class _Clock:
    """A hand-advanced clock so freshness and hysteresis are deterministic."""

    def __init__(self, now: float = 0.0) -> None:
        self.now = now

    def __call__(self) -> float:
        return self.now


class _FakePublisher:
    """A publisher a test drives directly, recording activation accounting."""

    def __init__(
        self,
        source_id: str,
        *,
        priority: int = PRIORITY_STREAM,
        paths: frozenset[FieldPath] = ALL_PATHS,
        fidelity: Fidelity = Fidelity.EXACT,
        max_age: float | None = None,
    ) -> None:
        self.source_id = source_id
        self.priority = priority
        self.requested: list[frozenset[FieldPath]] = []
        self.released: list[frozenset[FieldPath]] = []
        self.detached = 0
        self._sink: PublisherSink | None = None
        self._capabilities = tuple(
            Capability(
                path=path,
                delivery=Delivery.ON_CHANGE,
                fidelity=fidelity,
                max_age=max_age,
            )
            for path in sorted(paths)
        )

    @property
    def capabilities(self) -> tuple[Capability, ...]:
        return self._capabilities

    def attach(self, sink: PublisherSink) -> Unsubscribe:
        self._sink = sink

        def detach() -> None:
            self.detached += 1
            self._sink = None

        return detach

    def request(self, paths: frozenset[FieldPath]) -> None:
        self.requested.append(paths)

    def release(self, paths: frozenset[FieldPath]) -> None:
        self.released.append(paths)

    # -- test drivers ------------------------------------------------------

    def emit(self, path: FieldPath, value: bool, observed_at: float) -> None:
        assert self._sink is not None
        self._sink.publish(
            Observation(
                path=path,
                value=value,
                observed_at=observed_at,
                source_id=self.source_id,
            )
        )

    def health(self, healthy: bool) -> None:
        assert self._sink is not None
        self._sink.set_health(self.source_id, healthy)


class _Recorder:
    """An ordered timeline of everything a listener was handed."""

    def __init__(self) -> None:
        self.values: list[Any] = []
        self.availability: list[Any] = []

    def on_value(self, value: Any) -> None:
        self.values.append(value)

    def on_availability(self, available: Any) -> None:
        self.availability.append(available)


class TestSelectionAndFailover(TestCase):
    def test_fails_over_both_directions_without_a_transient_none(self) -> None:
        """The bug this router exists to prevent: a source loss blanking a field.

        Both the failover and the failback must carry a real value from the
        source that still has one; nothing may reach a listener as ``None``,
        and availability must never dip.
        """
        clock = _Clock()
        router = StreamRouter(clock=clock, failback_delay=5.0)
        stream = _FakePublisher("stream", priority=PRIORITY_STREAM)
        standby = _FakePublisher("standby", priority=PRIORITY_BROADCAST)
        router.attach(stream)
        router.attach(standby)

        recorder = _Recorder()
        router.listen(FieldPath.LOCKED, recorder.on_value)
        router.listen_availability(FieldPath.LOCKED, recorder.on_availability)
        self.assertEqual(recorder.availability, [False])

        stream.health(True)
        standby.health(True)
        stream.emit(FieldPath.LOCKED, True, observed_at=0.0)
        self.assertEqual(recorder.values, [True])

        # The standby disagrees, but the preferred source is selected, so its
        # observation must not reach the listener.
        clock.now = 1.0
        standby.emit(FieldPath.LOCKED, False, observed_at=1.0)
        self.assertEqual(recorder.values, [True])
        self.assertIs(router.value(FieldPath.LOCKED), True)

        # Failover: the preferred source dies, the standby's real value lands.
        clock.now = 2.0
        stream.health(False)
        self.assertEqual(recorder.values, [True, False])
        self.assertIs(router.value(FieldPath.LOCKED), False)
        self.assertTrue(router.is_available(FieldPath.LOCKED))

        # A recovered source may not take the field back until it has held
        # health for the failback delay.
        clock.now = 3.0
        stream.health(True)
        clock.now = 3.5
        stream.emit(FieldPath.LOCKED, True, observed_at=3.5)
        self.assertEqual(recorder.values, [True, False])

        # Failback, once that window has elapsed.
        clock.now = 10.0
        stream.emit(FieldPath.LOCKED, True, observed_at=10.0)
        self.assertEqual(recorder.values, [True, False, True])

        self.assertNotIn(None, recorder.values)
        self.assertTrue(all(isinstance(v, bool) for v in recorder.values))
        # One False at registration, one True on the first value: never dipped.
        self.assertEqual(recorder.availability, [False, True])

    def test_a_frame_racing_a_disconnect_is_not_resurrected_by_reconnect(self) -> None:
        """A dead source's reading may not come back as a live one.

        A broadcast already in flight can land after the transport loss is
        recorded. Broadcast capabilities are connection-bound, so caching it
        would let reconnect present a pre-disconnect value as an observation of
        the recovered session, and nothing would ever expire it.
        """
        clock = _Clock()
        router = StreamRouter(clock=clock, grace=50.0)
        ble = _FakePublisher("ble", priority=PRIORITY_BROADCAST, max_age=None)
        router.attach(ble)
        ble.health(True)

        recorder = _Recorder()
        router.listen(FieldPath.LOCKED, recorder.on_value)
        router.listen_availability(FieldPath.LOCKED, recorder.on_availability)
        ble.emit(FieldPath.LOCKED, False, observed_at=0.0)
        self.assertEqual(recorder.values, [False])

        clock.now = 10.0
        ble.health(False)

        # The race: the frame for a lock that happened as the link dropped
        # arrives after the loss was recorded.
        clock.now = 11.0
        ble.emit(FieldPath.LOCKED, True, observed_at=11.0)

        # The car is unlocked again while the link is down, so that frame is
        # already wrong by the time the link comes back.
        clock.now = 20.0
        ble.health(True)
        self.assertEqual(recorder.values, [False])
        self.assertIs(router.value(FieldPath.LOCKED), False)

        # Nor may it hold the field open: with nothing observed in the new
        # session, last-known availability still expires on the grace window.
        clock.now = 70.0
        self.assertFalse(router.is_available(FieldPath.LOCKED))
        self.assertEqual(recorder.values, [False])

        # The recovered session itself is unaffected.
        ble.emit(FieldPath.LOCKED, True, observed_at=70.0)
        self.assertEqual(recorder.values, [False, True])
        self.assertTrue(router.is_available(FieldPath.LOCKED))

    def test_losing_every_source_keeps_last_known_and_emits_nothing(self) -> None:
        clock = _Clock()
        router = StreamRouter(clock=clock, grace=50.0)
        stream = _FakePublisher("stream")
        router.attach(stream)
        recorder = _Recorder()
        router.listen(FieldPath.LOCKED, recorder.on_value)
        router.listen_availability(FieldPath.LOCKED, recorder.on_availability)

        stream.health(True)
        stream.emit(FieldPath.LOCKED, True, observed_at=0.0)
        clock.now = 5.0
        stream.health(False)

        self.assertEqual(recorder.values, [True])
        self.assertIs(router.value(FieldPath.LOCKED), True)
        # Within grace the last known value still stands.
        self.assertTrue(router.is_available(FieldPath.LOCKED))
        self.assertEqual(recorder.availability, [False, True])

        clock.now = 60.0
        self.assertFalse(router.is_available(FieldPath.LOCKED))
        self.assertIs(router.value(FieldPath.LOCKED), True)

    def test_exact_translation_outranks_lossy_from_a_better_priority(self) -> None:
        clock = _Clock()
        router = StreamRouter(clock=clock)
        lossy = _FakePublisher(
            "lossy", priority=PRIORITY_STREAM, fidelity=Fidelity.LOSSY
        )
        exact = _FakePublisher("exact", priority=PRIORITY_BROADCAST)
        router.attach(lossy)
        router.attach(exact)
        lossy.health(True)
        exact.health(True)

        recorder = _Recorder()
        router.listen(FieldPath.LOCKED, recorder.on_value)
        lossy.emit(FieldPath.LOCKED, True, observed_at=0.0)
        exact.emit(FieldPath.LOCKED, False, observed_at=0.0)

        self.assertEqual(recorder.values, [True, False])
        # The lossy source cannot take it back.
        lossy.emit(FieldPath.LOCKED, True, observed_at=1.0)
        self.assertEqual(recorder.values, [True, False])

    def test_equal_tier_is_sticky(self) -> None:
        clock = _Clock()
        router = StreamRouter(clock=clock)
        first = _FakePublisher("first", priority=PRIORITY_STREAM)
        second = _FakePublisher("second", priority=PRIORITY_STREAM)
        router.attach(first)
        router.attach(second)
        first.health(True)
        second.health(True)

        recorder = _Recorder()
        router.listen(FieldPath.LOCKED, recorder.on_value)
        first.emit(FieldPath.LOCKED, True, observed_at=0.0)
        second.emit(FieldPath.LOCKED, False, observed_at=1.0)
        self.assertEqual(recorder.values, [True])

    def test_a_delayed_top_source_does_not_mask_an_eligible_middle_one(self) -> None:
        """A field must not sit on a worse backend while a better one is ready.

        The top source is inside its failback delay, so it cannot take the field
        back yet. That must not stop an untouched middle-priority source from
        displacing the worst one it is currently sitting on.
        """
        clock = _Clock()
        router = StreamRouter(clock=clock, failback_delay=5.0)
        stream = _FakePublisher("stream", priority=PRIORITY_STREAM)
        ble = _FakePublisher("ble", priority=PRIORITY_BLE_PUSH)
        supplied = _FakePublisher("supplied", priority=PRIORITY_SUPPLIED_RESULT)
        for publisher in (stream, ble, supplied):
            router.attach(publisher)
            publisher.health(True)

        recorder = _Recorder()
        router.listen(FieldPath.LOCKED, recorder.on_value)

        # The top source holds the field; the middle one has said nothing yet.
        stream.emit(FieldPath.LOCKED, True, observed_at=0.0)
        supplied.emit(FieldPath.LOCKED, False, observed_at=0.0)
        self.assertEqual(recorder.values, [True])

        # The top source drops, leaving only the worst source with a reading.
        clock.now = 10.0
        stream.health(False)
        self.assertEqual(recorder.values, [True, False])

        # It comes back and reports, but is held by the failback delay.
        clock.now = 20.0
        stream.health(True)
        stream.emit(FieldPath.LOCKED, True, observed_at=20.0)
        self.assertEqual(recorder.values, [True, False])

        # The middle source never lost health, so it is eligible now and must
        # take the field off the worst source rather than waiting out a delay
        # that belongs to a different source.
        ble.emit(FieldPath.LOCKED, True, observed_at=21.0)
        self.assertEqual(recorder.values, [True, False, True])

        # Prove the middle source really holds it: only the selected source can
        # move the value, and the held top source still cannot.
        stream.emit(FieldPath.LOCKED, False, observed_at=22.0)
        self.assertEqual(recorder.values, [True, False, True])
        ble.emit(FieldPath.LOCKED, False, observed_at=23.0)
        self.assertEqual(recorder.values, [True, False, True, False])


class TestAvailabilityAnnouncement(TestCase):
    def test_a_listener_registered_after_grace_expiry_still_gets_the_recovery(
        self,
    ) -> None:
        """A late listener must not be permanently stuck on unavailable.

        Grace expiry has no event to announce, so a listener registering after
        it is told the recomputed truth. If that recomputation did not also
        correct what the router believes it has announced, the next real
        recovery looks like a repeat and this listener never hears it.
        """
        clock = _Clock()
        router = StreamRouter(clock=clock, grace=300.0)
        source = _FakePublisher("source")
        router.attach(source)
        source.health(True)

        source.emit(FieldPath.LOCKED, True, observed_at=0.0)
        early = _Recorder()
        router.listen_availability(FieldPath.LOCKED, early.on_availability)
        self.assertEqual(early.availability, [True])

        # Transport loss: last known data still stands during grace.
        source.health(False)
        self.assertEqual(early.availability, [True])
        self.assertTrue(router.is_available(FieldPath.LOCKED))

        # Grace lapses silently; there is no event to fire on.
        clock.now = 400.0
        self.assertFalse(router.is_available(FieldPath.LOCKED))
        self.assertEqual(early.availability, [True])

        late = _Recorder()
        router.listen_availability(FieldPath.LOCKED, late.on_availability)
        self.assertEqual(late.availability, [False])

        # A real recovery must reach the listener that was told False.
        source.health(True)
        source.emit(FieldPath.LOCKED, True, observed_at=400.0)
        self.assertEqual(late.availability, [False, True])
        self.assertTrue(router.is_available(FieldPath.LOCKED))


class TestFreshness(TestCase):
    def test_connection_bound_source_never_goes_stale_while_healthy(self) -> None:
        clock = _Clock()
        router = StreamRouter(clock=clock)
        stream = _FakePublisher("stream", max_age=None)
        router.attach(stream)
        stream.health(True)
        stream.emit(FieldPath.LOCKED, True, observed_at=0.0)

        clock.now = 100_000.0
        self.assertTrue(router.is_available(FieldPath.LOCKED))
        self.assertIs(router.value(FieldPath.LOCKED), True)

    def test_grace_runs_from_source_loss_not_from_the_last_change(self) -> None:
        """The window a grace period exists to provide, for an on-change source.

        A connection-bound source only speaks when the value changes, so a
        healthy one is legitimately hours behind. Measuring grace from the
        observation would expire the field the instant that source dropped,
        which is precisely the case grace is there to cover.
        """
        clock = _Clock()
        router = StreamRouter(clock=clock, grace=300.0)
        ble = _FakePublisher("ble", priority=PRIORITY_BROADCAST, max_age=None)
        router.attach(ble)
        recorder = _Recorder()
        router.listen_availability(FieldPath.LOCKED, recorder.on_availability)

        ble.health(True)
        ble.emit(FieldPath.LOCKED, True, observed_at=0.0)
        self.assertEqual(recorder.availability, [False, True])

        # Hours of a locked car: nothing changed, so nothing was broadcast.
        clock.now = 20_000.0
        self.assertTrue(router.is_available(FieldPath.LOCKED))

        ble.health(False)
        self.assertEqual(recorder.availability, [False, True])

        clock.now = 20_299.0
        self.assertTrue(router.is_available(FieldPath.LOCKED))
        self.assertIs(router.value(FieldPath.LOCKED), True)

        clock.now = 20_301.0
        self.assertFalse(router.is_available(FieldPath.LOCKED))
        self.assertIs(router.value(FieldPath.LOCKED), True)

    def test_grace_after_a_silent_expiry_runs_from_that_expiry(self) -> None:
        """An age-bounded source expires with no event to fire on.

        Grace is anchored to when candidacy actually ended, so the first caller
        to ask cannot restart the window merely by asking late.
        """
        clock = _Clock()
        router = StreamRouter(clock=clock, grace=100.0)
        result = _FakePublisher("result", max_age=60.0)
        router.attach(result)
        result.health(True)
        result.emit(FieldPath.LOCKED, True, observed_at=0.0)

        clock.now = 159.0
        self.assertTrue(router.is_available(FieldPath.LOCKED))
        clock.now = 161.0
        self.assertFalse(router.is_available(FieldPath.LOCKED))

    def test_grace_restarts_when_a_recovered_source_is_lost_again(self) -> None:
        clock = _Clock()
        router = StreamRouter(clock=clock, grace=100.0)
        source = _FakePublisher("source", max_age=None)
        router.attach(source)
        source.health(True)
        source.emit(FieldPath.LOCKED, True, observed_at=0.0)

        clock.now = 10.0
        source.health(False)
        clock.now = 50.0
        source.health(True)
        source.emit(FieldPath.LOCKED, True, observed_at=50.0)
        clock.now = 60.0
        source.health(False)

        # Anchored to the second loss, not the first.
        clock.now = 159.0
        self.assertTrue(router.is_available(FieldPath.LOCKED))
        clock.now = 161.0
        self.assertFalse(router.is_available(FieldPath.LOCKED))

    def test_expired_observation_is_rejected_and_yields_to_a_fresh_source(self) -> None:
        clock = _Clock()
        router = StreamRouter(clock=clock)
        aged = _FakePublisher("aged", priority=PRIORITY_STREAM, max_age=60.0)
        fresh = _FakePublisher("fresh", priority=PRIORITY_BROADCAST, max_age=60.0)
        router.attach(aged)
        router.attach(fresh)
        aged.health(True)
        fresh.health(True)

        recorder = _Recorder()
        router.listen(FieldPath.LOCKED, recorder.on_value)
        aged.emit(FieldPath.LOCKED, True, observed_at=0.0)
        self.assertEqual(recorder.values, [True])

        # Past its max age the preferred source is no longer a candidate.
        clock.now = 100.0
        fresh.emit(FieldPath.LOCKED, False, observed_at=100.0)
        self.assertEqual(recorder.values, [True, False])

    def test_out_of_order_observation_is_ignored(self) -> None:
        clock = _Clock()
        router = StreamRouter(clock=clock)
        stream = _FakePublisher("stream")
        router.attach(stream)
        stream.health(True)

        recorder = _Recorder()
        router.listen(FieldPath.LOCKED, recorder.on_value)
        stream.emit(FieldPath.LOCKED, True, observed_at=10.0)
        stream.emit(FieldPath.LOCKED, False, observed_at=5.0)
        self.assertEqual(recorder.values, [True])


class TestActivation(TestCase):
    def test_first_listener_activates_and_last_releases_exactly_once(self) -> None:
        router = StreamRouter(clock=_Clock())
        stream = _FakePublisher("stream")
        router.attach(stream)
        self.assertEqual(stream.requested, [])

        first = router.listen(FieldPath.LOCKED, lambda _: None)
        self.assertEqual(stream.requested, [frozenset({FieldPath.LOCKED})])

        second = router.listen(FieldPath.LOCKED, lambda _: None)
        self.assertEqual(len(stream.requested), 1)

        first()
        self.assertEqual(stream.released, [])

        second()
        self.assertEqual(stream.released, [frozenset({FieldPath.LOCKED})])

        # Unsubscribing again must not release a second time.
        second()
        first()
        self.assertEqual(len(stream.released), 1)

    def test_activation_is_per_path(self) -> None:
        router = StreamRouter(clock=_Clock())
        stream = _FakePublisher("stream")
        router.attach(stream)
        router.listen(FieldPath.LOCKED, lambda _: None)
        router.listen(FieldPath.CHARGE_PORT_DOOR_OPEN, lambda _: None)
        self.assertEqual(
            stream.requested,
            [
                frozenset({FieldPath.LOCKED}),
                frozenset({FieldPath.CHARGE_PORT_DOOR_OPEN}),
            ],
        )

    def test_publisher_attached_later_is_asked_for_already_active_paths(self) -> None:
        router = StreamRouter(clock=_Clock())
        router.listen(FieldPath.LOCKED, lambda _: None)
        stream = _FakePublisher("stream")
        detach = router.attach(stream)
        self.assertEqual(stream.requested, [frozenset({FieldPath.LOCKED})])

        detach()
        self.assertEqual(stream.released, [frozenset({FieldPath.LOCKED})])
        self.assertEqual(stream.detached, 1)

    def test_detaching_the_selected_source_reselects_without_emitting_none(
        self,
    ) -> None:
        clock = _Clock()
        router = StreamRouter(clock=clock)
        stream = _FakePublisher("stream", priority=PRIORITY_STREAM)
        standby = _FakePublisher("standby", priority=PRIORITY_BROADCAST)
        detach_stream = router.attach(stream)
        router.attach(standby)
        stream.health(True)
        standby.health(True)

        recorder = _Recorder()
        router.listen(FieldPath.LOCKED, recorder.on_value)
        stream.emit(FieldPath.LOCKED, True, observed_at=0.0)
        standby.emit(FieldPath.LOCKED, False, observed_at=0.0)

        detach_stream()
        self.assertEqual(recorder.values, [True, False])
        self.assertNotIn(None, recorder.values)

    def test_attaching_a_duplicate_source_id_is_rejected(self) -> None:
        router = StreamRouter(clock=_Clock())
        router.attach(_FakePublisher("stream"))
        with self.assertRaises(ValueError):
            router.attach(_FakePublisher("stream"))

    def test_a_detached_publisher_can_no_longer_feed_the_router(self) -> None:
        clock = _Clock()
        router = StreamRouter(clock=clock)
        stream = _FakePublisher("stream")
        sink_holder: list[PublisherSink] = []

        original_attach = stream.attach

        def capture(sink: PublisherSink) -> Unsubscribe:
            sink_holder.append(sink)
            return original_attach(sink)

        stream.attach = capture  # type: ignore[method-assign]
        detach = router.attach(stream)
        stream.health(True)
        recorder = _Recorder()
        router.listen(FieldPath.LOCKED, recorder.on_value)
        detach()

        sink_holder[0].publish(
            Observation(
                path=FieldPath.LOCKED,
                value=True,
                observed_at=0.0,
                source_id="stream",
            )
        )
        self.assertEqual(recorder.values, [])

    def test_releasing_one_availability_registration_twice_keeps_the_other(
        self,
    ) -> None:
        """Two registrations of one callback are two subscriptions, not one."""
        router = StreamRouter()
        source = _FakePublisher("source")
        router.attach(source)
        recorder = _Recorder()
        first = router.listen_availability(FieldPath.LOCKED, recorder.on_availability)
        router.listen_availability(FieldPath.LOCKED, recorder.on_availability)
        self.assertEqual(recorder.availability, [False, False])

        first()
        first()

        source.health(True)
        source.emit(FieldPath.LOCKED, True, observed_at=0.0)
        self.assertEqual(recorder.availability, [False, False, True])

    def test_a_callback_that_publishes_leaves_no_listener_on_the_old_value(
        self,
    ) -> None:
        """A nested update supersedes the one being delivered.

        Without that, the outer dispatch carries on handing the superseded
        value to the listeners it had not reached yet, and they are left
        holding a value the router itself no longer holds.
        """
        router = StreamRouter()
        source = _FakePublisher("source")
        router.attach(source)
        source.health(True)

        first: list[bool] = []
        second: list[bool] = []

        def on_first(value: bool) -> None:
            first.append(value)
            if value is True:
                source.emit(FieldPath.LOCKED, False, observed_at=2.0)

        router.listen(FieldPath.LOCKED, on_first)
        router.listen(FieldPath.LOCKED, second.append)

        source.emit(FieldPath.LOCKED, True, observed_at=1.0)

        self.assertIs(router.value(FieldPath.LOCKED), False)
        self.assertEqual(first, [True, False])
        self.assertEqual(second, [False])

    def test_a_listener_exception_does_not_stop_later_listeners(self) -> None:
        router = StreamRouter(clock=_Clock())
        stream = _FakePublisher("stream")
        router.attach(stream)
        stream.health(True)
        seen: list[bool] = []

        def boom(_: bool) -> None:
            raise RuntimeError("listener blew up")

        router.listen(FieldPath.LOCKED, boom)
        router.listen(FieldPath.LOCKED, seen.append)
        with self.assertLogs("tesla_fleet_api", level="ERROR"):
            stream.emit(FieldPath.LOCKED, True, observed_at=0.0)
        self.assertEqual(seen, [True])


class TestDemand(TestCase):
    def test_demand_reports_initial_state_then_only_aggregate_edges(self) -> None:
        router = StreamRouter(clock=_Clock())
        seen: list[bool] = []
        router.listen_demand(ALL_PATHS, seen.append)
        self.assertEqual(seen, [False])

        locked = router.listen(FieldPath.LOCKED, lambda _: None)
        self.assertEqual(seen, [False, True])

        # A second path in the same set is not a new edge.
        port = router.listen(FieldPath.CHARGE_PORT_DOOR_OPEN, lambda _: None)
        trunk = router.listen(FieldPath.DOOR_STATE_TRUNK_FRONT, lambda _: None)
        self.assertEqual(seen, [False, True])

        locked()
        port()
        self.assertEqual(seen, [False, True])

        # Only when every path in the set is back to zero.
        trunk()
        self.assertEqual(seen, [False, True, False])

    def test_demand_starts_true_when_a_listener_already_exists(self) -> None:
        router = StreamRouter(clock=_Clock())
        router.listen(FieldPath.LOCKED, lambda _: None)
        seen: list[bool] = []
        router.listen_demand(ALL_PATHS, seen.append)
        self.assertEqual(seen, [True])

    def test_demand_unsubscribe_removes_only_that_observer(self) -> None:
        router = StreamRouter(clock=_Clock())
        first: list[bool] = []
        second: list[bool] = []
        unsubscribe = router.listen_demand(ALL_PATHS, first.append)
        router.listen_demand(ALL_PATHS, second.append)
        unsubscribe()
        router.listen(FieldPath.LOCKED, lambda _: None)
        self.assertEqual(first, [False])
        self.assertEqual(second, [False, True])


class TestRouterCannotOriginateWork(TestCase):
    """The load-bearing invariant: the router is structurally unable to poll.

    Asserted against the module's own syntax tree rather than its behaviour,
    because a request path that exists but is merely unused would still be a
    request path.
    """

    @classmethod
    def setUpClass(cls) -> None:
        import tesla_fleet_api.router.stream as module

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
