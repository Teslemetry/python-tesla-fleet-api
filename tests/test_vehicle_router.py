"""Unit tests for VehicleRouter per-command failover and fall-through.

These use plain fakes for the two composed vehicle instances so no real BLE
hardware or network access is required.
"""

import asyncio
from unittest import IsolatedAsyncioTestCase

from tesla_fleet_api.exceptions import BluetoothTimeout
from tesla_fleet_api.tesla.vehicle.router import VehicleRouter


class _FakePrimary:
    """A fake primary whose shared command can be made to raise on demand."""

    def __init__(self, *, fail: bool = False, exc: BaseException | None = None):
        self.vin = "PRIMARY_VIN"
        self.fail = fail
        self.exc = exc
        self.shared_calls = 0

    async def shared(self, value: int) -> str:
        self.shared_calls += 1
        if self.exc is not None:
            raise self.exc
        if self.fail:
            raise ConnectionError("BLE command failed")
        return f"primary:{value}"

    async def primary_only(self) -> str:
        return "primary_only"


class _FakeFallback:
    """A fake cloud-style fallback exposing the shared surface plus extras."""

    def __init__(self, *, fail: bool = False):
        self.vin = "FALLBACK_VIN"
        self.fail = fail
        self.shared_calls = 0

    async def shared(self, value: int) -> str:
        self.shared_calls += 1
        if self.fail:
            raise ConnectionError("cloud command failed")
        return f"fallback:{value}"

    async def fallback_only(self) -> str:
        return "fallback_only"


class VehicleRouterTests(IsolatedAsyncioTestCase):
    """Behavioural tests for VehicleRouter."""

    async def test_primary_succeeds_routes_to_primary(self):
        primary = _FakePrimary()
        fallback = _FakeFallback()
        router: VehicleRouter[_FakePrimary, _FakeFallback] = VehicleRouter(
            primary, fallback
        )

        result = await router.shared(7)

        self.assertEqual(result, "primary:7")
        self.assertEqual(primary.shared_calls, 1)
        self.assertEqual(fallback.shared_calls, 0)

    async def test_primary_raises_falls_back_with_same_args(self):
        primary = _FakePrimary(fail=True)
        fallback = _FakeFallback()
        router = VehicleRouter(primary, fallback)

        result = await router.shared(9)

        # Primary was attempted, then the same call replayed on the fallback.
        self.assertEqual(result, "fallback:9")
        self.assertEqual(primary.shared_calls, 1)
        self.assertEqual(fallback.shared_calls, 1)

    async def test_both_raise_propagates(self):
        primary = _FakePrimary(fail=True)
        fallback = _FakeFallback(fail=True)
        router = VehicleRouter(primary, fallback)

        with self.assertRaises(ConnectionError):
            await router.shared(1)

        self.assertEqual(primary.shared_calls, 1)
        self.assertEqual(fallback.shared_calls, 1)

    async def test_primary_raises_tesla_fleet_error_falls_back(self):
        # Tesla faults subclass BaseException (not Exception); failover must
        # still catch them and route to the fallback.
        primary = _FakePrimary(exc=BluetoothTimeout())
        fallback = _FakeFallback()
        router = VehicleRouter(primary, fallback)

        result = await router.shared(11)

        self.assertEqual(result, "fallback:11")
        self.assertEqual(primary.shared_calls, 1)
        self.assertEqual(fallback.shared_calls, 1)

    async def test_primary_raises_cancelled_error_propagates(self):
        # CancelledError is a BaseException but not a TeslaFleetError; it must
        # propagate and never trigger fallback.
        primary = _FakePrimary(exc=asyncio.CancelledError())
        fallback = _FakeFallback()
        router = VehicleRouter(primary, fallback)

        with self.assertRaises(asyncio.CancelledError):
            await router.shared(12)

        self.assertEqual(primary.shared_calls, 1)
        self.assertEqual(fallback.shared_calls, 0)

    async def test_method_missing_on_primary_falls_through(self):
        primary = _FakePrimary()
        fallback = _FakeFallback()
        router = VehicleRouter(primary, fallback)

        result = await router.fallback_only()

        self.assertEqual(result, "fallback_only")

    async def test_method_only_on_primary_calls_primary(self):
        primary = _FakePrimary()
        fallback = _FakeFallback()
        router = VehicleRouter(primary, fallback)

        result = await router.primary_only()

        self.assertEqual(result, "primary_only")

    async def test_method_missing_on_both_raises_attribute_error(self):
        router = VehicleRouter(_FakePrimary(), _FakeFallback())

        with self.assertRaises(AttributeError):
            router.does_not_exist  # noqa: B018 - triggers __getattr__

    async def test_non_callable_attribute_prefers_primary(self):
        router = VehicleRouter(_FakePrimary(), _FakeFallback())
        self.assertEqual(router.vin, "PRIMARY_VIN")

    async def test_health_check_bool_true_attempts_primary(self):
        primary = _FakePrimary()
        fallback = _FakeFallback()
        router = VehicleRouter(primary, fallback, health=True)

        result = await router.shared(1)

        self.assertEqual(result, "primary:1")
        self.assertEqual(primary.shared_calls, 1)
        self.assertEqual(fallback.shared_calls, 0)

    async def test_health_check_true_but_primary_raises_falls_back(self):
        primary = _FakePrimary(fail=True)
        fallback = _FakeFallback()
        router = VehicleRouter(primary, fallback, health=True)

        result = await router.shared(2)

        self.assertEqual(result, "fallback:2")
        self.assertEqual(primary.shared_calls, 1)
        self.assertEqual(fallback.shared_calls, 1)

    async def test_health_check_bool_false_skips_primary(self):
        primary = _FakePrimary()
        fallback = _FakeFallback()
        router = VehicleRouter(primary, fallback, health=False)

        result = await router.shared(3)

        self.assertEqual(result, "fallback:3")
        # An explicit False gate must not attempt the primary at all.
        self.assertEqual(primary.shared_calls, 0)

    async def test_health_check_sync_callable(self):
        primary = _FakePrimary()
        fallback = _FakeFallback()
        state = {"healthy": False}
        router = VehicleRouter(primary, fallback, health=lambda: state["healthy"])

        self.assertEqual(await router.shared(4), "fallback:4")
        state["healthy"] = True
        self.assertEqual(await router.shared(5), "primary:5")

    async def test_health_check_async_callable(self):
        primary = _FakePrimary()
        fallback = _FakeFallback()

        async def _health() -> bool:
            return False

        router = VehicleRouter(primary, fallback, health=_health)

        self.assertEqual(await router.shared(6), "fallback:6")
        self.assertEqual(primary.shared_calls, 0)

    async def test_primary_and_fallback_properties(self):
        primary = _FakePrimary()
        fallback = _FakeFallback()
        router = VehicleRouter(primary, fallback)

        self.assertIs(router.primary, primary)
        self.assertIs(router.fallback, fallback)
