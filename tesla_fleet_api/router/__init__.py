"""Routing wrappers with per-command failover across backends."""

from tesla_fleet_api.router.base import HealthCheck, Router
from tesla_fleet_api.router.vehicle import VehicleRouter
from tesla_fleet_api.router.energysite import (
    EnergySiteRouter,
    LOCAL_LIVE_STATUS_KEYS,
    LOCAL_SITE_INFO_KEYS,
    merge_local_into_cloud,
    merge_live_status,
    merge_site_info,
)

__all__ = [
    "Router",
    "VehicleRouter",
    "EnergySiteRouter",
    "HealthCheck",
    "LOCAL_LIVE_STATUS_KEYS",
    "LOCAL_SITE_INFO_KEYS",
    "merge_local_into_cloud",
    "merge_live_status",
    "merge_site_info",
]
