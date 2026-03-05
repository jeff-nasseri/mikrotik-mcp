from typing import Literal, Optional

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class McpServerSettings(BaseModel):
    transport: Literal["stdio", "sse", "streamable-http"] = "stdio"
    host: str = "0.0.0.0"
    port: int = 8000


class MikrotikConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="MIKROTIK_",
        env_nested_delimiter="__",
        nested_model_default_partial_update=True,
        cli_prog_name="mcp-server-mikrotik",
        cli_kebab_case=True,
    )

    host: Optional[str] = None
    username: str = "admin"
    password: str = ""
    port: int = 22
    key_filename: Optional[str] = None
    mcp: McpServerSettings = McpServerSettings()


mikrotik_config = MikrotikConfig()


class ConnectionState:
    """Holds the active MikroTik device connection parameters set during conversation."""

    def __init__(self):
        self.host: Optional[str] = None
        self.username: Optional[str] = None
        self.password: Optional[str] = None
        self.port: Optional[int] = None
        self.key_filename: Optional[str] = None

    @property
    def is_set(self) -> bool:
        return self.host is not None

    def clear(self):
        self.host = None
        self.username = None
        self.password = None
        self.port = None
        self.key_filename = None


connection_state = ConnectionState()
