from typing import Dict, Any, List, Callable
from mcp.types import Tool

from .vlan_tools import get_vlan_tools, get_vlan_handlers
from .ip_tools import get_ip_address_tools, get_ip_pool_tools, get_ip_address_handlers, get_ip_pool_handlers
from .dhcp_tools import get_dhcp_tools, get_dhcp_handlers
from .firewall_tools import get_firewall_filter_tools, get_firewall_nat_tools, get_firewall_filter_handlers, \
    get_firewall_nat_handlers
from .dns_tools import get_dns_tools, get_dns_handlers
from .route_tools import get_route_tools, get_route_handlers
from .user_tools import get_user_tools, get_user_handlers
from .backup_tools import get_backup_tools, get_backup_handlers
from .log_tools import get_log_tools, get_log_handlers
from .wireless_tools import get_wireless_tools, get_wireless_handlers


def get_all_tools() -> List[Tool]:
    """Return all available tools."""
    tools = []

    # VLAN tools
    tools.extend(get_vlan_tools())

    # Wireless tools
    tools.extend(get_wireless_tools())

    # IP tools
    tools.extend(get_ip_address_tools())
    tools.extend(get_ip_pool_tools())

    # DHCP tools
    tools.extend(get_dhcp_tools())

    # Firewall tools
    tools.extend(get_firewall_filter_tools())
    tools.extend(get_firewall_nat_tools())

    # DNS tools
    tools.extend(get_dns_tools())

    # Route tools
    tools.extend(get_route_tools())

    # User tools
    tools.extend(get_user_tools())

    # Backup tools
    tools.extend(get_backup_tools())

    # Log tools
    tools.extend(get_log_tools())

    return tools


def get_all_handlers() -> Dict[str, Callable]:
    """Return all command handlers."""
    handlers = {}

    # VLAN handlers
    handlers.update(get_vlan_handlers())

    # Wireless Handler
    handlers.update(get_wireless_handlers())

    # IP handlers
    handlers.update(get_ip_address_handlers())
    handlers.update(get_ip_pool_handlers())

    # DHCP handlers
    handlers.update(get_dhcp_handlers())

    # Firewall handlers
    handlers.update(get_firewall_filter_handlers())
    handlers.update(get_firewall_nat_handlers())

    # DNS handlers
    handlers.update(get_dns_handlers())

    # Route handlers
    handlers.update(get_route_handlers())

    # User handlers
    handlers.update(get_user_handlers())

    # Backup handlers
    handlers.update(get_backup_handlers())

    # Log handlers
    handlers.update(get_log_handlers())

    return handlers