"""CN OAuth regressions; offline mocked responses, never real credentials."""

from contextlib import asynccontextmanager
from unittest import IsolatedAsyncioTestCase
from unittest.mock import MagicMock
from urllib.parse import parse_qs, urlsplit
import time

from tesla_fleet_api.const import SERVERS, Scope
from tesla_fleet_api.tesla.oauth import TeslaFleetOAuth


class CNOAuthTests(IsolatedAsyncioTestCase):
    def api(self, ok=True, response=None):
        self.sent = []

        @asynccontextmanager
        async def post(url, **kwargs):
            self.sent.append((url, kwargs))
            resp = MagicMock(ok=ok)

            async def json():
                return response or {
                    "access_token": "new",
                    "refresh_token": "rotated",
                    "expires_in": 3600,
                }

            resp.json = json
            yield resp

        session = MagicMock()
        session.post = post
        return TeslaFleetOAuth(
            session,
            "cn",
            "id&name",
            "secret",
            "https://example.com/cb?a=1&b=2",
            "initial",
            "refresh",
            int(time.time()) + 3600,
        )

    async def test_initial_access_token_survives_super_init(self):
        api = self.api()
        self.assertEqual(await api.access_token(), "initial")
        self.assertFalse(self.sent)

    async def test_authorize_parameters_are_encoded(self):
        url = urlsplit(
            self.api().get_login_url([Scope.OPENID, Scope.OFFLINE_ACCESS], "a&=+中")
        )
        self.assertEqual(url.hostname, "auth.tesla.cn")
        query = parse_qs(url.query)
        self.assertEqual(query["state"], ["a&=+中"])
        self.assertEqual(query["client_id"], ["id&name"])
        self.assertEqual(query["redirect_uri"], ["https://example.com/cb?a=1&b=2"])
        self.assertEqual(query["scope"], ["openid offline_access"])

    async def test_exchange_keeps_explicit_region_not_untrusted_code_prefix(self):
        api = self.api()
        await api.get_refresh_token("EU_untrusted")
        self.assertEqual(api.server, SERVERS["cn"])
        self.assertEqual(self.sent[0][1]["data"]["audience"], SERVERS["cn"])
        self.assertEqual(await api.access_token(), "new")

    async def test_exchange_and_refresh_failure_do_not_leak_response(self):
        api = self.api(ok=False, response={"error": "secret-response"})
        for action in (lambda: api.get_refresh_token("code"), api.refresh_access_token):
            with self.assertRaises(ValueError) as result:
                await action()
            self.assertNotIn("secret-response", str(result.exception))
        self.assertEqual(await api.access_token(), "initial")

    async def test_invalid_success_does_not_partially_replace_tokens(self):
        for data in (
            {"access_token": "new", "refresh_token": "rotated", "expires_in": -1},
            {"access_token": "new", "expires_in": 3600},
            {"access_token": "", "refresh_token": "rotated", "expires_in": 3600},
        ):
            api = self.api(response=data)
            with self.assertRaises(ValueError):
                await api.refresh_access_token()
            self.assertEqual(api.refresh_token, "refresh")
            self.assertEqual(await api.access_token(), "initial")
