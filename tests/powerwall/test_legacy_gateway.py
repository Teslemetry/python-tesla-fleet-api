"""Tests for is_legacy_gateway over the cloud site_info body."""

from __future__ import annotations

from typing import Any

import pytest

from tesla_fleet_api.exceptions import InvalidResponse
from tesla_fleet_api.tesla.powerwall import is_legacy_gateway

GATEWAY_1_DIN = "1118431-01-F--TG000000000000"
GATEWAY_2_DIN = "1232100-00-E--TG000000000000"


def _gateway(part_number: str) -> dict[str, Any]:
    return {
        "device_id": "device",
        "din": f"{part_number}--TG000000000000",
        "serial_number": "TG000000000000",
        "part_number": part_number,
        "is_active": True,
    }


@pytest.mark.parametrize(
    ("site_info", "expected"),
    [
        pytest.param(
            {
                "id": GATEWAY_2_DIN,
                "components": {"gateways": [_gateway("1118431-01-F")]},
            },
            True,
            id="gateway_1_part_number",
        ),
        pytest.param(
            {
                "id": GATEWAY_2_DIN,
                "components": {"gateways": [_gateway("1232100-00-E")]},
            },
            False,
            id="gateway_2_part_number",
        ),
        pytest.param(
            {
                "id": GATEWAY_1_DIN,
                "components": {"gateways": [_gateway("1232100-00-E")]},
            },
            False,
            id="listed_gateway_wins_over_id",
        ),
        pytest.param(
            {"id": GATEWAY_1_DIN, "components": {"gateways": []}},
            True,
            id="gateway_1_site_din",
        ),
        pytest.param(
            {"id": GATEWAY_1_DIN, "components": {}}, True, id="no_gateways_key"
        ),
        pytest.param({"id": GATEWAY_2_DIN}, False, id="gateway_2_site_din"),
        pytest.param(
            {"id": GATEWAY_1_DIN, "components": {"gateways": [{"part_number": None}]}},
            True,
            id="gateway_without_part_number_falls_back_to_id",
        ),
    ],
)
def test_is_legacy_gateway(site_info: dict[str, Any], expected: bool) -> None:
    assert is_legacy_gateway(site_info) is expected


@pytest.mark.parametrize(
    "site_info",
    [
        pytest.param(None, id="null_body"),
        pytest.param({}, id="empty_body"),
        pytest.param({"components": {"gateways": []}}, id="no_gateways_no_id"),
        pytest.param(
            {"components": {"gateways": [{"din": GATEWAY_1_DIN}]}},
            id="no_part_number_no_id",
        ),
    ],
)
def test_is_legacy_gateway_unknown_shape(site_info: Any) -> None:
    with pytest.raises(InvalidResponse):
        is_legacy_gateway(site_info)
