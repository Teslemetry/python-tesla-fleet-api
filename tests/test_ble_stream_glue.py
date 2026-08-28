"""Tests for BleBroadcastStreamGlue over a real VehicleBluetooth's listener seams.

Broadcasts are injected through ``vehicle._on_message``, the same routing path
the vehicle uses in production, matching ``test_funnel_bluetooth.py``. No BLE
connection, GATT traffic, or event loop is involved.
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
    FromVCSECMessage,
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


class _FakeSink:
    """A minimal stand-in satisfying the structural ``StreamSink`` contract."""

    def __init__(self) -> None:
        self.calls: list[tuple[Mapping[str, Any], Mapping[str, Any] | None]] = []

    def ingest(
        self, data: Mapping[str, Any], metadata: Mapping[str, Any] | None = None
    ) -> Mapping[str, Any]:
        self.calls.append((data, metadata))
        return data


class TestLockStateTranslation(TestCase):
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
                sink.calls,
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
                sink.calls,
                [({"Locked": False}, {"source": "bluetooth", "raw": name})],
            )


class TestClosureTranslation(TestCase):
    def test_charge_port_closure_states_ingest_booleans(self) -> None:
        vehicle = _make_vehicle()
        sink = _FakeSink()
        BleBroadcastStreamGlue(vehicle, sink)

        for state, expected in (
            (ClosureState_E.CLOSURESTATE_CLOSED, False),
            (ClosureState_E.CLOSURESTATE_OPEN, True),
            (ClosureState_E.CLOSURESTATE_AJAR, True),
            (ClosureState_E.CLOSURESTATE_OPENING, True),
            (ClosureState_E.CLOSURESTATE_CLOSING, True),
        ):
            sink.calls.clear()
            vehicle._on_message(_closures(chargePort=state))
            # Every status broadcast also reports vehicleLockState (UNLOCKED
            # is 0 with no proto3 presence), so a Locked call rides along.
            charge_port_calls = [c for c in sink.calls if "ChargePortDoorOpen" in c[0]]
            self.assertEqual(
                charge_port_calls,
                [
                    (
                        {"ChargePortDoorOpen": expected},
                        {
                            "source": "bluetooth",
                            "raw": ClosureState_E.Name(state),
                        },
                    )
                ],
            )

    def test_front_trunk_closure_states_ingest_nested_door_state(self) -> None:
        vehicle = _make_vehicle()
        sink = _FakeSink()
        BleBroadcastStreamGlue(vehicle, sink)

        vehicle._on_message(_closures(frontTrunk=ClosureState_E.CLOSURESTATE_OPEN))

        trunk_calls = [c for c in sink.calls if "DoorState" in c[0]]
        self.assertEqual(
            trunk_calls,
            [
                (
                    {"DoorState": {"TrunkFront": True}},
                    {
                        "source": "bluetooth",
                        "raw": "CLOSURESTATE_OPEN",
                    },
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
            vehicle._on_message(_closures(chargePort=state, frontTrunk=state))

        closure_calls = [
            c for c in sink.calls if "ChargePortDoorOpen" in c[0] or "DoorState" in c[0]
        ]
        self.assertEqual(closure_calls, [])

    def test_a_broadcast_without_closures_emits_no_closure_call(self) -> None:
        """Closures have proto3 presence, so an absent submessage says nothing."""
        vehicle = _make_vehicle()
        sink = _FakeSink()
        BleBroadcastStreamGlue(vehicle, sink)

        vehicle._on_message(_lock(VehicleLockState_E.VEHICLELOCKSTATE_LOCKED))

        # Only the lock-state call, none for charge port or front trunk.
        self.assertEqual(len(sink.calls), 1)
        self.assertEqual(sink.calls[0][0], {"Locked": True})


class TestLifecycle(TestCase):
    def test_stop_unsubscribes_every_listener(self) -> None:
        vehicle = _make_vehicle()
        sink = _FakeSink()
        glue = BleBroadcastStreamGlue(vehicle, sink)

        glue.stop()
        vehicle._on_message(_lock(VehicleLockState_E.VEHICLELOCKSTATE_LOCKED))
        vehicle._on_message(_closures(chargePort=ClosureState_E.CLOSURESTATE_OPEN))
        vehicle._on_message(_closures(frontTrunk=ClosureState_E.CLOSURESTATE_OPEN))

        self.assertEqual(sink.calls, [])

    def test_stop_is_idempotent(self) -> None:
        vehicle = _make_vehicle()
        sink = _FakeSink()
        glue = BleBroadcastStreamGlue(vehicle, sink)

        glue.stop()
        glue.stop()  # must not raise

    def test_only_registers_the_three_broadcast_listeners(self) -> None:
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

        self.assertEqual(len(sink.calls), 1)
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
