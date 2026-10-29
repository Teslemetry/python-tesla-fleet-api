"""Tests for dispatch_battery_power/resume_battery_operation.

The Fleet API ``EnergySite`` sends the unsigned ``grpc_command`` envelope; the
``TeslemetryEnergySite`` calls the two Teslemetry custom routes. Both share
aiopowerwall's local method names, arguments, units, sign convention and
duration limit, so ``EnergySiteRouter`` can send either command on the local or
the cloud path.
"""

from __future__ import annotations

import inspect
import math
from typing import Any
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock

from tesla_fleet_api.const import Method
from tesla_fleet_api.router import EnergySiteRouter
from tesla_fleet_api.tesla.energysite import (
    MAX_DISPATCH_DURATION_SECONDS,
    EnergySite,
)
from tesla_fleet_api.teslemetry.energysite import TeslemetryEnergySite

SITE_ID = 12345

INVALID_ARGS: list[tuple[Any, Any]] = [
    (math.nan, 60),
    (math.inf, 60),
    (-math.inf, 60),
    (5000, 0),
    (5000, -1),
    (5000, MAX_DISPATCH_DURATION_SECONDS + 1),
    (5000, 60.0),
    (5000, True),
    (5000, "60"),
]


def _make_site(cls: type[EnergySite]) -> tuple[EnergySite, AsyncMock]:
    request_mock: AsyncMock = AsyncMock(return_value={"response": {}})
    parent = AsyncMock()
    parent._request = request_mock
    return cls(parent, SITE_ID), request_mock


def _grpc_body(leaf: dict[str, Any]) -> dict[str, Any]:
    return {
        "command_type": "grpc_command",
        "command_properties": {
            "message": {"teg": {"dispatch_battery_power_request": leaf}},
            "identifier_type": 1,
        },
    }


class FleetBatteryDispatchTests(IsolatedAsyncioTestCase):
    async def test_dispatch_sends_real_power_leaf(self) -> None:
        site, request_mock = _make_site(EnergySite)
        await site.dispatch_battery_power(5000, 60)
        request_mock.assert_awaited_once_with(
            Method.POST,
            f"api/1/energy_sites/{SITE_ID}/command",
            json=_grpc_body(
                {"real_power": {"power_watts": 5000.0, "duration_seconds": 60}}
            ),
        )

    async def test_dispatch_negative_power_charges(self) -> None:
        site, request_mock = _make_site(EnergySite)
        await site.dispatch_battery_power(-2500.5, MAX_DISPATCH_DURATION_SECONDS)
        leaf = request_mock.await_args.kwargs["json"]["command_properties"]["message"][
            "teg"
        ]["dispatch_battery_power_request"]
        self.assertEqual(
            leaf,
            {
                "real_power": {
                    "power_watts": -2500.5,
                    "duration_seconds": MAX_DISPATCH_DURATION_SECONDS,
                }
            },
        )

    async def test_resume_sends_resume_device_mode_leaf(self) -> None:
        site, request_mock = _make_site(EnergySite)
        await site.resume_battery_operation()
        request_mock.assert_awaited_once_with(
            Method.POST,
            f"api/1/energy_sites/{SITE_ID}/command",
            json=_grpc_body({"resume_device_mode": {}}),
        )

    async def test_dispatch_invalid_args_raise_without_request(self) -> None:
        site, request_mock = _make_site(EnergySite)
        for power_watts, duration_seconds in INVALID_ARGS:
            with self.subTest(power=power_watts, duration=duration_seconds):
                with self.assertRaises(ValueError):
                    await site.dispatch_battery_power(power_watts, duration_seconds)
        request_mock.assert_not_called()


