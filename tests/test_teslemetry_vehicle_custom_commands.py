"""Tests for the ``TeslemetryVehicle`` ``custom_command/*`` methods added for
command parity with Teslemetry's source-verified route inventory.

These routes have no public OpenAPI schema, so each test only pins the
request shape (method, path, JSON body) this library sends - not a live
response contract.
"""

from __future__ import annotations

from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, MagicMock

from tesla_fleet_api.const import (
    DistanceUnit,
    EnergyDisplayFormat,
    Method,
    TemperatureUnit,
    TimeDisplayFormat,
    TirePressureUnit,
)
from tesla_fleet_api.teslemetry.vehicle import TeslemetryVehicle

VIN = "5YJ3E1EA1JF000001"


def _make_vehicle() -> tuple[TeslemetryVehicle, AsyncMock]:
    parent = MagicMock()
    request = AsyncMock(return_value={"response": {"result": True}})
    parent._request = request  # pyright: ignore[reportAttributeAccessIssue]
    return TeslemetryVehicle(parent, VIN), request


class CustomCommandRequestShapeTests(IsolatedAsyncioTestCase):
    """Each ``custom_command/*`` method sends the expected method/path/body."""

    async def test_get_charge_on_solar(self) -> None:
        vehicle, request = _make_vehicle()
        await vehicle.get_charge_on_solar()
        request.assert_awaited_once_with(
            Method.GET, f"api/1/vehicles/{VIN}/custom_command/charge_on_solar"
        )

    async def test_set_front_zone_lights(self) -> None:
        vehicle, request = _make_vehicle()
        await vehicle.set_front_zone_lights(2)
        request.assert_awaited_once_with(
            Method.POST,
            f"api/1/vehicles/{VIN}/custom_command/front_zone_light",
            json={"level": 2},
        )

    async def test_set_rear_zone_lights(self) -> None:
        vehicle, request = _make_vehicle()
        await vehicle.set_rear_zone_lights(1)
        request.assert_awaited_once_with(
            Method.POST,
            f"api/1/vehicles/{VIN}/custom_command/rear_zone_light",
            json={"level": 1},
        )

    async def test_set_outlets(self) -> None:
        vehicle, request = _make_vehicle()
        await vehicle.set_outlets(1)
        request.assert_awaited_once_with(
            Method.POST,
            f"api/1/vehicles/{VIN}/custom_command/set_outlets",
            json={"request": 1},
        )

    async def test_set_outlet_soc_limit(self) -> None:
        vehicle, request = _make_vehicle()
        await vehicle.set_outlet_soc_limit(80)
        request.assert_awaited_once_with(
            Method.POST,
            f"api/1/vehicles/{VIN}/custom_command/set_outlet_soc_limit",
            json={"percent": 80},
        )

    async def test_set_power_feed(self) -> None:
        vehicle, request = _make_vehicle()
        await vehicle.set_power_feed(3)
        request.assert_awaited_once_with(
            Method.POST,
            f"api/1/vehicles/{VIN}/custom_command/set_power_feed",
            json={"request": 3},
        )

    async def test_set_power_feed_soc_limit(self) -> None:
        vehicle, request = _make_vehicle()
        await vehicle.set_power_feed_soc_limit(90)
        request.assert_awaited_once_with(
            Method.POST,
            f"api/1/vehicles/{VIN}/custom_command/set_power_feed_soc_limit",
            json={"percent": 90},
        )

    async def test_set_lightbar_brightness(self) -> None:
        vehicle, request = _make_vehicle()
        await vehicle.set_lightbar_brightness(50)
        request.assert_awaited_once_with(
            Method.POST,
            f"api/1/vehicles/{VIN}/custom_command/set_lightbar_brightness",
            json={"brightness": 50},
        )

    async def test_set_lightbar_middle(self) -> None:
        vehicle, request = _make_vehicle()
        await vehicle.set_lightbar_middle(True)
        request.assert_awaited_once_with(
            Method.POST,
            f"api/1/vehicles/{VIN}/custom_command/set_lightbar_middle",
            json={"on": True},
        )

    async def test_set_lightbar_ditch(self) -> None:
        vehicle, request = _make_vehicle()
        await vehicle.set_lightbar_ditch(False)
        request.assert_awaited_once_with(
            Method.POST,
            f"api/1/vehicles/{VIN}/custom_command/set_lightbar_ditch",
            json={"on": False},
        )

    async def test_set_trailer_light_test(self) -> None:
        vehicle, request = _make_vehicle()
        await vehicle.set_trailer_light_test(True)
        request.assert_awaited_once_with(
            Method.POST,
            f"api/1/vehicles/{VIN}/custom_command/set_trailer_light_test",
            json={"on": True},
        )

    async def test_set_truck_bed_light_auto(self) -> None:
        vehicle, request = _make_vehicle()
        await vehicle.set_truck_bed_light_auto(True)
        request.assert_awaited_once_with(
            Method.POST,
            f"api/1/vehicles/{VIN}/custom_command/set_truck_bed_light_auto",
            json={"on": True},
        )

    async def test_set_truck_bed_light_brightness(self) -> None:
        vehicle, request = _make_vehicle()
        await vehicle.set_truck_bed_light_brightness(75)
        request.assert_awaited_once_with(
            Method.POST,
            f"api/1/vehicles/{VIN}/custom_command/set_truck_bed_light_brightness",
            json={"brightness": 75},
        )

    async def test_set_powershare_feature(self) -> None:
        vehicle, request = _make_vehicle()
        await vehicle.set_powershare_feature(True)
        request.assert_awaited_once_with(
            Method.POST,
            f"api/1/vehicles/{VIN}/custom_command/set_powershare_feature",
            json={"on": True},
        )

    async def test_set_powershare_request(self) -> None:
        vehicle, request = _make_vehicle()
        await vehicle.set_powershare_request(True)
        request.assert_awaited_once_with(
            Method.POST,
            f"api/1/vehicles/{VIN}/custom_command/set_powershare_request",
            json={"on": True},
        )

    async def test_set_powershare_discharge_limit(self) -> None:
        vehicle, request = _make_vehicle()
        await vehicle.set_powershare_discharge_limit(20)
        request.assert_awaited_once_with(
            Method.POST,
            f"api/1/vehicles/{VIN}/custom_command/set_powershare_discharge_limit",
            json={"percent": 20},
        )

    async def test_set_recirculation(self) -> None:
        vehicle, request = _make_vehicle()
        await vehicle.set_recirculation(True)
        request.assert_awaited_once_with(
            Method.POST,
            f"api/1/vehicles/{VIN}/custom_command/hvac_recirculation",
            json={"on": True},
        )

    async def test_set_tent_mode(self) -> None:
        vehicle, request = _make_vehicle()
        await vehicle.set_tent_mode(True)
        request.assert_awaited_once_with(
            Method.POST,
            f"api/1/vehicles/{VIN}/custom_command/set_tent_mode",
            json={"on": True},
        )

    async def test_set_suspension_level(self) -> None:
        vehicle, request = _make_vehicle()
        await vehicle.set_suspension_level(4)
        request.assert_awaited_once_with(
            Method.POST,
            f"api/1/vehicles/{VIN}/custom_command/set_suspension_level",
            json={"level": 4},
        )

    async def test_set_low_power_mode(self) -> None:
        vehicle, request = _make_vehicle()
        await vehicle.set_low_power_mode(True)
        request.assert_awaited_once_with(
            Method.POST,
            f"api/1/vehicles/{VIN}/custom_command/set_low_power_mode",
            json={"on": True},
        )

    async def test_set_keep_accessory_power_mode(self) -> None:
        vehicle, request = _make_vehicle()
        await vehicle.set_keep_accessory_power_mode(True)
        request.assert_awaited_once_with(
            Method.POST,
            f"api/1/vehicles/{VIN}/custom_command/set_keep_accessory_power_mode",
            json={"on": True},
        )

    async def test_set_temperature_unit(self) -> None:
        vehicle, request = _make_vehicle()
        await vehicle.set_temperature_unit(TemperatureUnit.CELSIUS)
        request.assert_awaited_once_with(
            Method.POST,
            f"api/1/vehicles/{VIN}/custom_command/set_temperature_unit",
            json={"unit": TemperatureUnit.CELSIUS},
        )

    async def test_set_distance_unit(self) -> None:
        vehicle, request = _make_vehicle()
        await vehicle.set_distance_unit(DistanceUnit.KILOMETERS)
        request.assert_awaited_once_with(
            Method.POST,
            f"api/1/vehicles/{VIN}/custom_command/set_distance_unit",
            json={"unit": DistanceUnit.KILOMETERS},
        )

    async def test_set_time_display_format(self) -> None:
        vehicle, request = _make_vehicle()
        await vehicle.set_time_display_format(TimeDisplayFormat.HOUR_24)
        request.assert_awaited_once_with(
            Method.POST,
            f"api/1/vehicles/{VIN}/custom_command/set_time_display_format",
            json={"format": TimeDisplayFormat.HOUR_24},
        )

    async def test_set_tire_pressure_unit(self) -> None:
        vehicle, request = _make_vehicle()
        await vehicle.set_tire_pressure_unit(TirePressureUnit.BAR)
        request.assert_awaited_once_with(
            Method.POST,
            f"api/1/vehicles/{VIN}/custom_command/set_tire_pressure_unit",
            json={"unit": TirePressureUnit.BAR},
        )

    async def test_set_energy_display_format(self) -> None:
        vehicle, request = _make_vehicle()
        await vehicle.set_energy_display_format(EnergyDisplayFormat.DISTANCE)
        request.assert_awaited_once_with(
            Method.POST,
            f"api/1/vehicles/{VIN}/custom_command/set_energy_display_format",
            json={"format": EnergyDisplayFormat.DISTANCE},
        )

    async def test_parental_controls(self) -> None:
        vehicle, request = _make_vehicle()
        await vehicle.parental_controls(True, "1234")
        request.assert_awaited_once_with(
            Method.POST,
            f"api/1/vehicles/{VIN}/custom_command/parental_controls",
            json={"activate": True, "pin": "1234"},
        )

    async def test_parental_controls_enable_setting(self) -> None:
        vehicle, request = _make_vehicle()
        await vehicle.parental_controls_enable_setting(1, True)
        request.assert_awaited_once_with(
            Method.POST,
            f"api/1/vehicles/{VIN}/custom_command/parental_controls_enable_setting",
            json={"setting": 1, "enable": True},
        )

    async def test_parental_controls_set_speed_limit(self) -> None:
        vehicle, request = _make_vehicle()
        await vehicle.parental_controls_set_speed_limit(65.0)
        request.assert_awaited_once_with(
            Method.POST,
            f"api/1/vehicles/{VIN}/custom_command/parental_controls_set_speed_limit",
            json={"limit_mph": 65.0},
        )

    async def test_navigation_gps_destination_request(self) -> None:
        vehicle, request = _make_vehicle()
        await vehicle.navigation_gps_destination_request(
            37.3230, -122.0322, "Tesla HQ", 1
        )
        request.assert_awaited_once_with(
            Method.POST,
            f"api/1/vehicles/{VIN}/custom_command/navigation_gps_destination",
            json={
                "lat": 37.3230,
                "lon": -122.0322,
                "destination": "Tesla HQ",
                "order": 1,
            },
        )

    async def test_auto_secure_vehicle(self) -> None:
        vehicle, request = _make_vehicle()
        await vehicle.auto_secure_vehicle()
        request.assert_awaited_once_with(
            Method.POST,
            f"api/1/vehicles/{VIN}/custom_command/auto_secure_vehicle",
        )

    async def test_cancel_soh_test(self) -> None:
        vehicle, request = _make_vehicle()
        await vehicle.cancel_soh_test()
        request.assert_awaited_once_with(
            Method.POST,
            f"api/1/vehicles/{VIN}/custom_command/cancel_soh_test",
        )

    async def test_get_nearby_charging_sites_omits_unset_fields(self) -> None:
        vehicle, request = _make_vehicle()
        await vehicle.get_nearby_charging_sites()
        request.assert_awaited_once_with(
            Method.POST,
            f"api/1/vehicles/{VIN}/custom_command/get_nearby_charging_sites",
            json={},
        )

    async def test_get_nearby_charging_sites_with_params(self) -> None:
        vehicle, request = _make_vehicle()
        await vehicle.get_nearby_charging_sites(count=5, radius=25, detail=True)
        request.assert_awaited_once_with(
            Method.POST,
            f"api/1/vehicles/{VIN}/custom_command/get_nearby_charging_sites",
            json={"count": 5, "radius": 25, "detail": True},
        )

    async def test_get_rate_tariff(self) -> None:
        vehicle, request = _make_vehicle()
        await vehicle.get_rate_tariff()
        request.assert_awaited_once_with(
            Method.POST,
            f"api/1/vehicles/{VIN}/custom_command/get_rate_tariff",
        )

    async def test_trigger_rate_tariff_update(self) -> None:
        vehicle, request = _make_vehicle()
        await vehicle.trigger_rate_tariff_update()
        request.assert_awaited_once_with(
            Method.POST,
            f"api/1/vehicles/{VIN}/custom_command/set_rate_tariff",
        )
