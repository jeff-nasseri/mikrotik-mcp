from typing import Literal, Optional, List
from mcp.server.fastmcp import Context
from ..app import mcp, READ, WRITE, WRITE_IDEMPOTENT, DESTRUCTIVE, DANGEROUS
from ..connector import execute_mikrotik_command

@mcp.tool(name="create_filter_rule", annotations=WRITE)
async def mikrotik_create_filter_rule(
    chain: Literal["input", "forward", "output"],
    action: Literal["accept", "drop", "reject", "jump", "log", "passthrough", "return", "tarpit", "fasttrack-connection"],
    ctx: Context,
    src_address: Optional[str] = None,
    dst_address: Optional[str] = None,
    src_port: Optional[str] = None,
    dst_port: Optional[str] = None,
    protocol: Optional[str] = None,
    in_interface: Optional[str] = None,
    out_interface: Optional[str] = None,
    connection_state: Optional[str] = None,
    connection_nat_state: Optional[str] = None,
    src_address_list: Optional[str] = None,
    dst_address_list: Optional[str] = None,
    limit: Optional[str] = None,
    tcp_flags: Optional[str] = None,
    comment: Optional[str] = None,
    disabled: bool = False,
    log: bool = False,
    log_prefix: Optional[str] = None,
    place_before: Optional[str] = None
) -> str:
    """
    Creates a firewall filter rule on MikroTik device.

    Args:
        chain: Filter chain (input, forward, output)
        action: Action to take (accept, drop, reject, jump, log, passthrough, return)
        src_address: Source IP address or range
        dst_address: Destination IP address or range
        src_port: Source port or range
        dst_port: Destination port or range
        protocol: Protocol (tcp, udp, icmp, etc.)
        in_interface: Input interface
        out_interface: Output interface
        connection_state: Connection state (established, related, new, invalid)
        connection_nat_state: NAT state (srcnat, dstnat)
        src_address_list: Source address list name
        dst_address_list: Destination address list name
        limit: Rate limit (e.g., "10,5:packet")
        tcp_flags: TCP flags to match
        comment: Optional comment for the rule
        disabled: Whether to disable the rule after creation
        log: Whether to log packets matching this rule
        log_prefix: Prefix for log entries
        place_before: Place this rule before another rule (by number)

    Returns:
        Command output or error message
    """
    await ctx.info(f"Creating firewall filter rule: chain={chain}, action={action}")

    # Build the command
    cmd = f"/ip firewall filter add chain={chain} action={action}"

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

    if connection_state:
        cmd += f" connection-state={connection_state}"

    if connection_nat_state:
        cmd += f" connection-nat-state={connection_nat_state}"

    if src_address_list:
        cmd += f' src-address-list="{src_address_list}"'

    if dst_address_list:
        cmd += f' dst-address-list="{dst_address_list}"'

    if limit:
        cmd += f" limit={limit}"

    if tcp_flags:
        cmd += f" tcp-flags={tcp_flags}"

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
            details_cmd = f"/ip firewall filter print detail where .id={rule_id}"
            details = await execute_mikrotik_command(details_cmd, ctx)

            if details.strip():
                return f"Firewall filter rule created successfully:\n\n{details}"
            else:
                return f"Firewall filter rule created with ID: {result}"
        else:
            # Error occurred
            return f"Failed to create firewall filter rule: {result}"
    else:
        # No output might mean success, let's check
        details_cmd = "/ip firewall filter print detail count-only"
        count = await execute_mikrotik_command(details_cmd, ctx)

        if count.strip().isdigit() and int(count.strip()) > 0:
            # Get the last rule
            last_rule_cmd = f"/ip firewall filter print detail from={int(count.strip())-1}"
            details = await execute_mikrotik_command(last_rule_cmd, ctx)
            return f"Firewall filter rule created successfully:\n\n{details}"
        else:
            return "Firewall filter rule creation completed but unable to verify."

@mcp.tool(name="list_filter_rules", annotations=READ)
async def mikrotik_list_filter_rules(
    ctx: Context,
    chain_filter: Optional[str] = None,
    action_filter: Optional[str] = None,
    src_address_filter: Optional[str] = None,
    dst_address_filter: Optional[str] = None,
    protocol_filter: Optional[str] = None,
    interface_filter: Optional[str] = None,
    disabled_only: bool = False,
    invalid_only: bool = False,
    dynamic_only: bool = False
) -> str:
    """
    Lists firewall filter rules on MikroTik device.

    Args:
        chain_filter: Filter by chain (input, forward, output)
        action_filter: Filter by action
        src_address_filter: Filter by source address
        dst_address_filter: Filter by destination address
        protocol_filter: Filter by protocol
        interface_filter: Filter by interface (in or out)
        disabled_only: Show only disabled rules
        invalid_only: Show only invalid rules
        dynamic_only: Show only dynamic rules

    Returns:
        List of firewall filter rules
    """
    await ctx.info(f"Listing firewall filter rules with filters: chain={chain_filter}, action={action_filter}")

    # Build the command
    cmd = "/ip firewall filter print"

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
    if dynamic_only:
        filters.append("dynamic=yes")

    if filters:
        cmd += " where " + " ".join(filters)

    result = await execute_mikrotik_command(cmd, ctx)

    # Check for empty result
    if not result or result.strip() == "" or result.strip() == "no such item":
        return "No firewall filter rules found matching the criteria."

    return f"FIREWALL FILTER RULES:\n\n{result}"

