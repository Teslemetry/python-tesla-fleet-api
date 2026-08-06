"""Regression tests for the BLE connect retry budget.

``bleak_retry_connector``'s own default (``MAX_CONNECT_ATTEMPTS`` = 4) pairs
with its fixed ~20s per-attempt connect timeout, so a contended connection
slot (every phone/watch slot held) burns ~81s of real GATT connect attempts
before ``connect()`` finally raises ``BluetoothTransportError`` and a
``Router`` can fail over to cloud - indistinguishable from a hang. These
tests lock in that ``connect()``/``connect_if_needed()`` now default to a
smaller attempt budget (``DEFAULT_CONNECT_ATTEMPTS``) instead of
``bleak_retry_connector``'s own default, while still letting a caller pass a
larger ``max_attempts`` explicitly for a scenario that genuinely needs it.
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


class ConnectRetryBudgetTests(IsolatedAsyncioTestCase):
    """The default attempt budget must be cut, not left at the vendored 4."""

    def test_default_is_smaller_than_bleak_retry_connectors_own_default(
        self,
    ) -> None:
        from bleak_retry_connector import MAX_CONNECT_ATTEMPTS

        self.assertLess(DEFAULT_CONNECT_ATTEMPTS, MAX_CONNECT_ATTEMPTS)
        # Still allows one retry - a bare single attempt would give a
        # genuinely transient failure (car waking, weak RF) no second try.
        self.assertGreaterEqual(DEFAULT_CONNECT_ATTEMPTS, 2)

    async def test_connect_passes_reduced_default_to_establish_connection(
        self,
    ) -> None:
        vehicle = _make_vehicle()
        establish = AsyncMock(return_value=_make_connected_client())

        with patch.object(vehicle_bluetooth, "establish_connection", establish):
            await vehicle.connect()

        self.assertEqual(
            establish.call_args.kwargs["max_attempts"], DEFAULT_CONNECT_ATTEMPTS
        )

    async def test_connect_if_needed_passes_reduced_default(self) -> None:
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

    async def test_contended_slot_failure_surfaces_after_the_reduced_budget(
        self,
    ) -> None:
        """A slot-exhausted vehicle (every attempt in the budget times out)
        must still raise ``BluetoothTransportError`` - only the budget
        handed to ``establish_connection`` shrinks, not the exception
        contract a ``Router`` fails over on."""
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
    reduced budget only changes how long that takes, not whether it works."""

    async def test_router_fails_over_after_reduced_connect_budget(self) -> None:
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
        # attempt - the reduced max_attempts is what bounds its internal
        # retry loop, not repeated calls from our code.
        establish.assert_awaited_once()
