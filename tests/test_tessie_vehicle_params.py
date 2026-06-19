"""Unit tests for Tessie vehicle command parameter mapping."""

from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, MagicMock

from tesla_fleet_api.const import Method
from tesla_fleet_api.tessie.vehicles import TessieVehicle


class TessieVehicleParameterTests(IsolatedAsyncioTestCase):
    """Verify Tessie-specific command parameters match the upstream API."""

    VIN = "5YJXCAE43LF123456"

    def create_vehicle(self) -> tuple[TessieVehicle, AsyncMock]:
        """Create a test vehicle with a mocked request method."""

        parent = MagicMock()
        request = AsyncMock(return_value={"result": True})
        parent._request = request  # pyright: ignore[reportAttributeAccessIssue]
        return TessieVehicle(parent, self.VIN), request

    async def test_climate_command_parameters_match_tessie_reference(self) -> None:
        """Climate-related Tessie commands should send the documented query params."""

        test_cases = [
            (
                "tessie_set_cabin_overheat_protection",
                lambda vehicle: vehicle.tessie_set_cabin_overheat_protection(
                    on=True,
                    fan_only=True,
                    max_attempts=2,
                    wait_for_completion=False,
                ),
                f"{self.VIN}/command/set_cabin_overheat_protection",
                {
                    "on": True,
                    "fan_only": True,
                    "max_attempts": 2,
                    "wait_for_completion": False,
                },
            ),
            (
                "tessie_set_cop_temp",
                lambda vehicle: vehicle.tessie_set_cop_temp(
                    cop_temp=3,
                    max_attempts=2,
                    wait_for_completion=False,
                ),
                f"{self.VIN}/command/set_cop_temp",
                {
                    "cop_temp": 3,
                    "max_attempts": 2,
                    "wait_for_completion": False,
                },
            ),
            (
                "tessie_set_bioweapon_mode",
                lambda vehicle: vehicle.tessie_set_bioweapon_mode(
                    on=True,
                    max_attempts=2,
                    wait_for_completion=False,
                ),
                f"{self.VIN}/command/set_bioweapon_mode",
                {
                    "on": True,
                    "max_attempts": 2,
                    "wait_for_completion": False,
                },
            ),
            (
                "tessie_set_climate_keeper_mode",
                lambda vehicle: vehicle.tessie_set_climate_keeper_mode(
                    mode=2,
                    max_attempts=2,
                    wait_for_completion=False,
                ),
                f"{self.VIN}/command/set_climate_keeper_mode",
                {
                    "mode": 2,
                    "max_attempts": 2,
                    "wait_for_completion": False,
                },
            ),
        ]

        for method_name, invoke, path, params in test_cases:
            with self.subTest(method=method_name):
                vehicle, request = self.create_vehicle()

                response = await invoke(vehicle)

                self.assertEqual(response, {"result": True})
                request.assert_awaited_once_with(Method.POST, path, params=params)

    async def test_misc_command_parameters_match_tessie_reference(self) -> None:
        """Other corrected Tessie commands should send the documented query params."""

        test_cases = [
            (
                "tessie_set_charging_amps",
                lambda vehicle: vehicle.tessie_set_charging_amps(
                    amps=16,
                    max_attempts=2,
                    wait_for_completion=False,
                ),
                f"{self.VIN}/command/set_charging_amps",
                {
                    "amps": 16,
                    "max_attempts": 2,
                    "wait_for_completion": False,
                },
            ),
            (
                "tessie_trigger_homelink",
                lambda vehicle: vehicle.tessie_trigger_homelink(
                    max_attempts=2,
                    wait_for_completion=False,
                ),
                f"{self.VIN}/command/trigger_homelink",
                {
                    "max_attempts": 2,
                    "wait_for_completion": False,
                },
            ),
            (
                "tessie_schedule_software_update",
                lambda vehicle: vehicle.tessie_schedule_software_update(
                    in_seconds=3600,
                    max_attempts=2,
                    wait_for_completion=False,
                ),
                f"{self.VIN}/command/schedule_software_update",
                {
                    "in_seconds": 3600,
                    "max_attempts": 2,
                    "wait_for_completion": False,
                },
            ),
            (
                "tessie_set_scheduled_departure",
                lambda vehicle: vehicle.tessie_set_scheduled_departure(
                    enable=True,
                    departure_time=480,
                    preconditioning_enabled=True,
                    end_off_peak_time=360,
                    max_attempts=2,
                    wait_for_completion=False,
                ),
                f"{self.VIN}/command/set_scheduled_departure",
                {
                    "enable": True,
                    "departure_time": 480,
                    "preconditioning_enabled": True,
                    "preconditioning_weekdays_only": False,
                    "off_peak_charging_enabled": False,
                    "off_peak_charging_weekdays_only": False,
                    "end_off_peak_time": 360,
                    "max_attempts": 2,
                    "wait_for_completion": False,
                },
            ),
        ]

        for method_name, invoke, path, params in test_cases:
            with self.subTest(method=method_name):
                vehicle, request = self.create_vehicle()

                response = await invoke(vehicle)

                self.assertEqual(response, {"result": True})
                request.assert_awaited_once_with(Method.POST, path, params=params)

    async def test_tessie_add_charge_schedule_uses_documented_parameters(self) -> None:
        """Charge schedule requests should follow the Tessie add_charge_schedule schema."""

        vehicle, request = self.create_vehicle()

        response = await vehicle.tessie_add_charge_schedule(
            days_of_week="Weekdays",
            enabled=True,
            start_enabled=True,
            end_enabled=False,
            lat=1.23,
            lon=4.56,
            start_time=360,
            one_time=True,
            id=7,
            max_attempts=2,
            wait_for_completion=False,
        )

        self.assertEqual(response, {"result": True})
        request.assert_awaited_once_with(
            Method.POST,
            f"{self.VIN}/command/add_charge_schedule",
            params={
                "days_of_week": "Weekdays",
                "enabled": True,
                "start_enabled": True,
                "end_enabled": False,
                "lat": 1.23,
                "lon": 4.56,
                "start_time": 360,
                "one_time": True,
                "id": 7,
                "max_attempts": 2,
                "wait_for_completion": False,
            },
        )

    async def test_tessie_add_charge_schedule_validates_enabled_times(self) -> None:
        """Charge schedule helpers should reject invalid start/end combinations."""

        vehicle, _ = self.create_vehicle()

        with self.assertRaisesRegex(
            ValueError, "Either start_enabled or end_enabled must be True"
        ):
            await vehicle.tessie_add_charge_schedule(
                days_of_week="Weekdays",
                enabled=True,
                start_enabled=False,
                end_enabled=False,
                lat=1.23,
                lon=4.56,
            )

        with self.assertRaisesRegex(
            ValueError, "start_time is required when start_enabled is True"
        ):
            await vehicle.tessie_add_charge_schedule(
                days_of_week="Weekdays",
                enabled=True,
                start_enabled=True,
                end_enabled=False,
                lat=1.23,
                lon=4.56,
            )

        with self.assertRaisesRegex(
            ValueError, "end_time is required when end_enabled is True"
        ):
            await vehicle.tessie_add_charge_schedule(
                days_of_week="Weekdays",
                enabled=True,
                start_enabled=False,
                end_enabled=True,
                lat=1.23,
                lon=4.56,
            )

    async def test_tessie_add_precondition_schedule_uses_documented_parameters(self) -> None:
        """Precondition schedule requests should follow the Tessie schema."""

        vehicle, request = self.create_vehicle()

        response = await vehicle.tessie_add_precondition_schedule(
            days_of_week="Weekdays",
            enabled=True,
            lat=1.23,
            lon=4.56,
            precondition_time=420,
            one_time=True,
            id=7,
            max_attempts=2,
            wait_for_completion=False,
        )

        self.assertEqual(response, {"result": True})
        request.assert_awaited_once_with(
            Method.POST,
            f"{self.VIN}/command/add_precondition_schedule",
            params={
                "days_of_week": "Weekdays",
                "enabled": True,
                "lat": 1.23,
                "lon": 4.56,
                "precondition_time": 420,
                "one_time": True,
                "id": 7,
                "max_attempts": 2,
                "wait_for_completion": False,
            },
        )