@mcp.tool(name="get_filter_rule", annotations=READ)
async def mikrotik_get_filter_rule(rule_id: str, ctx: Context) -> str:
    """
    Gets detailed information about a specific firewall filter rule.

    Args:
        rule_id: ID of the filter rule (can be number or *number format)

    Returns:
        Detailed information about the filter rule
    """
    await ctx.info(f"Getting firewall filter rule details: rule_id={rule_id}")

    cmd = f"/ip firewall filter print detail where .id={rule_id}"
    result = await execute_mikrotik_command(cmd, ctx)

    if not result or result.strip() == "":
        return f"Firewall filter rule with ID '{rule_id}' not found."

    return f"FIREWALL FILTER RULE DETAILS:\n\n{result}"

@mcp.tool(name="update_filter_rule", annotations=WRITE_IDEMPOTENT)
async def mikrotik_update_filter_rule(
    rule_id: str,
    ctx: Context,
    chain: Optional[str] = None,
    action: Optional[str] = None,
    src_address: Optional[str] = None,
    dst_address: Optional[str] = None,
    src_port: Optional[str] = None,
    dst_port: Optional[str] = None,
    protocol: Optional[str] = None,
    in_interface: Optional[str] = None,
    out_interface: Optional[str] = None,
    connection_state: Optional[str] = None,
    connection_nat_state: Optional[str] = None,
    src_address_list: Optional[str] = None,
    dst_address_list: Optional[str] = None,
    limit: Optional[str] = None,
    tcp_flags: Optional[str] = None,
    comment: Optional[str] = None,
    disabled: Optional[bool] = None,
    log: Optional[bool] = None,
    log_prefix: Optional[str] = None
) -> str:
    """
    Updates an existing firewall filter rule on MikroTik device.

    Args:
        rule_id: ID of the filter rule to update
        chain: New chain
        action: New action
        src_address: New source address
        dst_address: New destination address
        src_port: New source port
        dst_port: New destination port
        protocol: New protocol
        in_interface: New input interface
        out_interface: New output interface
        connection_state: New connection state
        connection_nat_state: New NAT state
        src_address_list: New source address list
        dst_address_list: New destination address list
        limit: New rate limit
        tcp_flags: New TCP flags
        comment: New comment
        disabled: Enable/disable the rule
        log: Enable/disable logging
        log_prefix: New log prefix

    Returns:
        Command output or error message
    """
    await ctx.info(f"Updating firewall filter rule: rule_id={rule_id}")

    # Build the command
    cmd = f"/ip firewall filter set {rule_id}"

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
    if connection_state is not None:
        if connection_state == "":
            updates.append("!connection-state")
        else:
            updates.append(f"connection-state={connection_state}")
    if connection_nat_state is not None:
        if connection_nat_state == "":
            updates.append("!connection-nat-state")
        else:
            updates.append(f"connection-nat-state={connection_nat_state}")
    if src_address_list is not None:
        if src_address_list == "":
            updates.append("!src-address-list")
        else:
            updates.append(f'src-address-list="{src_address_list}"')
    if dst_address_list is not None:
        if dst_address_list == "":
            updates.append("!dst-address-list")
        else:
            updates.append(f'dst-address-list="{dst_address_list}"')
    if limit is not None:
        if limit == "":
            updates.append("!limit")
        else:
            updates.append(f"limit={limit}")
    if tcp_flags is not None:
        if tcp_flags == "":
            updates.append("!tcp-flags")
        else:
            updates.append(f"tcp-flags={tcp_flags}")
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
        return f"Failed to update firewall filter rule: {result}"

    # Get the updated rule details
    details_cmd = f"/ip firewall filter print detail where .id={rule_id}"
    details = await execute_mikrotik_command(details_cmd, ctx)

    return f"Firewall filter rule updated successfully:\n\n{details}"

