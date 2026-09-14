"""Unit tests for exceptions.is_key_rejected."""

from unittest import TestCase

from tesla_fleet_api.exceptions import (
    BluetoothTimeout,
    CouldNotRetrieveKeyFault,
    NotOnWhitelistFault,
    SignedMessageInformationFaultCouldNotRetrieveKey,
    SignedMessageInformationFaultNotOnWhitelist,
    SignedMessageInformationFaultTimeExpired,
    TeslaFleetMessageFaultInactiveKey,
    TeslaFleetMessageFaultInvalidKeyHandle,
    TeslaFleetMessageFaultKeychainIsFull,
    TeslaFleetMessageFaultUnknownKeyId,
    TimeExpiredFault,
    is_key_rejected,
)


class IsKeyRejectedTests(TestCase):
    def test_true_for_not_on_whitelist_fault(self):
        self.assertTrue(is_key_rejected(NotOnWhitelistFault()))

    def test_true_for_signed_message_not_on_whitelist(self):
        self.assertTrue(is_key_rejected(SignedMessageInformationFaultNotOnWhitelist()))

    def test_true_for_could_not_retrieve_key_faults(self):
        self.assertTrue(is_key_rejected(CouldNotRetrieveKeyFault()))
        self.assertTrue(
            is_key_rejected(SignedMessageInformationFaultCouldNotRetrieveKey())
        )

    def test_true_for_unknown_key_id_and_inactive_key(self):
        self.assertTrue(is_key_rejected(TeslaFleetMessageFaultUnknownKeyId()))
        self.assertTrue(is_key_rejected(TeslaFleetMessageFaultInactiveKey()))

    def test_true_for_invalid_key_handle(self):
        self.assertTrue(is_key_rejected(TeslaFleetMessageFaultInvalidKeyHandle()))

    def test_false_for_keychain_full(self):
        # A full keychain means no room to add another key, not that this
        # already-paired key was rejected.
        self.assertFalse(is_key_rejected(TeslaFleetMessageFaultKeychainIsFull()))

    def test_false_for_unrelated_faults(self):
        self.assertFalse(is_key_rejected(TimeExpiredFault()))
        self.assertFalse(is_key_rejected(SignedMessageInformationFaultTimeExpired()))

    def test_false_for_transport_errors(self):
        self.assertFalse(is_key_rejected(BluetoothTimeout()))
        self.assertFalse(is_key_rejected(ConnectionError()))
