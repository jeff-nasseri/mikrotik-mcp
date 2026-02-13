from typing import Literal, Optional
from mcp.server.fastmcp import Context
from ..connector import execute_mikrotik_command
from ..app import mcp, READ, WRITE, WRITE_IDEMPOTENT, DESTRUCTIVE

@mcp.tool(name="create_nat_rule", annotations=WRITE)
async def mikrotik_create_nat_rule(
    ctx: Context,
    chain: Literal["srcnat", "dstnat"],
    action: str,
    src_address: Optional[str] = None,
    dst_address: Optional[str] = None,
    src_port: Optional[str] = None,
    dst_port: Optional[str] = None,
    protocol: Optional[str] = None,
    in_interface: Optional[str] = None,
    out_interface: Optional[str] = None,
    to_addresses: Optional[str] = None,
    to_ports: Optional[str] = None,
    comment: Optional[str] = None,
    disabled: bool = False,
    log: bool = False,
    log_prefix: Optional[str] = None,
    place_before: Optional[str] = None
) -> str:
    """
    Creates a NAT rule on MikroTik device.

    Args:
        chain: NAT chain (srcnat, dstnat)
        action: Action to take (accept, drop, masquerade, dst-nat, src-nat, etc.)
        src_address: Source IP address or range
        dst_address: Destination IP address or range
        src_port: Source port or range
        dst_port: Destination port or range
        protocol: Protocol (tcp, udp, icmp, etc.)
        in_interface: Input interface
        out_interface: Output interface
        to_addresses: Target address for translation
        to_ports: Target port for translation
        comment: Optional comment for the rule
        disabled: Whether to disable the rule after creation
        log: Whether to log packets matching this rule
        log_prefix: Prefix for log entries
        place_before: Place this rule before another rule (by number)

    Returns:
        Command output or error message
    """
    await ctx.info(f"Creating NAT rule: chain={chain}, action={action}")

    # Validate action based on chain
    srcnat_actions = ["accept", "drop", "masquerade", "src-nat", "same", "netmap", "jump", "return", "log", "passthrough"]
    dstnat_actions = ["accept", "drop", "dst-nat", "jump", "return", "log", "passthrough", "redirect", "netmap", "same"]

    if chain == "srcnat" and action not in srcnat_actions:
        return f"Error: Invalid action '{action}' for srcnat. Must be one of: {', '.join(srcnat_actions)}"
    elif chain == "dstnat" and action not in dstnat_actions:
        return f"Error: Invalid action '{action}' for dstnat. Must be one of: {', '.join(dstnat_actions)}"

    # Build the command
    cmd = f"/ip firewall nat add chain={chain} action={action}"

    # Add optional parameters
    if src_address:
        cmd += f" src-address={src_address}"

    if dst_address:
        cmd += f" dst-address={dst_address}"

    if src_port:
        cmd += f" src-port={src_port}"

    if dst_port:
        cmd += f" dst-port={dst_port}"

    if protocol:
        cmd += f" protocol={protocol}"

    if in_interface:
        cmd += f' in-interface="{in_interface}"'

    if out_interface:
        cmd += f' out-interface="{out_interface}"'

    if to_addresses:
        cmd += f" to-addresses={to_addresses}"

    if to_ports:
        cmd += f" to-ports={to_ports}"

    if comment:
        cmd += f' comment="{comment}"'

    if disabled:
        cmd += " disabled=yes"

    if log:
        cmd += " log=yes"
        if log_prefix:
            cmd += f' log-prefix="{log_prefix}"'

    if place_before:
        cmd += f" place-before={place_before}"

    result = await execute_mikrotik_command(cmd, ctx)

    # Check if creation was successful
    if result.strip():
        # MikroTik returns the ID of created item on success
        if "*" in result or result.strip().isdigit():
            # Success - get the details
            rule_id = result.strip()
            details_cmd = f"/ip firewall nat print detail where .id={rule_id}"
            details = await execute_mikrotik_command(details_cmd, ctx)

            if details.strip():
                return f"NAT rule created successfully:\n\n{details}"
            else:
                return f"NAT rule created with ID: {result}"
        else:
            # Error occurred
            return f"Failed to create NAT rule: {result}"
    else:
        # No output might mean success, let's check by getting the last rule
        details_cmd = "/ip firewall nat print detail count-only"
        count = await execute_mikrotik_command(details_cmd, ctx)

        if count.strip().isdigit() and int(count.strip()) > 0:
            # Get the last rule
            last_rule_cmd = f"/ip firewall nat print detail from={int(count.strip())-1}"
            details = await execute_mikrotik_command(last_rule_cmd, ctx)
            return f"NAT rule created successfully:\n\n{details}"
        else:
            return "NAT rule creation completed but unable to verify."

