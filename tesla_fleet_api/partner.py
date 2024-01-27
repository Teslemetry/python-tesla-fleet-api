from typing import Any
from .const import Methods


class Partner:
    """Class describing the Tesla Fleet API partner endpoints"""

    def __init__(self, parent):
        self._request = parent._request

    async def public_key(self, domain: str | None = None) -> dict[str, Any]:
        """Returns the public key associated with a domain. It can be used to ensure the registration was successful."""
        return await self._request(
            Methods.GET, "api/1/partner_accounts/public_key", {"domain": domain}
        )

    async def register(self, domain: str) -> dict[str, Any]:
        """Registers an existing account before it can be used for general API access. Each application from developer.tesla.com must complete this step."""
        return await self._request(
            Methods.POST, "api/1/partner_accounts", json={"domain": domain}
        )
