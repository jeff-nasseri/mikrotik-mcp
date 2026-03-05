import asyncio
import logging

from mcp.server.fastmcp import Context

from . import config
from .mikrotik_ssh_client import MikroTikSSHClient

logger = logging.getLogger(__name__)


def _get_connection_params() -> dict:
    """Resolve connection parameters from conversation state, falling back to config."""
    state = config.connection_state
    cfg = config.mikrotik_config

    host = state.host if state.host is not None else cfg.host
    if host is None:
        raise ValueError(
            "No MikroTik host configured. Use the connect_to_device tool to specify a device, "
            "or set the host via CLI arguments or MIKROTIK_HOST environment variable."
        )

    return {
        "host": host,
        "username": state.username if state.username is not None else cfg.username,
        "password": state.password if state.password is not None else cfg.password,
        "key_filename": state.key_filename if state.key_filename is not None else cfg.key_filename,
        "port": state.port if state.port is not None else cfg.port,
    }


def _execute_sync(command: str) -> str:
    """Execute a MikroTik command via SSH and return the output (blocking)."""
    logger.info(f"Executing MikroTik command: {command}")

    params = _get_connection_params()
    ssh_client = MikroTikSSHClient(**params)

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
    await ctx.info(f"Executing MikroTik command: {command}")
    result = await asyncio.to_thread(_execute_sync, command)
    if result.startswith("Error"):
        await ctx.error(result)
    return result
