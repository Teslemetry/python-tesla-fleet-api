"""Unit tests for Tessie vehicle command parameter mapping."""

from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, MagicMock

from tesla_fleet_api.const import Method
from tesla_fleet_api.tessie.tessie import Tessie
from tesla_fleet_api.tessie.vehicle import TessieVehicle


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

    async def test_set_temperatures_sends_driver_and_passenger_separately(
        self,
    ) -> None:
        """set_temperatures should pass per-seat temperatures to the Tessie API."""

        vehicle, request = self.create_vehicle()

        await vehicle.set_temperatures(
            driver_temperature=21.0,
            passenger_temperature=19.5,
            max_attempts=2,
            wait_for_completion=False,
        )

        request.assert_awaited_once_with(
            Method.POST,
            f"{self.VIN}/command/set_temperatures",
            params={
                "temperature": None,
                "driver_temperature": 21.0,
                "passenger_temperature": 19.5,
                "max_attempts": 2,
                "wait_for_completion": False,
            },
        )

    async def test_set_temperatures_keeps_positional_arguments(self) -> None:
        """Existing positional calls must still map to temperature and flags."""

        vehicle, request = self.create_vehicle()

        await vehicle.set_temperatures(21.0, False, 2)

        request.assert_awaited_once_with(
            Method.POST,
            f"{self.VIN}/command/set_temperatures",
            params={
                "temperature": 21.0,
                "driver_temperature": None,
                "passenger_temperature": None,
                "max_attempts": 2,
                "wait_for_completion": False,
            },
        )

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

    async def test_set_roles_uses_documented_parameters(self) -> None:
        """set_roles should send the documented JSON body with only provided fields."""

        vehicle, request = self.create_vehicle()

        response = await vehicle.set_roles(
            role="SUBSCRIPTION",
            account_id="555555555",
        )

        self.assertEqual(response, {"result": True})
        request.assert_awaited_once_with(
            Method.POST,
            f"{self.VIN}/roles",
            json={"role": "SUBSCRIPTION", "account_id": "555555555"},
        )

    async def test_set_roles_omits_unset_optional_fields(self) -> None:
        """set_roles should omit account_id/federation_id when not provided."""

        vehicle, request = self.create_vehicle()

        response = await vehicle.set_roles(role="CHARGING")

        self.assertEqual(response, {"result": True})
        request.assert_awaited_once_with(
            Method.POST,
            f"{self.VIN}/roles",
            json={"role": "CHARGING"},
        )

    async def test_tessie_add_precondition_schedule_uses_documented_parameters(
        self,
    ) -> None:
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

    async def test_firmware_alerts_sends_time_range(self) -> None:
        """firmware_alerts should map start/end to the documented from/to."""

        vehicle, request = self.create_vehicle()

        await vehicle.firmware_alerts(start=1700000000, end=1700100000)

        request.assert_awaited_once_with(
            Method.GET,
            f"{self.VIN}/firmware_alerts",
            params={"from": 1700000000, "to": 1700100000},
        )

    async def test_firmware_alerts_range_is_optional(self) -> None:
        """Existing no-argument calls keep working."""

        vehicle, request = self.create_vehicle()

        await vehicle.firmware_alerts()

        request.assert_awaited_once_with(
            Method.GET,
            f"{self.VIN}/firmware_alerts",
            params={"from": None, "to": None},
        )

    async def test_tessie_release_notes_uses_documented_parameters(self) -> None:
        """release_notes should put the version in the path and send the query."""

        vehicle, request = self.create_vehicle()

        response = await vehicle.tessie_release_notes(
            "2025.44.1", language="de", staged=True
        )

        self.assertEqual(response, {"result": True})
        request.assert_awaited_once_with(
            Method.GET,
            f"{self.VIN}/release_notes/2025.44.1",
            params={"language": "de", "staged": True},
        )

    async def test_tessie_release_notes_blank_version_targets_current(self) -> None:
        """A blank version keeps the trailing slash the API documents."""

        vehicle, request = self.create_vehicle()

        await vehicle.tessie_release_notes()

        request.assert_awaited_once_with(
            Method.GET,
            f"{self.VIN}/release_notes/",
            params={"language": None, "staged": None},
        )

    async def test_roles_gets_roles(self) -> None:
        """roles should GET the roles endpoint."""

        vehicle, request = self.create_vehicle()

        response = await vehicle.roles()

        self.assertEqual(response, {"result": True})
        request.assert_awaited_once_with(Method.GET, f"{self.VIN}/roles")

    async def test_set_drive_tag_sends_drives_as_comma_separated_string(
        self,
    ) -> None:
        """The documented body is a comma-separated string, not a JSON array."""

        vehicle, request = self.create_vehicle()

        await vehicle.set_drive_tag(drives=[10000, 10001, 10002], tag="Business")

        request.assert_awaited_once_with(
            Method.POST,
            f"{self.VIN}/drives/set_tag",
            json={"drives": "10000,10001,10002", "tag": "Business"},
        )

    async def test_drives_passes_boolean_exclude_flags(self) -> None:
        """exclude_tag and exclude_driver_profile are booleans in the reference."""

        vehicle, request = self.create_vehicle()

        await vehicle.drives(
            tag="Work",
            exclude_tag=True,
            driver_profile="Alex",
            exclude_driver_profile=False,
        )

        params = request.await_args.kwargs["params"]  # pyright: ignore[reportOptionalMemberAccess]
        self.assertEqual(params["tag"], "Work")
        self.assertIs(params["exclude_tag"], True)
        self.assertEqual(params["driver_profile"], "Alex")
        self.assertIs(params["exclude_driver_profile"], False)

    async def test_map_returns_raw_image_bytes(self) -> None:
        """map should return the PNG bytes through the raw request path."""

        parent = MagicMock()
        png = b"\x89PNG\r\n\x1a\n"
        request_bytes = AsyncMock(return_value=png)
        parent._request_bytes = request_bytes  # pyright: ignore[reportAttributeAccessIssue]
        vehicle = TessieVehicle(parent, self.VIN)

        response = await vehicle.map(width=800, height=600, zoom=15, marker_size=75)

        self.assertEqual(response, png)
        request_bytes.assert_awaited_once_with(
            f"{self.VIN}/map",
            params={
                "width": 800,
                "height": 600,
                "zoom": 15,
                "marker_size": 75,
                "style": None,
            },
        )


class TessieRequestBytesTests(IsolatedAsyncioTestCase):
    """The raw-bytes request path used by map()."""

    async def test_request_bytes_returns_body_without_json_decoding(self) -> None:
        """A non-JSON body is returned as bytes with the usual auth headers."""

        png = b"\x89PNG\r\n\x1a\n\xff"
        resp = MagicMock()
        resp.ok = True
        resp.status = 200
        resp.read = AsyncMock(return_value=png)
        context = MagicMock()
        context.__aenter__ = AsyncMock(return_value=resp)
        context.__aexit__ = AsyncMock(return_value=False)
        session = MagicMock()
        session.request = MagicMock(return_value=context)

        client = Tessie(session, "token")
        result = await client._request_bytes(  # pyright: ignore[reportPrivateUsage]
            "VIN/map", params={"zoom": 15, "style": None}
        )

        self.assertEqual(result, png)
        _, kwargs = session.request.call_args
        self.assertEqual(kwargs["headers"]["Authorization"], "Bearer token")
        self.assertEqual(kwargs["params"], {"zoom": 15})
        self.assertEqual(session.request.call_args.args[0], Method.GET)
        self.assertEqual(
            session.request.call_args.args[1], "https://api.tessie.com/VIN/map"
        )
