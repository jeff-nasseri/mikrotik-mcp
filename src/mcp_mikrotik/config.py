from typing import Literal, Optional

from pydantic import BaseModel
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


class MikrotikConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="MIKROTIK_",
        env_nested_delimiter="__",
        nested_model_default_partial_update=True,
        cli_prog_name="mcp-server-mikrotik",
        cli_kebab_case=True,
    )

    host: str = "127.0.0.1"
    username: str = "admin"
    password: str = ""
    port: int = 22
    key_filename: Optional[str] = None
    mcp: McpServerSettings = McpServerSettings()


mikrotik_config = MikrotikConfig()