@mcp.tool(name="list_nat_rules", annotations=READ)
async def mikrotik_list_nat_rules(
    ctx: Context,
    chain_filter: Optional[str] = None,
    action_filter: Optional[str] = None,
    src_address_filter: Optional[str] = None,
    dst_address_filter: Optional[str] = None,
    protocol_filter: Optional[str] = None,
    interface_filter: Optional[str] = None,
    disabled_only: bool = False,
    invalid_only: bool = False
) -> str:
    """
    Lists NAT rules on MikroTik device.

    Args:
        chain_filter: Filter by chain (srcnat, dstnat)
        action_filter: Filter by action
        src_address_filter: Filter by source address
        dst_address_filter: Filter by destination address
        protocol_filter: Filter by protocol
        interface_filter: Filter by interface (in or out)
        disabled_only: Show only disabled rules
        invalid_only: Show only invalid rules

    Returns:
        List of NAT rules
    """
    await ctx.info(f"Listing NAT rules with filters: chain={chain_filter}, action={action_filter}")

    # Build the command
    cmd = "/ip firewall nat print"

    # Add filters
    filters = []
    if chain_filter:
        filters.append(f"chain={chain_filter}")
    if action_filter:
        filters.append(f"action={action_filter}")
    if src_address_filter:
        filters.append(f'src-address~"{src_address_filter}"')
    if dst_address_filter:
        filters.append(f'dst-address~"{dst_address_filter}"')
    if protocol_filter:
        filters.append(f"protocol={protocol_filter}")
    if interface_filter:
        filters.append(f'(in-interface~"{interface_filter}" or out-interface~"{interface_filter}")')
    if disabled_only:
        filters.append("disabled=yes")
    if invalid_only:
        filters.append("invalid=yes")

    if filters:
        cmd += " where " + " ".join(filters)

    result = await execute_mikrotik_command(cmd, ctx)

    # Check for empty result
    if not result or result.strip() == "" or result.strip() == "no such item":
        return "No NAT rules found matching the criteria."

    return f"NAT RULES:\n\n{result}"

@mcp.tool(name="get_nat_rule", annotations=READ)
async def mikrotik_get_nat_rule(ctx: Context, rule_id: str) -> str:
    """
    Gets detailed information about a specific NAT rule.

    Args:
        rule_id: ID of the NAT rule (can be number or *number format)

    Returns:
        Detailed information about the NAT rule
    """
    await ctx.info(f"Getting NAT rule details: rule_id={rule_id}")

    cmd = f"/ip firewall nat print detail where .id={rule_id}"
    result = await execute_mikrotik_command(cmd, ctx)

    if not result or result.strip() == "":
        return f"NAT rule with ID '{rule_id}' not found."

    return f"NAT RULE DETAILS:\n\n{result}"

@mcp.tool(name="update_nat_rule", annotations=WRITE_IDEMPOTENT)
async def mikrotik_update_nat_rule(
    ctx: Context,
    rule_id: str,
    chain: Optional[str] = None,
    action: Optional[str] = None,
    src_address: Optional[str] = None,
    dst_address: Optional[str] = None,
    src_port: Optional[str] = None,
    dst_port: Optional[str] = None,
    protocol: Optional[str] = None,
    in_interface: Optional[str] = None,
    out_interface: Optional[str] = None,
    to_addresses: Optional[str] = None,
    to_ports: Optional[str] = None,
    comment: Optional[str] = None,
    disabled: Optional[bool] = None,
    log: Optional[bool] = None,
    log_prefix: Optional[str] = None
) -> str:
    """
    Updates an existing NAT rule on MikroTik device.

    Args:
        rule_id: ID of the NAT rule to update
        chain: New chain
        action: New action
        src_address: New source address
        dst_address: New destination address
        src_port: New source port
        dst_port: New destination port
        protocol: New protocol
        in_interface: New input interface
        out_interface: New output interface
        to_addresses: New target address
        to_ports: New target port
        comment: New comment
        disabled: Enable/disable the rule
        log: Enable/disable logging
        log_prefix: New log prefix

    Returns:
        Command output or error message
    """
    await ctx.info(f"Updating NAT rule: rule_id={rule_id}")

    # Build the command
    cmd = f"/ip firewall nat set {rule_id}"

    # Add parameters to update
    updates = []
    if chain:
        updates.append(f"chain={chain}")
    if action:
        updates.append(f"action={action}")
    if src_address is not None:
        if src_address == "":
            updates.append("!src-address")
        else:
            updates.append(f"src-address={src_address}")
    if dst_address is not None:
        if dst_address == "":
            updates.append("!dst-address")
        else:
            updates.append(f"dst-address={dst_address}")
    if src_port is not None:
        if src_port == "":
            updates.append("!src-port")
        else:
            updates.append(f"src-port={src_port}")
    if dst_port is not None:
        if dst_port == "":
            updates.append("!dst-port")
        else:
            updates.append(f"dst-port={dst_port}")
    if protocol is not None:
        if protocol == "":
            updates.append("!protocol")
        else:
            updates.append(f"protocol={protocol}")
    if in_interface is not None:
        if in_interface == "":
            updates.append("!in-interface")
        else:
            updates.append(f'in-interface="{in_interface}"')
    if out_interface is not None:
        if out_interface == "":
            updates.append("!out-interface")
        else:
            updates.append(f'out-interface="{out_interface}"')
    if to_addresses is not None:
        if to_addresses == "":
            updates.append("!to-addresses")
        else:
            updates.append(f"to-addresses={to_addresses}")
    if to_ports is not None:
        if to_ports == "":
            updates.append("!to-ports")
        else:
            updates.append(f"to-ports={to_ports}")
    if comment is not None:
        updates.append(f'comment="{comment}"')
    if disabled is not None:
        updates.append(f'disabled={"yes" if disabled else "no"}')
    if log is not None:
        updates.append(f'log={"yes" if log else "no"}')
        if log and log_prefix:
            updates.append(f'log-prefix="{log_prefix}"')

    if not updates:
        return "No updates specified."

    cmd += " " + " ".join(updates)

    result = await execute_mikrotik_command(cmd, ctx)

    # Check if update was successful
    if "failure:" in result.lower() or "error" in result.lower():
        return f"Failed to update NAT rule: {result}"

    # Get the updated rule details
    details_cmd = f"/ip firewall nat print detail where .id={rule_id}"
    details = await execute_mikrotik_command(details_cmd, ctx)

    return f"NAT rule updated successfully:\n\n{details}"

