from typing import Dict, Literal, Optional

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


class DeviceConnection:
    """Connection parameters for a single MikroTik device."""

    def __init__(self, host: str, username: str = "admin", password: str = "",
                 port: int = 22, key_filename: Optional[str] = None):
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.key_filename = key_filename


class DeviceRegistry:
    """Registry of named MikroTik device connections set during conversation."""

    def __init__(self):
        self._devices: Dict[str, DeviceConnection] = {}
        self._default: Optional[str] = None

    def add(self, name: str, connection: DeviceConnection, make_default: bool = True):
        self._devices[name] = connection
        if make_default or len(self._devices) == 1:
            self._default = name

    def remove(self, name: str) -> bool:
        if name not in self._devices:
            return False
        del self._devices[name]
        if self._default == name:
            self._default = next(iter(self._devices), None)
        return True

    def get(self, name: Optional[str] = None) -> Optional[DeviceConnection]:
        if name is not None:
            return self._devices.get(name)
        if self._default is not None:
            return self._devices.get(self._default)
        return None

    @property
    def default_name(self) -> Optional[str]:
        return self._default

    @default_name.setter
    def default_name(self, name: str):
        if name in self._devices:
            self._default = name

    @property
    def device_names(self) -> list:
        return list(self._devices.keys())

    @property
    def is_empty(self) -> bool:
        return len(self._devices) == 0

    def clear(self):
        self._devices.clear()
        self._default = None


device_registry = DeviceRegistry()
