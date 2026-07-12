"""Persistent listeners for unsolicited BLE vehicle-status broadcasts.

VCSEC emits ``VehicleStatus`` broadcasts on the same notification
subscription used for command replies (``_on_message`` in ``bluetooth.py``).
Every leaf field of ``VehicleStatus`` is a well-defined protobuf enum or int,
so each gets its own typed ``listen_<field>`` method here, mirroring
python-teslemetry-stream's per-field listener surface. Anything not decoded
into ``VehicleStatus`` - other VCSEC broadcast payloads (``CommandStatus``,
whitelist events, faults) and any future infotainment-domain broadcast -
falls back to the untyped ``listen_broadcast``.
"""

from __future__ import annotations

from typing import Callable, TypeVar

from tesla_fleet_api.tesla.vehicle.proto.universal_message_pb2 import (
    Domain,
    RoutableMessage,
)
from tesla_fleet_api.tesla.vehicle.proto.vcsec_pb2 import (
    ClosureState_E,
    UserPresence_E,
    VehicleLockState_E,
    VehicleSleepStatus_E,
    VehicleStatus,
)

Unsubscribe = Callable[[], None]

T = TypeVar("T")


class BroadcastListeners:
    """Typed and untyped listener registries fed by ``_on_message`` broadcasts.

    Both registries are created once and live for the lifetime of the
    ``VehicleBluetooth`` instance - they are plain Python callables, not
    connection-scoped resources, so they need no reset on reconnect and leak
    nothing beyond what a caller keeps registered without unsubscribing.
    """

    _status_listeners: list[Callable[[VehicleStatus], None]]
    _domain_listeners: dict[Domain, list[Callable[[RoutableMessage], None]]]

    def _init_broadcast_listeners(self) -> None:
        self._status_listeners = []
        self._domain_listeners = {}

    def _register(self, registry: list[T], item: T) -> Unsubscribe:
        registry.append(item)

        def unsubscribe() -> None:
            try:
                registry.remove(item)
            except ValueError:
                pass

        return unsubscribe

    def _dispatch_domain_listeners(self, domain: Domain, msg: RoutableMessage) -> None:
        for callback in list(self._domain_listeners.get(domain, ())):
            callback(msg)

    def _dispatch_status_listeners(self, status: VehicleStatus) -> None:
        for callback in list(self._status_listeners):
            callback(status)

    # -- Generic, untyped --------------------------------------------------

    def listen_broadcast(
        self, domain: Domain, callback: Callable[[RoutableMessage], None]
    ) -> Unsubscribe:
        """Listen for any unsolicited broadcast on ``domain``.

        Catch-all for broadcasts the typed listeners below don't cover:
        non-``VehicleStatus`` VCSEC payloads (``CommandStatus``, whitelist
        events, faults) and any infotainment-domain broadcast.
        """
        return self._register(self._domain_listeners.setdefault(domain, []), callback)

    # -- Typed VCSEC VehicleStatus fields ------------------------------------

    def listen_vehicle_lock_state(
        self, callback: Callable[[VehicleLockState_E], None]
    ) -> Unsubscribe:
        """Listen for the vehicle's overall lock state."""
        return self._register(
            self._status_listeners, lambda status: callback(status.vehicleLockState)
        )

    def listen_vehicle_sleep_status(
        self, callback: Callable[[VehicleSleepStatus_E], None]
    ) -> Unsubscribe:
        """Listen for the vehicle's sleep status."""
        return self._register(
            self._status_listeners, lambda status: callback(status.vehicleSleepStatus)
        )

    def listen_user_presence(
        self, callback: Callable[[UserPresence_E], None]
    ) -> Unsubscribe:
        """Listen for driver-presence status."""
        return self._register(
            self._status_listeners, lambda status: callback(status.userPresence)
        )

    def listen_tonneau_percent_open(
        self, callback: Callable[[int], None]
    ) -> Unsubscribe:
        """Listen for the tonneau's open percentage.

        Only fires on broadcasts that carry ``detailedClosureStatus`` - unlike
        the scalar enum fields above, proto3 tracks presence for this
        submessage, so a broadcast that omits it is skipped rather than
        reported as 0%.
        """

        def on_status(status: VehicleStatus) -> None:
            if status.HasField("detailedClosureStatus"):
                callback(status.detailedClosureStatus.tonneauPercentOpen)

        return self._register(self._status_listeners, on_status)

    def listen_front_driver_door(
        self, callback: Callable[[ClosureState_E], None]
    ) -> Unsubscribe:
        """Listen for the front driver door's closure state."""

        def on_status(status: VehicleStatus) -> None:
            if status.HasField("closureStatuses"):
                callback(status.closureStatuses.frontDriverDoor)

        return self._register(self._status_listeners, on_status)

    def listen_front_passenger_door(
        self, callback: Callable[[ClosureState_E], None]
    ) -> Unsubscribe:
        """Listen for the front passenger door's closure state."""

        def on_status(status: VehicleStatus) -> None:
            if status.HasField("closureStatuses"):
                callback(status.closureStatuses.frontPassengerDoor)

        return self._register(self._status_listeners, on_status)

    def listen_rear_driver_door(
        self, callback: Callable[[ClosureState_E], None]
    ) -> Unsubscribe:
        """Listen for the rear driver door's closure state."""

        def on_status(status: VehicleStatus) -> None:
            if status.HasField("closureStatuses"):
                callback(status.closureStatuses.rearDriverDoor)

        return self._register(self._status_listeners, on_status)

    def listen_rear_passenger_door(
        self, callback: Callable[[ClosureState_E], None]
    ) -> Unsubscribe:
        """Listen for the rear passenger door's closure state."""

        def on_status(status: VehicleStatus) -> None:
            if status.HasField("closureStatuses"):
                callback(status.closureStatuses.rearPassengerDoor)

        return self._register(self._status_listeners, on_status)

    def listen_front_trunk(
        self, callback: Callable[[ClosureState_E], None]
    ) -> Unsubscribe:
        """Listen for the front trunk's closure state."""

        def on_status(status: VehicleStatus) -> None:
            if status.HasField("closureStatuses"):
                callback(status.closureStatuses.frontTrunk)

        return self._register(self._status_listeners, on_status)

    def listen_rear_trunk(
        self, callback: Callable[[ClosureState_E], None]
    ) -> Unsubscribe:
        """Listen for the rear trunk's closure state."""

        def on_status(status: VehicleStatus) -> None:
            if status.HasField("closureStatuses"):
                callback(status.closureStatuses.rearTrunk)

        return self._register(self._status_listeners, on_status)

    def listen_charge_port(
        self, callback: Callable[[ClosureState_E], None]
    ) -> Unsubscribe:
        """Listen for the charge port's closure state."""

        def on_status(status: VehicleStatus) -> None:
            if status.HasField("closureStatuses"):
                callback(status.closureStatuses.chargePort)

        return self._register(self._status_listeners, on_status)

    def listen_tonneau(self, callback: Callable[[ClosureState_E], None]) -> Unsubscribe:
        """Listen for the tonneau's closure state."""

        def on_status(status: VehicleStatus) -> None:
            if status.HasField("closureStatuses"):
                callback(status.closureStatuses.tonneau)

        return self._register(self._status_listeners, on_status)
