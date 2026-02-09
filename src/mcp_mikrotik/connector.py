from .logger import app_logger
from .mikrotik_ssh_client import MikroTikSSHClient
from . import config


def execute_mikrotik_command(command: str) -> str:
    """
    Execute a MikroTik command via SSH and return the output.
    """
    app_logger.info(f"Executing MikroTik command: {command}")
    
    ssh_client = MikroTikSSHClient(
        host=config.mikrotik_config.host,
        username=config.mikrotik_config.username,
        password=config.mikrotik_config.password,
        key_filename=config.mikrotik_config.key_filename,
        port=config.mikrotik_config.port
    )
    
    try:
        if not ssh_client.connect():
            return "Error: Failed to connect to MikroTik device"
        
        result = ssh_client.execute_command(command)
        app_logger.info(f"Command result: {repr(result)}") 
        return result
    except Exception as e:
        error_msg = f"Error executing command: {str(e)}"
        app_logger.error(error_msg)
        return error_msg
    finally:
        ssh_client.disconnect()
