"""Tests for VehicleDataResultPublisher: audited leaves, and no way to fetch.

Every result here is a literal dictionary written in the test. The publisher is
given no client, session, or callable, so a value it produces can only have come
from that literal - which is what makes the "cannot request" claim checkable
rather than asserted.
"""

from __future__ import annotations

import inspect
from typing import Any
from unittest import TestCase

from tesla_fleet_api.router import (
    FieldPath,
    Observation,
    StreamRouter,
    VehicleDataResultPublisher,
)

# A trimmed but structurally real vehicle_data response.
RESULT: dict[str, Any] = {
    "response": {
        "id": 1234567890,
        "vin": "5YJXCAE43LF123456",
        "state": "online",
        "charge_state": {
            "battery_level": 72,
            "charge_port_door_open": True,
            "charge_port_latch": "Engaged",
        },
        "climate_state": {"inside_temp": 21.5},
        "vehicle_state": {
            "locked": True,
            "ft": 0,
            "rt": 0,
            "df": 0,
            "car_version": "2025.14.3",
        },
    }
}


class _Clock:
    def __init__(self, now: float = 0.0) -> None:
        self.now = now

    def __call__(self) -> float:
        return self.now


class _Sink:
    def __init__(self) -> None:
        self.observations: list[Observation] = []
        self.health: list[tuple[str, bool]] = []

    def publish(self, observation: Observation) -> None:
        self.observations.append(observation)

    def set_health(self, source_id: str, healthy: bool) -> None:
        self.health.append((source_id, healthy))


def _translate(result: dict[str, Any]) -> dict[FieldPath, bool]:
    publisher = VehicleDataResultPublisher(clock=_Clock())
    return {o.path: o.value for o in publisher.publish_result(result)}


class TestAuditedLeaves(TestCase):
    def test_maps_exactly_the_three_audited_leaves(self) -> None:
        self.assertEqual(
            _translate(RESULT),
            {
                FieldPath.LOCKED: True,
                FieldPath.CHARGE_PORT_DOOR_OPEN: True,
                FieldPath.DOOR_STATE_TRUNK_FRONT: False,
            },
        )

    def test_a_bare_response_body_is_accepted(self) -> None:
        self.assertEqual(_translate(RESULT["response"]), _translate(RESULT))

    def test_absent_leaves_emit_no_observation(self) -> None:
        self.assertEqual(_translate({"response": {}}), {})
        self.assertEqual(
            _translate({"response": {"vehicle_state": {}, "charge_state": {}}}), {}
        )

    def test_a_null_leaf_emits_no_observation(self) -> None:
        result = {"response": {"vehicle_state": {"locked": None, "ft": None}}}
        self.assertEqual(_translate(result), {})

    def test_a_non_boolean_locked_emits_no_observation(self) -> None:
        result = {"response": {"vehicle_state": {"locked": "true"}}}
        self.assertEqual(_translate(result), {})

    def test_front_trunk_maps_only_the_documented_codes(self) -> None:
        for code, expected in ((0, False), (1, True)):
            result = {"response": {"vehicle_state": {"ft": code}}}
            self.assertEqual(
                _translate(result), {FieldPath.DOOR_STATE_TRUNK_FRONT: expected}
            )

        for code in (2, 3, 255, -1):
            result = {"response": {"vehicle_state": {"ft": code}}}
            self.assertEqual(_translate(result), {}, msg=f"ft={code}")

    def test_a_boolean_front_trunk_is_not_read_as_a_code(self) -> None:
        """``False == 0`` in Python; the wire code and a bool are not the same fact."""
        result = {"response": {"vehicle_state": {"ft": False}}}
        self.assertEqual(_translate(result), {})

    def test_unaudited_leaves_are_never_routed(self) -> None:
        """A present, easily flattened leaf is still not a routable field."""
        observations = VehicleDataResultPublisher(clock=_Clock()).publish_result(RESULT)
        self.assertEqual({o.path for o in observations}, set(FieldPath))

    def test_a_malformed_result_is_ignored_rather_than_guessed(self) -> None:
        self.assertEqual(_translate({}), {})
        self.assertEqual(_translate({"response": None}), {})
        self.assertEqual(_translate({"response": "unavailable"}), {})
        self.assertEqual(_translate({"response": {"vehicle_state": []}}), {})


