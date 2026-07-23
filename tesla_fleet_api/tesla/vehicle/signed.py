from __future__ import annotations

import base64
from typing import TYPE_CHECKING, Any, Callable, Generic, TypeVar

from tesla_fleet_api.tesla.vehicle.fleet import VehicleFleet
from tesla_fleet_api.tesla.vehicle.commands import Commands
from tesla_protocol.command.universal_message_pb2 import (
    RoutableMessage,
)

if TYPE_CHECKING:
    from tesla_fleet_api.tesla.fleet import TeslaFleetApi

SignedParentT = TypeVar("SignedParentT", bound="TeslaFleetApi")


class VehicleSigned(  # pyright: ignore[reportIncompatibleMethodOverride]
    Commands[SignedParentT], VehicleFleet[SignedParentT], Generic[SignedParentT]
):
    """Class describing the Tesla Fleet API vehicle endpoints and commands for a specific vehicle with command signing."""

    _auth_method = "hmac"
    _transport_name = "fleet"

    def __init__(self, parent: SignedParentT, vin: str):
        """Initialize the VehicleSigned class."""
        super().__init__(parent, vin)
        super(Commands, self).__init__(parent, vin)

    async def _send(
        self,
        msg: RoutableMessage,
        requires: str,
        expects_data: bool = True,
        *,
        confirm_broadcast: Callable[[Any], bool] | None = None,
    ) -> RoutableMessage:
        """Serialize a message and send to the signed command endpoint."""
        # requires, expects_data, and confirm_broadcast are unused: Fleet API
        # replies are singular, delivered whole in one response with no
        # separate terminal ack frame and no broadcast side channel.

        async with self._sessions[msg.to_destination.domain].lock:
            json = await self.signed_command(
                base64.b64encode(msg.SerializeToString()).decode()
            )
            resp = RoutableMessage.FromString(base64.b64decode(json["response"]))
            self.validate_msg(resp, msg.uuid)
            return resp
