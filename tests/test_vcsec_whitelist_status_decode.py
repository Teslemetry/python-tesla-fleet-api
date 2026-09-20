"""``Commands._command()`` must decode ``whitelistOperationStatus`` on a VCSEC
reply, not just ``operationStatus`` - a ``WhitelistOperation`` the vehicle
rejects still replies with ``OPERATIONSTATUS_OK`` at the outer level.
"""

from __future__ import annotations

from tesla_fleet_api.exceptions import WhitelistOperationNoPermissionToAdd
from tesla_protocol.command.universal_message_pb2 import (
    Destination,
    Domain,
    RoutableMessage,
)
from tesla_protocol.command.vcsec_pb2 import (
    CommandStatus,
    FromVCSECMessage,
    OperationStatus_E,
    WHITELISTOPERATION_INFORMATION_NO_PERMISSION_TO_ADD,
    WhitelistOperation_status,
)

from ble_mocked_transport import MockedBleTransportTestCase


def whitelist_op_reply(info: int) -> RoutableMessage:
    """A VCSEC reply to a ``WhitelistOperation``: outer status OK, op status in ``info``."""
    body = FromVCSECMessage(
        commandStatus=CommandStatus(
            operationStatus=OperationStatus_E.OPERATIONSTATUS_OK,
            whitelistOperationStatus=WhitelistOperation_status(
                whitelistOperationInformation=info
            ),
        )
    )
    return RoutableMessage(
        from_destination=Destination(domain=Domain.DOMAIN_VEHICLE_SECURITY),
        protobuf_message_as_bytes=body.SerializeToString(),
    )


class VcsecWhitelistStatusDecodeTest(MockedBleTransportTestCase):
    async def test_rejected_whitelist_operation_raises(self) -> None:
        """A vehicle-rejected key add must raise, not report ``result: True``."""
        vehicle, send = self.make_vehicle()
        send.return_value = whitelist_op_reply(
            WHITELISTOPERATION_INFORMATION_NO_PERMISSION_TO_ADD
        )

        with self.assertRaises(WhitelistOperationNoPermissionToAdd):
            await vehicle._command(
                Domain.DOMAIN_VEHICLE_SECURITY,
                b"",
                expects_data=False,
            )

    async def test_accepted_whitelist_operation_succeeds(self) -> None:
        """A zero/absent whitelist status leaves the existing success path intact."""
        vehicle, send = self.make_vehicle()
        send.return_value = whitelist_op_reply(0)

        result = await vehicle._command(
            Domain.DOMAIN_VEHICLE_SECURITY,
            b"",
            expects_data=False,
        )

        self.assertEqual(result, {"response": {"result": True, "reason": ""}})
