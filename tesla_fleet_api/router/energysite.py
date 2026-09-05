from __future__ import annotations

from typing import Any

from tesla_fleet_api.router.base import PrimaryT, Router, SecondaryT

LOCAL_LIVE_STATUS_KEYS: frozenset[str] = frozenset(
    {
        "solar_power",
        "energy_left",
        "total_pack_energy",
        "percentage_charged",
        "battery_power",
        "load_power",
        "grid_power",
        "generator_power",
        "grid_status",
        "island_status",
    }
)
LOCAL_SITE_INFO_KEYS: frozenset[str] = frozenset(
    {"backup_reserve_percent", "default_real_mode"}
)


def merge_local_into_cloud(
    cloud: dict[str, Any], local: dict[str, Any] | None, owned_keys: frozenset[str]
) -> dict[str, Any]:
    """Overlay owned_keys present in local onto a copy of cloud; every other key keeps its cloud value.

    ``PowerwallEnergySite.live_status()`` returns all cloud keys with ``None``
    for the ones it cannot serve, so presence-in-response cannot be the
    ownership test — a fixed owned-key set lets a caller overlay local
    readings without clobbering cloud values, and lets a local outage fall
    back to the cloud value instead of an unavailable one.

    A key overlays only when it is owned, present in ``local``, and
    ``local[key] is not None``; ``None`` means "not served this tick" and the
    cloud value is kept, while any other falsy value (``0``, ``False``, ``""``)
    still overlays.
    """
    merged = dict(cloud)
    if local is None:
        return merged
    for key in owned_keys:
        if key in local and local[key] is not None:
            merged[key] = local[key]
    return merged


def merge_live_status(cloud: dict[str, Any], local: dict[str, Any] | None) -> dict[str, Any]:
    """Overlay a local Powerwall live_status onto the cloud document; see merge_local_into_cloud."""
    return merge_local_into_cloud(cloud, local, LOCAL_LIVE_STATUS_KEYS)


def merge_site_info(cloud: dict[str, Any], local: dict[str, Any] | None) -> dict[str, Any]:
    """Overlay a local Powerwall site_info onto the cloud document; see merge_local_into_cloud."""
    return merge_local_into_cloud(cloud, local, LOCAL_SITE_INFO_KEYS)


class EnergySiteRouter(Router[PrimaryT, SecondaryT]):
    """A :class:`Router` over energy-site instances.

    Pairs (or chains) a local primary — a duck-typed ``EnergySite``-shaped object
    such as aiopowerwall's ``PowerwallEnergySite`` — with one or more cloud
    fallbacks (e.g. a ``TeslemetryEnergySite``), routing each command to the local
    site first and failing over down the chain. See :class:`Router` for the full
    dispatch, failover, and health-check semantics.

    Example::

        router = EnergySiteRouter(local_energysite, teslemetry_energysite)
        await router.operation(...)  # local first, cloud on failure
    """
