from typing import Optional, List
from ..connector import execute_mikrotik_command
from ..logger import app_logger
from ..app import mcp, READ, WRITE, WRITE_IDEMPOTENT, DESTRUCTIVE

@mcp.tool(name="create_ip_pool", annotations=WRITE)
def mikrotik_create_ip_pool(
    name: str,
    ranges: str,
    next_pool: Optional[str] = None,
    comment: Optional[str] = None
) -> str:
    """
    Creates an IP pool on MikroTik device.
    
    Args:
        name: Name of the IP pool
        ranges: IP address ranges (e.g., "192.168.1.10-192.168.1.50")
        next_pool: Name of the next pool to use when this one is exhausted
        comment: Optional comment for the pool
    
    Returns:
        Command output or error message
    """
    app_logger.info(f"Creating IP pool: name={name}, ranges={ranges}")
    
    # Build the command
    cmd = f"/ip pool add name={name} ranges={ranges}"
    
    # Add optional parameters
    if next_pool:
        cmd += f' next-pool="{next_pool}"'
    
    if comment:
        cmd += f' comment="{comment}"'
    
    result = execute_mikrotik_command(cmd)
    
    # Check if creation was successful
    if result.strip():
        # MikroTik returns the ID of created item on success
        if "*" in result or result.strip().isdigit():
            # Success - get the details
            details_cmd = f'/ip pool print detail where name="{name}"'
            details = execute_mikrotik_command(details_cmd)
            
            if details.strip():
                return f"IP pool created successfully:\n\n{details}"
            else:
                return f"IP pool created with ID: {result}"
        else:
            # Error occurred
            return f"Failed to create IP pool: {result}"
    else:
        # No output might mean success, let's check
        details_cmd = f'/ip pool print detail where name="{name}"'
        details = execute_mikrotik_command(details_cmd)
        
        if details.strip():
            return f"IP pool created successfully:\n\n{details}"
        else:
            return "IP pool creation completed but unable to verify."

@mcp.tool(name="list_ip_pools", annotations=READ)
def mikrotik_list_ip_pools(
    name_filter: Optional[str] = None,
    ranges_filter: Optional[str] = None,
    include_used: bool = False
) -> str:
    """
    Lists IP pools on MikroTik device.
    
    Args:
        name_filter: Filter by pool name (partial match)
        ranges_filter: Filter by IP ranges
        include_used: Include information about used addresses
    
    Returns:
        List of IP pools
    """
    app_logger.info(f"Listing IP pools with filters: name={name_filter}, ranges={ranges_filter}")
    
    # Build the command
    cmd = "/ip pool print"
    
    if include_used:
        cmd += " detail"
    
    # Add filters
    filters = []
    if name_filter:
        filters.append(f'name~"{name_filter}"')
    if ranges_filter:
        filters.append(f'ranges~"{ranges_filter}"')
    
    if filters:
        cmd += " where " + " ".join(filters)
    
    result = execute_mikrotik_command(cmd)
    
    # Check for empty result
    if not result or result.strip() == "" or result.strip() == "no such item":
        return "No IP pools found matching the criteria."
    
    if include_used:
        # Parse and add used information
        result_lines = result.strip().split('\n')
        output_lines = []
        
        for line in result_lines:
            output_lines.append(line)
            if "name=" in line:
                # Extract pool name from the line
                name_start = line.find('name="') + 6
                name_end = line.find('"', name_start)
                if name_start > 5 and name_end > name_start:
                    pool_name = line[name_start:name_end]
                    # Get used addresses for this pool
                    used_cmd = f'/ip pool used print count-only where pool="{pool_name}"'
                    used_count = execute_mikrotik_command(used_cmd)
                    if used_count.strip().isdigit():
                        output_lines.append(f"      used-addresses={used_count.strip()}")
        
        return f"IP POOLS:\n\n" + "\n".join(output_lines)
    
    return f"IP POOLS:\n\n{result}"

@mcp.tool(name="get_ip_pool", annotations=READ)
def mikrotik_get_ip_pool(name: str) -> str:
    """
    Gets detailed information about a specific IP pool.
    
    Args:
        name: Name of the IP pool
    
    Returns:
        Detailed information about the IP pool
    """
    app_logger.info(f"Getting IP pool details: name={name}")
    
    cmd = f'/ip pool print detail where name="{name}"'
    result = execute_mikrotik_command(cmd)
    
    if not result or result.strip() == "":
        return f"IP pool '{name}' not found."
    
    # Get used addresses count
    used_cmd = f'/ip pool used print count-only where pool="{name}"'
    used_count = execute_mikrotik_command(used_cmd)
    
    if used_count.strip().isdigit():
        return f"IP POOL DETAILS:\n\n{result}\n      used-addresses={used_count.strip()}"
    
    return f"IP POOL DETAILS:\n\n{result}"

