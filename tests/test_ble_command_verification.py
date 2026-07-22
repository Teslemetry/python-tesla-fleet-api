"""Tests for opt-in post-timeout command verification on ``VehicleBluetooth``.

A ``BluetoothTimeout`` from a mutating BLE command is inconclusive - the vehicle
can execute the command without its ack reaching the client. With
``verify_commands=True``, a timed-out mutation whose expected post-state is
derivable from its arguments is confirmed by reading the mapped prover state:
verified-executed returns a normal success result, verified-not-executed raises
``BluetoothCommandFailed`` (proven non-application, not ambiguity), and an
unverifiable command re-raises the timeout unchanged. With the default
(``verify_commands=False``) every path is byte-identical to today, and no
verification read is ever issued.

The single mocked ``_send`` is scripted with a list ``side_effect``: the first
entry answers the command send (raise ``BluetoothTimeout`` to force the
ambiguous case), and the second, when present, answers the prover read.
"""

from __future__ import annotations

from tesla_fleet_api.exceptions import BluetoothCommandFailed, BluetoothTimeout
from tesla_protocol.command.vehicle_pb2 import (
    ChargeState,
    ClimateState,
    MediaState,
    VehicleData,
)
from tesla_protocol.command.vcsec_pb2 import (
    VehicleLockState_E,
    VehicleStatus,
)

from ble_mocked_transport import (
    MockedBleTransportTestCase,
    infotainment_action_ok_reply,
    infotainment_vehicle_data_reply,
    vcsec_ok_reply,
    vcsec_vehicle_status_reply,
)


class VcsecVerificationTests(MockedBleTransportTestCase):
    """Lock/unlock verify against the VCSEC ``vehicle_state`` lock field."""

    async def test_verified_executed_returns_success(self) -> None:
        vehicle, send = self.make_vehicle(verify_commands=True)
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
        # Command send + one prover read.
        self.assertEqual(send.await_count, 2)

    async def test_verified_not_executed_raises_command_failed(self) -> None:
        # A verify-read mismatch is proof the command did not apply, not
        # ambiguity - it raises BluetoothCommandFailed, not the timeout.
        vehicle, send = self.make_vehicle(verify_commands=True)
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
        self.assertEqual(send.await_count, 2)

    async def test_unlock_verified_executed(self) -> None:
        vehicle, send = self.make_vehicle(verify_commands=True)
        send.side_effect = [
            BluetoothTimeout(),
            vcsec_vehicle_status_reply(
                VehicleStatus(
                    vehicleLockState=VehicleLockState_E.VEHICLELOCKSTATE_UNLOCKED
                )
            ),
        ]

        result = await vehicle.door_unlock()

        self.assertEqual(result, {"response": {"result": True, "reason": ""}})

    async def test_unverifiable_vcsec_command_reraises_without_read(self) -> None:
        # A closure move has no derivable lock prover.
        vehicle, send = self.make_vehicle(verify_commands=True)
        send.side_effect = [BluetoothTimeout()]

        with self.assertRaises(BluetoothTimeout):
            await vehicle.charge_port_door_open()
        # No prover read issued for an unverifiable command.
        self.assertEqual(send.await_count, 1)


