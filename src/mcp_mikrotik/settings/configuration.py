from dataclasses import dataclass

@dataclass
class MikrotikConfig:
    host: str = "127.0.0.1"
    username: str = "admin"
    password: str = ""
    key_filename: str = ""
    port: int = 22

mikrotik_config = MikrotikConfig()
