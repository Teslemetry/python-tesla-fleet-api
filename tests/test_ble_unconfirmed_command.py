"""Tests for the pre-write vs. post-write BLE timeout distinction.

A GATT-write failure (connect/notify/write) before a command reaches the
vehicle is a genuine transport failure and keeps raising
``BluetoothTransportError``. An ack-wait timeout for a *mutating* command
already written to the vehicle is unconfirmed, not failed - the vehicle may
have executed it anyway (lock/unlock have both been observed to execute
despite a lost ack) - and now raises ``BluetoothUnconfirmedCommand`` instead
of plain ``BluetoothTimeout``, so a caller such as ``Router`` can tell the two
apart and avoid blind-retrying or failing over to another transport. A read
(no mutation, nothing to have "executed") keeps raising plain
``BluetoothTimeout`` on the same kind of ack-wait timeout.

Uses the same mocked-``_send`` harness as ``test_ble_command_verification.py``.
"""

from __future__ import annotations

from typing import Any, cast

from tesla_fleet_api.exceptions import (
    BluetoothCommandFailed,
    BluetoothTimeout,
    BluetoothTransportError,
    BluetoothUnconfirmedCommand,
)
from tesla_protocol.command.universal_message_pb2 import Domain
from tesla_protocol.command.universal_message_pb2 import (
    Destination,
    RoutableMessage,
)
from tesla_protocol.command.vcsec_pb2 import (
    VehicleLockState_E,
    VehicleStatus,
)

from ble_mocked_transport import (
    MockedBleTransportTestCase,
    vcsec_vehicle_status_reply,
)


class MutatingCommandTimeoutTests(MockedBleTransportTestCase):
    """A lost ack for a mutating command raises the unconfirmed subclass."""

    async def test_vcsec_actuation_timeout_raises_unconfirmed(self) -> None:
        vehicle, send = self.make_vehicle()
        send.side_effect = BluetoothTimeout()

        with self.assertRaises(BluetoothUnconfirmedCommand):
            await vehicle.door_lock()

    async def test_infotainment_action_timeout_raises_unconfirmed(self) -> None:
        vehicle, send = self.make_vehicle()
        send.side_effect = BluetoothTimeout()

        with self.assertRaises(BluetoothUnconfirmedCommand):
            await vehicle.honk_horn()

    async def test_non_mutating_infotainment_timeout_raises_plain_timeout(
        self,
    ) -> None:
        vehicle, send = self.make_vehicle()
        send.side_effect = BluetoothTimeout()

        with self.assertRaises(BluetoothTimeout) as ctx:
            await vehicle.ping()

        self.assertNotIsInstance(ctx.exception, BluetoothUnconfirmedCommand)

    async def test_unconfirmed_is_still_a_bluetooth_timeout(self) -> None:
        # Existing `except BluetoothTimeout` handling (verify_commands,
        # pair()'s fast path) must keep working unchanged.
        vehicle, send = self.make_vehicle()
        send.side_effect = BluetoothTimeout()

        with self.assertRaises(BluetoothTimeout):
            await vehicle.door_lock()

    async def test_unconfirmed_chains_the_original_timeout(self) -> None:
        vehicle, send = self.make_vehicle()
        original = BluetoothTimeout()
        send.side_effect = original

        with self.assertRaises(BluetoothUnconfirmedCommand) as ctx:
            await vehicle.door_lock()

        self.assertIs(ctx.exception.__cause__, original)

    async def test_verify_commands_mismatch_raises_command_failed(self) -> None:
        # With verify_commands on, a prover read that disagrees is proof the
        # command did not apply, distinct from an unresolved ack timeout - it
        # raises BluetoothCommandFailed, not BluetoothUnconfirmedCommand.
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

    async def test_verify_commands_no_plan_still_raises_unconfirmed(self) -> None:
        # An ack timeout that verify_commands could not even attempt to
        # resolve (no plan for this command) stays genuinely ambiguous.
        vehicle, send = self.make_vehicle(verify_commands=True)
        send.side_effect = [BluetoothTimeout()]

        with self.assertRaises(BluetoothUnconfirmedCommand):
            await vehicle.charge_port_door_open()

    async def test_handshake_timeout_raises_plain_bluetooth_timeout(self) -> None:
        vehicle, send = self.make_vehicle()
        sessions = cast("dict[int, Any]", getattr(vehicle, "_sessions"))
        sessions[Domain.DOMAIN_VEHICLE_SECURITY].epoch = None
        send.side_effect = BluetoothTimeout()

        with self.assertRaises(BluetoothTimeout) as ctx:
            await vehicle.door_lock()

        self.assertNotIsInstance(ctx.exception, BluetoothUnconfirmedCommand)

    async def test_ack_only_handshake_raises_plain_bluetooth_timeout(self) -> None:
        vehicle, send = self.make_vehicle()
        sessions = cast("dict[int, Any]", getattr(vehicle, "_sessions"))
        sessions[Domain.DOMAIN_VEHICLE_SECURITY].epoch = None

        async def ack_only(
            msg: RoutableMessage, _requires: str, **_kwargs: Any
        ) -> RoutableMessage:
            return RoutableMessage(
                from_destination=Destination(domain=Domain.DOMAIN_VEHICLE_SECURITY),
                request_uuid=msg.uuid,
            )

        send.side_effect = ack_only

        with self.assertRaises(BluetoothTimeout) as ctx:
            await vehicle.door_lock()

        self.assertNotIsInstance(ctx.exception, BluetoothUnconfirmedCommand)
        send.assert_awaited_once()


class ReadTimeoutTests(MockedBleTransportTestCase):
    """A lost response for a read (no mutation) keeps raising plain BluetoothTimeout."""

    async def test_read_timeout_raises_plain_bluetooth_timeout(self) -> None:
        vehicle, send = self.make_vehicle()
        send.side_effect = BluetoothTimeout()

        with self.assertRaises(BluetoothTimeout) as ctx:
            await vehicle.charge_state()

        self.assertNotIsInstance(ctx.exception, BluetoothUnconfirmedCommand)


class TransportFailureTests(MockedBleTransportTestCase):
    """A pre-write transport failure is unaffected and stays distinguishable."""

    async def test_write_failure_raises_transport_error_not_unconfirmed(self) -> None:
        vehicle, send = self.make_vehicle()
        send.side_effect = BluetoothTransportError()

        with self.assertRaises(BluetoothTransportError) as ctx:
            await vehicle.door_lock()

        self.assertNotIsInstance(ctx.exception, BluetoothTimeout)
        self.assertNotIsInstance(ctx.exception, BluetoothUnconfirmedCommand)
