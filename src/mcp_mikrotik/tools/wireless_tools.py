from typing import Dict, Any, List, Callable
from ..scope.wireless import (
    mikrotik_create_wireless_interface, mikrotik_list_wireless_interfaces,
    mikrotik_get_wireless_interface, mikrotik_update_wireless_interface,
    mikrotik_remove_wireless_interface, mikrotik_create_wireless_security_profile,
    mikrotik_list_wireless_security_profiles, mikrotik_get_wireless_security_profile,
    mikrotik_remove_wireless_security_profile, mikrotik_set_wireless_security_profile,
    mikrotik_scan_wireless_networks, mikrotik_get_wireless_registration_table,
    mikrotik_create_wireless_access_list, mikrotik_list_wireless_access_list,
    mikrotik_remove_wireless_access_list_entry, mikrotik_enable_wireless_interface,
    mikrotik_disable_wireless_interface, mikrotik_check_wireless_support
)
from mcp.types import Tool


def get_wireless_tools() -> List[Tool]:
    """Return the list of wireless management tools."""
    return [
        # Wireless Interface Management
        Tool(
            name="mikrotik_create_wireless_interface",
            description="Creates a wireless interface on MikroTik device",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Name of the wireless interface"},
                    "ssid": {"type": "string", "description": "Network SSID name"},
                    "disabled": {"type": "boolean", "description": "Whether to disable the interface"},
                    "comment": {"type": "string", "description": "Optional comment"},
                    # Legacy parameters for backward compatibility
                    "radio_name": {"type": "string",
                                   "description": "Name of the radio interface (legacy systems only)"},
                    "mode": {"type": "string",
                             "enum": ["ap-bridge", "bridge", "station", "station-pseudobridge", "station-bridge",
                                      "station-wds", "ap-bridge-wds", "alignment-only"],
                             "description": "Wireless mode (legacy systems only)"},
                    "frequency": {"type": "string", "description": "Operating frequency (legacy systems only)"},
                    "band": {"type": "string",
                             "enum": ["2ghz-b", "2ghz-b/g", "2ghz-b/g/n", "5ghz-a", "5ghz-a/n", "5ghz-a/n/ac", "2ghz-g",
                                      "2ghz-n", "5ghz-n", "5ghz-ac"],
                             "description": "Frequency band (legacy systems only)"},
                    "channel_width": {"type": "string",
                                      "enum": ["20mhz", "40mhz", "80mhz", "160mhz", "20/40mhz-eC", "20/40mhz-Ce"],
                                      "description": "Channel width (legacy systems only)"},
                    "security_profile": {"type": "string", "description": "Security profile name (legacy systems only)"}
                },
                "required": ["name"]
            },
        ),
        Tool(
            name="mikrotik_list_wireless_interfaces",
            description="Lists wireless interfaces on MikroTik device",
            inputSchema={
                "type": "object",
                "properties": {
                    "name_filter": {"type": "string", "description": "Filter by interface name"},
                    "disabled_only": {"type": "boolean", "description": "Show only disabled interfaces"},
                    "running_only": {"type": "boolean", "description": "Show only running interfaces"}
                },
                "required": []
            },
        ),
        Tool(
            name="mikrotik_get_wireless_interface",
            description="Gets detailed information about a specific wireless interface",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Name of the wireless interface"}
                },
                "required": ["name"]
            },
        ),
        Tool(
            name="mikrotik_update_wireless_interface",
            description="Updates an existing wireless interface",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Current name of the wireless interface"},
                    "new_name": {"type": "string", "description": "New name for the interface"},
                    "ssid": {"type": "string", "description": "New SSID name"},
                    "disabled": {"type": "boolean", "description": "Enable/disable interface"},
                    "comment": {"type": "string", "description": "New comment"}
                },
                "required": ["name"]
            },
        ),
        Tool(
            name="mikrotik_remove_wireless_interface",
            description="Removes a wireless interface from MikroTik device",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Name of the wireless interface to remove"}
                },
                "required": ["name"]
            },
        ),
        Tool(
            name="mikrotik_enable_wireless_interface",
            description="Enables a wireless interface",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Name of the wireless interface"}
                },
                "required": ["name"]
            },
        ),
        Tool(
            name="mikrotik_disable_wireless_interface",
            description="Disables a wireless interface",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Name of the wireless interface"}
                },
                "required": ["name"]
            },
        ),

        # Wireless Security Profile Management (Legacy)
        Tool(
            name="mikrotik_create_wireless_security_profile",
            description="Creates a wireless security profile (legacy systems only)",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Name of the security profile"}
                },
                "required": ["name"]
            },
        ),
        Tool(
            name="mikrotik_list_wireless_security_profiles",
            description="Lists wireless security profiles (legacy systems only)",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            },
        ),
        Tool(
            name="mikrotik_get_wireless_security_profile",
            description="Gets wireless security profile details (legacy systems only)",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Name of the security profile"}
                },
                "required": ["name"]
            },
        ),
        Tool(
            name="mikrotik_remove_wireless_security_profile",
            description="Removes a wireless security profile (legacy systems only)",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Name of the security profile to remove"}
                },
                "required": ["name"]
            },
        ),
        Tool(
            name="mikrotik_set_wireless_security_profile",
            description="Sets security profile for interface (legacy systems only)",
            inputSchema={
                "type": "object",
                "properties": {
                    "interface_name": {"type": "string", "description": "Name of the wireless interface"},
                    "security_profile": {"type": "string", "description": "Name of the security profile to apply"}
                },
                "required": ["interface_name", "security_profile"]
            },
        ),

        # Wireless Network Operations
        Tool(
            name="mikrotik_scan_wireless_networks",
            description="Scans for wireless networks using specified interface",
            inputSchema={
                "type": "object",
                "properties": {
                    "interface": {"type": "string", "description": "Wireless interface to use for scanning"},
                    "duration": {"type": "integer", "description": "Scan duration in seconds", "default": 5}
                },
                "required": ["interface"]
            },
        ),
        Tool(
            name="mikrotik_get_wireless_registration_table",
            description="Gets the wireless registration table (connected clients)",
            inputSchema={
                "type": "object",
                "properties": {
                    "interface": {"type": "string", "description": "Filter by specific wireless interface"}
                },
                "required": []
            },
        ),

        # Wireless Access List Management (Legacy)
        Tool(
            name="mikrotik_create_wireless_access_list",
            description="Creates a wireless access list entry (legacy systems only)",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            },
        ),
        Tool(
            name="mikrotik_list_wireless_access_list",
            description="Lists wireless access list entries (legacy systems only)",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            },
        ),
        Tool(
            name="mikrotik_remove_wireless_access_list_entry",
            description="Removes a wireless access list entry (legacy systems only)",
            inputSchema={
                "type": "object",
                "properties": {
                    "entry_id": {"type": "string", "description": "ID of the access list entry to remove"}
                },
                "required": ["entry_id"]
            },
        ),
        # Wireless Support Check
        Tool(
            name="mikrotik_check_wireless_support",
            description="Checks if the device supports wireless functionality",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            },
        ),
    ]


