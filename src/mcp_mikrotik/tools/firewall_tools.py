from typing import Dict, Any, List, Callable
from ..scope.firewall_filter import (
    mikrotik_create_filter_rule, mikrotik_list_filter_rules,
    mikrotik_get_filter_rule, mikrotik_update_filter_rule,
    mikrotik_remove_filter_rule, mikrotik_move_filter_rule,
    mikrotik_enable_filter_rule, mikrotik_disable_filter_rule,
    mikrotik_create_basic_firewall_setup
)
from ..scope.firewall_nat import (
    mikrotik_create_nat_rule, mikrotik_list_nat_rules,
    mikrotik_get_nat_rule, mikrotik_update_nat_rule,
    mikrotik_remove_nat_rule, mikrotik_move_nat_rule,
    mikrotik_enable_nat_rule, mikrotik_disable_nat_rule
)
from mcp.types import Tool

def get_firewall_filter_tools() -> List[Tool]:
    """Return the list of firewall filter tools."""
    return [
        # Firewall Filter tools
        Tool(
            name="create_filter_rule",
            description="Creates a firewall filter rule on MikroTik device",
            inputSchema={
                "type": "object",
                "properties": {
                    "chain": {"type": "string", "enum": ["input", "forward", "output"]},
                    "action": {"type": "string"},
                    "src_address": {"type": "string"},
                    "dst_address": {"type": "string"},
                    "src_port": {"type": "string"},
                    "dst_port": {"type": "string"},
                    "protocol": {"type": "string"},
                    "in_interface": {"type": "string"},
                    "out_interface": {"type": "string"},
                    "connection_state": {"type": "string"},
                    "connection_nat_state": {"type": "string"},
                    "src_address_list": {"type": "string"},
                    "dst_address_list": {"type": "string"},
                    "limit": {"type": "string"},
                    "tcp_flags": {"type": "string"},
                    "comment": {"type": "string"},
                    "disabled": {"type": "boolean"},
                    "log": {"type": "boolean"},
                    "log_prefix": {"type": "string"},
                    "place_before": {"type": "string"}
                },
                "required": ["chain", "action"]
            },
        ),
        Tool(
            name="list_filter_rules",
            description="Lists firewall filter rules on MikroTik device",
            inputSchema={
                "type": "object",
                "properties": {
                    "chain_filter": {"type": "string"},
                    "action_filter": {"type": "string"},
                    "src_address_filter": {"type": "string"},
                    "dst_address_filter": {"type": "string"},
                    "protocol_filter": {"type": "string"},
                    "interface_filter": {"type": "string"},
                    "disabled_only": {"type": "boolean"},
                    "invalid_only": {"type": "boolean"},
                    "dynamic_only": {"type": "boolean"}
                },
                "required": []
            },
        ),
        Tool(
            name="get_filter_rule",
            description="Gets detailed information about a specific firewall filter rule",
            inputSchema={
                "type": "object",
                "properties": {
                    "rule_id": {"type": "string"}
                },
                "required": ["rule_id"]
            },
        ),
        Tool(
            name="update_filter_rule",
            description="Updates an existing firewall filter rule on MikroTik device",
            inputSchema={
                "type": "object",
                "properties": {
                    "rule_id": {"type": "string"},
                    "chain": {"type": "string"},
                    "action": {"type": "string"},
                    "src_address": {"type": "string"},
                    "dst_address": {"type": "string"},
                    "src_port": {"type": "string"},
                    "dst_port": {"type": "string"},
                    "protocol": {"type": "string"},
                    "in_interface": {"type": "string"},
                    "out_interface": {"type": "string"},
                    "connection_state": {"type": "string"},
                    "connection_nat_state": {"type": "string"},
                    "src_address_list": {"type": "string"},
                    "dst_address_list": {"type": "string"},
                    "limit": {"type": "string"},
                    "tcp_flags": {"type": "string"},
                    "comment": {"type": "string"},
                    "disabled": {"type": "boolean"},
                    "log": {"type": "boolean"},
                    "log_prefix": {"type": "string"}
                },
                "required": ["rule_id"]
            },
        ),
        Tool(
            name="remove_filter_rule",
            description="Removes a firewall filter rule from MikroTik device",
            inputSchema={
                "type": "object",
                "properties": {
                    "rule_id": {"type": "string"}
                },
                "required": ["rule_id"]
            },
        ),
        Tool(
            name="move_filter_rule",
            description="Moves a firewall filter rule to a different position",
            inputSchema={
                "type": "object",
                "properties": {
                    "rule_id": {"type": "string"},
                    "destination": {"type": "integer"}
                },
                "required": ["rule_id", "destination"]
            },
        ),
        Tool(
            name="enable_filter_rule",
            description="Enables a firewall filter rule",
            inputSchema={
                "type": "object",
                "properties": {
                    "rule_id": {"type": "string"}
                },
                "required": ["rule_id"]
            },
        ),
        Tool(
            name="disable_filter_rule",
            description="Disables a firewall filter rule",
            inputSchema={
                "type": "object",
                "properties": {
                    "rule_id": {"type": "string"}
                },
                "required": ["rule_id"]
            },
        ),
        Tool(
            name="create_basic_firewall_setup",
            description="Creates a basic firewall setup with common security rules",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            },
        ),
    ]

