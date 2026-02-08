from typing import Dict, Any, List, Callable
from ..scope.routes import (
    mikrotik_add_route, mikrotik_list_routes, mikrotik_get_route,
    mikrotik_update_route, mikrotik_remove_route, mikrotik_enable_route,
    mikrotik_disable_route, mikrotik_get_routing_table, mikrotik_check_route_path,
    mikrotik_get_route_cache, mikrotik_flush_route_cache, mikrotik_add_default_route,
    mikrotik_add_blackhole_route, mikrotik_get_route_statistics
)
from mcp.types import Tool

def get_route_tools() -> List[Tool]:
    """Return the list of route tools."""
    return [
        # Route tools
        Tool(
            name="add_route",
            description="Adds a route to MikroTik routing table",
            inputSchema={
                "type": "object",
                "properties": {
                    "dst_address": {"type": "string"},
                    "gateway": {"type": "string"},
                    "distance": {"type": "integer"},
                    "scope": {"type": "integer"},
                    "target_scope": {"type": "integer"},
                    "routing_mark": {"type": "string"},
                    "comment": {"type": "string"},
                    "disabled": {"type": "boolean"},
                    "vrf_interface": {"type": "string"},
                    "pref_src": {"type": "string"},
                    "check_gateway": {"type": "string"}
                },
                "required": ["dst_address", "gateway"]
            },
        ),
        Tool(
            name="list_routes",
            description="Lists routes in MikroTik routing table",
            inputSchema={
                "type": "object",
                "properties": {
                    "dst_filter": {"type": "string"},
                    "gateway_filter": {"type": "string"},
                    "routing_mark_filter": {"type": "string"},
                    "distance_filter": {"type": "integer"},
                    "active_only": {"type": "boolean"},
                    "disabled_only": {"type": "boolean"},
                    "dynamic_only": {"type": "boolean"},
                    "static_only": {"type": "boolean"}
                },
                "required": []
            },
        ),
        Tool(
            name="get_route",
            description="Gets detailed information about a specific route",
            inputSchema={
                "type": "object",
                "properties": {
                    "route_id": {"type": "string"}
                },
                "required": ["route_id"]
            },
        ),
        Tool(
            name="update_route",
            description="Updates an existing route in MikroTik routing table",
            inputSchema={
                "type": "object",
                "properties": {
                    "route_id": {"type": "string"},
                    "dst_address": {"type": "string"},
                    "gateway": {"type": "string"},
                    "distance": {"type": "integer"},
                    "scope": {"type": "integer"},
                    "target_scope": {"type": "integer"},
                    "routing_mark": {"type": "string"},
                    "comment": {"type": "string"},
                    "disabled": {"type": "boolean"},
                    "vrf_interface": {"type": "string"},
                    "pref_src": {"type": "string"},
                    "check_gateway": {"type": "string"}
                },
                "required": ["route_id"]
            },
        ),
        Tool(
            name="remove_route",
            description="Removes a route from MikroTik routing table",
            inputSchema={
                "type": "object",
                "properties": {
                    "route_id": {"type": "string"}
                },
                "required": ["route_id"]
            },
        ),
        Tool(
            name="enable_route",
            description="Enables a route",
            inputSchema={
                "type": "object",
                "properties": {
                    "route_id": {"type": "string"}
                },
                "required": ["route_id"]
            },
        ),
        Tool(
            name="disable_route",
            description="Disables a route",
            inputSchema={
                "type": "object",
                "properties": {
                    "route_id": {"type": "string"}
                },
                "required": ["route_id"]
            },
        ),
        Tool(
            name="get_routing_table",
            description="Gets a specific routing table",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_name": {"type": "string"},
                    "protocol_filter": {"type": "string"},
                    "active_only": {"type": "boolean"}
                },
                "required": []
            },
        ),
        Tool(
            name="check_route_path",
            description="Checks the route path to a destination",
            inputSchema={
                "type": "object",
                "properties": {
                    "destination": {"type": "string"},
                    "source": {"type": "string"},
                    "routing_mark": {"type": "string"}
                },
                "required": ["destination"]
            },
        ),
        Tool(
            name="get_route_cache",
            description="Gets the route cache",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            },
        ),
        Tool(
            name="flush_route_cache",
            description="Flushes the route cache",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            },
        ),
        Tool(
            name="add_default_route",
            description="Adds a default route (0.0.0.0/0)",
            inputSchema={
                "type": "object",
                "properties": {
                    "gateway": {"type": "string"},
                    "distance": {"type": "integer"},
                    "comment": {"type": "string"},
                    "check_gateway": {"type": "string"}
                },
                "required": ["gateway"]
            },
        ),
        Tool(
            name="add_blackhole_route",
            description="Adds a blackhole route",
            inputSchema={
                "type": "object",
                "properties": {
                    "dst_address": {"type": "string"},
                    "distance": {"type": "integer"},
                    "comment": {"type": "string"}
                },
                "required": ["dst_address"]
            },
        ),
        Tool(
            name="get_route_statistics",
            description="Gets routing table statistics",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            },
        ),
    ]

def get_route_handlers() -> Dict[str, Callable]:
    """Return the handlers for route tools."""
    return {
        "add_route": lambda args: mikrotik_add_route(
            args["dst_address"],
            args["gateway"],
            args.get("distance"),
            args.get("scope"),
            args.get("target_scope"),
            args.get("routing_mark"),
            args.get("comment"),
            args.get("disabled", False),
            args.get("vrf_interface"),
            args.get("pref_src"),
            args.get("check_gateway")
        ),
        "list_routes": lambda args: mikrotik_list_routes(
            args.get("dst_filter"),
            args.get("gateway_filter"),
            args.get("routing_mark_filter"),
            args.get("distance_filter"),
            args.get("active_only", False),
            args.get("disabled_only", False),
            args.get("dynamic_only", False),
            args.get("static_only", False)
        ),
        "get_route": lambda args: mikrotik_get_route(
            args["route_id"]
        ),
        "update_route": lambda args: mikrotik_update_route(
            args["route_id"],
            args.get("dst_address"),
            args.get("gateway"),
            args.get("distance"),
            args.get("scope"),
            args.get("target_scope"),
            args.get("routing_mark"),
            args.get("comment"),
            args.get("disabled"),
            args.get("vrf_interface"),
            args.get("pref_src"),
            args.get("check_gateway")
        ),
        "remove_route": lambda args: mikrotik_remove_route(
            args["route_id"]
        ),
        "enable_route": lambda args: mikrotik_enable_route(
            args["route_id"]
        ),
        "disable_route": lambda args: mikrotik_disable_route(
            args["route_id"]
        ),
        "get_routing_table": lambda args: mikrotik_get_routing_table(
            args.get("table_name", "main"),
            args.get("protocol_filter"),
            args.get("active_only", True)
        ),
        "check_route_path": lambda args: mikrotik_check_route_path(
            args["destination"],
            args.get("source"),
            args.get("routing_mark")
        ),
        "get_route_cache": lambda args: mikrotik_get_route_cache(),
        "flush_route_cache": lambda args: mikrotik_flush_route_cache(),
        "add_default_route": lambda args: mikrotik_add_default_route(
            args["gateway"],
            args.get("distance", 1),
            args.get("comment"),
            args.get("check_gateway", "ping")
        ),
        "add_blackhole_route": lambda args: mikrotik_add_blackhole_route(
            args["dst_address"],
            args.get("distance", 1),
            args.get("comment")
        ),
        "get_route_statistics": lambda args: mikrotik_get_route_statistics(),
    }
