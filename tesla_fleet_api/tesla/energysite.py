from __future__ import annotations

import asyncio
import base64
import binascii
import math
from typing import TYPE_CHECKING, Any

from google.protobuf.message import DecodeError
from tesla_protocol.energy_device import transport_pb2

from tesla_fleet_api.const import (
    AuthorizedClientKeyType,
    AuthorizedClientType,
    EnergyDeviceIdentifierType,
    EnergyExportMode,
    EnergyIslandMode,
    EnergyOperationMode,
    Method,
    TeslaEnergyPeriod,
)
from tesla_fleet_api.exceptions import (
    DeviceUnexpectedResponse,
    InvalidCommand,
    SignedCommandRequired,
)
from tesla_fleet_api.tesla.energy_signing import EnergyDeviceSigner

if TYPE_CHECKING:
    from cryptography.hazmat.primitives.asymmetric import rsa

    from tesla_fleet_api.tesla.fleet import TeslaFleetApi

# The only device commands Tesla's cloud accepts unsigned: the reads a gateway
# answers before any key is paired. Unsigned, every other command was refused
# with HTTP 400 live on a Powerwall 3 (2026-10-29), and signed, each one
# reached the gateway. A site with a signing key signs everything else.
UNSIGNED_DEVICE_COMMANDS = frozenset(
    {
        ("common", "get_system_info_request"),
        ("common", "get_networking_status_request"),
        ("authorization", "get_signed_commands_public_key_request"),
        ("authorization", "list_authorized_clients_request"),
    }
)

# Upper bound on a ``dispatch_battery_power`` setpoint duration (one day),
# matching aiopowerwall's local ``dispatch_battery_power``.
MAX_DISPATCH_DURATION_SECONDS = 86400


def validate_dispatch_battery_power(power_watts: float, duration_seconds: int) -> None:
    """Raise ``ValueError`` on a non-finite power or an out-of-range duration."""
    if not math.isfinite(power_watts):
        raise ValueError("power_watts must be a finite number")
    if type(duration_seconds) is not int or not (
        1 <= duration_seconds <= MAX_DISPATCH_DURATION_SECONDS
    ):
        raise ValueError(
            "duration_seconds must be an integer from 1 to "
            f"{MAX_DISPATCH_DURATION_SECONDS}"
        )


# google.rpc.Code UNIMPLEMENTED: the gateway firmware has no handler.
_UNIMPLEMENTED = 12


def _raise_on_error_response(result: dict[str, Any]) -> None:
    """Raise if a ``device_command`` reply holds ``common.error_response``.

    The gateway refuses a command inside an HTTP 200 reply, for example code
    11 (OUT_OF_RANGE) on a dispatch above its power limit. Code 12 raises
    ``InvalidCommand``; any other code raises ``DeviceUnexpectedResponse``.
    Both carry ``{"code", "message"}`` as ``data``. A reply without
    decodable envelope bytes is left alone.
    """
    response = result.get("response")
    if not isinstance(response, dict):
        return
    encoded = response.get("message_envelope_as_bytes")  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
    if not isinstance(encoded, str):
        return
    envelope = transport_pb2.MessageEnvelope()
    try:
        envelope.ParseFromString(base64.b64decode(encoded, validate=True))
    except (binascii.Error, DecodeError):
        return
    # error_response sits outside CommonMessages' ``message`` oneof.
    if not envelope.common.HasField("error_response"):
        return
    status = envelope.common.error_response.status
    data: dict[str, Any] = {"code": status.code, "message": status.message}
    if status.code == _UNIMPLEMENTED:
        raise InvalidCommand(data)
    raise DeviceUnexpectedResponse(data)


