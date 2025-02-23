from __future__ import annotations

import base64
from typing import TYPE_CHECKING

from .fleet import VehicleFleet
from .commands import Commands

from ...exceptions import (
    MESSAGE_FAULTS,
)
from .proto.signatures_pb2 import (
    SessionInfo,
)
from .proto.universal_message_pb2 import (
    RoutableMessage,
)

if TYPE_CHECKING:
    from ..fleet import TeslaFleetApi


class VehicleSigned(VehicleFleet, Commands):
    """Class describing the Tesla Fleet API vehicle endpoints and commands for a specific vehicle with command signing."""


    _auth_method = "hmac"

    def __init__(self, parent: TeslaFleetApi, vin: str):
        """Initialize the VehicleSigned class."""
        super().__init__(parent, vin)
        super(Commands, self).__init__(parent, vin)


    async def _send(self, msg: RoutableMessage) -> RoutableMessage:
        """Serialize a message and send to the signed command endpoint."""

        async with self._sessions[msg.to_destination.domain].lock:
            resp = await self.signed_command(
                base64.b64encode(msg.SerializeToString()).decode()
            )

            resp_msg = RoutableMessage.FromString(base64.b64decode(resp["response"]))

            # Check UUID?
            # Check RoutingAdress?

            if resp_msg.session_info:
                self._sessions[resp_msg.from_destination.domain].update(
                    SessionInfo.FromString(resp_msg.session_info), self.private_key
                )

            if resp_msg.signedMessageStatus.signed_message_fault:
                raise MESSAGE_FAULTS[resp_msg.signedMessageStatus.signed_message_fault]

            return resp_msg
