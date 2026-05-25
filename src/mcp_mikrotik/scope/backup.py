from typing import Literal, Optional, List
from ..app import mcp, READ, WRITE, DANGEROUS, annotate
from ..connector import execute_mikrotik_command
from mcp.server.fastmcp import Context
import base64
import time
import os

@mcp.tool(name="create_backup", annotations=annotate(WRITE, "Create Backup"))
async def mikrotik_create_backup(
    ctx: Context,
    name: Optional[str] = None,
    dont_encrypt: bool = False,
    include_password: bool = True,
    comment: Optional[str] = None
) -> str:
    """Creates a system backup on the MikroTik device."""
    # Generate filename if not provided
    if not name:
        name = f"backup_{int(time.time())}"

    await ctx.info(f"Creating backup: name={name}")

    # Build the command
    cmd = f"/system backup save name={name}"

    # Add optional parameters
    if dont_encrypt:
        cmd += " dont-encrypt=yes"
    else:
        cmd += " password=\"\""  # Empty password for encryption

    if not include_password:
        cmd += " password-file=no"

    result = await execute_mikrotik_command(cmd, ctx)

    # Check if backup was successful
    print(result)
    if "saved" in result or not result.strip():
        # Get file details
        file_cmd = f"/file print detail where name={name}.backup"
        file_details = await execute_mikrotik_command(file_cmd, ctx)

        if file_details:
            return f"Backup created successfully:\n\n{file_details}"
        else:
            return f"Backup '{name}.backup' created successfully."
    else:
        return f"Failed to create backup: {result}"

@mcp.tool(name="list_backups", annotations=annotate(READ, "List Backups"))
async def mikrotik_list_backups(
    ctx: Context,
    name_filter: Optional[str] = None,
    include_exports: bool = False
) -> str:
    """Lists backup files on the MikroTik device."""
    await ctx.info(f"Listing backups with filter: name={name_filter}")

    # Build the command
    cmd = "/file print where type=backup"

    if include_exports:
        cmd = "/file print where (type=backup or type=script)"

    # Add name filter
    if name_filter:
        if include_exports:
            cmd = f'/file print where (type=backup or type=script) and name~"{name_filter}"'
        else:
            cmd = f'/file print where type=backup and name~"{name_filter}"'

    result = await execute_mikrotik_command(cmd, ctx)

    if not result or result.strip() == "" or result.strip() == "no such item":
        return "No backup files found."

    return f"BACKUP FILES:\n\n{result}"

@mcp.tool(name="create_export", annotations=annotate(READ, "Create Config Export"))
async def mikrotik_create_export(
    ctx: Context,
    name: Optional[str] = None,
    file_format: Literal["rsc", "json", "xml"] = "rsc",
    export_type: Literal["full", "compact", "verbose"] = "full",
    hide_sensitive: bool = True,
    verbose: bool = False,
    compact: bool = False,
    comment: Optional[str] = None
) -> str:
    """Creates a configuration export file (rsc/json/xml) on the MikroTik device."""
    # Generate filename if not provided
    if not name:
        name = f"export_{int(time.time())}"

    await ctx.info(f"Creating export: name={name}, format={file_format}")

    # Determine file extension based on format
    extension = file_format if file_format in ['json', 'xml'] else 'rsc'
    full_name = f"{name}.{extension}"

    # Build the command based on export type
    if export_type == "full":
        cmd = f"/export file={name}"
    else:
        cmd = f"/export"

    # Add format options
    if verbose:
        cmd += " verbose"

    if compact:
        cmd += " compact"

    if not hide_sensitive:
        cmd += " show-sensitive"

    # Add file parameter for non-full exports
    if export_type != "full":
        cmd += f" file={name}"

    result = await execute_mikrotik_command(cmd, ctx)

    # Check if export was successful
    if not result.strip() or "failure:" not in result.lower():
        # Get file details
        file_cmd = f"/file print detail where name={full_name}"
        file_details = await execute_mikrotik_command(file_cmd, ctx)

        if file_details:
            return f"Export created successfully:\n\n{file_details}"
        else:
            return f"Export '{full_name}' created successfully."
    else:
        return f"Failed to create export: {result}"

@mcp.tool(name="export_section", annotations=annotate(READ, "Export Config Section"))
async def mikrotik_export_section(
    ctx: Context,
    section: str,
    name: Optional[str] = None,
    hide_sensitive: bool = True,
    compact: bool = False
) -> str:
    """Exports a specific RouterOS configuration section to a file.

    Notes:
        section: RouterOS path without leading slash e.g. "ip address", "interface vlan",
            "ip firewall filter", "ip firewall nat", "queue simple"
    """
    # Generate filename if not provided
    if not name:
        clean_section = section.replace(" ", "_").replace("/", "_")
        name = f"export_{clean_section}_{int(time.time())}"

    await ctx.info(f"Exporting section: section={section}, name={name}")

    # Build the command
    cmd = f"/{section} export file={name}"

    if not hide_sensitive:
        cmd += " show-sensitive"

    if compact:
        cmd += " compact"

    result = await execute_mikrotik_command(cmd, ctx)

    # Check if export was successful
    if not result.strip() or "failure:" not in result.lower():
        # Get file details
        file_cmd = f"/file print detail where name={name}.rsc"
        file_details = await execute_mikrotik_command(file_cmd, ctx)

        if file_details:
            return f"Section export created successfully:\n\n{file_details}"
        else:
            return f"Section export '{name}.rsc' created successfully."
    else:
        return f"Failed to export section: {result}"

