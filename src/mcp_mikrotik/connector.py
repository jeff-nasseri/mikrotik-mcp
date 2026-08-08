import asyncio
import logging
from typing import Optional

from mcp.server.mcpserver import Context

from .inventory import DeviceNotFoundError, get_inventory

logger = logging.getLogger(__name__)


def _execute_sync(command: str, device: Optional[str] = None) -> str:
    """Execute a MikroTik command over a fresh SSH connection (blocking).

    Each call opens its own connection and closes it again, so concurrent
    sessions never share a client.
    """
    inventory = get_inventory()
    target = inventory.resolve(device)
    logger.info(f"Executing MikroTik command on '{target.title}': {command}")

    with inventory.session(target.title) as client:
        result = client.execute_command(command)

    logger.info(f"Command result: {repr(result)}")
    return result


def download_file_sync(filename: str, device: Optional[str] = None) -> bytes:
    """Download a file from the target device over SFTP and return its bytes."""
    inventory = get_inventory()
    target = inventory.resolve(device)
    logger.info(f"Downloading file from '{target.title}': {filename}")

    with inventory.session(target.title) as client:
        return client.download_file(filename)


def upload_file_sync(filename: str, data: bytes, device: Optional[str] = None) -> None:
    """Upload bytes to a file on the target device over SFTP."""
    inventory = get_inventory()
    target = inventory.resolve(device)
    logger.info(f"Uploading file to '{target.title}': {filename} ({len(data)} bytes)")

    with inventory.session(target.title) as client:
        client.upload_file(filename, data)


async def execute_mikrotik_command(
    command: str, ctx: Context, device: Optional[str] = None
) -> str:
    """Execute a MikroTik command on the selected device and return the output.

    ``device`` is the inventory title of the target. It may be omitted when the
    inventory holds exactly one device.

    When Safe Mode is active *for that device* the command is routed through
    that device's persistent interactive shell so it runs inside the safe-mode
    context.
    """
    from .safe_mode import get_safe_mode_manager

    # Resolve the target first so a bad/missing device is reported clearly and
    # never silently executed somewhere else.
    try:
        target = get_inventory().resolve(device)
    except DeviceNotFoundError as exc:
        msg = f"Error: {exc}"
        await ctx.error(msg)
        return msg

    safe_mgr = get_safe_mode_manager(target.title)
    if safe_mgr.is_active:
        await ctx.info(f"Executing on '{target.title}' (safe mode): {command}")
        try:
            result = await asyncio.to_thread(safe_mgr.execute, command)
        except Exception as e:
            result = f"Error executing command in safe mode session: {str(e)}"
    else:
        await ctx.info(f"Executing on '{target.title}': {command}")
        try:
            result = await asyncio.to_thread(_execute_sync, command, target.title)
        except ConnectionError as e:
            result = f"Error: {str(e)}"
        except Exception as e:
            result = f"Error executing command: {str(e)}"

    logger.info(f"Command result: {repr(result)}")
    if result.startswith("Error"):
        await ctx.error(result)
    return result
