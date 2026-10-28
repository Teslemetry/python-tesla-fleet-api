"""Fail-closed environment configuration; no Tesla credentials in MCP arguments."""

import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlsplit

from tesla_fleet_api.const import Region, Scope, is_valid_region

READ_TOOLS = frozenset({"list_vehicles", "get_vehicle_state", "get_location"})
WRITE_TOOLS = frozenset({"wake_vehicle", "navigate_to", "navigate_waypoints"})
VIN_PATTERN = re.compile(r"[A-HJ-NPR-Z0-9]{17}\Z")


@dataclass(frozen=True)
class Config:
    client_id: str
    vins: frozenset[str]
    state_dir: Path
    region: Region = "cn"
    client_secret: str = field(default="", repr=False)
    redirect_uri: str = ""
    tools: frozenset[str] = frozenset({"list_vehicles", "get_vehicle_state"})
    enable_commands: bool = False
    enable_waypoints: bool = False
    private_key: Path | None = None
    bearer_token: str = field(default="", repr=False)
    port: int = 8000

    def __post_init__(self) -> None:
        if not self.client_id or not is_valid_region(self.region):
            raise ValueError("A client ID and valid region are required")
        if not self.vins or any(not VIN_PATTERN.fullmatch(v) for v in self.vins):
            raise ValueError(
                "TESLA_ALLOWED_VINS must contain explicit 17-character VINs"
            )
        if not self.tools <= READ_TOOLS | WRITE_TOOLS:
            raise ValueError("Unknown tool permission")
        if not 1 <= self.port <= 65535:
            raise ValueError("Invalid MCP port")
        if self.redirect_uri:
            url = urlsplit(self.redirect_uri)
            if (
                url.scheme != "https"
                or not url.netloc
                or url.fragment
                or url.query
                or url.username
            ):
                raise ValueError(
                    "Redirect URI must be a registered HTTPS URL without query/fragment"
                )

    @property
    def scopes(self) -> list[Scope]:
        scopes = [Scope.OPENID, Scope.OFFLINE_ACCESS, Scope.VEHICLE_DEVICE_DATA]
        if "get_location" in self.tools:
            scopes.append(Scope.VEHICLE_LOCATION)
        if self.tools & WRITE_TOOLS and self.enable_commands:
            scopes.append(Scope.VEHICLE_CMDS)
        return scopes

    @classmethod
    def from_env(cls) -> "Config":
        region = os.environ.get("TESLA_REGION", "cn")
        if not is_valid_region(region):
            raise ValueError("Invalid TESLA_REGION")
        key = os.environ.get("TESLA_PRIVATE_KEY")
        return cls(
            client_id=os.environ.get("TESLA_CLIENT_ID", ""),
            client_secret=os.environ.get("TESLA_CLIENT_SECRET", ""),
            redirect_uri=os.environ.get("TESLA_REDIRECT_URI", ""),
            region=region,
            vins=frozenset(
                v.strip()
                for v in os.environ.get("TESLA_ALLOWED_VINS", "").split(",")
                if v.strip()
            ),
            state_dir=Path(os.environ.get("TESLA_STATE_DIR", ".tesla-mcp")).absolute(),
            tools=frozenset(
                t.strip()
                for t in os.environ.get(
                    "TESLA_TOOLS", "list_vehicles,get_vehicle_state"
                ).split(",")
                if t.strip()
            ),
            enable_commands=os.environ.get("TESLA_ENABLE_COMMANDS") == "true",
            enable_waypoints=os.environ.get("TESLA_ENABLE_WAYPOINTS") == "true",
            private_key=Path(key) if key else None,
            bearer_token=os.environ.get("MCP_BEARER_TOKEN", ""),
            port=int(os.environ.get("MCP_PORT", "8000")),
        )
