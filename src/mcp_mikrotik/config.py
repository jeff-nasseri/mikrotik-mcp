from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class MikrotikConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="MIKROTIK_",
        cli_prog_name="mcp-server-mikrotik",
        cli_kebab_case=True,
    )

    host: str = "127.0.0.1"
    username: str = "admin"
    password: str = ""
    port: int = 22
    key_filename: Optional[str] = None


mikrotik_config = MikrotikConfig()
