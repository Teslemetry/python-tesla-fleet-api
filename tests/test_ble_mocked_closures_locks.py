"""Regression tests for the closures/locks command group over the mocked BLE transport.

Covers ``door_unlock``, ``auto_secure_vehicle``, ``charge_port_door_open/close``
(all VCSEC, inherited from ``Commands``) and the 8 individual door open/close
commands (VCSEC, defined on ``VehicleBluetooth`` - no cloud REST equivalent).
``door_lock`` is already covered in ``test_ble_mocked_commands.py``.

Live-verify status: ``door_lock``/``door_unlock``/``auto_secure_vehicle`` are
live-verified (full snapshot->act->verify->restore->confirm cycle against the
test car). ``charge_port_door_open/close`` and the 8 individual door commands
are unit-test-only here - mocked-transport coverage only, no live actuation.
``charge_port_door_*`` is deferred because the test car had a charge cable
physically engaged (closing over an engaged latch is unsafe to test remotely).
The individual doors are deferred because an ``open_*_door()`` unlatches the
door but there is no reliable powered close on this Model 3 - one live probe
left a door physically ajar needing a human push to close (see the BLE
individual-door powered-close gotcha in AGENTS.md). Treat these the same as
the CAPTAIN-PRESENT group: live-verify only in a captain-present session.
"""

from tesla_protocol.command.universal_message_pb2 import Domain
from tesla_protocol.command.vcsec_pb2 import (
    ClosureMoveType_E,
    RKEAction_E,
    UnsignedMessage,
)

from ble_mocked_transport import (
    MockedBleTransportTestCase,
    decrypt_sent_command,
    vcsec_ok_reply,
)


class DoorUnlockTests(MockedBleTransportTestCase):
    async def test_sends_rke_unlock_and_decodes_ok_reply(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = vcsec_ok_reply()

        result = await vehicle.door_unlock()

        self.assertEqual(result, {"response": {"result": True, "reason": ""}})
        sent_msg = send.await_args.args[0]
        self.assertEqual(sent_msg.to_destination.domain, Domain.DOMAIN_VEHICLE_SECURITY)

        plaintext = decrypt_sent_command(vehicle, sent_msg)
        unsigned = UnsignedMessage.FromString(plaintext)
        self.assertEqual(unsigned.RKEAction, RKEAction_E.RKE_ACTION_UNLOCK)


class AutoSecureVehicleTests(MockedBleTransportTestCase):
    async def test_sends_rke_auto_secure_and_decodes_ok_reply(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = vcsec_ok_reply()

        result = await vehicle.auto_secure_vehicle()

        self.assertEqual(result, {"response": {"result": True, "reason": ""}})
        sent_msg = send.await_args.args[0]
        self.assertEqual(sent_msg.to_destination.domain, Domain.DOMAIN_VEHICLE_SECURITY)

        plaintext = decrypt_sent_command(vehicle, sent_msg)
        unsigned = UnsignedMessage.FromString(plaintext)
        self.assertEqual(unsigned.RKEAction, RKEAction_E.RKE_ACTION_AUTO_SECURE_VEHICLE)


class ChargePortDoorTests(MockedBleTransportTestCase):
    async def test_open_sends_closure_move_open(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = vcsec_ok_reply()

        result = await vehicle.charge_port_door_open()

        self.assertEqual(result, {"response": {"result": True, "reason": ""}})
        sent_msg = send.await_args.args[0]
        plaintext = decrypt_sent_command(vehicle, sent_msg)
        unsigned = UnsignedMessage.FromString(plaintext)
        self.assertEqual(
            unsigned.closureMoveRequest.chargePort,
            ClosureMoveType_E.CLOSURE_MOVE_TYPE_OPEN,
        )

    async def test_close_sends_closure_move_close(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = vcsec_ok_reply()

        result = await vehicle.charge_port_door_close()

        self.assertEqual(result, {"response": {"result": True, "reason": ""}})
        sent_msg = send.await_args.args[0]
        plaintext = decrypt_sent_command(vehicle, sent_msg)
        unsigned = UnsignedMessage.FromString(plaintext)
        self.assertEqual(
            unsigned.closureMoveRequest.chargePort,
            ClosureMoveType_E.CLOSURE_MOVE_TYPE_CLOSE,
        )


class IndividualDoorTests(MockedBleTransportTestCase):
    """The 8 individual door commands - each sets exactly one ``ClosureMoveRequest`` field."""

    DOORS = [
        (
            "open_front_driver_door",
            "frontDriverDoor",
            ClosureMoveType_E.CLOSURE_MOVE_TYPE_OPEN,
        ),
        (
            "close_front_driver_door",
            "frontDriverDoor",
            ClosureMoveType_E.CLOSURE_MOVE_TYPE_CLOSE,
        ),
        (
            "open_front_passenger_door",
            "frontPassengerDoor",
            ClosureMoveType_E.CLOSURE_MOVE_TYPE_OPEN,
        ),
        (
            "close_front_passenger_door",
            "frontPassengerDoor",
            ClosureMoveType_E.CLOSURE_MOVE_TYPE_CLOSE,
        ),
        (
            "open_rear_driver_door",
            "rearDriverDoor",
            ClosureMoveType_E.CLOSURE_MOVE_TYPE_OPEN,
        ),
        (
            "close_rear_driver_door",
            "rearDriverDoor",
            ClosureMoveType_E.CLOSURE_MOVE_TYPE_CLOSE,
        ),
        (
            "open_rear_passenger_door",
            "rearPassengerDoor",
            ClosureMoveType_E.CLOSURE_MOVE_TYPE_OPEN,
        ),
        (
            "close_rear_passenger_door",
            "rearPassengerDoor",
            ClosureMoveType_E.CLOSURE_MOVE_TYPE_CLOSE,
        ),
    ]

    async def test_each_door_command_sets_only_its_own_field(self) -> None:
        for method_name, field_name, expected_move in self.DOORS:
            with self.subTest(method=method_name):
                vehicle, send = self.make_vehicle()
                send.return_value = vcsec_ok_reply()

                result = await getattr(vehicle, method_name)()

                self.assertEqual(result, {"response": {"result": True, "reason": ""}})
                sent_msg = send.await_args.args[0]
                self.assertEqual(
                    sent_msg.to_destination.domain, Domain.DOMAIN_VEHICLE_SECURITY
                )

                plaintext = decrypt_sent_command(vehicle, sent_msg)
                unsigned = UnsignedMessage.FromString(plaintext)
                request = unsigned.closureMoveRequest
                self.assertEqual(getattr(request, field_name), expected_move)

                for other_field in (
                    "frontDriverDoor",
                    "frontPassengerDoor",
                    "rearDriverDoor",
                    "rearPassengerDoor",
                    "rearTrunk",
                    "frontTrunk",
                    "chargePort",
                    "tonneau",
                ):
                    if other_field == field_name:
                        continue
                    self.assertEqual(
                        getattr(request, other_field),
                        ClosureMoveType_E.CLOSURE_MOVE_TYPE_NONE,
                        f"{method_name} unexpectedly set {other_field}",
                    )
