"""Tests for TeslemetryStreamPublisher: signal-update translation, and no way to fetch.

Every update here is a literal dictionary written in the test. The publisher is
given no client, session, or callable, so a value it produces can only have come
from that literal - which is what makes the "cannot request" claim checkable
rather than asserted.
"""

from __future__ import annotations

import inspect
from typing import Any
from unittest import TestCase
from unittest.mock import AsyncMock, MagicMock

from cryptography.hazmat.primitives.asymmetric import ec

from tesla_fleet_api.funnel import (
    BleBroadcastPublisher,
    FieldPath,
    ObservationFunnel,
    TeslemetryStreamPublisher,
    Value,
)
from tesla_fleet_api.tesla.vehicle.bluetooth import VehicleBluetooth
from tesla_protocol.command.universal_message_pb2 import (
    Destination,
    Domain,
    RoutableMessage,
)
from tesla_protocol.command.vcsec_pb2 import (
    FromVCSECMessage,
    VehicleLockState_E,
    VehicleStatus,
)

# A trimmed but structurally real Teslemetry stream ``data`` push.
UPDATE: dict[str, Any] = {
    "Locked": True,
    "ChargePortDoorOpen": True,
    "DoorState": {
        "DriverFront": False,
        "TrunkFront": False,
        "TrunkRear": False,
    },
    "Soc": 72,
}


class _Clock:
    def __init__(self, now: float = 0.0) -> None:
        self.now = now

    def __call__(self) -> float:
        return self.now


def _translate(data: dict[str, Any]) -> dict[FieldPath, Value]:
    publisher = TeslemetryStreamPublisher(clock=_Clock())
    return {o.path: o.value for o in publisher.publish_update(data)}


class TestSignalTranslation(TestCase):
    def test_maps_exactly_the_three_audited_signals(self) -> None:
        self.assertEqual(
            _translate(UPDATE),
            {
                FieldPath.LOCKED: True,
                FieldPath.CHARGE_PORT_DOOR_OPEN: True,
                FieldPath.DOOR_STATE_TRUNK_FRONT: False,
            },
        )

    def test_absent_signals_emit_no_observation(self) -> None:
        self.assertEqual(_translate({"Soc": 72}), {})

    def test_a_null_signal_is_an_explicit_unavailable_reading(self) -> None:
        self.assertEqual(
            _translate(
                {
                    "Locked": None,
                    "ChargePortDoorOpen": None,
                    "DoorState": None,
                }
            ),
            {
                FieldPath.LOCKED: None,
                FieldPath.CHARGE_PORT_DOOR_OPEN: None,
                FieldPath.DOOR_STATE_TRUNK_FRONT: None,
            },
        )

    def test_string_encoded_booleans_are_coerced(self) -> None:
        """Some vehicles stream 'true'/'false' strings instead of JSON booleans."""
        self.assertEqual(
            _translate(
                {
                    "Locked": "true",
                    "ChargePortDoorOpen": "false",
                    "DoorState": {"TrunkFront": "true"},
                }
            ),
            {
                FieldPath.LOCKED: True,
                FieldPath.CHARGE_PORT_DOOR_OPEN: False,
                FieldPath.DOOR_STATE_TRUNK_FRONT: True,
            },
        )

    def test_a_non_boolean_locked_emits_no_observation(self) -> None:
        self.assertEqual(_translate({"Locked": "unlocked"}), {})

    def test_a_partial_door_state_only_reports_trunk_front_when_present(self) -> None:
        self.assertEqual(
            _translate({"DoorState": {"DriverFront": True}}),
            {},
        )

    def test_a_malformed_door_state_is_ignored_rather_than_guessed(self) -> None:
        self.assertEqual(_translate({"DoorState": "open"}), {})

    def test_unaudited_signals_are_never_routed(self) -> None:
        self.assertEqual(_translate({"Soc": 72, "ChargerVoltage": 240.0}), {})


class TestSuppliedUpdateFunnelling(TestCase):
    def test_a_supplied_update_reaches_listeners(self) -> None:
        funnel = ObservationFunnel()
        publisher = TeslemetryStreamPublisher(clock=_Clock())
        funnel.attach(publisher)

        seen: dict[FieldPath, list[Value]] = {path: [] for path in FieldPath}
        for path in FieldPath:
            funnel.listen(path, seen[path].append)

        publisher.publish_update(UPDATE, observed_at=1.0)

        self.assertEqual(
            seen,
            {
                FieldPath.LOCKED: [True],
                FieldPath.CHARGE_PORT_DOOR_OPEN: [True],
                FieldPath.DOOR_STATE_TRUNK_FRONT: [False],
            },
        )

    def test_a_repeated_update_is_not_re_dispatched(self) -> None:
        funnel = ObservationFunnel()
        publisher = TeslemetryStreamPublisher(clock=_Clock())
        funnel.attach(publisher)

        seen: list[Value] = []
        funnel.listen(FieldPath.LOCKED, seen.append)

        publisher.publish_update(UPDATE, observed_at=1.0)
        publisher.publish_update(UPDATE, observed_at=2.0)

        self.assertEqual(seen, [True])

    def test_a_partial_update_leaves_other_fields_untouched(self) -> None:
        """A stream push carrying only one changed signal doesn't blank the rest."""
        funnel = ObservationFunnel()
        publisher = TeslemetryStreamPublisher(clock=_Clock())
        funnel.attach(publisher)

        seen: dict[FieldPath, list[Value]] = {path: [] for path in FieldPath}
        for path in FieldPath:
            funnel.listen(path, seen[path].append)

        publisher.publish_update(UPDATE, observed_at=1.0)
        publisher.publish_update({"Locked": False}, observed_at=2.0)

        self.assertEqual(seen[FieldPath.LOCKED], [True, False])
        self.assertEqual(seen[FieldPath.CHARGE_PORT_DOOR_OPEN], [True])
        self.assertEqual(seen[FieldPath.DOOR_STATE_TRUNK_FRONT], [False])

    def test_activation_subscribes_a_passive_source_to_nothing(self) -> None:
        funnel = ObservationFunnel()
        publisher = TeslemetryStreamPublisher(clock=_Clock())
        funnel.attach(publisher)
        before = dict(vars(publisher))

        release = funnel.listen(FieldPath.LOCKED, lambda _: None)
        release()

        self.assertEqual(vars(publisher), before)

    def test_publishing_before_attach_translates_but_reaches_no_listener(self) -> None:
        funnel = ObservationFunnel()
        publisher = TeslemetryStreamPublisher(clock=_Clock())

        seen: list[Value] = []
        funnel.listen(FieldPath.LOCKED, seen.append)
        observations = publisher.publish_update(UPDATE, observed_at=1.0)

        self.assertEqual(len(observations), 3)
        self.assertEqual(seen, [])


