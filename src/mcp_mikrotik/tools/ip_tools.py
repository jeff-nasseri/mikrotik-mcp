from typing import Dict, Any, List, Callable
from ..scope.ip_address import (
    mikrotik_add_ip_address, mikrotik_list_ip_addresses,
    mikrotik_get_ip_address, mikrotik_remove_ip_address
)
from ..scope.ip_pool import (
    mikrotik_create_ip_pool, mikrotik_list_ip_pools, mikrotik_get_ip_pool,
    mikrotik_update_ip_pool, mikrotik_remove_ip_pool, mikrotik_list_ip_pool_used,
    mikrotik_expand_ip_pool
)
from mcp.types import Tool

def get_ip_address_tools() -> List[Tool]:
    """Return the list of IP address tools."""
    return [
        # IP Address tools
        Tool(
            name="add_ip_address",
            description="Adds an IP address to an interface",
            inputSchema={
                "type": "object",
                "properties": {
                    "address": {"type": "string"},
                    "interface": {"type": "string"},
                    "network": {"type": "string"},
                    "broadcast": {"type": "string"},
                    "comment": {"type": "string"},
                    "disabled": {"type": "boolean"}
                },
                "required": ["address", "interface"]
            },
        ),
        Tool(
            name="list_ip_addresses",
            description="Lists IP addresses on MikroTik device",
            inputSchema={
                "type": "object",
                "properties": {
                    "interface_filter": {"type": "string"},
                    "address_filter": {"type": "string"},
                    "network_filter": {"type": "string"},
                    "disabled_only": {"type": "boolean"},
                    "dynamic_only": {"type": "boolean"}
                },
                "required": []
            },
        ),
        Tool(
            name="get_ip_address",
            description="Gets detailed information about a specific IP address",
            inputSchema={
                "type": "object",
                "properties": {
                    "address_id": {"type": "string"}
                },
                "required": ["address_id"]
            },
        ),
        Tool(
            name="remove_ip_address",
            description="Removes an IP address from MikroTik device",
            inputSchema={
                "type": "object",
                "properties": {
                    "address_id": {"type": "string"}
                },
                "required": ["address_id"]
            },
        ),
    ]

def get_ip_pool_tools() -> List[Tool]:
    """Return the list of IP pool tools."""
    return [
        # IP Pool tools
        Tool(
            name="create_ip_pool",
            description="Creates an IP pool on MikroTik device",
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
            name="list_ip_pools",
            description="Lists IP pools on MikroTik device",
            inputSchema={
                "type": "object",
                "properties": {
                    "name_filter": {"type": "string"},
                    "ranges_filter": {"type": "string"},
                    "include_used": {"type": "boolean"}
                },
                "required": []
            },
        ),
        Tool(
            name="get_ip_pool",
            description="Gets detailed information about a specific IP pool",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"}
                },
                "required": ["name"]
            },
        ),
        Tool(
            name="update_ip_pool",
            description="Updates an existing IP pool on MikroTik device",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "new_name": {"type": "string"},
                    "ranges": {"type": "string"},
                    "next_pool": {"type": "string"},
                    "comment": {"type": "string"}
                },
                "required": ["name"]
            },
        ),
        Tool(
            name="remove_ip_pool",
            description="Removes an IP pool from MikroTik device",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"}
                },
                "required": ["name"]
            },
        ),
        Tool(
            name="list_ip_pool_used",
            description="Lists used addresses from IP pools",
            inputSchema={
                "type": "object",
                "properties": {
                    "pool_name": {"type": "string"},
                    "address_filter": {"type": "string"},
                    "mac_filter": {"type": "string"},
                    "info_filter": {"type": "string"}
                },
                "required": []
            },
        ),
        Tool(
            name="expand_ip_pool",
            description="Expands an existing IP pool by adding more ranges",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "additional_ranges": {"type": "string"}
                },
                "required": ["name", "additional_ranges"]
            },
        ),
    ]

def get_ip_address_handlers() -> Dict[str, Callable]:
    """Return the handlers for IP address tools."""
    return {
        "add_ip_address": lambda args: mikrotik_add_ip_address(
            args["address"],
            args["interface"],
            args.get("network"),
            args.get("broadcast"),
            args.get("comment"),
            args.get("disabled", False)
        ),
        "list_ip_addresses": lambda args: mikrotik_list_ip_addresses(
            args.get("interface_filter"),
            args.get("address_filter"),
            args.get("network_filter"),
            args.get("disabled_only", False),
            args.get("dynamic_only", False)
        ),
        "get_ip_address": lambda args: mikrotik_get_ip_address(
            args["address_id"]
        ),
        "remove_ip_address": lambda args: mikrotik_remove_ip_address(
            args["address_id"]
        ),
    }

def get_ip_pool_handlers() -> Dict[str, Callable]:
    """Return the handlers for IP pool tools."""
    return {
        "create_ip_pool": lambda args: mikrotik_create_ip_pool(
            args["name"],
            args["ranges"],
            args.get("next_pool"),
            args.get("comment")
        ),
        "list_ip_pools": lambda args: mikrotik_list_ip_pools(
            args.get("name_filter"),
            args.get("ranges_filter"),
            args.get("include_used", False)
        ),
        "get_ip_pool": lambda args: mikrotik_get_ip_pool(
            args["name"]
        ),
        "update_ip_pool": lambda args: mikrotik_update_ip_pool(
            args["name"],
            args.get("new_name"),
            args.get("ranges"),
            args.get("next_pool"),
            args.get("comment")
        ),
        "remove_ip_pool": lambda args: mikrotik_remove_ip_pool(
            args["name"]
        ),
        "list_ip_pool_used": lambda args: mikrotik_list_ip_pool_used(
            args.get("pool_name"),
            args.get("address_filter"),
            args.get("mac_filter"),
            args.get("info_filter")
        ),
        "expand_ip_pool": lambda args: mikrotik_expand_ip_pool(
            args["name"],
            args["additional_ranges"]
        ),
    }
