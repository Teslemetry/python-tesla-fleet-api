"""Tests for BleBroadcastStreamGlue over a real VehicleBluetooth's listener seams.

Broadcasts are injected through ``vehicle._on_message``, the same routing path
the vehicle uses in production, matching ``test_funnel_bluetooth.py``. No BLE
connection, GATT traffic, or event loop is involved.

Each mapping test cites the exact teslemetry-stream field name (a
``Signal`` value, or a ``DoorState`` dict leaf) the ingested payload targets,
verified against the installed ``teslemetry-stream`` 0.13.0 package's own
``TeslemetryStreamVehicle`` listener implementations - this module never
imports that package (see ``TestDuckTypedContract`` below), so the citation
is what keeps the mapping honest.
"""

from __future__ import annotations

import sys
import tomllib
from pathlib import Path
from typing import Any, Mapping
from unittest import TestCase
from unittest.mock import AsyncMock, MagicMock

from cryptography.hazmat.primitives.asymmetric import ec

from tesla_fleet_api.tesla.vehicle.bluetooth import VehicleBluetooth
from tesla_fleet_api.tesla.vehicle.stream_glue import BleBroadcastStreamGlue
from tesla_protocol.command.universal_message_pb2 import (
    Destination,
    Domain,
    RoutableMessage,
)
from tesla_protocol.command.vcsec_pb2 import (
    ClosureState_E,
    ClosureStatuses,
    DetailedClosureStatus,
    FromVCSECMessage,
    Gear_E,
    VehicleLockState_E,
    VehicleStatus,
)

VIN = "5YJXCAE43LF123456"
DOMAIN = Domain.DOMAIN_VEHICLE_SECURITY


def _make_vehicle() -> VehicleBluetooth[Any]:
    parent = MagicMock()
    parent.private_key = ec.generate_private_key(ec.SECP256R1())
    vehicle = VehicleBluetooth(parent, VIN)
    vehicle.connect_if_needed = AsyncMock()  # type: ignore[method-assign]
    vehicle.connect = AsyncMock()  # type: ignore[method-assign]
    vehicle.client = MagicMock()
    vehicle.client.is_connected = True
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


def _gear(state: Gear_E) -> RoutableMessage:
    return _broadcast(VehicleStatus(gear=state))


def _tonneau_percent(percent: int) -> RoutableMessage:
    return _broadcast(
        VehicleStatus(
            detailedClosureStatus=DetailedClosureStatus(tonneauPercentOpen=percent)
        )
    )


class _FakeSink:
    """A minimal stand-in satisfying the structural ``StreamSink`` contract."""

    def __init__(self) -> None:
        self.calls: list[tuple[Mapping[str, Any], Mapping[str, Any] | None]] = []

    def ingest(
        self, data: Mapping[str, Any], metadata: Mapping[str, Any] | None = None
    ) -> Mapping[str, Any]:
        self.calls.append((data, metadata))
        return data


def _calls_for(sink: _FakeSink, key: str) -> list[tuple[Mapping[str, Any], Any]]:
    """Calls whose top-level ``data`` carries ``key``.

    ``Gear`` fires on every broadcast (a scalar field with no proto3
    presence, like ``vehicleLockState``) and ``DoorState`` calls for
    different doors share the same top-level key, so most mapping tests
    isolate the field under test this way rather than asserting the exact
    call list.
    """
    return [c for c in sink.calls if key in c[0]]


def _door_state_calls(
    sink: _FakeSink, leaf: str
) -> list[tuple[Mapping[str, Any], Any]]:
    """``DoorState`` calls whose single leaf is ``leaf`` (e.g. ``"TrunkFront"``)."""
    return [c for c in sink.calls if "DoorState" in c[0] and leaf in c[0]["DoorState"]]


