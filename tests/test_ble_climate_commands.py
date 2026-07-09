"""Climate command group (PR-4) over the mocked BLE transport.

Live-verified against the test car (VIN LRW3F7EK4NC716336, m5-btproxy)
per-command status:

- Fully live-verified snapshot->act->verify->restore->confirm:
  ``auto_conditioning_start``, ``auto_conditioning_stop``, ``set_temps``,
  ``set_climate_keeper_mode``, ``set_cabin_overheat_protection``.
- Live-attempted, cleanly rejected by the vehicle (ACK decodes correctly,
  state confirmed unchanged - not a library bug, see AGENTS.md):
  ``set_cop_temp`` (``not_supported``); ``remote_seat_heater_request``,
  ``remote_auto_seat_climate_request``, ``remote_steering_wheel_heater_request``,
  ``remote_steering_wheel_heat_level_request``,
  ``remote_auto_steering_wheel_heat_climate_request`` (all: ``cabin comfort
  remote settings not enabled`` - the ``remote_heater_control_enabled`` gate).
- Deferred, mocked-transport only: ``set_bioweapon_mode`` and
  ``remote_seat_cooler_request`` (no HEPA filter / no seat coolers on this
  Model 3 - the relevant ``ClimateState`` fields are absent from every live
  read); ``set_preconditioning_max`` and ``set_recirculation`` (no
  ``ClimateState`` field reflects either the preconditioning override flag or
  recirculation mode - not reliably snapshot/verify/restore-able over BLE).
"""

from tesla_fleet_api.const import AutoSeat
from tesla_fleet_api.tesla.vehicle.proto.car_server_pb2 import (
    Action,
    ActionStatus,
    HvacSeatCoolerActions,
    OperationStatus_E as InfoOperationStatus_E,
    Response,
    ResultReason,
)
from tesla_fleet_api.tesla.vehicle.proto.common_pb2 import StwHeatLevel
from tesla_fleet_api.tesla.vehicle.proto.universal_message_pb2 import (
    Destination,
    Domain,
    RoutableMessage,
)
from tesla_fleet_api.tesla.vehicle.proto.vehicle_pb2 import ClimateState

from ble_mocked_transport import (
    MockedBleTransportTestCase,
    decrypt_sent_command,
    infotainment_action_ok_reply,
)


def _decode_vehicle_action(vehicle, sent_msg):
    plaintext = decrypt_sent_command(vehicle, sent_msg)
    action = Action.FromString(plaintext)
    assert sent_msg.to_destination.domain == Domain.DOMAIN_INFOTAINMENT
    assert sent_msg.signature_data.HasField("AES_GCM_Personalized_data")
    return action.vehicleAction


def _rejection_reply(reason: str) -> RoutableMessage:
    body = Response(
        actionStatus=ActionStatus(
            result=InfoOperationStatus_E.OPERATIONSTATUS_ERROR,
            result_reason=ResultReason(plain_text=reason),
        )
    )
    return RoutableMessage(
        from_destination=Destination(domain=Domain.DOMAIN_INFOTAINMENT),
        protobuf_message_as_bytes=body.SerializeToString(),
    )


