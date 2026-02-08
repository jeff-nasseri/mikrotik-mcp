from typing import Dict, Any, List, Callable
from ..scope.backup import (
    mikrotik_create_backup, mikrotik_list_backups, mikrotik_create_export,
    mikrotik_export_section, mikrotik_download_file, mikrotik_upload_file,
    mikrotik_restore_backup, mikrotik_import_configuration, mikrotik_remove_file,
    mikrotik_backup_info
)
from mcp.types import Tool

def get_backup_tools() -> List[Tool]:
    """Return the list of backup and export tools."""
    return [
        # Backup and Export tools
        Tool(
            name="create_backup",
            description="Creates a system backup on MikroTik device",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "dont_encrypt": {"type": "boolean"},
                    "include_password": {"type": "boolean"},
                    "comment": {"type": "string"}
                },
                "required": []
            },
        ),
        Tool(
            name="list_backups",
            description="Lists backup files on MikroTik device",
            inputSchema={
                "type": "object",
                "properties": {
                    "name_filter": {"type": "string"},
                    "include_exports": {"type": "boolean"}
                },
                "required": []
            },
        ),
        Tool(
            name="create_export",
            description="Creates a configuration export on MikroTik device",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "file_format": {"type": "string", "enum": ["rsc", "json", "xml"]},
                    "export_type": {"type": "string", "enum": ["full", "compact", "verbose"]},
                    "hide_sensitive": {"type": "boolean"},
                    "verbose": {"type": "boolean"},
                    "compact": {"type": "boolean"},
                    "comment": {"type": "string"}
                },
                "required": []
            },
        ),
        Tool(
            name="export_section",
            description="Exports a specific configuration section",
            inputSchema={
                "type": "object",
                "properties": {
                    "section": {"type": "string"},
                    "name": {"type": "string"},
                    "hide_sensitive": {"type": "boolean"},
                    "compact": {"type": "boolean"}
                },
                "required": ["section"]
            },
        ),
        Tool(
            name="download_file",
            description="Downloads a file from MikroTik device",
            inputSchema={
                "type": "object",
                "properties": {
                    "filename": {"type": "string"},
                    "file_type": {"type": "string", "enum": ["backup", "export"]}
                },
                "required": ["filename"]
            },
        ),
        Tool(
            name="upload_file",
            description="Uploads a file to MikroTik device",
            inputSchema={
                "type": "object",
                "properties": {
                    "filename": {"type": "string"},
                    "content_base64": {"type": "string"}
                },
                "required": ["filename", "content_base64"]
            },
        ),
        Tool(
            name="restore_backup",
            description="Restores a system backup on MikroTik device",
            inputSchema={
                "type": "object",
                "properties": {
                    "filename": {"type": "string"},
                    "password": {"type": "string"}
                },
                "required": ["filename"]
            },
        ),
        Tool(
            name="import_configuration",
            description="Imports a configuration script file",
            inputSchema={
                "type": "object",
                "properties": {
                    "filename": {"type": "string"},
                    "run_after_reset": {"type": "boolean"},
                    "verbose": {"type": "boolean"}
                },
                "required": ["filename"]
            },
        ),
        Tool(
            name="remove_file",
            description="Removes a file from MikroTik device",
            inputSchema={
                "type": "object",
                "properties": {
                    "filename": {"type": "string"}
                },
                "required": ["filename"]
            },
        ),
        Tool(
            name="backup_info",
            description="Gets detailed information about a backup file",
            inputSchema={
                "type": "object",
                "properties": {
                    "filename": {"type": "string"}
                },
                "required": ["filename"]
            },
        ),
    ]

def get_backup_handlers() -> Dict[str, Callable]:
    """Return the handlers for backup and export tools."""
    return {
        "create_backup": lambda args: mikrotik_create_backup(
            args.get("name"),
            args.get("dont_encrypt", False),
            args.get("include_password", True),
            args.get("comment")
        ),
        "list_backups": lambda args: mikrotik_list_backups(
            args.get("name_filter"),
            args.get("include_exports", False)
        ),
        "create_export": lambda args: mikrotik_create_export(
            args.get("name"),
            args.get("file_format", "rsc"),
            args.get("export_type", "full"),
            args.get("hide_sensitive", True),
            args.get("verbose", False),
            args.get("compact", False),
            args.get("comment")
        ),
        "export_section": lambda args: mikrotik_export_section(
            args["section"],
            args.get("name"),
            args.get("hide_sensitive", True),
            args.get("compact", False)
        ),
        "download_file": lambda args: mikrotik_download_file(
            args["filename"],
            args.get("file_type", "backup")
        ),
        "upload_file": lambda args: mikrotik_upload_file(
            args["filename"],
            args["content_base64"]
        ),
        "restore_backup": lambda args: mikrotik_restore_backup(
            args["filename"],
            args.get("password")
        ),
        "import_configuration": lambda args: mikrotik_import_configuration(
            args["filename"],
            args.get("run_after_reset", False),
            args.get("verbose", False)
        ),
        "remove_file": lambda args: mikrotik_remove_file(
            args["filename"]
        ),
        "backup_info": lambda args: mikrotik_backup_info(
            args["filename"]
        ),
    }
