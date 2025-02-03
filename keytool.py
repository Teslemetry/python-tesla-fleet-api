from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec


with open("tesla_private_key.pem", "rb") as key_file:
    key_data = key_file.read()

private_key = serialization.load_pem_private_key(
    key_data, password=None, backend=default_backend()
)

if not isinstance(private_key, ec.EllipticCurvePrivateKey):
    raise AssertionError("Loaded key is not an EllipticCurvePrivateKey")

private_bytes = private_key.private_bytes(
    encoding=serialization.Encoding.DER,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
)
print("PRIVATE",private_bytes.hex())

#with open("private.key", "wb") as f:
#    f.write(private_bytes)

public_bytes = private_key.public_key().public_bytes(
    encoding=serialization.Encoding.X962, format=serialization.PublicFormat.UncompressedPoint
)

print("PUBLIC",public_bytes.hex())

#with open("public.key", "wb") as f:
#    f.write(public_bytes)