def get_firewall_nat_tools() -> List[Tool]:
    """Return the list of firewall NAT tools."""
    return [
        # NAT tools
        Tool(
            name="create_nat_rule",
            description="Creates a NAT rule on MikroTik device",
            inputSchema={
                "type": "object",
                "properties": {
                    "chain": {"type": "string", "enum": ["srcnat", "dstnat"]},
                    "action": {"type": "string"},
                    "src_address": {"type": "string"},
                    "dst_address": {"type": "string"},
                    "src_port": {"type": "string"},
                    "dst_port": {"type": "string"},
                    "protocol": {"type": "string"},
                    "in_interface": {"type": "string"},
                    "out_interface": {"type": "string"},
                    "to_addresses": {"type": "string"},
                    "to_ports": {"type": "string"},
                    "comment": {"type": "string"},
                    "disabled": {"type": "boolean"},
                    "log": {"type": "boolean"},
                    "log_prefix": {"type": "string"},
                    "place_before": {"type": "string"}
                },
                "required": ["chain", "action"]
            },
        ),
        Tool(
            name="list_nat_rules",
            description="Lists NAT rules on MikroTik device",
            inputSchema={
                "type": "object",
                "properties": {
                    "chain_filter": {"type": "string"},
                    "action_filter": {"type": "string"},
                    "src_address_filter": {"type": "string"},
                    "dst_address_filter": {"type": "string"},
                    "protocol_filter": {"type": "string"},
                    "interface_filter": {"type": "string"},
                    "disabled_only": {"type": "boolean"},
                    "invalid_only": {"type": "boolean"}
                },
                "required": []
            },
        ),
        Tool(
            name="get_nat_rule",
            description="Gets detailed information about a specific NAT rule",
            inputSchema={
                "type": "object",
                "properties": {
                    "rule_id": {"type": "string"}
                },
                "required": ["rule_id"]
            },
        ),
        Tool(
            name="update_nat_rule",
            description="Updates an existing NAT rule on MikroTik device",
            inputSchema={
                "type": "object",
                "properties": {
                    "rule_id": {"type": "string"},
                    "chain": {"type": "string"},
                    "action": {"type": "string"},
                    "src_address": {"type": "string"},
                    "dst_address": {"type": "string"},
                    "src_port": {"type": "string"},
                    "dst_port": {"type": "string"},
                    "protocol": {"type": "string"},
                    "in_interface": {"type": "string"},
                    "out_interface": {"type": "string"},
                    "to_addresses": {"type": "string"},
                    "to_ports": {"type": "string"},
                    "comment": {"type": "string"},
                    "disabled": {"type": "boolean"},
                    "log": {"type": "boolean"},
                    "log_prefix": {"type": "string"}
                },
                "required": ["rule_id"]
            },
        ),
        Tool(
            name="remove_nat_rule",
            description="Removes a NAT rule from MikroTik device",
            inputSchema={
                "type": "object",
                "properties": {
                    "rule_id": {"type": "string"}
                },
                "required": ["rule_id"]
            },
        ),
        Tool(
            name="move_nat_rule",
            description="Moves a NAT rule to a different position in the chain",
            inputSchema={
                "type": "object",
                "properties": {
                    "rule_id": {"type": "string"},
                    "destination": {"type": "integer"}
                },
                "required": ["rule_id", "destination"]
            },
        ),
        Tool(
            name="enable_nat_rule",
            description="Enables a NAT rule",
            inputSchema={
                "type": "object",
                "properties": {
                    "rule_id": {"type": "string"}
                },
                "required": ["rule_id"]
            },
        ),
        Tool(
            name="disable_nat_rule",
            description="Disables a NAT rule",
            inputSchema={
                "type": "object",
                "properties": {
                    "rule_id": {"type": "string"}
                },
                "required": ["rule_id"]
            },
        ),
    ]

