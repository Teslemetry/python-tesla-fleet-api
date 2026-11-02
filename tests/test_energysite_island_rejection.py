"""A cloud island-mode request the gateway refuses must raise, not return.

The gateway answers a refused ``set_island_mode_request`` with an ordinary
``set_island_mode_response`` whose ``result`` is a ``REJECTED_*`` value. The
local Powerwall client already raises on those codes. Through the cloud the
same refusal came back as a normal reply. The signed path carries the result
in the reply envelope, and Teslemetry's keyless route answers the decoded
``{"response": {"result": ...}}``. The contactor commands also accept only
``ON_GRID`` (1) and ``OFF_GRID`` (6), checked before any request.
"""

from __future__ import annotations

import base64
from typing import Any
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock

from cryptography.hazmat.primitives.asymmetric import rsa
from tesla_protocol.energy_device import teg_api_pb2, transport_pb2

from tesla_fleet_api.const import EnergyIslandMode
from tesla_fleet_api.exceptions import DeviceUnexpectedResponse
from tesla_fleet_api.tesla.energysite import EnergySite
from tesla_fleet_api.teslemetry.energysite import TeslemetryEnergySite

SITE_ID = 12345
DIN = "1232100-00-E--TG123456789ABC"

# A test key only; it is not registered on any gateway.
TEST_KEY = rsa.generate_private_key(public_exponent=65537, key_size=2048)

REJECTIONS = (
    teg_api_pb2.TEG_SET_ISLAND_MODE_RESULT_REJECTED_NOT_READY_FOR_ISLANDING,
    teg_api_pb2.TEG_SET_ISLAND_MODE_RESULT_REJECTED_LOAD_DROP_EXPECTED,
    teg_api_pb2.TEG_SET_ISLAND_MODE_RESULT_REJECTED_LOW_ENERGY,
    teg_api_pb2.TEG_SET_ISLAND_MODE_RESULT_REJECTED_EXCESSIVE_SOLAR,
)

CALLS: tuple[tuple[str, tuple[Any, ...]], ...] = (
    ("set_island_mode", (EnergyIslandMode.OFF_GRID, True)),
    ("go_off_grid", ()),
    ("reconnect_grid", ()),
)


def _make_site(
    cls: type[EnergySite], signed: bool = True
) -> tuple[EnergySite, AsyncMock]:
    request_mock: AsyncMock = AsyncMock()
    parent = AsyncMock()
    parent._request = request_mock
    if signed:
        return cls(parent, SITE_ID, private_key=TEST_KEY, din=DIN), request_mock
    return cls(parent, SITE_ID), request_mock


def _signed_reply(result: int | None) -> dict[str, Any]:
    envelope = transport_pb2.MessageEnvelope()
    if result is None:
        envelope.teg.set_island_mode_response.SetInParent()
    else:
        envelope.teg.set_island_mode_response.result = result  # pyright: ignore[reportAttributeAccessIssue]
    return {
        "response": {
            "message_envelope_as_bytes": base64.b64encode(
                envelope.SerializeToString()
            ).decode("ascii"),
        }
    }


class SignedIslandRejectionTests(IsolatedAsyncioTestCase):
    async def test_each_rejection_raises(self) -> None:
        for cls in (EnergySite, TeslemetryEnergySite):
            for name, args in CALLS:
                for result in REJECTIONS:
                    with self.subTest(cls=cls.__name__, call=name, result=result):
                        site, request_mock = _make_site(cls)
                        request_mock.return_value = _signed_reply(result)
                        with self.assertRaises(DeviceUnexpectedResponse) as ctx:
                            await getattr(site, name)(*args)
                        self.assertEqual(
                            ctx.exception.data,
                            {
                                "code": result,
                                "message": teg_api_pb2.TEGSetIslandModeResult.Name(
                                    result
                                ),
                            },
                        )

    async def test_other_results_return_the_reply(self) -> None:
        for cls in (EnergySite, TeslemetryEnergySite):
            for result in (
                teg_api_pb2.TEG_SET_ISLAND_MODE_RESULT_ACCEPTED,
                teg_api_pb2.TEG_SET_ISLAND_MODE_RESULT_INVALID,
                99,
                None,
            ):
                with self.subTest(cls=cls.__name__, result=result):
                    site, request_mock = _make_site(cls)
                    reply = _signed_reply(result)
                    request_mock.return_value = reply
                    self.assertIs(await site.go_off_grid(), reply)


class KeylessRouteIslandRejectionTests(IsolatedAsyncioTestCase):
    async def test_rejection_raises(self) -> None:
        low_energy = teg_api_pb2.TEG_SET_ISLAND_MODE_RESULT_REJECTED_LOW_ENERGY
        name = "TEG_SET_ISLAND_MODE_RESULT_REJECTED_LOW_ENERGY"
        for call, args in CALLS:
            for result in (low_energy, name):
                with self.subTest(call=call, result=result):
                    site, request_mock = _make_site(TeslemetryEnergySite, signed=False)
                    request_mock.return_value = {"response": {"result": result}}
                    with self.assertRaises(DeviceUnexpectedResponse) as ctx:
                        await getattr(site, call)(*args)
                    self.assertEqual(
                        ctx.exception.data, {"code": low_energy, "message": name}
                    )

    async def test_other_replies_return_unchanged(self) -> None:
        replies: tuple[dict[str, Any], ...] = (
            {"response": {"result": 1}},
            {"response": {"result": True}},
            {"response": {"result": 99}},
            {"response": {}},
            {"response": None},
            {"response": "ok"},
        )
        for reply in replies:
            with self.subTest(reply=reply):
                site, request_mock = _make_site(TeslemetryEnergySite, signed=False)
                request_mock.return_value = reply
                self.assertIs(await site.reconnect_grid(), reply)


class IslandModeValidationTests(IsolatedAsyncioTestCase):
    async def test_only_on_and_off_grid_are_sent(self) -> None:
        bad_modes: tuple[Any, ...] = (0, 2, 3, 5, 99, -1, "6", "1", None, True, 6.0)
        for cls, signed in (
            (EnergySite, True),
            (TeslemetryEnergySite, True),
            (TeslemetryEnergySite, False),
        ):
            for mode in bad_modes:
                with self.subTest(cls=cls.__name__, signed=signed, mode=mode):
                    site, request_mock = _make_site(cls, signed=signed)
                    with self.assertRaises(ValueError):
                        await site.set_island_mode(mode)
                    request_mock.assert_not_called()

    async def test_force_must_be_a_bool(self) -> None:
        for cls, signed in (
            (EnergySite, True),
            (TeslemetryEnergySite, True),
            (TeslemetryEnergySite, False),
        ):
            for force in ("yes", 1, 0):
                with self.subTest(cls=cls.__name__, signed=signed, force=force):
                    site, request_mock = _make_site(cls, signed=signed)
                    with self.assertRaises(ValueError):
                        await site.set_island_mode(EnergyIslandMode.OFF_GRID, force)  # pyright: ignore[reportArgumentType]
                    request_mock.assert_not_called()

    async def test_plain_ints_one_and_six_are_accepted(self) -> None:
        site, request_mock = _make_site(TeslemetryEnergySite, signed=False)
        request_mock.return_value = {"response": {"result": True}}
        await site.set_island_mode(6, True)
        await site.set_island_mode(1)
        self.assertEqual(request_mock.await_count, 2)
