"""Destructive data-clearing commands over the mocked BLE transport.

``format_usb``/``delete_dashcam_clips`` are unguarded no-confirmation
wrappers, matching the existing ``erase_user_data()`` precedent
(``tests/test_ble_mocked_commands.py`` has no dedicated test for that one
either - it is exercised indirectly via the cross-transport suite).
"""

from tesla_protocol.command.car_server_pb2 import Action
from tesla_protocol.command.universal_message_pb2 import Domain

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


class FormatUsbTests(MockedBleTransportTestCase):
    async def test_sends_format_usb_true(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_action_ok_reply()

        result = await vehicle.format_usb()

        self.assertEqual(result, {"response": {"result": True, "reason": ""}})
        vehicle_action = _decode_vehicle_action(vehicle, send.await_args.args[0])
        self.assertTrue(vehicle_action.formatUsbAction.format_usb)


class DeleteDashcamClipsTests(MockedBleTransportTestCase):
    async def test_sends_delete_clips_true(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_action_ok_reply()

        result = await vehicle.delete_dashcam_clips()

        self.assertEqual(result, {"response": {"result": True, "reason": ""}})
        vehicle_action = _decode_vehicle_action(vehicle, send.await_args.args[0])
        self.assertTrue(vehicle_action.deleteDashcamClipsAction.delete_clips)
