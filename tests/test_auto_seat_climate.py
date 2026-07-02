"""Regression tests for issue #11 — auto seat climate seat indexing.

The auto-seat-climate command is 1-indexed (``AutoSeat.FRONT_LEFT`` == 1),
matching Tesla's wire values and the proto ``AutoSeatPosition_*`` enum. Both the
Fleet REST path and the signed/protobuf path must agree on that convention for
the same input.
"""

from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, MagicMock

from cryptography.hazmat.primitives.asymmetric import ec

from tesla_fleet_api.const import AutoSeat, Method
from tesla_fleet_api.tesla.vehicle.commands import Commands
from tesla_fleet_api.tesla.vehicle.fleet import VehicleFleet
from tesla_fleet_api.tesla.vehicle.proto.car_server_pb2 import (
    Action,
    AutoSeatClimateAction,
)

VIN = "5YJXCAE43LF123456"


class _TestCommands(Commands):
    """Concrete ``Commands`` subclass so the ABC can be instantiated in tests."""

    _auth_method = "hmac"

    async def _send(self, msg, requires):  # pragma: no cover - never invoked
        raise NotImplementedError


class AutoSeatClimateFleetTests(IsolatedAsyncioTestCase):
    """The Fleet REST path sends the 1-indexed seat position verbatim."""

    def create_vehicle(self) -> tuple[VehicleFleet, AsyncMock]:
        parent = MagicMock()
        request = AsyncMock(return_value={"response": {"result": True}})
        parent._request = request  # pyright: ignore[reportAttributeAccessIssue]
        return VehicleFleet(parent, VIN), request

    async def test_front_left_sends_index_one(self) -> None:
        vehicle, request = self.create_vehicle()

        await vehicle.remote_auto_seat_climate_request(AutoSeat.FRONT_LEFT, True)

        request.assert_awaited_once_with(
            Method.POST,
            f"api/1/vehicles/{VIN}/command/remote_auto_seat_climate_request",
            json={"auto_seat_position": 1, "auto_climate_on": True},
        )

    async def test_front_right_sends_index_two(self) -> None:
        vehicle, request = self.create_vehicle()

        await vehicle.remote_auto_seat_climate_request(AutoSeat.FRONT_RIGHT, False)

        request.assert_awaited_once_with(
            Method.POST,
            f"api/1/vehicles/{VIN}/command/remote_auto_seat_climate_request",
            json={"auto_seat_position": 2, "auto_climate_on": False},
        )


class AutoSeatClimateSignedTests(IsolatedAsyncioTestCase):
    """The signed/protobuf path maps the same 1-indexed input onto the proto enum."""

    def create_vehicle(self) -> tuple[_TestCommands, AsyncMock]:
        parent = MagicMock()
        parent.private_key = ec.generate_private_key(ec.SECP256R1())
        vehicle = _TestCommands(parent, VIN)
        send = AsyncMock(return_value={"response": {"result": True}})
        vehicle._sendInfotainment = send  # pyright: ignore[reportAttributeAccessIssue]
        return vehicle, send

    def _seat_position(self, send: AsyncMock) -> int:
        action: Action = send.await_args.args[0]
        carseats = action.vehicleAction.autoSeatClimateAction.carseat
        self.assertEqual(len(carseats), 1)
        return carseats[0].seat_position

    async def test_front_left_emits_front_left_proto(self) -> None:
        vehicle, send = self.create_vehicle()

        await vehicle.remote_auto_seat_climate_request(AutoSeat.FRONT_LEFT, True)

        self.assertEqual(
            self._seat_position(send),
            AutoSeatClimateAction.AutoSeatPosition_FrontLeft,
        )
        self.assertTrue(
            send.await_args.args[0].vehicleAction.autoSeatClimateAction.carseat[0].on
        )

    async def test_front_right_emits_front_right_proto(self) -> None:
        vehicle, send = self.create_vehicle()

        # AutoSeat.FRONT_RIGHT == 2 must no longer raise (previously IndexError).
        await vehicle.remote_auto_seat_climate_request(AutoSeat.FRONT_RIGHT, False)

        self.assertEqual(
            self._seat_position(send),
            AutoSeatClimateAction.AutoSeatPosition_FrontRight,
        )
