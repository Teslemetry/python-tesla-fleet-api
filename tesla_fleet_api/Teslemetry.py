import aiohttp
from .TeslaFleetApi import TeslaFleetApi


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

    async def subscriptions(self):
        """Get the subscriptions."""
        raise NotImplementedError("Not implemented yet")
        return await self.get(
            "/meta/subscriptions",
            {"headers": {"Authorization": f"Bearer {self.access_token}"}},
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
            self, only_subscribed=False
        ) -> [TeslaFleetApi.Vehicle.Specific]:
            """Creates a class for each vehicle."""
            list = await self.list()
            return [self.Specific(self, x["vin"]) for x in list["response"]]
