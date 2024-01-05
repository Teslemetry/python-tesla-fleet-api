import aiohttp
import datetime
from .TeslaFleetApi import TeslaFleetApi


class TeslaFleetOAuth(TeslaFleetApi):
    """Tesla Fleet OAuth API."""

    expires: datetime

    def __init__(
        self,
        session: aiohttp.ClientSession,
        client_id: str,
        refresh_token: str,
        region: str | None = None,
        server: str | None = None,
        raise_for_status: bool = True,
    ):
        raise NotImplementedError("This is not implemented yet")
        self.client_id = client_id
        self.refresh_token = refresh_token
        self.expires = datetime.now()

        super().__init__(
            session,
            access_token="",
            region=region,
            server=server,
            raise_for_status=raise_for_status,
        )

    async def check_access_token(self) -> None:
        """Get the access token."""
        if self.expires > datetime.now():
            return
        await self.refresh_access_token()

    async def refresh_access_token(self) -> str:
        if not self.refresh_token:
            raise ValueError("Refresh token is missing")
        with self.session.post(
            "https://auth.tesla.com/oauth2/v3/token",
            data={
                "grant_type": "refresh_token",
                "client_id": self.client_id,
                "refresh_token": self.refresh_token,
            },
        ) as resp:
            data = await resp.json()
            self.access_token = data["access_token"]
            self.expires = datetime.now() + datetime.timedelta(
                seconds=data["expires_in"]
            )

    async def get_refresh_token(self, client_secret: str, code: str):
        """Get the refresh token."""
        data = {
            "grant_type": "authorization_code",
            "client_id": self.client_id,
            "code": code,
            "audience": self.region,
        }

        self.session.post(
            "https://auth.tesla.com/oauth2/v3/token",
        )
