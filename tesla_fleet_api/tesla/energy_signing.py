"""RSA signing for energy device commands.

One stateless scheme serves both the local TEDapi ``/tedapi/v1r`` endpoint and
Tesla's cloud ``device_command`` endpoint: a ``MessageEnvelope`` is wrapped in a
``RoutableMessage`` signed with RSA PKCS#1 v1.5 / SHA-512 over a TLV header
personalised to the gateway DIN. It matches aiopowerwall's
``V1rTransport._build_signed_request`` byte for byte; the cloud path was proven
live on 2026-09-21 with a 30 second TTL.

There is no session, counter or handshake: the same bytes execute again if
resent before ``expires_at``. Keep the TTL short.
"""

from __future__ import annotations

import math
import struct
import time
import uuid
from typing import Any

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from google.protobuf import json_format
from tesla_protocol.energy_device import (
    authorization_types_pb2,
    signed_message_pb2,
    transport_pb2,
)

# The cloud round trip needs more than aiopowerwall's 12 s LAN TTL; 30 s
# worked live through ``device_command``.
ENERGY_SIGNATURE_TTL_SECONDS = 30


def _tlv(tag: int, value: bytes) -> bytes:
    """Encode one tag-length-value entry."""
    return bytes([tag, len(value)]) + value


class EnergyDeviceSigner:
    """Builds RSA-signed ``RoutableMessage`` bytes for one energy device key.

    The key must be an RSA key registered on the gateway with
    ``add_authorized_client`` and in state ``VERIFIED``. An ECC key cannot sign
    this scheme: the ``SignatureData`` oneof has only ``rsa_data``.
    """

    def __init__(
        self,
        private_key: rsa.RSAPrivateKey,
        ttl: int = ENERGY_SIGNATURE_TTL_SECONDS,
    ) -> None:
        if not isinstance(private_key, rsa.RSAPrivateKey):  # pyright: ignore[reportUnnecessaryIsInstance]
            raise TypeError(
                "Energy device signing requires an RSA private key, "
                f"got {type(private_key).__name__}"
            )
        self._private_key = private_key
        self.public_key_der = private_key.public_key().public_bytes(
            serialization.Encoding.DER, serialization.PublicFormat.PKCS1
        )
        self.ttl = ttl

    @staticmethod
    def envelope(
        din: str,
        category: str,
        command: str,
        params: dict[str, Any] | None = None,
    ) -> bytes:
        """Serialize a ``MessageEnvelope`` addressed to ``din``.

        ``category``, ``command`` and ``params`` are the same proto field names
        ``EnergySite._command`` sends unsigned, so every gRPC helper can be
        signed without per-command code. ``delivery_channel`` stays unset, as in
        the envelope proven on the cloud path.
        """
        envelope = json_format.ParseDict(
            {category: {command: params or {}}}, transport_pb2.MessageEnvelope()
        )
        envelope.sender.authorized_client = (
            authorization_types_pb2.AUTHORIZED_CLIENT_TYPE_CUSTOMER_MOBILE_APP
        )
        envelope.recipient.din = din
        return envelope.SerializeToString()

    def sign(
        self,
        envelope: bytes,
        din: str,
        *,
        now: float | None = None,
        message_uuid: bytes | None = None,
    ) -> bytes:
        """Wrap ``envelope`` in a signed ``RoutableMessage`` and serialize it.

        ``din`` must be the same gateway DIN the envelope and the request
        target. ``now`` and ``message_uuid`` exist for deterministic tests.
        """
        expires_at = math.ceil(time.time() if now is None else now) + self.ttl
        signed_data = b"".join(
            (
                _tlv(
                    signed_message_pb2.TAG_SIGNATURE_TYPE,
                    bytes([signed_message_pb2.SIGNATURE_TYPE_RSA]),
                ),
                _tlv(
                    signed_message_pb2.TAG_DOMAIN,
                    bytes([signed_message_pb2.DOMAIN_ENERGY_DEVICE]),
                ),
                _tlv(signed_message_pb2.TAG_PERSONALIZATION, din.encode("ascii")),
                _tlv(signed_message_pb2.TAG_EXPIRES_AT, struct.pack(">I", expires_at)),
                bytes([signed_message_pb2.TAG_END]),
                envelope,
            )
        )
        signature = self._private_key.sign(
            signed_data, padding.PKCS1v15(), hashes.SHA512()
        )

        routable = signed_message_pb2.RoutableMessage()
        routable.to_destination.domain = signed_message_pb2.DOMAIN_ENERGY_DEVICE
        routable.protobuf_message_as_bytes = envelope
        routable.uuid = message_uuid if message_uuid is not None else uuid.uuid4().bytes
        routable.signature_data.signer_identity.public_key = self.public_key_der
        routable.signature_data.rsa_data.expires_at = expires_at
        routable.signature_data.rsa_data.signature = signature
        return routable.SerializeToString()
