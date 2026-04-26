import asyncio
import logging
from typing import TYPE_CHECKING

from mcp.server.fastmcp import Context

from . import config
from .mikrotik_ssh_client import MikroTikSSHClient

if TYPE_CHECKING:
    from .config import DeviceConfig

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


def _execute_sync_on_device(device: "DeviceConfig", command: str) -> str:
    """Execute *command* on a specific device (blocking, for use with asyncio.to_thread)."""
    logger.info(f"Executing on {device.name} ({device.host}): {command}")

    ssh_client = MikroTikSSHClient(
        host=device.host,
        username=device.username,
        password=device.password,
        key_filename=device.key_filename,
        port=device.port,
    )

    try:
        if not ssh_client.connect():
            return f"Error: Failed to connect to {device.host}"

        result = ssh_client.execute_command(command)
        logger.info(f"[{device.name}] result: {repr(result)}")
        return result
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        logger.error(f"[{device.name}] {error_msg}")
        return error_msg
    finally:
        ssh_client.disconnect()


async def execute_mikrotik_command(command: str, ctx: Context) -> str:
    """Execute a MikroTik command via SSH and return the output.

    When Safe Mode is active the command is routed through the persistent
    interactive shell session so it runs inside the safe-mode context.
    """
    from .safe_mode import get_safe_mode_manager

    safe_mgr = get_safe_mode_manager()
    if safe_mgr.is_active:
        await ctx.info(f"Executing (safe mode): {command}")
        try:
            result = await asyncio.to_thread(safe_mgr.execute, command)
        except Exception as e:
            result = f"Error executing command in safe mode session: {str(e)}"
    else:
        await ctx.info(f"Executing MikroTik command: {command}")
        result = await asyncio.to_thread(_execute_sync, command)

    logger.info(f"Command result: {repr(result)}")
    if result.startswith("Error"):
        await ctx.error(result)
    return result


async def execute_command_on_device(device: "DeviceConfig", command: str, ctx: Context) -> str:
    """Execute *command* on a specific fleet device and return the output.

    Unlike ``execute_mikrotik_command`` this function bypasses the global
    single-device config and the Safe Mode manager — it always uses a fresh
    SSH connection to the given *device*.
    """
    await ctx.info(f"Executing on {device.name} ({device.host}): {command}")
    result = await asyncio.to_thread(_execute_sync_on_device, device, command)
    if result.startswith("Error"):
        await ctx.error(result)
    return result
