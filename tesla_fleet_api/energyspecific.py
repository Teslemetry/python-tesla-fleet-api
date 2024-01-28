from typing import Any


class EnergySpecific:
    """Class describing the Tesla Fleet API partner endpoints"""

    def __init__(
        self,
        parent,
        energy_site_id: int,
    ):
        self._parent = parent
        self.energy_site_id = energy_site_id

    async def backup(self, backup_reserve_percent: int) -> dict[str, Any]:
        """Adjust the site's backup reserve."""
        return await self._parent.backup(
            self.energy_site_id,
            data={"backup_reserve_percent": backup_reserve_percent},
        )

    async def backup_history(
        self,
        kind: str,
        start_date: str,
        end_date: str,
        period: str,
        time_zone: str,
    ) -> dict[str, Any]:
        """Returns the backup (off-grid) event history of the site in duration of seconds."""
        return await self._parent.backup_history(
            self.energy_site_id, kind, start_date, end_date, period, time_zone
        )

    async def charge_history(
        self,
        kind: str,
        start_date: str,
        end_date: str,
        time_zone: str,
    ) -> dict[str, Any]:
        """Returns the charging history of a wall connector."""
        return await self._parent.charge_history(
            self.energy_site_id,
            kind,
            start_date,
            end_date,
            time_zone,
        )

    async def energy_history(
        self,
        kind: str,
        start_date: str,
        end_date: str,
        period: str,
        time_zone: str,
    ) -> dict[str, Any]:
        """Returns the energy measurements of the site, aggregated to the requested period."""
        return await self._parent.energy_history(
            self.energy_site_id,
            kind,
            start_date,
            end_date,
            period,
            time_zone,
        )

    async def grid_import_export(
        self,
        disallow_charge_from_grid_with_solar_installed: bool,
        customer_preferred_export_rule: str,
    ) -> dict[str, Any]:
        """Allow/disallow charging from the grid and exporting energy to the grid."""
        return await self._parent.grid_import_export(
            self.energy_site_id,
            disallow_charge_from_grid_with_solar_installed,
            customer_preferred_export_rule,
        )

    async def live_status(self) -> dict[str, Any]:
        """Returns the live status of the site (power, state of energy, grid status, storm mode)."""
        return await self._parent.live_status(self.energy_site_id)

    async def off_grid_vehicle_charging_reserve(
        self, off_grid_vehicle_charging_reserve_percent: int
    ) -> dict[str, Any]:
        """Adjust the site's off-grid vehicle charging backup reserve."""
        return await self._parent.off_grid_vehicle_charging_reserve(
            self.energy_site_id, off_grid_vehicle_charging_reserve_percent
        )

    async def operation(self, default_real_mode: str) -> dict[str, Any]:
        """Set the site's mode."""
        return await self._parent.operation(
            self.energy_site_id,
            default_real_mode,
        )

    async def site_info(self) -> dict[str, Any]:
        """Returns information about the site. Things like assets (has solar, etc), settings (backup reserve, etc), and features (storm_mode_capable, etc)."""
        return await self._parent.site_info()

    async def storm_mode(self, enabled: bool) -> dict[str, Any]:
        """Update storm watch participation."""
        return await self._parent.storm_mode(
            self.energy_site_id,
            enabled,
        )
