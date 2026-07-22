"""Connectivity/diagnostics commands over the mocked BLE transport."""

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


class BluetoothClassicPairingRequestTests(MockedBleTransportTestCase):
    async def test_sends_name_and_mac_address(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_action_ok_reply()

        await vehicle.bluetooth_classic_pairing_request(
            "My Phone", b"\x00\x11\x22\x33\x44\x55"
        )

        vehicle_action = _decode_vehicle_action(vehicle, send.await_args.args[0])
        req = vehicle_action.bluetoothClassicPairingRequest
        self.assertEqual(req.utf8_name, "My Phone")
        self.assertEqual(req.mac_address, b"\x00\x11\x22\x33\x44\x55")


class BandwidthTestTests(MockedBleTransportTestCase):
    async def test_sends_requested_size(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_action_ok_reply()

        await vehicle.bandwidth_test(1024)

        vehicle_action = _decode_vehicle_action(vehicle, send.await_args.args[0])
        self.assertEqual(vehicle_action.bandwidthTest.requested_size, 1024)


class FetchKeysInfoTests(MockedBleTransportTestCase):
    async def test_sends_fetch_keys_info_action(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_action_ok_reply()

        await vehicle.fetch_keys_info()

        vehicle_action = _decode_vehicle_action(vehicle, send.await_args.args[0])
        self.assertTrue(vehicle_action.HasField("fetchKeysInfoAction"))
