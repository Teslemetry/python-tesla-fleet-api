from typing import Any
import aiohttp
import time

from tesla_fleet_api.const import Method
from .teslafleetapi import TeslaFleetApi
from .const import Scope, SERVERS


class TeslaFleetOAuth(TeslaFleetApi):
    """Tesla Fleet OAuth API."""

    expires: int

    def __init__(
        self,
        session: aiohttp.ClientSession,
        client_id: str,
        access_token: str | None = None,
        refresh_token: str | None = None,
        expires: int = 0,
        region: str | None = None,
        server: str | None = None,
        raise_for_status: bool = True,
    ):
        self.client_id = client_id
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.expires = expires

        super().__init__(
            session,
            access_token="",
            region=region,
            server=server,
            raise_for_status=raise_for_status,
        )

    def get_login_url(
        self, redirect_uri: str, scopes: list[Scope], state: str = "login"
    ) -> str:
        """Get the login URL."""
        return f"https://auth.tesla.com/oauth2/v3/authorize?response_type=code&client_id={self.client_id}&redirect_uri={redirect_uri}&scope={' '.join(scopes)}&state={state}"

    async def get_refresh_token(
        self, client_secret: str, code: str, redirect_uri: str
    ) -> None:
        """Get the refresh token."""
        async with self.session.post(
            "https://auth.tesla.com/oauth2/v3/token",
            data={
                "grant_type": "authorization_code",
                "client_id": self.client_id,
                "client_secret": client_secret,
                "code": code,
                "audience": self.server,
                "redirect_uri": redirect_uri,
            },
        ) as resp:
            if resp.ok:
                data = await resp.json()
                self.refresh_token = data["refresh_token"]
                self.access_token = data["access_token"]
                self.expires = int(time.time()) + data["expires_in"]
                region = code.split("_")[0].lower()
                self.server = SERVERS.get(region)

    async def check_access_token(self) -> dict[str, Any] | None:
        """Get the access token."""
        if self.access_token and self.expires > time.time():
            return None
        return await self.refresh_access_token()

    async def refresh_access_token(self) -> dict[str, Any]:
        """Refresh the access token."""
        if not self.refresh_token:
            raise ValueError("Refresh token is missing")
        async with self.session.post(
            "https://auth.tesla.com/oauth2/v3/token",
            data={
                "grant_type": "refresh_token",
                "client_id": self.client_id,
                "refresh_token": self.refresh_token,
            },
        ) as resp:
            data = await resp.json()
            if resp.ok:
                self.access_token = data["access_token"]
                self.refresh_token = data["refresh_token"]
                self.expires = int(time.time()) + data["expires_in"]
                return {"refresh_token": self.refresh_token, "expires": self.expires}
            raise ValueError(data)

    async def _request(
        self,
        method: Method,
        path: str,
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
    ) -> str | dict[str, Any]:
        """Send a request to the Tesla Fleet API."""
        await self.check_access_token()
        return await super()._request(method, path, params, data)
