"""Tests for issue #31 — low power mode and keep accessory power signed commands.

These two toggles are only available via the Tesla Vehicle Command Protocol
(signed protobuf), not the REST API, so they live on ``Commands`` and are
exercised through the signed/infotainment path. The tests also pin the
serialized wire format (``VehicleAction`` field 130 / 138 wrapping a single bool
field) so it stays compatible with the raw-protobuf encoding downstream users
relied on before these public methods existed.
"""

from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, MagicMock

from cryptography.hazmat.primitives.asymmetric import ec

from tesla_fleet_api.tesla.vehicle.commands import Commands
from tesla_protocol.command.car_server_pb2 import Action

VIN = "5YJXCAE43LF123456"


class _TestCommands(Commands):
    """Concrete ``Commands`` subclass so the ABC can be instantiated in tests."""

    _auth_method = "hmac"

    async def _send(self, msg, requires):  # pragma: no cover - never invoked
        raise NotImplementedError


class PowerModeSignedTests(IsolatedAsyncioTestCase):
    """The signed path emits the correct power-mode proto actions."""

    def create_vehicle(self) -> tuple[_TestCommands, AsyncMock]:
        parent = MagicMock()
        parent.private_key = ec.generate_private_key(ec.SECP256R1())
        vehicle = _TestCommands(parent, VIN)
        send = AsyncMock(return_value={"response": {"result": True}})
        vehicle._sendInfotainment = send  # pyright: ignore[reportAttributeAccessIssue]
        return vehicle, send

    async def test_low_power_mode_on(self) -> None:
        vehicle, send = self.create_vehicle()

        await vehicle.set_low_power_mode(True)

        action: Action = send.await_args.args[0]
        self.assertTrue(action.vehicleAction.HasField("setLowPowerModeAction"))
        self.assertTrue(action.vehicleAction.setLowPowerModeAction.low_power_mode)
        # Wire format: Action.vehicleAction (field 2) -> setLowPowerModeAction
        # (field 130) -> low_power_mode (field 1) == true.
        self.assertEqual(action.SerializeToString(), b"\x12\x05\x92\x08\x02\x08\x01")

    async def test_low_power_mode_off(self) -> None:
        vehicle, send = self.create_vehicle()

        await vehicle.set_low_power_mode(False)

        action: Action = send.await_args.args[0]
        self.assertTrue(action.vehicleAction.HasField("setLowPowerModeAction"))
        self.assertFalse(action.vehicleAction.setLowPowerModeAction.low_power_mode)

    async def test_keep_accessory_power_mode_on(self) -> None:
        vehicle, send = self.create_vehicle()

        await vehicle.set_keep_accessory_power_mode(True)

        action: Action = send.await_args.args[0]
        self.assertTrue(
            action.vehicleAction.HasField("setKeepAccessoryPowerModeAction")
        )
        self.assertTrue(
            action.vehicleAction.setKeepAccessoryPowerModeAction.keep_accessory_power_mode
        )
        # Wire format: Action.vehicleAction (field 2) ->
        # setKeepAccessoryPowerModeAction (field 138) ->
        # keep_accessory_power_mode (field 1) == true.
        self.assertEqual(action.SerializeToString(), b"\x12\x05\xd2\x08\x02\x08\x01")

    async def test_keep_accessory_power_mode_off(self) -> None:
        vehicle, send = self.create_vehicle()

        await vehicle.set_keep_accessory_power_mode(False)

        action: Action = send.await_args.args[0]
        self.assertTrue(
            action.vehicleAction.HasField("setKeepAccessoryPowerModeAction")
        )
        self.assertFalse(
            action.vehicleAction.setKeepAccessoryPowerModeAction.keep_accessory_power_mode
        )
