"""Tesla Fleet API for Python."""

import base64
import asyncio
import os
import sys
import time
from os.path import exists
import aiofiles

from tesla_fleet_api.const import LOGGER
from tesla_fleet_api.tesla.charging import Charging
from tesla_fleet_api.tesla.energysite import EnergySites
from tesla_fleet_api.tesla.partner import Partner
from tesla_fleet_api.tesla.user import User
from tesla_fleet_api.tesla.vehicle.vehicles import Vehicles

# cryptography
from cryptography.hazmat.primitives.asymmetric import ec, rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

_KEY_READ_RETRY_TIMEOUT = 1.0
_KEY_READ_RETRY_INTERVAL = 0.05


def _generate_rsa_private_key_pem(key_size: int) -> bytes:
    """Generate an RSA key and serialize it.

    cryptography's RSA keygen holds the GIL for its full duration, so a
    thread (unlike a separate process) would still stall the caller's event
    loop; used both as the isolated subprocess's script body and as the
    in-process fallback.
    """
    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size,
        backend=default_backend(),
    )
    return key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    )


_RSA_KEYGEN_SUBPROCESS_SCRIPT = """
import sys
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

key = rsa.generate_private_key(
    public_exponent=65537, key_size=int(sys.argv[1]), backend=default_backend()
)
sys.stdout.buffer.write(
    key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    )
)
"""


