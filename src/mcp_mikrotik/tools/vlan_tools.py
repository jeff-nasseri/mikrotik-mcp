from typing import Dict, Any, List, Callable
from ..scope.vlan import (
    mikrotik_create_vlan_interface, mikrotik_list_vlan_interfaces,
    mikrotik_get_vlan_interface, mikrotik_update_vlan_interface,
    mikrotik_remove_vlan_interface
)
from mcp.types import Tool

def get_vlan_tools() -> List[Tool]:
    """Return the list of VLAN interface tools."""
    return [
        # VLAN interface tools
        Tool(
            name="create_vlan_interface",
            description="Creates a VLAN interface on MikroTik device",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "vlan_id": {"type": "integer", "minimum": 1, "maximum": 4094},
                    "interface": {"type": "string"},
                    "comment": {"type": "string"},
                    "disabled": {"type": "boolean"},
                    "mtu": {"type": "integer"},
                    "use_service_tag": {"type": "boolean"},
                    "arp": {"type": "string", "enum": ["enabled", "disabled", "proxy-arp", "reply-only"]},
                    "arp_timeout": {"type": "string"}
                },
                "required": ["name", "vlan_id", "interface"]
            },
        ),
        Tool(
            name="list_vlan_interfaces",
            description="Lists VLAN interfaces on MikroTik device",
            inputSchema={
                "type": "object",
                "properties": {
                    "name_filter": {"type": "string"},
                    "vlan_id_filter": {"type": "integer"},
                    "interface_filter": {"type": "string"},
                    "disabled_only": {"type": "boolean"}
                },
                "required": []
            },
        ),
        Tool(
            name="get_vlan_interface",
            description="Gets detailed information about a specific VLAN interface",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"}
                },
                "required": ["name"]
            },
        ),
        Tool(
            name="update_vlan_interface",
            description="Updates an existing VLAN interface on MikroTik device",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "new_name": {"type": "string"},
                    "vlan_id": {"type": "integer", "minimum": 1, "maximum": 4094},
                    "interface": {"type": "string"},
                    "comment": {"type": "string"},
                    "disabled": {"type": "boolean"},
                    "mtu": {"type": "integer"},
                    "use_service_tag": {"type": "boolean"},
                    "arp": {"type": "string", "enum": ["enabled", "disabled", "proxy-arp", "reply-only"]},
                    "arp_timeout": {"type": "string"}
                },
                "required": ["name"]
            },
        ),
        Tool(
            name="remove_vlan_interface",
            description="Removes a VLAN interface from MikroTik device",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"}
                },
                "required": ["name"]
            },
        ),
    ]

def get_vlan_handlers() -> Dict[str, Callable]:
    """Return the handlers for VLAN interface tools."""
    return {
        "create_vlan_interface": lambda args: mikrotik_create_vlan_interface(
            args["name"],
            args["vlan_id"],
            args["interface"],
            args.get("comment"),
            args.get("disabled", False),
            args.get("mtu"),
            args.get("use_service_tag", False),
            args.get("arp", "enabled"),
            args.get("arp_timeout")
        ),
        "list_vlan_interfaces": lambda args: mikrotik_list_vlan_interfaces(
            args.get("name_filter"),
            args.get("vlan_id_filter"),
            args.get("interface_filter"),
            args.get("disabled_only", False)
        ),
        "get_vlan_interface": lambda args: mikrotik_get_vlan_interface(
            args["name"]
        ),
        "update_vlan_interface": lambda args: mikrotik_update_vlan_interface(
            args["name"],
            args.get("new_name"),
            args.get("vlan_id"),
            args.get("interface"),
            args.get("comment"),
            args.get("disabled"),
            args.get("mtu"),
            args.get("use_service_tag"),
            args.get("arp"),
            args.get("arp_timeout")
        ),
        "remove_vlan_interface": lambda args: mikrotik_remove_vlan_interface(
            args["name"]
        ),
    }
