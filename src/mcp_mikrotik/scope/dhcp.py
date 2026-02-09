from typing import List, Literal, Optional

from ..app import mcp, READ, WRITE, DESTRUCTIVE
from ..connector import execute_mikrotik_command
from ..logger import app_logger


@mcp.tool(name="create_dhcp_server", annotations=WRITE)
def mikrotik_create_dhcp_server(
    name: str,
    interface: str,
    lease_time: str = "1d",
    address_pool: Optional[str] = None,
    disabled: bool = False,
    authoritative: Literal["yes", "no", "after-2sec-delay"] = "yes",
    delay_threshold: Optional[str] = None,
    comment: Optional[str] = None
) -> str:
    """
    Creates a DHCP server on MikroTik device.
    
    Args:
        name: Name of the DHCP server
        interface: Interface to bind the DHCP server to
        lease_time: Default lease time (default: "1d")
        address_pool: Address pool name (optional)
        disabled: Whether to disable the server after creation
        authoritative: Authoritative mode (yes/no/after-2sec-delay)
        delay_threshold: Delay threshold for authoritative mode
        comment: Optional comment
    
    Returns:
        Command output or error message
    """
    app_logger.info(f"Creating DHCP server: name={name}, interface={interface}")
    
    # Build the command
    cmd = f"/ip dhcp-server add name={name} interface={interface} lease-time={lease_time}"
    
    # Add optional parameters
    if address_pool:
        cmd += f" address-pool={address_pool}"
    
    if disabled:
        cmd += " disabled=yes"
    
    if authoritative != "yes":
        cmd += f" authoritative={authoritative}"
    
    if delay_threshold:
        cmd += f" delay-threshold={delay_threshold}"
    
    if comment:
        cmd += f' comment="{comment}"'
    
    result = execute_mikrotik_command(cmd)
    
    if "failure:" in result.lower() or "error" in result.lower():
        return f"Failed to create DHCP server: {result}"
    
    # Get the created server details
    details_cmd = f'/ip dhcp-server print detail where name="{name}"'
    details = execute_mikrotik_command(details_cmd)
    
    return f"DHCP server created successfully:\n\n{details}"

@mcp.tool(name="list_dhcp_servers", annotations=READ)
def mikrotik_list_dhcp_servers(
    name_filter: Optional[str] = None,
    interface_filter: Optional[str] = None,
    disabled_only: bool = False,
    invalid_only: bool = False
) -> str:
    """
    Lists DHCP servers on MikroTik device.
    
    Args:
        name_filter: Filter by server name (partial match)
        interface_filter: Filter by interface
        disabled_only: Show only disabled servers
        invalid_only: Show only invalid servers
    
    Returns:
        List of DHCP servers
    """
    app_logger.info(f"Listing DHCP servers with filters: name={name_filter}, interface={interface_filter}")
    
    # Build the command
    cmd = "/ip dhcp-server print"
    
    # Add filters
    filters = []
    if name_filter:
        filters.append(f'name~"{name_filter}"')
    if interface_filter:
        filters.append(f'interface="{interface_filter}"')
    if disabled_only:
        filters.append("disabled=yes")
    if invalid_only:
        filters.append("invalid=yes")
    
    if filters:
        cmd += " where " + " ".join(filters)
    
    result = execute_mikrotik_command(cmd)
    
    if not result or result.strip() == "":
        return "No DHCP servers found matching the criteria."
    
    return f"DHCP SERVERS:\n\n{result}"

@mcp.tool(name="get_dhcp_server", annotations=READ)
def mikrotik_get_dhcp_server(name: str) -> str:
    """
    Gets detailed information about a specific DHCP server.
    
    Args:
        name: Name of the DHCP server
    
    Returns:
        Detailed information about the DHCP server
    """
    app_logger.info(f"Getting DHCP server details: name={name}")
    
    cmd = f'/ip dhcp-server print detail where name="{name}"'
    result = execute_mikrotik_command(cmd)
    
    if not result or result.strip() == "":
        return f"DHCP server '{name}' not found."
    
    return f"DHCP SERVER DETAILS:\n\n{result}"

