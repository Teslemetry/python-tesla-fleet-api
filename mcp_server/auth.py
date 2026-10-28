"""SDK-backed OAuth with serialized refresh and durable token rotation."""

import asyncio
import getpass
import secrets
import time
from urllib.parse import parse_qs, urlsplit

import aiohttp

from mcp_server.config import Config
from mcp_server.storage import Store
from tesla_fleet_api.tesla.oauth import TeslaFleetOAuth


class ManagedOAuth(TeslaFleetOAuth):
    _transport_name = "fleet"

    def __init__(self, session: aiohttp.ClientSession, config: Config, store: Store):
        self.store = store
        self.config = config
        saved = store.read("tokens.json")
        if saved and (
            saved.get("region") != config.region
            or saved.get("client_id") != config.client_id
        ):
            raise ValueError("Stored tokens belong to another region/application")
        super().__init__(
            session,
            config.region,
            config.client_id,
            config.client_secret or None,
            config.redirect_uri or None,
            saved.get("access_token"),
            saved.get("refresh_token"),
            saved.get("expires", 0),
        )
        self._refresh_lock = asyncio.Lock()
        self._persistence_failed = False

    def save(self) -> None:
        try:
            if (
                not self.refresh_token
                or not isinstance(self._access_token, str)
                or not self._access_token
            ):
                raise ValueError("Incomplete credentials")
            self.store.write(
                "tokens.json",
                {
                    "region": self.region,
                    "client_id": self.client_id,
                    "access_token": self._access_token,
                    "refresh_token": self.refresh_token,
                    "expires": self.expires,
                },
            )
        except Exception:
            self._persistence_failed = True
            raise RuntimeError(
                "Token persistence failed; stop service and recover credentials"
            ) from None

    async def check_access_token(self) -> dict[str, object] | None:
        async with self._refresh_lock:
            if self._persistence_failed:
                raise RuntimeError("Token persistence failed; restart after recovery")
            if not self._access_token or self.expires <= time.time() + 60:
                await super().refresh_access_token()
                self.save()
            return None

    async def access_token(self) -> str:
        await self.check_access_token()
        if not isinstance(self._access_token, str) or not self._access_token:
            raise ValueError("Access token missing; run login")
        return self._access_token


async def login(config: Config, store: Store) -> None:
    if not config.client_secret or not config.redirect_uri:
        raise ValueError("Login requires TESLA_CLIENT_SECRET and TESLA_REDIRECT_URI")
    async with aiohttp.ClientSession(
        timeout=aiohttp.ClientTimeout(total=30)
    ) as session:
        api = ManagedOAuth(session, config, store)
        state = secrets.token_urlsafe(32)
        started = time.monotonic()
        print(
            "Open this Tesla authorization URL in your browser:\n"
            + api.get_login_url(config.scopes, state)
        )
        # Local operator input only. Never expose code/token exchange as an MCP tool.
        callback = await asyncio.to_thread(
            getpass.getpass, "Paste the complete callback URL (hidden): "
        )
        actual, expected = urlsplit(callback), urlsplit(config.redirect_uri)
        query = parse_qs(actual.query)
        if (actual.scheme, actual.netloc, actual.path) != (
            expected.scheme,
            expected.netloc,
            expected.path,
        ) or actual.fragment:
            raise ValueError("Callback URL does not match registered redirect")
        states, codes = query.get("state", []), query.get("code", [])
        if (
            time.monotonic() - started > 600
            or len(states) != 1
            or not secrets.compare_digest(states[0], state)
        ):
            raise ValueError("OAuth state invalid or expired")
        if "error" in query or len(codes) != 1 or not codes[0]:
            raise ValueError("OAuth authorization was not granted")
        await api.get_refresh_token(codes[0])
        api.save()
        print("Credentials saved locally with owner-only permissions.")
