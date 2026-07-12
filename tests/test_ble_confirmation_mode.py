"""Tests for the ``confirmation`` ladder-depth setting on ``VehicleBluetooth``.

``confirmation`` ("optimistic" | "ack" | "verify") replaces the old
``optimistic``/``verify_commands`` booleans as the single ladder-depth choice;
``raise_unconfirmed`` stays a separate orthogonal bool for what to do once a
ladder is still genuinely inconclusive. The old booleans remain as deprecated
constructor aliases (mapped onto ``confirmation``, with a ``DeprecationWarning``)
and as read-only properties for existing callers.
"""

from __future__ import annotations

import warnings
from unittest import TestCase
from unittest.mock import MagicMock

from cryptography.hazmat.primitives.asymmetric import ec

from tesla_fleet_api.exceptions import BluetoothTimeout, BluetoothUnconfirmedCommand
from tesla_fleet_api.tesla.vehicle.bluetooth import VehicleBluetooth
from tesla_fleet_api.tesla.vehicle.vehicles import Vehicles, VehiclesBluetooth
from tesla_fleet_api.tesla.vehicle.proto.vcsec_pb2 import (
    VehicleLockState_E,
    VehicleStatus,
)

from ble_mocked_transport import MockedBleTransportTestCase, vcsec_vehicle_status_reply

VIN = "5YJXCAE43LF123456"


def _make_parent() -> MagicMock:
    parent = MagicMock()
    parent.private_key = ec.generate_private_key(ec.SECP256R1())
    return parent


class DefaultsTests(TestCase):
    """The class's own defaults, independent of any test-harness convenience default."""

    def test_new_defaults_are_ack_and_raise_unconfirmed_false(self) -> None:
        vehicle = VehicleBluetooth(_make_parent(), VIN)

        self.assertEqual(vehicle.confirmation, "ack")
        self.assertFalse(vehicle.raise_unconfirmed)
        self.assertFalse(vehicle.optimistic)
        self.assertFalse(vehicle.verify_commands)


class DeprecatedArgMappingTests(TestCase):
    """The deprecated ``verify_commands``/``optimistic`` constructor aliases."""

    def test_verify_commands_true_warns_and_maps_to_verify(self) -> None:
        with self.assertWarns(DeprecationWarning):
            vehicle = VehicleBluetooth(_make_parent(), VIN, verify_commands=True)

        self.assertEqual(vehicle.confirmation, "verify")
        self.assertTrue(vehicle.verify_commands)
        self.assertFalse(vehicle.optimistic)

    def test_optimistic_true_warns_and_maps_to_optimistic(self) -> None:
        with self.assertWarns(DeprecationWarning):
            vehicle = VehicleBluetooth(_make_parent(), VIN, optimistic=True)

        self.assertEqual(vehicle.confirmation, "optimistic")
        self.assertTrue(vehicle.optimistic)
        self.assertFalse(vehicle.verify_commands)

    def test_verify_commands_false_still_warns_but_leaves_default_confirmation(
        self,
    ) -> None:
        # Passing the deprecated arg at all is deprecated usage, even if the
        # value itself wouldn't change anything.
        with self.assertWarns(DeprecationWarning):
            vehicle = VehicleBluetooth(_make_parent(), VIN, verify_commands=False)

        self.assertEqual(vehicle.confirmation, "ack")

    def test_positional_verify_commands_maps_to_confirmation(self) -> None:
        with self.assertWarns(DeprecationWarning):
            vehicle = VehicleBluetooth(_make_parent(), VIN, None, None, True)

        self.assertEqual(vehicle.confirmation, "verify")

    def test_positional_optimistic_slot_still_maps_to_optimistic(self) -> None:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            vehicle = VehicleBluetooth(
                _make_parent(), VIN, None, None, False, None, True
            )

        self.assertEqual(vehicle.confirmation, "optimistic")
        self.assertFalse(vehicle.raise_unconfirmed)

    def test_vehicle_factory_preserves_old_positional_bool_order(self) -> None:
        vehicles = Vehicles(_make_parent())

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            vehicle = vehicles.createBluetooth(VIN, True, None, True, False)

        self.assertEqual(vehicle.confirmation, "optimistic")
        self.assertFalse(vehicle.raise_unconfirmed)

    def test_bluetooth_collection_preserves_old_positional_bool_order(self) -> None:
        vehicles = VehiclesBluetooth(_make_parent())

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            vehicle = vehicles.createBluetooth(VIN, None, None, True, None, True, False)

        self.assertEqual(vehicle.confirmation, "optimistic")
        self.assertFalse(vehicle.raise_unconfirmed)

    def test_optimistic_true_dominates_verify_commands_true(self) -> None:
        # Matches the old three-boolean dominance order: optimistic wins.
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            vehicle = VehicleBluetooth(
                _make_parent(), VIN, verify_commands=True, optimistic=True
            )

        self.assertEqual(vehicle.confirmation, "optimistic")

    def test_optimistic_and_verify_commands_are_read_only(self) -> None:
        vehicle = VehicleBluetooth(_make_parent(), VIN)

        with self.assertRaises(AttributeError):
            vehicle.verify_commands = True  # type: ignore[misc]
        with self.assertRaises(AttributeError):
            vehicle.optimistic = True  # type: ignore[misc]


