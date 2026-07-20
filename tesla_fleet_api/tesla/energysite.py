from __future__ import annotations

import base64
from typing import TYPE_CHECKING, Any

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
from tesla_fleet_api.exceptions import SignedCommandRequired

if TYPE_CHECKING:
    from tesla_fleet_api.tesla.fleet import TeslaFleetApi


class EnergySite:
    """Class describing the Tesla Fleet API partner endpoints"""

    energy_site_id: int

    def __init__(self, parent: TeslaFleetApi, energy_site_id: int):
        self._request = parent._request  # pyright: ignore[reportPrivateUsage]
        self.energy_site_id = energy_site_id

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
        """Send a gRPC command to the energy device gateway."""
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

        Used to pair a local key (typically RSA-4096 in DER PKCS1 format) with
        a Powerwall so it can be used for the LAN TEDapi v1r protocol. After
        registration the key may be in PENDING or PENDING_VERIFICATION state
        until the gateway confirms it - see ``AuthorizedClientState``. The
        gateway may auto-verify via cloud, otherwise a physical breaker
        toggle is required to confirm. Verify readiness with a signed local
        read through the paired LAN client; ``list_authorized_clients`` is
        only a secondary, best-effort cloud check.

        Args:
            public_key: The public key to register. Either raw DER PKCS1
                bytes (which will be base64-encoded), or an already
                base64-encoded string.
            description: Human-readable description of the client.
            key_type: The type of key being registered (default RSA).
            authorized_client_type: The authorized client type (default
                CUSTOMER_MOBILE_APP for LAN clients).
        """
        if isinstance(public_key, bytes):
            public_key_b64 = base64.b64encode(public_key).decode("ascii")
        else:
            public_key_b64 = public_key
        return await self._command(
            "authorization",
            "add_authorized_client_request",
            {
                "key_type": int(key_type),
                "public_key": public_key_b64,
                "authorized_client_type": int(authorized_client_type),
                "description": description,
            },
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

    async def set_island_mode(
        self,
        mode: EnergyIslandMode | int,
        force: bool | None = None,
    ) -> dict[str, Any]:
        """Set the island mode on the energy gateway.

        Always raises ``SignedCommandRequired``: this cloud method can only
        send an unsigned ``grpc_command``, and gateways have been observed
        accepting that request without physically operating the grid
        contactor. For a signed local LAN control path, pair an RSA key with
        ``add_authorized_client`` and compose an aiopowerwall local backend
        with ``EnergySiteRouter``.

        Args:
            mode: Unused - the call raises before inspecting it. Kept for
                  signature compatibility.
            force: Unused - the call raises before inspecting it. Kept for
                   signature compatibility.
        """
        raise SignedCommandRequired

    async def go_off_grid(self) -> dict[str, Any]:
        """Request off-grid mode through the cloud ``grpc_command`` path.

        Always raises ``SignedCommandRequired`` - see ``set_island_mode``.
        """
        return await self.set_island_mode(EnergyIslandMode.OFF_GRID)

    async def reconnect_grid(self) -> dict[str, Any]:
        """Request on-grid mode through the cloud ``grpc_command`` path.

        Always raises ``SignedCommandRequired`` - see ``set_island_mode``.
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

    def __init__(self, parent: TeslaFleetApi):
        self._parent = parent

    def create(self, energy_site_id: int) -> EnergySite:
        """Create a specific energy site."""
        self[energy_site_id] = self.Site(self._parent, energy_site_id)
        return self[energy_site_id]
