import time
from collections.abc import Awaitable, Callable
from typing import Any
from urllib.parse import urlencode

import aiohttp

from tesla_fleet_api.const import (
    SERVERS,
    TOKEN_URLS,
    Method,
    Region,
    Scope,
    is_valid_region,
)
from tesla_fleet_api.tesla import TeslaFleetApi


class TeslaFleetOAuth(TeslaFleetApi):
    """Tesla Fleet OAuth API."""

    expires: int
    refresh_token: str | None
    redirect_uri: str | None
    _client_secret: str | None
    _access_token: str | Callable[[], Awaitable[str | None]] | None

    def __init__(
        self,
        session: aiohttp.ClientSession,
        region: Region,
        client_id: str,
        client_secret: str | None = None,
        redirect_uri: str | None = None,
        access_token: str | None = None,
        refresh_token: str | None = None,
        expires: int = 0,
    ) -> None:
        if not is_valid_region(region):
            raise ValueError("Invalid region")

        self.client_id = client_id
        self._client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.refresh_token = refresh_token
        self.expires = expires

        super().__init__(
            session,
            access_token=access_token,
            region=region,
        )

    def get_login_url(self, scopes: list[Scope], state: str = "login") -> str:
        """Get the login URL."""
        if self.redirect_uri is None:
            raise ValueError("Redirect URI is missing")
        if self.region == "cn":
            domain = "auth.tesla.cn"
        else:
            domain = "auth.tesla.com"

        query = urlencode(
            {
                "response_type": "code",
                "client_id": self.client_id,
                "redirect_uri": self.redirect_uri,
                "scope": " ".join(scopes),
                "state": state,
            }
        )
        return f"https://{domain}/oauth2/v3/authorize?{query}"

    async def get_refresh_token(self, code: str) -> None:
        """Get the refresh token."""

        if self._client_secret is None:
            raise ValueError("Client secret is missing")

        if self.redirect_uri is None:
            raise ValueError("Redirect URI is missing")

        if self.server is None and self.region is not None:
            self.server = SERVERS.get(self.region)

        async with self.session.post(
            TOKEN_URLS.get(self.region or "na", TOKEN_URLS["na"]),
            data={
                "grant_type": "authorization_code",
                "client_id": self.client_id,
                "client_secret": self._client_secret,
                "code": code,
                "audience": self.server,
                "redirect_uri": self.redirect_uri,
            },
        ) as resp:
            if not resp.ok:
                raise ValueError("OAuth code exchange failed")
            data = await resp.json()
            self._update_tokens(data)

    def _update_tokens(
        self, data: dict[str, Any], *, require_refresh: bool = False
    ) -> None:
        """Validate a success response before replacing any existing credentials."""
        access = data.get("access_token")
        refresh = data.get("refresh_token")
        lifetime = data.get("expires_in")
        if (
            not isinstance(access, str)
            or not access
            or not isinstance(lifetime, int)
            or isinstance(lifetime, bool)
            or lifetime <= 0
            or (refresh is not None and (not isinstance(refresh, str) or not refresh))
            or (require_refresh and not refresh)
        ):
            raise ValueError("Invalid OAuth token response")
        self._access_token = access
        self.refresh_token = refresh
        self.expires = int(time.time()) + lifetime

    async def access_token(self) -> str:
        """Get the access token."""
        if self.expires < time.time():
            await self.refresh_access_token()
        if self._access_token and not callable(self._access_token):
            return self._access_token
        raise ValueError("Access token is missing")

    async def check_access_token(self) -> dict[str, Any] | None:
        """Get the access token."""
        if self._access_token and self.expires > time.time():
            return None
        return await self.refresh_access_token()

    async def refresh_access_token(self) -> dict[str, Any]:
        """Refresh the access token."""
        if not self.refresh_token:
            raise ValueError("Refresh token is missing")
        async with self.session.post(
            TOKEN_URLS.get(self.region or "na", TOKEN_URLS["na"]),
            data={
                "grant_type": "refresh_token",
                "client_id": self.client_id,
                "refresh_token": self.refresh_token,
            },
        ) as resp:
            data = await resp.json()
            if resp.ok:
                self._update_tokens(data, require_refresh=True)
                return {"refresh_token": self.refresh_token, "expires": self.expires}
            raise ValueError("OAuth token refresh failed")

    async def _request(
        self,
        method: Method,
        path: str,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Send a request to the Tesla Fleet API."""
        await self.check_access_token()
        return await super()._request(method, path, params, json)
