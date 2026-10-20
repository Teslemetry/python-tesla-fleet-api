"""The OAuth token endpoint follows the region, like the authorize URL."""

from contextlib import asynccontextmanager
from unittest import IsolatedAsyncioTestCase
from unittest.mock import MagicMock

from tesla_fleet_api.const import Region
from tesla_fleet_api.tesla.fleet import TeslaFleetApi
from tesla_fleet_api.tesla.oauth import TeslaFleetOAuth

GLOBAL = "https://fleet-auth.prd.vn.cloud.tesla.com/oauth2/v3/token"
CN = "https://auth.tesla.cn/oauth2/v3/token"


def _session(urls: list[str]) -> MagicMock:
    resp = MagicMock()
    resp.ok = True

    async def _json() -> dict[str, object]:
        return {"access_token": "a", "refresh_token": "r", "expires_in": 60}

    resp.json = _json

    @asynccontextmanager
    async def _ctx(url: str, **kwargs: object):
        urls.append(url)
        yield resp

    session = MagicMock()
    session.post = MagicMock(side_effect=_ctx)
    return session


class TestTokenHost(IsolatedAsyncioTestCase):
    async def test_code_exchange_and_refresh(self) -> None:
        for region, expected in (("na", GLOBAL), ("eu", GLOBAL), ("cn", CN)):
            urls: list[str] = []
            api = TeslaFleetOAuth(
                _session(urls),
                region,  # type: ignore[arg-type]
                "id",
                client_secret="secret",
                redirect_uri="https://example.com/cb",
            )
            await api.get_refresh_token("code")
            await api.refresh_access_token()
            self.assertEqual(urls, [expected, expected], region)

    async def test_partner_login(self) -> None:
        for region, expected in (("na", GLOBAL), ("cn", CN)):
            urls: list[str] = []
            region_: Region = region  # type: ignore[assignment]
            api = TeslaFleetApi(_session(urls), access_token="t", region=region_)
            await api.partner_login("id", "secret")
            self.assertEqual(urls, [expected], region)
