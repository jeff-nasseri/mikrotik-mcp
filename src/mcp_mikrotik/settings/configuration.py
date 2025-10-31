import os
from dataclasses import dataclass

DEFAULT_MIKROTIK_HOST = "127.0.0.1"
DEFAULT_MIKROTIK_USER = "admin"
DEFAULT_MIKROTIK_PASS = ""


@dataclass
class MikrotikConfig:
    host: str = os.getenv("MIKROTIK_HOST", DEFAULT_MIKROTIK_HOST)
    username: str = os.getenv("MIKROTIK_USERNAME", DEFAULT_MIKROTIK_USER)
    password: str = os.getenv("MIKROTIK_PASSWORD", DEFAULT_MIKROTIK_PASS)
    port: int = int(os.getenv("MIKROTIK_PORT", "22"))
    key_filename: str = os.getenv("MIKROTIK_KEY_FILENAME", None)


mikrotik_config = MikrotikConfig()
