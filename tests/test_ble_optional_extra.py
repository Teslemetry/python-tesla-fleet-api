"""Bluetooth (``bleak``/``bleak-retry-connector``) is an optional extra
(``tesla-fleet-api[ble]``); the cloud-only surface must import without it.

These tests run the check in a subprocess with ``bleak``/``bleak_retry_connector``
poisoned in ``sys.modules`` (setting a module name to ``None`` makes any
``import`` of it raise ``ModuleNotFoundError``, the same failure a real
uninstalled package produces) so the proof holds even though this repo's own
dev/test environment has the ``ble`` extra installed.
"""

from __future__ import annotations

import subprocess
import sys
import textwrap
from unittest import TestCase

_BLOCK_BLE_PRELUDE = """
import sys
sys.modules["bleak"] = None
sys.modules["bleak_retry_connector"] = None
"""


def _run(script: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-c", _BLOCK_BLE_PRELUDE + textwrap.dedent(script)],
        capture_output=True,
        text=True,
        timeout=60,
    )


class TestBluetoothIsOptional(TestCase):
    def test_top_level_package_imports_without_bleak(self):
        result = _run("import tesla_fleet_api")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_cloud_surface_imports_and_works_without_bleak(self):
        result = _run(
            """
            from tesla_fleet_api import (
                ObservationFunnel,
                Region,
                TeslaFleetApi,
                TeslaFleetOAuth,
                Teslemetry,
                Tessie,
            )
            from tesla_fleet_api.router import EnergySiteRouter, Router, VehicleRouter
            from tesla_fleet_api.tesla.vehicle.vehicles import Vehicles
            from cryptography.hazmat.primitives.asymmetric import ec

            class DummyParent:
                private_key = ec.generate_private_key(ec.SECP256R1())

                def _request(self):
                    raise NotImplementedError

            vehicles = Vehicles(parent=DummyParent())
            vehicles.createFleet("5YJXCAE43LF123456")
            vehicles.createSigned("5YJXCAE43LF123456")
            """
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_teslemetry_and_tessie_subpackages_import_without_bleak(self):
        result = _run(
            """
            import tesla_fleet_api.teslemetry.teslemetry
            import tesla_fleet_api.tessie.tessie
            """
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_creating_bluetooth_vehicle_without_bleak_raises_clear_error(self):
        result = _run(
            """
            from tesla_fleet_api.tesla.vehicle.vehicles import Vehicles

            vehicles = Vehicles(parent=object())
            try:
                vehicles.createBluetooth("5YJXCAE43LF123456")
            except ImportError as err:
                assert "ble" in str(err)
                assert "tesla-fleet-api[ble]" in str(err)
            else:
                raise AssertionError("expected ImportError")
            """
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_tesla_bluetooth_attribute_without_bleak_raises_clear_error(self):
        result = _run(
            """
            import tesla_fleet_api

            try:
                tesla_fleet_api.TeslaBluetooth
            except ImportError as err:
                assert "tesla-fleet-api[ble]" in str(err)
            else:
                raise AssertionError("expected ImportError")
            """
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_tesla_vehicle_bluetooth_attribute_without_bleak_raises_clear_error(self):
        result = _run(
            """
            import tesla_fleet_api.tesla

            try:
                tesla_fleet_api.tesla.TeslaBluetooth
            except ImportError as err:
                assert "tesla-fleet-api[ble]" in str(err)
            else:
                raise AssertionError("expected ImportError")

            try:
                tesla_fleet_api.tesla.VehicleBluetooth
            except ImportError as err:
                assert "tesla-fleet-api[ble]" in str(err)
            else:
                raise AssertionError("expected ImportError")
            """
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_vehicle_bluetooth_attribute_without_bleak_raises_clear_error(self):
        result = _run(
            """
            import tesla_fleet_api.tesla.vehicle

            try:
                tesla_fleet_api.tesla.vehicle.VehicleBluetooth
            except ImportError as err:
                assert "tesla-fleet-api[ble]" in str(err)
            else:
                raise AssertionError("expected ImportError")
            """
        )
        self.assertEqual(result.returncode, 0, result.stderr)
