"""Regression tests for the BLE connect retry budget.

Under Home Assistant every connect attempt re-picks the best connection path
(local adapter or ESPHome proxy), so the attempt budget is how many paths one
``connect()`` can reach. Two attempts were not enough: a failing local
adapter plus one timed-out proxy ended the connect before a third path was
ever tried. ``bleak_retry_connector``'s own per-attempt timeout is a fixed
20s, so ``connect()`` bounds each attempt itself to keep the
all-attempts-time-out worst case no longer than the old 2 x 20s budget. These
tests lock in the budget, the per-attempt bound, and that a caller can still
override both.
"""

from __future__ import annotations

from typing import Any
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, MagicMock, patch

from bleak.exc import BleakError
from cryptography.hazmat.primitives.asymmetric import ec

import tesla_fleet_api.tesla.vehicle.bluetooth as vehicle_bluetooth
from tesla_fleet_api.exceptions import BluetoothTransportError
from tesla_fleet_api.router import VehicleRouter
from tesla_fleet_api.tesla.vehicle.bluetooth import (
    DEFAULT_CONNECT_ATTEMPT_TIMEOUT,
    DEFAULT_CONNECT_ATTEMPTS,
    VehicleBluetooth,
)

VIN = "5YJXCAE43LF123456"


def _make_vehicle() -> VehicleBluetooth[Any]:
    parent = MagicMock()
    parent.private_key = ec.generate_private_key(ec.SECP256R1())
    vehicle = VehicleBluetooth(parent, VIN)
    vehicle.device = MagicMock()
    vehicle._start_keepalive = AsyncMock()  # type: ignore[method-assign]
    return vehicle


def _make_connected_client() -> MagicMock:
    client = MagicMock()
    client.start_notify = AsyncMock()
    client.disconnect = AsyncMock()
    client.is_connected = True
    return client


class _RecordingClient:
    """Stand-in for the live bleak.BleakClient that records connect timeouts."""

    timeouts: list[float] = []

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        pass

    async def connect(self, **kwargs: Any) -> None:
        self.timeouts.append(kwargs["timeout"])


async def _attempt_timeouts_seen(do_connect: Any) -> list[float]:
    """Run ``do_connect`` and drive one attempt the way the connector does."""
    _RecordingClient.timeouts = []
    establish = AsyncMock(return_value=_make_connected_client())
    with (
        patch("bleak.BleakClient", _RecordingClient),
        patch.object(vehicle_bluetooth, "establish_connection", establish),
    ):
        await do_connect()
        client = establish.call_args.args[0](MagicMock())
        # bleak_retry_connector's fixed per-attempt timeout.
        await client.connect(timeout=20.0, dangerous_use_bleak_cache=False)
    return _RecordingClient.timeouts


class ConnectRetryBudgetTests(IsolatedAsyncioTestCase):
    """The default budget must reach several paths without a longer worst case."""

    def test_default_budget_reaches_several_connection_paths(self) -> None:
        # Adapter plus two proxies needs at least three attempts.
        self.assertGreaterEqual(DEFAULT_CONNECT_ATTEMPTS, 3)

    def test_worst_case_is_no_longer_than_the_old_two_by_twenty_budget(
        self,
    ) -> None:
        from bleak_retry_connector import BLEAK_TIMEOUT

        self.assertLess(DEFAULT_CONNECT_ATTEMPT_TIMEOUT, BLEAK_TIMEOUT)
        self.assertLessEqual(
            DEFAULT_CONNECT_ATTEMPTS * DEFAULT_CONNECT_ATTEMPT_TIMEOUT,
            2 * BLEAK_TIMEOUT,
        )

    async def test_connect_passes_default_budget_to_establish_connection(
        self,
    ) -> None:
        vehicle = _make_vehicle()
        establish = AsyncMock(return_value=_make_connected_client())

        with patch.object(vehicle_bluetooth, "establish_connection", establish):
            await vehicle.connect()

        self.assertEqual(
            establish.call_args.kwargs["max_attempts"], DEFAULT_CONNECT_ATTEMPTS
        )

    async def test_connect_if_needed_passes_default_budget(self) -> None:
        vehicle = _make_vehicle()
        establish = AsyncMock(return_value=_make_connected_client())

        with patch.object(vehicle_bluetooth, "establish_connection", establish):
            await vehicle.connect_if_needed()

        self.assertEqual(
            establish.call_args.kwargs["max_attempts"], DEFAULT_CONNECT_ATTEMPTS
        )

    async def test_caller_can_still_override_for_a_larger_budget(self) -> None:
        """A caller doing its own long-poll retry can still ask for more."""
        vehicle = _make_vehicle()
        establish = AsyncMock(return_value=_make_connected_client())

        with patch.object(vehicle_bluetooth, "establish_connection", establish):
            await vehicle.connect(max_attempts=5)

        self.assertEqual(establish.call_args.kwargs["max_attempts"], 5)

    async def test_each_attempt_is_bounded_to_the_default_timeout(self) -> None:
        """establish_connection calls connect(timeout=20); the client class
        connect() hands it must replace that with the shorter bound."""
        timeouts = await _attempt_timeouts_seen(_make_vehicle().connect)
        self.assertEqual(timeouts, [DEFAULT_CONNECT_ATTEMPT_TIMEOUT])

    async def test_caller_can_override_the_per_attempt_timeout(self) -> None:
        timeouts = await _attempt_timeouts_seen(
            lambda: _make_vehicle().connect_if_needed(attempt_timeout=25)
        )
        self.assertEqual(timeouts, [25])

    async def test_contended_slot_failure_surfaces_after_the_budget(
        self,
    ) -> None:
        """A slot-exhausted vehicle (every attempt in the budget times out)
        must still raise ``BluetoothTransportError`` - the budget handed to
        ``establish_connection`` changes how long that takes, not the
        exception contract a ``Router`` fails over on."""
        vehicle = _make_vehicle()
        # bleak_retry_connector exhausts the whole budget internally and
        # raises a single BleakError once max_attempts is used up.
        establish = AsyncMock(
            side_effect=BleakError("device not found: out of connection slots")
        )

        with patch.object(vehicle_bluetooth, "establish_connection", establish):
            with self.assertRaises(BluetoothTransportError):
                await vehicle.connect()

        establish.assert_awaited_once()
        self.assertEqual(
            establish.call_args.kwargs["max_attempts"], DEFAULT_CONNECT_ATTEMPTS
        )


class _FakeCloudFallback:
    """A cloud secondary tracking whether the router fell over to it."""

    def __init__(self) -> None:
        self.vin = VIN
        self.wake_up_calls = 0

    async def wake_up(self) -> dict[str, Any]:
        self.wake_up_calls += 1
        return {"response": {"result": True, "reason": ""}}


class ContendedSlotFailsOverFastTests(IsolatedAsyncioTestCase):
    """A contended-slot connect failure must still fail over to cloud - the
    connect budget only changes how long that takes, not whether it works."""

    async def test_router_fails_over_after_connect_budget(self) -> None:
        primary = _make_vehicle()
        establish = AsyncMock(
            side_effect=BleakError("device not found: out of connection slots")
        )
        fallback = _FakeCloudFallback()
        router = VehicleRouter(primary, fallback)

        with patch.object(vehicle_bluetooth, "establish_connection", establish):
            result = await router.wake_up()

        self.assertEqual(result, {"response": {"result": True, "reason": ""}})
        self.assertEqual(fallback.wake_up_calls, 1)
        # Only one establish_connection call for the whole failed primary
        # attempt - max_attempts is what bounds its internal
        # retry loop, not repeated calls from our code.
        establish.assert_awaited_once()
