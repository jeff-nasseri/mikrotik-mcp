from typing import Optional, List

from mcp.server.fastmcp import Context

from ..connector import execute_mikrotik_command
from ..app import mcp, READ, WRITE, WRITE_IDEMPOTENT, DESTRUCTIVE

@mcp.tool(name="set_dns_servers", annotations=WRITE)
async def mikrotik_set_dns_servers(
    servers: List[str],
    ctx: Context,
    allow_remote_requests: bool = False,
    max_udp_packet_size: Optional[int] = None,
    max_concurrent_queries: Optional[int] = None,
    cache_size: Optional[int] = None,
    cache_max_ttl: Optional[str] = None,
    use_doh: bool = False,
    doh_server: Optional[str] = None,
    verify_doh_cert: bool = True
) -> str:
    """Sets DNS server configuration."""
    await ctx.info(f"Setting DNS servers: {', '.join(servers)}")

    cmd = "/ip dns set servers=" + ",".join(servers)

    if allow_remote_requests:
        cmd += " allow-remote-requests=yes"
    else:
        cmd += " allow-remote-requests=no"

    if max_udp_packet_size:
        cmd += f" max-udp-packet-size={max_udp_packet_size}"

    if max_concurrent_queries:
        cmd += f" max-concurrent-queries={max_concurrent_queries}"

    if cache_size:
        cmd += f" cache-size={cache_size}"

    if cache_max_ttl:
        cmd += f" cache-max-ttl={cache_max_ttl}"

    if use_doh and doh_server:
        cmd += f' use-doh-server="{doh_server}"'
        cmd += f' verify-doh-cert={"yes" if verify_doh_cert else "no"}'

    result = await execute_mikrotik_command(cmd, ctx)

    if not result.strip() or "failure:" not in result.lower():
        details_cmd = "/ip dns print"
        details = await execute_mikrotik_command(details_cmd, ctx)
        return f"DNS settings updated successfully:\n\n{details}"
    else:
        return f"Failed to update DNS settings: {result}"

@mcp.tool(name="get_dns_settings", annotations=READ)
async def mikrotik_get_dns_settings(ctx: Context) -> str:
    """Gets current DNS configuration."""
    await ctx.info("Getting DNS settings")

    cmd = "/ip dns print"
    result = await execute_mikrotik_command(cmd, ctx)

    if not result:
        return "Unable to retrieve DNS settings."

    return f"DNS SETTINGS:\n\n{result}"

@mcp.tool(name="add_dns_static", annotations=WRITE)
async def mikrotik_add_dns_static(
    name: str,
    ctx: Context,
    address: Optional[str] = None,
    cname: Optional[str] = None,
    mx_preference: Optional[int] = None,
    mx_exchange: Optional[str] = None,
    text: Optional[str] = None,
    srv_priority: Optional[int] = None,
    srv_weight: Optional[int] = None,
    srv_port: Optional[int] = None,
    srv_target: Optional[str] = None,
    ttl: Optional[str] = None,
    comment: Optional[str] = None,
    disabled: bool = False,
    regexp: Optional[str] = None
) -> str:
    """Adds a static DNS entry."""
    await ctx.info(f"Adding static DNS entry: name={name}")

    cmd = f'/ip dns static add name="{name}"'

    if address:
        cmd += f" address={address}"

    if cname:
        cmd += f' cname="{cname}"'

    if mx_preference is not None and mx_exchange:
        cmd += f' mx-preference={mx_preference} mx-exchange="{mx_exchange}"'

    if text:
        cmd += f' text="{text}"'

    if srv_priority is not None and srv_weight is not None and srv_port is not None and srv_target:
        cmd += f" srv-priority={srv_priority} srv-weight={srv_weight} srv-port={srv_port}"
        cmd += f' srv-target="{srv_target}"'

    if ttl:
        cmd += f" ttl={ttl}"

    if comment:
        cmd += f' comment="{comment}"'

    if disabled:
        cmd += " disabled=yes"

    if regexp:
        cmd += f' regexp="{regexp}"'

    result = await execute_mikrotik_command(cmd, ctx)

    if result.strip():
        if "*" in result or result.strip().isdigit():
            entry_id = result.strip()
            details_cmd = f"/ip dns static print detail where .id={entry_id}"
            details = await execute_mikrotik_command(details_cmd, ctx)

            if details.strip():
                return f"Static DNS entry added successfully:\n\n{details}"
            else:
                return f"Static DNS entry added with ID: {result}"
        else:
            return f"Failed to add static DNS entry: {result}"
    else:
        details_cmd = f'/ip dns static print detail where name="{name}"'
        details = await execute_mikrotik_command(details_cmd, ctx)

        if details.strip():
            return f"Static DNS entry added successfully:\n\n{details}"
        else:
            return "Static DNS entry addition completed but unable to verify."

