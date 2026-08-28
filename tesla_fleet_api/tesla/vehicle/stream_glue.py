"""Feeds BLE broadcasts into a stream-shaped ``ingest()`` sink.

``BleBroadcastStreamGlue`` wires the typed listeners in ``broadcast.py`` to a
duck-typed sink (structurally: python-teslemetry-stream's
``TeslemetryStream(Vehicle).ingest``) so a BLE observation reaches the same
listeners a native stream event does, translated into the identical
stream-shaped payload. This module never imports ``teslemetry_stream`` - the
sink contract below is a structural :class:`typing.Protocol`, matching the
duck-typed ``EnergySite`` composition :class:`~tesla_fleet_api.router.EnergySiteRouter`
already uses for aiopowerwall.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Mapping, Protocol

from tesla_fleet_api.funnel import CLOSURE_STATES, LOCK_STATES
from tesla_fleet_api.tesla.vehicle.broadcast import Unsubscribe
from tesla_protocol.command.vcsec_pb2 import ClosureState_E, VehicleLockState_E

if TYPE_CHECKING:
    from tesla_fleet_api.tesla.vehicle.bluetooth import VehicleBluetooth


class StreamSink(Protocol):
    """Structurally identical to ``TeslemetryStream(Vehicle).ingest`` - not imported."""

    def ingest(
        self, data: Mapping[str, Any], metadata: Mapping[str, Any] | None = None
    ) -> Mapping[str, Any]: ...


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

    def _on_front_trunk(self, raw: int) -> None:
        if raw not in CLOSURE_STATES:
            return
        self._sink.ingest(
            {"DoorState": {"TrunkFront": CLOSURE_STATES[raw]}},
            {"source": "bluetooth", "raw": ClosureState_E.Name(raw)},
        )
