from tesla_fleet_api.const import StrEnum

class SnapshotTopic(StrEnum):
    """Telemetry Topics in snapshots"""

    STATE = "state"
    DATA = "data"
    CONNECTIVITY = "connectivity"
    ALERTS = "alerts"
    ERRORS = "errors"
    VEHICLE_DATA = "vehicle_data"

class WaitTopic(StrEnum):
    """Telemetry Topics which can be awaited"""

    STATE = "state"
    DATA = "data"
    CONNECTIVITY = "connectivity"
    ALERTS = "alerts"
    ERRORS = "errors"