@mcp.tool(name="list_dns_static", annotations=READ)
async def mikrotik_list_dns_static(
    ctx: Context,
    name_filter: Optional[str] = None,
    address_filter: Optional[str] = None,
    type_filter: Optional[str] = None,
    disabled_only: bool = False,
    regexp_only: bool = False
) -> str:
    """Lists static DNS entries."""
    await ctx.info(f"Listing static DNS entries with filters: name={name_filter}")

    cmd = "/ip dns static print"

    filters = []
    if name_filter:
        filters.append(f'name~"{name_filter}"')
    if address_filter:
        filters.append(f'address~"{address_filter}"')
    if type_filter:
        filters.append(f'type="{type_filter}"')
    if disabled_only:
        filters.append("disabled=yes")
    if regexp_only:
        filters.append("regexp!=\"\"")

    if filters:
        cmd += " where " + " ".join(filters)

    result = await execute_mikrotik_command(cmd, ctx)

    if not result or result.strip() == "" or result.strip() == "no such item":
        return "No static DNS entries found matching the criteria."

    return f"STATIC DNS ENTRIES:\n\n{result}"

@mcp.tool(name="get_dns_static", annotations=READ)
async def mikrotik_get_dns_static(entry_id: str, ctx: Context) -> str:
    """Gets details of a specific static DNS entry."""
    await ctx.info(f"Getting static DNS entry details: entry_id={entry_id}")

    cmd = f"/ip dns static print detail where .id={entry_id}"
    result = await execute_mikrotik_command(cmd, ctx)

    if not result or result.strip() == "":
        return f"Static DNS entry with ID '{entry_id}' not found."

    return f"STATIC DNS ENTRY DETAILS:\n\n{result}"

@mcp.tool(name="update_dns_static", annotations=WRITE_IDEMPOTENT)
async def mikrotik_update_dns_static(
    entry_id: str,
    ctx: Context,
    name: Optional[str] = None,
    address: Optional[str] = None,
    cname: Optional[str] = None,
    mx_preference: Optional[int] = None,
    mx_exchange: Optional[str] = None,
    text: Optional[str] = None,
    srv_priority: Optional[int] = None,
    srv_weight: Optional[int] = None,
    srv_port: Optional[int] = None,
    srv_target: Optional[str] = None,
    ttl: Optional[str] = None,
    comment: Optional[str] = None,
    disabled: Optional[bool] = None,
    regexp: Optional[str] = None
) -> str:
    """Updates a static DNS entry."""
    await ctx.info(f"Updating static DNS entry: entry_id={entry_id}")

    cmd = f"/ip dns static set {entry_id}"

    updates = []
    if name:
        updates.append(f'name="{name}"')
    if address is not None:
        if address == "":
            updates.append("!address")
        else:
            updates.append(f"address={address}")
    if cname is not None:
        if cname == "":
            updates.append("!cname")
        else:
            updates.append(f'cname="{cname}"')
    if mx_preference is not None:
        updates.append(f"mx-preference={mx_preference}")
    if mx_exchange is not None:
        if mx_exchange == "":
            updates.append("!mx-exchange")
        else:
            updates.append(f'mx-exchange="{mx_exchange}"')
    if text is not None:
        if text == "":
            updates.append("!text")
        else:
            updates.append(f'text="{text}"')
    if srv_priority is not None:
        updates.append(f"srv-priority={srv_priority}")
    if srv_weight is not None:
        updates.append(f"srv-weight={srv_weight}")
    if srv_port is not None:
        updates.append(f"srv-port={srv_port}")
    if srv_target is not None:
        if srv_target == "":
            updates.append("!srv-target")
        else:
            updates.append(f'srv-target="{srv_target}"')
    if ttl is not None:
        if ttl == "":
            updates.append("!ttl")
        else:
            updates.append(f"ttl={ttl}")
    if comment is not None:
        updates.append(f'comment="{comment}"')
    if disabled is not None:
        updates.append(f'disabled={"yes" if disabled else "no"}')
    if regexp is not None:
        if regexp == "":
            updates.append("!regexp")
        else:
            updates.append(f'regexp="{regexp}"')

    if not updates:
        return "No updates specified."

    cmd += " " + " ".join(updates)

    result = await execute_mikrotik_command(cmd, ctx)

    if "failure:" in result.lower() or "error" in result.lower():
        return f"Failed to update static DNS entry: {result}"

    details_cmd = f"/ip dns static print detail where .id={entry_id}"
    details = await execute_mikrotik_command(details_cmd, ctx)

    return f"Static DNS entry updated successfully:\n\n{details}"

