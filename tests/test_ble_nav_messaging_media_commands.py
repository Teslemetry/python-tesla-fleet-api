"""Navigation/messaging/media commands over the mocked BLE transport.

``upcoming_calendar_entries``/``take_drivenote`` are signed-command siblings of
the existing REST-only ``VehicleFleet`` methods of the same name - cross-
transport parity for those two is covered in ``test_cross_transport_parity.py``.
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


class UpcomingCalendarEntriesTests(MockedBleTransportTestCase):
    async def test_sends_calendar_data(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_action_ok_reply()

        result = await vehicle.upcoming_calendar_entries("some-ics-payload")

        self.assertEqual(result, {"response": {"result": True, "reason": ""}})
        vehicle_action = _decode_vehicle_action(vehicle, send.await_args.args[0])
        self.assertEqual(
            vehicle_action.uiSetUpcomingCalendarEntries.calendar_data,
            "some-ics-payload",
        )


class TakeDrivenoteTests(MockedBleTransportTestCase):
    async def test_sends_note(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_action_ok_reply()

        await vehicle.take_drivenote("check the noise near the front left wheel")

        vehicle_action = _decode_vehicle_action(vehicle, send.await_args.args[0])
        self.assertEqual(
            vehicle_action.takeDrivenoteAction.note,
            "check the noise near the front left wheel",
        )


class VideoRequestTests(MockedBleTransportTestCase):
    async def test_sends_url(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_action_ok_reply()

        await vehicle.video_request("https://example.com/stream.m3u8")

        vehicle_action = _decode_vehicle_action(vehicle, send.await_args.args[0])
        self.assertEqual(
            vehicle_action.videoRequestAction.url, "https://example.com/stream.m3u8"
        )


class NavigationRouteTests(MockedBleTransportTestCase):
    async def test_sends_navigation_route_action(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_action_ok_reply()

        result = await vehicle.navigation_route()

        self.assertEqual(result, {"response": {"result": True, "reason": ""}})
        vehicle_action = _decode_vehicle_action(vehicle, send.await_args.args[0])
        self.assertTrue(vehicle_action.HasField("navigationRouteAction"))


class GetMessagesTests(MockedBleTransportTestCase):
    async def test_sends_get_messages_action(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_action_ok_reply()

        await vehicle.get_messages()

        vehicle_action = _decode_vehicle_action(vehicle, send.await_args.args[0])
        self.assertTrue(vehicle_action.HasField("getMessagesAction"))
