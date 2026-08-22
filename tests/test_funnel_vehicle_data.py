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

from tesla_fleet_api.funnel import (
    FieldPath,
    ObservationFunnel,
    Value,
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


def _translate(result: dict[str, Any]) -> dict[FieldPath, Value]:
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
        self.assertEqual(
            _translate({"response": {"vehicle_state": {"car_version": "2025.14.3"}}}),
            {},
        )

    def test_a_null_leaf_is_an_explicit_unavailable_reading(self) -> None:
        """A null is the vehicle reporting the field unavailable, not silence."""
        self.assertEqual(
            _translate(
                {
                    "response": {
                        "vehicle_state": {"locked": None, "ft": None},
                        "charge_state": {"charge_port_door_open": None},
                    }
                }
            ),
            {
                FieldPath.LOCKED: None,
                FieldPath.CHARGE_PORT_DOOR_OPEN: None,
                FieldPath.DOOR_STATE_TRUNK_FRONT: None,
            },
        )

    def test_a_non_boolean_locked_emits_no_observation(self) -> None:
        self.assertEqual(
            _translate({"response": {"vehicle_state": {"locked": "true"}}}), {}
        )

    def test_front_trunk_maps_only_the_documented_codes(self) -> None:
        for code, expected in ((0, False), (1, True)):
            self.assertEqual(
                _translate({"response": {"vehicle_state": {"ft": code}}}),
                {FieldPath.DOOR_STATE_TRUNK_FRONT: expected},
            )
        for code in (2, 3, -1):
            self.assertEqual(
                _translate({"response": {"vehicle_state": {"ft": code}}}),
                {},
                msg=f"ft code {code}",
            )

    def test_a_boolean_front_trunk_is_not_read_as_a_code(self) -> None:
        self.assertEqual(_translate({"response": {"vehicle_state": {"ft": False}}}), {})

    def test_unaudited_leaves_are_never_routed(self) -> None:
        """No reflective flattening: a sibling closure leaf produces nothing."""
        self.assertEqual(
            _translate({"response": {"vehicle_state": {"rt": 1, "df": 1}}}), {}
        )

    def test_a_malformed_result_is_ignored_rather_than_guessed(self) -> None:
        for result in (
            {},
            {"response": None},
            {"response": {"vehicle_state": None}},
            {"response": {"vehicle_state": "locked"}},
        ):
            self.assertEqual(_translate(result), {}, msg=f"{result}")


class TestSuppliedResultFunnelling(TestCase):
    def test_a_supplied_result_reaches_listeners(self) -> None:
        funnel = ObservationFunnel()
        publisher = VehicleDataResultPublisher(clock=_Clock())
        funnel.attach(publisher)

        seen: dict[FieldPath, list[Value]] = {path: [] for path in FieldPath}
        for path in FieldPath:
            funnel.listen(path, seen[path].append)

        publisher.publish_result(RESULT, observed_at=1.0)

        self.assertEqual(
            seen,
            {
                FieldPath.LOCKED: [True],
                FieldPath.CHARGE_PORT_DOOR_OPEN: [True],
                FieldPath.DOOR_STATE_TRUNK_FRONT: [False],
            },
        )

    def test_a_repeated_result_is_not_re_dispatched(self) -> None:
        funnel = ObservationFunnel()
        publisher = VehicleDataResultPublisher(clock=_Clock())
        funnel.attach(publisher)

        seen: list[Value] = []
        funnel.listen(FieldPath.LOCKED, seen.append)

        publisher.publish_result(RESULT, observed_at=1.0)
        publisher.publish_result(RESULT, observed_at=2.0)

        self.assertEqual(seen, [True])

    def test_a_supplied_result_never_expires_by_itself(self) -> None:
        """Age is not a reading either: nothing here blanks a stale value."""
        clock = _Clock()
        funnel = ObservationFunnel()
        publisher = VehicleDataResultPublisher(clock=clock)
        funnel.attach(publisher)

        seen: list[Value] = []
        funnel.listen(FieldPath.LOCKED, seen.append)
        publisher.publish_result(RESULT)

        clock.now = 100_000.0
        self.assertEqual(seen, [True])
        self.assertIs(funnel.value(FieldPath.LOCKED), True)

    def test_activation_subscribes_a_passive_source_to_nothing(self) -> None:
        funnel = ObservationFunnel()
        publisher = VehicleDataResultPublisher(clock=_Clock())
        funnel.attach(publisher)
        before = dict(vars(publisher))

        release = funnel.listen(FieldPath.LOCKED, lambda _: None)
        release()

        self.assertEqual(vars(publisher), before)

    def test_publishing_before_attach_translates_but_reaches_no_listener(self) -> None:
        funnel = ObservationFunnel()
        publisher = VehicleDataResultPublisher(clock=_Clock())

        seen: list[Value] = []
        funnel.listen(FieldPath.LOCKED, seen.append)
        observations = publisher.publish_result(RESULT, observed_at=1.0)

        self.assertEqual(len(observations), 3)
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
        self.assertEqual(set(vars(publisher)), {"_clock", "_sink"})

        # The clock is the only callable it keeps, and it takes no arguments.
        self.assertEqual(
            list(inspect.signature(publisher._clock).parameters),  # type: ignore[attr-defined]
            [],
        )

    def test_it_yields_nothing_when_no_result_is_supplied(self) -> None:
        """With the fake input withheld there is no other source to fall back on."""
        clock = _Clock()
        funnel = ObservationFunnel()
        publisher = VehicleDataResultPublisher(clock=clock)
        funnel.attach(publisher)

        seen: list[Value] = []
        for path in FieldPath:
            funnel.listen(path, seen.append)

        clock.now = 10_000.0
        self.assertEqual(seen, [])
        for path in FieldPath:
            self.assertIsNone(funnel.value(path))

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
