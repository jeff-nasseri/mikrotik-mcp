from typing import Dict, Any, List, Callable
from ..scope.dhcp import (
    mikrotik_create_dhcp_server, mikrotik_list_dhcp_servers,
    mikrotik_get_dhcp_server, mikrotik_create_dhcp_network,
    mikrotik_create_dhcp_pool, mikrotik_remove_dhcp_server
)
from mcp.types import Tool

def get_dhcp_tools() -> List[Tool]:
    """Return the list of DHCP server tools."""
    return [
        # DHCP Server tools
        Tool(
            name="create_dhcp_server",
            description="Creates a DHCP server on MikroTik device",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "interface": {"type": "string"},
                    "lease_time": {"type": "string"},
                    "address_pool": {"type": "string"},
                    "disabled": {"type": "boolean"},
                    "authoritative": {"type": "string", "enum": ["yes", "no", "after-2sec-delay"]},
                    "delay_threshold": {"type": "string"},
                    "comment": {"type": "string"}
                },
                "required": ["name", "interface"]
            },
        ),
        Tool(
            name="list_dhcp_servers",
            description="Lists DHCP servers on MikroTik device",
            inputSchema={
                "type": "object",
                "properties": {
                    "name_filter": {"type": "string"},
                    "interface_filter": {"type": "string"},
                    "disabled_only": {"type": "boolean"},
                    "invalid_only": {"type": "boolean"}
                },
                "required": []
            },
        ),
        Tool(
            name="get_dhcp_server",
            description="Gets detailed information about a specific DHCP server",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"}
                },
                "required": ["name"]
            },
        ),
        Tool(
            name="create_dhcp_network",
            description="Creates a DHCP network configuration",
            inputSchema={
                "type": "object",
                "properties": {
                    "network": {"type": "string"},
                    "gateway": {"type": "string"},
                    "netmask": {"type": "string"},
                    "dns_servers": {"type": "array", "items": {"type": "string"}},
                    "domain": {"type": "string"},
                    "wins_servers": {"type": "array", "items": {"type": "string"}},
                    "ntp_servers": {"type": "array", "items": {"type": "string"}},
                    "dhcp_option": {"type": "array", "items": {"type": "string"}},
                    "comment": {"type": "string"}
                },
                "required": ["network", "gateway"]
            },
        ),
        Tool(
            name="create_dhcp_pool",
            description="Creates a DHCP address pool",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "ranges": {"type": "string"},
                    "next_pool": {"type": "string"},
                    "comment": {"type": "string"}
                },
                "required": ["name", "ranges"]
            },
        ),
        Tool(
            name="remove_dhcp_server",
            description="Removes a DHCP server from MikroTik device",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"}
                },
                "required": ["name"]
            },
        ),
    ]

def get_dhcp_handlers() -> Dict[str, Callable]:
    """Return the handlers for DHCP server tools."""
    return {
        "create_dhcp_server": lambda args: mikrotik_create_dhcp_server(
            args["name"],
            args["interface"],
            args.get("lease_time", "1d"),
            args.get("address_pool"),
            args.get("disabled", False),
            args.get("authoritative", "yes"),
            args.get("delay_threshold"),
            args.get("comment")
        ),
        "list_dhcp_servers": lambda args: mikrotik_list_dhcp_servers(
            args.get("name_filter"),
            args.get("interface_filter"),
            args.get("disabled_only", False),
            args.get("invalid_only", False)
        ),
        "get_dhcp_server": lambda args: mikrotik_get_dhcp_server(
            args["name"]
        ),
        "create_dhcp_network": lambda args: mikrotik_create_dhcp_network(
            args["network"],
            args["gateway"],
            args.get("netmask"),
            args.get("dns_servers"),
            args.get("domain"),
            args.get("wins_servers"),
            args.get("ntp_servers"),
            args.get("dhcp_option"),
            args.get("comment")
        ),
        "create_dhcp_pool": lambda args: mikrotik_create_dhcp_pool(
            args["name"],
            args["ranges"],
            args.get("next_pool"),
            args.get("comment")
        ),
        "remove_dhcp_server": lambda args: mikrotik_remove_dhcp_server(
            args["name"]
        ),
    }
