"""Tesla Fleet API for Python."""

from os.path import exists
import aiofiles

from tesla_fleet_api.tesla.charging import Charging
from tesla_fleet_api.tesla.energysite import EnergySites
from tesla_fleet_api.tesla.partner import Partner
from tesla_fleet_api.tesla.user import User
from tesla_fleet_api.tesla.vehicle.vehicles import Vehicles

# cryptography
from cryptography.hazmat.primitives.asymmetric import ec
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
