"""An unconfirmed infotainment command to a sleeping car must not resolve as
best-effort success: a sleeping infotainment computer cannot have run it. By
default the car is woken over BLE and the command resent; with
``wake_if_asleep=False`` it raises so ``VehicleRouter`` can fall back to the
cloud.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock

from tesla_fleet_api.exceptions import BluetoothCommandFailed, BluetoothTimeout
from tesla_fleet_api.router import VehicleRouter
from tesla_fleet_api.tesla.bluetooth import TeslaBluetooth
from tesla_fleet_api.tesla.vehicle.bluetooth import VehicleBluetooth
from tesla_protocol.command.car_server_pb2 import Action
from tesla_protocol.command.universal_message_pb2 import Domain, RoutableMessage
from tesla_protocol.command.vcsec_pb2 import (
    RKEAction_E,
    UnsignedMessage,
    VehicleSleepStatus_E,
    VehicleStatus,
)

from ble_mocked_transport import (
    MockedBleTransportTestCase,
    decrypt_sent_command,
    infotainment_action_ok_reply,
    vcsec_ok_reply,
    vcsec_vehicle_status_reply,
)

ASLEEP = VehicleSleepStatus_E.VEHICLE_SLEEP_STATUS_ASLEEP
AWAKE = VehicleSleepStatus_E.VEHICLE_SLEEP_STATUS_AWAKE


def sleep_status_reply(status: int) -> RoutableMessage:
    return vcsec_vehicle_status_reply(VehicleStatus(vehicleSleepStatus=status))


def sent_messages(vehicle: VehicleBluetooth[Any], send: Any) -> list[tuple[str, Any]]:
    """Decode each message handed to ``_send`` as ("vcsec"|"info"|"handshake", proto)."""
    out: list[tuple[str, Any]] = []
    for call in send.await_args_list:
        msg = call.args[0]
        if msg.HasField("session_info_request"):
            out.append(("handshake", msg))
            continue
        plain = decrypt_sent_command(vehicle, msg)
        if msg.to_destination.domain == Domain.DOMAIN_VEHICLE_SECURITY:
            out.append(("vcsec", UnsignedMessage.FromString(plain)))
        else:
            out.append(("info", Action.FromString(plain)))
    return out


class _FakeCloudFallback:
    def __init__(self, vin: str) -> None:
        self.vin = vin
        self.calls = 0

    async def set_charge_limit(self, percent: int) -> dict[str, Any]:
        self.calls += 1
        return {"response": {"result": True, "reason": "cloud"}}


class WakeIfAsleepTests(MockedBleTransportTestCase):
    async def test_asleep_wakes_over_ble_and_resends(self) -> None:
        vehicle, send = self.make_vehicle(raise_unconfirmed=False)
        send.side_effect = [
            BluetoothTimeout(),
            sleep_status_reply(ASLEEP),
            vcsec_ok_reply(),
            RoutableMessage(),
            infotainment_action_ok_reply(),
        ]

        result = await vehicle.set_charge_limit(80)

        self.assertEqual(result["response"]["result"], True)
        sent = sent_messages(vehicle, send)
        self.assertEqual(
            [domain for domain, _ in sent],
            ["info", "vcsec", "vcsec", "handshake", "info"],
        )
        self.assertEqual(sent[2][1].RKEAction, RKEAction_E.RKE_ACTION_WAKE_VEHICLE)
        self.assertEqual(sent[4][1], sent[0][1])

    async def test_still_asleep_after_wake_falls_back_to_cloud(self) -> None:
        vehicle, send = self.make_vehicle(raise_unconfirmed=False)
        setattr(vehicle, "_wake_timeout", 0.05)

        async def car(msg: RoutableMessage, *args: Any, **kwargs: Any) -> Any:
            if msg.HasField("session_info_request"):
                raise BluetoothTimeout()
            if msg.to_destination.domain == Domain.DOMAIN_INFOTAINMENT:
                raise BluetoothTimeout()
            plain = UnsignedMessage.FromString(decrypt_sent_command(vehicle, msg))
            if plain.HasField("RKEAction"):
                return vcsec_ok_reply()
            return sleep_status_reply(ASLEEP)

        send.side_effect = car
        cloud = _FakeCloudFallback(vehicle.vin)

        result = await VehicleRouter(vehicle, cloud).set_charge_limit(80)

        self.assertEqual(cloud.calls, 1)
        self.assertEqual(result["response"]["reason"], "cloud")


class WakeDisabledTests(MockedBleTransportTestCase):
    def make_vehicle_no_wake(self) -> tuple[VehicleBluetooth[Any], Any]:
        vehicle, send = self.make_vehicle(raise_unconfirmed=False)
        vehicle.wake_if_asleep = False
        return vehicle, send

    async def test_asleep_raises_command_failed(self) -> None:
        vehicle, send = self.make_vehicle_no_wake()
        send.side_effect = [BluetoothTimeout(), sleep_status_reply(ASLEEP)]

        with self.assertRaises(BluetoothCommandFailed):
            await vehicle.set_charge_limit(80)

    async def test_asleep_falls_back_to_cloud(self) -> None:
        vehicle, send = self.make_vehicle_no_wake()
        send.side_effect = [BluetoothTimeout(), sleep_status_reply(ASLEEP)]
        cloud = _FakeCloudFallback(vehicle.vin)

        result = await VehicleRouter(vehicle, cloud).set_charge_limit(80)

        self.assertEqual(cloud.calls, 1)
        self.assertEqual(result["response"]["reason"], "cloud")

    def test_factory_forwards_flag(self) -> None:
        vehicles = TeslaBluetooth().vehicles
        self.assertTrue(vehicles.createBluetooth(self.VIN, False).wake_if_asleep)
        self.assertFalse(
            vehicles.createBluetooth(
                self.VIN, False, wake_if_asleep=False
            ).wake_if_asleep
        )


class NotAsleepTests(MockedBleTransportTestCase):
    async def test_awake_stays_best_effort(self) -> None:
        vehicle, send = self.make_vehicle(raise_unconfirmed=False)
        send.side_effect = [BluetoothTimeout(), sleep_status_reply(AWAKE)]

        result = await vehicle.set_charge_limit(80)

        self.assertEqual(result, {"response": {"result": True, "reason": ""}})
        self.assertEqual(send.await_count, 2)

    async def test_unreadable_sleep_status_stays_best_effort(self) -> None:
        vehicle, send = self.make_vehicle(raise_unconfirmed=False)
        send.side_effect = BluetoothTimeout()

        result = await vehicle.set_charge_limit(80)

        self.assertEqual(result, {"response": {"result": True, "reason": ""}})


class _SessionlessTestCase(MockedBleTransportTestCase):
    def make_sessionless(self) -> tuple[VehicleBluetooth[Any], Any]:
        vehicle, send = self.make_vehicle(raise_unconfirmed=False)
        self.info_session = getattr(vehicle, "_sessions")[Domain.DOMAIN_INFOTAINMENT]
        self.info_session.epoch = None
        return vehicle, send


class HandshakeOnSleepingCarTests(_SessionlessTestCase):
    """No INFO session yet (fresh process or reconnect): the handshake itself
    is what times out on a sleeping car, before any command is sent."""

    async def test_wakes_then_sends_once_infotainment_answers(self) -> None:
        vehicle, send = self.make_sessionless()
        handshakes = 0

        async def car(msg: RoutableMessage, *args: Any, **kwargs: Any) -> Any:
            nonlocal handshakes
            if msg.HasField("session_info_request"):
                handshakes += 1
                if handshakes == 1:
                    raise BluetoothTimeout()
                self.info_session.epoch = b"\x00" * 16
                return RoutableMessage()
            if msg.to_destination.domain == Domain.DOMAIN_INFOTAINMENT:
                return infotainment_action_ok_reply()
            plain = UnsignedMessage.FromString(decrypt_sent_command(vehicle, msg))
            if plain.HasField("RKEAction"):
                return vcsec_ok_reply()
            return sleep_status_reply(ASLEEP)

        send.side_effect = car

        result = await vehicle.set_charge_limit(80)

        self.assertEqual(result["response"]["result"], True)
        self.assertEqual(
            [domain for domain, _ in sent_messages(vehicle, send)],
            ["handshake", "vcsec", "vcsec", "handshake", "info"],
        )

    async def test_wake_disabled_does_not_wake(self) -> None:
        vehicle, send = self.make_sessionless()
        vehicle.wake_if_asleep = False
        send.side_effect = [BluetoothTimeout(), sleep_status_reply(ASLEEP)]

        with self.assertRaises(BluetoothTimeout):
            await vehicle.set_charge_limit(80)
        self.assertEqual(send.await_count, 2)

    async def test_unreadable_sleep_status_raises(self) -> None:
        vehicle, send = self.make_sessionless()
        send.side_effect = BluetoothTimeout()

        with self.assertRaises(BluetoothTimeout):
            await vehicle.set_charge_limit(80)
        self.assertEqual(send.await_count, 2)


class AwakeButBootingTests(_SessionlessTestCase):
    """VCSEC reports awake seconds before infotainment answers a handshake
    (e.g. a car just woken by a phone key): retry the handshake, never wake."""

    def script(self, vehicle: VehicleBluetooth[Any], ready_on: int | None) -> list[str]:
        sent: list[str] = []

        async def car(msg: RoutableMessage, *args: Any, **kwargs: Any) -> Any:
            if msg.HasField("session_info_request"):
                sent.append("handshake")
                if sent.count("handshake") != ready_on:
                    raise BluetoothTimeout()
                self.info_session.epoch = b"\x00" * 16
                return RoutableMessage()
            if msg.to_destination.domain == Domain.DOMAIN_INFOTAINMENT:
                sent.append("info")
                return infotainment_action_ok_reply()
            plain = UnsignedMessage.FromString(decrypt_sent_command(vehicle, msg))
            sent.append("wake" if plain.HasField("RKEAction") else "status")
            return sleep_status_reply(AWAKE)

        setattr(vehicle, "_send", AsyncMock(side_effect=car))
        return sent

    async def test_retries_handshake_until_infotainment_answers(self) -> None:
        vehicle, _ = self.make_sessionless()
        sent = self.script(vehicle, ready_on=4)

        result = await vehicle.set_charge_limit(80)

        self.assertEqual(result["response"]["result"], True)
        self.assertEqual(
            sent, ["handshake", "status", "handshake", "handshake", "handshake", "info"]
        )

    async def test_retries_even_with_wake_disabled(self) -> None:
        vehicle, _ = self.make_sessionless()
        vehicle.wake_if_asleep = False
        sent = self.script(vehicle, ready_on=2)

        await vehicle.set_charge_limit(80)

        self.assertNotIn("wake", sent)
        self.assertEqual(sent[-1], "info")

    async def test_never_answers_raises_timeout(self) -> None:
        vehicle, _ = self.make_sessionless()
        setattr(vehicle, "_infotainment_boot_timeout", 0.05)
        sent = self.script(vehicle, ready_on=None)

        with self.assertRaises(BluetoothTimeout):
            await vehicle.set_charge_limit(80)
        self.assertNotIn("wake", sent)
        self.assertNotIn("info", sent)
