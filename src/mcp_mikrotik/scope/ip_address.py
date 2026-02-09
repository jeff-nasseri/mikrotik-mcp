from typing import Optional

from ..connector import execute_mikrotik_command
from ..logger import app_logger
from ..app import mcp

@mcp.tool()
def mikrotik_add_ip_address(
    address: str,
    interface: str,
    network: Optional[str] = None,
    broadcast: Optional[str] = None,
    comment: Optional[str] = None,
    disabled: bool = False
) -> str:
    """
    Adds an IP address to an interface on MikroTik device.
    
    Args:
        address: IP address with prefix (e.g., "192.168.1.1/24")
        interface: Interface name (e.g., "ether1", "vlan100")
        network: Network address (optional, calculated automatically)
        broadcast: Broadcast address (optional, calculated automatically)
        comment: Optional comment
        disabled: Whether to disable the address after creation
    
    Returns:
        Command output or error message
    """
    app_logger.info(f"Adding IP address: address={address}, interface={interface}")
    
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
    
    result = execute_mikrotik_command(cmd)
    
    if "failure:" in result.lower() or "error" in result.lower():
        return f"Failed to add IP address: {result}"
    
    # Get the created address details
    details_cmd = f'/ip address print detail where address="{address}"'
    details = execute_mikrotik_command(details_cmd)
    
    return f"IP address added successfully:\n\n{details}"

@mcp.tool()
def mikrotik_list_ip_addresses(
    interface_filter: Optional[str] = None,
    address_filter: Optional[str] = None,
    network_filter: Optional[str] = None,
    disabled_only: bool = False,
    dynamic_only: bool = False
) -> str:
    """
    Lists IP addresses on MikroTik device.
    
    Args:
        interface_filter: Filter by interface name
        address_filter: Filter by IP address (partial match)
        network_filter: Filter by network
        disabled_only: Show only disabled addresses
        dynamic_only: Show only dynamic addresses
    
    Returns:
        List of IP addresses
    """
    app_logger.info(f"Listing IP addresses with filters: interface={interface_filter}, address={address_filter}")
    
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
    
    result = execute_mikrotik_command(cmd)
    
    if not result or result.strip() == "":
        return "No IP addresses found matching the criteria."
    
    return f"IP ADDRESSES:\n\n{result}"

@mcp.tool()
def mikrotik_get_ip_address(address_id: str) -> str:
    """
    Gets detailed information about a specific IP address.
    
    Args:
        address_id: IP address ID or address value
    
    Returns:
        Detailed information about the IP address
    """
    app_logger.info(f"Getting IP address details: address_id={address_id}")
    
    # Try to find by ID first, then by address
    cmd = f'/ip address print detail where .id="{address_id}"'
    result = execute_mikrotik_command(cmd)
    
    if not result or result.strip() == "":
        # Try finding by address value
        cmd = f'/ip address print detail where address="{address_id}"'
        result = execute_mikrotik_command(cmd)
    
    if not result or result.strip() == "":
        return f"IP address '{address_id}' not found."
    
    return f"IP ADDRESS DETAILS:\n\n{result}"

@mcp.tool()
def mikrotik_remove_ip_address(address_id: str) -> str:
    """
    Removes an IP address from MikroTik device.
    
    Args:
        address_id: IP address ID or address value to remove
    
    Returns:
        Command output or error message
    """
    app_logger.info(f"Removing IP address: address_id={address_id}")
    
    # Try to find by ID first
    check_cmd = f'/ip address print count-only where .id="{address_id}"'
    count = execute_mikrotik_command(check_cmd)
    
    if count.strip() == "0":
        # Try finding by address value
        check_cmd = f'/ip address print count-only where address="{address_id}"'
        count = execute_mikrotik_command(check_cmd)
        
        if count.strip() == "0":
            return f"IP address '{address_id}' not found."
        
        # Remove by address value
        cmd = f'/ip address remove [find address="{address_id}"]'
    else:
        # Remove by ID
        cmd = f'/ip address remove [find .id="{address_id}"]'
    
    result = execute_mikrotik_command(cmd)
    
    if "failure:" in result.lower() or "error" in result.lower():
        return f"Failed to remove IP address: {result}"
    
    return f"IP address '{address_id}' removed successfully."
