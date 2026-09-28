"""An unconfirmed infotainment command to a sleeping car must not resolve as
best-effort success: a sleeping infotainment computer cannot have run it, and a
success would stop ``VehicleRouter`` from falling back to the cloud, which can
wake the car.
"""

from __future__ import annotations

from typing import Any

from tesla_fleet_api.exceptions import BluetoothCommandFailed, BluetoothTimeout
from tesla_fleet_api.router import VehicleRouter
from tesla_protocol.command.vcsec_pb2 import VehicleSleepStatus_E, VehicleStatus

from ble_mocked_transport import MockedBleTransportTestCase, vcsec_vehicle_status_reply


def sleep_status_reply(status: int) -> Any:
    return vcsec_vehicle_status_reply(VehicleStatus(vehicleSleepStatus=status))


class _FakeCloudFallback:
    def __init__(self, vin: str) -> None:
        self.vin = vin
        self.calls = 0

    async def set_charge_limit(self, percent: int) -> dict[str, Any]:
        self.calls += 1
        return {"response": {"result": True, "reason": "cloud"}}


class InfotainmentAsleepTests(MockedBleTransportTestCase):
    async def test_asleep_raises_command_failed(self) -> None:
        vehicle, send = self.make_vehicle(raise_unconfirmed=False)
        send.side_effect = [
            BluetoothTimeout(),
            sleep_status_reply(VehicleSleepStatus_E.VEHICLE_SLEEP_STATUS_ASLEEP),
        ]

        with self.assertRaises(BluetoothCommandFailed):
            await vehicle.set_charge_limit(80)

    async def test_asleep_falls_back_to_cloud(self) -> None:
        vehicle, send = self.make_vehicle(raise_unconfirmed=False)
        send.side_effect = [
            BluetoothTimeout(),
            sleep_status_reply(VehicleSleepStatus_E.VEHICLE_SLEEP_STATUS_ASLEEP),
        ]
        cloud = _FakeCloudFallback(vehicle.vin)

        result = await VehicleRouter(vehicle, cloud).set_charge_limit(80)

        self.assertEqual(cloud.calls, 1)
        self.assertEqual(result["response"]["reason"], "cloud")

    async def test_awake_stays_best_effort(self) -> None:
        vehicle, send = self.make_vehicle(raise_unconfirmed=False)
        send.side_effect = [
            BluetoothTimeout(),
            sleep_status_reply(VehicleSleepStatus_E.VEHICLE_SLEEP_STATUS_AWAKE),
        ]

        result = await vehicle.set_charge_limit(80)

        self.assertEqual(result, {"response": {"result": True, "reason": ""}})

    async def test_unreadable_sleep_status_stays_best_effort(self) -> None:
        vehicle, send = self.make_vehicle(raise_unconfirmed=False)
        send.side_effect = BluetoothTimeout()

        result = await vehicle.set_charge_limit(80)

        self.assertEqual(result, {"response": {"result": True, "reason": ""}})
