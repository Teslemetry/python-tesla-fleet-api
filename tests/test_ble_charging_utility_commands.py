"""Charging/utility commands over the mocked BLE transport.

``set_rate_tariff``/``add_managed_charging_site`` accept ``tesla_protocol``
message types directly for their deeply-nested arguments rather than a
parallel flattened API - see ``commands.py`` docstrings.
"""

from tesla_protocol.command.car_server_pb2 import Action, SetRateTariffRequest
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


class SetRateTariffTests(MockedBleTransportTestCase):
    async def test_sends_seasons_only(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_action_ok_reply()

        seasons = SetRateTariffRequest.Seasons(
            Summer=SetRateTariffRequest.Season(from_month=6, to_month=8)
        )
        await vehicle.set_rate_tariff(seasons)

        vehicle_action = _decode_vehicle_action(vehicle, send.await_args.args[0])
        action = vehicle_action.setRateTariffRequest
        self.assertEqual(action.seasons.Summer.from_month, 6)
        self.assertEqual(action.seasons.Summer.to_month, 8)
        self.assertFalse(action.HasField("tariff"))

    async def test_sends_tariff_when_given(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_action_ok_reply()

        seasons = SetRateTariffRequest.Seasons()
        tariff = SetRateTariffRequest.Tariff(seasons=seasons)
        await vehicle.set_rate_tariff(seasons, tariff)

        vehicle_action = _decode_vehicle_action(vehicle, send.await_args.args[0])
        action = vehicle_action.setRateTariffRequest
        self.assertTrue(action.HasField("tariff"))


class GetRateTariffTests(MockedBleTransportTestCase):
    async def test_sends_get_rate_tariff_request(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_action_ok_reply()

        await vehicle.get_rate_tariff()

        vehicle_action = _decode_vehicle_action(vehicle, send.await_args.args[0])
        self.assertTrue(vehicle_action.HasField("getRateTariffRequest"))


class AddManagedChargingSiteTests(MockedBleTransportTestCase):
    async def test_sends_public_key_and_coordinates(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_action_ok_reply()

        await vehicle.add_managed_charging_site("pubkey-bytes", 37.3230, -122.0322)

        vehicle_action = _decode_vehicle_action(vehicle, send.await_args.args[0])
        site = vehicle_action.addManagedChargingSiteRequest.site
        self.assertEqual(site.public_key, "pubkey-bytes")
        self.assertTrue(site.manager_type.HasField("site_controller"))
        # LatLong lat/lon are 32-bit floats, so compare at reduced precision.
        self.assertAlmostEqual(site.lat_lon.latitude, 37.3230, places=4)
        self.assertAlmostEqual(site.lat_lon.longitude, -122.0322, places=4)


class RemoveManagedChargingSiteTests(MockedBleTransportTestCase):
    async def test_sends_public_key(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_action_ok_reply()

        await vehicle.remove_managed_charging_site("pubkey-bytes")

        vehicle_action = _decode_vehicle_action(vehicle, send.await_args.args[0])
        self.assertEqual(
            vehicle_action.removeManagedChargingSiteRequest.public_key,
            "pubkey-bytes",
        )


class GetManagedChargingSitesTests(MockedBleTransportTestCase):
    async def test_sends_get_managed_charging_sites_request(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_action_ok_reply()

        await vehicle.get_managed_charging_sites()

        vehicle_action = _decode_vehicle_action(vehicle, send.await_args.args[0])
        self.assertTrue(vehicle_action.HasField("getManagedChargingSitesRequest"))


class SetDischargeLimitTests(MockedBleTransportTestCase):
    async def test_sends_discharge_limit(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_action_ok_reply()

        await vehicle.set_discharge_limit(50)

        vehicle_action = _decode_vehicle_action(vehicle, send.await_args.args[0])
        self.assertEqual(vehicle_action.setDischargeLimitAction.discharge_limit, 50)
