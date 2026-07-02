"""Regression test: signed-command counter increment runs under the session lock."""

from unittest import IsolatedAsyncioTestCase
from unittest.mock import MagicMock

from cryptography.hazmat.primitives.asymmetric import ec

from tesla_fleet_api.tesla.vehicle.commands import Commands
from tesla_fleet_api.tesla.vehicle.proto.universal_message_pb2 import (
    Domain,
)


class _ConcreteCommands(Commands):
    """Minimal concrete subclass so Commands can be instantiated."""

    _auth_method = "hmac"

    async def _send(self, msg, requires):  # pragma: no cover - not reached
        raise AssertionError("_send should not be called in this test")


class CounterLockTests(IsolatedAsyncioTestCase):
    VIN = "5YJXCAE43LF123456"

    def _make_commands(self) -> _ConcreteCommands:
        parent = MagicMock()
        key = ec.generate_private_key(ec.SECP256R1())
        return _ConcreteCommands(parent, self.VIN, private_key=key)

    async def test_command_holds_session_lock_during_message_build(self):
        cmds = self._make_commands()
        session = cmds._sessions[Domain.DOMAIN_VEHICLE_SECURITY]

        # Mark the session ready so _command skips the handshake.
        session.epoch = b"\x00" * 16
        session.hmac = b"\x00" * 32
        session.delta = 0

        observed = {}

        # Replace the message builder with a stub that records lock state, then
        # aborts before _send via a sentinel.
        async def fake_command_hmac(sess, command, attempt=1):
            observed["locked"] = sess.lock.locked()
            raise RuntimeError("stop-after-build")

        cmds._commandHmac = fake_command_hmac  # type: ignore[assignment]

        with self.assertRaisesRegex(RuntimeError, "stop-after-build"):
            await cmds._command(Domain.DOMAIN_VEHICLE_SECURITY, b"")

        self.assertTrue(
            observed.get("locked"),
            "session.lock must be held while the command message is built",
        )
        # And after the aborted call the lock must be released (not leaked).
        self.assertFalse(session.lock.locked())