class ConfirmationLadderTests(MockedBleTransportTestCase):
    """Each ``confirmation`` rung behaves as documented."""

    async def test_optimistic_returns_on_write_without_waiting(self) -> None:
        vehicle, send = self.make_vehicle(confirmation="optimistic")

        result = await vehicle.door_lock()

        self.assertEqual(result, {"response": {"result": True, "reason": ""}})
        send.assert_awaited_once()

    async def test_ack_mode_raises_unconfirmed_on_timeout_when_opted_in(self) -> None:
        vehicle, send = self.make_vehicle(confirmation="ack", raise_unconfirmed=True)
        send.side_effect = [BluetoothTimeout()]

        with self.assertRaises(BluetoothUnconfirmedCommand):
            await vehicle.door_lock()

    async def test_verify_mode_confirms_via_prover_read(self) -> None:
        vehicle, send = self.make_vehicle(confirmation="verify")
        send.side_effect = [
            BluetoothTimeout(),
            vcsec_vehicle_status_reply(
                VehicleStatus(
                    vehicleLockState=VehicleLockState_E.VEHICLELOCKSTATE_LOCKED
                )
            ),
        ]

        result = await vehicle.door_lock()

        self.assertEqual(result, {"response": {"result": True, "reason": ""}})
        self.assertEqual(send.await_count, 2)

    async def test_ack_mode_never_issues_a_verify_read(self) -> None:
        # "ack" must not fall through to a state-read - that's "verify" only.
        vehicle, send = self.make_vehicle(confirmation="ack", raise_unconfirmed=False)
        send.side_effect = [BluetoothTimeout()]

        result = await vehicle.door_lock()

        self.assertEqual(result, {"response": {"result": True, "reason": ""}})
        send.assert_awaited_once()

    async def test_ack_with_raise_unconfirmed_false_matches_production_defaults(
        self,
    ) -> None:
        # These match VehicleBluetooth's own defaults - see DefaultsTests for
        # the direct-construction check; this exercises their behavior.
        vehicle, send = self.make_vehicle(confirmation="ack", raise_unconfirmed=False)
        send.side_effect = [BluetoothTimeout()]

        result = await vehicle.door_lock()

        self.assertEqual(result, {"response": {"result": True, "reason": ""}})


class MootComboTests(MockedBleTransportTestCase):
    """Combinations invalid only under the old three-boolean surface are moot, not errors."""

    async def test_optimistic_with_raise_unconfirmed_true_is_moot_not_error(
        self,
    ) -> None:
        # optimistic never reaches an unconfirmed outcome, so raise_unconfirmed
        # simply never gets consulted - constructing/using both must not raise.
        vehicle, send = self.make_vehicle(
            confirmation="optimistic", raise_unconfirmed=True
        )

        result = await vehicle.door_lock()

        self.assertEqual(result, {"response": {"result": True, "reason": ""}})
        send.assert_awaited_once()
