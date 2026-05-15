import asyncio

from mcp.server.fastmcp import Context

from ..app import mcp, READ, WRITE, annotate
from ..safe_mode import get_safe_mode_manager


@mcp.tool(name="safe_mode_status", annotations=annotate(READ, "Safe Mode Status"))
async def mikrotik_safe_mode_status(ctx: Context) -> str:
    """Returns whether MikroTik Safe Mode is currently active."""
    await ctx.info("Checking safe mode status")
    return get_safe_mode_manager().status()


@mcp.tool(name="enable_safe_mode", annotations=annotate(WRITE, "Enable Safe Mode"))
async def mikrotik_enable_safe_mode(ctx: Context) -> str:
    """Activates MikroTik Safe Mode; changes are held in memory and auto-reverted on disconnect until committed."""
    await ctx.info("Enabling MikroTik safe mode")
    result = await asyncio.to_thread(get_safe_mode_manager().enable)
    return result


@mcp.tool(name="commit_safe_mode", annotations=annotate(WRITE, "Commit Safe Mode"))
async def mikrotik_commit_safe_mode(ctx: Context) -> str:
    """Commits all pending Safe Mode changes to persistent storage and exits Safe Mode."""
    await ctx.info("Committing safe mode changes")
    result = await asyncio.to_thread(get_safe_mode_manager().commit)
    return result


@mcp.tool(name="rollback_safe_mode", annotations=annotate(WRITE, "Rollback Safe Mode"))
async def mikrotik_rollback_safe_mode(ctx: Context) -> str:
    """Discards all pending Safe Mode changes by closing the SSH session, triggering automatic rollback."""
    await ctx.info("Rolling back safe mode changes")
    result = await asyncio.to_thread(get_safe_mode_manager().rollback)
    return result
