"""Cross-transport parity: the same Python call must build semantically
equivalent vehicle instructions over the Fleet REST (cloud) path and the BLE
signed-command (protobuf) path.

Response bodies legitimately differ in FORM (cloud returns a REST JSON dict,
BLE returns decoded protobuf), so these tests assert on the *outbound
instruction* each transport constructs from identical arguments - that is where
a parameter-handling divergence between the two code paths would show up.

The cloud path is exercised through ``VehicleFleet`` with ``_request`` mocked;
the BLE path through ``VehicleBluetooth`` with ``_send`` mocked (see
``ble_mocked_transport``).
"""

from __future__ import annotations

from typing import Any, cast
from unittest.mock import AsyncMock, MagicMock

from tesla_fleet_api.tesla.vehicle.bluetooth import VehicleBluetooth
from tesla_fleet_api.tesla.vehicle.fleet import VehicleFleet
from tesla_protocol.command.car_server_pb2 import Action, VehicleAction
from tesla_protocol.command.universal_message_pb2 import RoutableMessage

from ble_mocked_transport import (
    MockedBleTransportTestCase,
    decrypt_sent_command,
    infotainment_action_ok_reply,
)


def _make_fleet_vehicle(vin: str) -> tuple[VehicleFleet[Any], AsyncMock]:
    """A ``VehicleFleet`` whose ``_request`` is mocked to capture the REST call."""
    parent = MagicMock()
    request = AsyncMock(return_value={"response": {"result": True}})
    parent._request = request  # pyright: ignore[reportAttributeAccessIssue]
    return VehicleFleet(parent, vin), request


def _sent_vehicle_action(
    vehicle: VehicleBluetooth[Any], send: AsyncMock
) -> VehicleAction:
    """Decrypt the signed command the BLE transport was about to send."""
    assert send.await_args is not None
    sent_msg = cast("RoutableMessage", send.await_args.args[0])
    plaintext = decrypt_sent_command(vehicle, sent_msg)
    return Action.FromString(plaintext).vehicleAction


class TriggerHomelinkParityTests(MockedBleTransportTestCase):
    """``trigger_homelink`` must carry the given coordinates on both transports.

    Regression: the cloud path used a truthy ``if lat and lon`` check that
    silently dropped a valid ``0.0`` coordinate, while BLE (``is not None``)
    kept it - a genuine parameter-handling divergence.
    """

    async def test_zero_coordinates_survive_on_both_transports(self) -> None:
        # Cloud (REST)
        cloud, request = _make_fleet_vehicle(self.VIN)
        await cloud.trigger_homelink(token="tok", lat=0.0, lon=0.0)
        assert request.await_args is not None
        cloud_json = request.await_args.kwargs["json"]
        self.assertEqual(cloud_json["lat"], 0.0)
        self.assertEqual(cloud_json["lon"], 0.0)
        self.assertEqual(cloud_json["token"], "tok")

        # BLE (signed protobuf)
        ble, send = self.make_vehicle()
        send.return_value = infotainment_action_ok_reply()
        await ble.trigger_homelink(token="tok", lat=0.0, lon=0.0)
        action = _sent_vehicle_action(ble, send).vehicleControlTriggerHomelinkAction
        self.assertEqual(action.location.latitude, 0.0)
        self.assertEqual(action.location.longitude, 0.0)
        self.assertEqual(action.token, "tok")

    async def test_omitted_coordinates_absent_on_both_transports(self) -> None:
        cloud, request = _make_fleet_vehicle(self.VIN)
        await cloud.trigger_homelink(token="tok")
        assert request.await_args is not None
        cloud_json = request.await_args.kwargs["json"]
        self.assertNotIn("lat", cloud_json)
        self.assertNotIn("lon", cloud_json)

        ble, send = self.make_vehicle()
        send.return_value = infotainment_action_ok_reply()
        await ble.trigger_homelink(token="tok")
        action = _sent_vehicle_action(ble, send).vehicleControlTriggerHomelinkAction
        # No location submessage set when coordinates are omitted.
        self.assertFalse(action.HasField("location"))


class AdjustVolumeParityTests(MockedBleTransportTestCase):
    """``adjust_volume`` must reject the same out-of-range values on both
    transports.

    Regression: the cloud path validated ``0.0 <= volume <= 11.0`` and raised
    ``ValueError``; the BLE path forwarded any float to the car unchecked - a
    parameter-validation divergence.
    """

    async def test_out_of_range_rejected_on_both_transports(self) -> None:
        for bad in (-1.0, 11.5):
            cloud, request = _make_fleet_vehicle(self.VIN)
            with self.assertRaises(ValueError):
                await cloud.adjust_volume(bad)
            request.assert_not_awaited()

            ble, send = self.make_vehicle()
            with self.assertRaises(ValueError):
                await ble.adjust_volume(bad)
            send.assert_not_awaited()

    async def test_in_range_sends_absolute_volume_on_both_transports(self) -> None:
        cloud, request = _make_fleet_vehicle(self.VIN)
        await cloud.adjust_volume(5.0)
        assert request.await_args is not None
        self.assertEqual(request.await_args.kwargs["json"], {"volume": 5.0})

        ble, send = self.make_vehicle()
        send.return_value = infotainment_action_ok_reply()
        await ble.adjust_volume(5.0)
        action = _sent_vehicle_action(ble, send)
        self.assertAlmostEqual(action.mediaUpdateVolume.volume_absolute_float, 5.0)


