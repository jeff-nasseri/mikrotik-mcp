from typing import Optional, List
from ..connector import execute_mikrotik_command
from mcp.server.fastmcp import Context
from ..app import mcp, READ, WRITE, WRITE_IDEMPOTENT, DESTRUCTIVE

@mcp.tool(name="add_route", annotations=WRITE)
async def mikrotik_add_route(
    dst_address: str,
    gateway: str,
    ctx: Context,
    distance: Optional[int] = None,
    scope: Optional[int] = None,
    target_scope: Optional[int] = None,
    routing_mark: Optional[str] = None,
    comment: Optional[str] = None,
    disabled: bool = False,
    vrf_interface: Optional[str] = None,
    pref_src: Optional[str] = None,
    check_gateway: Optional[str] = None
) -> str:
    """Adds a route to the routing table."""
    await ctx.info(f"Adding route: dst={dst_address}, gateway={gateway}")

    cmd = f"/ip route add dst-address={dst_address} gateway={gateway}"

    if distance is not None:
        cmd += f" distance={distance}"
    if scope is not None:
        cmd += f" scope={scope}"
    if target_scope is not None:
        cmd += f" target-scope={target_scope}"
    if routing_mark:
        cmd += f' routing-mark="{routing_mark}"'
    if comment:
        cmd += f' comment="{comment}"'
    if disabled:
        cmd += " disabled=yes"
    if vrf_interface:
        cmd += f' vrf-interface="{vrf_interface}"'
    if pref_src:
        cmd += f" pref-src={pref_src}"
    if check_gateway:
        cmd += f" check-gateway={check_gateway}"

    result = await execute_mikrotik_command(cmd, ctx)

    if result.strip():
        if "*" in result or result.strip().isdigit():
            route_id = result.strip()
            details_cmd = f"/ip route print detail where .id={route_id}"
            details = await execute_mikrotik_command(details_cmd, ctx)

            if details.strip():
                return f"Route added successfully:\n\n{details}"
            else:
                return f"Route added with ID: {result}"
        else:
            return f"Failed to add route: {result}"
    else:
        details_cmd = f'/ip route print detail where dst-address="{dst_address}" and gateway="{gateway}"'
        details = await execute_mikrotik_command(details_cmd, ctx)

        if details.strip():
            return f"Route added successfully:\n\n{details}"
        else:
            return "Route addition completed but unable to verify."

@mcp.tool(name="list_routes", annotations=READ)
async def mikrotik_list_routes(
    ctx: Context,
    dst_filter: Optional[str] = None,
    gateway_filter: Optional[str] = None,
    routing_mark_filter: Optional[str] = None,
    distance_filter: Optional[int] = None,
    active_only: bool = False,
    disabled_only: bool = False,
    dynamic_only: bool = False,
    static_only: bool = False
) -> str:
    """Lists routes in MikroTik routing table."""
    await ctx.info(f"Listing routes with filters: dst={dst_filter}, gateway={gateway_filter}")

    cmd = "/ip route print"

    filters = []
    if dst_filter:
        filters.append(f'dst-address~"{dst_filter}"')
    if gateway_filter:
        filters.append(f'gateway~"{gateway_filter}"')
    if routing_mark_filter:
        filters.append(f'routing-mark="{routing_mark_filter}"')
    if distance_filter is not None:
        filters.append(f"distance={distance_filter}")
    if active_only:
        filters.append("active=yes")
    if disabled_only:
        filters.append("disabled=yes")
    if dynamic_only:
        filters.append("dynamic=yes")
    if static_only:
        filters.append("static=yes")

    if filters:
        cmd += " where " + " ".join(filters)

    result = await execute_mikrotik_command(cmd, ctx)

    if not result or result.strip() == "" or result.strip() == "no such item":
        return "No routes found matching the criteria."

    return f"ROUTES:\n\n{result}"

@mcp.tool(name="get_route", annotations=READ)
async def mikrotik_get_route(route_id: str, ctx: Context) -> str:
    """Gets detailed information about a specific route."""
    await ctx.info(f"Getting route details: route_id={route_id}")

    cmd = f"/ip route print detail where .id={route_id}"
    result = await execute_mikrotik_command(cmd, ctx)

    if not result or result.strip() == "":
        return f"Route with ID '{route_id}' not found."

    return f"ROUTE DETAILS:\n\n{result}"

