"""Tests for TeslemetryEnergySite.wait_until_paired(), the verify-by-use
pairing-completion helper described in docs/energy_local_control.md step 4.

Polling is exercised against a mocked find_authorized_clients() rather than
real HTTP, with small timeout/poll_interval values so the tests run fast
while still exercising the real asyncio.sleep()-based polling loop.
"""

from __future__ import annotations

import asyncio
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, MagicMock

from tesla_fleet_api.const import AuthorizedClientState
from tesla_fleet_api.exceptions import (
    AuthorizedClientPairingTimedOut,
    AuthorizedClientWaitExpired,
)
from tesla_fleet_api.teslemetry.energysite import AuthorizedClient, AuthorizedClients
from tesla_fleet_api.teslemetry.teslemetry import Teslemetry

PUBLIC_KEY_B64 = "MIIBCgKCAQEAsomeBase64EncodedRsaPublicKeyBytes=="


def _client(state: AuthorizedClientState) -> AuthorizedClient:
    return AuthorizedClient(
        public_key=PUBLIC_KEY_B64,
        state=state,
        roles=None,
        verification=None,
        raw={},
    )


class WaitUntilPairedTests(IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.api = Teslemetry(session=MagicMock(), access_token="token")
        self.site = self.api.energySites.create(12345)

    async def test_returns_immediately_on_verified(self) -> None:
        self.site.find_authorized_clients = AsyncMock(  # type: ignore[method-assign]
            return_value=AuthorizedClients(
                clients=[_client(AuthorizedClientState.VERIFIED)], raw={}
            )
        )
        result = await self.site.wait_until_paired(
            PUBLIC_KEY_B64, timeout=5, poll_interval=0.01
        )
        self.assertEqual(result.state, AuthorizedClientState.VERIFIED)
        self.site.find_authorized_clients.assert_awaited_once()

    async def test_polls_until_verified(self) -> None:
        responses = [
            AuthorizedClients(
                clients=[_client(AuthorizedClientState.PENDING_VERIFICATION)], raw={}
            ),
            AuthorizedClients(
                clients=[_client(AuthorizedClientState.PENDING_VERIFICATION)], raw={}
            ),
            AuthorizedClients(
                clients=[_client(AuthorizedClientState.VERIFIED)], raw={}
            ),
        ]
        self.site.find_authorized_clients = AsyncMock(  # type: ignore[method-assign]
            side_effect=responses
        )
        result = await self.site.wait_until_paired(
            PUBLIC_KEY_B64, timeout=5, poll_interval=0.01
        )
        self.assertEqual(result.state, AuthorizedClientState.VERIFIED)
        self.assertEqual(self.site.find_authorized_clients.await_count, 3)

    async def test_raises_distinctly_on_pending_verification_timeout(self) -> None:
        self.site.find_authorized_clients = AsyncMock(  # type: ignore[method-assign]
            return_value=AuthorizedClients(
                clients=[_client(AuthorizedClientState.PENDING_VERIFICATION_TIMEOUT)],
                raw={},
            )
        )
        with self.assertRaises(AuthorizedClientPairingTimedOut):
            await self.site.wait_until_paired(
                PUBLIC_KEY_B64, timeout=5, poll_interval=0.01
            )
        self.site.find_authorized_clients.assert_awaited_once()

    async def test_enforces_overall_timeout_while_pending(self) -> None:
        self.site.find_authorized_clients = AsyncMock(  # type: ignore[method-assign]
            return_value=AuthorizedClients(
                clients=[_client(AuthorizedClientState.PENDING_VERIFICATION)], raw={}
            )
        )
        with self.assertRaises(AuthorizedClientWaitExpired):
            await self.site.wait_until_paired(
                PUBLIC_KEY_B64, timeout=0.03, poll_interval=0.01
            )
        self.assertGreaterEqual(self.site.find_authorized_clients.await_count, 1)

    async def test_enforces_timeout_when_client_lookup_hangs(self) -> None:
        never_returns = asyncio.Event()
        self.site.find_authorized_clients = AsyncMock(  # type: ignore[method-assign]
            side_effect=never_returns.wait
        )

        with self.assertRaises(AuthorizedClientWaitExpired):
            await self.site.wait_until_paired(
                PUBLIC_KEY_B64, timeout=0.03, poll_interval=0.01
            )

        self.site.find_authorized_clients.assert_awaited_once()

    async def test_verify_by_use_confirms_after_verified_state(self) -> None:
        self.site.find_authorized_clients = AsyncMock(  # type: ignore[method-assign]
            return_value=AuthorizedClients(
                clients=[_client(AuthorizedClientState.VERIFIED)], raw={}
            )
        )
        verify_by_use = AsyncMock(return_value=None)
        result = await self.site.wait_until_paired(
            PUBLIC_KEY_B64,
            verify_by_use=verify_by_use,
            timeout=5,
            poll_interval=0.01,
        )
        self.assertEqual(result.state, AuthorizedClientState.VERIFIED)
        verify_by_use.assert_awaited_once()

    async def test_verify_by_use_failure_keeps_polling_until_it_succeeds(
        self,
    ) -> None:
        self.site.find_authorized_clients = AsyncMock(  # type: ignore[method-assign]
            return_value=AuthorizedClients(
                clients=[_client(AuthorizedClientState.VERIFIED)], raw={}
            )
        )
        verify_by_use = AsyncMock(side_effect=[RuntimeError("not yet"), None])
        result = await self.site.wait_until_paired(
            PUBLIC_KEY_B64,
            verify_by_use=verify_by_use,
            timeout=5,
            poll_interval=0.01,
        )
        self.assertEqual(result.state, AuthorizedClientState.VERIFIED)
        self.assertEqual(verify_by_use.await_count, 2)

    async def test_verify_by_use_never_succeeding_raises_wait_expired(self) -> None:
        self.site.find_authorized_clients = AsyncMock(  # type: ignore[method-assign]
            return_value=AuthorizedClients(
                clients=[_client(AuthorizedClientState.VERIFIED)], raw={}
            )
        )
        verify_by_use = AsyncMock(side_effect=RuntimeError("never confirms"))
        with self.assertRaises(AuthorizedClientWaitExpired):
            await self.site.wait_until_paired(
                PUBLIC_KEY_B64,
                verify_by_use=verify_by_use,
                timeout=0.03,
                poll_interval=0.01,
            )

    async def test_enforces_timeout_when_verify_by_use_hangs(self) -> None:
        self.site.find_authorized_clients = AsyncMock(  # type: ignore[method-assign]
            return_value=AuthorizedClients(
                clients=[_client(AuthorizedClientState.VERIFIED)], raw={}
            )
        )
        never_returns = asyncio.Event()
        verify_by_use = AsyncMock(side_effect=never_returns.wait)

        with self.assertRaises(AuthorizedClientWaitExpired):
            await self.site.wait_until_paired(
                PUBLIC_KEY_B64,
                verify_by_use=verify_by_use,
                timeout=0.03,
                poll_interval=0.01,
            )

        verify_by_use.assert_awaited_once()

    async def test_no_matching_client_yet_keeps_polling(self) -> None:
        self.site.find_authorized_clients = AsyncMock(  # type: ignore[method-assign]
            return_value=AuthorizedClients(clients=[], raw={})
        )
        with self.assertRaises(AuthorizedClientWaitExpired):
            await self.site.wait_until_paired(
                PUBLIC_KEY_B64, timeout=0.03, poll_interval=0.01
            )

    async def test_accepts_raw_public_key_bytes(self) -> None:
        import base64

        raw_key = b"raw-der-bytes"
        b64 = base64.b64encode(raw_key).decode("ascii")
        self.site.find_authorized_clients = AsyncMock(  # type: ignore[method-assign]
            return_value=AuthorizedClients(
                clients=[
                    AuthorizedClient(
                        public_key=b64,
                        state=AuthorizedClientState.VERIFIED,
                        roles=None,
                        verification=None,
                        raw={},
                    )
                ],
                raw={},
            )
        )
        result = await self.site.wait_until_paired(
            raw_key, timeout=5, poll_interval=0.01
        )
        self.assertEqual(result.public_key, b64)