class TeslemetryBatteryDispatchTests(IsolatedAsyncioTestCase):
    async def test_dispatch_calls_custom_route(self) -> None:
        site, request_mock = _make_site(TeslemetryEnergySite)
        await site.dispatch_battery_power(-3000, 30)
        request_mock.assert_awaited_once_with(
            Method.POST,
            f"api/1/energy_sites/{SITE_ID}/command/dispatch_battery_power",
            json={"power_watts": -3000.0, "duration_seconds": 30},
        )

    async def test_resume_calls_custom_route(self) -> None:
        site, request_mock = _make_site(TeslemetryEnergySite)
        await site.resume_battery_operation()
        request_mock.assert_awaited_once_with(
            Method.POST,
            f"api/1/energy_sites/{SITE_ID}/command/resume_battery_operation",
        )

    async def test_dispatch_invalid_args_raise_without_request(self) -> None:
        site, request_mock = _make_site(TeslemetryEnergySite)
        for power_watts, duration_seconds in INVALID_ARGS:
            with self.subTest(power=power_watts, duration=duration_seconds):
                with self.assertRaises(ValueError):
                    await site.dispatch_battery_power(power_watts, duration_seconds)
        request_mock.assert_not_called()


class _LocalPowerwallSite:
    """Stand-in with aiopowerwall's local ``dispatch_battery_power`` signature."""

    def __init__(self, *, fail: bool = False) -> None:
        self.fail = fail
        self.calls: list[tuple[str, tuple[Any, ...], dict[str, Any]]] = []

    async def dispatch_battery_power(
        self, power_watts: float, duration_seconds: int
    ) -> None:
        self.calls.append(
            ("dispatch_battery_power", (power_watts, duration_seconds), {})
        )
        if self.fail:
            raise ConnectionError("local unreachable")

    async def resume_battery_operation(self) -> None:
        self.calls.append(("resume_battery_operation", (), {}))
        if self.fail:
            raise ConnectionError("local unreachable")


class RouterBatteryDispatchTests(IsolatedAsyncioTestCase):
    def test_cloud_signatures_match_local(self) -> None:
        for name in ("dispatch_battery_power", "resume_battery_operation"):
            local_params = list(
                inspect.signature(getattr(_LocalPowerwallSite, name)).parameters
            )
            for cls in (EnergySite, TeslemetryEnergySite):
                with self.subTest(cls=cls.__name__, name=name):
                    self.assertEqual(
                        list(inspect.signature(getattr(cls, name)).parameters),
                        local_params,
                    )

    async def test_routes_to_local_primary(self) -> None:
        local = _LocalPowerwallSite()
        cloud, request_mock = _make_site(TeslemetryEnergySite)
        router = EnergySiteRouter(local, cloud)

        await router.dispatch_battery_power(power_watts=5000, duration_seconds=60)
        await router.resume_battery_operation()

        self.assertEqual(
            local.calls,
            [
                ("dispatch_battery_power", (5000, 60), {}),
                ("resume_battery_operation", (), {}),
            ],
        )
        request_mock.assert_not_called()

    async def test_falls_back_to_cloud_with_same_args(self) -> None:
        local = _LocalPowerwallSite(fail=True)
        cloud, request_mock = _make_site(TeslemetryEnergySite)
        router = EnergySiteRouter(local, cloud)

        await router.dispatch_battery_power(power_watts=-1500, duration_seconds=45)
        request_mock.assert_awaited_once_with(
            Method.POST,
            f"api/1/energy_sites/{SITE_ID}/command/dispatch_battery_power",
            json={"power_watts": -1500.0, "duration_seconds": 45},
        )

        request_mock.reset_mock()
        await router.resume_battery_operation()
        request_mock.assert_awaited_once_with(
            Method.POST,
            f"api/1/energy_sites/{SITE_ID}/command/resume_battery_operation",
        )

    async def test_falls_back_to_fleet_grpc(self) -> None:
        local = _LocalPowerwallSite(fail=True)
        fleet, request_mock = _make_site(EnergySite)
        router = EnergySiteRouter(local, fleet)

        await router.dispatch_battery_power(1000, 10)
        request_mock.assert_awaited_once_with(
            Method.POST,
            f"api/1/energy_sites/{SITE_ID}/command",
            json=_grpc_body(
                {"real_power": {"power_watts": 1000.0, "duration_seconds": 10}}
            ),
        )
