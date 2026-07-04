from __future__ import annotations

from tesla_fleet_api.router.base import PrimaryT, Router, SecondaryT


class EnergySiteRouter(Router[PrimaryT, SecondaryT]):
    """A :class:`Router` over energy-site instances.

    Pairs (or chains) a local primary — a duck-typed ``EnergySite``-shaped object
    such as aiopowerwall's ``PowerwallEnergySite`` — with one or more cloud
    fallbacks (e.g. a ``TeslemetryEnergySite``), routing each command to the local
    site first and failing over down the chain. See :class:`Router` for the full
    dispatch, failover, and health-check semantics.

    Example::

        router = EnergySiteRouter(local_energysite, teslemetry_energysite)
        await router.set_operation(...)  # local first, cloud on failure
    """
