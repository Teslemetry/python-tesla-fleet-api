"""Regression tests for all 14 BLE state readers over the mocked transport.

Each reader is defined on ``VehicleBluetooth`` (not inherited from
``Commands``) and composes a ``GetVehicleData`` request; these tests feed a
canned reply and assert the reader decodes it to the expected typed proto.
"""

from tesla_fleet_api.const import BluetoothVehicleData
from tesla_protocol.command.car_server_pb2 import Action
from tesla_protocol.command.vcsec_pb2 import (
    VehicleLockState_E,
    VehicleStatus,
)
from tesla_protocol.command.vehicle_pb2 import (
    ChargeScheduleState,
    ChargeState,
    ClimateState,
    ClosuresState,
    DriveState,
    LocationState,
    MediaDetailState,
    MediaState,
    ParentalControlsState,
    PreconditioningScheduleState,
    SoftwareUpdateState,
    TirePressureState,
    VehicleData,
)

from ble_mocked_transport import (
    MockedBleTransportTestCase,
    decrypt_sent_command,
    infotainment_vehicle_data_reply,
    vcsec_vehicle_status_reply,
)


class ChargeStateTests(MockedBleTransportTestCase):
    async def test_charge_state(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_vehicle_data_reply(
            VehicleData(charge_state=ChargeState(battery_level=42))
        )
        result = await vehicle.charge_state()
        self.assertIsInstance(result, ChargeState)
        self.assertEqual(result.battery_level, 42)


class ClimateStateTests(MockedBleTransportTestCase):
    async def test_climate_state(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_vehicle_data_reply(
            VehicleData(climate_state=ClimateState(inside_temp_celsius=21.5))
        )
        result = await vehicle.climate_state()
        self.assertIsInstance(result, ClimateState)
        self.assertAlmostEqual(result.inside_temp_celsius, 21.5)


class DriveStateTests(MockedBleTransportTestCase):
    async def test_drive_state(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_vehicle_data_reply(
            VehicleData(drive_state=DriveState(speed=55))
        )
        result = await vehicle.drive_state()
        self.assertIsInstance(result, DriveState)
        self.assertEqual(result.speed, 55)


class LocationStateTests(MockedBleTransportTestCase):
    async def test_location_state(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_vehicle_data_reply(
            VehicleData(location_state=LocationState(latitude=37.4, longitude=-122.1))
        )
        result = await vehicle.location_state()
        self.assertIsInstance(result, LocationState)
        self.assertAlmostEqual(result.latitude, 37.4, places=5)
        self.assertAlmostEqual(result.longitude, -122.1, places=5)


class ClosuresStateTests(MockedBleTransportTestCase):
    async def test_closures_state(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_vehicle_data_reply(
            VehicleData(closures_state=ClosuresState(door_open_driver_front=True))
        )
        result = await vehicle.closures_state()
        self.assertIsInstance(result, ClosuresState)
        self.assertTrue(result.door_open_driver_front)


class ChargeScheduleStateTests(MockedBleTransportTestCase):
    async def test_charge_schedule_state(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_vehicle_data_reply(
            VehicleData(charge_schedule_state=ChargeScheduleState(charge_buffer=10))
        )
        result = await vehicle.charge_schedule_state()
        self.assertIsInstance(result, ChargeScheduleState)
        self.assertEqual(result.charge_buffer, 10)


class PreconditioningScheduleStateTests(MockedBleTransportTestCase):
    async def test_preconditioning_schedule_state(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_vehicle_data_reply(
            VehicleData(
                preconditioning_schedule_state=PreconditioningScheduleState(
                    max_num_precondition_schedules=5
                )
            )
        )
        result = await vehicle.preconditioning_schedule_state()
        self.assertIsInstance(result, PreconditioningScheduleState)
        self.assertEqual(result.max_num_precondition_schedules, 5)


class TirePressureStateTests(MockedBleTransportTestCase):
    async def test_tire_pressure_state(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_vehicle_data_reply(
            VehicleData(tire_pressure_state=TirePressureState(tpms_pressure_fl=2.9))
        )
        result = await vehicle.tire_pressure_state()
        self.assertIsInstance(result, TirePressureState)
        self.assertAlmostEqual(result.tpms_pressure_fl, 2.9, places=5)


class MediaStateTests(MockedBleTransportTestCase):
    async def test_media_state(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_vehicle_data_reply(
            VehicleData(
                media_state=MediaState(audio_volume=7.0, now_playing_title="Song")
            )
        )
        result = await vehicle.media_state()
        self.assertIsInstance(result, MediaState)
        self.assertAlmostEqual(result.audio_volume, 7.0)
        self.assertEqual(result.now_playing_title, "Song")


class MediaDetailStateTests(MockedBleTransportTestCase):
    async def test_media_detail_state(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_vehicle_data_reply(
            VehicleData(
                media_detail_state=MediaDetailState(now_playing_duration=180000)
            )
        )
        result = await vehicle.media_detail_state()
        self.assertIsInstance(result, MediaDetailState)
        self.assertEqual(result.now_playing_duration, 180000)


class SoftwareUpdateStateTests(MockedBleTransportTestCase):
    async def test_software_update_state(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_vehicle_data_reply(
            VehicleData(software_update_state=SoftwareUpdateState(version="2025.14.3"))
        )
        result = await vehicle.software_update_state()
        self.assertIsInstance(result, SoftwareUpdateState)
        self.assertEqual(result.version, "2025.14.3")


class ParentalControlsStateTests(MockedBleTransportTestCase):
    async def test_parental_controls_state(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_vehicle_data_reply(
            VehicleData(
                parental_controls_state=ParentalControlsState(
                    parental_controls_active=True
                )
            )
        )
        result = await vehicle.parental_controls_state()
        self.assertIsInstance(result, ParentalControlsState)
        self.assertTrue(result.parental_controls_active)


class VehicleStateTests(MockedBleTransportTestCase):
    """``vehicle_state`` is the VCSEC ``VehicleStatus`` reader (not the infotainment ``VehicleState``, see §2.3)."""

    async def test_vehicle_state(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = vcsec_vehicle_status_reply(
            VehicleStatus(vehicleLockState=VehicleLockState_E.VEHICLELOCKSTATE_LOCKED)
        )
        result = await vehicle.vehicle_state()
        self.assertIsInstance(result, VehicleStatus)
        self.assertEqual(
            result.vehicleLockState, VehicleLockState_E.VEHICLELOCKSTATE_LOCKED
        )


class VehicleDataTests(MockedBleTransportTestCase):
    """``vehicle_data`` composite reader; ``endpoints`` is required (no all-endpoints default,
    see the response-size-cap note in its docstring)."""

    async def test_explicit_endpoints_requests_only_those_substates(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_vehicle_data_reply(
            VehicleData(charge_state=ChargeState(battery_level=77))
        )

        result = await vehicle.vehicle_data([BluetoothVehicleData.CHARGE_STATE])

        self.assertIsInstance(result, VehicleData)
        self.assertEqual(result.charge_state.battery_level, 77)

        send.assert_awaited_once()
        sent_msg = send.await_args.args[0]

        plaintext = decrypt_sent_command(vehicle, sent_msg)
        action = Action.FromString(plaintext)
        get_vehicle_data = action.vehicleAction.getVehicleData
        self.assertTrue(get_vehicle_data.HasField("getChargeState"))
        self.assertFalse(get_vehicle_data.HasField("getClimateState"))