class TestPublisherCannotRequestData(TestCase):
    """The publisher's only data source is the mapping handed to it."""

    def test_it_exposes_no_coroutine_and_no_awaitable_member(self) -> None:
        publisher = TeslemetryStreamPublisher(clock=_Clock())
        for name, member in inspect.getmembers(publisher):
            self.assertFalse(
                inspect.iscoroutinefunction(member),
                msg=f"{name} is a coroutine function",
            )
            self.assertFalse(inspect.isawaitable(member), msg=f"{name} is awaitable")

    def test_it_holds_no_client_session_or_fetch_callable(self) -> None:
        publisher = TeslemetryStreamPublisher(clock=_Clock())
        self.assertEqual(set(vars(publisher)), {"_clock", "_sink"})

        self.assertEqual(
            list(inspect.signature(publisher._clock).parameters),  # type: ignore[attr-defined]
            [],
        )

    def test_it_yields_nothing_when_no_update_is_supplied(self) -> None:
        clock = _Clock()
        funnel = ObservationFunnel()
        publisher = TeslemetryStreamPublisher(clock=clock)
        funnel.attach(publisher)

        seen: list[Value] = []
        for path in FieldPath:
            funnel.listen(path, seen.append)

        clock.now = 10_000.0
        self.assertEqual(seen, [])
        for path in FieldPath:
            self.assertIsNone(funnel.value(path))

    def test_an_object_that_could_fetch_is_never_called(self) -> None:
        """An update-shaped mapping whose lookups are counted proves the reads."""
        calls: list[str] = []

        class _Tripwire(dict[str, Any]):
            def __getitem__(self, key: str) -> Any:
                calls.append(key)
                return super().__getitem__(key)

            def fetch(self) -> None:  # pragma: no cover - must never be reached
                raise AssertionError("the publisher invoked a fetch callable")

        publisher = TeslemetryStreamPublisher(clock=_Clock())
        publisher.publish_update(_Tripwire(UPDATE))
        self.assertEqual(calls, ["Locked", "ChargePortDoorOpen", "DoorState"])


class TestRegressionWalkthrough(TestCase):
    """Bluetooth and streaming feed the same funnel; neither blanks the other.

    The captain's direction is that streaming is the primary source of truth
    and Bluetooth is opportunistic - here both publishers are attached to one
    funnel and each field keeps a value whichever source is producing, with
    no ranking between them.
    """

    def test_streaming_and_bluetooth_both_reach_the_same_listeners(self) -> None:
        parent = MagicMock()
        parent.private_key = ec.generate_private_key(ec.SECP256R1())
        vehicle: VehicleBluetooth[Any] = VehicleBluetooth(parent, "5YJXCAE43LF123456")
        vehicle.connect_if_needed = AsyncMock()  # type: ignore[method-assign]
        vehicle.connect = AsyncMock()  # type: ignore[method-assign]
        vehicle.client = MagicMock()
        vehicle.client.is_connected = True
        vehicle.client.write_gatt_char = AsyncMock()

        funnel = ObservationFunnel()
        funnel.attach(BleBroadcastPublisher(vehicle, clock=_Clock(100.0)))
        stream_publisher = TeslemetryStreamPublisher(clock=_Clock(0.0))
        funnel.attach(stream_publisher)

        seen: dict[FieldPath, list[Value]] = {path: [] for path in FieldPath}
        for path in FieldPath:
            funnel.listen(path, seen[path].append)

        stream_publisher.publish_update({"Locked": True}, observed_at=1.0)
        vehicle._on_message(
            RoutableMessage(
                from_destination=Destination(domain=Domain.DOMAIN_VEHICLE_SECURITY),
                protobuf_message_as_bytes=FromVCSECMessage(
                    vehicleStatus=VehicleStatus(
                        vehicleLockState=VehicleLockState_E.VEHICLELOCKSTATE_UNLOCKED
                    )
                ).SerializeToString(),
            )
        )

        self.assertEqual(seen[FieldPath.LOCKED], [True, False])
        self.assertIs(funnel.value(FieldPath.LOCKED), False)
