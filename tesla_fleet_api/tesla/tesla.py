"""Tesla Fleet API for Python."""

import base64
from os.path import exists
import aiofiles

from tesla_fleet_api.tesla.charging import Charging
from tesla_fleet_api.tesla.energysite import EnergySites
from tesla_fleet_api.tesla.partner import Partner
from tesla_fleet_api.tesla.user import User
from tesla_fleet_api.tesla.vehicle.vehicles import Vehicles

# cryptography
from cryptography.hazmat.primitives.asymmetric import ec, rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

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
        """Get or create the private key."""
        if not exists(path):
            self.private_key = ec.generate_private_key(
                ec.SECP256R1(), default_backend()
            )
            # save the key
            pem = self.private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption(),
            )
            async with aiofiles.open(path, "wb") as key_file:
                await key_file.write(pem)
            try:
                from os import chmod

                chmod(path, 0o600)
            except OSError:
                pass
        else:
            try:
                async with aiofiles.open(path, "rb") as key_file:
                    key_data = await key_file.read()
                value = serialization.load_pem_private_key(
                    key_data, password=None, backend=default_backend()
                )
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
        return self.private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ).decode('utf-8')

    @property
    def public_uncompressed_point(self) -> str:
        """Get the public key in uncompressed point format."""
        if self.private_key is None:
            raise ValueError("Private key is not set")
        return self.private_key.public_key().public_bytes(
            encoding=serialization.Encoding.X962,
            format=serialization.PublicFormat.UncompressedPoint,
        ).hex()

    async def get_rsa_private_key(
        self, path: str = "tedapi_rsa_private.pem", key_size: int = 4096
    ) -> rsa.RSAPrivateKey:
        """Get or create an RSA private key for energy gateway client registration.

        The default 4096-bit key matches the format expected by the Powerwall
        TEDapi v1r LAN protocol. The private key is stored as an unencrypted
        PEM file with permissions 0o600 when created.
        """
        if not exists(path):
            self.rsa_private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=key_size,
                backend=default_backend(),
            )
            pem = self.rsa_private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption(),
            )
            async with aiofiles.open(path, "wb") as key_file:
                await key_file.write(pem)
            try:
                from os import chmod

                chmod(path, 0o600)
            except OSError:
                pass
        else:
            async with aiofiles.open(path, "rb") as key_file:
                key_data = await key_file.read()
            value = serialization.load_pem_private_key(
                key_data, password=None, backend=default_backend()
            )
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
        return self.rsa_private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ).decode("utf-8")
