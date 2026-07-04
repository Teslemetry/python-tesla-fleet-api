from __future__ import annotations

from tesla_fleet_api.router.base import PrimaryT, Router, SecondaryT


class VehicleRouter(Router[PrimaryT, SecondaryT]):
    """A :class:`Router` over vehicle instances.

    Pairs (or chains) a local primary — typically a :class:`VehicleBluetooth` —
    with one or more cloud fallbacks (e.g. a ``TeslemetryVehicle``), routing each
    command to the primary first and failing over down the chain. See
    :class:`Router` for the full dispatch, failover, and health-check semantics.
    """
