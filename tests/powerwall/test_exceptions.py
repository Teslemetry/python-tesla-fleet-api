"""Failover markers read by tesla_fleet_api's Router."""

from __future__ import annotations

import pytest

from tesla_fleet_api.tesla.powerwall.exceptions import (
    PowerwallAuthenticationError,
    PowerwallCommandError,
    PowerwallConnectionError,
    PowerwallNotSupportedError,
    PowerwallRateLimitError,
)


@pytest.mark.parametrize(
    "exc",
    [
        PowerwallConnectionError("unreachable"),
        PowerwallRateLimitError("429"),
        PowerwallAuthenticationError("401"),
    ],
)
def test_local_path_failures_are_failover_safe(exc: Exception) -> None:
    assert getattr(exc, "failover_safe", None) is True


@pytest.mark.parametrize(
    "exc",
    [
        PowerwallCommandError("set_backup_reserve", 3, "invalid"),
        PowerwallNotSupportedError("set_backup_reserve", 12, "unimplemented"),
    ],
)
def test_gateway_rejections_are_not_marked(exc: Exception) -> None:
    assert getattr(exc, "failover_safe", None) is not True
