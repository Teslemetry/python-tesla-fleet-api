"""Tests that the ``expects_data`` hint is threaded from the command layer into
``_send`` and preserved across the WAIT retry.

Uses the mocked-transport base (``_send`` is an ``AsyncMock``) to inspect the
flag each command passes without a real BLE connection. A VCSEC actuation
replies with a bare terminal ack, so it must send ``expects_data=False``; reads
and infotainment actions expect a data frame and keep ``expects_data=True``.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

from tesla_protocol.command.universal_message_pb2 import (
    Destination,
    Domain,
    MessageStatus,
    OperationStatus_E,
    RoutableMessage,
)
from tesla_protocol.command.vcsec_pb2 import VehicleStatus

from ble_mocked_transport import (
    MockedBleTransportTestCase,
    infotainment_action_ok_reply,
    vcsec_ok_reply,
    vcsec_vehicle_status_reply,
)


def _expects_data(send: AsyncMock) -> bool:
    """Return the ``expects_data`` kwarg of the most recent ``_send`` call."""
    await_args = send.await_args
    assert await_args is not None
    return await_args.kwargs["expects_data"]


def vcsec_wait_reply() -> RoutableMessage:
    """A canned VCSEC reply asking the caller to retry (OPERATIONSTATUS_WAIT)."""
    return RoutableMessage(
        from_destination=Destination(domain=Domain.DOMAIN_VEHICLE_SECURITY),
        signedMessageStatus=MessageStatus(
            operation_status=OperationStatus_E.OPERATIONSTATUS_WAIT
        ),
    )


class ExpectsDataFlagTests(MockedBleTransportTestCase):
    async def test_vcsec_actuation_sends_expects_data_false(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = vcsec_ok_reply()

        await vehicle.door_lock()

        self.assertFalse(_expects_data(send))

    async def test_infotainment_action_sends_expects_data_true(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = infotainment_action_ok_reply()

        await vehicle.charge_start()

        self.assertTrue(_expects_data(send))

    async def test_vcsec_read_sends_expects_data_true(self) -> None:
        vehicle, send = self.make_vehicle()
        send.return_value = vcsec_vehicle_status_reply(VehicleStatus())

        await vehicle.vehicle_state()

        self.assertTrue(_expects_data(send))


class ExpectsDataRetryTests(MockedBleTransportTestCase):
    async def test_wait_reply_retries_and_preserves_expects_data(self) -> None:
        vehicle, send = self.make_vehicle()
        send.side_effect = [vcsec_wait_reply(), vcsec_ok_reply()]

        # Patch out the 2s inter-retry sleep so the retry path runs instantly.
        with patch(
            "tesla_fleet_api.tesla.vehicle.commands.sleep", AsyncMock()
        ) as sleep:
            result = await vehicle.door_lock()

        self.assertEqual(result, {"response": {"result": True, "reason": ""}})
        self.assertEqual(send.await_count, 2)
        sleep.assert_awaited_once()
        for call in send.await_args_list:
            self.assertFalse(call.kwargs["expects_data"])
