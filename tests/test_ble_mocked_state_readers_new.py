"""Regression tests for the 7 new BLE vehicle-data sub-state readers.

Completes GetVehicleData coverage alongside the existing 12 readers
(``test_ble_mocked_state_readers.py``): gui_settings, parked_accessory_state,
legacy_vehicle_state, alert_state, light_show_state, suspension_state,
child_presence_detection_state.
"""

from tesla_fleet_api.const import BluetoothVehicleData
from tesla_protocol.command.car_server_pb2 import Action
from tesla_protocol.command.vehicle_pb2 import (
    AlertState,
    ChildPresenceDetectionState,
    GuiSettings,
    LightShowState,
    ParkedAccessoryState,
    SuspensionState,
    VehicleData,
    VehicleState,
)

from ble_mocked_transport import (
    MockedBleTransportTestCase,
    decrypt_sent_command,
    infotainment_vehicle_data_reply,
)


class GuiSettingsTests(MockedBleTransportTestCase):
    async def test_gui_settings(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_vehicle_data_reply(
            VehicleData(gui_settings=GuiSettings(gui_24_hour_time=True))
        )
        result = await vehicle.gui_settings()
        self.assertIsInstance(result, GuiSettings)
        self.assertTrue(result.gui_24_hour_time)


class ParkedAccessoryStateTests(MockedBleTransportTestCase):
    async def test_parked_accessory_state(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_vehicle_data_reply(
            VehicleData(
                parked_accessory_state=ParkedAccessoryState(tent_mode_request=True)
            )
        )
        result = await vehicle.parked_accessory_state()
        self.assertIsInstance(result, ParkedAccessoryState)
        self.assertTrue(result.tent_mode_request)


class LegacyVehicleStateTests(MockedBleTransportTestCase):
    async def test_legacy_vehicle_state(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_vehicle_data_reply(
            VehicleData(legacy_vehicle_state=VehicleState(car_version="2025.14.3"))
        )
        result = await vehicle.legacy_vehicle_state()
        self.assertIsInstance(result, VehicleState)
        self.assertEqual(result.car_version, "2025.14.3")


class AlertStateTests(MockedBleTransportTestCase):
    async def test_alert_state(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_vehicle_data_reply(
            VehicleData(alert_state=AlertState())
        )
        result = await vehicle.alert_state()
        self.assertIsInstance(result, AlertState)


class LightShowStateTests(MockedBleTransportTestCase):
    async def test_light_show_state(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_vehicle_data_reply(
            VehicleData(light_show_state=LightShowState(light_show_active=True))
        )
        result = await vehicle.light_show_state()
        self.assertIsInstance(result, LightShowState)
        self.assertTrue(result.light_show_active)


class SuspensionStateTests(MockedBleTransportTestCase):
    async def test_suspension_state(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_vehicle_data_reply(
            VehicleData(suspension_state=SuspensionState(offroad_on=True))
        )
        result = await vehicle.suspension_state()
        self.assertIsInstance(result, SuspensionState)
        self.assertTrue(result.offroad_on)


class ChildPresenceDetectionStateTests(MockedBleTransportTestCase):
    async def test_child_presence_detection_state(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_vehicle_data_reply(
            VehicleData(
                child_presence_detection_state=ChildPresenceDetectionState(
                    cpd_hvac_active=True
                )
            )
        )
        result = await vehicle.child_presence_detection_state()
        self.assertIsInstance(result, ChildPresenceDetectionState)
        self.assertTrue(result.cpd_hvac_active)


class VehicleDataDispatchNewEndpointsTests(MockedBleTransportTestCase):
    """The 7 new sub-states must wire into ``vehicle_data()``'s endpoints dispatch."""

    async def test_new_endpoints_are_requested_when_given(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_vehicle_data_reply(
            VehicleData(gui_settings=GuiSettings())
        )

        await vehicle.vehicle_data([BluetoothVehicleData.GUI_SETTINGS])

        sent_msg = send.await_args.args[0]
        plaintext = decrypt_sent_command(vehicle, sent_msg)
        get_vehicle_data = Action.FromString(plaintext).vehicleAction.getVehicleData
        self.assertTrue(get_vehicle_data.HasField("getGuiSettings"))
        self.assertFalse(get_vehicle_data.HasField("getParkedAccessoryState"))
        self.assertFalse(get_vehicle_data.HasField("getVehicleState"))
        self.assertFalse(get_vehicle_data.HasField("getAlertState"))
        self.assertFalse(get_vehicle_data.HasField("getLightShowState"))
        self.assertFalse(get_vehicle_data.HasField("getSuspensionState"))
        self.assertFalse(get_vehicle_data.HasField("getChildPresenceDetectionState"))