async def _generate_rsa_private_key_pem_isolated(key_size: int) -> bytes:
    """Generate an RSA key's PEM in a plain, short-lived `sys.executable -c ...` subprocess.

    Unlike `multiprocessing`, a plain subprocess's `-c` script is its own
    `__main__` - it never re-imports the caller's actual entry point, so
    there is nothing to guard, nothing to pickle, no semaphore to create, and
    no daemonic-process restriction. `asyncio.create_subprocess_exec` is
    awaited natively, off the loop by construction, including cancellation:
    killing and awaiting the child's exit are both async, so cancelling the
    caller can't block the loop either. Raises on any exec or non-zero-exit
    failure, so the caller can fall back to in-process generation.
    """
    proc = await asyncio.create_subprocess_exec(
        sys.executable,
        "-c",
        _RSA_KEYGEN_SUBPROCESS_SCRIPT,
        str(key_size),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        stdout, stderr = await proc.communicate()
    except asyncio.CancelledError:
        proc.kill()
        await proc.wait()
        raise
    if proc.returncode != 0:
        raise RuntimeError(
            f"RSA key generation subprocess exited with code {proc.returncode}: "
            f"{stderr.decode(errors='replace').strip()}"
        )
    return stdout


async def _generate_rsa_private_key(key_size: int) -> tuple[rsa.RSAPrivateKey, bytes]:
    """Generate an RSA key and return it with its PEM.

    Prefers a short-lived subprocess so keygen - which holds the GIL for its
    full duration, unlike a thread - never stalls the caller's event loop.
    Falls back to in-process generation, which does block the loop, whenever
    that subprocess can't be used - the same environments this method could
    already generate keys in before process isolation was introduced. The
    fallback catches any exception from launching or running the subprocess,
    deliberately not enumerated by type, since process isolation is
    best-effort here and any way it can fail should degrade to the working
    (if blocking) legacy path rather than propagate.
    """
    try:
        pem = await _generate_rsa_private_key_pem_isolated(key_size)
    except Exception as err:
        LOGGER.warning(
            "RSA key generation could not use an isolated subprocess "
            "(%s: %s); falling back to in-process generation, which will "
            "block the event loop for the duration of key generation.",
            type(err).__name__,
            err,
        )
        pem = await asyncio.to_thread(_generate_rsa_private_key_pem, key_size)
    value = await asyncio.to_thread(
        serialization.load_pem_private_key,
        pem,
        password=None,
        backend=default_backend(),
    )
    if not isinstance(value, rsa.RSAPrivateKey):
        raise AssertionError("Generated key is not an RSAPrivateKey")
    return value, pem


def _owner_only_opener(file: str, flags: int) -> int:
    """Open a new file exclusively, born at mode 0o600 with no chmod window."""
    fd = os.open(file, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        fchmod = getattr(os, "fchmod", None)
        if fchmod is not None:
            fchmod(fd, 0o600)
        else:
            os.chmod(file, 0o600)
    except OSError:
        os.close(fd)
        raise
    return fd


async def _load_pem_private_key(path: str, retry_invalid: bool = False) -> object:
    deadline = time.monotonic() + _KEY_READ_RETRY_TIMEOUT
    while True:
        async with aiofiles.open(path, "rb") as key_file:
            key_data = await key_file.read()
        try:
            return serialization.load_pem_private_key(
                key_data, password=None, backend=default_backend()
            )
        except ValueError:
            if not retry_invalid or time.monotonic() >= deadline:
                raise
            await asyncio.sleep(_KEY_READ_RETRY_INTERVAL)


class Tesla:
    """Base class describing interactions with Tesla products."""

    Charging = Charging
    EnergySites = EnergySites
    Partner = Partner
    User = User
    Vehicles = Vehicles

    private_key: ec.EllipticCurvePrivateKey | None = None
    rsa_private_key: rsa.RSAPrivateKey | None = None

    async def get_private_key(
        self, path: str = "private_key.pem"
    ) -> ec.EllipticCurvePrivateKey:
        """Get or create the private key.

        The private key is stored as an unencrypted PEM file. A newly created
        key file is opened with O_EXCL so it is born at mode 0o600 with no
        world-readable window. If another process wins the create race, its
        file is read instead of raising.
        """
        if not exists(path):
            self.private_key = ec.generate_private_key(
                ec.SECP256R1(), default_backend()
            )
            pem = self.private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption(),
            )
            try:
                async with aiofiles.open(
                    path, "wb", opener=_owner_only_opener
                ) as key_file:
                    await key_file.write(pem)
                return self.private_key
            except FileExistsError:
                value = await _load_pem_private_key(path, retry_invalid=True)
                if not isinstance(value, ec.EllipticCurvePrivateKey):
                    raise AssertionError("Loaded key is not an EllipticCurvePrivateKey")
                self.private_key = value
                return self.private_key

        try:
            value = await _load_pem_private_key(path, retry_invalid=True)
        except FileNotFoundError:
            raise FileNotFoundError(f"Private key file not found at {path}")
        except PermissionError:
            raise PermissionError(f"Permission denied when trying to read {path}")

        if not isinstance(value, ec.EllipticCurvePrivateKey):
            raise AssertionError("Loaded key is not an EllipticCurvePrivateKey")
        self.private_key = value
        return self.private_key

    @property
    def has_private_key(self) -> bool:
        """Check if the private key has been set."""
        return self.private_key is not None

    @property
    def public_pem(self) -> str:
        """Get the public key in PEM format."""
        if self.private_key is None:
            raise ValueError("Private key is not set")
        return (
            self.private_key.public_key()
            .public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )
            .decode("utf-8")
        )

    @property
    def public_uncompressed_point(self) -> str:
        """Get the public key in uncompressed point format."""
        if self.private_key is None:
            raise ValueError("Private key is not set")
        return (
            self.private_key.public_key()
            .public_bytes(
                encoding=serialization.Encoding.X962,
                format=serialization.PublicFormat.UncompressedPoint,
            )
            .hex()
        )

    async def get_rsa_private_key(
        self, path: str = "tedapi_rsa_private.pem", key_size: int = 4096
    ) -> rsa.RSAPrivateKey:
        """Get or create an RSA private key for energy gateway client registration.

        The default 4096-bit key matches the format expected by the Powerwall
        TEDapi v1r LAN protocol. The private key is stored as an unencrypted
        PEM file. A newly created key file is opened with O_EXCL so it is born
        at mode 0o600 with no world-readable window. If another process wins
        the create race, its file is read instead of raising.
        """
        if not exists(path):
            value, pem = await _generate_rsa_private_key(key_size)
            self.rsa_private_key = value
            try:
                async with aiofiles.open(
                    path, "wb", opener=_owner_only_opener
                ) as key_file:
                    await key_file.write(pem)
                return self.rsa_private_key
            except FileExistsError:
                value = await _load_pem_private_key(path, retry_invalid=True)
                if not isinstance(value, rsa.RSAPrivateKey):
                    raise AssertionError("Loaded key is not an RSAPrivateKey")
                self.rsa_private_key = value
                return self.rsa_private_key

        value = await _load_pem_private_key(path, retry_invalid=True)
        if not isinstance(value, rsa.RSAPrivateKey):
            raise AssertionError("Loaded key is not an RSAPrivateKey")
        self.rsa_private_key = value
        return self.rsa_private_key

    @property
    def has_rsa_private_key(self) -> bool:
        """Check if the RSA private key has been set."""
        return self.rsa_private_key is not None

    @property
    def rsa_public_der_pkcs1(self) -> bytes:
        """Return the RSA public key in DER PKCS1 format.

        This is the format the Tesla energy gateway expects when
        registering an authorized client.
        """
        if self.rsa_private_key is None:
            raise ValueError("RSA private key is not set")
        return self.rsa_private_key.public_key().public_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PublicFormat.PKCS1,
        )

    @property
    def rsa_public_der_pkcs1_b64(self) -> str:
        """Return the RSA public key in base64-encoded DER PKCS1 format."""
        return base64.b64encode(self.rsa_public_der_pkcs1).decode("ascii")

    @property
    def rsa_public_pem(self) -> str:
        """Get the RSA public key in PEM (SubjectPublicKeyInfo) format."""
        if self.rsa_private_key is None:
            raise ValueError("RSA private key is not set")
        return (
            self.rsa_private_key.public_key()
            .public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )
            .decode("utf-8")
        )
