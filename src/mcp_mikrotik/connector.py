import asyncio
import logging
from typing import Optional

from mcp.server.fastmcp import Context

from . import config
from .mikrotik_ssh_client import MikroTikSSHClient

logger = logging.getLogger(__name__)


def _get_connection_params(device: Optional[str] = None) -> dict:
    """Resolve connection parameters for a named device, the default device, or config fallback."""
    registry = config.device_registry
    cfg = config.mikrotik_config

    # Try registry first (explicit device name or default)
    conn = registry.get(device)
    if conn is not None:
        return {
            "host": conn.host,
            "username": conn.username,
            "password": conn.password,
            "key_filename": conn.key_filename,
            "port": conn.port,
        }

    # If a specific device was requested but not found, error
    if device is not None:
        available = ", ".join(registry.device_names) if not registry.is_empty else "none"
        raise ValueError(
            f"Device '{device}' not found. Available devices: {available}. "
            f"Use connect_to_device to register it first."
        )

    # Fall back to config
    if cfg.host is not None:
        return {
            "host": cfg.host,
            "username": cfg.username,
            "password": cfg.password,
            "key_filename": cfg.key_filename,
            "port": cfg.port,
        }

    raise ValueError(
        "No MikroTik device configured. Use the connect_to_device tool to specify a device, "
        "or set the host via CLI arguments or MIKROTIK_HOST environment variable."
    )


def _execute_sync(command: str, device: Optional[str] = None) -> str:
    """Execute a MikroTik command via SSH and return the output (blocking)."""
    logger.info(f"Executing MikroTik command: {command}")

    params = _get_connection_params(device)
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


async def execute_mikrotik_command(command: str, ctx: Context, device: Optional[str] = None) -> str:
    """Execute a MikroTik command via SSH and return the output."""
    await ctx.info(f"Executing MikroTik command: {command}")
    result = await asyncio.to_thread(_execute_sync, command, device)
    if result.startswith("Error"):
        await ctx.error(result)
    return result
