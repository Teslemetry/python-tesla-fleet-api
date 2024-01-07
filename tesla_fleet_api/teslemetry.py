import aiohttp
from .teslafleetapi import TeslaFleetApi
from .vehicle import Vehicle
from .vehiclespecific import VehicleSpecific
from .const import Methods


class TeslemetryVehicle(Vehicle):
    """Tesla Fleet API Vehicle."""

    async def create(self, only_subscribed=True) -> [VehicleSpecific]:
        """Creates a class for each vehicle."""
        if only_subscribed:
            return [VehicleSpecific(self, vin) for vin in await self._parent.vehicles()]
        return await super().create()


class Teslemetry(TeslaFleetApi):
    def __init__(
        self,
        session: aiohttp.ClientSession,
        access_token: str,
        raise_for_status: bool = True,
    ):
        """Initialize the Teslemetry API."""
        super().__init__(
            session,
            access_token,
            use_command_protocol=False,
            server="https://teslemetry.com",
            raise_for_status=raise_for_status,
            partner_scope=False,
            user_scope=False,
            vehicle_scope=False,
        )
        self.vehicle = TeslemetryVehicle(self)

    async def vehicles(self):
        """Get the subscribed vehicles."""
        return await self._request(
            Methods.GET,
            "/meta/vehicles",
        )

    async def find_server(self):
        """Find the server URL for the Tesla Fleet API."""
        raise NotImplementedError("Do not use this function for Teslemetry.")
