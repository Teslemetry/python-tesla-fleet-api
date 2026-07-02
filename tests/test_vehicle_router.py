"""Unit tests for VehicleRouter health-gated dispatch and fall-through.

These use plain fakes for the two composed vehicle instances so no real BLE
hardware or network access is required.
"""

from unittest import IsolatedAsyncioTestCase

from tesla_fleet_api.tesla.vehicle.router import VehicleRouter


class _FakePrimary:
    """A fake Bluetooth-style primary with a connect_if_needed health signal."""

    def __init__(self, *, can_connect: bool = True):
        self.vin = "PRIMARY_VIN"
        self.can_connect = can_connect
        self.connect_calls = 0
        self.shared_calls = 0

    async def connect_if_needed(self) -> None:
        self.connect_calls += 1
        if not self.can_connect:
            raise ConnectionError("BLE unreachable")

    async def shared(self, value: int) -> str:
        self.shared_calls += 1
        return f"primary:{value}"

    async def primary_only(self) -> str:
        return "primary_only"


class _FakeFallback:
    """A fake cloud-style fallback exposing the shared surface plus extras."""

    def __init__(self):
        self.vin = "FALLBACK_VIN"
        self.shared_calls = 0

    async def shared(self, value: int) -> str:
        self.shared_calls += 1
        return f"fallback:{value}"

    async def fallback_only(self) -> str:
        return "fallback_only"


class VehicleRouterTests(IsolatedAsyncioTestCase):
    """Behavioural tests for VehicleRouter."""

    async def test_primary_healthy_routes_to_primary(self):
        primary = _FakePrimary(can_connect=True)
        fallback = _FakeFallback()
        router: VehicleRouter[_FakePrimary, _FakeFallback] = VehicleRouter(
            primary, fallback
        )

        result = await router.shared(7)

        self.assertEqual(result, "primary:7")
        self.assertEqual(primary.shared_calls, 1)
        self.assertEqual(fallback.shared_calls, 0)
        # Default health should have attempted a connection.
        self.assertEqual(primary.connect_calls, 1)

    async def test_primary_unhealthy_routes_to_fallback(self):
        primary = _FakePrimary(can_connect=False)
        fallback = _FakeFallback()
        router = VehicleRouter(primary, fallback)

        result = await router.shared(9)

        self.assertEqual(result, "fallback:9")
        self.assertEqual(primary.shared_calls, 0)
        self.assertEqual(fallback.shared_calls, 1)

    async def test_method_missing_on_primary_falls_through(self):
        primary = _FakePrimary(can_connect=True)
        fallback = _FakeFallback()
        router = VehicleRouter(primary, fallback)

        result = await router.fallback_only()

        self.assertEqual(result, "fallback_only")
        # Pure fall-through: no health gate, so no connection attempt.
        self.assertEqual(primary.connect_calls, 0)

    async def test_method_only_on_primary_calls_primary(self):
        primary = _FakePrimary(can_connect=True)
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

    async def test_health_check_bool_true(self):
        primary = _FakePrimary(can_connect=False)
        fallback = _FakeFallback()
        router = VehicleRouter(primary, fallback, health=True)

        result = await router.shared(1)

        self.assertEqual(result, "primary:1")
        # Static bool health should not consult the connection signal.
        self.assertEqual(primary.connect_calls, 0)

    async def test_health_check_bool_false(self):
        primary = _FakePrimary(can_connect=True)
        fallback = _FakeFallback()
        router = VehicleRouter(primary, fallback, health=False)

        result = await router.shared(2)

        self.assertEqual(result, "fallback:2")

    async def test_health_check_sync_callable(self):
        primary = _FakePrimary(can_connect=True)
        fallback = _FakeFallback()
        state = {"healthy": False}
        router = VehicleRouter(primary, fallback, health=lambda: state["healthy"])

        self.assertEqual(await router.shared(3), "fallback:3")
        state["healthy"] = True
        self.assertEqual(await router.shared(4), "primary:4")

    async def test_health_check_async_callable(self):
        primary = _FakePrimary(can_connect=True)
        fallback = _FakeFallback()

        async def _health() -> bool:
            return False

        router = VehicleRouter(primary, fallback, health=_health)

        self.assertEqual(await router.shared(5), "fallback:5")

    async def test_default_health_client_is_connected(self):
        """A primary without connect_if_needed uses client.is_connected."""

        class _ClientPrimary:
            def __init__(self, connected: bool):
                self.client = type("C", (), {"is_connected": connected})()

            async def shared(self, value: int) -> str:
                return f"primary:{value}"

        fallback = _FakeFallback()

        connected = VehicleRouter(_ClientPrimary(True), fallback)
        self.assertEqual(await connected.shared(1), "primary:1")

        disconnected = VehicleRouter(_ClientPrimary(False), fallback)
        self.assertEqual(await disconnected.shared(1), "fallback:1")

    async def test_default_health_no_signal_is_healthy(self):
        """A primary with no recognised connection signal is treated healthy."""

        class _PlainPrimary:
            async def shared(self, value: int) -> str:
                return f"primary:{value}"

        router = VehicleRouter(_PlainPrimary(), _FakeFallback())
        self.assertEqual(await router.shared(1), "primary:1")

    async def test_primary_and_fallback_properties(self):
        primary = _FakePrimary()
        fallback = _FakeFallback()
        router = VehicleRouter(primary, fallback)

        self.assertIs(router.primary, primary)
        self.assertIs(router.fallback, fallback)