class EnergySite:
    """Class describing the Tesla Fleet API partner endpoints

    Pass ``private_key`` and ``din`` to send client-signed device commands
    through the cloud ``device_command`` endpoint. With a key, every device
    command is signed except the four pre-pairing reads in
    ``UNSIGNED_DEVICE_COMMANDS``. Without a key, device commands are sent
    unsigned, and Tesla's cloud refuses most of them with 400. The key
    must be an RSA key that is ``VERIFIED`` on this gateway (see
    ``add_authorized_client``), and ``din`` is the gateway DIN (the energy
    site's ``gateway_id`` in ``products``). ``None`` means unsigned: unlike
    vehicles, there is no fallback to the parent's key.
    """

    energy_site_id: int
    din: str | None

    def __init__(
        self,
        parent: TeslaFleetApi,
        energy_site_id: int,
        private_key: rsa.RSAPrivateKey | None = None,
        din: str | None = None,
    ) -> None:
        self._request = parent._request  # pyright: ignore[reportPrivateUsage]
        self.energy_site_id = energy_site_id
        self.din = din
        self._signer: EnergyDeviceSigner | None = None
        if private_key is not None:
            if not din:
                raise ValueError("A signing private_key requires the gateway din.")
            self._signer = EnergyDeviceSigner(private_key)

    # Energy device gRPC commands based on research from
    # https://github.com/jasonacox/pypowerwall (MIT licensed)
    async def _command(
        self,
        category: str,
        command: str,
        params: dict[str, Any] | None = None,
        identifier_type: EnergyDeviceIdentifierType
        | int = EnergyDeviceIdentifierType.GATEWAY_DIN,
    ) -> dict[str, Any]:
        """Send a gRPC command to the energy device gateway.

        With a signing key, this signs every command except the ones in
        ``UNSIGNED_DEVICE_COMMANDS``. Otherwise it sends the unsigned
        ``grpc_command``.
        """
        if (
            self._signer is not None
            and (category, command) not in UNSIGNED_DEVICE_COMMANDS
        ):
            return await self._signed_command(category, command, params)
        return await self._unsigned_command(category, command, params, identifier_type)

    async def _unsigned_command(
        self,
        category: str,
        command: str,
        params: dict[str, Any] | None = None,
        identifier_type: EnergyDeviceIdentifierType
        | int = EnergyDeviceIdentifierType.GATEWAY_DIN,
    ) -> dict[str, Any]:
        """Send an unsigned ``grpc_command`` to the energy device gateway."""
        message: dict[str, Any] = {category: {command: params or {}}}
        return await self._request(
            Method.POST,
            f"api/1/energy_sites/{self.energy_site_id}/command",
            json={
                "command_type": "grpc_command",
                "command_properties": {
                    "message": message,
                    "identifier_type": int(identifier_type),
                },
            },
        )

    def _device_command_body(
        self,
        routable_message: bytes,
        target_id: str,
        identifier_type: EnergyDeviceIdentifierType | int,
    ) -> dict[str, Any]:
        """Build the flat ``device_command`` body around a signed message."""
        return {
            "identifier_type": int(identifier_type),
            "routable_message": base64.b64encode(routable_message).decode("ascii"),
            "target_id": target_id,
        }

    async def _device_command(
        self,
        routable_message: bytes,
        target_id: str,
        identifier_type: EnergyDeviceIdentifierType
        | int = EnergyDeviceIdentifierType.GATEWAY_DIN,
    ) -> dict[str, Any]:
        """Send a signed ``RoutableMessage`` to the energy device.

        Tesla requires the body wrapped in ``data`` and ``identifier_type`` as
        an integer. The reply is returned unchanged; :meth:`_signed_command`
        checks it for a gateway error.
        """
        return await self._request(
            Method.POST,
            f"api/1/energy_sites/{self.energy_site_id}/device_command",
            json={
                "data": self._device_command_body(
                    routable_message, target_id, identifier_type
                )
            },
        )

    async def _signed_command(
        self,
        category: str,
        command: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Sign a gRPC command with the constructor key and send it to the gateway.

        Takes the same arguments as :meth:`_command`. Raises
        ``SignedCommandRequired`` when the site has no signing key. A resend
        of the same signed bytes inside the TTL executes again, so this never
        retries. Raises as :func:`_raise_on_error_response` does when the
        gateway refuses the command.
        """
        signer, din = self._signer, self.din
        if signer is None or din is None:
            raise SignedCommandRequired
        envelope = signer.envelope(din, category, command, params)
        # RSA-4096 with SHA-512 takes about 10 ms; keep it off the event loop.
        routable_message = await asyncio.to_thread(signer.sign, envelope, din)
        result = await self._device_command(routable_message, din)
        _raise_on_error_response(result)
        return result

    async def get_system_info(self) -> dict[str, Any]:
        """Get energy device system information including firmware version, device type, part number, serial number, and DIN."""
        return await self._command("common", "get_system_info_request")

    async def raw_networking_status(self) -> dict[str, Any]:
        """Get raw energy device networking status including WiFi, Ethernet, and cellular connectivity."""
        return await self._command("common", "get_networking_status_request")

    async def get_networking_status(self) -> dict[str, Any]:
        """Get energy device networking status including WiFi, Ethernet, and cellular connectivity."""
        result = await self.raw_networking_status()
        return (
            result.get("response", {})
            .get("message", {})
            .get("Payload", {})
            .get("Common", {})
            .get("Message", {})
            .get("GetNetworkingStatusResponse", {})
        )

    async def wifi_scan(self) -> dict[str, Any]:
        """Scan for available WiFi networks from the energy gateway."""
        return await self._command("common", "wifi_scan_request")

    async def get_device_cert(self) -> dict[str, Any]:
        """Get the energy device certificate including subject, issuer, and validity."""
        return await self._command("common", "device_cert_request")

    async def get_cellular_info(self) -> dict[str, Any]:
        """Get cellular modem information from the energy gateway including the embedded SIM identifier (EID) and supported cellular profiles."""
        return await self._command("common", "get_cellular_info_request")

    async def check_for_update(self) -> dict[str, Any]:
        """Check if a firmware update is available for the energy gateway."""
        return await self._command("common", "check_for_update_request")

    async def check_for_update_urgency(self) -> dict[str, Any]:
        """Check the urgency level of any available firmware update for the energy gateway."""
        return await self._command("common", "check_for_update_urgency_request")

    async def check_internet(self) -> dict[str, Any]:
        """Test internet connectivity on the energy gateway across all network interfaces (WiFi, Ethernet, GSM)."""
        return await self._command("common", "check_internet_request")

    async def set_local_site_config(
        self, params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Update local site configuration on the energy gateway.

        Accepts raw protobuf request fields. This writes gateway
        configuration and is an undocumented energy device gRPC command.
        """
        return await self._command("common", "set_local_site_config_request", params)

    async def list_authorized_clients(self) -> dict[str, Any]:
        """List authorized clients (paired keys) on the energy gateway including their roles and state."""
        return await self._command("authorization", "list_authorized_clients_request")

    async def add_authorized_client(
        self,
        public_key: bytes | str,
        description: str = "Powerwall LAN Client",
        key_type: AuthorizedClientKeyType | int = AuthorizedClientKeyType.RSA,
        authorized_client_type: AuthorizedClientType
        | int = AuthorizedClientType.CUSTOMER_MOBILE_APP,
    ) -> dict[str, Any]:
        """Register an authorized client (public key) with the energy gateway.

        Used to pair a local key with a Powerwall so it can be used for the
        LAN TEDapi v1r protocol. The public key encoding is per ``key_type``:
        RSA is raw PKCS1 ``RSAPublicKey`` DER (``Tesla.rsa_public_der_pkcs1``);
        ECC is DER SubjectPublicKeyInfo (SPKI), not a raw X9.62 uncompressed
        point (``Tesla.ec_public_der_spki``) - the gateway rejects a raw
        point with an asn1 structure error. Do not offer ECC as an
        alternative to RSA for TEDapi v1r signing: a fully VERIFIED ECC key
        cannot authenticate that protocol (its ``SignatureData`` oneof has no
        ECDSA member), even though ECC registers and lists back fine.

        After registration the key is PENDING_VERIFICATION until the
        gateway confirms it within a ~9-minute presence-proof window, a
        physical breaker toggle (verified in as little as 59s) - no
        cloud auto-verify was observed. A window that elapses without
        confirmation moves the key to the terminal
        PENDING_VERIFICATION_TIMEOUT state - see ``AuthorizedClientState``;
        a register-then-poll helper must surface that state rather than
        wait indefinitely. Re-registering the same public key resets the
        window without creating a second record, and is the correct retry
        for a missed window. Verify readiness with a signed local read
        through the paired LAN client; ``list_authorized_clients`` is only a
        secondary, best-effort cloud check.

        Args:
            public_key: The public key to register. Either raw DER bytes in
                the encoding matching ``key_type`` (which will be
                base64-encoded), or an already base64-encoded string.
            description: Human-readable description of the client.
            key_type: The type of key being registered (default RSA).
            authorized_client_type: The authorized client type (default
                CUSTOMER_MOBILE_APP for LAN clients).
        """
        if isinstance(public_key, bytes):
            public_key_b64 = base64.b64encode(public_key).decode("ascii")
        else:
            public_key_b64 = public_key
        params: dict[str, Any] = {
            "key_type": int(key_type),
            "public_key": public_key_b64,
            "authorized_client_type": int(authorized_client_type),
            "description": description,
        }
        if self._signer is not None:
            # The signed envelope is parsed against the proto, which names
            # this field ``type``.
            params["type"] = params.pop("authorized_client_type")
        return await self._command(
            "authorization", "add_authorized_client_request", params
        )

    async def remove_authorized_client(self, public_key: bytes | str) -> dict[str, Any]:
        """Remove an authorized client (public key) from the energy gateway.

        [UNVERIFIED]: removal was live-verified only over the local v1r
        transport; this Fleet-API ``_command`` route is inferred from
        ``add_authorized_client`` using the same mechanism and has not been
        confirmed against hardware. The response message is empty, so
        callers must not assert on response fields - some firmware may
        return no body at all.

        Security note: unlike adding a client, removal requires no physical
        presence proof - an authenticated session is sufficient, including
        to remove a VERIFIED record. Any paired key can therefore revoke
        every other key, including the owner's.

        Args:
            public_key: The public key to remove, exactly as reported by
                ``list_authorized_clients`` - either raw DER bytes (which
                will be base64-encoded) or an already base64-encoded string,
                so a listed record round-trips to removal with no
                re-encoding.
        """
        if isinstance(public_key, bytes):
            public_key_b64 = base64.b64encode(public_key).decode("ascii")
        else:
            public_key_b64 = public_key
        return await self._command(
            "authorization",
            "remove_authorized_client_request",
            {"public_key": public_key_b64},
        )

    async def get_signed_commands_public_key(self) -> dict[str, Any]:
        """Get the energy gateway's public key for signed commands."""
        return await self._command(
            "authorization", "get_signed_commands_public_key_request"
        )

    async def get_backup_events(self) -> dict[str, Any]:
        """Get backup events from the energy gateway. May timeout on some firmware versions."""
        return await self._command("teg", "get_backup_events_request")

    async def schedule_backup_event(
        self,
        start_time: str | None = None,
        duration_seconds: int | None = None,
        priority: int | None = None,
    ) -> dict[str, Any]:
        """Schedule a manual backup event on the energy gateway.

        Args:
            start_time: ISO 8601 timestamp for when the backup event should start.
            duration_seconds: Duration of the backup event in seconds.
            priority: Priority level for the backup event.
        """
        params: dict[str, Any] = {}
        if (
            start_time is not None
            or duration_seconds is not None
            or priority is not None
        ):
            scheduling_info: dict[str, Any] = {}
            if start_time is not None:
                scheduling_info["start_time"] = start_time
            if duration_seconds is not None:
                scheduling_info["duration_seconds"] = duration_seconds
            if priority is not None:
                scheduling_info["priority"] = priority
            params["scheduling_info"] = scheduling_info
        return await self._command(
            "teg", "schedule_manual_backup_event_request", params or None
        )

    async def cancel_backup_event(self) -> dict[str, Any]:
        """Cancel a scheduled manual backup event on the energy gateway."""
        return await self._command("teg", "cancel_manual_backup_event_request")

    async def get_teg_config(self) -> dict[str, Any]:
        """Get Tesla Energy Gateway configuration from the TEG service."""
        return await self._command("teg", "get_config_request")

    async def dispatch_battery_power(
        self, power_watts: float, duration_seconds: int
    ) -> dict[str, Any]:
        """Request a timed battery power setpoint on the energy gateway.

        Sends ``teg.dispatch_battery_power_request.real_power``.
        ``power_watts`` is battery power in watts: **positive discharges,
        negative charges**. The gateway holds the setpoint for
        ``duration_seconds`` (1 to 86400) and then returns to its configured
        operating mode by itself. A new call replaces an active setpoint.

        Keep durations short and re-send to renew, so a caller that stops
        cannot leave the battery on a stale setpoint. Call
        :meth:`resume_battery_operation` to release early. The reply is an
        empty acknowledgement, not readback. A setpoint was seen to discharge
        below the backup reserve and to export with export set to
        ``pv_only``/``never``. The gateway refuses (it does not clamp) a
        request above its power limit, seen at 10,000 W: the signed path
        raises ``DeviceUnexpectedResponse`` with code 11.

        Tesla's cloud refuses this command unsigned (HTTP 400), so it acts
        only on a site built with a signing key.

        Same name, arguments, units, sign and limits as aiopowerwall's local
        ``dispatch_battery_power``, so ``EnergySiteRouter`` can send it on
        either path. Raises ``ValueError`` before any request on a
        non-finite ``power_watts`` or an out-of-range ``duration_seconds``.
        """
        validate_dispatch_battery_power(power_watts, duration_seconds)
        return await self._command(
            "teg",
            "dispatch_battery_power_request",
            {
                "real_power": {
                    "power_watts": float(power_watts),
                    "duration_seconds": duration_seconds,
                }
            },
        )

    async def resume_battery_operation(self) -> dict[str, Any]:
        """Release a :meth:`dispatch_battery_power` setpoint.

        Sends ``teg.dispatch_battery_power_request.resume_device_mode``; the
        gateway goes back to its configured operating mode. The gateway also
        acknowledges it when no setpoint is active. Like
        :meth:`dispatch_battery_power`, it acts only on a site with a signing
        key.
        """
        return await self._command(
            "teg",
            "dispatch_battery_power_request",
            {"resume_device_mode": {}},
        )

    async def set_island_mode(
        self,
        mode: EnergyIslandMode | int,
        force: bool | None = None,
    ) -> dict[str, Any]:
        """Set the island mode on the energy gateway.

        Signed only: gateways have been observed accepting the unsigned
        ``grpc_command`` without physically operating the grid contactor.
        With a signing key this sends ``teg.set_island_mode_request`` signed
        through ``device_command``. Without one it raises
        ``SignedCommandRequired`` before any request. For a signed local LAN
        path, compose an aiopowerwall local backend with ``EnergySiteRouter``.

        A success-shaped reply does not prove the contactor moved: confirm
        ``island_status`` with a status read before relying on it.

        Args:
            mode: ``EnergyIslandMode.OFF_GRID`` (6) or ``ON_GRID`` (1).
            force: Sent when not ``None``. Some gateways need ``True`` to
                   open the contactor.
        """
        params: dict[str, Any] = {"mode": int(mode)}
        if force is not None:
            params["force"] = force
        return await self._signed_command("teg", "set_island_mode_request", params)

    async def go_off_grid(self) -> dict[str, Any]:
        """Request off-grid mode, with ``force=True`` as aiopowerwall does.

        Signed only - see ``set_island_mode``.
        """
        return await self.set_island_mode(EnergyIslandMode.OFF_GRID, force=True)

    async def reconnect_grid(self) -> dict[str, Any]:
        """Request on-grid mode.

        Signed only - see ``set_island_mode``.
        """
        return await self.set_island_mode(EnergyIslandMode.ON_GRID)

    async def backup(self, backup_reserve_percent: int) -> dict[str, Any]:
        """Adjust the site's backup reserve."""
        return await self._request(
            Method.POST,
            f"api/1/energy_sites/{self.energy_site_id}/backup",
            json={"backup_reserve_percent": backup_reserve_percent},
        )

    async def backup_history(
        self,
        period: TeslaEnergyPeriod | str | None,
        start_date: str | None = None,
        end_date: str | None = None,
        time_zone: str | None = None,
    ) -> dict[str, Any]:
        """Returns the backup (off-grid) event history of the site in duration of seconds."""
        return await self._request(
            Method.GET,
            f"api/1/energy_sites/{self.energy_site_id}/calendar_history",
            params={
                "kind": "backup",
                "start_date": start_date,
                "end_date": end_date,
                "period": period,
                "time_zone": time_zone,
            },
        )

    async def charge_history(
        self,
        start_date: str,
        end_date: str,
        time_zone: str | None = None,
    ) -> dict[str, Any]:
        """Returns the charging history of a wall connector."""
        return await self._request(
            Method.GET,
            f"api/1/energy_sites/{self.energy_site_id}/telemetry_history",
            params={
                "kind": "charge",
                "start_date": start_date,
                "end_date": end_date,
                "time_zone": time_zone,
            },
        )

    async def energy_history(
        self,
        period: TeslaEnergyPeriod | str | None,
        start_date: str | None = None,
        end_date: str | None = None,
        time_zone: str | None = None,
    ) -> dict[str, Any]:
        """Returns the energy measurements of the site, aggregated to the requested period."""
        return await self._request(
            Method.GET,
            f"api/1/energy_sites/{self.energy_site_id}/calendar_history",
            params={
                "kind": "energy",
                "start_date": start_date,
                "end_date": end_date,
                "period": period,
                "time_zone": time_zone,
            },
        )

    async def grid_import_export(
        self,
        disallow_charge_from_grid_with_solar_installed: bool | None = None,
        customer_preferred_export_rule: EnergyExportMode | str | None = None,
    ) -> dict[str, Any]:
        """Allow/disallow charging from the grid and exporting energy to the grid."""
        return await self._request(
            Method.POST,
            f"api/1/energy_sites/{self.energy_site_id}/grid_import_export",
            json={
                "disallow_charge_from_grid_with_solar_installed": disallow_charge_from_grid_with_solar_installed,
                "customer_preferred_export_rule": customer_preferred_export_rule,
            },
        )

    async def live_status(self) -> dict[str, Any]:
        """Returns the live status of the site (power, state of energy, grid status, storm mode)."""
        return await self._request(
            Method.GET,
            f"api/1/energy_sites/{self.energy_site_id}/live_status",
        )

    async def off_grid_vehicle_charging_reserve(
        self, off_grid_vehicle_charging_reserve_percent: int
    ) -> dict[str, Any]:
        """Adjust the site's off-grid vehicle charging backup reserve."""
        return await self._request(
            Method.POST,
            f"api/1/energy_sites/{self.energy_site_id}/off_grid_vehicle_charging_reserve",
            json={
                "off_grid_vehicle_charging_reserve_percent": off_grid_vehicle_charging_reserve_percent
            },
        )

    async def operation(
        self, default_real_mode: EnergyOperationMode | str
    ) -> dict[str, Any]:
        """Set the site's mode."""
        return await self._request(
            Method.POST,
            f"api/1/energy_sites/{self.energy_site_id}/operation",
            json={"default_real_mode": default_real_mode},
        )

    async def site_info(self) -> dict[str, Any]:
        """Returns information about the site. Things like assets (has solar, etc), settings (backup reserve, etc), and features (storm_mode_capable, etc)."""
        return await self._request(
            Method.GET,
            f"api/1/energy_sites/{self.energy_site_id}/site_info",
        )

    async def storm_mode(self, enabled: bool) -> dict[str, Any]:
        """Update storm watch participation."""
        return await self._request(
            Method.POST,
            f"api/1/energy_sites/{self.energy_site_id}/storm_mode",
            json={"enabled": enabled},
        )

    async def time_of_use_settings(self, settings: dict[str, Any]) -> dict[str, Any]:
        """Update the time of use settings for the energy site."""
        return await self._request(
            Method.POST,
            f"api/1/energy_sites/{self.energy_site_id}/time_of_use_settings",
            json={"tou_settings": {"tariff_content_v2": settings}},
        )


class EnergySites(dict[int, EnergySite]):
    """Class describing the Tesla Fleet API partner endpoints"""

    _parent: TeslaFleetApi
    Site = EnergySite

    def __init__(self, parent: TeslaFleetApi) -> None:
        self._parent = parent

    def create(
        self,
        energy_site_id: int,
        private_key: rsa.RSAPrivateKey | None = None,
        din: str | None = None,
    ) -> EnergySite:
        """Create a specific energy site.

        Pass ``private_key`` and ``din`` to enable client-signed device
        commands; see :class:`EnergySite`.
        """
        self[energy_site_id] = self.Site(
            self._parent, energy_site_id, private_key=private_key, din=din
        )
        return self[energy_site_id]