class TestSuppliedResultRouting(TestCase):
    def test_a_supplied_result_reaches_listeners_through_arbitration(self) -> None:
        clock = _Clock()
        router = StreamRouter(clock=clock)
        publisher = VehicleDataResultPublisher(clock=clock)
        router.attach(publisher)

        seen: list[Any] = []
        router.listen(FieldPath.LOCKED, seen.append)
        publisher.publish_result(RESULT)

        self.assertEqual(seen, [True])
        self.assertIs(router.value(FieldPath.LOCKED), True)
        self.assertTrue(router.is_available(FieldPath.LOCKED))

    def test_a_supplied_result_expires_and_schedules_no_refresh(self) -> None:
        clock = _Clock()
        router = StreamRouter(clock=clock, grace=0.0)
        publisher = VehicleDataResultPublisher(clock=clock, max_age=60.0)
        router.attach(publisher)
        router.listen(FieldPath.LOCKED, lambda _: None)

        publisher.publish_result(RESULT)
        clock.now = 30.0
        self.assertTrue(router.is_available(FieldPath.LOCKED))

        clock.now = 120.0
        self.assertFalse(router.is_available(FieldPath.LOCKED))
        # Expiry retains the last known value and originates nothing.
        self.assertIs(router.value(FieldPath.LOCKED), True)

    def test_activation_asks_a_passive_source_for_nothing(self) -> None:
        router = StreamRouter(clock=_Clock())
        publisher = VehicleDataResultPublisher(clock=_Clock())
        router.attach(publisher)
        sink = _Sink()
        publisher.attach(sink)

        unsubscribe = router.listen(FieldPath.LOCKED, lambda _: None)
        unsubscribe()
        # A request/release round trip produced no observation of its own.
        self.assertEqual(sink.observations, [])

    def test_publishing_before_attach_translates_but_reaches_no_listener(self) -> None:
        router = StreamRouter(clock=_Clock())
        publisher = VehicleDataResultPublisher(clock=_Clock())
        seen: list[Any] = []
        router.listen(FieldPath.LOCKED, seen.append)

        self.assertEqual(len(publisher.publish_result(RESULT)), 3)
        self.assertEqual(seen, [])


class TestPublisherCannotRequestData(TestCase):
    """The publisher's only data source is the dictionary handed to it."""

    def test_it_exposes_no_coroutine_and_no_awaitable_member(self) -> None:
        publisher = VehicleDataResultPublisher(clock=_Clock())
        for name, member in inspect.getmembers(publisher):
            self.assertFalse(
                inspect.iscoroutinefunction(member),
                msg=f"{name} is a coroutine function",
            )
            self.assertFalse(inspect.isawaitable(member), msg=f"{name} is awaitable")

    def test_it_holds_no_client_session_or_fetch_callable(self) -> None:
        publisher = VehicleDataResultPublisher(clock=_Clock())
        held = {
            name: value
            for name, value in vars(publisher).items()
            if name not in ("_clock", "_sink", "_capabilities")
        }
        self.assertEqual(held, {"source_id": "vehicle-data", "priority": 40})

        # The clock is the only callable it keeps, and it takes no arguments.
        self.assertEqual(
            list(inspect.signature(publisher._clock).parameters),  # type: ignore[attr-defined]
            [],
        )

    def test_it_yields_nothing_when_no_result_is_supplied(self) -> None:
        """With the fake input withheld there is no other source to fall back on."""
        clock = _Clock()
        router = StreamRouter(clock=clock)
        publisher = VehicleDataResultPublisher(clock=clock)
        router.attach(publisher)

        seen: list[Any] = []
        router.listen(FieldPath.LOCKED, seen.append)
        router.listen(FieldPath.CHARGE_PORT_DOOR_OPEN, seen.append)
        router.listen(FieldPath.DOOR_STATE_TRUNK_FRONT, seen.append)

        clock.now = 10_000.0
        self.assertEqual(seen, [])
        for path in FieldPath:
            self.assertIsNone(router.value(path))
            self.assertFalse(router.is_available(path))

    def test_an_object_that_could_fetch_is_never_called(self) -> None:
        """A result-shaped mapping whose lookups are counted proves the reads."""
        calls: list[str] = []

        class _Tripwire(dict[str, Any]):
            def __getitem__(self, key: str) -> Any:
                calls.append(key)
                return super().__getitem__(key)

            def fetch(self) -> None:  # pragma: no cover - must never be reached
                raise AssertionError("the publisher invoked a fetch callable")

        publisher = VehicleDataResultPublisher(clock=_Clock())
        publisher.publish_result(_Tripwire(RESULT))
        self.assertEqual(calls, ["response"])