def get_wireless_handlers() -> Dict[str, Callable]:
    """Return the handlers for wireless management tools."""
    return {
        # Wireless Interface Management - Updated to match new function signatures
        "mikrotik_create_wireless_interface": lambda args: mikrotik_create_wireless_interface(
            name=args["name"],
            ssid=args.get("ssid"),
            disabled=args.get("disabled", False),
            comment=args.get("comment"),
            # Pass all other args as kwargs for legacy compatibility
            **{k: v for k, v in args.items() if k not in ["name", "ssid", "disabled", "comment"]}
        ),
        "mikrotik_list_wireless_interfaces": lambda args: mikrotik_list_wireless_interfaces(
            args.get("name_filter"),
            args.get("disabled_only", False),
            args.get("running_only", False)
        ),
        "mikrotik_get_wireless_interface": lambda args: mikrotik_get_wireless_interface(
            args["name"]
        ),
        "mikrotik_update_wireless_interface": lambda args: mikrotik_update_wireless_interface(
            name=args["name"],
            **{k: v for k, v in args.items() if k != "name"}
        ),
        "mikrotik_remove_wireless_interface": lambda args: mikrotik_remove_wireless_interface(
            args["name"]
        ),
        "mikrotik_enable_wireless_interface": lambda args: mikrotik_enable_wireless_interface(
            args["name"]
        ),
        "mikrotik_disable_wireless_interface": lambda args: mikrotik_disable_wireless_interface(
            args["name"]
        ),

        # Wireless Security Profile Management - Simplified for new system
        "mikrotik_create_wireless_security_profile": lambda args: mikrotik_create_wireless_security_profile(
            name=args["name"],
            **{k: v for k, v in args.items() if k != "name"}
        ),
        "mikrotik_list_wireless_security_profiles": lambda args: mikrotik_list_wireless_security_profiles(
            **args
        ),
        "mikrotik_get_wireless_security_profile": lambda args: mikrotik_get_wireless_security_profile(
            args["name"]
        ),
        "mikrotik_remove_wireless_security_profile": lambda args: mikrotik_remove_wireless_security_profile(
            args["name"]
        ),
        "mikrotik_set_wireless_security_profile": lambda args: mikrotik_set_wireless_security_profile(
            args["interface_name"],
            args["security_profile"]
        ),

        # Wireless Network Operations
        "mikrotik_scan_wireless_networks": lambda args: mikrotik_scan_wireless_networks(
            args["interface"],
            args.get("duration", 5)
        ),
        "mikrotik_get_wireless_registration_table": lambda args: mikrotik_get_wireless_registration_table(
            args.get("interface")
        ),

        # Wireless Access List Management - Simplified for new system
        "mikrotik_create_wireless_access_list": lambda args: mikrotik_create_wireless_access_list(
            **args
        ),
        "mikrotik_list_wireless_access_list": lambda args: mikrotik_list_wireless_access_list(
            **args
        ),
        "mikrotik_remove_wireless_access_list_entry": lambda args: mikrotik_remove_wireless_access_list_entry(
            args["entry_id"]
        ),

        # Wireless Support Check
        "mikrotik_check_wireless_support": lambda args: mikrotik_check_wireless_support(),
    }