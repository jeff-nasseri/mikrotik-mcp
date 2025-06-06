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
    mikrotik_disable_wireless_interface
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
                    "radio_name": {"type": "string", "description": "Name of the radio interface (e.g., wlan1)"},
                    "mode": {"type": "string",
                             "enum": ["ap-bridge", "bridge", "station", "station-pseudobridge", "station-bridge",
                                      "station-wds", "ap-bridge-wds", "alignment-only"],
                             "description": "Wireless mode"},
                    "ssid": {"type": "string", "description": "Network SSID name"},
                    "frequency": {"type": "string", "description": "Operating frequency"},
                    "band": {"type": "string",
                             "enum": ["2ghz-b", "2ghz-b/g", "2ghz-b/g/n", "5ghz-a", "5ghz-a/n", "5ghz-a/n/ac", "2ghz-g",
                                      "2ghz-n", "5ghz-n", "5ghz-ac"], "description": "Frequency band"},
                    "channel_width": {"type": "string",
                                      "enum": ["20mhz", "40mhz", "80mhz", "160mhz", "20/40mhz-eC", "20/40mhz-Ce"],
                                      "description": "Channel width"},
                    "disabled": {"type": "boolean", "description": "Whether to disable the interface"},
                    "comment": {"type": "string", "description": "Optional comment"}
                },
                "required": ["name", "radio_name"]
            },
        ),
        Tool(
            name="mikrotik_list_wireless_interfaces",
            description="Lists wireless interfaces on MikroTik device",
            inputSchema={
                "type": "object",
                "properties": {
                    "name_filter": {"type": "string", "description": "Filter by interface name"},
                    "mode_filter": {"type": "string", "description": "Filter by wireless mode"},
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
                    "frequency": {"type": "string", "description": "New operating frequency"},
                    "band": {"type": "string", "description": "New frequency band"},
                    "channel_width": {"type": "string", "description": "New channel width"},
                    "mode": {"type": "string", "description": "New wireless mode"},
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

        # Wireless Security Profile Management
        Tool(
            name="mikrotik_create_wireless_security_profile",
            description="Creates a wireless security profile on MikroTik device",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Name of the security profile"},
                    "mode": {"type": "string", "enum": ["none", "static-keys-required", "dynamic-keys"],
                             "description": "Security mode"},
                    "authentication_types": {"type": "array", "items": {"type": "string",
                                                                        "enum": ["wpa-psk", "wpa2-psk", "wpa-eap",
                                                                                 "wpa2-eap"]},
                                             "description": "Authentication types"},
                    "unicast_ciphers": {"type": "array", "items": {"type": "string", "enum": ["tkip", "aes-ccm"]},
                                        "description": "Unicast ciphers"},
                    "group_ciphers": {"type": "array", "items": {"type": "string", "enum": ["tkip", "aes-ccm"]},
                                      "description": "Group ciphers"},
                    "wpa_pre_shared_key": {"type": "string", "description": "WPA pre-shared key"},
                    "wpa2_pre_shared_key": {"type": "string", "description": "WPA2 pre-shared key"},
                    "supplicant_identity": {"type": "string", "description": "Supplicant identity for EAP"},
                    "eap_methods": {"type": "string", "description": "EAP methods"},
                    "tls_mode": {"type": "string", "description": "TLS mode"},
                    "tls_certificate": {"type": "string", "description": "TLS certificate"},
                    "comment": {"type": "string", "description": "Optional comment"}
                },
                "required": ["name"]
            },
        ),
        Tool(
            name="mikrotik_list_wireless_security_profiles",
            description="Lists wireless security profiles on MikroTik device",
            inputSchema={
                "type": "object",
                "properties": {
                    "name_filter": {"type": "string", "description": "Filter by profile name"},
                    "mode_filter": {"type": "string", "description": "Filter by security mode"}
                },
                "required": []
            },
        ),
        Tool(
            name="mikrotik_get_wireless_security_profile",
            description="Gets detailed information about a specific wireless security profile",
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
            description="Removes a wireless security profile from MikroTik device",
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
            description="Sets the security profile for a wireless interface",
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

        # Wireless Access List Management
        Tool(
            name="mikrotik_create_wireless_access_list",
            description="Creates a wireless access list entry",
            inputSchema={
                "type": "object",
                "properties": {
                    "interface": {"type": "string", "description": "Wireless interface"},
                    "mac_address": {"type": "string", "description": "MAC address to control"},
                    "action": {"type": "string", "enum": ["accept", "reject", "query"],
                               "description": "Action to take"},
                    "signal_range": {"type": "string", "description": "Signal strength range"},
                    "time": {"type": "string", "description": "Time schedule"},
                    "comment": {"type": "string", "description": "Optional comment"}
                },
                "required": ["interface", "mac_address"]
            },
        ),
        Tool(
            name="mikrotik_list_wireless_access_list",
            description="Lists wireless access list entries",
            inputSchema={
                "type": "object",
                "properties": {
                    "interface_filter": {"type": "string", "description": "Filter by interface"},
                    "action_filter": {"type": "string", "description": "Filter by action"}
                },
                "required": []
            },
        ),
        Tool(
            name="mikrotik_remove_wireless_access_list_entry",
            description="Removes a wireless access list entry",
            inputSchema={
                "type": "object",
                "properties": {
                    "entry_id": {"type": "string", "description": "ID of the access list entry to remove"}
                },
                "required": ["entry_id"]
            },
        ),
    ]


def get_wireless_handlers() -> Dict[str, Callable]:
    """Return the handlers for wireless management tools."""
    return {
        # Wireless Interface Management
        "mikrotik_create_wireless_interface": lambda args: mikrotik_create_wireless_interface(
            args["name"],
            args["radio_name"],
            args.get("mode", "ap-bridge"),
            args.get("ssid"),
            args.get("frequency"),
            args.get("band"),
            args.get("channel_width"),
            args.get("disabled", False),
            args.get("comment")
        ),
        "mikrotik_list_wireless_interfaces": lambda args: mikrotik_list_wireless_interfaces(
            args.get("name_filter"),
            args.get("mode_filter"),
            args.get("disabled_only", False),
            args.get("running_only", False)
        ),
        "mikrotik_get_wireless_interface": lambda args: mikrotik_get_wireless_interface(
            args["name"]
        ),
        "mikrotik_update_wireless_interface": lambda args: mikrotik_update_wireless_interface(
            args["name"],
            args.get("new_name"),
            args.get("ssid"),
            args.get("frequency"),
            args.get("band"),
            args.get("channel_width"),
            args.get("mode"),
            args.get("disabled"),
            args.get("comment")
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

        # Wireless Security Profile Management
        "mikrotik_create_wireless_security_profile": lambda args: mikrotik_create_wireless_security_profile(
            args["name"],
            args.get("mode", "dynamic-keys"),
            args.get("authentication_types"),
            args.get("unicast_ciphers"),
            args.get("group_ciphers"),
            args.get("wpa_pre_shared_key"),
            args.get("wpa2_pre_shared_key"),
            args.get("supplicant_identity"),
            args.get("eap_methods"),
            args.get("tls_mode"),
            args.get("tls_certificate"),
            args.get("comment")
        ),
        "mikrotik_list_wireless_security_profiles": lambda args: mikrotik_list_wireless_security_profiles(
            args.get("name_filter"),
            args.get("mode_filter")
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

        # Wireless Access List Management
        "mikrotik_create_wireless_access_list": lambda args: mikrotik_create_wireless_access_list(
            args["interface"],
            args["mac_address"],
            args.get("action", "accept"),
            args.get("signal_range"),
            args.get("time"),
            args.get("comment")
        ),
        "mikrotik_list_wireless_access_list": lambda args: mikrotik_list_wireless_access_list(
            args.get("interface_filter"),
            args.get("action_filter")
        ),
        "mikrotik_remove_wireless_access_list_entry": lambda args: mikrotik_remove_wireless_access_list_entry(
            args["entry_id"]
        ),
    }