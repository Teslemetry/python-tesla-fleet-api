"""BLE command tests over a mocked transport (no car, no BLE/GATT connection).

Proves the mocked-transport pattern end to end: inherited ``Commands`` route
through ``VehicleBluetooth``'s ``_send``, produce the expected signed
``RoutableMessage``, and a canned reply decodes to the expected result. Every
later BLE command-test PR builds on ``ble_mocked_transport``.
"""

from tesla_fleet_api.tesla.vehicle.proto.car_server_pb2 import Action
from tesla_fleet_api.tesla.vehicle.proto.universal_message_pb2 import Domain
from tesla_fleet_api.tesla.vehicle.proto.vcsec_pb2 import RKEAction_E, UnsignedMessage
from tesla_fleet_api.tesla.vehicle.proto.vehicle_pb2 import ChargeState, VehicleData

from ble_mocked_transport import (
    MockedBleTransportTestCase,
    decrypt_sent_command,
    infotainment_action_ok_reply,
    infotainment_vehicle_data_reply,
    vcsec_ok_reply,
)


class DoorLockTests(MockedBleTransportTestCase):
    """``door_lock`` (VCSEC, inherited from Commands) over the mocked BLE transport."""

    async def test_sends_rke_lock_and_decodes_ok_reply(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = vcsec_ok_reply()

        result = await vehicle.door_lock()

        self.assertEqual(result, {"response": {"result": True, "reason": ""}})

        send.assert_awaited_once()
        sent_msg = send.await_args.args[0]
        self.assertEqual(sent_msg.to_destination.domain, Domain.DOMAIN_VEHICLE_SECURITY)
        self.assertTrue(sent_msg.signature_data.HasField("AES_GCM_Personalized_data"))

        plaintext = decrypt_sent_command(vehicle, sent_msg)
        unsigned = UnsignedMessage.FromString(plaintext)
        self.assertEqual(unsigned.RKEAction, RKEAction_E.RKE_ACTION_LOCK)


class SetTempsTests(MockedBleTransportTestCase):
    """``set_temps`` (INFO, inherited from Commands) over the mocked BLE transport."""

    async def test_sends_hvac_temperature_action_and_decodes_ok_reply(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_action_ok_reply()

        result = await vehicle.set_temps(21.5, 19.0)

        self.assertEqual(result, {"response": {"result": True, "reason": ""}})

        send.assert_awaited_once()
        sent_msg = send.await_args.args[0]
        self.assertEqual(sent_msg.to_destination.domain, Domain.DOMAIN_INFOTAINMENT)
        self.assertTrue(sent_msg.signature_data.HasField("AES_GCM_Personalized_data"))

        plaintext = decrypt_sent_command(vehicle, sent_msg)
        action = Action.FromString(plaintext)
        hvac = action.vehicleAction.hvacTemperatureAdjustmentAction
        self.assertAlmostEqual(hvac.driver_temp_celsius, 21.5)
        self.assertAlmostEqual(hvac.passenger_temp_celsius, 19.0)


class ChargeStateTypedReplyTests(MockedBleTransportTestCase):
    """``charge_state`` (INFO read, defined on VehicleBluetooth) decodes a typed reply."""

    async def test_decodes_canned_vehicle_data_to_charge_state_proto(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_vehicle_data_reply(
            VehicleData(charge_state=ChargeState(battery_level=42))
        )

        charge_state = await vehicle.charge_state()

        self.assertIsInstance(charge_state, ChargeState)
        self.assertEqual(charge_state.battery_level, 42)
