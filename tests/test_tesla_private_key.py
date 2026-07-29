"""``get_private_key``/``get_rsa_private_key`` must create their PEM files atomically.

The keys sign Tesla vehicle commands (Fleet API and BLE) and register with the
Powerwall TEDapi gateway. Both are created via an O_EXCL-opened file at mode
0o600 so there is never a write-then-chmod window where the key is
world-readable, and a losing concurrent creator falls back to reading the
winner's file instead of raising.
"""

from __future__ import annotations

import asyncio
import os
import stat
import tempfile
from pathlib import Path
from unittest import IsolatedAsyncioTestCase, mock

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec, rsa

from tesla_fleet_api.tesla.tesla import Tesla


def _ec_pem(key: ec.EllipticCurvePrivateKey) -> bytes:
    return key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    )


def _rsa_pem(key: rsa.RSAPrivateKey) -> bytes:
    return key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    )


class GetPrivateKeyPermissionsTests(IsolatedAsyncioTestCase):
    async def test_new_key_file_uses_chmod_without_fchmod(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = str(Path(tmp_dir) / "private_key.pem")

            with (
                mock.patch("tesla_fleet_api.tesla.tesla.os.fchmod", new=None),
                mock.patch(
                    "tesla_fleet_api.tesla.tesla.os.chmod", wraps=os.chmod
                ) as chmod,
            ):
                await Tesla().get_private_key(path)

            chmod.assert_called_once_with(path, 0o600)

    async def test_new_key_file_closes_fd_when_chmod_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = str(Path(tmp_dir) / "private_key.pem")

            with (
                mock.patch("tesla_fleet_api.tesla.tesla.os.fchmod", new=None),
                mock.patch(
                    "tesla_fleet_api.tesla.tesla.os.chmod",
                    side_effect=OSError("chmod failed"),
                ),
                mock.patch(
                    "tesla_fleet_api.tesla.tesla.os.close", wraps=os.close
                ) as close,
            ):
                with self.assertRaises(OSError):
                    await Tesla().get_private_key(path)

            close.assert_called_once()

    async def test_new_key_file_is_owner_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = str(Path(tmp_dir) / "private_key.pem")
            tesla = Tesla()

            await tesla.get_private_key(path)

            mode = stat.S_IMODE(Path(path).stat().st_mode)
            self.assertEqual(mode, 0o600)

    async def test_new_key_file_is_owner_only_with_restrictive_umask(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = str(Path(tmp_dir) / "private_key.pem")
            tesla = Tesla()
            old_umask = os.umask(0o777)
            try:
                await tesla.get_private_key(path)
            finally:
                os.umask(old_umask)

            mode = stat.S_IMODE(Path(path).stat().st_mode)
            self.assertEqual(mode, 0o600)

    async def test_existing_key_read_path_unchanged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = str(Path(tmp_dir) / "private_key.pem")
            creator = Tesla()
            created = await creator.get_private_key(path)

            reader = Tesla()
            read_back = await reader.get_private_key(path)

            self.assertEqual(_ec_pem(read_back), _ec_pem(created))
            mode = stat.S_IMODE(Path(path).stat().st_mode)
            self.assertEqual(mode, 0o600)

    async def test_concurrent_create_falls_back_to_read(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = str(Path(tmp_dir) / "private_key.pem")
            winner = Tesla()
            winner_key = await winner.get_private_key(path)

            # Simulate a caller whose exists() check ran before the winner's
            # create - it must fall back to reading the winner's file rather
            # than raising FileExistsError.
            loser = Tesla()
            with mock.patch("tesla_fleet_api.tesla.tesla.exists", return_value=False):
                key = await loser.get_private_key(path)

            self.assertEqual(_ec_pem(key), _ec_pem(winner_key))

    async def test_concurrent_create_waits_for_winner_to_finish_writing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "private_key.pem"
            winner_key = ec.generate_private_key(ec.SECP256R1())
            path.touch(mode=0o600)

            async def finish_write() -> None:
                await asyncio.sleep(0.1)
                path.write_bytes(_ec_pem(winner_key))

            writer = asyncio.create_task(finish_write())
            try:
                loser = Tesla()
                with mock.patch(
                    "tesla_fleet_api.tesla.tesla.exists", return_value=False
                ):
                    key = await loser.get_private_key(str(path))
            finally:
                await writer

            self.assertEqual(_ec_pem(key), _ec_pem(winner_key))

    async def test_existing_path_waits_for_winner_to_finish_writing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "private_key.pem"
            winner_key = ec.generate_private_key(ec.SECP256R1())
            path.touch(mode=0o600)

            async def finish_write() -> None:
                await asyncio.sleep(0.1)
                path.write_bytes(_ec_pem(winner_key))

            writer = asyncio.create_task(finish_write())
            try:
                key = await Tesla().get_private_key(str(path))
            finally:
                await writer

            self.assertEqual(_ec_pem(key), _ec_pem(winner_key))


class GetRsaPrivateKeyPermissionsTests(IsolatedAsyncioTestCase):
    async def test_new_key_file_is_owner_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = str(Path(tmp_dir) / "tedapi_rsa_private.pem")
            tesla = Tesla()

            await tesla.get_rsa_private_key(path, key_size=1024)

            mode = stat.S_IMODE(Path(path).stat().st_mode)
            self.assertEqual(mode, 0o600)

    async def test_new_key_file_is_owner_only_with_restrictive_umask(self) -> None:
        # Unlike multiprocessing's semaphore file, a plain subprocess has no
        # umask-sensitive IPC of its own, so this exercises the isolated
        # subprocess path directly (no fallback needed) and still produces a
        # correct owner-only key file via _owner_only_opener's explicit
        # fchmod, which bypasses umask entirely.
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = str(Path(tmp_dir) / "tedapi_rsa_private.pem")
            tesla = Tesla()
            old_umask = os.umask(0o777)
            try:
                await tesla.get_rsa_private_key(path, key_size=1024)
            finally:
                os.umask(old_umask)

            mode = stat.S_IMODE(Path(path).stat().st_mode)
            self.assertEqual(mode, 0o600)

    async def test_existing_key_read_path_unchanged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = str(Path(tmp_dir) / "tedapi_rsa_private.pem")
            creator = Tesla()
            created = await creator.get_rsa_private_key(path, key_size=1024)

            reader = Tesla()
            read_back = await reader.get_rsa_private_key(path, key_size=1024)

            self.assertEqual(_rsa_pem(read_back), _rsa_pem(created))
            mode = stat.S_IMODE(Path(path).stat().st_mode)
            self.assertEqual(mode, 0o600)

    async def test_concurrent_create_falls_back_to_read(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = str(Path(tmp_dir) / "tedapi_rsa_private.pem")
            winner = Tesla()
            winner_key = await winner.get_rsa_private_key(path, key_size=1024)

            loser = Tesla()
            with mock.patch("tesla_fleet_api.tesla.tesla.exists", return_value=False):
                key = await loser.get_rsa_private_key(path, key_size=1024)

            self.assertEqual(_rsa_pem(key), _rsa_pem(winner_key))

    async def test_concurrent_create_waits_for_winner_to_finish_writing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "tedapi_rsa_private.pem"
            winner_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=1024,
            )
            path.touch(mode=0o600)

            async def finish_write() -> None:
                await asyncio.sleep(0.1)
                path.write_bytes(_rsa_pem(winner_key))

            writer = asyncio.create_task(finish_write())
            try:
                loser = Tesla()
                with mock.patch(
                    "tesla_fleet_api.tesla.tesla.exists", return_value=False
                ):
                    key = await loser.get_rsa_private_key(str(path), key_size=1024)
            finally:
                await writer

            self.assertEqual(_rsa_pem(key), _rsa_pem(winner_key))

    async def test_existing_path_waits_for_winner_to_finish_writing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "tedapi_rsa_private.pem"
            winner_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=1024,
            )
            path.touch(mode=0o600)

            async def finish_write() -> None:
                await asyncio.sleep(0.1)
                path.write_bytes(_rsa_pem(winner_key))

            writer = asyncio.create_task(finish_write())
            try:
                key = await Tesla().get_rsa_private_key(str(path), key_size=1024)
            finally:
                await writer

            self.assertEqual(_rsa_pem(key), _rsa_pem(winner_key))

    async def test_generation_does_not_block_the_event_loop(self) -> None:
        """A concurrent heartbeat must keep ticking during real RSA generation.

        Generation runs in a separate worker process (a plain
        ``asyncio.to_thread`` would not do - cryptography's RSA keygen holds
        the GIL for its full duration, so a thread still stalls the caller's
        event loop), which is why this uses a real key rather than a mocked
        stand-in: only genuine process isolation proves the loop stays free.
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = str(Path(tmp_dir) / "tedapi_rsa_private.pem")

            ticks = 0

            async def heartbeat() -> None:
                nonlocal ticks
                while True:
                    await asyncio.sleep(0.01)
                    ticks += 1

            heart = asyncio.create_task(heartbeat())
            try:
                key = await Tesla().get_rsa_private_key(path, key_size=4096)
            finally:
                heart.cancel()

            self.assertGreater(ticks, 5)
            self.assertEqual(_rsa_pem(key), Path(path).read_bytes())

    async def test_deserialization_does_not_block_the_event_loop(self) -> None:
        """The post-generation PEM deserialization also must not stall the loop.

        It runs in the main process (via ``asyncio.to_thread``), so unlike
        generation it can be exercised with a mocked slow stand-in.
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = str(Path(tmp_dir) / "tedapi_rsa_private.pem")
            real_key = rsa.generate_private_key(public_exponent=65537, key_size=1024)

            def slow_load_pem_private_key(
                *args: object, **kwargs: object
            ) -> rsa.RSAPrivateKey:
                import time as time_module

                time_module.sleep(0.15)
                return real_key

            ticks = 0

            async def heartbeat() -> None:
                nonlocal ticks
                while True:
                    await asyncio.sleep(0.01)
                    ticks += 1

            with mock.patch(
                "tesla_fleet_api.tesla.tesla.serialization.load_pem_private_key",
                side_effect=slow_load_pem_private_key,
            ):
                heart = asyncio.create_task(heartbeat())
                try:
                    await Tesla().get_rsa_private_key(path, key_size=1024)
                finally:
                    heart.cancel()

            self.assertGreater(ticks, 10)

    async def test_cancellation_kills_the_subprocess(self) -> None:
        """Cancelling mid-generation kills the child rather than leaving it orphaned.

        Killing and awaiting the child's exit are both async operations, so
        this also can't block the event loop the way a synchronous
        `ProcessPoolExecutor.shutdown(wait=True)` could.
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = str(Path(tmp_dir) / "tedapi_rsa_private.pem")
            generation_started = asyncio.Event()
            killed = asyncio.Event()

            class _SlowProc:
                returncode: int | None = None

                async def communicate(self) -> tuple[bytes, bytes]:
                    generation_started.set()
                    await asyncio.Event().wait()  # never resolves on its own
                    raise AssertionError("unreachable")

                def kill(self) -> None:
                    killed.set()

                async def wait(self) -> int:
                    await killed.wait()
                    self.returncode = -9
                    return self.returncode

            async def fake_create_subprocess_exec(
                *args: object, **kwargs: object
            ) -> _SlowProc:
                return _SlowProc()

            with mock.patch(
                "tesla_fleet_api.tesla.tesla.asyncio.create_subprocess_exec",
                side_effect=fake_create_subprocess_exec,
            ):
                task = asyncio.create_task(
                    Tesla().get_rsa_private_key(path, key_size=1024)
                )
                await generation_started.wait()
                task.cancel()
                with self.assertRaises(asyncio.CancelledError):
                    await task

            self.assertTrue(killed.is_set())

    async def test_cancellation_preserves_cancel_when_subprocess_already_exited(
        self,
    ) -> None:
        generation_started = asyncio.Event()
        waited = asyncio.Event()

        class _ExitedProc:
            returncode = 0

            async def communicate(self) -> tuple[bytes, bytes]:
                generation_started.set()
                await asyncio.Event().wait()
                raise AssertionError("unreachable")

            def kill(self) -> None:
                raise ProcessLookupError

            async def wait(self) -> int:
                waited.set()
                return self.returncode

        async def fake_create_subprocess_exec(
            *args: object, **kwargs: object
        ) -> _ExitedProc:
            return _ExitedProc()

        with mock.patch(
            "tesla_fleet_api.tesla.tesla.asyncio.create_subprocess_exec",
            side_effect=fake_create_subprocess_exec,
        ):
            task = asyncio.create_task(
                Tesla().get_rsa_private_key("unused.pem", key_size=1024)
            )
            await generation_started.wait()
            task.cancel()
            with self.assertRaises(asyncio.CancelledError):
                await task

        self.assertTrue(waited.is_set())

    async def test_subprocess_launch_failure_falls_back_to_in_process_generation(
        self,
    ) -> None:
        """A caller whose environment can't launch the subprocess still succeeds.

        Falls back to in-process generation with a logged warning instead of
        raising, matching the pre-process-isolation behavior. The fallback
        deliberately isn't specific to any one launch-failure cause (a
        restrictive umask, a REPL/notebook caller, a sandboxed environment
        without `sys.executable`, ...) - any of them lands here the same way.
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = str(Path(tmp_dir) / "tedapi_rsa_private.pem")

            with (
                mock.patch(
                    "tesla_fleet_api.tesla.tesla.asyncio.create_subprocess_exec",
                    side_effect=OSError("boom"),
                ),
                self.assertLogs("tesla_fleet_api", level="WARNING") as logs,
            ):
                key = await Tesla().get_rsa_private_key(path, key_size=1024)

            self.assertIsInstance(key, rsa.RSAPrivateKey)
            mode = stat.S_IMODE(Path(path).stat().st_mode)
            self.assertEqual(mode, 0o600)
            self.assertTrue(
                any("isolated subprocess" in message for message in logs.output)
            )

    async def test_subprocess_nonzero_exit_falls_back_to_in_process_generation(
        self,
    ) -> None:
        """A subprocess that launches but exits non-zero also falls back."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = str(Path(tmp_dir) / "tedapi_rsa_private.pem")

            class _FailingProc:
                returncode = 1

                async def communicate(self) -> tuple[bytes, bytes]:
                    return b"", b"boom"

            async def fake_create_subprocess_exec(
                *args: object, **kwargs: object
            ) -> _FailingProc:
                return _FailingProc()

            with (
                mock.patch(
                    "tesla_fleet_api.tesla.tesla.asyncio.create_subprocess_exec",
                    side_effect=fake_create_subprocess_exec,
                ),
                self.assertLogs("tesla_fleet_api", level="WARNING") as logs,
            ):
                key = await Tesla().get_rsa_private_key(path, key_size=1024)

            self.assertIsInstance(key, rsa.RSAPrivateKey)
            mode = stat.S_IMODE(Path(path).stat().st_mode)
            self.assertEqual(mode, 0o600)
            self.assertTrue(
                any("isolated subprocess" in message for message in logs.output)
            )
