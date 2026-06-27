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


def download_file_sync(filename: str) -> bytes:
    """Download a file from the MikroTik device over SFTP and return its bytes (blocking)."""
    logger.info(f"Downloading MikroTik file: {filename}")

    ssh_client = MikroTikSSHClient(
        host=config.mikrotik_config.host,
        username=config.mikrotik_config.username,
        password=config.mikrotik_config.password,
        key_filename=config.mikrotik_config.key_filename,
        port=config.mikrotik_config.port
    )

    try:
        if not ssh_client.connect():
            raise ConnectionError("Failed to connect to MikroTik device")
        return ssh_client.download_file(filename)
    finally:
        ssh_client.disconnect()


def upload_file_sync(filename: str, data: bytes) -> None:
    """Upload bytes to a file on the MikroTik device over SFTP (blocking)."""
    logger.info(f"Uploading MikroTik file: {filename} ({len(data)} bytes)")

    ssh_client = MikroTikSSHClient(
        host=config.mikrotik_config.host,
        username=config.mikrotik_config.username,
        password=config.mikrotik_config.password,
        key_filename=config.mikrotik_config.key_filename,
        port=config.mikrotik_config.port
    )

    try:
        if not ssh_client.connect():
            raise ConnectionError("Failed to connect to MikroTik device")
        ssh_client.upload_file(filename, data)
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
