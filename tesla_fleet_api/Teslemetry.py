import aiohttp
from .TeslaFleetApi import TeslaFleetApi
from .const import Methods


class Teslemetry(TeslaFleetApi):
    def __init__(
        self,
        session: aiohttp.ClientSession,
        access_token: str,
        raise_for_status: bool = False,
    ):
        """Initialize the Teslemetry API."""
        super().__init__(
            session,
            access_token,
            use_command_protocol=False,
            server="https://teslemetry.com",
            raise_for_status=raise_for_status,
        )

    async def vehicles(self):
        """Get the subscribed vehicles."""
        return await self._request(
            Methods.GET,
            "/meta/vehicles",
        )

    async def find_server(self):
        """Find the server URL for the Tesla Fleet API."""
        raise NotImplementedError("Do not use this function for Teslemetry.")

    def stream(self, vin: str, fields, alerts, expire: int):
        """Stream data from the Tesla Fleet API."""
        raise NotImplementedError("Not implemented yet")

    class Vehicle(TeslaFleetApi.Vehicle):
        """Tesla Fleet API Vehicle."""

        async def create(
            self, only_subscribed=True
        ) -> [TeslaFleetApi.Vehicle.Specific]:
            """Creates a class for each vehicle."""
            if only_subscribed:
                return [
                    self.Specific(self, vin) for vin in await self._parent.vehicles()
                ]
            return await super().create()