class TestLockStateTranslation(TestCase):
    """Targets ``Signal.LOCKED`` (``"Locked"``), consumed by ``listen_Locked``."""

    def test_locked_states_ingest_true_with_raw_metadata(self) -> None:
        vehicle = _make_vehicle()
        sink = _FakeSink()
        BleBroadcastStreamGlue(vehicle, sink)

        for state, name in (
            (VehicleLockState_E.VEHICLELOCKSTATE_LOCKED, "VEHICLELOCKSTATE_LOCKED"),
            (
                VehicleLockState_E.VEHICLELOCKSTATE_INTERNAL_LOCKED,
                "VEHICLELOCKSTATE_INTERNAL_LOCKED",
            ),
        ):
            sink.calls.clear()
            vehicle._on_message(_lock(state))
            self.assertEqual(
                _calls_for(sink, "Locked"),
                [({"Locked": True}, {"source": "bluetooth", "raw": name})],
            )

    def test_unlocked_states_ingest_false_with_raw_metadata(self) -> None:
        vehicle = _make_vehicle()
        sink = _FakeSink()
        BleBroadcastStreamGlue(vehicle, sink)

        for state, name in (
            (VehicleLockState_E.VEHICLELOCKSTATE_UNLOCKED, "VEHICLELOCKSTATE_UNLOCKED"),
            (
                VehicleLockState_E.VEHICLELOCKSTATE_SELECTIVE_UNLOCKED,
                "VEHICLELOCKSTATE_SELECTIVE_UNLOCKED",
            ),
        ):
            sink.calls.clear()
            vehicle._on_message(_lock(state))
            self.assertEqual(
                _calls_for(sink, "Locked"),
                [({"Locked": False}, {"source": "bluetooth", "raw": name})],
            )


