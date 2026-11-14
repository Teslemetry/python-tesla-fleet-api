"""Tests for the Wall Connector commands on ``EnergySite``.

Each is an unsigned ``grpc_command`` addressed to the connector's DIN. The
reply fixtures follow the shape Tesla's cloud returns for each message.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock

from cryptography.hazmat.primitives.asymmetric import rsa

from tesla_fleet_api.const import Method, WallConnectorThirdPartyVehicleMode
from tesla_fleet_api.exceptions import DeviceUnexpectedResponse, InvalidResponse
from tesla_fleet_api.tesla.energysite import EnergySite
from tesla_fleet_api.teslemetry.energysite import TeslemetryEnergySite

SITE_ID = 12345
WC_DIN = "1529455-02-F--PGT00000000000"
GATEWAY_DIN = "1707000-30-L--TG000000000000"
REPLIES: dict[str, Any] = json.loads(
    (Path(__file__).parent / "fixtures" / "wall_connector_replies.json").read_text()
)


def _site(command: str, **kwargs: Any) -> tuple[EnergySite, AsyncMock]:
    request_mock = AsyncMock(return_value=copy.deepcopy(REPLIES[command]))
    parent = AsyncMock()
    parent._request = request_mock
    return EnergySite(parent, SITE_ID, **kwargs), request_mock


def _body(command: str, params: dict[str, Any]) -> dict[str, Any]:
    return {
        "command_type": "grpc_command",
        "command_properties": {
            "message": {"wc": {command: params}},
            "identifier_type": 4,
            "target_id": WC_DIN,
        },
    }


def _sent(request_mock: AsyncMock) -> dict[str, Any]:
    request_mock.assert_awaited_once()
    args = request_mock.await_args
    assert args is not None
    assert args.args == (Method.POST, f"api/1/energy_sites/{SITE_ID}/command")
    return args.kwargs["json"]


def _schedule_params(
    enabled: bool, periods: list[dict[str, int]], offset: int = 36000
) -> dict[str, Any]:
    return {
        "config": {
            "enable_schedule": enabled,
            "schedule": {
                "day_time_periods": [{"day_bitmask": 127, "time_periods": periods}]
            },
            "delay": {"max_delay_seconds": 0},
        },
        "time_zone": {
            "time_zone_id": "Australia/Brisbane",
            "time_zone_info": {
                "transitions": [
                    {
                        "timestamp": {"seconds": 0, "nanos": 0},
                        "local_time_utc_offset": offset,
                    }
                ]
            },
        },
    }


class UnsignedTargetTests(IsolatedAsyncioTestCase):
    async def test_gateway_command_has_no_target_id(self) -> None:
        site, request_mock = _site("get_config_request")
        await site.get_system_info()
        self.assertNotIn("target_id", _sent(request_mock)["command_properties"])

    async def test_signing_key_does_not_sign_wall_connector_commands(self) -> None:
        key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        site, request_mock = _site(
            "get_config_request", private_key=key, din=GATEWAY_DIN
        )
        await site.get_wall_connector_config(WC_DIN)
        self.assertEqual(_sent(request_mock), _body("get_config_request", {}))


class ReadTests(IsolatedAsyncioTestCase):
    async def test_get_config(self) -> None:
        site, request_mock = _site("get_config_request")
        config = await site.get_wall_connector_config(WC_DIN)
        self.assertEqual(_sent(request_mock), _body("get_config_request", {}))
        self.assertEqual(config["settings"]["max_output_current_amps"], 32)

    async def test_get_recent_vehicles(self) -> None:
        site, request_mock = _site("get_recent_vehicles_request")
        vins = await site.get_wall_connector_recent_vehicles(WC_DIN)
        self.assertEqual(_sent(request_mock), _body("get_recent_vehicles_request", {}))
        self.assertEqual(vins, ["5YJ3E1EA0KF000001", "LRW3F7EK0NC000002"])

    async def test_get_recent_vehicles_empty(self) -> None:
        site, request_mock = _site("get_recent_vehicles_request")
        request_mock.return_value["response"]["message"]["Payload"]["Wc"]["Message"][
            "GetRecentVehiclesResponse"
        ] = {}
        self.assertEqual(await site.get_wall_connector_recent_vehicles(WC_DIN), [])

    async def test_get_recent_vehicles_plain_strings(self) -> None:
        site, request_mock = _site("get_recent_vehicles_request")
        request_mock.return_value["response"]["message"]["Payload"]["Wc"]["Message"][
            "GetRecentVehiclesResponse"
        ] = {"recent_vehicles": ["5YJ3E1EA0KF000001", "LRW3F7EK0NC000002"]}
        self.assertEqual(
            await site.get_wall_connector_recent_vehicles(WC_DIN),
            ["5YJ3E1EA0KF000001", "LRW3F7EK0NC000002"],
        )

    async def test_get_recent_vehicles_rejects_unknown_entries(self) -> None:
        for entries in ([1], [{"vin": "x"}], [{"value": 1}], {"value": "x"}):
            with self.subTest(entries=entries):
                site, request_mock = _site("get_recent_vehicles_request")
                request_mock.return_value["response"]["message"]["Payload"]["Wc"][
                    "Message"
                ]["GetRecentVehiclesResponse"] = {"recent_vehicles": entries}
                with self.assertRaises(InvalidResponse):
                    await site.get_wall_connector_recent_vehicles(WC_DIN)

    async def test_unexpected_reply_shape_raises(self) -> None:
        for reply in (
            None,
            {"response": None},
            {"response": {"message": {"Payload": {"Wc": {"Message": {}}}}}},
            REPLIES["push_charge_command_request"],
        ):
            with self.subTest(reply=reply):
                site, request_mock = _site("get_config_request")
                request_mock.return_value = reply
                with self.assertRaises(InvalidResponse):
                    await site.get_wall_connector_config(WC_DIN)


class ScheduleTests(IsolatedAsyncioTestCase):
    async def test_same_day_window_is_one_period(self) -> None:
        site, request_mock = _site("configure_charge_schedule_request")
        result = await site.set_wall_connector_charge_schedule(
            WC_DIN, True, 39600, 57600, "Australia/Brisbane", 36000
        )
        self.assertEqual(
            _sent(request_mock),
            _body(
                "configure_charge_schedule_request",
                _schedule_params(
                    True, [{"start_seconds": 39600, "end_seconds": 57600}]
                ),
            ),
        )
        self.assertEqual(result, {"error": 1})

    async def test_overnight_window_splits_at_midnight(self) -> None:
        site, request_mock = _site("configure_charge_schedule_request")
        await site.set_wall_connector_charge_schedule(
            WC_DIN, False, 84600, 19800, "Australia/Brisbane", 36000
        )
        self.assertEqual(
            _sent(request_mock),
            _body(
                "configure_charge_schedule_request",
                _schedule_params(
                    False,
                    [
                        {"start_seconds": 84600, "end_seconds": 86400},
                        {"start_seconds": 0, "end_seconds": 19800},
                    ],
                ),
            ),
        )

    async def test_overnight_window_moves_morning_to_next_day(self) -> None:
        for days, next_days in ((2, 4), (64, 1), (2 | 64, 4 | 1), (65, 3)):
            with self.subTest(days=days):
                site, request_mock = _site("configure_charge_schedule_request")
                await site.set_wall_connector_charge_schedule(
                    WC_DIN, True, 84600, 19800, "Australia/Brisbane", 36000, days
                )
                sent = _sent(request_mock)["command_properties"]["message"]["wc"][
                    "configure_charge_schedule_request"
                ]["config"]["schedule"]["day_time_periods"]
                self.assertEqual(
                    sent,
                    [
                        {
                            "day_bitmask": days,
                            "time_periods": [
                                {"start_seconds": 84600, "end_seconds": 86400}
                            ],
                        },
                        {
                            "day_bitmask": next_days,
                            "time_periods": [
                                {"start_seconds": 0, "end_seconds": 19800}
                            ],
                        },
                    ],
                )

    async def test_window_ending_at_midnight_is_one_period(self) -> None:
        for end in (0, 86400):
            with self.subTest(end=end):
                site, request_mock = _site("configure_charge_schedule_request")
                await site.set_wall_connector_charge_schedule(
                    WC_DIN, True, 79200, end, "Australia/Brisbane", 36000
                )
                periods = _sent(request_mock)["command_properties"]["message"]["wc"][
                    "configure_charge_schedule_request"
                ]["config"]["schedule"]["day_time_periods"][0]["time_periods"]
                self.assertEqual(
                    periods, [{"start_seconds": 79200, "end_seconds": 86400}]
                )

    async def test_invalid_arguments_send_nothing(self) -> None:
        for start, end, days in (
            (3600, 3600, 127),
            (-1, 3600, 127),
            (86400, 3600, 127),
            (0, 86401, 127),
            (0, 3600, 0),
            (0, 3600, 128),
        ):
            with self.subTest(start=start, end=end, days=days):
                site, request_mock = _site("configure_charge_schedule_request")
                with self.assertRaises(ValueError):
                    await site.set_wall_connector_charge_schedule(
                        WC_DIN, True, start, end, "UTC", 0, days
                    )
                request_mock.assert_not_awaited()

    async def test_schedule_error_raises(self) -> None:
        for reply, code, name in (
            ({"error": 4}, 4, "WC_CHARGE_SCHEDULE_ERROR_INTERNAL"),
            ({}, 0, "WC_CHARGE_SCHEDULE_ERROR_INVALID"),
            ({"error": 99}, 99, "99"),
        ):
            with self.subTest(reply=reply):
                site, request_mock = _site("configure_charge_schedule_request")
                request_mock.return_value["response"]["message"]["Payload"]["Wc"][
                    "Message"
                ]["ConfigureChargeScheduleResponse"] = reply
                with self.assertRaises(DeviceUnexpectedResponse) as ctx:
                    await site.set_wall_connector_charge_schedule(
                        WC_DIN, True, 0, 3600, "UTC", 0
                    )
                self.assertEqual(ctx.exception.data, {"code": code, "message": name})


class ActionTests(IsolatedAsyncioTestCase):
    async def test_start_and_stop_charging(self) -> None:
        for method, command in (
            (EnergySite.start_wall_connector_charging, 1),
            (EnergySite.stop_wall_connector_charging, 2),
        ):
            with self.subTest(command=command):
                site, request_mock = _site("push_charge_command_request")
                self.assertEqual(await method(site, WC_DIN), {})
                self.assertEqual(
                    _sent(request_mock),
                    _body(
                        "push_charge_command_request",
                        {"charge_command": {"charging_command": command}},
                    ),
                )

    async def test_third_party_vehicle_mode(self) -> None:
        site, request_mock = _site("configure_third_party_vehicle_mode_request")
        result = await site.set_wall_connector_third_party_vehicle_mode(
            WC_DIN, WallConnectorThirdPartyVehicleMode.DISABLED
        )
        self.assertEqual(result, {})
        self.assertEqual(
            _sent(request_mock),
            _body(
                "configure_third_party_vehicle_mode_request",
                {"third_party_vehicle_mode": 2},
            ),
        )


class TeslemetryTests(IsolatedAsyncioTestCase):
    async def test_wall_connector_commands_send_nothing(self) -> None:
        request_mock = AsyncMock()
        parent = AsyncMock()
        parent._request = request_mock
        site = TeslemetryEnergySite(parent, SITE_ID)
        with self.assertRaises(NotImplementedError):
            await site.get_wall_connector_config(WC_DIN)
        request_mock.assert_not_awaited()
