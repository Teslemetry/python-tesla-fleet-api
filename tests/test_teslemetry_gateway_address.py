"""Tests for TeslemetryEnergySite.find_gateway_address(), the typed accessor
over the Teslemetry ``command/networking_status`` endpoint.

Only ``eth``/``wifi`` are considered (never ``gsm`` - cellular isn't a LAN
path). An interface with ``active_route`` set wins; otherwise the first of
``eth``, ``wifi`` (in that order) with a decodable address is used. Address
fields on the wire are raw big-endian uint32 integers, not strings - see
``GatewayAddressRealCaptureTests`` for the real captured sample this decoding
is pinned against (see ``_parse_gateway_address`` in
``tesla_fleet_api/teslemetry/energysite.py``).

A null body or an unrecognized response shape is malformed data and must
raise :class:`~tesla_fleet_api.exceptions.InvalidResponse`; a well-formed
response that simply has no usable interface returns ``None``.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, MagicMock

from tesla_fleet_api.exceptions import InvalidResponse
from tesla_fleet_api.teslemetry.teslemetry import Teslemetry

_UNSET = object()


def _fake_response(*, json_body: object = _UNSET) -> MagicMock:
    resp = MagicMock()
    resp.status = 200
    resp.ok = True
    resp.content_type = "application/json"
    resp.url = "https://example.com/x"
    resp.headers = {}
    resp.json = AsyncMock(return_value={} if json_body is _UNSET else json_body)
    resp.text = AsyncMock(return_value="")
    return resp


def _make_session(response: object) -> MagicMock:
    session = MagicMock()

    @asynccontextmanager
    async def _ctx(*args: Any, **kwargs: Any):
        yield response

    session.request = MagicMock(side_effect=lambda *a, **k: _ctx(*a, **k))
    return session


def _make_site(json_body: object):
    api = Teslemetry(
        session=_make_session(_fake_response(json_body=json_body)),
        access_token="token",
    )
    return api.energySites.create(12345)


class GatewayAddressRealCaptureTests(IsolatedAsyncioTestCase):
    """Captured 2026-07-14 from a Powerwall 3's ``networking_status``
    response (identifiers anonymized, structure verbatim). ``wifi`` is the
    active route; ``eth`` is populated but not active; ``gsm`` must never
    be considered.
    """

    REAL_CAPTURE_RESPONSE = {
        "response": {
            "wifi_config": {"ssid": "ANONYMIZED_SSID"},
            "wifi": {
                "mac_address": "ANONYMIZED_MAC_1",
                "enabled": True,
                "active_route": True,
                "ipv4_config": {
                    "dhcp_enabled": True,
                    "address": 3232235914,
                    "subnet_mask": 4294967040,
                    "gateway": 3232235777,
                },
                "connectivity_status": {
                    "connected_physical": True,
                    "connected_internet": True,
                    "connected_tesla": True,
                    "rssi": {"signal_strength_percent": {"value": 42}},
                },
                "device_state": 6,
                "device_state_reason": 1,
            },
            "eth": {
                "mac_address": "ANONYMIZED_MAC_2",
                "enabled": True,
                "ipv4_config": {
                    "dhcp_enabled": True,
                    "address": 3232258562,
                    "subnet_mask": 4294967040,
                },
                "connectivity_status": {"rssi": {"signal_strength_percent": {}}},
            },
            "gsm": {
                "enabled": True,
                "ipv4_config": {
                    "address": 168866907,
                    "subnet_mask": 4294967295,
                    "gateway": 168866907,
                },
                "connectivity_status": {
                    "connected_physical": True,
                    "connected_internet": True,
                    "connected_tesla": True,
                    "rssi": {"signal_strength_percent": {"value": 60}},
                },
            },
        }
    }

    async def test_real_captured_sample_selects_active_route_wifi(self) -> None:
        site = _make_site(self.REAL_CAPTURE_RESPONSE)

        result = await site.find_gateway_address()

        self.assertEqual(result, "192.168.1.138")


class GatewayAddressSelectionTests(IsolatedAsyncioTestCase):
    async def test_eth_preferred_when_eth_has_active_route(self) -> None:
        site = _make_site(
            {
                "response": {
                    "eth": {
                        "active_route": True,
                        "ipv4_config": {"address": 3232235777},
                    },
                    "wifi": {
                        "active_route": True,
                        "ipv4_config": {"address": 3232235914},
                    },
                }
            }
        )

        result = await site.find_gateway_address()

        self.assertEqual(result, "192.168.1.1")

    async def test_no_active_route_falls_back_to_eth_first(self) -> None:
        site = _make_site(
            {
                "response": {
                    "eth": {"ipv4_config": {"address": 3232258562}},
                    "wifi": {"ipv4_config": {"address": 3232235914}},
                }
            }
        )

        result = await site.find_gateway_address()

        self.assertEqual(result, "192.168.90.2")

    async def test_no_active_route_falls_back_to_wifi_when_eth_has_no_address(
        self,
    ) -> None:
        site = _make_site(
            {
                "response": {
                    "eth": {"enabled": True},
                    "wifi": {"ipv4_config": {"address": 3232235914}},
                }
            }
        )

        result = await site.find_gateway_address()

        self.assertEqual(result, "192.168.1.138")

    async def test_gsm_only_returns_none(self) -> None:
        site = _make_site(
            {
                "response": {
                    "gsm": {
                        "active_route": True,
                        "ipv4_config": {"address": 168866907},
                    }
                }
            }
        )

        result = await site.find_gateway_address()

        self.assertIsNone(result)

    async def test_empty_response_returns_none(self) -> None:
        site = _make_site({"response": {}})

        result = await site.find_gateway_address()

        self.assertIsNone(result)

    async def test_interfaces_missing_ipv4_config_return_none(self) -> None:
        site = _make_site(
            {"response": {"eth": {"enabled": True}, "wifi": {"enabled": True}}}
        )

        result = await site.find_gateway_address()

        self.assertIsNone(result)

    async def test_bare_body_without_response_envelope(self) -> None:
        site = _make_site(
            {"wifi": {"active_route": True, "ipv4_config": {"address": 3232235914}}}
        )

        result = await site.find_gateway_address()

        self.assertEqual(result, "192.168.1.138")


class GatewayAddressInvalidResponseTests(IsolatedAsyncioTestCase):
    async def test_null_body_raises_invalid_response(self) -> None:
        site = _make_site(None)

        with self.assertRaises(InvalidResponse):
            await site.find_gateway_address()

    async def test_unrecognized_non_dict_body_raises_invalid_response(self) -> None:
        site = _make_site("not-a-valid-shape")

        with self.assertRaises(InvalidResponse):
            await site.find_gateway_address()

    async def test_list_body_raises_invalid_response(self) -> None:
        site = _make_site([])

        with self.assertRaises(InvalidResponse):
            await site.find_gateway_address()