class ClearPinToDriveAdminParityTests(MockedBleTransportTestCase):
    """``clear_pin_to_drive_admin`` targets the same feature (PIN-to-Drive
    admin reset) on both transports, though the wire forms now legitimately
    differ - a documented, accepted gap, not a bug:

    Fix (live-verified, see report history / task tfa-ble-pin-clear-verify):
    BLE previously built ``DrivingClearSpeedLimitPinAction`` (the
    Speed-Limit-Mode pin clear) instead of a PIN-to-Drive action at all -
    confirmed by the vehicle rejecting a live call with reason
    ``speed_limit_mode_active``. BLE now builds
    ``VehicleControlResetPinToDriveAdminAction``, which has no pin field, so
    ``pin`` is accepted (cross-transport signature parity) but not sent.
    Cloud's REST endpoint still takes ``pin`` in the body - that divergence
    is real but expected (same pattern as ``set_scheduled_departure``'s dead
    args - see CLAUDE.md).
    """

    async def test_cloud_still_sends_pin_ble_ignores_it(self) -> None:
        cloud, request = _make_fleet_vehicle(self.VIN)
        await cloud.clear_pin_to_drive_admin(pin="1234")
        assert request.await_args is not None
        self.assertEqual(request.await_args.kwargs["json"], {"pin": "1234"})

        ble, send = self.make_vehicle()
        send.return_value = infotainment_action_ok_reply()
        await ble.clear_pin_to_drive_admin(pin="1234")
        action = _sent_vehicle_action(ble, send)
        self.assertEqual(
            action.WhichOneof("vehicle_action_msg"),
            "vehicleControlResetPinToDriveAdminAction",
        )
        self.assertFalse(action.HasField("drivingClearSpeedLimitPinAction"))


class NavigationGpsRequestParityTests(MockedBleTransportTestCase):
    """``navigation_gps_request``'s ``order`` must default identically on
    both transports.

    Regression: cloud's ``order`` was optional (omitted -> ``null`` on the
    wire) while BLE's was a required int - a signature mismatch. Both now
    default to ``0`` (``REMOTE_NAV_TRIP_ORDER_UNKNOWN``) when omitted.
    """

    async def test_omitted_order_defaults_to_zero_on_both_transports(self) -> None:
        cloud, request = _make_fleet_vehicle(self.VIN)
        await cloud.navigation_gps_request(37.3230, -122.0322)
        assert request.await_args is not None
        self.assertEqual(
            request.await_args.kwargs["json"],
            {"lat": 37.3230, "lon": -122.0322, "order": 0},
        )

        ble, send = self.make_vehicle()
        send.return_value = infotainment_action_ok_reply()
        await ble.navigation_gps_request(37.3230, -122.0322)
        action = _sent_vehicle_action(ble, send)
        self.assertEqual(action.navigationGpsRequest.order, 0)

    async def test_explicit_order_passes_through_unchanged_on_both_transports(
        self,
    ) -> None:
        cloud, request = _make_fleet_vehicle(self.VIN)
        await cloud.navigation_gps_request(37.3230, -122.0322, order=2)
        assert request.await_args is not None
        self.assertEqual(request.await_args.kwargs["json"]["order"], 2)

        ble, send = self.make_vehicle()
        send.return_value = infotainment_action_ok_reply()
        await ble.navigation_gps_request(37.3230, -122.0322, order=2)
        action = _sent_vehicle_action(ble, send)
        self.assertEqual(action.navigationGpsRequest.order, 2)


class UpcomingCalendarEntriesParityTests(MockedBleTransportTestCase):
    """``upcoming_calendar_entries`` must carry the same ``calendar_data`` string
    on both the REST-only cloud path and its new signed-command BLE sibling."""

    async def test_calendar_data_survives_on_both_transports(self) -> None:
        cloud, request = _make_fleet_vehicle(self.VIN)
        await cloud.upcoming_calendar_entries("some-ics-payload")
        assert request.await_args is not None
        self.assertEqual(
            request.await_args.kwargs["json"], {"calendar_data": "some-ics-payload"}
        )

        ble, send = self.make_vehicle()
        send.return_value = infotainment_action_ok_reply()
        await ble.upcoming_calendar_entries("some-ics-payload")
        action = _sent_vehicle_action(ble, send)
        self.assertEqual(
            action.uiSetUpcomingCalendarEntries.calendar_data, "some-ics-payload"
        )


class TakeDrivenoteParityTests(MockedBleTransportTestCase):
    """``take_drivenote`` must carry the same ``note`` string on both the
    REST-only cloud path and its new signed-command BLE sibling."""

    async def test_note_survives_on_both_transports(self) -> None:
        cloud, request = _make_fleet_vehicle(self.VIN)
        await cloud.take_drivenote("brake noise up front")
        assert request.await_args is not None
        self.assertEqual(
            request.await_args.kwargs["json"], {"note": "brake noise up front"}
        )

        ble, send = self.make_vehicle()
        send.return_value = infotainment_action_ok_reply()
        await ble.take_drivenote("brake noise up front")
        action = _sent_vehicle_action(ble, send)
        self.assertEqual(action.takeDrivenoteAction.note, "brake noise up front")
