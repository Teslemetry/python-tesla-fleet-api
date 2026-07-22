"""Regression tests for the media command group over the mocked BLE transport.

Covers ``adjust_volume``, ``media_volume_up/down``, ``media_toggle_playback``,
``media_next_track``/``media_prev_track``/``media_next_fav``/``media_prev_fav``
(all INFO, inherited from ``Commands``). Live-verify against the test car is
DEFERRED - the BLE proxy rig was unreliable during the attempt (GATT
write-response timeouts on every signed-command write; plain reads succeeded),
so no snapshot->act->verify->restore cycle could complete. See AGENTS.md for
the transport-instability finding.

``remote_boombox`` is CAPTAIN-PRESENT-ONLY (plays sound through the external
speaker) - mocked-transport coverage only here, never actuated live.
"""

from typing import Any, cast
from unittest.mock import AsyncMock

from tesla_fleet_api.tesla.vehicle.bluetooth import VehicleBluetooth
from tesla_protocol.command.car_server_pb2 import Action, VehicleAction
from tesla_protocol.command.universal_message_pb2 import (
    Domain,
    RoutableMessage,
)

from ble_mocked_transport import (
    MockedBleTransportTestCase,
    decrypt_sent_command,
    infotainment_action_ok_reply,
)


def _sent_vehicle_action(
    vehicle: VehicleBluetooth[Any], send: AsyncMock
) -> tuple[RoutableMessage, VehicleAction]:
    assert send.await_args is not None
    sent_msg = cast("RoutableMessage", send.await_args.args[0])
    plaintext = decrypt_sent_command(vehicle, sent_msg)
    return sent_msg, Action.FromString(plaintext).vehicleAction


class AdjustVolumeTests(MockedBleTransportTestCase):
    async def test_sends_absolute_volume_and_decodes_ok_reply(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_action_ok_reply()

        result = await vehicle.adjust_volume(5.0)

        self.assertEqual(result, {"response": {"result": True, "reason": ""}})
        sent_msg, vehicle_action = _sent_vehicle_action(vehicle, send)
        self.assertEqual(sent_msg.to_destination.domain, Domain.DOMAIN_INFOTAINMENT)
        self.assertAlmostEqual(
            vehicle_action.mediaUpdateVolume.volume_absolute_float, 5.0
        )


class MediaVolumeUpTests(MockedBleTransportTestCase):
    async def test_sends_volume_delta_plus_one(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_action_ok_reply()

        result = await vehicle.media_volume_up()

        self.assertEqual(result, {"response": {"result": True, "reason": ""}})
        _sent_msg, vehicle_action = _sent_vehicle_action(vehicle, send)
        self.assertEqual(vehicle_action.mediaUpdateVolume.volume_delta, 1)


class MediaVolumeDownTests(MockedBleTransportTestCase):
    async def test_sends_volume_delta_minus_one(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_action_ok_reply()

        result = await vehicle.media_volume_down()

        self.assertEqual(result, {"response": {"result": True, "reason": ""}})
        _sent_msg, vehicle_action = _sent_vehicle_action(vehicle, send)
        self.assertEqual(vehicle_action.mediaUpdateVolume.volume_delta, -1)


class MediaTogglePlaybackTests(MockedBleTransportTestCase):
    async def test_sends_media_play_action(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_action_ok_reply()

        result = await vehicle.media_toggle_playback()

        self.assertEqual(result, {"response": {"result": True, "reason": ""}})
        _sent_msg, vehicle_action = _sent_vehicle_action(vehicle, send)
        self.assertTrue(vehicle_action.HasField("mediaPlayAction"))


class MediaNextTrackTests(MockedBleTransportTestCase):
    async def test_sends_media_next_track(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_action_ok_reply()

        result = await vehicle.media_next_track()

        self.assertEqual(result, {"response": {"result": True, "reason": ""}})
        _sent_msg, vehicle_action = _sent_vehicle_action(vehicle, send)
        self.assertTrue(vehicle_action.HasField("mediaNextTrack"))


class MediaPrevTrackTests(MockedBleTransportTestCase):
    async def test_sends_media_previous_track(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_action_ok_reply()

        result = await vehicle.media_prev_track()

        self.assertEqual(result, {"response": {"result": True, "reason": ""}})
        _sent_msg, vehicle_action = _sent_vehicle_action(vehicle, send)
        self.assertTrue(vehicle_action.HasField("mediaPreviousTrack"))


class MediaNextFavTests(MockedBleTransportTestCase):
    async def test_sends_media_next_favorite(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_action_ok_reply()

        result = await vehicle.media_next_fav()

        self.assertEqual(result, {"response": {"result": True, "reason": ""}})
        _sent_msg, vehicle_action = _sent_vehicle_action(vehicle, send)
        self.assertTrue(vehicle_action.HasField("mediaNextFavorite"))


class MediaPrevFavTests(MockedBleTransportTestCase):
    async def test_sends_media_previous_favorite(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_action_ok_reply()

        result = await vehicle.media_prev_fav()

        self.assertEqual(result, {"response": {"result": True, "reason": ""}})
        _sent_msg, vehicle_action = _sent_vehicle_action(vehicle, send)
        self.assertTrue(vehicle_action.HasField("mediaPreviousFavorite"))


class RemoteBoomboxTests(MockedBleTransportTestCase):
    """CAPTAIN-PRESENT-ONLY (external speaker) - proto construction only, never live."""

    async def test_sends_boombox_action_with_sound_index(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_action_ok_reply()

        result = await vehicle.remote_boombox(2)

        self.assertEqual(result, {"response": {"result": True, "reason": ""}})
        _sent_msg, vehicle_action = _sent_vehicle_action(vehicle, send)
        self.assertEqual(vehicle_action.boomboxAction.sound, 2)