@mcp.tool(name="create_dhcp_network", annotations=WRITE)
def mikrotik_create_dhcp_network(
    network: str,
    gateway: str,
    netmask: Optional[str] = None,
    dns_servers: Optional[List[str]] = None,
    domain: Optional[str] = None,
    wins_servers: Optional[List[str]] = None,
    ntp_servers: Optional[List[str]] = None,
    dhcp_option: Optional[List[str]] = None,
    comment: Optional[str] = None
) -> str:
    """
    Creates a DHCP network configuration on MikroTik device.
    
    Args:
        network: Network address (e.g., "192.168.1.0/24")
        gateway: Default gateway
        netmask: Network mask (optional, derived from network)
        dns_servers: List of DNS servers
        domain: Domain name
        wins_servers: List of WINS servers
        ntp_servers: List of NTP servers
        dhcp_option: List of additional DHCP options
        comment: Optional comment
    
    Returns:
        Command output or error message
    """
    app_logger.info(f"Creating DHCP network: network={network}, gateway={gateway}")
    
    # Build the command
    cmd = f"/ip dhcp-server network add address={network} gateway={gateway}"
    
    # Add optional parameters
    if netmask:
        cmd += f" netmask={netmask}"
    
    if dns_servers:
        cmd += f" dns-server={','.join(dns_servers)}"
    
    if domain:
        cmd += f' domain="{domain}"'
    
    if wins_servers:
        cmd += f" wins-server={','.join(wins_servers)}"
    
    if ntp_servers:
        cmd += f" ntp-server={','.join(ntp_servers)}"
    
    if dhcp_option:
        cmd += f" dhcp-option={','.join(dhcp_option)}"
    
    if comment:
        cmd += f' comment="{comment}"'
    
    result = execute_mikrotik_command(cmd)
    
    if "failure:" in result.lower() or "error" in result.lower():
        return f"Failed to create DHCP network: {result}"
    
    # Get the created network details
    details_cmd = f'/ip dhcp-server network print detail where address="{network}"'
    details = execute_mikrotik_command(details_cmd)
    
    return f"DHCP network created successfully:\n\n{details}"

@mcp.tool(name="create_dhcp_pool", annotations=WRITE)
def mikrotik_create_dhcp_pool(
    name: str,
    ranges: str,
    next_pool: Optional[str] = None,
    comment: Optional[str] = None
) -> str:
    """
    Creates a DHCP address pool on MikroTik device.
    
    Args:
        name: Name of the address pool
        ranges: IP address ranges (e.g., "192.168.1.10-192.168.1.100")
        next_pool: Name of the next pool in chain
        comment: Optional comment
    
    Returns:
        Command output or error message
    """
    app_logger.info(f"Creating DHCP pool: name={name}, ranges={ranges}")
    
    # Build the command
    cmd = f'/ip pool add name={name} ranges={ranges}'
    
    # Add optional parameters
    if next_pool:
        cmd += f" next-pool={next_pool}"
    
    if comment:
        cmd += f' comment="{comment}"'
    
    result = execute_mikrotik_command(cmd)
    
    if "failure:" in result.lower() or "error" in result.lower():
        return f"Failed to create DHCP pool: {result}"
    
    # Get the created pool details
    details_cmd = f'/ip pool print detail where name="{name}"'
    details = execute_mikrotik_command(details_cmd)
    
    return f"DHCP pool created successfully:\n\n{details}"

@mcp.tool(name="remove_dhcp_server", annotations=DESTRUCTIVE)
def mikrotik_remove_dhcp_server(name: str) -> str:
    """
    Removes a DHCP server from MikroTik device.
    
    Args:
        name: Name of the DHCP server to remove
    
    Returns:
        Command output or error message
    """
    app_logger.info(f"Removing DHCP server: name={name}")
    
    # First check if the server exists
    check_cmd = f'/ip dhcp-server print count-only where name="{name}"'
    count = execute_mikrotik_command(check_cmd)
    
    if count.strip() == "0":
        return f"DHCP server '{name}' not found."
    
    # Remove the server
    cmd = f'/ip dhcp-server remove [find name="{name}"]'
    result = execute_mikrotik_command(cmd)
    
    if "failure:" in result.lower() or "error" in result.lower():
        return f"Failed to remove DHCP server: {result}"
    
    return f"DHCP server '{name}' removed successfully."