def get_firewall_filter_handlers() -> Dict[str, Callable]:
    """Return the handlers for firewall filter tools."""
    return {
        "create_filter_rule": lambda args: mikrotik_create_filter_rule(
            args["chain"],
            args["action"],
            args.get("src_address"),
            args.get("dst_address"),
            args.get("src_port"),
            args.get("dst_port"),
            args.get("protocol"),
            args.get("in_interface"),
            args.get("out_interface"),
            args.get("connection_state"),
            args.get("connection_nat_state"),
            args.get("src_address_list"),
            args.get("dst_address_list"),
            args.get("limit"),
            args.get("tcp_flags"),
            args.get("comment"),
            args.get("disabled", False),
            args.get("log", False),
            args.get("log_prefix"),
            args.get("place_before")
        ),
        "list_filter_rules": lambda args: mikrotik_list_filter_rules(
            args.get("chain_filter"),
            args.get("action_filter"),
            args.get("src_address_filter"),
            args.get("dst_address_filter"),
            args.get("protocol_filter"),
            args.get("interface_filter"),
            args.get("disabled_only", False),
            args.get("invalid_only", False),
            args.get("dynamic_only", False)
        ),
        "get_filter_rule": lambda args: mikrotik_get_filter_rule(
            args["rule_id"]
        ),
        "update_filter_rule": lambda args: mikrotik_update_filter_rule(
            args["rule_id"],
            args.get("chain"),
            args.get("action"),
            args.get("src_address"),
            args.get("dst_address"),
            args.get("src_port"),
            args.get("dst_port"),
            args.get("protocol"),
            args.get("in_interface"),
            args.get("out_interface"),
            args.get("connection_state"),
            args.get("connection_nat_state"),
            args.get("src_address_list"),
            args.get("dst_address_list"),
            args.get("limit"),
            args.get("tcp_flags"),
            args.get("comment"),
            args.get("disabled"),
            args.get("log"),
            args.get("log_prefix")
        ),
        "remove_filter_rule": lambda args: mikrotik_remove_filter_rule(
            args["rule_id"]
        ),
        "move_filter_rule": lambda args: mikrotik_move_filter_rule(
            args["rule_id"],
            args["destination"]
        ),
        "enable_filter_rule": lambda args: mikrotik_enable_filter_rule(
            args["rule_id"]
        ),
        "disable_filter_rule": lambda args: mikrotik_disable_filter_rule(
            args["rule_id"]
        ),
        "create_basic_firewall_setup": lambda args: mikrotik_create_basic_firewall_setup(),
    }

def get_firewall_nat_handlers() -> Dict[str, Callable]:
    """Return the handlers for firewall NAT tools."""
    return {
        "create_nat_rule": lambda args: mikrotik_create_nat_rule(
            args["chain"],
            args["action"],
            args.get("src_address"),
            args.get("dst_address"),
            args.get("src_port"),
            args.get("dst_port"),
            args.get("protocol"),
            args.get("in_interface"),
            args.get("out_interface"),
            args.get("to_addresses"),
            args.get("to_ports"),
            args.get("comment"),
            args.get("disabled", False),
            args.get("log", False),
            args.get("log_prefix"),
            args.get("place_before")
        ),
        "list_nat_rules": lambda args: mikrotik_list_nat_rules(
            args.get("chain_filter"),
            args.get("action_filter"),
            args.get("src_address_filter"),
            args.get("dst_address_filter"),
            args.get("protocol_filter"),
            args.get("interface_filter"),
            args.get("disabled_only", False),
            args.get("invalid_only", False)
        ),
        "get_nat_rule": lambda args: mikrotik_get_nat_rule(
            args["rule_id"]
        ),
        "update_nat_rule": lambda args: mikrotik_update_nat_rule(
            args["rule_id"],
            args.get("chain"),
            args.get("action"),
            args.get("src_address"),
            args.get("dst_address"),
            args.get("src_port"),
            args.get("dst_port"),
            args.get("protocol"),
            args.get("in_interface"),
            args.get("out_interface"),
            args.get("to_addresses"),
            args.get("to_ports"),
            args.get("comment"),
            args.get("disabled"),
            args.get("log"),
            args.get("log_prefix")
        ),
        "remove_nat_rule": lambda args: mikrotik_remove_nat_rule(
            args["rule_id"]
        ),
        "move_nat_rule": lambda args: mikrotik_move_nat_rule(
            args["rule_id"],
            args["destination"]
        ),
        "enable_nat_rule": lambda args: mikrotik_enable_nat_rule(
            args["rule_id"]
        ),
        "disable_nat_rule": lambda args: mikrotik_disable_nat_rule(
            args["rule_id"]
        ),
    }
