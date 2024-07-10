import aiohttp
import time
import secrets
import hashlib
import base64

from .teslafleetoauth import TeslaFleetOAuth
from .const import Scope, SERVERS


class TeslaFleetOpenSource(TeslaFleetOAuth):
    """Tesla Fleet Open Source OAuth API."""

    code_verifier: str
    code_challenge: str

    def __init__(
        self,
        session: aiohttp.ClientSession,
        client_id: str,
        redirect_uri: str,
    ):
        self.code_verifier = secrets.token_urlsafe(32)

        # Hash the code_verifier using SHA-256
        hashed_verifier = hashlib.sha256(self.code_verifier.encode()).digest()
        # Encode the hash using URL-safe Base64 encoding, without padding
        self.code_challenge = (
            base64.urlsafe_b64encode(hashed_verifier).decode().replace("=", "")
        )

        super().__init__(session, client_id, redirect_uri=redirect_uri)

    def get_login_url(self, scopes: list[Scope], state: str = "login") -> str:
        """Get the login URL without a client secret."""

        return (
            super().get_login_url(scopes, state)
            + f"&code_challenge={self.code_challenge}"
        )

    async def get_refresh_token(self, code: str) -> None:
        """Get the refresh token."""
        async with self.session.post(
            "https://auth.tesla.com/oauth2/v3/token",
            data={
                "grant_type": "authorization_code",
                "client_id": self.client_id,
                "code": code,
                "audience": self.server,
                "redirect_uri": self.redirect_uri,
                "code_verifier": self.code_verifier,
            },
        ) as resp:
            if resp.ok:
                data = await resp.json()
                self.refresh_token = data["refresh_token"]
                self.access_token = data["access_token"]
                self.expires = int(time.time()) + data["expires_in"]
                region = code.split("_")[0].lower()
                self.server = SERVERS.get(region)
