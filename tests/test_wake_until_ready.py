"""``wake_up(wait=True)`` blocks until the vehicle can take commands.

Over BLE, VCSEC reports awake ~0.5s after an RKE wake but infotainment only
answers a session handshake 6-9s later (measured live), so readiness is proven
by polling that handshake, never by VCSEC status or broadcasts. Over the Fleet
API the wake request returns immediately, so readiness is polling ``vehicle()``
for ``state == "online"``.
"""

from __future__ import annotations

from typing import Any
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, MagicMock

from tesla_fleet_api.exceptions import (
    BluetoothTimeout,
    BluetoothUnconfirmedCommand,
    VehicleOffline,
)
from tesla_fleet_api.tesla.vehicle.bluetooth import VehicleBluetooth
from tesla_fleet_api.tesla.vehicle.fleet import VehicleFleet
from tesla_protocol.command.universal_message_pb2 import RoutableMessage
from tesla_protocol.command.vcsec_pb2 import RKEAction_E, UnsignedMessage

from ble_mocked_transport import (
    VIN,
    MockedBleTransportTestCase,
    decrypt_sent_command,
    vcsec_ok_reply,
)


class ScriptedCar:
    """Fake ``_send``: acks every wake; infotainment answers the Nth handshake."""

    def __init__(
        self,
        vehicle: VehicleBluetooth[Any],
        ready_on_handshake: int | None,
        wake_error: BaseException | None = None,
    ) -> None:
        self.vehicle = vehicle
        self.ready_on_handshake = ready_on_handshake
        self.wake_error = wake_error
        self.sent: list[str] = []

    async def __call__(self, msg: RoutableMessage, *args: Any, **kwargs: Any) -> Any:
        if msg.HasField("session_info_request"):
            self.sent.append("handshake")
            if self.sent.count("handshake") != self.ready_on_handshake:
                raise BluetoothTimeout()
            return RoutableMessage()
        plain = UnsignedMessage.FromString(decrypt_sent_command(self.vehicle, msg))
        assert plain.RKEAction == RKEAction_E.RKE_ACTION_WAKE_VEHICLE
        self.sent.append("wake")
        if self.wake_error is not None:
            raise self.wake_error
        return vcsec_ok_reply()


class BluetoothWakeUpTests(MockedBleTransportTestCase):
    def script(
        self, ready_on_handshake: int | None, **kwargs: Any
    ) -> tuple[VehicleBluetooth[Any], ScriptedCar]:
        vehicle, send = self.make_vehicle(raise_unconfirmed=False)
        car = ScriptedCar(vehicle, ready_on_handshake, **kwargs)
        send.side_effect = car.__call__
        return vehicle, car

    async def test_default_only_sends_the_wake(self) -> None:
        vehicle, car = self.script(ready_on_handshake=1)

        await vehicle.wake_up()

        self.assertEqual(car.sent, ["wake"])

    async def test_wait_polls_handshake_until_infotainment_answers(self) -> None:
        vehicle, car = self.script(ready_on_handshake=3)

        result = await vehicle.wake_up(wait=True)

        self.assertEqual(result, {"response": {"result": True, "reason": ""}})
        self.assertEqual(car.sent, ["wake", "handshake", "handshake", "handshake"])

    async def test_wait_probes_even_with_a_cached_session(self) -> None:
        # make_vehicle pre-marks the INFO session ready; a cached session says
        # nothing about whether the car is awake now.
        vehicle, car = self.script(ready_on_handshake=1)

        await vehicle.wake_up(wait=True)

        self.assertEqual(car.sent, ["wake", "handshake"])

    async def test_wait_resends_wake_while_not_ready(self) -> None:
        vehicle, car = self.script(ready_on_handshake=2)
        setattr(vehicle, "_wake_resend_interval", 0)

        await vehicle.wake_up(wait=True)

        self.assertEqual(car.sent, ["wake", "handshake", "wake", "handshake"])

    async def test_unconfirmed_wake_still_probes(self) -> None:
        vehicle, car = self.script(
            ready_on_handshake=1, wake_error=BluetoothUnconfirmedCommand()
        )

        await vehicle.wake_up(wait=True)

        self.assertEqual(car.sent, ["wake", "handshake"])

    async def test_wait_times_out(self) -> None:
        vehicle, _ = self.script(ready_on_handshake=None)

        with self.assertRaises(BluetoothTimeout):
            await vehicle.wake_up(wait=True, timeout=0.05)


class FleetWakeUpTests(IsolatedAsyncioTestCase):
    def make_vehicle(self, states: list[str]) -> tuple[VehicleFleet[Any], AsyncMock]:
        parent = MagicMock()
        replies = [{"response": {"state": state}} for state in states]
        parent._request = AsyncMock(side_effect=replies)
        vehicle = VehicleFleet(parent, VIN)
        setattr(vehicle, "_wake_poll_interval", 0)
        return vehicle, parent._request

    async def test_default_returns_the_wake_response(self) -> None:
        vehicle, request = self.make_vehicle(["asleep"])

        result = await vehicle.wake_up()

        self.assertEqual(result["response"]["state"], "asleep")
        self.assertEqual(request.await_count, 1)

    async def test_wait_polls_vehicle_until_online(self) -> None:
        vehicle, request = self.make_vehicle(["asleep", "asleep", "online"])

        result = await vehicle.wake_up(wait=True)

        self.assertEqual(result["response"]["state"], "online")
        paths = [call.args[1] for call in request.await_args_list]
        self.assertEqual(
            paths,
            [
                f"api/1/vehicles/{VIN}/wake_up",
                f"api/1/vehicles/{VIN}",
                f"api/1/vehicles/{VIN}",
            ],
        )

    async def test_wait_returns_immediately_when_already_online(self) -> None:
        vehicle, request = self.make_vehicle(["online"])

        await vehicle.wake_up(wait=True)

        self.assertEqual(request.await_count, 1)

    async def test_wait_times_out(self) -> None:
        vehicle, _ = self.make_vehicle(["asleep"] * 5)
        setattr(vehicle, "_wake_poll_interval", 1)

        with self.assertRaises(VehicleOffline):
            await vehicle.wake_up(wait=True, timeout=0.5)