@mcp.tool(name="remove_nat_rule", annotations=DESTRUCTIVE)
async def mikrotik_remove_nat_rule(ctx: Context, rule_id: str) -> str:
    """
    Removes a NAT rule from MikroTik device.

    Args:
        rule_id: ID of the NAT rule to remove

    Returns:
        Command output or error message
    """
    await ctx.info(f"Removing NAT rule: rule_id={rule_id}")

    # First check if the rule exists
    check_cmd = f"/ip firewall nat print count-only where .id={rule_id}"
    count = await execute_mikrotik_command(check_cmd, ctx)

    if count.strip() == "0":
        return f"NAT rule with ID '{rule_id}' not found."

    # Remove the rule
    cmd = f"/ip firewall nat remove {rule_id}"
    result = await execute_mikrotik_command(cmd, ctx)

    if "failure:" in result.lower() or "error" in result.lower():
        return f"Failed to remove NAT rule: {result}"

    return f"NAT rule with ID '{rule_id}' removed successfully."

@mcp.tool(name="move_nat_rule", annotations=WRITE_IDEMPOTENT)
async def mikrotik_move_nat_rule(ctx: Context, rule_id: str, destination: int) -> str:
    """
    Moves a NAT rule to a different position in the chain.

    Args:
        rule_id: ID of the NAT rule to move
        destination: Destination position (0-based index)

    Returns:
        Command output or error message
    """
    await ctx.info(f"Moving NAT rule: rule_id={rule_id} to position {destination}")

    # Check if the rule exists
    check_cmd = f"/ip firewall nat print count-only where .id={rule_id}"
    count = await execute_mikrotik_command(check_cmd, ctx)

    if count.strip() == "0":
        return f"NAT rule with ID '{rule_id}' not found."

    # Move the rule
    cmd = f"/ip firewall nat move {rule_id} destination={destination}"
    result = await execute_mikrotik_command(cmd, ctx)

    if "failure:" in result.lower() or "error" in result.lower():
        return f"Failed to move NAT rule: {result}"

    return f"NAT rule with ID '{rule_id}' moved to position {destination}."

@mcp.tool(name="enable_nat_rule", annotations=WRITE_IDEMPOTENT)
async def mikrotik_enable_nat_rule(ctx: Context, rule_id: str) -> str:
    """
    Enables a NAT rule.

    Args:
        rule_id: ID of the NAT rule to enable

    Returns:
        Command output or error message
    """
    return await mikrotik_update_nat_rule(rule_id, disabled=False, ctx=ctx)

@mcp.tool(name="disable_nat_rule", annotations=WRITE_IDEMPOTENT)
async def mikrotik_disable_nat_rule(ctx: Context, rule_id: str) -> str:
    """
    Disables a NAT rule.

    Args:
        rule_id: ID of the NAT rule to disable

    Returns:
        Command output or error message
    """
    return await mikrotik_update_nat_rule(rule_id, disabled=True, ctx=ctx)
