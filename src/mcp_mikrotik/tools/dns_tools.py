from typing import Dict, Any, List, Callable
from ..scope.dns import (
    mikrotik_set_dns_servers, mikrotik_get_dns_settings,
    mikrotik_add_dns_static, mikrotik_list_dns_static,
    mikrotik_get_dns_static, mikrotik_update_dns_static,
    mikrotik_remove_dns_static, mikrotik_enable_dns_static,
    mikrotik_disable_dns_static, mikrotik_get_dns_cache,
    mikrotik_flush_dns_cache, mikrotik_get_dns_cache_statistics,
    mikrotik_add_dns_regexp, mikrotik_test_dns_query,
    mikrotik_export_dns_config
)
from mcp.types import Tool

def get_dns_tools() -> List[Tool]:
    """Return the list of DNS tools."""
    return [
        # DNS tools
        Tool(
            name="set_dns_servers",
            description="Sets DNS server configuration on MikroTik device",
            inputSchema={
                "type": "object",
                "properties": {
                    "servers": {"type": "array", "items": {"type": "string"}},
                    "allow_remote_requests": {"type": "boolean"},
                    "max_udp_packet_size": {"type": "integer"},
                    "max_concurrent_queries": {"type": "integer"},
                    "cache_size": {"type": "integer"},
                    "cache_max_ttl": {"type": "string"},
                    "use_doh": {"type": "boolean"},
                    "doh_server": {"type": "string"},
                    "verify_doh_cert": {"type": "boolean"}
                },
                "required": ["servers"]
            },
        ),
        Tool(
            name="get_dns_settings",
            description="Gets current DNS configuration",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            },
        ),
        Tool(
            name="add_dns_static",
            description="Adds a static DNS entry",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "address": {"type": "string"},
                    "cname": {"type": "string"},
                    "mx_preference": {"type": "integer"},
                    "mx_exchange": {"type": "string"},
                    "text": {"type": "string"},
                    "srv_priority": {"type": "integer"},
                    "srv_weight": {"type": "integer"},
                    "srv_port": {"type": "integer"},
                    "srv_target": {"type": "string"},
                    "ttl": {"type": "string"},
                    "comment": {"type": "string"},
                    "disabled": {"type": "boolean"},
                    "regexp": {"type": "string"}
                },
                "required": ["name"]
            },
        ),
        Tool(
            name="list_dns_static",
            description="Lists static DNS entries",
            inputSchema={
                "type": "object",
                "properties": {
                    "name_filter": {"type": "string"},
                    "address_filter": {"type": "string"},
                    "type_filter": {"type": "string"},
                    "disabled_only": {"type": "boolean"},
                    "regexp_only": {"type": "boolean"}
                },
                "required": []
            },
        ),
        Tool(
            name="get_dns_static",
            description="Gets details of a specific static DNS entry",
            inputSchema={
                "type": "object",
                "properties": {
                    "entry_id": {"type": "string"}
                },
                "required": ["entry_id"]
            },
        ),
        Tool(
            name="update_dns_static",
            description="Updates an existing static DNS entry",
            inputSchema={
                "type": "object",
                "properties": {
                    "entry_id": {"type": "string"},
                    "name": {"type": "string"},
                    "address": {"type": "string"},
                    "cname": {"type": "string"},
                    "mx_preference": {"type": "integer"},
                    "mx_exchange": {"type": "string"},
                    "text": {"type": "string"},
                    "srv_priority": {"type": "integer"},
                    "srv_weight": {"type": "integer"},
                    "srv_port": {"type": "integer"},
                    "srv_target": {"type": "string"},
                    "ttl": {"type": "string"},
                    "comment": {"type": "string"},
                    "disabled": {"type": "boolean"},
                    "regexp": {"type": "string"}
                },
                "required": ["entry_id"]
            },
        ),
        Tool(
            name="remove_dns_static",
            description="Removes a static DNS entry",
            inputSchema={
                "type": "object",
                "properties": {
                    "entry_id": {"type": "string"}
                },
                "required": ["entry_id"]
            },
        ),
        Tool(
            name="enable_dns_static",
            description="Enables a static DNS entry",
            inputSchema={
                "type": "object",
                "properties": {
                    "entry_id": {"type": "string"}
                },
                "required": ["entry_id"]
            },
        ),
        Tool(
            name="disable_dns_static",
            description="Disables a static DNS entry",
            inputSchema={
                "type": "object",
                "properties": {
                    "entry_id": {"type": "string"}
                },
                "required": ["entry_id"]
            },
        ),
        Tool(
            name="get_dns_cache",
            description="Gets the current DNS cache",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            },
        ),
        Tool(
            name="flush_dns_cache",
            description="Flushes the DNS cache",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            },
        ),
        Tool(
            name="get_dns_cache_statistics",
            description="Gets DNS cache statistics",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            },
        ),
        Tool(
            name="add_dns_regexp",
            description="Adds a DNS regexp entry for pattern matching",
            inputSchema={
                "type": "object",
                "properties": {
                    "regexp": {"type": "string"},
                    "address": {"type": "string"},
                    "ttl": {"type": "string"},
                    "comment": {"type": "string"},
                    "disabled": {"type": "boolean"}
                },
                "required": ["regexp", "address"]
            },
        ),
        Tool(
            name="test_dns_query",
            description="Tests a DNS query",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "server": {"type": "string"},
                    "type": {"type": "string"}
                },
                "required": ["name"]
            },
        ),
        Tool(
            name="export_dns_config",
            description="Exports DNS configuration to a file",
            inputSchema={
                "type": "object",
                "properties": {
                    "filename": {"type": "string"}
                },
                "required": []
            },
        ),
    ]

