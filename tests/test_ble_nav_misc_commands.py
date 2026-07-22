"""Nav/dashcam/power-mode command group (PR-8) over the mocked BLE transport.

Live-verified against a test car over a local BLE proxy in a single held BLE
connection using the best-effort-wake + poll-confirm strategy (a ``wake_up()``
``BluetoothTimeout`` is a known false negative - see AGENTS.md):
``navigation_request``, ``navigation_gps_request``,
``navigation_sc_request``, ``navigation_waypoints_request``,
``navigation_gps_destination_request``, ``dashcam_save_clip``,
``flash_lights``, ``set_keep_accessory_power_mode`` (True then False),
``set_low_power_mode`` (True then False) - all 11 calls ACKed
``{"result": True}``. None of these have a BLE state prover (momentary or
unobservable), so live "verify" is ACK-only, per the master plan; the nav
commands set a harmless destination and need no restore, and the two
power-mode commands were toggled back off to leave no lasting state change.

Live-discovered bug (fixed in this PR, not a test-only find):
``navigation_gps_request`` called ``NavigationGpsRequest.RemoteNavTripOrder(order)``,
treating the protobuf nested-enum wrapper as if it were a callable Python
enum class - ``EnumTypeWrapper`` isn't callable, so every live call raised
``TypeError`` before a message was ever sent. Fixed to pass the raw int
``order`` directly, matching the working sibling
``navigation_gps_destination_request``.
"""

from tesla_protocol.command.car_server_pb2 import (
    Action,
    NavigationGpsDestinationRequest,
    NavigationGpsRequest,
)
from tesla_protocol.command.universal_message_pb2 import Domain

from ble_mocked_transport import (
    MockedBleTransportTestCase,
    decrypt_sent_command,
    infotainment_action_ok_reply,
)

REPLACE_GPS = NavigationGpsRequest.RemoteNavTripOrder.REMOTE_NAV_TRIP_ORDER_REPLACE
REPLACE_GPS_DEST = (
    NavigationGpsDestinationRequest.RemoteNavTripOrder.REMOTE_NAV_TRIP_ORDER_REPLACE
)


def _decode_vehicle_action(vehicle, sent_msg):
    plaintext = decrypt_sent_command(vehicle, sent_msg)
    action = Action.FromString(plaintext)
    assert sent_msg.to_destination.domain == Domain.DOMAIN_INFOTAINMENT
    assert sent_msg.signature_data.HasField("AES_GCM_Personalized_data")
    return action.vehicleAction


