"""Charging command group (PR-5) over the mocked BLE transport.

Live-verified against the test car (VIN LRW3F7EK4NC716336, m5-btproxy,
plugged in throughout) per-command status:

- Fully live-verified snapshot->act->verify->restore->confirm, in a single
  BLE session: ``set_charge_limit``, ``charge_max_range``, ``charge_stop``,
  ``charge_start``, ``charge_standard``, ``set_charging_amps``,
  ``set_scheduled_charging``, ``set_scheduled_departure``,
  ``add_charge_schedule``, ``remove_charge_schedule``,
  ``add_precondition_schedule``, ``remove_precondition_schedule``.
  ``batch_remove_charge_schedules``/``batch_remove_precondition_schedules``
  were live-exercised with ``home=work=other=False`` (the only safe live
  case - removes nothing in any category) to prove ACK + wire path without
  touching the car's real schedules; the six real charge schedules and five
  real precondition schedules present on the car were confirmed untouched
  before and after every schedule test. The car was confirmed restored to
  its exact original charge_limit_soc, charge_current_request,
  scheduled_charging_mode, and schedule-id sets at the end of the session.
- Live-discovered vehicle-side behavior (not a library bug): calling
  ``charge_standard()`` while the current limit already equals
  ``charge_limit_soc_std`` is cleanly rejected by the car
  (``{"result": False, "reason": "already_standard"}``) rather than treated
  as a no-op success - the test below exercises the accepted path.
- Live-discovered: ``set_scheduled_departure()``'s ``preconditioning_enabled``
  and ``off_peak_charging_enabled`` parameters are accepted by the Python
  signature but never wired into ``ScheduledDepartureAction`` (that proto
  message has no such fields, see ``proto/car_server.proto``) - passing
  ``preconditioning_enabled=False`` live had no effect on the vehicle's
  observed ``ChargeState.preconditioning_enabled``. Documented in AGENTS.md.
- ``charge_port_door_open``/``charge_port_door_close`` are EXCLUDED from live
  testing (CAPTAIN-PRESENT-ONLY - unlatching a plugged-in cable does not
  re-engage without a physical reseat) and ship mocked-transport-only below.
"""

from tesla_fleet_api.tesla.vehicle.proto.car_server_pb2 import Action
from tesla_fleet_api.tesla.vehicle.proto.common_pb2 import (
    OffPeakChargingTimes,
    PreconditioningTimes,
)
from tesla_fleet_api.tesla.vehicle.proto.universal_message_pb2 import Domain
from tesla_fleet_api.tesla.vehicle.proto.vcsec_pb2 import (
    ClosureMoveType_E,
    UnsignedMessage,
)

from ble_mocked_transport import (
    MockedBleTransportTestCase,
    decrypt_sent_command,
    infotainment_action_ok_reply,
    vcsec_ok_reply,
)


def _decode_vehicle_action(vehicle, sent_msg):
    plaintext = decrypt_sent_command(vehicle, sent_msg)
    action = Action.FromString(plaintext)
    assert sent_msg.to_destination.domain == Domain.DOMAIN_INFOTAINMENT
    assert sent_msg.signature_data.HasField("AES_GCM_Personalized_data")
    return action.vehicleAction


