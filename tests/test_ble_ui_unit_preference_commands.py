"""UI/unit-preference commands over the mocked BLE transport.

Trivial single-scalar/nested-message wrappers over
``Set*UnitAction``/``SetTimeDisplayFormatAction``/``SetEnergyDisplayFormatAction``/
``SetPhoneSettingPreferencesAction``.
"""

from tesla_protocol.command.car_server_pb2 import Action
from tesla_protocol.command.universal_message_pb2 import Domain

from tesla_fleet_api.const import (
    DistanceUnit,
    EnergyDisplayFormat,
    PhoneFontSize,
    TemperatureUnit,
    TimeDisplayFormat,
    TirePressureUnit,
)
from ble_mocked_transport import (
    MockedBleTransportTestCase,
    decrypt_sent_command,
    infotainment_action_ok_reply,
)


def _decode_vehicle_action(vehicle, sent_msg):
    plaintext = decrypt_sent_command(vehicle, sent_msg)
    action = Action.FromString(plaintext)
    assert sent_msg.to_destination.domain == Domain.DOMAIN_INFOTAINMENT
    return action.vehicleAction


class SetTemperatureUnitTests(MockedBleTransportTestCase):
    async def test_sends_celsius(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_action_ok_reply()

        result = await vehicle.set_temperature_unit(TemperatureUnit.CELSIUS)

        self.assertEqual(result, {"response": {"result": True, "reason": ""}})
        vehicle_action = _decode_vehicle_action(vehicle, send.await_args.args[0])
        self.assertEqual(
            vehicle_action.setTemperatureUnitAction.unit, TemperatureUnit.CELSIUS
        )


class SetDistanceUnitTests(MockedBleTransportTestCase):
    async def test_sends_kilometers(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_action_ok_reply()

        await vehicle.set_distance_unit(DistanceUnit.KILOMETERS)

        vehicle_action = _decode_vehicle_action(vehicle, send.await_args.args[0])
        self.assertEqual(
            vehicle_action.setDistanceUnitAction.unit, DistanceUnit.KILOMETERS
        )


class SetTimeDisplayFormatTests(MockedBleTransportTestCase):
    async def test_sends_24_hour(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_action_ok_reply()

        await vehicle.set_time_display_format(TimeDisplayFormat.HOUR_24)

        vehicle_action = _decode_vehicle_action(vehicle, send.await_args.args[0])
        self.assertEqual(
            vehicle_action.setTimeDisplayFormatAction.format,
            TimeDisplayFormat.HOUR_24,
        )


class SetTirePressureUnitTests(MockedBleTransportTestCase):
    async def test_sends_bar(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_action_ok_reply()

        await vehicle.set_tire_pressure_unit(TirePressureUnit.BAR)

        vehicle_action = _decode_vehicle_action(vehicle, send.await_args.args[0])
        self.assertEqual(
            vehicle_action.setTirePressureUnitAction.unit, TirePressureUnit.BAR
        )


class SetEnergyDisplayFormatTests(MockedBleTransportTestCase):
    async def test_sends_distance_format(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_action_ok_reply()

        await vehicle.set_energy_display_format(EnergyDisplayFormat.DISTANCE)

        vehicle_action = _decode_vehicle_action(vehicle, send.await_args.args[0])
        self.assertEqual(
            vehicle_action.setEnergyDisplayFormatAction.format,
            EnergyDisplayFormat.DISTANCE,
        )


class SetPhoneSettingPreferencesTests(MockedBleTransportTestCase):
    async def test_font_size_only_leaves_unit_preferences_unset(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_action_ok_reply()

        await vehicle.set_phone_setting_preferences(PhoneFontSize.LARGE)

        vehicle_action = _decode_vehicle_action(vehicle, send.await_args.args[0])
        action = vehicle_action.setPhoneSettingPreferencesAction
        self.assertEqual(action.font_size, PhoneFontSize.LARGE)
        self.assertFalse(action.HasField("unit_preferences"))

    async def test_units_are_nested_under_unit_preferences(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_action_ok_reply()

        await vehicle.set_phone_setting_preferences(
            distance_unit=DistanceUnit.KILOMETERS,
            temperature_unit=TemperatureUnit.CELSIUS,
        )

        vehicle_action = _decode_vehicle_action(vehicle, send.await_args.args[0])
        prefs = vehicle_action.setPhoneSettingPreferencesAction.unit_preferences
        self.assertEqual(prefs.distance_unit, DistanceUnit.KILOMETERS)
        self.assertEqual(prefs.temperature_unit, TemperatureUnit.CELSIUS)