class InfotainmentVerificationTests(MockedBleTransportTestCase):
    async def test_set_charge_limit_verified_executed(self) -> None:
        vehicle, send = self.make_vehicle(verify_commands=True)
        send.side_effect = [
            BluetoothTimeout(),
            infotainment_vehicle_data_reply(
                VehicleData(charge_state=ChargeState(charge_limit_soc=80))
            ),
        ]

        result = await vehicle.set_charge_limit(80)

        self.assertEqual(result, {"response": {"result": True, "reason": ""}})
        self.assertEqual(send.await_count, 2)

    async def test_set_charge_limit_mismatch_raises_command_failed(self) -> None:
        vehicle, send = self.make_vehicle(verify_commands=True)
        send.side_effect = [
            BluetoothTimeout(),
            infotainment_vehicle_data_reply(
                VehicleData(charge_state=ChargeState(charge_limit_soc=70))
            ),
        ]

        with self.assertRaises(BluetoothCommandFailed):
            await vehicle.set_charge_limit(80)

    async def test_set_charging_amps_verified_executed(self) -> None:
        vehicle, send = self.make_vehicle(verify_commands=True)
        send.side_effect = [
            BluetoothTimeout(),
            infotainment_vehicle_data_reply(
                VehicleData(charge_state=ChargeState(charging_amps=16))
            ),
        ]

        result = await vehicle.set_charging_amps(16)

        self.assertEqual(result, {"response": {"result": True, "reason": ""}})

    async def test_adjust_volume_verified_executed(self) -> None:
        vehicle, send = self.make_vehicle(verify_commands=True)
        send.side_effect = [
            BluetoothTimeout(),
            infotainment_vehicle_data_reply(
                VehicleData(media_state=MediaState(audio_volume=5.0))
            ),
        ]

        result = await vehicle.adjust_volume(5.0)

        self.assertEqual(result, {"response": {"result": True, "reason": ""}})

    async def test_relative_volume_step_is_unverifiable(self) -> None:
        # media_volume_up sends a relative delta - not derivable without a
        # pre-read, so it stays inconclusive and re-raises.
        vehicle, send = self.make_vehicle(verify_commands=True)
        send.side_effect = [BluetoothTimeout()]

        with self.assertRaises(BluetoothTimeout):
            await vehicle.media_volume_up()
        self.assertEqual(send.await_count, 1)

    async def test_set_temps_verified_executed(self) -> None:
        vehicle, send = self.make_vehicle(verify_commands=True)
        send.side_effect = [
            BluetoothTimeout(),
            infotainment_vehicle_data_reply(
                VehicleData(
                    climate_state=ClimateState(
                        driver_temp_setting=21.0, passenger_temp_setting=21.0
                    )
                )
            ),
        ]

        result = await vehicle.set_temps(21.0, 21.0)

        self.assertEqual(result, {"response": {"result": True, "reason": ""}})

    async def test_auto_conditioning_start_verified_executed(self) -> None:
        vehicle, send = self.make_vehicle(verify_commands=True)
        send.side_effect = [
            BluetoothTimeout(),
            infotainment_vehicle_data_reply(
                VehicleData(climate_state=ClimateState(is_climate_on=True))
            ),
        ]

        result = await vehicle.auto_conditioning_start()

        self.assertEqual(result, {"response": {"result": True, "reason": ""}})

    async def test_unverifiable_infotainment_command_reraises_without_read(
        self,
    ) -> None:
        # honk_horn is ack-only with no derivable prover.
        vehicle, send = self.make_vehicle(verify_commands=True)
        send.side_effect = [BluetoothTimeout()]

        with self.assertRaises(BluetoothTimeout):
            await vehicle.honk_horn()
        self.assertEqual(send.await_count, 1)

    async def test_prover_read_timeout_reraises_original(self) -> None:
        # The prover read itself times out (e.g. car asleep for an INFO read):
        # fall back to raising rather than waking the car to verify.
        vehicle, send = self.make_vehicle(verify_commands=True)
        send.side_effect = [BluetoothTimeout(), BluetoothTimeout()]

        with self.assertRaises(BluetoothTimeout):
            await vehicle.set_charge_limit(80)
        self.assertEqual(send.await_count, 2)


class VerificationDisabledTests(MockedBleTransportTestCase):
    """Default (verify off) must be byte-identical to today."""

    async def test_timeout_reraises_without_verification_read(self) -> None:
        vehicle, send = self.make_vehicle()  # verify_commands defaults to False
        send.side_effect = [BluetoothTimeout()]

        with self.assertRaises(BluetoothTimeout):
            await vehicle.door_lock()
        # No prover read when verification is disabled.
        self.assertEqual(send.await_count, 1)

    async def test_infotainment_timeout_reraises_without_read(self) -> None:
        vehicle, send = self.make_vehicle()
        send.side_effect = [BluetoothTimeout()]

        with self.assertRaises(BluetoothTimeout):
            await vehicle.set_charge_limit(80)
        self.assertEqual(send.await_count, 1)


class HappyPathTimingTests(MockedBleTransportTestCase):
    """With verify on, a normal ack must NOT trigger a verification read."""

    async def test_vcsec_success_issues_no_verification_read(self) -> None:
        vehicle, send = self.make_vehicle(verify_commands=True)
        send.return_value = vcsec_ok_reply()

        result = await vehicle.door_lock()

        self.assertEqual(result, {"response": {"result": True, "reason": ""}})
        # Only the command send; the happy path never reads the prover.
        self.assertEqual(send.await_count, 1)

    async def test_infotainment_success_issues_no_verification_read(self) -> None:
        vehicle, send = self.make_vehicle(verify_commands=True)
        send.return_value = infotainment_action_ok_reply()

        result = await vehicle.set_charge_limit(80)

        self.assertEqual(result, {"response": {"result": True, "reason": ""}})
        self.assertEqual(send.await_count, 1)
