import aiohttp
from .exceptions import RaiseForStatus


# Based on https://developer.tesla.com/docs/fleet-api
class TeslaFleetApi:
    """Class describing the Tesla Fleet API."""

    server: str
    session: aiohttp.ClientSession
    headers: dict[str, str]
    raise_for_status: bool

    def __init__(
        self,
        access_token: str,
        server: str,
        session: aiohttp.ClientSession | None = None,
        raise_for_status: bool = True,
    ):
        """Initialize the Tesla Fleet API."""
        self.server = server
        self.session = session or aiohttp.ClientSession()
        self.headers = {"Authorization": f"Bearer {access_token}"}
        self.raise_for_status = raise_for_status

    async def _get(self, path):
        """Get data from the Tesla Fleet API."""

        async with self.session.get(
            f"{self.server}/{path}",
            headers=self.headers,
        ) as resp:
            if self.raise_for_status:
                RaiseForStatus(resp)
            return await resp.json()

    async def _post(self, path, data: dict):
        """Post data to the Tesla Fleet API with URL encoded data."""

        async with self.session.post(
            f"{self.server}/{path}",
            headers=self.headers,
            data=data,
        ) as resp:
            if self.raise_for_status:
                RaiseForStatus(resp)
            return await resp.json()

    def get_vehicle_list(self):
        pass

    def get_vehicle(self, vehicle_id):
        pass

    def get_vehicle_data(self, vehicle_id):
        pass

    def get_vehicle_state(self, vehicle_id):
        pass

    def get_vehicle_config(self, vehicle_id):
        pass

    def get_vehicle_drive_state(self, vehicle_id):
        pass

    def get_vehicle_gui_settings(self, vehicle_id):
        pass

    def get_vehicle_climate_state(self, vehicle_id):
        pass

    def get_vehicle_charge_state(self, vehicle_id):
        pass

    def get_vehicle_nearby_charging_sites(self, vehicle_id):
        pass

    def get_vehicle_service_data(self, vehicle_id):
        pass

    def get_vehicle_mobile_enabled(self, vehicle_id):
        pass

    def get_vehicle_mobile_access(self, vehicle_id):
        pass

    def get_vehicle_state(self, vehicle_id):
        pass

    def get_vehicle_config(self, vehicle_id):
        pass

    def get_vehicle_drive_state(self, vehicle_id):
        pass

    def get_vehicle_gui_settings(self, vehicle_id):
        pass

    def get_vehicle_climate_state(self, vehicle_id):
        pass

    def get_vehicle_charge_state(self, vehicle_id):
        pass

    def get_vehicle_nearby_charging_sites(self, vehicle_id):
        pass

    def get_vehicle_service_data(self, vehicle_id):
        pass

    def get_vehicle_mobile_enabled(self, vehicle_id):
        pass

    def get_vehicle_mobile_access(self, vehicle_id):
        pass

    def get_vehicle_state(self, vehicle_id):
        pass

    def get_vehicle_config(self, vehicle_id):
        pass

    def get_vehicle_drive_state(self, vehicle_id):
        pass

    def get_vehicle_gui_settings(self, vehicle_id):
        pass

    def get_vehicle_climate_state(self, vehicle_id):
        pass

    def get_vehicle_charge_state(self, vehicle_id):
        pass

    def get_vehicle_nearby_charging_sites(self, vehicle_id):
        pass

    def get_vehicle_service_data(self, vehicle_id):
        pass

    def get_vehicle_mobile_enabled(self, vehicle_id):
        pass

    def get_vehicle_mobile_access(self, vehicle_id):
        pass

    def get_vehicle_state(self, vehicle_id):
        pass
