"""Wire tests for the GraphQL and system-info (firmware) reads.

The hex constants are the exact bytes the pre-0.5 ``tedapi`` schema encoded
for the same requests, and gateway replies in the layout a PW3 sends. They pin
the ``tesla_protocol.energy_device`` encoding to that wire format.
"""

from __future__ import annotations

import subprocess
import sys

import pytest

from tesla_fleet_api.tesla.powerwall import PowerwallClient
from tesla_fleet_api.tesla.powerwall.exceptions import PowerwallProtocolError

DIN = "1707000-00-J--TG9999999999XP"
QUERY = " query DeviceControllerQuery {x}"
CODE = b"0\x81\x88\x02B\x026\xddT"

GRAPHQL_REQUEST = bytes.fromhex(
    "0801120218011a1e0a1c313730373030302d30302d4a2d2d5447393939393939393939395850"
    "82013b0a39080212240801122020717565727920446576696365436f6e74726f6c6c65725175"
    "657279207b787d1a0930818802420236dd5422040a027b7d"
)
GRAPHQL_RESPONSE = bytes.fromhex(
    "0801121e0a1c313730373030302d30302d4a2d2d54473939393939393939393958501a021801"
    "82011412120801120e7b22636f6e74726f6c223a7b7d7d"
)
SYSTEM_INFO_REQUEST = bytes.fromhex(
    "0801120218011a1e0a1c313730373030302d30302d4a2d2d544739393939393939393939585022021200"
)
# Fields 1-3 and 5-9 of CommonAPIGetSystemInfoResponse, as the gateway sends
# them: din is a plain string, 5 is SystemUpdate, 6 is DeviceType.
SYSTEM_INFO_RESPONSE = bytes.fromhex(
    "0801121e0a1c313730373030302d30302d4a2d2d54473939393939393939393958501a021801"
    "22b6011ab3010a1e0a0c313730373030302d30302d4a120e5447393939393939393939395850"
    "121c313730373030302d30302d4a2d2d54473939393939393939393958501a210a1932342e31"
    "322e362d5057332d414643492030303862663666661204008bf6ff2a02100130043a3e0a3c0a"
    "090a075175656374656c12090a07424739352d4d321a0f0a0d584d5232303230424739354d32"
    "22130a113130323234412d32303230424739354d324204f82173c64a04fb55ebd2"
)


class _RawTransport:
    def __init__(self, response: bytes) -> None:
        self._response = response
        self.sent: list[bytes] = []

    async def post_v1r(self, envelope_bytes: bytes, din: str) -> bytes:
        assert din == DIN
        self.sent.append(envelope_bytes)
        return self._response


def _client_for(response: bytes) -> tuple[PowerwallClient, _RawTransport]:
    pw = PowerwallClient.__new__(PowerwallClient)

    async def fake_connect() -> str:
        return DIN

    transport = _RawTransport(response)
    pw.connect = fake_connect  # type: ignore[method-assign]
    pw._transport = transport  # type: ignore[attr-defined]
    return pw, transport


async def test_graphql_query_wire_format() -> None:
    pw, transport = _client_for(GRAPHQL_RESPONSE)
    text = await pw._query_graphql(QUERY, CODE, "{}")
    assert transport.sent == [GRAPHQL_REQUEST]
    assert text == '{"control":{}}'


async def test_graphql_response_without_payload_raises() -> None:
    pw, _ = _client_for(SYSTEM_INFO_REQUEST)
    with pytest.raises(PowerwallProtocolError, match="missing payload"):
        await pw._query_graphql(QUERY, CODE, "{}")


async def test_firmware_details_wire_format() -> None:
    pw, transport = _client_for(SYSTEM_INFO_RESPONSE)
    result = await pw.get_firmware_details()
    assert transport.sent == [SYSTEM_INFO_REQUEST]
    assert result == {
        "system": {
            "gateway": {"partNumber": "1707000-00-J", "serialNumber": "TG9999999999XP"},
            "din": DIN,
            "version": {
                "text": "24.12.6-PW3-AFCI 008bf6ff",
                "githash": b"\x00\x8b\xf6\xff",
            },
            "five": 1,
            "six": 4,
            "wireless": {"device": []},
        }
    }


def test_import_with_foreign_tedapi_proto_registered() -> None:
    """pypowerwall registers a bare ``tedapi.proto`` (package ``tedapi``) in the
    default pool. Importing tesla_fleet_api.tesla.powerwall afterwards must not collide with it
    (jasonacox/pypowerwall#408)."""
    script = """
from google.protobuf import descriptor_pb2, descriptor_pool
fdp = descriptor_pb2.FileDescriptorProto(name="tedapi.proto", package="tedapi", syntax="proto3")
msg = fdp.message_type.add(name="MessageEnvelope")
msg.field.add(name="deliveryChannel", number=1, type=5, label=1)
descriptor_pool.Default().AddSerializedFile(fdp.SerializeToString())

import tesla_fleet_api.tesla.powerwall
import tesla_fleet_api.tesla.powerwall.client
import tesla_fleet_api.tesla.powerwall.energysite
print("ok")
"""
    result = subprocess.run(
        [sys.executable, "-c", script], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "ok"
