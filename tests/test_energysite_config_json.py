"""Tests for the config.json grid export/import limit and solar curtailment commands.

A ``TeslemetryEnergySite`` without a key calls Teslemetry's ``config_json``
routes. With a key, either backend signs a filestore read of config.json and a
hash-checked update of it through ``device_command``. A Fleet API site without
a key raises ``SignedCommandRequired``.
"""

from __future__ import annotations

import base64
import json
from typing import Any
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock

from cryptography.hazmat.primitives.asymmetric import rsa
from tesla_protocol.energy_device import (
    filestore_api_pb2,
    signed_message_pb2,
    transport_pb2,
)

from tesla_fleet_api.const import Method
from tesla_fleet_api.exceptions import InvalidResponse, SignedCommandRequired
from tesla_fleet_api.tesla.energysite import EnergySite
from tesla_fleet_api.teslemetry.energysite import TeslemetryEnergySite

SITE_ID = 12345
DIN = "1232100-00-E--TG123456789ABC"
HASH = b"\x01\x02hash"
CONFIG: dict[str, Any] = {
    "vin": "1232100-00-E--TG123456789ABC",
    "site_info": {
        "site_name": "Home",
        "min_site_meter_power_ac": -5,
        "max_site_meter_power_ac": 20,
    },
}

# A test key only; it is not registered on any gateway.
TEST_KEY = rsa.generate_private_key(public_exponent=65537, key_size=2048)

INVALID_SETTINGS: list[dict[str, Any]] = [
    {},
    {"min_site_meter_power_ac": 1},
    {"min_site_meter_power_ac": -1001},
    {"min_site_meter_power_ac": float("-inf")},
    {"min_site_meter_power_ac": float("nan")},
    {"min_site_meter_power_ac": True},
    {"max_site_meter_power_ac": -1},
    {"max_site_meter_power_ac": 1001},
    {"max_site_meter_power_ac": "5"},
    {"on_grid_solar_curtailment_enabled": 1},
]


def _site(cls: type[EnergySite], signed: bool = False) -> tuple[EnergySite, AsyncMock]:
    request_mock: AsyncMock = AsyncMock(return_value={"response": {}})
    parent = AsyncMock()
    parent._request = request_mock
    if signed:
        return cls(parent, SITE_ID, private_key=TEST_KEY, din=DIN), request_mock
    return cls(parent, SITE_ID), request_mock


def _reply(field: str, config: dict[str, Any], hash_: bytes = HASH) -> dict[str, Any]:
    """A ``device_command`` reply carrying a filestore answer."""
    envelope = transport_pb2.MessageEnvelope()
    answer = getattr(envelope.filestore, field)
    answer.file.name = "config.json"
    answer.file.blob = json.dumps(config).encode()
    answer.hash = hash_
    return {
        "response": {
            "message_envelope_as_bytes": base64.b64encode(
                envelope.SerializeToString()
            ).decode()
        }
    }


def _sent_envelope(call: Any) -> transport_pb2.MessageEnvelope:
    """The ``MessageEnvelope`` inside a recorded ``device_command`` call."""
    body = call.kwargs["json"]
    body = body.get("data", body)
    routable = signed_message_pb2.RoutableMessage()
    routable.ParseFromString(base64.b64decode(body["routable_message"]))
    envelope = transport_pb2.MessageEnvelope()
    envelope.ParseFromString(routable.protobuf_message_as_bytes)
    return envelope


class TeslemetryKeylessTests(IsolatedAsyncioTestCase):
    async def test_get_config_json_calls_route(self) -> None:
        site, request_mock = _site(TeslemetryEnergySite)
        await site.get_config_json()
        request_mock.assert_awaited_once_with(
            Method.GET, f"api/1/energy_sites/{SITE_ID}/command/config_json"
        )

    async def test_set_config_json_posts_only_given_keys(self) -> None:
        site, request_mock = _site(TeslemetryEnergySite)
        await site.set_config_json(
            max_site_meter_power_ac=14.5, on_grid_solar_curtailment_enabled=False
        )
        request_mock.assert_awaited_once_with(
            Method.POST,
            f"api/1/energy_sites/{SITE_ID}/command/config_json",
            json={
                "max_site_meter_power_ac": 14.5,
                "on_grid_solar_curtailment_enabled": False,
            },
        )

    async def test_named_setters(self) -> None:
        cases: list[tuple[str, Any, dict[str, Any]]] = [
            ("set_export_limit", 5, {"min_site_meter_power_ac": -5}),
            ("set_import_limit", 2.5, {"max_site_meter_power_ac": 2.5}),
            (
                "set_on_grid_solar_curtailment",
                True,
                {"on_grid_solar_curtailment_enabled": True},
            ),
        ]
        for method, arg, body in cases:
            with self.subTest(method=method):
                site, request_mock = _site(TeslemetryEnergySite)
                await getattr(site, method)(arg)
                self.assertEqual(request_mock.await_args.kwargs["json"], body)

    async def test_invalid_settings_send_nothing(self) -> None:
        for settings in INVALID_SETTINGS:
            with self.subTest(settings=settings):
                site, request_mock = _site(TeslemetryEnergySite)
                with self.assertRaises(ValueError):
                    await site.set_config_json(**settings)
                request_mock.assert_not_awaited()

    async def test_negative_export_limit_raises(self) -> None:
        site, request_mock = _site(TeslemetryEnergySite)
        with self.assertRaises(ValueError):
            await site.set_export_limit(-5)
        request_mock.assert_not_awaited()


