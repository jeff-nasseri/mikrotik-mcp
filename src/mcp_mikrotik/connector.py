import asyncio
import logging

from mcp.server.fastmcp import Context

from . import config
from .mikrotik_ssh_client import MikroTikSSHClient

logger = logging.getLogger(__name__)


def _execute_sync(command: str) -> str:
    """Execute a MikroTik command via SSH and return the output (blocking)."""
    logger.info(f"Executing MikroTik command: {command}")

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
        logger.info(f"Command result: {repr(result)}")
        return result
    except Exception as e:
        error_msg = f"Error executing command: {str(e)}"
        logger.error(error_msg)
        return error_msg
    finally:
        ssh_client.disconnect()


async def execute_mikrotik_command(command: str, ctx: Context) -> str:
    """Execute a MikroTik command via SSH and return the output."""
    return await asyncio.to_thread(_execute_sync, command)
