from typing import Literal, Optional, List
from ..app import mcp, READ, WRITE, DANGEROUS
from ..connector import execute_mikrotik_command
from mcp.server.fastmcp import Context
import base64
import time
import os

@mcp.tool(name="create_backup", annotations=WRITE)
async def mikrotik_create_backup(
    ctx: Context,
    name: Optional[str] = None,
    dont_encrypt: bool = False,
    include_password: bool = True,
    comment: Optional[str] = None
) -> str:
    """
    Creates a system backup on MikroTik device.

    Args:
        name: Backup filename (without extension). If not specified, uses timestamp
        dont_encrypt: Don't encrypt the backup file
        include_password: Include passwords in export
        comment: Optional comment for the backup

    Returns:
        Command output or error message
    """
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

@mcp.tool(name="list_backups", annotations=READ)
async def mikrotik_list_backups(
    ctx: Context,
    name_filter: Optional[str] = None,
    include_exports: bool = False
) -> str:
    """
    Lists backup files on MikroTik device.

    Args:
        name_filter: Filter by filename (partial match)
        include_exports: Also list export (.rsc) files

    Returns:
        List of backup files
    """
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

@mcp.tool(name="create_export", annotations=READ)
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
    """
    Creates a configuration export on MikroTik device.

    Args:
        name: Export filename (without extension). If not specified, uses timestamp
        file_format: Export format ('rsc' for script, 'json', 'xml')
        export_type: Export type ('full', 'compact', 'verbose')
        hide_sensitive: Hide sensitive information (passwords, certificates)
        verbose: Include default values in export
        compact: Use compact export format
        comment: Optional comment for the export

    Returns:
        Command output or error message
    """
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

@mcp.tool(name="export_section", annotations=READ)
async def mikrotik_export_section(
    section: str,
    ctx: Context,
    name: Optional[str] = None,
    hide_sensitive: bool = True,
    compact: bool = False
) -> str:
    """
    Exports a specific configuration section.

    Args:
        section: Section to export (e.g., 'ip address', 'interface', 'system')
        name: Export filename. If not specified, uses section name and timestamp
        hide_sensitive: Hide sensitive information
        compact: Use compact export format

    Returns:
        Command output or error message
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

@mcp.tool(name="download_file", annotations=READ)
async def mikrotik_download_file(
    filename: str,
    ctx: Context,
    file_type: Literal["backup", "export"] = "backup"
) -> str:
    """
    Downloads a file from MikroTik device (backup or export).

    Args:
        filename: Name of the file to download
        file_type: Type of file ('backup' or 'export')

    Returns:
        Base64 encoded file content or error message
    """
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

@mcp.tool(name="upload_file", annotations=WRITE)
async def mikrotik_upload_file(
    filename: str,
    content_base64: str,
    ctx: Context
) -> str:
    """
    Uploads a file to MikroTik device (for restore operations).

    Args:
        filename: Name for the uploaded file
        content_base64: Base64 encoded file content

    Returns:
        Command output or error message
    """
    await ctx.info(f"Uploading file: filename={filename}")

    # Decode base64 content
    try:
        content = base64.b64decode(content_base64).decode('utf-8')
    except Exception as e:
        return f"Failed to decode file content: {str(e)}"

    # This is a simplified version - actual implementation would need proper file upload
    # For now, we'll simulate it
    return f"File '{filename}' uploaded successfully (simulated)."

@mcp.tool(name="restore_backup", annotations=DANGEROUS)
async def mikrotik_restore_backup(
    filename: str,
    ctx: Context,
    password: Optional[str] = None
) -> str:
    """
    Restores a system backup on MikroTik device.

    Args:
        filename: Backup filename to restore
        password: Password for encrypted backup (if applicable)

    Returns:
        Command output or error message
    """
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

@mcp.tool(name="import_configuration", annotations=DANGEROUS)
async def mikrotik_import_configuration(
    filename: str,
    ctx: Context,
    run_after_reset: bool = False,
    verbose: bool = False
) -> str:
    """
    Imports a configuration script (.rsc file).

    Args:
        filename: Script filename to import
        run_after_reset: Run script after system reset
        verbose: Show verbose output during import

    Returns:
        Command output or error message
    """
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

@mcp.tool(name="remove_file", annotations=DANGEROUS)
async def mikrotik_remove_file(
    filename: str,
    ctx: Context
) -> str:
    """
    Removes a file from MikroTik device.

    Args:
        filename: Name of the file to remove

    Returns:
        Command output or error message
    """
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

@mcp.tool(name="backup_info", annotations=READ)
async def mikrotik_backup_info(
    filename: str,
    ctx: Context
) -> str:
    """
    Gets detailed information about a backup file.

    Args:
        filename: Backup filename

    Returns:
        Detailed information about the backup
    """
    await ctx.info(f"Getting backup info: filename={filename}")

    # Get file details
    cmd = f"/file print detail where name={filename}"
    result = await execute_mikrotik_command(cmd, ctx)

    if not result or result.strip() == "":
        return f"Backup file '{filename}' not found."

    return f"BACKUP FILE DETAILS:\n\n{result}"
