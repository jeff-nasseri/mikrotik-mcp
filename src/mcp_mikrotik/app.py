from typing import Optional

from mcp.server.fastmcp import Context, FastMCP
from mcp.types import ToolAnnotations
from starlette.requests import Request
from starlette.responses import Response

from mcp_mikrotik import config

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
    username: str = "admin",
    password: str = "",
    port: int = 22,
    key_filename: Optional[str] = None,
) -> str:
    """
    Connect to a MikroTik device. Sets the target device for all subsequent commands.
    Must be called before using any other tools if no default host is configured.

    Args:
        host: IP address or hostname of the MikroTik device
        username: SSH username (default: admin)
        password: SSH password (default: empty)
        port: SSH port (default: 22)
        key_filename: Optional path to SSH private key file
    """
    await ctx.info(f"Setting target device to {host}")

    state = config.connection_state
    state.host = host
    state.username = username
    state.password = password
    state.port = port
    state.key_filename = key_filename

    return f"Connected to MikroTik device at {host}:{port} as {username}"


@mcp.tool(name="disconnect_device", annotations=WRITE)
async def disconnect_device(ctx: Context) -> str:
    """
    Disconnect from the current MikroTik device. Clears the connection state
    so that a new device can be targeted.
    """
    state = config.connection_state
    if not state.is_set:
        return "No device is currently connected"

    old_host = state.host
    state.clear()
    await ctx.info(f"Disconnected from {old_host}")
    return f"Disconnected from {old_host}"


@mcp.tool(name="get_connection_info", annotations=READ)
async def get_connection_info(ctx: Context) -> str:
    """
    Returns the current MikroTik device connection information.
    Shows which device commands will be sent to.
    """
    state = config.connection_state
    cfg = config.mikrotik_config

    host = state.host if state.host is not None else cfg.host
    username = state.username if state.username is not None else cfg.username
    port = state.port if state.port is not None else cfg.port
    source = "conversation" if state.is_set else "configuration"

    if host is None:
        return "No device configured. Use connect_to_device to specify a MikroTik device."

    return f"Host: {host}\nPort: {port}\nUsername: {username}\nSource: {source}"


# Import scope modules to trigger @mcp.tool() registration
from mcp_mikrotik.scope import (  # noqa: F401, E402
    backup, dhcp, dns, firewall_filter, firewall_nat,
    ip_address, ip_pool, logs, routes, users, vlan, wireless, wireguard,
)
