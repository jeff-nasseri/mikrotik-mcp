import asyncio
import json
from typing import Optional

from mcp.server.fastmcp import Context

from ..app import mcp, READ, WRITE
from ..connector import execute_command_on_device
from ..inventory import get_inventory


@mcp.tool(name="list_devices", annotations=READ)
async def mikrotik_list_devices(ctx: Context) -> str:
    """
    Lists all MikroTik devices configured in the fleet inventory.

    Returns a JSON array where each element contains the device name, host,
    port, and tags.  This tool is read-only and never connects to any device.

    Returns:
        JSON array of device summaries, or a message when the inventory is empty.
    """
    await ctx.info("Listing fleet inventory devices")

    inventory = get_inventory()
    devices = inventory.get_all_devices()

    if not devices:
        return (
            "No devices are configured in the fleet inventory. "
            "Set MIKROTIK_DEVICES as a JSON array to define your fleet, e.g.:\n"
            'MIKROTIK_DEVICES=\'[{"name":"mt-nl-1","host":"1.1.1.1","tags":["nl","eu"]}]\''
        )

    summary = [
        {
            "name": d.name,
            "host": d.host,
            "port": d.port,
            "username": d.username,
            "tags": d.tags,
        }
        for d in devices
    ]
    return json.dumps(summary, indent=2)


@mcp.tool(name="run_command_on_device", annotations=WRITE)
async def mikrotik_run_command_on_device(
    ctx: Context,
    device_name: str,
    command: str,
) -> str:
    """
    Executes a RouterOS command on a specific device from the fleet inventory.

    The device is looked up by its configured name.  The command is executed via
    a new SSH connection; it does NOT run inside the active Safe Mode session (if
    any) because Safe Mode is per-connection to the default device.

    Args:
        device_name: The ``name`` of the target device as defined in MIKROTIK_DEVICES.
        command: A RouterOS CLI command string (e.g. ``/ip address print``).

    Returns:
        The command output prefixed with the device name, or an error message.
    """
    await ctx.info(f"Running command on device '{device_name}': {command}")

    inventory = get_inventory()
    device = inventory.get_device(device_name)

    if device is None:
        available = inventory.list_names()
        hint = f"Available devices: {available}" if available else "No devices are configured."
        return f"Device '{device_name}' not found in fleet inventory. {hint}"

    result = await execute_command_on_device(device, command, ctx)
    return f"{device_name}:\n{result}"


@mcp.tool(name="run_command_on_tag", annotations=WRITE)
async def mikrotik_run_command_on_tag(
    ctx: Context,
    tag: str,
    command: str,
) -> str:
    """
    Executes a RouterOS command in parallel on every device that carries the given tag.

    Results are returned as a JSON object keyed by device name so the caller can
    immediately see which devices succeeded and which failed.

    Args:
        tag: The tag to match against device tags (e.g. ``"eu"`` or ``"core"``).
        command: A RouterOS CLI command string (e.g. ``/system resource print``).

    Returns:
        JSON object mapping device names to their command output or error message.
        Example: ``{"mt-nl-1": "...", "mt-usa-1": "Error: ..."}``
    """
    await ctx.info(f"Running command on all devices tagged '{tag}': {command}")

    inventory = get_inventory()
    devices = inventory.get_devices_by_tag(tag)

    if not devices:
        all_tags: set[str] = set()
        for d in inventory.get_all_devices():
            all_tags.update(d.tags)
        hint = f"Known tags: {sorted(all_tags)}" if all_tags else "No devices are configured."
        return f"No devices found with tag '{tag}'. {hint}"

    tasks = [execute_command_on_device(d, command, ctx) for d in devices]
    raw_results = await asyncio.gather(*tasks, return_exceptions=True)

    aggregated: dict[str, str] = {}
    for device, result in zip(devices, raw_results):
        if isinstance(result, Exception):
            aggregated[device.name] = f"Error: {result}"
        else:
            aggregated[device.name] = str(result)

    return json.dumps(aggregated, indent=2)


@mcp.tool(name="run_command_on_all_devices", annotations=WRITE)
async def mikrotik_run_command_on_all_devices(
    ctx: Context,
    command: str,
    tag_filter: Optional[str] = None,
) -> str:
    """
    Executes a RouterOS command in parallel on all devices in the fleet inventory.

    Optionally restrict execution to devices that carry a specific tag via the
    ``tag_filter`` parameter.  Results are returned as a JSON object keyed by
    device name.

    Args:
        command: A RouterOS CLI command string (e.g. ``/system resource print``).
        tag_filter: Optional tag — when provided only devices carrying this tag
                    are targeted (equivalent to ``run_command_on_tag``).

    Returns:
        JSON object mapping device names to their command output or error message.
        Example: ``{"mt-nl-1": "...", "mt-usa-1": "timeout", "mt-uae-1": "..."}``
    """
    inventory = get_inventory()

    if tag_filter:
        devices = inventory.get_devices_by_tag(tag_filter)
        await ctx.info(
            f"Running command on all devices (tag='{tag_filter}'): {command}"
        )
        if not devices:
            return f"No devices found with tag '{tag_filter}'."
    else:
        devices = inventory.get_all_devices()
        await ctx.info(f"Running command on all {len(devices)} device(s): {command}")
        if not devices:
            return (
                "No devices are configured in the fleet inventory. "
                "Set MIKROTIK_DEVICES to define your fleet."
            )

    tasks = [execute_command_on_device(d, command, ctx) for d in devices]
    raw_results = await asyncio.gather(*tasks, return_exceptions=True)

    aggregated: dict[str, str] = {}
    for device, result in zip(devices, raw_results):
        if isinstance(result, Exception):
            aggregated[device.name] = f"Error: {result}"
        else:
            aggregated[device.name] = str(result)

    return json.dumps(aggregated, indent=2)
