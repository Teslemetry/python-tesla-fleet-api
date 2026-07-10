"""Tests for VehicleBluetooth's idle-triggered BLE keepalive.

The keepalive holds an otherwise idle link open by issuing a bounded passive
GATT read after ``keepalive_interval`` seconds without traffic. These tests
drive the real timer/task machinery with a mocked GATT client - no BLE - and
cover: idle firing, activity resetting the timer, the disabled case, failures
being swallowed and bounded, and task cleanup on disconnect.
"""

from __future__ import annotations

import asyncio
import time
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, MagicMock, patch

from bleak.exc import BleakError
from cryptography.hazmat.primitives.asymmetric import ec

from tesla_fleet_api.tesla.vehicle.bluetooth import (
    READ_UUID,
    VERSION_UUID,
    VehicleBluetooth,
)

VIN = "5YJXCAE43LF123456"


def _make_vehicle(keepalive_interval: float | None) -> VehicleBluetooth:
    parent = MagicMock()
    parent.private_key = ec.generate_private_key(ec.SECP256R1())
    vehicle = VehicleBluetooth(parent, VIN, keepalive_interval=keepalive_interval)
    client = MagicMock()
    client.is_connected = True
    client.read_gatt_char = AsyncMock()
    client.disconnect = AsyncMock()
    vehicle.client = client
    return vehicle


class KeepaliveIdleFiringTests(IsolatedAsyncioTestCase):
    async def test_idle_span_triggers_passive_version_read(self) -> None:
        vehicle = _make_vehicle(keepalive_interval=0.02)
        await vehicle._start_keepalive()
        await asyncio.sleep(0.1)
        await vehicle._stop_keepalive()

        self.assertGreaterEqual(vehicle.client.read_gatt_char.await_count, 1)
        # The keepalive is a passive read of the version characteristic, never
        # a signed/mutating command.
        vehicle.client.read_gatt_char.assert_awaited_with(VERSION_UUID)


class KeepaliveActivityResetTests(IsolatedAsyncioTestCase):
    async def test_continuous_activity_prevents_any_read(self) -> None:
        vehicle = _make_vehicle(keepalive_interval=0.1)
        await vehicle._start_keepalive()

        # Keep the link busier than the interval for well over one interval;
        # the read must never fire while activity keeps resetting the timer.
        for _ in range(10):
            vehicle._last_activity = time.monotonic()
            await asyncio.sleep(0.02)
        await vehicle._stop_keepalive()

        self.assertEqual(vehicle.client.read_gatt_char.await_count, 0)

    async def test_received_frame_resets_the_idle_timer(self) -> None:
        vehicle = _make_vehicle(keepalive_interval=100)
        before = vehicle._last_activity = 0.0
        sender = MagicMock()
        sender.uuid = READ_UUID

        vehicle._on_notify(sender, bytearray())

        self.assertGreater(vehicle._last_activity, before)


class KeepaliveDisabledTests(IsolatedAsyncioTestCase):
    async def test_none_and_zero_start_no_task(self) -> None:
        for interval in (None, 0):
            vehicle = _make_vehicle(keepalive_interval=interval)
            await vehicle._start_keepalive()
            self.assertIsNone(vehicle._keepalive_task)
            await asyncio.sleep(0.02)
            self.assertEqual(vehicle.client.read_gatt_char.await_count, 0)


class KeepaliveFailureHandlingTests(IsolatedAsyncioTestCase):
    async def test_failing_read_is_swallowed_and_loop_survives(self) -> None:
        vehicle = _make_vehicle(keepalive_interval=0.02)
        vehicle.client.read_gatt_char = AsyncMock(side_effect=BleakError("boom"))

        await vehicle._start_keepalive()
        await asyncio.sleep(0.1)
        task = vehicle._keepalive_task

        # The read failed at least once yet never escaped, and the loop is still
        # running rather than having crashed on the exception.
        self.assertGreaterEqual(vehicle.client.read_gatt_char.await_count, 1)
        self.assertIsNotNone(task)
        assert task is not None
        self.assertFalse(task.done())
        await vehicle._stop_keepalive()

    async def test_hanging_read_is_bounded_by_timeout(self) -> None:
        vehicle = _make_vehicle(keepalive_interval=0.01)
        vehicle._keepalive_timeout = 0.02

        async def never_returns(_uuid: str) -> None:
            await asyncio.sleep(100)

        vehicle.client.read_gatt_char = AsyncMock(side_effect=never_returns)

        # A read against a sleeping car must not hang the loop: the bounded
        # timeout returns control well inside the outer wait_for.
        await asyncio.wait_for(vehicle._keepalive_read(), timeout=1.0)

    async def test_read_skipped_when_not_connected(self) -> None:
        vehicle = _make_vehicle(keepalive_interval=0.01)
        vehicle.client.is_connected = False

        await vehicle._keepalive_read()

        self.assertEqual(vehicle.client.read_gatt_char.await_count, 0)


class KeepaliveLifecycleTests(IsolatedAsyncioTestCase):
    async def test_disconnect_cancels_the_keepalive_task(self) -> None:
        vehicle = _make_vehicle(keepalive_interval=0.02)
        await vehicle._start_keepalive()
        task = vehicle._keepalive_task
        self.assertIsNotNone(task)
        assert task is not None

        await vehicle.disconnect()

        self.assertIsNone(vehicle._keepalive_task)
        self.assertTrue(task.cancelled() or task.done())

    async def test_restart_replaces_the_prior_task(self) -> None:
        vehicle = _make_vehicle(keepalive_interval=0.02)
        await vehicle._start_keepalive()
        first = vehicle._keepalive_task

        await vehicle._start_keepalive()
        second = vehicle._keepalive_task

        self.assertIsNotNone(first)
        self.assertIsNotNone(second)
        self.assertIsNot(first, second)
        assert first is not None
        self.assertTrue(first.cancelled() or first.done())
        await vehicle._stop_keepalive()

    async def test_connect_starts_keepalive_and_disconnect_stops_it(self) -> None:
        vehicle = _make_vehicle(keepalive_interval=0.02)
        vehicle.device = MagicMock()
        client = MagicMock()
        client.is_connected = True
        client.start_notify = AsyncMock()
        client.read_gatt_char = AsyncMock()
        client.disconnect = AsyncMock()

        with patch(
            "tesla_fleet_api.tesla.vehicle.bluetooth.establish_connection",
            AsyncMock(return_value=client),
        ):
            await vehicle.connect()
            self.assertIsNotNone(vehicle._keepalive_task)
            await vehicle.disconnect()

        self.assertIsNone(vehicle._keepalive_task)

    async def test_connect_starts_no_task_when_disabled(self) -> None:
        vehicle = _make_vehicle(keepalive_interval=None)
        vehicle.device = MagicMock()
        client = MagicMock()
        client.start_notify = AsyncMock()

        with patch(
            "tesla_fleet_api.tesla.vehicle.bluetooth.establish_connection",
            AsyncMock(return_value=client),
        ):
            await vehicle.connect()

        self.assertIsNone(vehicle._keepalive_task)
