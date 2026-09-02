"""Feeds BLE broadcasts into a stream-shaped ``ingest()`` sink.

``BleBroadcastStreamGlue`` wires the typed listeners in ``broadcast.py`` to a
duck-typed sink (structurally: python-teslemetry-stream's
``TeslemetryStream(Vehicle).ingest``) so a BLE observation reaches the same
listeners a native stream event does, translated into the identical
stream-shaped payload. This module never imports ``teslemetry_stream`` - the
sink contract below is a structural :class:`typing.Protocol`, matching the
duck-typed ``EnergySite`` composition :class:`~tesla_fleet_api.router.EnergySiteRouter`
already uses for aiopowerwall.

Every field wired here is verified against teslemetry-stream 0.13.0's actual
``TeslemetryStreamVehicle`` listener implementations, not guessed: ``Gear``
and ``TonneauPosition`` carry ``<Prefix><Option>``-shaped wire strings (e.g.
``"ShiftStateP"``, ``"TonneauPositionStateClosed"``) because that package's
own listeners strip the prefix again via its ``TeslemetryEnum.get()`` helper.
Three BLE-derivable fields are deliberately left unwired because the current
``ingest()`` API cannot carry them faithfully:

- Vehicle sleep status: ``ingest()`` unconditionally nests its payload under
  the ``data`` key of a wire event, the shape a *signal* update carries.
  Vehicle sleep status streams on the separate ``state`` topic
  (``online``/``offline``/``asleep``) that native stream events carry
  alongside, not inside, ``data`` - there is no ``ingest_state()`` or
  equivalent to target.
- User presence and UI desire: teslemetry-stream 0.13.0 has no ``Signal``
  entry or ``listen_*`` method for either today, so no wire field name exists
  yet to target.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Mapping, Protocol

from tesla_fleet_api.funnel import CLOSURE_STATES, LOCK_STATES
from tesla_fleet_api.tesla.vehicle.broadcast import Unsubscribe
from tesla_protocol.command.vcsec_pb2 import ClosureState_E, Gear_E, VehicleLockState_E

if TYPE_CHECKING:
    from tesla_fleet_api.tesla.vehicle.bluetooth import VehicleBluetooth


class StreamSink(Protocol):
    """Structurally identical to ``TeslemetryStream(Vehicle).ingest`` - not imported."""

    def ingest(
        self, data: Mapping[str, Any], metadata: Mapping[str, Any] | None = None
    ) -> Mapping[str, Any]: ...


# teslemetry-stream's listen_Gear reads a ShiftState-prefixed wire string and
# strips the prefix via TeslemetryEnum.get() - GEAR_UNKNOWN is VCSEC's
# always-present proto3 default (0), mirroring LOCK_STATES' treatment of
# VEHICLELOCKSTATE_UNLOCKED.
#
# These values stay hardcoded rather than derived from Gear_E's own
# descriptor names (GEAR_UNKNOWN/GEAR_PARK/GEAR_DRIVE/GEAR_REVERSE/
# GEAR_NEUTRAL): there is no total stripping rule from those names to the
# wire strings above - PARK/DRIVE/REVERSE/NEUTRAL each collapse to an
# unrelated single letter while UNKNOWN spells out in full - so any
# derivation would need a per-value special case anyway.
GEAR_STATES: Mapping[int, str] = {
    Gear_E.GEAR_UNKNOWN: "ShiftStateUnknown",
    Gear_E.GEAR_PARK: "ShiftStateP",
    Gear_E.GEAR_DRIVE: "ShiftStateD",
    Gear_E.GEAR_REVERSE: "ShiftStateR",
    Gear_E.GEAR_NEUTRAL: "ShiftStateN",
}

# TonneauPosition is a 3-option wire string (TonneauPositionState-prefixed),
# coarser than VCSEC's 7-value ClosureState_E. Only CLOSED/OPEN/AJAR translate
# unambiguously; OPENING/CLOSING/UNKNOWN/FAILED_UNLATCH are left unmapped,
# matching the CLOSURE_STATES UNKNOWN/FAILED_UNLATCH ruling in funnel.py.
#
# These values stay hardcoded rather than derived from ClosureState_E's own
# descriptor names (CLOSURESTATE_CLOSED/CLOSURESTATE_OPEN/CLOSURESTATE_AJAR):
# OPEN renames to "FullyOpen" and AJAR to "PartiallyOpen" on the wire, so no
# total stripping rule maps the descriptor name to the wire string.
TONNEAU_POSITION_STATES: Mapping[int, str] = {
    ClosureState_E.CLOSURESTATE_CLOSED: "TonneauPositionStateClosed",
    ClosureState_E.CLOSURESTATE_OPEN: "TonneauPositionStateFullyOpen",
    ClosureState_E.CLOSURESTATE_AJAR: "TonneauPositionStatePartiallyOpen",
}


class BleBroadcastStreamGlue:
    """Translates a :class:`VehicleBluetooth`'s broadcasts into ``sink.ingest()`` calls.

    Reuses the same lock/closure decode maps
    :class:`~tesla_fleet_api.funnel.BleBroadcastPublisher` does, so the "any
    unlocked state reads as unlocked" ruling and the deliberate
    UNKNOWN/FAILED_UNLATCH omission carry over unchanged. There is no source
    ranking here or in ``ingest()`` itself - every call reaches listeners in
    arrival order alongside whatever the sink's own stream connection reports.
    """

    def __init__(self, vehicle: "VehicleBluetooth[Any]", sink: StreamSink) -> None:
        self._sink = sink
        self._unsubs: list[Unsubscribe] = [
            vehicle.listen_vehicle_lock_state(self._on_lock_state),
            vehicle.listen_charge_port(self._on_charge_port),
            vehicle.listen_front_trunk(self._on_front_trunk),
            vehicle.listen_rear_trunk(self._on_rear_trunk),
            vehicle.listen_front_driver_door(self._on_front_driver_door),
            vehicle.listen_front_passenger_door(self._on_front_passenger_door),
            vehicle.listen_rear_driver_door(self._on_rear_driver_door),
            vehicle.listen_rear_passenger_door(self._on_rear_passenger_door),
            vehicle.listen_gear(self._on_gear),
            vehicle.listen_tonneau(self._on_tonneau),
            vehicle.listen_tonneau_percent_open(self._on_tonneau_percent_open),
        ]

    def stop(self) -> None:
        """Unsubscribe from every broadcast listener; safe to call more than once."""
        for unsub in self._unsubs:
            unsub()
        self._unsubs = []

    def _on_lock_state(self, raw: int) -> None:
        if raw not in LOCK_STATES:
            return
        self._sink.ingest(
            {"Locked": LOCK_STATES[raw]},
            {"source": "bluetooth", "raw": VehicleLockState_E.Name(raw)},
        )

    def _on_charge_port(self, raw: int) -> None:
        if raw not in CLOSURE_STATES:
            return
        self._sink.ingest(
            {"ChargePortDoorOpen": CLOSURE_STATES[raw]},
            {"source": "bluetooth", "raw": ClosureState_E.Name(raw)},
        )

    def _ingest_door_state(self, key: str, raw: int) -> None:
        """Ingest one leaf of the ``DoorState`` dict signal by its wire key."""
        if raw not in CLOSURE_STATES:
            return
        self._sink.ingest(
            {"DoorState": {key: CLOSURE_STATES[raw]}},
            {"source": "bluetooth", "raw": ClosureState_E.Name(raw)},
        )

    def _on_front_trunk(self, raw: int) -> None:
        self._ingest_door_state("TrunkFront", raw)

    def _on_rear_trunk(self, raw: int) -> None:
        self._ingest_door_state("TrunkRear", raw)

    def _on_front_driver_door(self, raw: int) -> None:
        self._ingest_door_state("DriverFront", raw)

    def _on_front_passenger_door(self, raw: int) -> None:
        self._ingest_door_state("PassengerFront", raw)

    def _on_rear_driver_door(self, raw: int) -> None:
        self._ingest_door_state("DriverRear", raw)

    def _on_rear_passenger_door(self, raw: int) -> None:
        self._ingest_door_state("PassengerRear", raw)

    def _on_gear(self, raw: int) -> None:
        if raw not in GEAR_STATES:
            return
        self._sink.ingest(
            {"Gear": GEAR_STATES[raw]},
            {"source": "bluetooth", "raw": Gear_E.Name(raw)},
        )

    def _on_tonneau(self, raw: int) -> None:
        if raw not in TONNEAU_POSITION_STATES:
            return
        self._sink.ingest(
            {"TonneauPosition": TONNEAU_POSITION_STATES[raw]},
            {"source": "bluetooth", "raw": ClosureState_E.Name(raw)},
        )

    def _on_tonneau_percent_open(self, percent: int) -> None:
        self._sink.ingest(
            {"TonneauOpenPercent": float(percent)}, {"source": "bluetooth"}
        )