@mcp.tool(name="update_route", annotations=WRITE_IDEMPOTENT)
async def mikrotik_update_route(
    route_id: str,
    ctx: Context,
    dst_address: Optional[str] = None,
    gateway: Optional[str] = None,
    distance: Optional[int] = None,
    scope: Optional[int] = None,
    target_scope: Optional[int] = None,
    routing_mark: Optional[str] = None,
    comment: Optional[str] = None,
    disabled: Optional[bool] = None,
    vrf_interface: Optional[str] = None,
    pref_src: Optional[str] = None,
    check_gateway: Optional[str] = None
) -> str:
    """Updates a route."""
    await ctx.info(f"Updating route: route_id={route_id}")

    cmd = f"/ip route set {route_id}"

    updates = []
    if dst_address:
        updates.append(f"dst-address={dst_address}")
    if gateway:
        updates.append(f"gateway={gateway}")
    if distance is not None:
        updates.append(f"distance={distance}")
    if scope is not None:
        updates.append(f"scope={scope}")
    if target_scope is not None:
        updates.append(f"target-scope={target_scope}")
    if routing_mark is not None:
        if routing_mark == "":
            updates.append("!routing-mark")
        else:
            updates.append(f'routing-mark="{routing_mark}"')
    if comment is not None:
        updates.append(f'comment="{comment}"')
    if disabled is not None:
        updates.append(f'disabled={"yes" if disabled else "no"}')
    if vrf_interface is not None:
        if vrf_interface == "":
            updates.append("!vrf-interface")
        else:
            updates.append(f'vrf-interface="{vrf_interface}"')
    if pref_src is not None:
        if pref_src == "":
            updates.append("!pref-src")
        else:
            updates.append(f"pref-src={pref_src}")
    if check_gateway is not None:
        updates.append(f"check-gateway={check_gateway}")

    if not updates:
        return "No updates specified."

    cmd += " " + " ".join(updates)

    result = await execute_mikrotik_command(cmd, ctx)

    if "failure:" in result.lower() or "error" in result.lower():
        return f"Failed to update route: {result}"

    details_cmd = f"/ip route print detail where .id={route_id}"
    details = await execute_mikrotik_command(details_cmd, ctx)

    return f"Route updated successfully:\n\n{details}"

@mcp.tool(name="remove_route", annotations=DESTRUCTIVE)
async def mikrotik_remove_route(route_id: str, ctx: Context) -> str:
    """Removes a route."""
    await ctx.info(f"Removing route: route_id={route_id}")

    check_cmd = f"/ip route print count-only where .id={route_id}"
    count = await execute_mikrotik_command(check_cmd, ctx)

    if count.strip() == "0":
        return f"Route with ID '{route_id}' not found."

    cmd = f"/ip route remove {route_id}"
    result = await execute_mikrotik_command(cmd, ctx)

    if "failure:" in result.lower() or "error" in result.lower():
        return f"Failed to remove route: {result}"

    return f"Route with ID '{route_id}' removed successfully."

@mcp.tool(name="enable_route", annotations=WRITE_IDEMPOTENT)
async def mikrotik_enable_route(route_id: str, ctx: Context) -> str:
    """Enables a route."""
    return await mikrotik_update_route(route_id, disabled=False, ctx=ctx)

@mcp.tool(name="disable_route", annotations=WRITE_IDEMPOTENT)
async def mikrotik_disable_route(route_id: str, ctx: Context) -> str:
    """Disables a route."""
    return await mikrotik_update_route(route_id, disabled=True, ctx=ctx)

@mcp.tool(name="get_routing_table", annotations=READ)
async def mikrotik_get_routing_table(
    ctx: Context,
    table_name: Optional[str] = "main",
    protocol_filter: Optional[str] = None,
    active_only: bool = True
) -> str:
    """Gets a specific routing table."""
    await ctx.info(f"Getting routing table: table={table_name}")

    cmd = "/ip route print"

    filters = []
    if table_name and table_name != "main":
        filters.append(f'routing-table="{table_name}"')
    if protocol_filter:
        filters.append(f'protocol="{protocol_filter}"')
    if active_only:
        filters.append("active=yes")

    if filters:
        cmd += " where " + " ".join(filters)

    result = await execute_mikrotik_command(cmd, ctx)

    if not result or result.strip() == "":
        return f"No routes found in table '{table_name}'."

    return f"ROUTING TABLE ({table_name}):\n\n{result}"

