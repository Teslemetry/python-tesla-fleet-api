"""``get_private_key`` must write its PEM file with owner-only permissions.

The key it creates signs Tesla vehicle commands (Fleet API and BLE) - written
with the process default mode (typically group/world-readable), it leaks
command-signing material to any other local user. ``get_rsa_private_key``
(the TEDapi/Powerwall key created later in the same module) already chmods to
0o600 after writing; this locks ``get_private_key`` into the same contract.
"""

from __future__ import annotations

import stat
import tempfile
from pathlib import Path
from unittest import IsolatedAsyncioTestCase

from tesla_fleet_api.tesla.tesla import Tesla


class GetPrivateKeyPermissionsTests(IsolatedAsyncioTestCase):
    async def test_new_key_file_is_owner_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = str(Path(tmp_dir) / "private_key.pem")
            tesla = Tesla()

            await tesla.get_private_key(path)

            mode = stat.S_IMODE(Path(path).stat().st_mode)
            self.assertEqual(mode, 0o600)
