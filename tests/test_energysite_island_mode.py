"""Tests for EnergySite.set_island_mode/go_off_grid/reconnect_grid.

These cloud-only methods can only send an unsigned ``grpc_command`` -
gateways have been observed acknowledging that request without physically
operating the grid contactor. They must raise
:class:`~tesla_fleet_api.exceptions.SignedCommandRequired` instead of
shipping a silent no-op; the signed local control path
(``add_authorized_client`` + ``EnergySiteRouter``) is unaffected.
"""

from __future__ import annotations

from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock

from tesla_fleet_api.const import EnergyIslandMode
from tesla_fleet_api.exceptions import SignedCommandRequired
from tesla_fleet_api.tesla.energysite import EnergySite


def _make_site() -> tuple[EnergySite, AsyncMock]:
    request_mock: AsyncMock = AsyncMock()
    parent = AsyncMock()
    parent._request = request_mock
    site = EnergySite(parent, 12345)
    return site, request_mock


class IslandModeCloudNoOpTests(IsolatedAsyncioTestCase):
    async def test_set_island_mode_raises(self) -> None:
        site, request_mock = _make_site()
        with self.assertRaises(SignedCommandRequired):
            await site.set_island_mode(EnergyIslandMode.OFF_GRID)
        request_mock.assert_not_called()

    async def test_go_off_grid_raises(self) -> None:
        site, request_mock = _make_site()
        with self.assertRaises(SignedCommandRequired):
            await site.go_off_grid()
        request_mock.assert_not_called()

    async def test_reconnect_grid_raises(self) -> None:
        site, request_mock = _make_site()
        with self.assertRaises(SignedCommandRequired):
            await site.reconnect_grid()
        request_mock.assert_not_called()