@mcp.tool(name="check_route_path", annotations=READ)
async def mikrotik_check_route_path(
    destination: str,
    ctx: Context,
    source: Optional[str] = None,
    routing_mark: Optional[str] = None
) -> str:
    """Checks the route path to a destination."""
    await ctx.info(f"Checking route path to: {destination}")

    cmd = f"/ip route check {destination}"

    if source:
        cmd += f" src-address={source}"
    if routing_mark:
        cmd += f' routing-mark="{routing_mark}"'

    result = await execute_mikrotik_command(cmd, ctx)

    if not result:
        return f"Unable to check route to {destination}"

    return f"ROUTE PATH TO {destination}:\n\n{result}"

@mcp.tool(name="get_route_cache", annotations=READ)
async def mikrotik_get_route_cache(ctx: Context) -> str:
    """Gets the route cache."""
    await ctx.info("Getting route cache")

    cmd = "/ip route cache print"
    result = await execute_mikrotik_command(cmd, ctx)

    if not result or result.strip() == "":
        return "Route cache is empty."

    return f"ROUTE CACHE:\n\n{result}"

@mcp.tool(name="flush_route_cache", annotations=DESTRUCTIVE)
async def mikrotik_flush_route_cache(ctx: Context) -> str:
    """Flushes the route cache."""
    await ctx.info("Flushing route cache")

    cmd = "/ip route cache flush"
    result = await execute_mikrotik_command(cmd, ctx)

    if not result.strip():
        return "Route cache flushed successfully."
    else:
        return f"Flush result: {result}"

@mcp.tool(name="add_default_route", annotations=WRITE)
async def mikrotik_add_default_route(
    gateway: str,
    ctx: Context,
    distance: int = 1,
    comment: Optional[str] = None,
    check_gateway: str = "ping"
) -> str:
    """Adds a default route."""
    return await mikrotik_add_route(
        dst_address="0.0.0.0/0",
        gateway=gateway,
        distance=distance,
        comment=comment or "Default route",
        check_gateway=check_gateway,
        ctx=ctx
    )

@mcp.tool(name="add_blackhole_route", annotations=WRITE)
async def mikrotik_add_blackhole_route(
    dst_address: str,
    ctx: Context,
    distance: int = 1,
    comment: Optional[str] = None
) -> str:
    """Adds a blackhole route."""
    await ctx.info(f"Adding blackhole route: dst={dst_address}")

    cmd = f"/ip route add dst-address={dst_address} type=blackhole distance={distance}"

    if comment:
        cmd += f' comment="{comment}"'

    result = await execute_mikrotik_command(cmd, ctx)

    if result.strip():
        if "*" in result or result.strip().isdigit():
            return f"Blackhole route added successfully. ID: {result}"
        else:
            return f"Failed to add blackhole route: {result}"
    else:
        return "Blackhole route added successfully."

@mcp.tool(name="get_route_statistics", annotations=READ)
async def mikrotik_get_route_statistics(ctx: Context) -> str:
    """Gets routing table statistics."""
    await ctx.info("Getting route statistics")

    total_cmd = "/ip route print count-only"
    total_count = await execute_mikrotik_command(total_cmd, ctx)

    active_cmd = "/ip route print count-only where active=yes"
    active_count = await execute_mikrotik_command(active_cmd, ctx)

    dynamic_cmd = "/ip route print count-only where dynamic=yes"
    dynamic_count = await execute_mikrotik_command(dynamic_cmd, ctx)

    static_cmd = "/ip route print count-only where static=yes"
    static_count = await execute_mikrotik_command(static_cmd, ctx)

    disabled_cmd = "/ip route print count-only where disabled=yes"
    disabled_count = await execute_mikrotik_command(disabled_cmd, ctx)

    stats = [
        f"Total routes: {total_count.strip()}",
        f"Active routes: {active_count.strip()}",
        f"Dynamic routes: {dynamic_count.strip()}",
        f"Static routes: {static_count.strip()}",
        f"Disabled routes: {disabled_count.strip()}"
    ]

    return "ROUTE STATISTICS:\n\n" + "\n".join(stats)
