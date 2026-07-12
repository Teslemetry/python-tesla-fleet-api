"""Regression test for the write-timeout double-execution gap.

Before this fix, a GATT write that was submitted and then timed out waiting
for the ATT write completion raised ``BluetoothTransportError`` - the same
exception as a provable pre-submission failure - so ``Router``/``VehicleRouter``
treated it as safe to retry and failed over to the cloud secondary. Field data
showed such writes had often already reached the vehicle, so failing over
risked double-executing a non-idempotent command (e.g. door_lock/door_unlock).

This drives the real (unmocked) ``VehicleBluetooth`` send state machine -
only the GATT client is faked, exactly like ``test_ble_broadcast_confirmation``
- wrapped in a real ``VehicleRouter`` with a fake cloud fallback, and asserts
the fallback's ``door_lock`` is never invoked when the primary's write is
delivery-ambiguous.
"""

from __future__ import annotations

from typing import Any, cast
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, MagicMock

from bleak.exc import BleakError
from cryptography.hazmat.primitives.asymmetric import ec

from tesla_fleet_api.exceptions import (
    BluetoothTransportError,
    BluetoothUnconfirmedCommand,
)
from tesla_fleet_api.router import VehicleRouter
from tesla_fleet_api.tesla.vehicle.bluetooth import VehicleBluetooth

VIN = "5YJXCAE43LF123456"


def _make_primary(**kwargs: Any) -> VehicleBluetooth[Any]:
    """A VehicleBluetooth with real send/ladder logic but a faked GATT client."""
    parent = MagicMock()
    parent.private_key = ec.generate_private_key(ec.SECP256R1())
    vehicle = VehicleBluetooth(parent, VIN, **kwargs)
    vehicle.connect_if_needed = AsyncMock()  # type: ignore[method-assign]
    vehicle.client = MagicMock()

    sessions = cast("dict[int, Any]", getattr(vehicle, "_sessions"))
    for session in sessions.values():
        session.epoch = b"\x00" * 16
        session.hmac = b"\x00" * 32
        session.delta = 0
        session.sharedKey = b"\x00" * 16
    return vehicle


class _FakeCloudFallback:
    """A fake cloud secondary tracking whether it was ever invoked."""

    def __init__(self) -> None:
        self.vin = VIN
        self.door_lock_calls = 0

    async def door_lock(self) -> dict[str, Any]:
        self.door_lock_calls += 1
        return {"response": {"result": True, "reason": ""}}


class WriteTimeoutDoesNotFailOverTests(IsolatedAsyncioTestCase):
    async def test_submitted_then_timed_out_write_does_not_replay_on_fallback(
        self,
    ) -> None:
        primary = _make_primary(raise_unconfirmed=True)
        primary._actuation_timeout = 0.05
        # No verify plan is armed (confirm_broadcast is only raced when it
        # resolves); a bare write timeout with nothing else confirming must
        # still be treated as ambiguous, not a provable miss.
        primary.client.write_gatt_char = AsyncMock(
            side_effect=TimeoutError("write timed out")
        )
        fallback = _FakeCloudFallback()
        router = VehicleRouter(primary, fallback)

        with self.assertRaises(BluetoothUnconfirmedCommand):
            await router.door_lock()

        self.assertEqual(fallback.door_lock_calls, 0)

    async def test_mid_write_bleak_error_does_not_replay_on_fallback(self) -> None:
        primary = _make_primary(raise_unconfirmed=True)
        primary._actuation_timeout = 0.05
        primary.client.write_gatt_char = AsyncMock(
            side_effect=BleakError("write failed")
        )
        fallback = _FakeCloudFallback()
        router = VehicleRouter(primary, fallback)

        with self.assertRaises(BluetoothUnconfirmedCommand):
            await router.door_lock()

        self.assertEqual(fallback.door_lock_calls, 0)

    async def test_provable_pre_submission_failure_still_fails_over(self) -> None:
        # Contrast: a failure the local BLE stack raises before any backend
        # I/O (never reaches the vehicle) is safe to retry, and still does.
        primary = _make_primary(raise_unconfirmed=True)
        primary._actuation_timeout = 0.05
        primary.connect_if_needed = AsyncMock(  # type: ignore[method-assign]
            side_effect=BluetoothTransportError()
        )
        fallback = _FakeCloudFallback()
        router = VehicleRouter(primary, fallback)

        result = await router.door_lock()

        self.assertEqual(result, {"response": {"result": True, "reason": ""}})
        self.assertEqual(fallback.door_lock_calls, 1)

    async def test_default_raise_unconfirmed_off_resolves_best_effort_no_failover(
        self,
    ) -> None:
        primary = _make_primary()  # raise_unconfirmed defaults False
        primary._actuation_timeout = 0.05
        primary.client.write_gatt_char = AsyncMock(
            side_effect=TimeoutError("write timed out")
        )
        fallback = _FakeCloudFallback()
        router = VehicleRouter(primary, fallback)

        result = await router.door_lock()

        self.assertEqual(result, {"response": {"result": True, "reason": ""}})
        self.assertEqual(fallback.door_lock_calls, 0)
