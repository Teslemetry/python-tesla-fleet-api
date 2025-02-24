from typing import Any
from tesla_fleet_api.const import Method


class User:
    """Class describing the Tesla Fleet API user endpoints"""

    def __init__(self, parent):
        self._request = parent._request

    async def backup_key(self) -> dict[str, Any]:
        """Returns the public key associated with the user."""
        return await self._request(Method.GET, "api/1/users/backup_key")

    async def feature_config(self) -> dict[str, Any]:
        """Returns any custom feature flag applied to a user."""
        return await self._request(Method.GET, "api/1/users/feature_config")

    async def me(self) -> dict[str, Any]:
        """Returns a summary of a user's account."""
        return await self._request(Method.GET, "api/1/users/me")

    async def orders(self) -> dict[str, Any]:
        """Returns the active orders for a user."""
        return await self._request(Method.GET, "api/1/users/orders")

    async def region(self) -> dict[str, Any]:
        """Returns a user's region and appropriate fleet-api base URL. Accepts no parameters, response is based on the authentication token subject."""
        return await self._request(Method.GET, "api/1/users/region")
