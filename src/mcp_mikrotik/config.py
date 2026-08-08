import json
from typing import List, Literal, Optional

from pydantic import BaseModel, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class McpServerSettings(BaseModel):
    transport: Literal["stdio", "sse", "streamable-http"] = "stdio"
    host: str = "0.0.0.0"
    port: int = 8000

    # DNS-rebinding protection for the HTTP transports (sse / streamable-http).
    # Comma-separated allowlists for the Host and Origin request headers. Needed
    # when serving behind a reverse proxy or on a non-localhost host — otherwise
    # requests with an external Host header are rejected with HTTP 421
    # "Invalid Host header". Set allowed_hosts to your domain (e.g.
    # "mcp.example.com"); a value of "*" disables the host check entirely.
    allowed_hosts: str = ""
    allowed_origins: str = ""


class DeviceConfig(BaseModel):
    """A single MikroTik device in the inventory.

    ``title`` is the identifier the LLM uses to target this device; it must be
    unique across the inventory.
    """

    title: str
    host: str
    port: int = 22
    username: str = "admin"
    password: str = ""
    key_filename: Optional[str] = None
    tags: List[str] = []
    region: Optional[str] = None

    @field_validator("title")
    @classmethod
    def _title_not_blank(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("device 'title' must be a non-empty string")
        return v.strip()


class MikrotikConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="MIKROTIK_",
        env_nested_delimiter="__",
        nested_model_default_partial_update=True,
        cli_prog_name="mcp-server-mikrotik",
        cli_kebab_case=True,
    )

    # ── Single-device settings (unchanged; still the default) ───────────────
    host: str = "127.0.0.1"
    username: str = "admin"
    password: str = ""
    port: int = 22
    key_filename: Optional[str] = None
    mcp: McpServerSettings = McpServerSettings()

    # ── Multi-device inventory ─────────────────────────────────────────────
    # Supplied as a JSON array, either inline or from a file:
    #
    #   MIKROTIK_INVENTORY='[{"title":"TitleA","host":"10.0.0.1","tags":["eu"],
    #                         "region":"NL","username":"admin","password":"..."}]'
    #   MIKROTIK_INVENTORY_FILE=/etc/mikrotik/inventory.json
    #
    # In an MCP client config these belong in the server's "env" block — that is
    # the channel a client actually forwards to the spawned process.
    #
    # When left empty, a single-device inventory is synthesised from the flat
    # settings above, so existing single-device setups keep working unchanged.
    inventory: List[DeviceConfig] = []
    inventory_file: Optional[str] = None

    @field_validator("inventory", mode="before")
    @classmethod
    def _parse_inventory(cls, v):
        """Accept a JSON string (env var) as well as a real list."""
        if isinstance(v, str):
            v = v.strip()
            if not v:
                return []
            try:
                v = json.loads(v)
            except json.JSONDecodeError as exc:
                raise ValueError(f"MIKROTIK_INVENTORY is not valid JSON: {exc}") from exc
        if isinstance(v, dict):
            v = [v]
        return v


mikrotik_config = MikrotikConfig()
