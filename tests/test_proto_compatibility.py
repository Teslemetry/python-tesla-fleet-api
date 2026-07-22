import importlib
import unittest

from tesla_fleet_api.tesla.vehicle import proto


MODULE_NAMES = (
    "car_server_pb2",
    "common_pb2",
    "errors_pb2",
    "keys_pb2",
    "managed_charging_pb2",
    "session_pb2",
    "signatures_pb2",
    "universal_message_pb2",
    "vcsec_pb2",
    "vehicle_pb2",
)


class ProtoCompatibilityTests(unittest.TestCase):
    def test_legacy_modules_reexport_upstream_symbols(self) -> None:
        for module_name in MODULE_NAMES:
            with self.subTest(module=module_name):
                legacy = importlib.import_module(
                    f"tesla_fleet_api.tesla.vehicle.proto.{module_name}"
                )
                upstream = importlib.import_module(
                    f"tesla_protocol.command.{module_name}"
                )

                self.assertIs(getattr(proto, module_name), legacy)
                for name, value in vars(upstream).items():
                    if not name.startswith("_"):
                        self.assertIs(getattr(legacy, name), value)
