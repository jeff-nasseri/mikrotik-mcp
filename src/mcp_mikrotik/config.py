from typing import List, Literal, Optional

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class McpServerSettings(BaseModel):
    transport: Literal["stdio", "sse", "streamable-http"] = "stdio"
    host: str = "0.0.0.0"
    port: int = 8000


class DeviceConfig(BaseModel):
    """Represents a single MikroTik device in the fleet inventory."""

    name: str
    host: str
    username: str = "admin"
    password: str = ""
    port: int = 22
    key_filename: Optional[str] = None
    tags: List[str] = []


class MikrotikConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="MIKROTIK_",
        env_nested_delimiter="__",
        nested_model_default_partial_update=True,
        cli_prog_name="mcp-server-mikrotik",
        cli_kebab_case=True,
    )

    # Single-device config (backward-compatible default)
    host: str = "127.0.0.1"
    username: str = "admin"
    password: str = ""
    port: int = 22
    key_filename: Optional[str] = None
    mcp: McpServerSettings = McpServerSettings()

    # Multi-device fleet inventory.
    # Set via MIKROTIK_DEVICES as a JSON array, e.g.:
    #   MIKROTIK_DEVICES='[{"name":"mt-nl-1","host":"1.1.1.1","tags":["nl","eu"]}]'
    devices: List[DeviceConfig] = []


mikrotik_config = MikrotikConfig()