class ChargeStartStopTests(MockedBleTransportTestCase):
    async def test_charge_start_sends_start_void(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_action_ok_reply()

        result = await vehicle.charge_start()

        self.assertEqual(result, {"response": {"result": True, "reason": ""}})
        action = _decode_vehicle_action(vehicle, send.await_args.args[0])
        self.assertTrue(action.chargingStartStopAction.HasField("start"))

    async def test_charge_stop_sends_stop_void(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_action_ok_reply()

        await vehicle.charge_stop()

        action = _decode_vehicle_action(vehicle, send.await_args.args[0])
        self.assertTrue(action.chargingStartStopAction.HasField("stop"))


class ChargeStandardMaxRangeTests(MockedBleTransportTestCase):
    async def test_charge_standard_sends_start_standard_void(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_action_ok_reply()

        await vehicle.charge_standard()

        action = _decode_vehicle_action(vehicle, send.await_args.args[0])
        self.assertTrue(action.chargingStartStopAction.HasField("start_standard"))

    async def test_charge_max_range_sends_start_max_range_void(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_action_ok_reply()

        await vehicle.charge_max_range()

        action = _decode_vehicle_action(vehicle, send.await_args.args[0])
        self.assertTrue(action.chargingStartStopAction.HasField("start_max_range"))


class SetChargeLimitTests(MockedBleTransportTestCase):
    async def test_sends_charge_limit_percent(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_action_ok_reply()

        result = await vehicle.set_charge_limit(75)

        self.assertEqual(result, {"response": {"result": True, "reason": ""}})
        action = _decode_vehicle_action(vehicle, send.await_args.args[0])
        self.assertEqual(action.chargingSetLimitAction.percent, 75)


class SetChargingAmpsTests(MockedBleTransportTestCase):
    async def test_sends_charging_amps(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_action_ok_reply()

        await vehicle.set_charging_amps(16)

        action = _decode_vehicle_action(vehicle, send.await_args.args[0])
        self.assertEqual(action.setChargingAmpsAction.charging_amps, 16)


class SetScheduledChargingTests(MockedBleTransportTestCase):
    async def test_sends_enabled_and_charging_time(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_action_ok_reply()

        await vehicle.set_scheduled_charging(True, 120)

        action = _decode_vehicle_action(vehicle, send.await_args.args[0])
        scheduled = action.scheduledChargingAction
        self.assertTrue(scheduled.enabled)
        self.assertEqual(scheduled.charging_time, 120)

    async def test_disable_sends_enabled_false(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_action_ok_reply()

        await vehicle.set_scheduled_charging(False, 0)

        action = _decode_vehicle_action(vehicle, send.await_args.args[0])
        self.assertFalse(action.scheduledChargingAction.enabled)


class SetScheduledDepartureTests(MockedBleTransportTestCase):
    """``preconditioning_enabled``/``off_peak_charging_enabled`` are accepted by
    the Python signature but not wired into ``ScheduledDepartureAction`` - live-
    verified (see module docstring). This asserts the actual wire behavior:
    only ``enabled``/``departure_time``/the two *_times recurrence messages/
    ``off_peak_hours_end_time`` reach the proto."""

    async def test_sends_departure_time_and_recurrence_windows(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_action_ok_reply()

        await vehicle.set_scheduled_departure(
            enable=True,
            preconditioning_enabled=False,
            preconditioning_weekdays_only=True,
            departure_time=90,
            off_peak_charging_enabled=False,
            off_peak_charging_weekdays_only=True,
            end_off_peak_time=360,
        )

        action = _decode_vehicle_action(vehicle, send.await_args.args[0])
        departure = action.scheduledDepartureAction
        self.assertTrue(departure.enabled)
        self.assertEqual(departure.departure_time, 90)
        self.assertEqual(departure.off_peak_hours_end_time, 360)
        self.assertEqual(
            departure.preconditioning_times.WhichOneof("times"), "weekdays"
        )
        self.assertEqual(
            departure.off_peak_charging_times.WhichOneof("times"), "weekdays"
        )
        # No field on ScheduledDepartureAction carries preconditioning_enabled
        # or off_peak_charging_enabled - proving they cannot be wired.
        self.assertNotIn(
            "preconditioning_enabled", [f.name for f in departure.DESCRIPTOR.fields]
        )
        self.assertNotIn(
            "off_peak_charging_enabled", [f.name for f in departure.DESCRIPTOR.fields]
        )

    async def test_all_week_when_not_weekdays_only(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_action_ok_reply()

        await vehicle.set_scheduled_departure(departure_time=0)

        action = _decode_vehicle_action(vehicle, send.await_args.args[0])
        departure = action.scheduledDepartureAction
        self.assertEqual(
            departure.preconditioning_times,
            PreconditioningTimes(all_week=departure.preconditioning_times.all_week),
        )
        self.assertEqual(
            departure.off_peak_charging_times,
            OffPeakChargingTimes(all_week=departure.off_peak_charging_times.all_week),
        )


class ChargeScheduleTests(MockedBleTransportTestCase):
    async def test_add_charge_schedule_sends_schedule_fields(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_action_ok_reply()

        await vehicle.add_charge_schedule(
            days_of_week=64,
            enabled=True,
            lat=1.5,
            lon=2.5,
            start_time=60,
            end_time=120,
            one_time=True,
            id=42,
            name="test",
        )

        action = _decode_vehicle_action(vehicle, send.await_args.args[0])
        schedule = action.addChargeScheduleAction
        self.assertEqual(schedule.days_of_week, 64)
        self.assertTrue(schedule.enabled)
        self.assertAlmostEqual(schedule.latitude, 1.5)
        self.assertAlmostEqual(schedule.longitude, 2.5)
        self.assertEqual(schedule.start_time, 60)
        self.assertEqual(schedule.end_time, 120)
        self.assertTrue(schedule.one_time)
        self.assertEqual(schedule.id, 42)
        self.assertEqual(schedule.name, "test")

    async def test_add_charge_schedule_requires_start_or_end_time(self) -> None:
        vehicle, _send = self.make_vehicle()

        with self.assertRaises(ValueError):
            await vehicle.add_charge_schedule(
                days_of_week=1, enabled=True, lat=0.0, lon=0.0
            )

    async def test_remove_charge_schedule_sends_id(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_action_ok_reply()

        await vehicle.remove_charge_schedule(7)

        action = _decode_vehicle_action(vehicle, send.await_args.args[0])
        self.assertEqual(action.removeChargeScheduleAction.id, 7)

    async def test_batch_remove_charge_schedules_sends_location_flags(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_action_ok_reply()

        await vehicle.batch_remove_charge_schedules(home=True, work=False, other=True)

        action = _decode_vehicle_action(vehicle, send.await_args.args[0])
        batch = action.batchRemoveChargeSchedulesAction
        self.assertTrue(batch.home)
        self.assertFalse(batch.work)
        self.assertTrue(batch.other)


class PreconditionScheduleTests(MockedBleTransportTestCase):
    async def test_add_precondition_schedule_sends_schedule_fields(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_action_ok_reply()

        await vehicle.add_precondition_schedule(
            days_of_week=1,
            enabled=True,
            lat=3.5,
            lon=4.5,
            precondition_time=585,
            id=99,
            one_time=False,
            name="precon-test",
        )

        action = _decode_vehicle_action(vehicle, send.await_args.args[0])
        schedule = action.addPreconditionScheduleAction
        self.assertEqual(schedule.days_of_week, 1)
        self.assertTrue(schedule.enabled)
        self.assertAlmostEqual(schedule.latitude, 3.5)
        self.assertAlmostEqual(schedule.longitude, 4.5)
        self.assertEqual(schedule.precondition_time, 585)
        self.assertEqual(schedule.id, 99)
        self.assertFalse(schedule.one_time)
        self.assertEqual(schedule.name, "precon-test")

    async def test_remove_precondition_schedule_sends_id(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_action_ok_reply()

        await vehicle.remove_precondition_schedule(11)

        action = _decode_vehicle_action(vehicle, send.await_args.args[0])
        self.assertEqual(action.removePreconditionScheduleAction.id, 11)

    async def test_batch_remove_precondition_schedules_sends_location_flags(
        self,
    ) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_action_ok_reply()

        await vehicle.batch_remove_precondition_schedules(
            home=False, work=True, other=False
        )

        action = _decode_vehicle_action(vehicle, send.await_args.args[0])
        batch = action.batchRemovePreconditionSchedulesAction
        self.assertFalse(batch.home)
        self.assertTrue(batch.work)
        self.assertFalse(batch.other)


class ChargePortDoorTests(MockedBleTransportTestCase):
    """CAPTAIN-PRESENT-ONLY (unlatching a plugged-in cable does not re-engage
    without a physical reseat) - mocked-transport proto construction only,
    never live-actuated. See decisions-resolved.md."""

    async def test_charge_port_door_open_sends_rke_open(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = vcsec_ok_reply()

        result = await vehicle.charge_port_door_open()

        self.assertEqual(result, {"response": {"result": True, "reason": ""}})
        send.assert_awaited_once()
        sent_msg = send.await_args.args[0]
        self.assertEqual(sent_msg.to_destination.domain, Domain.DOMAIN_VEHICLE_SECURITY)
        plaintext = decrypt_sent_command(vehicle, sent_msg)
        unsigned = UnsignedMessage.FromString(plaintext)
        self.assertEqual(
            unsigned.closureMoveRequest.chargePort,
            ClosureMoveType_E.CLOSURE_MOVE_TYPE_OPEN,
        )

    async def test_charge_port_door_close_sends_rke_close(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = vcsec_ok_reply()

        await vehicle.charge_port_door_close()

        sent_msg = send.await_args.args[0]
        plaintext = decrypt_sent_command(vehicle, sent_msg)
        unsigned = UnsignedMessage.FromString(plaintext)
        self.assertEqual(
            unsigned.closureMoveRequest.chargePort,
            ClosureMoveType_E.CLOSURE_MOVE_TYPE_CLOSE,
        )
