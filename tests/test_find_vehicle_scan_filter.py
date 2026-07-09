"""Regression test: find_vehicle must not scan-filter by service UUID.

The vehicle advertises no 128-bit service UUID (SERVICE_UUID is GATT-only,
available only after connecting); it only advertises its VIN-derived name in
the scan response. A service_uuids scan filter hides the vehicle entirely on
a direct BlueZ adapter.
"""

from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, MagicMock, patch

from cryptography.hazmat.primitives.asymmetric import ec

from tesla_fleet_api.tesla.vehicle.bluetooth import VehicleBluetooth


class _ConcreteVehicleBluetooth(VehicleBluetooth):
    async def _send(self, msg, requires):  # pragma: no cover - not reached
        raise AssertionError("_send should not be called in this test")


class FindVehicleScanFilterTests(IsolatedAsyncioTestCase):
    VIN = "5YJXCAE43LF123456"

    def _make_vehicle(self) -> _ConcreteVehicleBluetooth:
        parent = MagicMock()
        key = ec.generate_private_key(ec.SECP256R1())
        return _ConcreteVehicleBluetooth(parent, self.VIN, key)

    async def test_default_scanner_has_no_service_uuid_filter(self):
        vehicle = self._make_vehicle()

        fake_device = MagicMock()
        captured_kwargs = {}

        class FakeScanner:
            def __init__(self, *args, **kwargs):
                captured_kwargs.update(kwargs)

            async def find_device_by_name(self, name):
                return fake_device

        with patch("tesla_fleet_api.tesla.vehicle.bluetooth.BleakScanner", FakeScanner):
            device = await vehicle.find_vehicle()

        self.assertIs(device, fake_device)
        self.assertNotIn("service_uuids", captured_kwargs)
        self.assertEqual(captured_kwargs.get("scanning_mode"), "active")

    async def test_matches_by_vin_derived_name_without_service_uuid(self):
        vehicle = self._make_vehicle()

        fake_device = MagicMock()
        find_device_by_name = AsyncMock(return_value=fake_device)
        scanner = MagicMock()
        scanner.find_device_by_name = find_device_by_name

        device = await vehicle.find_vehicle(scanner=scanner)

        find_device_by_name.assert_awaited_once_with(vehicle.ble_name)
        self.assertIs(device, fake_device)
