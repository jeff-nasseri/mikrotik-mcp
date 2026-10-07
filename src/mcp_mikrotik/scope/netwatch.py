"""Read-only view over `/tool netwatch`.

A configuration export shows which probes exist; only `print detail` carries
`status` and `since`, which is what says whether a monitored host is up right
now and how long it has been that way.
"""

from typing import Optional

from mcp.server.mcpserver import Context

from ..app import mcp, READ, annotate
from ..connector import execute_mikrotik_command


@mcp.tool(name="list_netwatch", annotations=annotate(READ, "List Netwatch Probes"))
async def mikrotik_list_netwatch(
    ctx: Context,
    host_filter: Optional[str] = None,
    comment_filter: Optional[str] = None,
    status_filter: Optional[str] = None,
    type_filter: Optional[str] = None,
    device: Optional[str] = None
) -> str:
    """Lists the netwatch probes with their live status and last change.

    Each entry reports `status` (up / down / unknown) and `since`, the
    timestamp of the last transition — the two fields a configuration export
    cannot give you.

    Notes:
        `host_filter` and `comment_filter` are substring matches; `status_filter`
        and `type_filter` are exact. Pass `status_filter="down"` to list only
        what is currently failing.

        A probe with no `src-address` follows whichever WAN is active, so it
        keeps reporting across a failover; one pinned to a source address
        reports that path only. Which of the two you want depends on whether
        you are watching the internet or a specific link.
    """
    await ctx.info("Listing netwatch probes")
    command = "/tool netwatch print detail"
    filters = []
    if host_filter:
        filters.append(f'host~"{host_filter}"')
    if comment_filter:
        filters.append(f'comment~"{comment_filter}"')
    if status_filter:
        filters.append(f'status="{status_filter}"')
    if type_filter:
        filters.append(f'type="{type_filter}"')
    if filters:
        command += " where " + " ".join(filters)

    result = await execute_mikrotik_command(command, ctx, device=device)
    # `print detail` prints the Flags legend (non-empty) even when no row
    # matches, so emptiness is decided by real entry data, not by length.
    if not result or "host=" not in result:
        return "No netwatch probes found matching the criteria."
    return f"NETWATCH PROBES:\n\n{result}"
