"""Niche/low-certainty-value command group over the mocked BLE transport.

pii_key_request, pseudonym_sync_request, tesla_auth_response,
setup_cloud_profile_with_local_profile_uuid, and
get_local_profiles_for_vault_uuid - included per the captain's
full-proto-coverage directive despite no known third-party consumer use
case (see commands.py's Group 18 docstring).
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


class PiiKeyRequestTests(MockedBleTransportTestCase):
    async def test_sends_public_key_and_expiration(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_action_ok_reply()

        await vehicle.pii_key_request("subscriber-pubkey", 1893456000)

        vehicle_action = _decode_vehicle_action(vehicle, send.await_args.args[0])
        req = vehicle_action.piiKeyRequest
        self.assertEqual(req.subscriber_public_key, "subscriber-pubkey")
        self.assertEqual(req.pii_key_expiration.seconds, 1893456000)


class PseudonymSyncRequestTests(MockedBleTransportTestCase):
    async def test_sends_last_known_pseudonym_hashed(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_action_ok_reply()

        await vehicle.pseudonym_sync_request(b"\xaa\xbb\xcc")

        vehicle_action = _decode_vehicle_action(vehicle, send.await_args.args[0])
        self.assertEqual(
            vehicle_action.pseudonymSyncRequest.last_known_pseudonym_hashed,
            b"\xaa\xbb\xcc",
        )


class TeslaAuthResponseTests(MockedBleTransportTestCase):
    async def test_sends_full_oauth_response(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_action_ok_reply()

        await vehicle.tesla_auth_response(
            client_id="my-client",
            scope="openid",
            access_token="access-tok",
            refresh_token="refresh-tok",
            expiry_timestamp=1893456000,
            scoped_token="scoped-tok",
        )

        vehicle_action = _decode_vehicle_action(vehicle, send.await_args.args[0])
        action = vehicle_action.teslaAuthResponseAction
        self.assertEqual(action.client_id, "my-client")
        self.assertEqual(action.scope, "openid")
        self.assertEqual(action.access_token, "access-tok")
        self.assertEqual(action.refresh_token, "refresh-tok")
        self.assertEqual(action.expiry_timestamp, 1893456000)
        self.assertEqual(action.error, "")
        self.assertEqual(action.scoped_token, "scoped-tok")


class SetupCloudProfileWithLocalProfileUuidTests(MockedBleTransportTestCase):
    async def test_sends_uuids_and_delete_flag(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_action_ok_reply()

        await vehicle.setup_cloud_profile_with_local_profile_uuid(
            "cloud-uuid", "local-uuid", delete_local_profile_after_setup=True
        )

        vehicle_action = _decode_vehicle_action(vehicle, send.await_args.args[0])
        action = vehicle_action.setupCloudProfileWithLocalProfileUuidAction
        self.assertEqual(action.cloud_vault_uuid, "cloud-uuid")
        self.assertEqual(action.local_profile_uuid, "local-uuid")
        self.assertTrue(action.delete_local_profile_after_setup)


class GetLocalProfilesForVaultUuidTests(MockedBleTransportTestCase):
    async def test_sends_vault_uuid(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_action_ok_reply()

        await vehicle.get_local_profiles_for_vault_uuid("vault-uuid")

        vehicle_action = _decode_vehicle_action(vehicle, send.await_args.args[0])
        self.assertEqual(
            vehicle_action.getLocalProfilesForVaultUuidAction.vault_uuid,
            "vault-uuid",
        )
