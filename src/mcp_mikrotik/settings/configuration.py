import os

DEFAULT_MIKROTIK_HOST = "127.0.0.1"  
DEFAULT_MIKROTIK_USER = "admin"        
DEFAULT_MIKROTIK_PASS = ""    

mikrotik_config = {
    "host": os.getenv("MIKROTIK_HOST", DEFAULT_MIKROTIK_HOST),
    "username": os.getenv("MIKROTIK_USERNAME", DEFAULT_MIKROTIK_USER),
    "password": os.getenv("MIKROTIK_PASSWORD", DEFAULT_MIKROTIK_PASS),
    "port": int(os.getenv("MIKROTIK_PORT", "22"))
}
