"""A VCSEC ``OPERATIONSTATUS_ERROR`` reply must never resolve as success,
whichever inner ``commandStatus`` sub-message (if any) accompanies it.
"""

from __future__ import annotations

from tesla_fleet_api.exceptions import (
    SignedMessageInformationFaultNotOnWhitelist,
    WhitelistOperationNoPermissionToAdd,
)
from tesla_protocol.command.universal_message_pb2 import (
    Destination,
    Domain,
    RoutableMessage,
)
from tesla_protocol.command.vcsec_pb2 import (
    SIGNEDMESSAGE_INFORMATION_FAULT_NOT_ON_WHITELIST,
    SIGNEDMESSAGE_INFORMATION_NONE,
    WHITELISTOPERATION_INFORMATION_NO_PERMISSION_TO_ADD,
    CommandStatus,
    FromVCSECMessage,
    OperationStatus_E,
    SignedMessage_status,
    WhitelistOperation_status,
)

from ble_mocked_transport import MockedBleTransportTestCase


def error_reply(status: CommandStatus) -> RoutableMessage:
    status.operationStatus = OperationStatus_E.OPERATIONSTATUS_ERROR
    return RoutableMessage(
        from_destination=Destination(domain=Domain.DOMAIN_VEHICLE_SECURITY),
        protobuf_message_as_bytes=FromVCSECMessage(
            commandStatus=status
        ).SerializeToString(),
    )


class VcsecOperationErrorTests(MockedBleTransportTestCase):
    async def test_signed_message_fault_raises(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = error_reply(
            CommandStatus(
                signedMessageStatus=SignedMessage_status(
                    signedMessageInformation=SIGNEDMESSAGE_INFORMATION_FAULT_NOT_ON_WHITELIST
                )
            )
        )

        with self.assertRaises(SignedMessageInformationFaultNotOnWhitelist):
            await vehicle.door_unlock()

    async def test_whitelist_fault_raises(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = error_reply(
            CommandStatus(
                whitelistOperationStatus=WhitelistOperation_status(
                    whitelistOperationInformation=WHITELISTOPERATION_INFORMATION_NO_PERMISSION_TO_ADD
                )
            )
        )

        with self.assertRaises(WhitelistOperationNoPermissionToAdd):
            await vehicle.door_unlock()

    async def test_no_mapped_fault_returns_failure(self) -> None:
        for status in (
            CommandStatus(),
            CommandStatus(
                signedMessageStatus=SignedMessage_status(
                    signedMessageInformation=SIGNEDMESSAGE_INFORMATION_NONE
                )
            ),
            CommandStatus(whitelistOperationStatus=WhitelistOperation_status()),
        ):
            with self.subTest(status=status):
                vehicle, send = self.make_vehicle()
                send.return_value = error_reply(status)

                result = await vehicle.door_unlock()

                self.assertEqual(
                    result,
                    {"response": {"result": False, "reason": "OPERATIONSTATUS_ERROR"}},
                )