class FleetKeylessTests(IsolatedAsyncioTestCase):
    async def test_requires_signing_key(self) -> None:
        for method, kwargs in (
            ("get_config_json", {}),
            ("set_config_json", {"max_site_meter_power_ac": 5}),
        ):
            with self.subTest(method=method):
                site, request_mock = _site(EnergySite)
                with self.assertRaises(SignedCommandRequired):
                    await getattr(site, method)(**kwargs)
                request_mock.assert_not_awaited()


class SignedConfigJsonTests(IsolatedAsyncioTestCase):
    async def test_get_config_json_signs_filestore_read(self) -> None:
        for cls in (EnergySite, TeslemetryEnergySite):
            with self.subTest(cls=cls.__name__):
                site, request_mock = _site(cls, signed=True)
                request_mock.return_value = _reply("read_file_response", CONFIG)
                self.assertEqual(await site.get_config_json(), {"response": CONFIG})
                call = request_mock.await_args
                self.assertEqual(
                    call.args,
                    (Method.POST, f"api/1/energy_sites/{SITE_ID}/device_command"),
                )
                read = _sent_envelope(call).filestore.read_file_request
                self.assertEqual(
                    read.domain, filestore_api_pb2.FILE_STORE_API_DOMAIN_CONFIG_JSON
                )
                self.assertEqual(read.name, "config.json")

    async def test_set_writes_merged_config_with_read_hash(self) -> None:
        for cls in (EnergySite, TeslemetryEnergySite):
            with self.subTest(cls=cls.__name__):
                site, request_mock = _site(cls, signed=True)
                written = {
                    **CONFIG,
                    "site_info": {
                        **CONFIG["site_info"],
                        "min_site_meter_power_ac": -2.5,
                        "on_grid_solar_curtailment_enabled": True,
                    },
                }
                request_mock.side_effect = [
                    _reply("read_file_response", CONFIG),
                    _reply("update_file_response", written, b"new"),
                ]
                result = await site.set_config_json(
                    min_site_meter_power_ac=-2.5,
                    on_grid_solar_curtailment_enabled=True,
                )
                self.assertEqual(
                    result,
                    {
                        "response": {
                            "min_site_meter_power_ac": -2.5,
                            "max_site_meter_power_ac": 20,
                            "on_grid_solar_curtailment_enabled": True,
                            "applied": True,
                        }
                    },
                )
                update = _sent_envelope(
                    request_mock.await_args_list[1]
                ).filestore.update_file_request
                self.assertEqual(
                    update.domain, filestore_api_pb2.FILE_STORE_API_DOMAIN_CONFIG_JSON
                )
                self.assertEqual(update.file.name, "config.json")
                self.assertEqual(update.hash, HASH)
                self.assertEqual(json.loads(update.file.blob), written)

    async def test_unchanged_values_write_nothing(self) -> None:
        site, request_mock = _site(EnergySite, signed=True)
        request_mock.return_value = _reply("read_file_response", CONFIG)
        result = await site.set_config_json(
            min_site_meter_power_ac=-5, on_grid_solar_curtailment_enabled=False
        )
        self.assertTrue(result["response"]["applied"])
        request_mock.assert_awaited_once()

    async def test_readback_mismatch_is_not_applied(self) -> None:
        site, request_mock = _site(EnergySite, signed=True)
        request_mock.side_effect = [
            _reply("read_file_response", CONFIG),
            _reply("update_file_response", CONFIG),
        ]
        result = await site.set_import_limit(10)
        self.assertEqual(result["response"]["max_site_meter_power_ac"], 20)
        self.assertFalse(result["response"]["applied"])

    async def test_unreadable_reply_raises(self) -> None:
        replies: list[dict[str, Any]] = [
            {"response": {}},
            _reply("update_file_response", CONFIG),
            _reply("read_file_response", CONFIG, b""),
            _reply("read_file_response", {"site_info": None}),
        ]
        for reply in replies:
            with self.subTest(reply=reply):
                site, request_mock = _site(EnergySite, signed=True)
                request_mock.return_value = reply
                with self.assertRaises(InvalidResponse):
                    await site.set_import_limit(10)
                request_mock.assert_awaited_once()