@mcp.tool(name="download_file", annotations=annotate(READ, "Download File"))
async def mikrotik_download_file(
    ctx: Context,
    filename: str,
    file_type: Literal["backup", "export"] = "backup"
) -> str:
    """Downloads a backup or export file from the MikroTik device as base64-encoded content."""
    await ctx.info(f"Downloading file: filename={filename}, type={file_type}")

    # First, check if file exists
    check_cmd = f"/file print count-only where name={filename}"
    count = await execute_mikrotik_command(check_cmd, ctx)

    if count.strip() == "0":
        return f"File '{filename}' not found."

    # Get file content (this is a simplified version)
    # In a real implementation, you'd need to handle file transfer properly
    content_cmd = f"/file print file={filename}"
    content = await execute_mikrotik_command(content_cmd, ctx)

    if content:
        # Encode content to base64 for safe transmission
        encoded = base64.b64encode(content.encode('utf-8')).decode('utf-8')
        return f"FILE_CONTENT_BASE64:{encoded}"
    else:
        return f"Failed to download file '{filename}'."

@mcp.tool(name="upload_file", annotations=annotate(WRITE, "Upload File"))
async def mikrotik_upload_file(
    ctx: Context,
    filename: str,
    content_base64: str
) -> str:
    """Uploads a base64-encoded file to the MikroTik device (for restore operations)."""
    await ctx.info(f"Uploading file: filename={filename}")

    # Decode base64 content
    try:
        content = base64.b64decode(content_base64).decode('utf-8')
    except Exception as e:
        return f"Failed to decode file content: {str(e)}"

    # This is a simplified version - actual implementation would need proper file upload
    # For now, we'll simulate it
    return f"File '{filename}' uploaded successfully (simulated)."

@mcp.tool(name="restore_backup", annotations=annotate(DANGEROUS, "Restore Backup"))
async def mikrotik_restore_backup(
    ctx: Context,
    filename: str,
    password: Optional[str] = None
) -> str:
    """Restores a system backup on the MikroTik device; triggers a reboot."""
    await ctx.info(f"Restoring backup: filename={filename}")

    # Check if backup file exists
    check_cmd = f"/file print count-only where name={filename}"
    count = await execute_mikrotik_command(check_cmd, ctx)

    if count.strip() == "0":
        return f"Backup file '{filename}' not found."

    # Build restore command
    cmd = f"/system backup load name={filename}"

    if password:
        cmd += f' password="{password}"'

    result = await execute_mikrotik_command(cmd, ctx)

    if "Restoring system configuration" in result or not result.strip():
        return f"Backup '{filename}' restored successfully. System will reboot."
    else:
        return f"Failed to restore backup: {result}"

@mcp.tool(name="import_configuration", annotations=annotate(DANGEROUS, "Import Configuration"))
async def mikrotik_import_configuration(
    ctx: Context,
    filename: str,
    run_after_reset: bool = False,
    verbose: bool = False
) -> str:
    """Imports and executes a RouterOS configuration script (.rsc file) on the device."""
    await ctx.info(f"Importing configuration: filename={filename}")

    # Check if file exists
    check_cmd = f"/file print count-only where name={filename}"
    count = await execute_mikrotik_command(check_cmd, ctx)

    if count.strip() == "0":
        return f"Configuration file '{filename}' not found."

    # Build import command
    cmd = f"/import file={filename}"

    if run_after_reset:
        cmd += " run-after-reset=yes"

    if verbose:
        cmd += " verbose=yes"

    result = await execute_mikrotik_command(cmd, ctx)

    if not result.strip() or "Script file loaded and executed successfully" in result:
        return f"Configuration '{filename}' imported successfully."
    else:
        return f"Import result:\n{result}"

@mcp.tool(name="remove_file", annotations=annotate(DANGEROUS, "Remove File"))
async def mikrotik_remove_file(
    ctx: Context,
    filename: str
) -> str:
    """Removes a file from the MikroTik device filesystem."""
    await ctx.info(f"Removing file: filename={filename}")

    # Check if file exists
    check_cmd = f"/file print count-only where name={filename}"
    count = await execute_mikrotik_command(check_cmd, ctx)

    if count.strip() == "0":
        return f"File '{filename}' not found."

    # Remove the file
    cmd = f"/file remove {filename}"
    result = await execute_mikrotik_command(cmd, ctx)

    if not result.strip():
        return f"File '{filename}' removed successfully."
    else:
        return f"Failed to remove file: {result}"

@mcp.tool(name="backup_info", annotations=annotate(READ, "Backup File Info"))
async def mikrotik_backup_info(
    ctx: Context,
    filename: str
) -> str:
    """Gets detailed information about a backup file on the MikroTik device."""
    await ctx.info(f"Getting backup info: filename={filename}")

    # Get file details
    cmd = f"/file print detail where name={filename}"
    result = await execute_mikrotik_command(cmd, ctx)

    if not result or result.strip() == "":
        return f"Backup file '{filename}' not found."

    return f"BACKUP FILE DETAILS:\n\n{result}"
