"""Pairing over a mocked transport: reply fast-path vs. verify-by-state polling.

``pair()`` confirms whitelisting either by the one-shot whitelist reply (fast
path) or, when that frame is lost to a session cycle, by polling a VCSEC
handshake with our own key (whitelisted keys handshake; unpaired keys fault).
These tests drive both paths and the reconnect/deadline behaviour with the real
``_send``/``_handshake`` seams mocked.
"""

from __future__ import annotations

import asyncio
from typing import Any
from unittest.mock import AsyncMock, patch

from tesla_fleet_api.exceptions import (
    BluetoothTimeout,
    BluetoothTransportError,
    NotOnWhitelistFault,
    WhitelistOperationWhitelistFull,
)
from tesla_fleet_api.tesla.vehicle.proto.universal_message_pb2 import (
    Destination,
    Domain,
    RoutableMessage,
)
from tesla_fleet_api.tesla.vehicle.proto.vcsec_pb2 import (
    CommandStatus,
    FromVCSECMessage,
    WHITELISTOPERATION_INFORMATION_NONE,
    WHITELISTOPERATION_INFORMATION_WHITELIST_FULL,
    WhitelistOperation_information_E,
    WhitelistOperation_status,
)

from ble_mocked_transport import MockedBleTransportTestCase


def whitelist_reply(
    info: WhitelistOperation_information_E = WHITELISTOPERATION_INFORMATION_NONE,
) -> RoutableMessage:
    """A canned whitelist-op reply; ``info=0`` means success, else a fault code."""
    body = FromVCSECMessage(
        commandStatus=CommandStatus(
            whitelistOperationStatus=WhitelistOperation_status(
                whitelistOperationInformation=info
            )
        )
    )
    return RoutableMessage(
        from_destination=Destination(domain=Domain.DOMAIN_VEHICLE_SECURITY),
        protobuf_message_as_bytes=body.SerializeToString(),
    )


class PairTest(MockedBleTransportTestCase):
    """Cover the whitelist reply fast-path and the verify-by-state poll loop."""

    def _mock_handshake(self, vehicle: Any, *outcomes: Any) -> AsyncMock:
        """Install a mocked ``_handshake`` scripting each poll's outcome."""
        handshake = AsyncMock(side_effect=list(outcomes))
        setattr(vehicle, "_handshake", handshake)
        return handshake

    async def test_reply_path_success(self) -> None:
        """A surviving success reply returns without ever polling."""
        vehicle, send = self.make_vehicle()
        send.return_value = whitelist_reply()
        handshake = self._mock_handshake(vehicle)

        await vehicle.pair(poll_interval=0.01, timeout=1)

        self.assertEqual(send.await_count, 1)
        handshake.assert_not_awaited()

    async def test_reply_path_fault_raises(self) -> None:
        """A whitelist-op fault reply raises its mapped exception."""
        vehicle, send = self.make_vehicle()
        send.return_value = whitelist_reply(
            info=WHITELISTOPERATION_INFORMATION_WHITELIST_FULL
        )

        with self.assertRaises(WhitelistOperationWhitelistFull):
            await vehicle.pair(poll_interval=0.01, timeout=1)

    async def test_reply_lost_poll_detects_success(self) -> None:
        """A lost reply is recovered by the poll, without re-sending the op."""
        vehicle, send = self.make_vehicle()
        send.side_effect = BluetoothTimeout
        handshake = self._mock_handshake(vehicle, NotOnWhitelistFault, True)

        await vehicle.pair(poll_interval=0.01, timeout=1)

        # Whitelist op written exactly once; re-sending would re-prompt the user.
        self.assertEqual(send.await_count, 1)
        self.assertEqual(handshake.await_count, 2)

    async def test_late_reply_fault_raises_during_poll(self) -> None:
        """A late whitelist-op fault raises its mapped exception while polling."""
        vehicle, send = self.make_vehicle()

        async def timeout_after_late_fault(*args: Any, **kwargs: Any) -> None:
            getattr(vehicle, "_queues")[Domain.DOMAIN_VEHICLE_SECURITY].put_nowait(
                whitelist_reply(info=WHITELISTOPERATION_INFORMATION_WHITELIST_FULL)
            )
            raise BluetoothTimeout

        send.side_effect = timeout_after_late_fault
        handshake = self._mock_handshake(vehicle, True)

        with self.assertRaises(WhitelistOperationWhitelistFull):
            await vehicle.pair(poll_interval=0.01, timeout=1)

        self.assertEqual(send.await_count, 1)
        handshake.assert_not_awaited()

    async def test_late_reply_after_final_sleep_returns(self) -> None:
        """A reply landing in the final sleep is drained before timing out."""
        vehicle, send = self.make_vehicle()
        send.side_effect = BluetoothTimeout
        handshake = self._mock_handshake(vehicle, False)

        original_sleep = asyncio.sleep

        async def queue_reply_then_return(delay: float) -> None:
            getattr(vehicle, "_queues")[Domain.DOMAIN_VEHICLE_SECURITY].put_nowait(
                whitelist_reply()
            )
            await original_sleep(delay)

        with patch(
            "tesla_fleet_api.tesla.vehicle.bluetooth.asyncio.sleep",
            new=queue_reply_then_return,
        ):
            await vehicle.pair(poll_interval=0.02, timeout=0.01)

        self.assertEqual(send.await_count, 1)
        self.assertEqual(handshake.await_count, 1)

    async def test_nonpositive_poll_interval_raises(self) -> None:
        """Invalid poll intervals are rejected before sending the whitelist op."""
        vehicle, send = self.make_vehicle()

        with self.assertRaisesRegex(ValueError, "poll_interval must be greater than 0"):
            await vehicle.pair(poll_interval=0)

        send.assert_not_awaited()

    async def test_reconnect_midwait_poll_continues(self) -> None:
        """A transport failure mid-poll is 'not yet', so polling keeps going."""
        vehicle, send = self.make_vehicle()
        send.side_effect = BluetoothTimeout
        handshake = self._mock_handshake(
            vehicle, BluetoothTransportError, NotOnWhitelistFault, True
        )

        await vehicle.pair(poll_interval=0.01, timeout=1)

        self.assertEqual(send.await_count, 1)
        self.assertEqual(handshake.await_count, 3)

    async def test_deadline_failure(self) -> None:
        """Never confirming before the deadline raises a typed BluetoothTimeout."""
        vehicle, send = self.make_vehicle()
        send.side_effect = BluetoothTimeout
        handshake = self._mock_handshake(vehicle)
        handshake.side_effect = NotOnWhitelistFault

        with self.assertRaises(BluetoothTimeout):
            await vehicle.pair(poll_interval=0.01, timeout=0.05)

        # Still only one whitelist op the whole time.
        self.assertEqual(send.await_count, 1)
        self.assertGreater(handshake.await_count, 0)