@mcp.tool(name="remove_dns_static", annotations=DESTRUCTIVE)
async def mikrotik_remove_dns_static(entry_id: str, ctx: Context) -> str:
    """Removes a static DNS entry."""
    await ctx.info(f"Removing static DNS entry: entry_id={entry_id}")

    check_cmd = f"/ip dns static print count-only where .id={entry_id}"
    count = await execute_mikrotik_command(check_cmd, ctx)

    if count.strip() == "0":
        return f"Static DNS entry with ID '{entry_id}' not found."

    cmd = f"/ip dns static remove {entry_id}"
    result = await execute_mikrotik_command(cmd, ctx)

    if "failure:" in result.lower() or "error" in result.lower():
        return f"Failed to remove static DNS entry: {result}"

    return f"Static DNS entry with ID '{entry_id}' removed successfully."

@mcp.tool(name="enable_dns_static", annotations=WRITE_IDEMPOTENT)
async def mikrotik_enable_dns_static(entry_id: str, ctx: Context) -> str:
    """Enables a static DNS entry."""
    return await mikrotik_update_dns_static(entry_id, disabled=False, ctx=ctx)

@mcp.tool(name="disable_dns_static", annotations=WRITE_IDEMPOTENT)
async def mikrotik_disable_dns_static(entry_id: str, ctx: Context) -> str:
    """Disables a static DNS entry."""
    return await mikrotik_update_dns_static(entry_id, disabled=True, ctx=ctx)

@mcp.tool(name="get_dns_cache", annotations=READ)
async def mikrotik_get_dns_cache(ctx: Context) -> str:
    """Gets the current DNS cache."""
    await ctx.info("Getting DNS cache")

    cmd = "/ip dns cache print"
    result = await execute_mikrotik_command(cmd, ctx)

    if not result or result.strip() == "":
        return "DNS cache is empty."

    return f"DNS CACHE:\n\n{result}"

@mcp.tool(name="flush_dns_cache", annotations=DESTRUCTIVE)
async def mikrotik_flush_dns_cache(ctx: Context) -> str:
    """Flushes the DNS cache."""
    await ctx.info("Flushing DNS cache")

    cmd = "/ip dns cache flush"
    result = await execute_mikrotik_command(cmd, ctx)

    if not result.strip():
        return "DNS cache flushed successfully."
    else:
        return f"Flush result: {result}"

@mcp.tool(name="get_dns_cache_statistics", annotations=READ)
async def mikrotik_get_dns_cache_statistics(ctx: Context) -> str:
    """Gets DNS cache statistics."""
    await ctx.info("Getting DNS cache statistics")

    cmd = "/ip dns cache print stats"
    result = await execute_mikrotik_command(cmd, ctx)

    if not result:
        return "Unable to retrieve DNS cache statistics."

    return f"DNS CACHE STATISTICS:\n\n{result}"

@mcp.tool(name="add_dns_regexp", annotations=WRITE)
async def mikrotik_add_dns_regexp(
    regexp: str,
    address: str,
    ctx: Context,
    ttl: str = "1d",
    comment: Optional[str] = None,
    disabled: bool = False
) -> str:
    """Adds a DNS regexp entry."""
    await ctx.info(f"Adding DNS regexp entry: regexp={regexp}")

    return await mikrotik_add_dns_static(
        name="dummy",
        address=address,
        regexp=regexp,
        ttl=ttl,
        comment=comment,
        disabled=disabled,
        ctx=ctx
    )

@mcp.tool(name="test_dns_query", annotations=READ)
async def mikrotik_test_dns_query(
    name: str,
    ctx: Context,
    server: Optional[str] = None,
    type: str = "A"
) -> str:
    """Tests a DNS query."""
    await ctx.info(f"Testing DNS query: name={name}, type={type}")

    cmd = f"/resolve {name}"

    if server:
        cmd += f" server={server}"

    if type != "A":
        cmd += f" type={type}"

    result = await execute_mikrotik_command(cmd, ctx)

    if not result:
        return f"Failed to resolve {name}"

    return f"DNS QUERY RESULT for {name}:\n\n{result}"

@mcp.tool(name="export_dns_config", annotations=READ)
async def mikrotik_export_dns_config(ctx: Context, filename: Optional[str] = None) -> str:
    """Exports DNS configuration to a file."""
    await ctx.info("Exporting DNS configuration")

    if not filename:
        filename = "dns_config"

    cmd = f"/ip dns export file={filename}"
    result = await execute_mikrotik_command(cmd, ctx)

    if not result.strip():
        return f"DNS configuration exported to {filename}.rsc"
    else:
        return f"Export result: {result}"
