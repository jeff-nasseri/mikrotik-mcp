from typing import Dict, Any, List, Callable
from ..scope.users import (
    mikrotik_add_user, mikrotik_list_users, mikrotik_get_user,
    mikrotik_update_user, mikrotik_remove_user, mikrotik_disable_user,
    mikrotik_enable_user, mikrotik_add_user_group, mikrotik_list_user_groups,
    mikrotik_get_user_group, mikrotik_update_user_group, mikrotik_remove_user_group,
    mikrotik_get_active_users, mikrotik_disconnect_user, mikrotik_export_user_config,
    mikrotik_set_user_ssh_keys, mikrotik_list_user_ssh_keys, mikrotik_remove_user_ssh_key
)
from mcp.types import Tool

def get_user_tools() -> List[Tool]:
    """Return the list of user management tools."""
    return [
        # User Management tools
        Tool(
            name="add_user",
            description="Adds a new user to MikroTik device",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "password": {"type": "string"},
                    "group": {"type": "string"},
                    "address": {"type": "string"},
                    "comment": {"type": "string"},
                    "disabled": {"type": "boolean"}
                },
                "required": ["name", "password"]
            },
        ),
        Tool(
            name="list_users",
            description="Lists users on MikroTik device",
            inputSchema={
                "type": "object",
                "properties": {
                    "name_filter": {"type": "string"},
                    "group_filter": {"type": "string"},
                    "disabled_only": {"type": "boolean"},
                    "active_only": {"type": "boolean"}
                },
                "required": []
            },
        ),
        Tool(
            name="get_user",
            description="Gets detailed information about a specific user",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"}
                },
                "required": ["name"]
            },
        ),
        Tool(
            name="update_user",
            description="Updates an existing user on MikroTik device",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "new_name": {"type": "string"},
                    "password": {"type": "string"},
                    "group": {"type": "string"},
                    "address": {"type": "string"},
                    "comment": {"type": "string"},
                    "disabled": {"type": "boolean"}
                },
                "required": ["name"]
            },
        ),
        Tool(
            name="remove_user",
            description="Removes a user from MikroTik device",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"}
                },
                "required": ["name"]
            },
        ),
        Tool(
            name="disable_user",
            description="Disables a user account",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"}
                },
                "required": ["name"]
            },
        ),
        Tool(
            name="enable_user",
            description="Enables a user account",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"}
                },
                "required": ["name"]
            },
        ),
        Tool(
            name="add_user_group",
            description="Adds a new user group to MikroTik device",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "policy": {"type": "array", "items": {"type": "string"}},
                    "skin": {"type": "string"},
                    "comment": {"type": "string"}
                },
                "required": ["name", "policy"]
            },
        ),
        Tool(
            name="list_user_groups",
            description="Lists user groups on MikroTik device",
            inputSchema={
                "type": "object",
                "properties": {
                    "name_filter": {"type": "string"},
                    "policy_filter": {"type": "string"}
                },
                "required": []
            },
        ),
        Tool(
            name="get_user_group",
            description="Gets detailed information about a specific user group",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"}
                },
                "required": ["name"]
            },
        ),
        Tool(
            name="update_user_group",
            description="Updates an existing user group on MikroTik device",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "new_name": {"type": "string"},
                    "policy": {"type": "array", "items": {"type": "string"}},
                    "skin": {"type": "string"},
                    "comment": {"type": "string"}
                },
                "required": ["name"]
            },
        ),
        Tool(
            name="remove_user_group",
            description="Removes a user group from MikroTik device",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"}
                },
                "required": ["name"]
            },
        ),
        Tool(
            name="get_active_users",
            description="Gets currently active/logged-in users",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            },
        ),
        Tool(
            name="disconnect_user",
            description="Disconnects an active user session",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string"}
                },
                "required": ["user_id"]
            },
        ),
        Tool(
            name="export_user_config",
            description="Exports user configuration to a file",
            inputSchema={
                "type": "object",
                "properties": {
                    "filename": {"type": "string"}
                },
                "required": []
            },
        ),
        Tool(
            name="set_user_ssh_keys",
            description="Sets SSH public keys for a user",
            inputSchema={
                "type": "object",
                "properties": {
                    "username": {"type": "string"},
                    "key_file": {"type": "string"}
                },
                "required": ["username", "key_file"]
            },
        ),
        Tool(
            name="list_user_ssh_keys",
            description="Lists SSH keys for a specific user",
            inputSchema={
                "type": "object",
                "properties": {
                    "username": {"type": "string"}
                },
                "required": ["username"]
            },
        ),
        Tool(
            name="remove_user_ssh_key",
            description="Removes an SSH key",
            inputSchema={
                "type": "object",
                "properties": {
                    "key_id": {"type": "string"}
                },
                "required": ["key_id"]
            },
        ),
    ]

def get_user_handlers() -> Dict[str, Callable]:
    """Return the handlers for user management tools."""
    return {
        "add_user": lambda args: mikrotik_add_user(
            args["name"],
            args["password"],
            args.get("group", "read"),
            args.get("address"),
            args.get("comment"),
            args.get("disabled", False)
        ),
        "list_users": lambda args: mikrotik_list_users(
            args.get("name_filter"),
            args.get("group_filter"),
            args.get("disabled_only", False),
            args.get("active_only", False)
        ),
        "get_user": lambda args: mikrotik_get_user(
            args["name"]
        ),
        "update_user": lambda args: mikrotik_update_user(
            args["name"],
            args.get("new_name"),
            args.get("password"),
            args.get("group"),
            args.get("address"),
            args.get("comment"),
            args.get("disabled")
        ),
        "remove_user": lambda args: mikrotik_remove_user(
            args["name"]
        ),
        "disable_user": lambda args: mikrotik_disable_user(
            args["name"]
        ),
        "enable_user": lambda args: mikrotik_enable_user(
            args["name"]
        ),
        "add_user_group": lambda args: mikrotik_add_user_group(
            args["name"],
            args["policy"],
            args.get("skin"),
            args.get("comment")
        ),
        "list_user_groups": lambda args: mikrotik_list_user_groups(
            args.get("name_filter"),
            args.get("policy_filter")
        ),
        "get_user_group": lambda args: mikrotik_get_user_group(
            args["name"]
        ),
        "update_user_group": lambda args: mikrotik_update_user_group(
            args["name"],
            args.get("new_name"),
            args.get("policy"),
            args.get("skin"),
            args.get("comment")
        ),
        "remove_user_group": lambda args: mikrotik_remove_user_group(
            args["name"]
        ),
        "get_active_users": lambda args: mikrotik_get_active_users(),
        "disconnect_user": lambda args: mikrotik_disconnect_user(
            args["user_id"]
        ),
        "export_user_config": lambda args: mikrotik_export_user_config(
            args.get("filename")
        ),
        "set_user_ssh_keys": lambda args: mikrotik_set_user_ssh_keys(
            args["username"],
            args["key_file"]
        ),
        "list_user_ssh_keys": lambda args: mikrotik_list_user_ssh_keys(
            args["username"]
        ),
        "remove_user_ssh_key": lambda args: mikrotik_remove_user_ssh_key(
            args["key_id"]
        ),
    }