@mcp.tool(name="update_ip_pool", annotations=WRITE_IDEMPOTENT)
def mikrotik_update_ip_pool(
    name: str,
    new_name: Optional[str] = None,
    ranges: Optional[str] = None,
    next_pool: Optional[str] = None,
    comment: Optional[str] = None
) -> str:
    """
    Updates an existing IP pool on MikroTik device.
    
    Args:
        name: Current name of the IP pool
        new_name: New name for the pool
        ranges: New IP address ranges
        next_pool: New next pool reference
        comment: New comment
    
    Returns:
        Command output or error message
    """
    app_logger.info(f"Updating IP pool: name={name}")
    
    # Build the command
    cmd = f'/ip pool set [find name="{name}"]'
    
    # Add parameters to update
    updates = []
    if new_name:
        updates.append(f'name={new_name}')
    if ranges:
        updates.append(f'ranges={ranges}')
    if next_pool is not None:
        if next_pool == "":
            updates.append('!next-pool')
        else:
            updates.append(f'next-pool="{next_pool}"')
    if comment is not None:
        updates.append(f'comment="{comment}"')
    
    if not updates:
        return "No updates specified."
    
    cmd += " " + " ".join(updates)
    
    result = execute_mikrotik_command(cmd)
    
    # Check if update was successful
    if "failure:" in result.lower() or "error" in result.lower():
        return f"Failed to update IP pool: {result}"
    
    # Get the updated pool details
    details_name = new_name if new_name else name
    details_cmd = f'/ip pool print detail where name="{details_name}"'
    details = execute_mikrotik_command(details_cmd)
    
    return f"IP pool updated successfully:\n\n{details}"

@mcp.tool(name="remove_ip_pool", annotations=DESTRUCTIVE)
def mikrotik_remove_ip_pool(name: str) -> str:
    """
    Removes an IP pool from MikroTik device.
    
    Args:
        name: Name of the IP pool to remove
    
    Returns:
        Command output or error message
    """
    app_logger.info(f"Removing IP pool: name={name}")
    
    # First check if the pool exists
    check_cmd = f'/ip pool print count-only where name="{name}"'
    count = execute_mikrotik_command(check_cmd)
    
    if count.strip() == "0":
        return f"IP pool '{name}' not found."
    
    # Check if pool is in use
    pool_used_cmd = f'/ip pool used print count-only where pool="{name}"'
    used_count = execute_mikrotik_command(pool_used_cmd)
    
    if used_count.strip() != "0":
        return f"Cannot remove IP pool '{name}': {used_count.strip()} addresses are currently in use."
    
    # Check if pool is referenced by DHCP servers
    dhcp_check_cmd = f'/ip dhcp-server print count-only where address-pool="{name}"'
    dhcp_count = execute_mikrotik_command(dhcp_check_cmd)
    
    if dhcp_count.strip() != "0":
        return f"Cannot remove IP pool '{name}': It is used by {dhcp_count.strip()} DHCP server(s)."
    
    # Remove the pool
    cmd = f'/ip pool remove [find name="{name}"]'
    result = execute_mikrotik_command(cmd)
    
    if "failure:" in result.lower() or "error" in result.lower():
        return f"Failed to remove IP pool: {result}"
    
    return f"IP pool '{name}' removed successfully."

@mcp.tool(name="list_ip_pool_used", annotations=READ)
def mikrotik_list_ip_pool_used(
    pool_name: Optional[str] = None,
    address_filter: Optional[str] = None,
    mac_filter: Optional[str] = None,
    info_filter: Optional[str] = None
) -> str:
    """
    Lists used addresses from IP pools.
    
    Args:
        pool_name: Filter by pool name
        address_filter: Filter by IP address
        mac_filter: Filter by MAC address
        info_filter: Filter by info field
    
    Returns:
        List of used addresses
    """
    app_logger.info(f"Listing used IP pool addresses: pool={pool_name}, address={address_filter}")
    
    cmd = "/ip pool used print"
    
    # Add filters
    filters = []
    if pool_name:
        filters.append(f'pool="{pool_name}"')
    if address_filter:
        filters.append(f'address~"{address_filter}"')
    if mac_filter:
        filters.append(f'mac-address~"{mac_filter}"')
    if info_filter:
        filters.append(f'info~"{info_filter}"')
    
    if filters:
        cmd += " where " + " ".join(filters)
    
    result = execute_mikrotik_command(cmd)
    
    if not result or result.strip() == "" or result.strip() == "no such item":
        return "No used addresses found matching the criteria."
    
    return f"USED IP POOL ADDRESSES:\n\n{result}"

@mcp.tool(name="expand_ip_pool", annotations=WRITE_IDEMPOTENT)
def mikrotik_expand_ip_pool(name: str, additional_ranges: str) -> str:
    """
    Expands an existing IP pool by adding more ranges.
    
    Args:
        name: Name of the IP pool to expand
        additional_ranges: Additional IP ranges to add
    
    Returns:
        Command output or error message
    """
    app_logger.info(f"Expanding IP pool: name={name}, additional_ranges={additional_ranges}")
    
    # Get current ranges
    get_cmd = f'/ip pool print detail where name="{name}"'
    current = execute_mikrotik_command(get_cmd)
    
    if not current or "no such item" in current:
        return f"IP pool '{name}' not found."
    
    # Extract current ranges
    import re
    ranges_match = re.search(r'ranges=([^\s]+)', current)
    if not ranges_match:
        return "Unable to determine current ranges."
    
    current_ranges = ranges_match.group(1)
    
    # Combine ranges
    new_ranges = f"{current_ranges},{additional_ranges}"
    
    # Update the pool
    return mikrotik_update_ip_pool(name, ranges=new_ranges)