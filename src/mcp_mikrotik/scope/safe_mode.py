import asyncio

from mcp.server.fastmcp import Context

from ..app import mcp, READ, WRITE
from ..safe_mode import get_safe_mode_manager


@mcp.tool(name="safe_mode_status", annotations=READ)
async def mikrotik_safe_mode_status(ctx: Context) -> str:
    """
    Returns whether MikroTik Safe Mode is currently active.

    Safe Mode protects against accidental misconfigurations: while active, all
    changes are held in memory only and will be reverted automatically on reboot
    or connection loss.  Use commit_safe_mode to persist changes or
    rollback_safe_mode to discard them explicitly.

    Returns:
        Current safe mode state
    """
    await ctx.info("Checking safe mode status")
    return get_safe_mode_manager().status()


@mcp.tool(name="enable_safe_mode", annotations=WRITE)
async def mikrotik_enable_safe_mode(ctx: Context) -> str:
    """
    Activates MikroTik Safe Mode by opening a persistent SSH shell session and
    sending Ctrl+X to the router.

    While Safe Mode is active:
    - Every subsequent tool call is executed inside the same persistent session.
    - Changes are NOT written to flash/NVRAM — a reboot reverts them.
    - If the MCP server process exits unexpectedly the session drops and the
      router reverts automatically.

    After reviewing the changes, call commit_safe_mode to persist them or
    rollback_safe_mode to discard them.

    Returns:
        Confirmation message or error
    """
    await ctx.info("Enabling MikroTik safe mode")
    result = await asyncio.to_thread(get_safe_mode_manager().enable)
    return result


@mcp.tool(name="commit_safe_mode", annotations=WRITE)
async def mikrotik_commit_safe_mode(ctx: Context) -> str:
    """
    Commits all pending Safe Mode changes and disables Safe Mode.

    Sends a second Ctrl+X to the router, which exits Safe Mode and writes all
    in-memory changes to persistent storage (flash/NVRAM).  After this call the
    persistent SSH session is closed and subsequent tools use normal per-command
    connections again.

    Returns:
        Confirmation message or error
    """
    await ctx.info("Committing safe mode changes")
    result = await asyncio.to_thread(get_safe_mode_manager().commit)
    return result


@mcp.tool(name="rollback_safe_mode", annotations=WRITE)
async def mikrotik_rollback_safe_mode(ctx: Context) -> str:
    """
    Discards all pending Safe Mode changes by closing the persistent SSH session.

    MikroTik automatically reverts every change made during the Safe Mode
    session when the controlling terminal disconnects.  No Ctrl+X is sent —
    the session is simply dropped, triggering the router's built-in rollback.

    Returns:
        Confirmation message
    """
    await ctx.info("Rolling back safe mode changes")
    result = await asyncio.to_thread(get_safe_mode_manager().rollback)
    return result
