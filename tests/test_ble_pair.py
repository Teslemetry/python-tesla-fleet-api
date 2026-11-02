"""Pairing over a mocked transport: reply fast-path vs. verify-by-state polling.

``pair()`` confirms whitelisting either by the one-shot whitelist reply (fast
path) or, when that frame is lost to a session cycle, by polling a VCSEC
handshake with our own key (whitelisted keys handshake; unpaired keys fault).
These tests drive both paths and the reconnect/deadline behaviour with the real
``_send``/``_handshake`` seams mocked.
"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import Any, cast
from unittest.mock import AsyncMock, patch

from tesla_fleet_api.exceptions import (
    BluetoothTimeout,
    BluetoothTransportError,
    NotOnWhitelistFault,
    WhitelistOperationStatus,
    WhitelistOperationWhitelistFull,
)
from tesla_protocol.command.universal_message_pb2 import (
    Destination,
    Domain,
    RoutableMessage,
)
from tesla_protocol.command.errors_pb2 import GenericError_E, NominalError
from tesla_protocol.command.vcsec_pb2 import (
    CommandStatus,
    FromVCSECMessage,
    OperationStatus_E,
    VehicleStatus,
    WHITELISTOPERATION_INFORMATION_NONE,
    WHITELISTOPERATION_INFORMATION_WHITELIST_FULL,
    WhitelistOperation_information_E,
    WhitelistOperation_status,
)

from ble_mocked_transport import MockedBleTransportTestCase


def vcsec_reply(body: FromVCSECMessage | bytes) -> RoutableMessage:
    """A canned VCSEC reply carrying ``body`` as its payload."""
    payload = body if isinstance(body, bytes) else body.SerializeToString()
    return RoutableMessage(
        from_destination=Destination(domain=Domain.DOMAIN_VEHICLE_SECURITY),
        protobuf_message_as_bytes=payload,
    )


def whitelist_reply(
    info: WhitelistOperation_information_E = WHITELISTOPERATION_INFORMATION_NONE,
    status: OperationStatus_E = OperationStatus_E.OPERATIONSTATUS_OK,
) -> RoutableMessage:
    """A canned whitelist-op reply; ``info=0`` means success, else a fault code."""
    return vcsec_reply(
        FromVCSECMessage(
            commandStatus=CommandStatus(
                whitelistOperationStatus=WhitelistOperation_status(
                    whitelistOperationInformation=info, operationStatus=status
                )
            )
        )
    )


def session_info_reply() -> RoutableMessage:
    """A probe reply carrying session info, as only a whitelisted key gets."""
    return RoutableMessage(
        from_destination=Destination(domain=Domain.DOMAIN_VEHICLE_SECURITY),
        session_info=b"\x01",
    )


# Replies that do not prove the key was added: each must keep pair() waiting.
NON_SUCCESS_REPLIES: dict[str, RoutableMessage] = {
    "WAIT": vcsec_reply(
        FromVCSECMessage(
            commandStatus=CommandStatus(
                operationStatus=OperationStatus_E.OPERATIONSTATUS_WAIT
            )
        )
    ),
    "WAIT on the whitelist status": whitelist_reply(
        status=OperationStatus_E.OPERATIONSTATUS_WAIT
    ),
    "OK with no whitelist status": vcsec_reply(
        FromVCSECMessage(
            commandStatus=CommandStatus(
                operationStatus=OperationStatus_E.OPERATIONSTATUS_OK
            )
        )
    ),
    "a bare vehicleStatus": vcsec_reply(
        FromVCSECMessage(vehicleStatus=VehicleStatus())
    ),
    "a bare ack": RoutableMessage(
        from_destination=Destination(domain=Domain.DOMAIN_VEHICLE_SECURITY)
    ),
    "bytes that do not decode": vcsec_reply(b"\xff"),
}

# Replies that report the vehicle refused the operation.
REFUSAL_REPLIES: dict[str, RoutableMessage] = {
    "ERROR": vcsec_reply(
        FromVCSECMessage(
            commandStatus=CommandStatus(
                operationStatus=OperationStatus_E.OPERATIONSTATUS_ERROR
            )
        )
    ),
    "ERROR on the whitelist status": whitelist_reply(
        status=OperationStatus_E.OPERATIONSTATUS_ERROR
    ),
    "a nominalError": vcsec_reply(
        FromVCSECMessage(
            nominalError=NominalError(genericError=GenericError_E.GENERICERROR_UNKNOWN)
        )
    ),
}


class PairScriptTestCase(MockedBleTransportTestCase):
    """Base for pair() tests that script the whitelist op and each probe."""

    def _script(self, send: AsyncMock, whitelist: Any, *probes: Any) -> list[Any]:
        """Script ``_send``: the whitelist op gets ``whitelist``, probes get ``probes``.

        Each outcome is a reply to return or an exception to raise; ``True``
        stands for a probe answered with session info, ``False`` for a probe
        the vehicle faults with ``NotOnWhitelistFault``. Returns the list of
        probe outcomes actually consumed, one entry per probe sent.
        """
        remaining = list(probes)
        consumed: list[Any] = []

        async def fake_send(msg: RoutableMessage, *args: Any, **kwargs: Any) -> Any:
            if msg.HasField("session_info_request"):
                outcome: Any = remaining.pop(0) if remaining else False
                consumed.append(outcome)
            else:
                outcome = whitelist
            if outcome is True:
                return session_info_reply()
            if outcome is False:
                raise NotOnWhitelistFault
            if isinstance(outcome, (BaseException, type)):
                # An exception instance or class (every class scripted here is one).
                raise cast(BaseException, outcome)
            if isinstance(outcome, RoutableMessage):
                return outcome
            return await cast(Callable[[], Awaitable[Any]], outcome)()

        send.side_effect = fake_send
        return consumed

    def _whitelist_writes(self, send: AsyncMock) -> int:
        """Count the whitelist-op writes among ``_send`` calls."""
        return sum(
            1
            for call in send.await_args_list
            if not call.args[0].HasField("session_info_request")
        )


class PairTest(PairScriptTestCase):
    """Cover the whitelist reply fast-path and the verify-by-state poll loop."""

    async def test_reply_path_success(self) -> None:
        """A surviving success reply returns without ever polling."""
        vehicle, send = self.make_vehicle()
        probes = self._script(send, whitelist_reply())

        await vehicle.pair(poll_interval=0.01, timeout=1)

        self.assertEqual(send.await_count, 1)
        self.assertEqual(probes, [])

    async def test_reply_path_fault_raises(self) -> None:
        """A whitelist-op fault reply raises its mapped exception."""
        vehicle, send = self.make_vehicle()
        self._script(
            send, whitelist_reply(info=WHITELISTOPERATION_INFORMATION_WHITELIST_FULL)
        )

        with self.assertRaises(WhitelistOperationWhitelistFull):
            await vehicle.pair(poll_interval=0.01, timeout=1)

    async def test_reply_lost_poll_detects_success(self) -> None:
        """A lost reply is recovered by the poll, without re-sending the op."""
        vehicle, send = self.make_vehicle()
        probes = self._script(send, BluetoothTimeout, False, True)

        await vehicle.pair(poll_interval=0.01, timeout=1)

        # Whitelist op written exactly once; re-sending would re-prompt the user.
        self.assertEqual(self._whitelist_writes(send), 1)
        self.assertEqual(probes, [False, True])

    async def test_late_reply_fault_raises_during_poll(self) -> None:
        """A late whitelist-op fault raises its mapped exception while polling."""
        vehicle, send = self.make_vehicle()

        async def timeout_after_late_fault() -> None:
            getattr(vehicle, "_queues")[Domain.DOMAIN_VEHICLE_SECURITY].put_nowait(
                whitelist_reply(info=WHITELISTOPERATION_INFORMATION_WHITELIST_FULL)
            )
            raise BluetoothTimeout

        probes = self._script(send, timeout_after_late_fault, True)

        with self.assertRaises(WhitelistOperationWhitelistFull):
            await vehicle.pair(poll_interval=0.01, timeout=1)

        self.assertEqual(send.await_count, 1)
        self.assertEqual(probes, [])

    async def test_late_reply_after_final_sleep_returns(self) -> None:
        """A reply landing in the final sleep is drained before timing out."""
        vehicle, send = self.make_vehicle()
        probes = self._script(send, BluetoothTimeout, False)

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

        self.assertEqual(self._whitelist_writes(send), 1)
        self.assertEqual(probes, [False])

    async def test_nonpositive_poll_interval_raises(self) -> None:
        """Invalid poll intervals are rejected before sending the whitelist op."""
        vehicle, send = self.make_vehicle()

        with self.assertRaisesRegex(ValueError, "poll_interval must be greater than 0"):
            await vehicle.pair(poll_interval=0)

        send.assert_not_awaited()

    async def test_reconnect_midwait_poll_continues(self) -> None:
        """A transport failure mid-poll is 'not yet', so polling keeps going."""
        vehicle, send = self.make_vehicle()
        probes = self._script(
            send, BluetoothTimeout, BluetoothTransportError, False, True
        )

        await vehicle.pair(poll_interval=0.01, timeout=1)

        self.assertEqual(self._whitelist_writes(send), 1)
        self.assertEqual(len(probes), 3)

    async def test_deadline_failure(self) -> None:
        """Never confirming before the deadline raises a typed BluetoothTimeout."""
        vehicle, send = self.make_vehicle()
        probes = self._script(send, BluetoothTimeout)

        with self.assertRaises(BluetoothTimeout):
            await vehicle.pair(poll_interval=0.01, timeout=0.05)

        # Still only one whitelist op the whole time.
        self.assertEqual(self._whitelist_writes(send), 1)
        self.assertGreater(len(probes), 0)


class PairEvidenceTest(PairScriptTestCase):
    """pair() succeeds only on an explicit success reply or a session-info probe."""

    async def test_non_success_reply_keeps_waiting(self) -> None:
        """A reply that does not report the key added never ends pair() as success."""
        for name, reply in NON_SUCCESS_REPLIES.items():
            with self.subTest(name):
                vehicle, send = self.make_vehicle()
                self._script(send, reply)

                with self.assertRaises(BluetoothTimeout):
                    await vehicle.pair(poll_interval=0.01, timeout=0.05)

                self.assertEqual(self._whitelist_writes(send), 1)

    async def test_wait_then_probe_success(self) -> None:
        """A WAIT keeps polling until the probe proves the key, with one write."""
        vehicle, send = self.make_vehicle()
        probes = self._script(send, NON_SUCCESS_REPLIES["WAIT"], False, False, True)

        await vehicle.pair(poll_interval=0.01, timeout=1)

        self.assertEqual(self._whitelist_writes(send), 1)
        self.assertEqual(probes, [False, False, True])

    async def test_refusal_reply_raises(self) -> None:
        """A reply that reports the operation refused raises WhitelistOperationStatus."""
        for name, reply in REFUSAL_REPLIES.items():
            with self.subTest(name):
                vehicle, send = self.make_vehicle()
                self._script(send, reply)

                with self.assertRaises(WhitelistOperationStatus):
                    await vehicle.pair(poll_interval=0.01, timeout=1)

                self.assertEqual(self._whitelist_writes(send), 1)

    async def test_probe_bare_ack_with_ready_session_is_not_success(self) -> None:
        """A probe answered without session info proves nothing, even if a session is ready."""
        vehicle, send = self.make_vehicle()
        # make_vehicle pre-marks both sessions ready, as a session from before would be.
        self.assertTrue(
            getattr(vehicle, "_sessions")[Domain.DOMAIN_VEHICLE_SECURITY].ready
        )
        bare_ack = NON_SUCCESS_REPLIES["a bare ack"]
        self._script(send, BluetoothTimeout, *([bare_ack] * 50))

        with self.assertRaises(BluetoothTimeout):
            await vehicle.pair(poll_interval=0.01, timeout=0.05)

    async def test_late_non_success_reply_is_not_success(self) -> None:
        """A late reply that does not report success leaves pair() polling."""
        vehicle, send = self.make_vehicle()

        async def timeout_after_late_wait() -> None:
            getattr(vehicle, "_queues")[Domain.DOMAIN_VEHICLE_SECURITY].put_nowait(
                NON_SUCCESS_REPLIES["WAIT on the whitelist status"]
            )
            raise BluetoothTimeout

        self._script(send, timeout_after_late_wait)

        with self.assertRaises(BluetoothTimeout):
            await vehicle.pair(poll_interval=0.01, timeout=0.05)
