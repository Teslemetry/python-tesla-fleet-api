from __future__ import annotations

import base64
from typing import TYPE_CHECKING

from tesla_fleet_api.tesla.vehicle.fleet import VehicleFleet
from tesla_fleet_api.tesla.vehicle.commands import Commands
from tesla_fleet_api.tesla.vehicle.proto.universal_message_pb2 import (
    RoutableMessage,
)

if TYPE_CHECKING:
    from tesla_fleet_api.tesla.fleet import TeslaFleetApi


class VehicleSigned(VehicleFleet, Commands):
    """Class describing the Tesla Fleet API vehicle endpoints and commands for a specific vehicle with command signing."""


    _auth_method = "hmac"

    def __init__(self, parent: TeslaFleetApi, vin: str):
        """Initialize the VehicleSigned class."""
        super().__init__(parent, vin)
        super(Commands, self).__init__(parent, vin)


    async def _send(self, msg: RoutableMessage, requires: str) -> RoutableMessage:
        """Serialize a message and send to the signed command endpoint."""
        # requires isnt used because Fleet API messages are singular

        async with self._sessions[msg.to_destination.domain].lock:
            json = await self.signed_command(
                base64.b64encode(msg.SerializeToString()).decode()
            )
            resp = RoutableMessage.FromString(base64.b64decode(json["response"]))
            self.validate_msg(resp)
            return resp