class TestClosureTranslation(TestCase):
    """Targets ``Signal.CHARGE_PORT_DOOR_OPEN`` and the ``DoorState`` dict leaves."""

    def test_charge_port_closure_states_ingest_booleans(self) -> None:
        """``Signal.CHARGE_PORT_DOOR_OPEN`` (``"ChargePortDoorOpen"``)."""
        vehicle = _make_vehicle()
        sink = _FakeSink()
        BleBroadcastStreamGlue(vehicle, sink)

        for state, expected, name in (
            (ClosureState_E.CLOSURESTATE_CLOSED, False, "CLOSURESTATE_CLOSED"),
            (ClosureState_E.CLOSURESTATE_OPEN, True, "CLOSURESTATE_OPEN"),
            (ClosureState_E.CLOSURESTATE_AJAR, True, "CLOSURESTATE_AJAR"),
            (ClosureState_E.CLOSURESTATE_OPENING, True, "CLOSURESTATE_OPENING"),
            (ClosureState_E.CLOSURESTATE_CLOSING, True, "CLOSURESTATE_CLOSING"),
        ):
            sink.calls.clear()
            vehicle._on_message(_closures(chargePort=state))
            self.assertEqual(
                _calls_for(sink, "ChargePortDoorOpen"),
                [
                    (
                        {"ChargePortDoorOpen": expected},
                        {
                            "source": "bluetooth",
                            "raw": name,
                        },
                    )
                ],
            )

    def test_front_trunk_closure_states_ingest_nested_door_state(self) -> None:
        """``Signal.DOOR_STATE`` (``"DoorState"``), leaf ``"TrunkFront"``."""
        vehicle = _make_vehicle()
        sink = _FakeSink()
        BleBroadcastStreamGlue(vehicle, sink)

        vehicle._on_message(_closures(frontTrunk=ClosureState_E.CLOSURESTATE_OPEN))

        self.assertEqual(
            _door_state_calls(sink, "TrunkFront"),
            [
                (
                    {"DoorState": {"TrunkFront": True}},
                    {"source": "bluetooth", "raw": "CLOSURESTATE_OPEN"},
                )
            ],
        )

    def test_rear_trunk_closure_states_ingest_nested_door_state(self) -> None:
        """``Signal.DOOR_STATE`` (``"DoorState"``), leaf ``"TrunkRear"``."""
        vehicle = _make_vehicle()
        sink = _FakeSink()
        BleBroadcastStreamGlue(vehicle, sink)

        vehicle._on_message(_closures(rearTrunk=ClosureState_E.CLOSURESTATE_OPEN))

        self.assertEqual(
            _door_state_calls(sink, "TrunkRear"),
            [
                (
                    {"DoorState": {"TrunkRear": True}},
                    {"source": "bluetooth", "raw": "CLOSURESTATE_OPEN"},
                )
            ],
        )

    def test_the_four_side_doors_ingest_their_own_door_state_leaf(self) -> None:
        """``Signal.DOOR_STATE`` (``"DoorState"``) leaves for the 4 side doors.

        Field names match ``TeslemetryStreamVehicle.listen_FrontDriverDoor``
        etc., which read ``DriverFront``/``PassengerFront``/``DriverRear``/
        ``PassengerRear`` out of the same ``DoorState`` dict.
        """
        vehicle = _make_vehicle()
        sink = _FakeSink()
        BleBroadcastStreamGlue(vehicle, sink)

        for kwarg, leaf in (
            ("frontDriverDoor", "DriverFront"),
            ("frontPassengerDoor", "PassengerFront"),
            ("rearDriverDoor", "DriverRear"),
            ("rearPassengerDoor", "PassengerRear"),
        ):
            sink.calls.clear()
            vehicle._on_message(_closures(**{kwarg: ClosureState_E.CLOSURESTATE_OPEN}))
            self.assertEqual(
                _door_state_calls(sink, leaf),
                [
                    (
                        {"DoorState": {leaf: True}},
                        {"source": "bluetooth", "raw": "CLOSURESTATE_OPEN"},
                    )
                ],
            )

    def test_ambiguous_closure_states_emit_no_ingest_call(self) -> None:
        vehicle = _make_vehicle()
        sink = _FakeSink()
        BleBroadcastStreamGlue(vehicle, sink)

        for state in (
            ClosureState_E.CLOSURESTATE_UNKNOWN,
            ClosureState_E.CLOSURESTATE_FAILED_UNLATCH,
        ):
            sink.calls.clear()
            vehicle._on_message(_closures(chargePort=state, frontTrunk=state))

            self.assertEqual(_calls_for(sink, "ChargePortDoorOpen"), [])
            self.assertEqual(_door_state_calls(sink, "TrunkFront"), [])

    def test_a_broadcast_without_closures_emits_no_closure_call(self) -> None:
        """Closures have proto3 presence, so an absent submessage says nothing."""
        vehicle = _make_vehicle()
        sink = _FakeSink()
        BleBroadcastStreamGlue(vehicle, sink)

        vehicle._on_message(_lock(VehicleLockState_E.VEHICLELOCKSTATE_LOCKED))

        # Locked and Gear are scalar fields with no proto3 presence, so both
        # fire on every broadcast; nothing closure-shaped does.
        self.assertEqual(
            sink.calls,
            [
                (
                    {"Locked": True},
                    {"source": "bluetooth", "raw": "VEHICLELOCKSTATE_LOCKED"},
                ),
                (
                    {"Gear": "ShiftStateUnknown"},
                    {"source": "bluetooth", "raw": "GEAR_UNKNOWN"},
                ),
            ],
        )


