"""Tests for the ``optimistic`` and ``raise_unconfirmed`` consumer knobs.

Both form one outcome contract on top of the existing confirmation ladder
(write -> ack wait -> ``verify_commands`` -> unconfirmed outcome):

- ``optimistic`` (default off) skips the ack wait and ``verify_commands``
  entirely for a mutating command - a confirmed GATT write is the whole
  outcome. Only a write/transport failure still raises.
- ``raise_unconfirmed`` (default on, i.e. current behavior) controls what
  happens when the ladder is exhausted without a positive or negative
  answer: off resolves that ambiguous case as a best-effort success instead
  of raising ``BluetoothUnconfirmedCommand``. A car-side rejection, a
  ``verify_commands`` state mismatch, and write failures are unaffected and
  always raise.
"""

from __future__ import annotations

from tesla_fleet_api.exceptions import (
    BluetoothCommandFailed,
    BluetoothTimeout,
    BluetoothTransportError,
    BluetoothUnconfirmedCommand,
)
from tesla_fleet_api.tesla.vehicle.proto.vcsec_pb2 import (
    VehicleLockState_E,
    VehicleStatus,
)

from ble_mocked_transport import (
    MockedBleTransportTestCase,
    infotainment_action_ok_reply,
    vcsec_vehicle_status_reply,
)


class OptimisticModeTests(MockedBleTransportTestCase):
    """``optimistic=True`` returns on a confirmed write with no ack wait."""

    async def test_vcsec_returns_on_write_without_waiting(self) -> None:
        vehicle, send = self.make_vehicle(optimistic=True)
        # No return_value/side_effect scripted: if the code waited on the
        # reply it would receive a bare MagicMock and fail decoding it.

        result = await vehicle.door_lock()

        self.assertEqual(result, {"response": {"result": True, "reason": ""}})
        send.assert_awaited_once()

    async def test_infotainment_returns_on_write_without_waiting(self) -> None:
        vehicle, send = self.make_vehicle(optimistic=True)

        result = await vehicle.honk_horn()

        self.assertEqual(result, {"response": {"result": True, "reason": ""}})
        send.assert_awaited_once()

    async def test_write_failure_still_raises(self) -> None:
        vehicle, send = self.make_vehicle(optimistic=True)
        send.side_effect = BluetoothTransportError()

        with self.assertRaises(BluetoothTransportError):
            await vehicle.door_lock()

    async def test_non_mutating_infotainment_is_unaffected(self) -> None:
        # ping() always waits for its real reply; optimistic mode is only for
        # mutating commands.
        vehicle, send = self.make_vehicle(optimistic=True)
        send.return_value = infotainment_action_ok_reply()

        result = await vehicle.ping()

        self.assertEqual(result["response"]["result"], True)
        send.assert_awaited_once()

    async def test_optimistic_and_raise_unconfirmed_combo_is_moot_not_error(
        self,
    ) -> None:
        # confirmation="optimistic" makes raise_unconfirmed irrelevant rather
        # than an error - optimistic never reaches an unconfirmed outcome to
        # apply it to, and construction/use with both set must not raise.
        vehicle, send = self.make_vehicle(
            confirmation="optimistic", raise_unconfirmed=True
        )

        result = await vehicle.door_lock()

        self.assertEqual(result, {"response": {"result": True, "reason": ""}})
        send.assert_awaited_once()


class RaiseUnconfirmedTests(MockedBleTransportTestCase):
    """``raise_unconfirmed=False`` converts only the truly-unconfirmed case."""

    async def test_default_still_raises(self) -> None:
        vehicle, send = self.make_vehicle()
        send.side_effect = BluetoothTimeout()

        with self.assertRaises(BluetoothUnconfirmedCommand):
            await vehicle.door_lock()

    async def test_no_verify_commands_resolves_best_effort(self) -> None:
        vehicle, send = self.make_vehicle(raise_unconfirmed=False)
        send.side_effect = BluetoothTimeout()

        result = await vehicle.door_lock()

        self.assertEqual(result, {"response": {"result": True, "reason": ""}})

    async def test_infotainment_resolves_best_effort(self) -> None:
        vehicle, send = self.make_vehicle(raise_unconfirmed=False)
        send.side_effect = BluetoothTimeout()

        result = await vehicle.honk_horn()

        self.assertEqual(result, {"response": {"result": True, "reason": ""}})

    async def test_verify_commands_unresolvable_resolves_best_effort(self) -> None:
        # verify_commands on, but the command has no verify plan at all
        # (honk_horn is ack-only) - still exhausted, still convertible.
        vehicle, send = self.make_vehicle(verify_commands=True, raise_unconfirmed=False)
        send.side_effect = BluetoothTimeout()

        result = await vehicle.honk_horn()

        self.assertEqual(result, {"response": {"result": True, "reason": ""}})

    async def test_verify_commands_read_failure_resolves_best_effort(self) -> None:
        # verify_commands on, has a plan, but the prover read itself fails
        # (e.g. asleep car) - still an ambiguous, convertible outcome.
        vehicle, send = self.make_vehicle(verify_commands=True, raise_unconfirmed=False)
        send.side_effect = [BluetoothTimeout(), BluetoothTimeout()]

        result = await vehicle.door_lock()

        self.assertEqual(result, {"response": {"result": True, "reason": ""}})

    async def test_verify_commands_confirmed_success_is_unaffected(self) -> None:
        vehicle, send = self.make_vehicle(verify_commands=True, raise_unconfirmed=False)
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

    async def test_verify_commands_mismatch_still_raises(self) -> None:
        # A prover read that disagrees is affirmative evidence, not mere
        # absence of confirmation - it must raise BluetoothCommandFailed
        # regardless of raise_unconfirmed.
        vehicle, send = self.make_vehicle(verify_commands=True, raise_unconfirmed=False)
        send.side_effect = [
            BluetoothTimeout(),
            vcsec_vehicle_status_reply(
                VehicleStatus(
                    vehicleLockState=VehicleLockState_E.VEHICLELOCKSTATE_UNLOCKED
                )
            ),
        ]

        with self.assertRaises(BluetoothCommandFailed):
            await vehicle.door_lock()

    async def test_write_failure_still_raises(self) -> None:
        vehicle, send = self.make_vehicle(raise_unconfirmed=False)
        send.side_effect = BluetoothTransportError()

        with self.assertRaises(BluetoothTransportError):
            await vehicle.door_lock()

    async def test_non_mutating_timeout_still_raises_plain_timeout(self) -> None:
        vehicle, send = self.make_vehicle(raise_unconfirmed=False)
        send.side_effect = BluetoothTimeout()

        with self.assertRaises(BluetoothTimeout) as ctx:
            await vehicle.ping()

        self.assertNotIsInstance(ctx.exception, BluetoothUnconfirmedCommand)

    async def test_read_timeout_still_raises_plain_timeout(self) -> None:
        # A read (no mutation) is unaffected by raise_unconfirmed.
        vehicle, send = self.make_vehicle(raise_unconfirmed=False)
        send.side_effect = BluetoothTimeout()

        with self.assertRaises(BluetoothTimeout) as ctx:
            await vehicle.charge_state()

        self.assertNotIsInstance(ctx.exception, BluetoothUnconfirmedCommand)