def get_dns_handlers() -> Dict[str, Callable]:
    """Return the handlers for DNS tools."""
    return {
        "set_dns_servers": lambda args: mikrotik_set_dns_servers(
            args["servers"],
            args.get("allow_remote_requests", False),
            args.get("max_udp_packet_size"),
            args.get("max_concurrent_queries"),
            args.get("cache_size"),
            args.get("cache_max_ttl"),
            args.get("use_doh", False),
            args.get("doh_server"),
            args.get("verify_doh_cert", True)
        ),
        "get_dns_settings": lambda args: mikrotik_get_dns_settings(),
        "add_dns_static": lambda args: mikrotik_add_dns_static(
            args["name"],
            args.get("address"),
            args.get("cname"),
            args.get("mx_preference"),
            args.get("mx_exchange"),
            args.get("text"),
            args.get("srv_priority"),
            args.get("srv_weight"),
            args.get("srv_port"),
            args.get("srv_target"),
            args.get("ttl"),
            args.get("comment"),
            args.get("disabled", False),
            args.get("regexp")
        ),
        "list_dns_static": lambda args: mikrotik_list_dns_static(
            args.get("name_filter"),
            args.get("address_filter"),
            args.get("type_filter"),
            args.get("disabled_only", False),
            args.get("regexp_only", False)
        ),
        "get_dns_static": lambda args: mikrotik_get_dns_static(
            args["entry_id"]
        ),
        "update_dns_static": lambda args: mikrotik_update_dns_static(
            args["entry_id"],
            args.get("name"),
            args.get("address"),
            args.get("cname"),
            args.get("mx_preference"),
            args.get("mx_exchange"),
            args.get("text"),
            args.get("srv_priority"),
            args.get("srv_weight"),
            args.get("srv_port"),
            args.get("srv_target"),
            args.get("ttl"),
            args.get("comment"),
            args.get("disabled"),
            args.get("regexp")
        ),
        "remove_dns_static": lambda args: mikrotik_remove_dns_static(
            args["entry_id"]
        ),
        "enable_dns_static": lambda args: mikrotik_enable_dns_static(
            args["entry_id"]
        ),
        "disable_dns_static": lambda args: mikrotik_disable_dns_static(
            args["entry_id"]
        ),
        "get_dns_cache": lambda args: mikrotik_get_dns_cache(),
        "flush_dns_cache": lambda args: mikrotik_flush_dns_cache(),
        "get_dns_cache_statistics": lambda args: mikrotik_get_dns_cache_statistics(),
        "add_dns_regexp": lambda args: mikrotik_add_dns_regexp(
            args["regexp"],
            args["address"],
            args.get("ttl", "1d"),
            args.get("comment"),
            args.get("disabled", False)
        ),
        "test_dns_query": lambda args: mikrotik_test_dns_query(
            args["name"],
            args.get("server"),
            args.get("type", "A")
        ),
        "export_dns_config": lambda args: mikrotik_export_dns_config(
            args.get("filename")
        ),
    }