class TestGearTranslation(TestCase):
    """Targets ``Signal.GEAR`` (``"Gear"``), consumed by ``listen_Gear``.

    The wire value is ``ShiftState``-prefixed
    (``TeslemetryEnum(prefix="ShiftState", options=[...])``); the package's
    own listener strips the prefix via ``ShiftState.get()`` before handing a
    caller the bare ``"P"``/``"D"``/``"R"``/``"N"``/``"Unknown"``.
    """

    def test_mapped_gears_ingest_shift_state_prefixed_strings(self) -> None:
        vehicle = _make_vehicle()
        sink = _FakeSink()
        BleBroadcastStreamGlue(vehicle, sink)

        for state, expected, name in (
            (Gear_E.GEAR_UNKNOWN, "ShiftStateUnknown", "GEAR_UNKNOWN"),
            (Gear_E.GEAR_PARK, "ShiftStateP", "GEAR_PARK"),
            (Gear_E.GEAR_DRIVE, "ShiftStateD", "GEAR_DRIVE"),
            (Gear_E.GEAR_REVERSE, "ShiftStateR", "GEAR_REVERSE"),
            (Gear_E.GEAR_NEUTRAL, "ShiftStateN", "GEAR_NEUTRAL"),
        ):
            sink.calls.clear()
            vehicle._on_message(_gear(state))
            self.assertEqual(
                _calls_for(sink, "Gear"),
                [({"Gear": expected}, {"source": "bluetooth", "raw": name})],
            )


class TestTonneauTranslation(TestCase):
    """Targets ``Signal.TONNEAU_POSITION`` and ``Signal.TONNEAU_OPEN_PERCENT``."""

    def test_mapped_tonneau_closures_ingest_tonneau_position_strings(self) -> None:
        """``Signal.TONNEAU_POSITION`` (``"TonneauPosition"``).

        Its wire value is ``TonneauPositionState``-prefixed and only
        3-valued (``Closed``/``PartiallyOpen``/``FullyOpen``), coarser than
        VCSEC's ``ClosureState_E`` - only CLOSED/OPEN/AJAR translate
        unambiguously.
        """
        vehicle = _make_vehicle()
        sink = _FakeSink()
        BleBroadcastStreamGlue(vehicle, sink)

        for state, expected, name in (
            (
                ClosureState_E.CLOSURESTATE_CLOSED,
                "TonneauPositionStateClosed",
                "CLOSURESTATE_CLOSED",
            ),
            (
                ClosureState_E.CLOSURESTATE_OPEN,
                "TonneauPositionStateFullyOpen",
                "CLOSURESTATE_OPEN",
            ),
            (
                ClosureState_E.CLOSURESTATE_AJAR,
                "TonneauPositionStatePartiallyOpen",
                "CLOSURESTATE_AJAR",
            ),
        ):
            sink.calls.clear()
            vehicle._on_message(_closures(tonneau=state))
            self.assertEqual(
                _calls_for(sink, "TonneauPosition"),
                [
                    (
                        {"TonneauPosition": expected},
                        {"source": "bluetooth", "raw": name},
                    )
                ],
            )

    def test_unmapped_tonneau_closures_emit_no_ingest_call(self) -> None:
        vehicle = _make_vehicle()
        sink = _FakeSink()
        BleBroadcastStreamGlue(vehicle, sink)

        for state in (
            ClosureState_E.CLOSURESTATE_UNKNOWN,
            ClosureState_E.CLOSURESTATE_FAILED_UNLATCH,
            ClosureState_E.CLOSURESTATE_OPENING,
            ClosureState_E.CLOSURESTATE_CLOSING,
        ):
            sink.calls.clear()
            vehicle._on_message(_closures(tonneau=state))
            self.assertEqual(_calls_for(sink, "TonneauPosition"), [])

    def test_tonneau_percent_open_ingests_a_float(self) -> None:
        """``Signal.TONNEAU_OPEN_PERCENT`` (``"TonneauOpenPercent"``)."""
        vehicle = _make_vehicle()
        sink = _FakeSink()
        BleBroadcastStreamGlue(vehicle, sink)

        vehicle._on_message(_tonneau_percent(42))

        self.assertEqual(
            _calls_for(sink, "TonneauOpenPercent"),
            [({"TonneauOpenPercent": 42.0}, {"source": "bluetooth"})],
        )