class AutoConditioningTests(MockedBleTransportTestCase):
    async def test_auto_conditioning_start_sends_hvac_auto_on(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_action_ok_reply()

        result = await vehicle.auto_conditioning_start()

        self.assertEqual(result, {"response": {"result": True, "reason": ""}})
        vehicle_action = _decode_vehicle_action(vehicle, send.await_args.args[0])
        self.assertTrue(vehicle_action.hvacAutoAction.power_on)

    async def test_auto_conditioning_stop_sends_hvac_auto_off(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_action_ok_reply()

        await vehicle.auto_conditioning_stop()

        vehicle_action = _decode_vehicle_action(vehicle, send.await_args.args[0])
        self.assertFalse(vehicle_action.hvacAutoAction.power_on)


class SetTempsTests(MockedBleTransportTestCase):
    async def test_sends_driver_and_passenger_temps(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_action_ok_reply()

        result = await vehicle.set_temps(21.5, 19.0)

        self.assertEqual(result, {"response": {"result": True, "reason": ""}})
        vehicle_action = _decode_vehicle_action(vehicle, send.await_args.args[0])
        hvac = vehicle_action.hvacTemperatureAdjustmentAction
        self.assertAlmostEqual(hvac.driver_temp_celsius, 21.5)
        self.assertAlmostEqual(hvac.passenger_temp_celsius, 19.0)


class SetClimateKeeperModeTests(MockedBleTransportTestCase):
    async def test_keep_mode_sends_climate_keeper_on(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_action_ok_reply()

        await vehicle.set_climate_keeper_mode(1)

        vehicle_action = _decode_vehicle_action(vehicle, send.await_args.args[0])
        keeper = vehicle_action.hvacClimateKeeperAction
        self.assertEqual(
            keeper.ClimateKeeperAction,
            keeper.ClimateKeeperAction_On,
        )


class SetCabinOverheatProtectionTests(MockedBleTransportTestCase):
    async def test_fan_only_sends_on_and_fan_only(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_action_ok_reply()

        await vehicle.set_cabin_overheat_protection(True, True)

        vehicle_action = _decode_vehicle_action(vehicle, send.await_args.args[0])
        cop = vehicle_action.setCabinOverheatProtectionAction
        self.assertTrue(cop.on)
        self.assertTrue(cop.fan_only)


class SetCopTempTests(MockedBleTransportTestCase):
    """Live-attempted; car rejected with ``not_supported`` (state unchanged,
    not a library bug - see module docstring). Mocked-transport still proves
    proto construction and rejection decoding."""

    async def test_sends_medium_activation_temp(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_action_ok_reply()

        await vehicle.set_cop_temp(1)

        vehicle_action = _decode_vehicle_action(vehicle, send.await_args.args[0])
        cop = vehicle_action.setCopTempAction
        self.assertEqual(
            cop.copActivationTemp,
            ClimateState.CopActivationTemp.CopActivationTempMedium,
        )

    async def test_decodes_not_supported_rejection(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = _rejection_reply("not_supported")

        result = await vehicle.set_cop_temp(1)

        self.assertEqual(
            result, {"response": {"result": False, "reason": "not_supported"}}
        )


class RemoteSeatHeaterRequestTests(MockedBleTransportTestCase):
    """Live-attempted; car rejected with ``cabin comfort remote settings not
    enabled`` (``remote_heater_control_enabled=False`` on the test car - see
    AGENTS.md). ``test_medium_level_regression`` locks the ``SEAT_HEATER_MED``
    fix (was incorrectly ``SEAT_HEATER_MEDIUM``, found live during PR-4)."""

    async def test_sends_front_left_low(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_action_ok_reply()

        await vehicle.remote_seat_heater_request(0, 1)

        vehicle_action = _decode_vehicle_action(vehicle, send.await_args.args[0])
        heater = vehicle_action.hvacSeatHeaterActions.hvacSeatHeaterAction[0]
        self.assertEqual(heater.WhichOneof("seat_position"), "CAR_SEAT_FRONT_LEFT")
        self.assertEqual(heater.WhichOneof("seat_heater_level"), "SEAT_HEATER_LOW")

    async def test_medium_level_regression(self) -> None:
        """Level 2 must map to the proto's SEAT_HEATER_MED, not SEAT_HEATER_MEDIUM."""
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_action_ok_reply()

        await vehicle.remote_seat_heater_request(0, 2)

        vehicle_action = _decode_vehicle_action(vehicle, send.await_args.args[0])
        heater = vehicle_action.hvacSeatHeaterActions.hvacSeatHeaterAction[0]
        self.assertEqual(heater.WhichOneof("seat_heater_level"), "SEAT_HEATER_MED")

    async def test_decodes_remote_settings_not_enabled_rejection(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = _rejection_reply(
            "cabin comfort remote settings not enabled"
        )

        result = await vehicle.remote_seat_heater_request(0, 1)

        self.assertEqual(result["response"]["result"], False)
        self.assertEqual(
            result["response"]["reason"],
            "cabin comfort remote settings not enabled",
        )


class RemoteSeatCoolerRequestTests(MockedBleTransportTestCase):
    """Deferred live (no seat coolers on this Model 3 - ``seat_fan_front_*``
    absent from every live ``climate_state()`` read). Mocked-transport only."""

    async def test_sends_front_left_low(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_action_ok_reply()

        await vehicle.remote_seat_cooler_request(0, 1)

        vehicle_action = _decode_vehicle_action(vehicle, send.await_args.args[0])
        cooler = vehicle_action.hvacSeatCoolerActions.hvacSeatCoolerAction[0]
        self.assertEqual(
            cooler.seat_position,
            HvacSeatCoolerActions.HvacSeatCoolerPosition_FrontLeft,
        )
        self.assertEqual(
            cooler.seat_cooler_level,
            HvacSeatCoolerActions.HvacSeatCoolerLevel_Low,
        )


class RemoteAutoSeatClimateRequestTests(MockedBleTransportTestCase):
    """Live-attempted; car rejected with ``cabin comfort remote settings not
    enabled`` (same gate as the seat heater group)."""

    async def test_front_left_uses_1_indexed_autoseat(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_action_ok_reply()

        await vehicle.remote_auto_seat_climate_request(AutoSeat.FRONT_LEFT, True)

        vehicle_action = _decode_vehicle_action(vehicle, send.await_args.args[0])
        carseat = vehicle_action.autoSeatClimateAction.carseat[0]
        self.assertTrue(carseat.on)
        self.assertEqual(carseat.seat_position, AutoSeat.FRONT_LEFT)
        self.assertEqual(AutoSeat.FRONT_LEFT, 1)


class RemoteAutoSteeringWheelHeatClimateRequestTests(MockedBleTransportTestCase):
    """Live-attempted; car rejected with ``cabin comfort remote settings not
    enabled`` (same gate as the seat heater group)."""

    async def test_sends_auto_stw_heat_off(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_action_ok_reply()

        await vehicle.remote_auto_steering_wheel_heat_climate_request(False)

        vehicle_action = _decode_vehicle_action(vehicle, send.await_args.args[0])
        self.assertFalse(vehicle_action.autoStwHeatAction.on)


class RemoteSteeringWheelHeaterRequestTests(MockedBleTransportTestCase):
    """Live-attempted; car rejected with ``cabin comfort remote settings not
    enabled`` (same gate as the seat heater group)."""

    async def test_sends_power_on(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_action_ok_reply()

        await vehicle.remote_steering_wheel_heater_request(True)

        vehicle_action = _decode_vehicle_action(vehicle, send.await_args.args[0])
        self.assertTrue(vehicle_action.hvacSteeringWheelHeaterAction.power_on)


class RemoteSteeringWheelHeatLevelRequestTests(MockedBleTransportTestCase):
    """Live-attempted; car rejected with ``cabin comfort remote settings not
    enabled`` (same gate as the seat heater group)."""

    async def test_low_level_sends_stw_heat_low(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_action_ok_reply()

        await vehicle.remote_steering_wheel_heat_level_request(1)

        vehicle_action = _decode_vehicle_action(vehicle, send.await_args.args[0])
        stw = vehicle_action.stwHeatLevelAction
        self.assertEqual(stw.stw_heat_level, StwHeatLevel.StwHeatLevel_Low)


class SetBioweaponModeTests(MockedBleTransportTestCase):
    """Deferred live (no HEPA filter on this Model 3 - ``bioweapon_mode_on``
    absent from every live ``climate_state()`` read). Mocked-transport only."""

    async def test_sends_on_and_manual_override(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_action_ok_reply()

        await vehicle.set_bioweapon_mode(True, True)

        vehicle_action = _decode_vehicle_action(vehicle, send.await_args.args[0])
        bioweapon = vehicle_action.hvacBioweaponModeAction
        self.assertTrue(bioweapon.on)
        self.assertTrue(bioweapon.manual_override)


class SetPreconditioningMaxTests(MockedBleTransportTestCase):
    """Deferred live (no ``ClimateState`` field reliably reflects the
    preconditioning-max override flag - ``is_preconditioning`` tracks actual
    HVAC activity, not the override, so it cannot be safely
    snapshot/verify/restored over BLE). Mocked-transport only."""

    async def test_sends_on_and_manual_override(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_action_ok_reply()

        await vehicle.set_preconditioning_max(True, True)

        vehicle_action = _decode_vehicle_action(vehicle, send.await_args.args[0])
        precon = vehicle_action.hvacSetPreconditioningMaxAction
        self.assertTrue(precon.on)
        self.assertTrue(precon.manual_override)


class SetRecirculationTests(MockedBleTransportTestCase):
    """Deferred live (``ClimateState`` has no recirculation field at all -
    confirmed against ``proto/vehicle.proto``, so the command's effect is not
    observable over BLE). Mocked-transport only."""

    async def test_sends_recirculation_on(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_action_ok_reply()

        await vehicle.set_recirculation(True)

        vehicle_action = _decode_vehicle_action(vehicle, send.await_args.args[0])
        self.assertTrue(vehicle_action.hvacRecirculationAction.on)
