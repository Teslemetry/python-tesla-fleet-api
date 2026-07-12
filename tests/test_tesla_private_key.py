"""``get_private_key``/``get_rsa_private_key`` must create their PEM files atomically.

The keys sign Tesla vehicle commands (Fleet API and BLE) and register with the
Powerwall TEDapi gateway. Both are created via an O_EXCL-opened file at mode
0o600 so there is never a write-then-chmod window where the key is
world-readable, and a losing concurrent creator falls back to reading the
winner's file instead of raising.
"""

from __future__ import annotations

import asyncio
import stat
import os
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
