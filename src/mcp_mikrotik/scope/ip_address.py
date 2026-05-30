from typing import Optional

from ..connector import execute_mikrotik_command
from mcp.server.fastmcp import Context
from ..app import mcp, READ, WRITE, DESTRUCTIVE, annotate
from ..security import SecurityError, V, validate_field

@mcp.tool(name="add_ip_address", annotations=annotate(WRITE, "Add IP Address"))
async def mikrotik_add_ip_address(
    ctx: Context,
    address: str,
    interface: str,
    network: Optional[str] = None,
    broadcast: Optional[str] = None,
    comment: Optional[str] = None,
    disabled: bool = False
) -> str:
    """Adds an IP address to an interface on the MikroTik device."""
    validate_field(address, V.IP_CIDR, "address")
    validate_field(interface, V.INTERFACE_NAME, "interface")
    validate_field(network, V.IP_CIDR, "network")
    validate_field(comment, V.COMMENT, "comment")
    await ctx.info(f"Adding IP address: address={address}, interface={interface}")

    # Build the command
    cmd = f"/ip address add address={address} interface={interface}"

    # Add optional parameters
    if network:
        cmd += f" network={network}"

    if broadcast:
        cmd += f" broadcast={broadcast}"

    if comment:
        cmd += f' comment="{comment}"'

    if disabled:
        cmd += " disabled=yes"

    result = await execute_mikrotik_command(cmd, ctx)

    if "failure:" in result.lower() or "error" in result.lower():
        return f"Failed to add IP address: {result}"

    # Get the created address details
    details_cmd = f'/ip address print detail where address="{address}"'
    details = await execute_mikrotik_command(details_cmd, ctx)

    return f"IP address added successfully:\n\n{details}"

@mcp.tool(name="list_ip_addresses", annotations=annotate(READ, "List IP Addresses"))
async def mikrotik_list_ip_addresses(
    ctx: Context,
    interface_filter: Optional[str] = None,
    address_filter: Optional[str] = None,
    network_filter: Optional[str] = None,
    disabled_only: bool = False,
    dynamic_only: bool = False
) -> str:
    """Lists IP addresses on the MikroTik device."""
    validate_field(interface_filter, V.INTERFACE_NAME, "interface_filter")
    validate_field(address_filter, V.IP_CIDR, "address_filter")
    validate_field(network_filter, V.IP_CIDR, "network_filter")
    await ctx.info(f"Listing IP addresses with filters: interface={interface_filter}, address={address_filter}")

    # Build the command
    cmd = "/ip address print"

    # Add filters
    filters = []
    if interface_filter:
        filters.append(f'interface="{interface_filter}"')
    if address_filter:
        filters.append(f'address~"{address_filter}"')
    if network_filter:
        filters.append(f'network="{network_filter}"')
    if disabled_only:
        filters.append("disabled=yes")
    if dynamic_only:
        filters.append("dynamic=yes")

    if filters:
        cmd += " where " + " ".join(filters)

    result = await execute_mikrotik_command(cmd, ctx)

    if not result or result.strip() == "":
        return "No IP addresses found matching the criteria."

    return f"IP ADDRESSES:\n\n{result}"

@mcp.tool(name="get_ip_address", annotations=annotate(READ, "Get IP Address"))
async def mikrotik_get_ip_address(ctx: Context, address_id: str) -> str:
    """Gets detailed information about a specific IP address by ID or address value."""
    validate_field(address_id, V.COMMENT, "address_id")
    await ctx.info(f"Getting IP address details: address_id={address_id}")

    # Try to find by ID first, then by address
    cmd = f'/ip address print detail where .id="{address_id}"'
    result = await execute_mikrotik_command(cmd, ctx)

    if not result or result.strip() == "":
        # Try finding by address value
        cmd = f'/ip address print detail where address="{address_id}"'
        result = await execute_mikrotik_command(cmd, ctx)

    if not result or result.strip() == "":
        return f"IP address '{address_id}' not found."

    return f"IP ADDRESS DETAILS:\n\n{result}"

@mcp.tool(name="remove_ip_address", annotations=annotate(DESTRUCTIVE, "Remove IP Address"))
async def mikrotik_remove_ip_address(ctx: Context, address_id: str) -> str:
    """Removes an IP address from the MikroTik device by ID or address value."""
    validate_field(address_id, V.COMMENT, "address_id")
    await ctx.info(f"Removing IP address: address_id={address_id}")

    # Try to find by ID first
    check_cmd = f'/ip address print count-only where .id="{address_id}"'
    count = await execute_mikrotik_command(check_cmd, ctx)

    if count.strip() == "0":
        # Try finding by address value
        check_cmd = f'/ip address print count-only where address="{address_id}"'
        count = await execute_mikrotik_command(check_cmd, ctx)

        if count.strip() == "0":
            return f"IP address '{address_id}' not found."

        # Remove by address value
        cmd = f'/ip address remove [find address="{address_id}"]'
    else:
        # Remove by ID
        cmd = f'/ip address remove [find .id="{address_id}"]'

    result = await execute_mikrotik_command(cmd, ctx)

    if "failure:" in result.lower() or "error" in result.lower():
        return f"Failed to remove IP address: {result}"

    return f"IP address '{address_id}' removed successfully."