class NavigationRequestTests(MockedBleTransportTestCase):
    async def test_sends_destination_string(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_action_ok_reply()

        result = await vehicle.navigation_request("1 Infinite Loop, Cupertino, CA")

        self.assertEqual(result, {"response": {"result": True, "reason": ""}})
        vehicle_action = _decode_vehicle_action(vehicle, send.await_args.args[0])
        self.assertEqual(
            vehicle_action.navigationRequest.destination,
            "1 Infinite Loop, Cupertino, CA",
        )


class NavigationGpsRequestTests(MockedBleTransportTestCase):
    """Regression test for the ``EnumTypeWrapper`` order bug found live."""

    async def test_sends_lat_lon_and_order(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_action_ok_reply()

        result = await vehicle.navigation_gps_request(37.3230, -122.0322, REPLACE_GPS)

        self.assertEqual(result, {"response": {"result": True, "reason": ""}})
        vehicle_action = _decode_vehicle_action(vehicle, send.await_args.args[0])
        gps = vehicle_action.navigationGpsRequest
        self.assertAlmostEqual(gps.lat, 37.3230)
        self.assertAlmostEqual(gps.lon, -122.0322)
        self.assertEqual(gps.order, REPLACE_GPS)


class NavigationScRequestTests(MockedBleTransportTestCase):
    async def test_sends_supercharger_order(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_action_ok_reply()

        result = await vehicle.navigation_sc_request(1)

        self.assertEqual(result, {"response": {"result": True, "reason": ""}})
        vehicle_action = _decode_vehicle_action(vehicle, send.await_args.args[0])
        self.assertEqual(vehicle_action.navigationSuperchargerRequest.order, 1)


class NavigationWaypointsRequestTests(MockedBleTransportTestCase):
    async def test_sends_waypoints_string(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_action_ok_reply()

        waypoints = "37.3230,-122.0322;37.4419,-122.1430"
        result = await vehicle.navigation_waypoints_request(waypoints)

        self.assertEqual(result, {"response": {"result": True, "reason": ""}})
        vehicle_action = _decode_vehicle_action(vehicle, send.await_args.args[0])
        self.assertEqual(vehicle_action.navigationWaypointsRequest.waypoints, waypoints)


class NavigationGpsDestinationRequestTests(MockedBleTransportTestCase):
    async def test_sends_lat_lon_destination_and_order(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_action_ok_reply()

        result = await vehicle.navigation_gps_destination_request(
            37.4419, -122.1430, "Palo Alto, CA", REPLACE_GPS_DEST
        )

        self.assertEqual(result, {"response": {"result": True, "reason": ""}})
        vehicle_action = _decode_vehicle_action(vehicle, send.await_args.args[0])
        dest = vehicle_action.navigationGpsDestinationRequest
        self.assertAlmostEqual(dest.lat, 37.4419)
        self.assertAlmostEqual(dest.lon, -122.1430)
        self.assertEqual(dest.destination, "Palo Alto, CA")
        self.assertEqual(dest.order, REPLACE_GPS_DEST)


class DashcamSaveClipTests(MockedBleTransportTestCase):
    async def test_sends_dashcam_save_clip_action(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_action_ok_reply()

        result = await vehicle.dashcam_save_clip()

        self.assertEqual(result, {"response": {"result": True, "reason": ""}})
        vehicle_action = _decode_vehicle_action(vehicle, send.await_args.args[0])
        self.assertTrue(vehicle_action.HasField("dashcamSaveClipAction"))


class FlashLightsTests(MockedBleTransportTestCase):
    async def test_sends_flash_lights_action(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_action_ok_reply()

        result = await vehicle.flash_lights()

        self.assertEqual(result, {"response": {"result": True, "reason": ""}})
        vehicle_action = _decode_vehicle_action(vehicle, send.await_args.args[0])
        self.assertTrue(vehicle_action.HasField("vehicleControlFlashLightsAction"))


class SetKeepAccessoryPowerModeTests(MockedBleTransportTestCase):
    async def test_on_sends_keep_accessory_power_mode_true(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_action_ok_reply()

        await vehicle.set_keep_accessory_power_mode(True)

        vehicle_action = _decode_vehicle_action(vehicle, send.await_args.args[0])
        self.assertTrue(
            vehicle_action.setKeepAccessoryPowerModeAction.keep_accessory_power_mode
        )

    async def test_off_sends_keep_accessory_power_mode_false(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_action_ok_reply()

        await vehicle.set_keep_accessory_power_mode(False)

        vehicle_action = _decode_vehicle_action(vehicle, send.await_args.args[0])
        self.assertFalse(
            vehicle_action.setKeepAccessoryPowerModeAction.keep_accessory_power_mode
        )


class SetLowPowerModeTests(MockedBleTransportTestCase):
    async def test_on_sends_low_power_mode_true(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_action_ok_reply()

        await vehicle.set_low_power_mode(True)

        vehicle_action = _decode_vehicle_action(vehicle, send.await_args.args[0])
        self.assertTrue(vehicle_action.setLowPowerModeAction.low_power_mode)

    async def test_off_sends_low_power_mode_false(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_action_ok_reply()

        await vehicle.set_low_power_mode(False)

        vehicle_action = _decode_vehicle_action(vehicle, send.await_args.args[0])
        self.assertFalse(vehicle_action.setLowPowerModeAction.low_power_mode)
