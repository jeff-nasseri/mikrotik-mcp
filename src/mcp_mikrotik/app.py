from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from starlette.requests import Request
from starlette.responses import Response

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


# Import scope modules to trigger @mcp.tool() registration
from mcp_mikrotik.scope import (  # noqa: F401, E402
    backup, dhcp, dns, firewall_filter, firewall_nat,
    ip_address, ip_pool, logs, routes, users, vlan, wireless,
)
