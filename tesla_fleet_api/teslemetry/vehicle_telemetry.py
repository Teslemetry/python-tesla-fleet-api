from typing import Any, List, Union

from tesla_fleet_api.teslemetry.const import SnapshotTopic
from tesla_fleet_api.teslemetry.vehicle import TeslemetryVehicle


class TeslemetryVehicleTelemetry():
    """A cursor aware Vehicle Telemetry reader"""

    _parent: TeslemetryVehicle
    _topics: str | None
    cursor: int = 0
    snapshot: dict[str, Any]

    def __init__(
        self,
        parent: TeslemetryVehicle,
        topics: list[SnapshotTopic] | list[str] | str | None = None,
    ) -> None:
        self._parent = parent
        self._topics = ";".join(topics) if isinstance(topics, list) else topics
        self.snapshot = {}

    async def update(self) -> dict[str, Any]:
        """Returns the public key associated with the user."""
        update = await self._parent.telemetry(self._topics, self.cursor)
        self.cursor = update["cursor"]
        if update.get("state"):
            self.snapshot["state"] = update["state"]
        if update.get("data"):
            self.snapshot.setdefault("data", {})
            for field, data in update["data"].items():
                self.snapshot["data"][field] = data
        if update.get("connectivity"):
            self.snapshot["connectivity"] = update["connectivity"]
        if update.get("alerts"):
            self.snapshot["alerts"] = update["alerts"]
        if update.get("errors"):
            self.snapshot["errors"] = update["errors"]
        if update.get("vehicle_data"):
            self.snapshot["vehicle_data"] = update["vehicle_data"]
        return update