class TestLifecycle(TestCase):
    def test_stop_unsubscribes_every_listener(self) -> None:
        vehicle = _make_vehicle()
        sink = _FakeSink()
        glue = BleBroadcastStreamGlue(vehicle, sink)

        glue.stop()
        vehicle._on_message(_lock(VehicleLockState_E.VEHICLELOCKSTATE_LOCKED))
        vehicle._on_message(_closures(chargePort=ClosureState_E.CLOSURESTATE_OPEN))
        vehicle._on_message(_closures(frontTrunk=ClosureState_E.CLOSURESTATE_OPEN))
        vehicle._on_message(_gear(Gear_E.GEAR_DRIVE))
        vehicle._on_message(_tonneau_percent(10))

        self.assertEqual(sink.calls, [])

    def test_stop_is_idempotent(self) -> None:
        vehicle = _make_vehicle()
        sink = _FakeSink()
        glue = BleBroadcastStreamGlue(vehicle, sink)

        glue.stop()
        glue.stop()  # must not raise

    def test_registering_does_not_touch_the_transport(self) -> None:
        """Registering (not stopping) must not touch the transport."""
        vehicle = _make_vehicle()
        sink = _FakeSink()
        BleBroadcastStreamGlue(vehicle, sink)

        vehicle.connect.assert_not_awaited()  # type: ignore[attr-defined]
        vehicle.connect_if_needed.assert_not_awaited()  # type: ignore[attr-defined]
        vehicle.client.write_gatt_char.assert_not_awaited()


class TestDuckTypedContract(TestCase):
    """Locks in the design's hard constraint: no import of teslemetry_stream."""

    def test_module_source_never_references_teslemetry_stream(self) -> None:
        self.assertNotIn("teslemetry_stream", sys.modules)
        vehicle = _make_vehicle()
        sink = MagicMock()
        glue = BleBroadcastStreamGlue(vehicle, sink)
        vehicle._on_message(_lock(VehicleLockState_E.VEHICLELOCKSTATE_LOCKED))
        glue.stop()

        self.assertNotIn("teslemetry_stream", sys.modules)

    def test_a_plain_object_with_ingest_satisfies_the_sink(self) -> None:
        """No base class, no registration - purely structural."""
        vehicle = _make_vehicle()

        class PlainSink:
            def __init__(self) -> None:
                self.calls: list[Any] = []

            def ingest(
                self, data: Mapping[str, Any], metadata: Mapping[str, Any] | None = None
            ) -> Mapping[str, Any]:
                self.calls.append((data, metadata))
                return data

        sink = PlainSink()
        glue = BleBroadcastStreamGlue(vehicle, sink)
        vehicle._on_message(_lock(VehicleLockState_E.VEHICLELOCKSTATE_LOCKED))

        # Locked and Gear both fire (two scalar fields with no proto3
        # presence), rather than just the one field this broadcast targets.
        self.assertEqual(len(sink.calls), 2)
        glue.stop()

    def test_zero_net_new_dependency(self) -> None:
        pyproject = Path(__file__).resolve().parent.parent / "pyproject.toml"
        with pyproject.open("rb") as f:
            data = tomllib.load(f)

        def _names(specs: list[str]) -> set[str]:
            return {
                spec.split(";")[0].split(">=")[0].split("==")[0].strip()
                for spec in specs
            }

        project = data["project"]
        dependency_names = _names(project.get("dependencies", []))
        for extra_deps in project.get("optional-dependencies", {}).values():
            dependency_names |= _names(extra_deps)
        for group_deps in data.get("dependency-groups", {}).values():
            dependency_names |= _names(
                dep for dep in group_deps if isinstance(dep, str)
            )
        source_names = set(data.get("tool", {}).get("uv", {}).get("sources", {}))

        self.assertNotIn("teslemetry-stream", dependency_names)
        self.assertNotIn("teslemetry_stream", dependency_names)
        self.assertNotIn("teslemetry-stream", source_names)
        self.assertNotIn("teslemetry_stream", source_names)
