from dataclasses import dataclass
from typing import Optional

@dataclass
class MikrotikConfig:
    host: str = "127.0.0.1"
    username: str = "admin"
    password: str = ""
    key_filename: Optional[str] = None
    port: int = 22

mikrotik_config = MikrotikConfig()
