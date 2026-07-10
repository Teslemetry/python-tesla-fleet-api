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
from tesla_fleet_api.tesla.vehicle.proto.car_server_pb2 import Action, VehicleAction
from tesla_fleet_api.tesla.vehicle.proto.universal_message_pb2 import RoutableMessage

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
