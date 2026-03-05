from typing import Optional

from mcp.server.fastmcp import Context, FastMCP
from mcp.types import ToolAnnotations
from starlette.requests import Request
from starlette.responses import Response

from mcp_mikrotik import config
from mcp_mikrotik.config import DeviceConnection

mcp = FastMCP("mcp-mikrotik")

READ = ToolAnnotations(readOnlyHint=True, idempotentHint=True, openWorldHint=False)
WRITE = ToolAnnotations(destructiveHint=False, openWorldHint=False)
WRITE_IDEMPOTENT = ToolAnnotations(destructiveHint=False, idempotentHint=True, openWorldHint=False)
DESTRUCTIVE = ToolAnnotations(destructiveHint=True, idempotentHint=True, openWorldHint=False)
DANGEROUS = ToolAnnotations(destructiveHint=True, openWorldHint=False)


# Only available on HTTP transports (sse, streamable-http)
@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> Response:
    return Response("OK", media_type="text/plain")


@mcp.tool(name="connect_to_device", annotations=WRITE)
async def connect_to_device(
    ctx: Context,
    host: str,
    name: Optional[str] = None,
    username: str = "admin",
    password: str = "",
    port: int = 22,
    key_filename: Optional[str] = None,
    make_default: bool = True,
) -> str:
    """
    Register a MikroTik device for use in this session.
    Multiple devices can be registered under different names.
    All other tools accept an optional 'device' parameter to select which device to use.

    Args:
        host: IP address or hostname of the MikroTik device
        name: A short name for this device (e.g. "main-router", "switch-1"). Defaults to the host value.
        username: SSH username (default: admin)
        password: SSH password (default: empty)
        port: SSH port (default: 22)
        key_filename: Optional path to SSH private key file
        make_default: Whether to make this the default device (default: true)
    """
    device_name = name or host
    await ctx.info(f"Registering device '{device_name}' at {host}:{port}")

    conn = DeviceConnection(
        host=host,
        username=username,
        password=password,
        port=port,
        key_filename=key_filename,
    )
    config.device_registry.add(device_name, conn, make_default=make_default)

    default_note = " (default)" if config.device_registry.default_name == device_name else ""
    return f"Device '{device_name}' registered at {host}:{port} as {username}{default_note}"


@mcp.tool(name="disconnect_device", annotations=WRITE)
async def disconnect_device(ctx: Context, name: Optional[str] = None) -> str:
    """
    Remove a registered MikroTik device.

    Args:
        name: Device name to remove. If not specified, removes the default device.
    """
    registry = config.device_registry
    target = name or registry.default_name

    if target is None:
        return "No devices are currently registered"

    if registry.remove(target):
        await ctx.info(f"Removed device '{target}'")
        return f"Device '{target}' removed"
    else:
        return f"Device '{target}' not found"


@mcp.tool(name="list_devices", annotations=READ)
async def list_devices(ctx: Context) -> str:
    """
    List all registered MikroTik devices and show which is the default.
    """
    registry = config.device_registry
    cfg = config.mikrotik_config

    lines = []

    if not registry.is_empty:
        for device_name in registry.device_names:
            conn = registry.get(device_name)
            default_marker = " (default)" if device_name == registry.default_name else ""
            lines.append(f"- {device_name}: {conn.host}:{conn.port} as {conn.username}{default_marker}")
    elif cfg.host:
        lines.append(f"- (from config): {cfg.host}:{cfg.port} as {cfg.username} (default)")
    else:
        return "No devices configured. Use connect_to_device to register a MikroTik device."

    return "Registered devices:\n" + "\n".join(lines)


@mcp.tool(name="set_default_device", annotations=WRITE)
async def set_default_device(ctx: Context, name: str) -> str:
    """
    Set which registered device is used by default when no device name is specified.

    Args:
        name: Device name to set as default
    """
    registry = config.device_registry
    if name not in registry.device_names:
        available = ", ".join(registry.device_names) if not registry.is_empty else "none"
        return f"Device '{name}' not found. Available: {available}"

    registry.default_name = name
    return f"Default device set to '{name}'"


# Import scope modules to trigger @mcp.tool() registration
from mcp_mikrotik.scope import (  # noqa: F401, E402
    backup, dhcp, dns, firewall_filter, firewall_nat,
    ip_address, ip_pool, logs, routes, users, vlan, wireless, wireguard,
)
