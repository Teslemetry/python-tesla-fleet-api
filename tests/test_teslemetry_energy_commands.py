"""Tests for the energy device commands on ``TeslemetryEnergySite``.

Teslemetry rejects the Fleet API ``grpc_command`` envelope, so each command
calls its dedicated Teslemetry route, never the generic
``POST /api/1/energy_sites/{id}/command`` route.
"""

from __future__ import annotations

import inspect
from collections.abc import Awaitable, Callable
from typing import Any
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock

from tesla_fleet_api.const import Method
from tesla_fleet_api.tesla.energysite import EnergySite
from tesla_fleet_api.teslemetry.energysite import TeslemetryEnergySite

SITE_ID = 12345
BASE = f"api/1/energy_sites/{SITE_ID}/command"

Call = Callable[[EnergySite], Awaitable[dict[str, Any]]]

# (name, call, category, command_name, params) for each command.
COMMANDS: list[tuple[str, Call, str, str, dict[str, Any]]] = [
    (
        "get_system_info",
        lambda s: s.get_system_info(),
        "common",
        "get_system_info_request",
        {},
    ),
    (
        "raw_networking_status",
        lambda s: s.raw_networking_status(),
        "common",
        "get_networking_status_request",
        {},
    ),
    ("wifi_scan", lambda s: s.wifi_scan(), "common", "wifi_scan_request", {}),
    (
        "get_device_cert",
        lambda s: s.get_device_cert(),
        "common",
        "device_cert_request",
        {},
    ),
    (
        "get_cellular_info",
        lambda s: s.get_cellular_info(),
        "common",
        "get_cellular_info_request",
        {},
    ),
    (
        "check_for_update",
        lambda s: s.check_for_update(),
        "common",
        "check_for_update_request",
        {},
    ),
    (
        "check_for_update_urgency",
        lambda s: s.check_for_update_urgency(),
        "common",
        "check_for_update_urgency_request",
        {},
    ),
    (
        "check_internet",
        lambda s: s.check_internet(),
        "common",
        "check_internet_request",
        {},
    ),
    (
        "set_local_site_config",
        lambda s: s.set_local_site_config({"site_name": "Home"}),
        "common",
        "set_local_site_config_request",
        {"site_name": "Home"},
    ),
    (
        "get_signed_commands_public_key",
        lambda s: s.get_signed_commands_public_key(),
        "authorization",
        "get_signed_commands_public_key_request",
        {},
    ),
    (
        "get_backup_events",
        lambda s: s.get_backup_events(),
        "teg",
        "get_backup_events_request",
        {},
    ),
    (
        "schedule_backup_event",
        lambda s: s.schedule_backup_event(
            start_time="2026-10-29T10:00:00Z", duration_seconds=3600, priority=1
        ),
        "teg",
        "schedule_manual_backup_event_request",
        {
            "scheduling_info": {
                "start_time": "2026-10-29T10:00:00Z",
                "duration_seconds": 3600,
                "priority": 1,
            }
        },
    ),
    (
        "cancel_backup_event",
        lambda s: s.cancel_backup_event(),
        "teg",
        "cancel_manual_backup_event_request",
        {},
    ),
    ("get_teg_config", lambda s: s.get_teg_config(), "teg", "get_config_request", {}),
]

# Teslemetry route (method, path suffix, JSON body) for each command.
ROUTES: dict[str, tuple[Method, str, dict[str, Any] | None]] = {
    "get_system_info": (Method.GET, "system_info", None),
    "raw_networking_status": (Method.GET, "networking_status", None),
    "wifi_scan": (Method.GET, "wifi_scan", None),
    "get_device_cert": (Method.GET, "device_cert", None),
    "get_cellular_info": (Method.GET, "cellular_info", None),
    "check_for_update": (Method.GET, "check_for_update", None),
    "check_for_update_urgency": (Method.GET, "check_for_update_urgency", None),
    "check_internet": (Method.GET, "check_internet", None),
    "set_local_site_config": (
        Method.POST,
        "set_local_site_config",
        {"site_name": "Home"},
    ),
    "get_signed_commands_public_key": (
        Method.GET,
        "signed_commands_public_key",
        None,
    ),
    "get_backup_events": (Method.GET, "backup_events", None),
    "schedule_backup_event": (
        Method.POST,
        "schedule_backup_event",
        {
            "scheduling_info": {
                "start_time": "2026-10-29T10:00:00Z",
                "duration_seconds": 3600,
                "priority": 1,
            }
        },
    ),
    "cancel_backup_event": (Method.POST, "cancel_backup_event", {}),
    "get_teg_config": (Method.GET, "config", None),
}


def _make_site(cls: type[EnergySite]) -> tuple[EnergySite, AsyncMock]:
    request_mock: AsyncMock = AsyncMock(return_value={"response": {}})
    parent = AsyncMock()
    parent._request = request_mock
    return cls(parent, SITE_ID), request_mock


class TeslemetryDedicatedRouteTests(IsolatedAsyncioTestCase):
    async def test_each_command_calls_its_dedicated_route(self) -> None:
        self.assertEqual({c[0] for c in COMMANDS}, set(ROUTES))
        for name, call, *_ in COMMANDS:
            method, route, body = ROUTES[name]
            with self.subTest(method=name):
                site, request_mock = _make_site(TeslemetryEnergySite)
                await call(site)
                if body is None:
                    request_mock.assert_awaited_once_with(method, f"{BASE}/{route}")
                else:
                    request_mock.assert_awaited_once_with(
                        method, f"{BASE}/{route}", json=body
                    )

    async def test_schedule_backup_event_without_args_sends_empty_body(
        self,
    ) -> None:
        site, request_mock = _make_site(TeslemetryEnergySite)
        await site.schedule_backup_event()
        request_mock.assert_awaited_once_with(
            Method.POST, f"{BASE}/schedule_backup_event", json={}
        )

    async def test_set_local_site_config_without_params_sends_empty_body(
        self,
    ) -> None:
        site, request_mock = _make_site(TeslemetryEnergySite)
        await site.set_local_site_config()
        request_mock.assert_awaited_once_with(
            Method.POST, f"{BASE}/set_local_site_config", json={}
        )

    async def test_returns_route_response(self) -> None:
        site, request_mock = _make_site(TeslemetryEnergySite)
        request_mock.return_value = {"response": {"din": "1232100-00-E--TG1"}}
        self.assertEqual(
            await site.get_system_info(), {"response": {"din": "1232100-00-E--TG1"}}
        )

    def test_every_grpc_command_method_is_overridden(self) -> None:
        # A new EnergySite method on _command must get a Teslemetry route
        # override, or it inherits the grpc_command body Teslemetry rejects.
        uses_command = {
            name
            for name, func in vars(EnergySite).items()
            if inspect.iscoroutinefunction(func)
            and name != "_command"
            and "self._command(" in inspect.getsource(func)
        }
        self.assertTrue(set(ROUTES) <= uses_command)
        self.assertEqual(uses_command - set(vars(TeslemetryEnergySite)), set())


class FleetGrpcCommandUnchangedTests(IsolatedAsyncioTestCase):
    async def test_fleet_site_keeps_grpc_command_envelope(self) -> None:
        for name, call, category, command_name, params in COMMANDS:
            with self.subTest(method=name):
                site, request_mock = _make_site(EnergySite)
                await call(site)
                request_mock.assert_awaited_once_with(
                    Method.POST,
                    f"api/1/energy_sites/{SITE_ID}/command",
                    json={
                        "command_type": "grpc_command",
                        "command_properties": {
                            "message": {category: {command_name: params}},
                            "identifier_type": 1,
                        },
                    },
                )