@mcp.tool(name="remove_filter_rule", annotations=DESTRUCTIVE)
async def mikrotik_remove_filter_rule(rule_id: str, ctx: Context) -> str:
    """
    Removes a firewall filter rule from MikroTik device.

    Args:
        rule_id: ID of the filter rule to remove

    Returns:
        Command output or error message
    """
    await ctx.info(f"Removing firewall filter rule: rule_id={rule_id}")

    # First check if the rule exists
    check_cmd = f"/ip firewall filter print count-only where .id={rule_id}"
    count = await execute_mikrotik_command(check_cmd, ctx)

    if count.strip() == "0":
        return f"Firewall filter rule with ID '{rule_id}' not found."

    # Remove the rule
    cmd = f"/ip firewall filter remove {rule_id}"
    result = await execute_mikrotik_command(cmd, ctx)

    if "failure:" in result.lower() or "error" in result.lower():
        return f"Failed to remove firewall filter rule: {result}"

    return f"Firewall filter rule with ID '{rule_id}' removed successfully."

@mcp.tool(name="move_filter_rule", annotations=WRITE_IDEMPOTENT)
async def mikrotik_move_filter_rule(rule_id: str, destination: int, ctx: Context) -> str:
    """
    Moves a firewall filter rule to a different position in the chain.

    Args:
        rule_id: ID of the filter rule to move
        destination: Destination position (0-based index)

    Returns:
        Command output or error message
    """
    await ctx.info(f"Moving firewall filter rule: rule_id={rule_id} to position {destination}")

    # Check if the rule exists
    check_cmd = f"/ip firewall filter print count-only where .id={rule_id}"
    count = await execute_mikrotik_command(check_cmd, ctx)

    if count.strip() == "0":
        return f"Firewall filter rule with ID '{rule_id}' not found."

    # Move the rule
    cmd = f"/ip firewall filter move {rule_id} destination={destination}"
    result = await execute_mikrotik_command(cmd, ctx)

    if "failure:" in result.lower() or "error" in result.lower():
        return f"Failed to move firewall filter rule: {result}"

    return f"Firewall filter rule with ID '{rule_id}' moved to position {destination}."

@mcp.tool(name="enable_filter_rule", annotations=WRITE_IDEMPOTENT)
async def mikrotik_enable_filter_rule(rule_id: str, ctx: Context) -> str:
    """
    Enables a firewall filter rule.

    Args:
        rule_id: ID of the filter rule to enable

    Returns:
        Command output or error message
    """
    return await mikrotik_update_filter_rule(rule_id, disabled=False, ctx=ctx)

@mcp.tool(name="disable_filter_rule", annotations=WRITE_IDEMPOTENT)
async def mikrotik_disable_filter_rule(rule_id: str, ctx: Context) -> str:
    """
    Disables a firewall filter rule.

    Args:
        rule_id: ID of the filter rule to disable

    Returns:
        Command output or error message
    """
    return await mikrotik_update_filter_rule(rule_id, disabled=True, ctx=ctx)

@mcp.tool(name="create_basic_firewall_setup", annotations=DANGEROUS)
async def mikrotik_create_basic_firewall_setup(ctx: Context) -> str:
    """
    Creates a basic firewall setup with common security rules.

    Returns:
        Setup result
    """
    await ctx.info("Creating basic firewall setup")

    results = []

    # Allow established and related connections
    cmd1 = "/ip firewall filter add chain=input action=accept connection-state=established,related comment=\"Accept established,related\""
    result1 = await execute_mikrotik_command(cmd1, ctx)
    results.append("Rule 1 (established/related): " + ("Created" if not result1 or "*" in result1 else result1))

    # Drop invalid connections
    cmd2 = "/ip firewall filter add chain=input action=drop connection-state=invalid comment=\"Drop invalid\""
    result2 = await execute_mikrotik_command(cmd2, ctx)
    results.append("Rule 2 (drop invalid): " + ("Created" if not result2 or "*" in result2 else result2))

    # Allow ICMP
    cmd3 = "/ip firewall filter add chain=input action=accept protocol=icmp comment=\"Accept ICMP\""
    result3 = await execute_mikrotik_command(cmd3, ctx)
    results.append("Rule 3 (ICMP): " + ("Created" if not result3 or "*" in result3 else result3))

    # Allow management from specific network
    cmd4 = "/ip firewall filter add chain=input action=accept src-address=192.168.88.0/24 comment=\"Accept management network\""
    result4 = await execute_mikrotik_command(cmd4, ctx)
    results.append("Rule 4 (management network): " + ("Created" if not result4 or "*" in result4 else result4))

    # Drop everything else
    cmd5 = "/ip firewall filter add chain=input action=drop comment=\"Drop everything else\""
    result5 = await execute_mikrotik_command(cmd5, ctx)
    results.append("Rule 5 (drop all): " + ("Created" if not result5 or "*" in result5 else result5))

    return "BASIC FIREWALL SETUP RESULTS:\n\n" + "\n".join(results)
