import logging

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from starlette.requests import Request
from starlette.responses import Response

from .security import SecurityError, scan_arguments

logger = logging.getLogger(__name__)


class GuardedFastMCP(FastMCP):
    """FastMCP subclass that scans tool arguments for prompt-injection.

    The optional LLM Guard scan runs here — on the raw, untrusted *arguments*
    supplied by the MCP client — rather than on the assembled RouterOS command
    (which the model misclassifies as injection).  When scanning is disabled or
    ``llm-guard`` is not installed, ``scan_arguments`` is a no-op, so this adds
    no overhead to the default configuration.

    A detected injection raises ``SecurityError``; the MCP framework turns the
    raised exception into an ``isError`` tool result carrying the message, so
    the request never reaches the device.
    """

    async def call_tool(self, name, arguments):
        try:
            scan_arguments(name, arguments)
        except SecurityError as exc:
            logger.warning(f"Blocked tool call '{name}': {exc}")
            raise
        return await super().call_tool(name, arguments)


mcp = GuardedFastMCP("mcp-mikrotik")

# ── Behaviour presets ──────────────────────────────────────────────────────
# These capture the *risk profile* of a tool (MCP spec §Tool Annotations).
# Always pass them through annotate() so every tool also carries a short
# human-readable title, which allows MCP clients to surface compact tool
# lists without re-rendering full descriptions — shrinking prompt context.
READ = ToolAnnotations(readOnlyHint=True, idempotentHint=True, openWorldHint=False)
WRITE = ToolAnnotations(destructiveHint=False, openWorldHint=False)
WRITE_IDEMPOTENT = ToolAnnotations(destructiveHint=False, idempotentHint=True, openWorldHint=False)
DESTRUCTIVE = ToolAnnotations(destructiveHint=True, idempotentHint=True, openWorldHint=False)
DANGEROUS = ToolAnnotations(destructiveHint=True, openWorldHint=False)


def annotate(base: ToolAnnotations, title: str) -> ToolAnnotations:
    """Return a copy of *base* with a human-readable *title* attached.

    The ``title`` field (MCP spec 2025-03-26) gives MCP clients a short
    display name they can show in place of the full description, reducing
    the number of tokens sent to the LLM when listing available tools.

    Usage::

        @mcp.tool(name="get_dns_settings", annotations=annotate(READ, "DNS Settings"))
        async def mikrotik_get_dns_settings(ctx: Context) -> str: ...
    """
    return ToolAnnotations(
        title=title,
        readOnlyHint=base.readOnlyHint,
        destructiveHint=base.destructiveHint,
        idempotentHint=base.idempotentHint,
        openWorldHint=base.openWorldHint,
    )


# Only available on HTTP transports (sse, streamable-http)
@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> Response:
    return Response("OK", media_type="text/plain")


# Import scope modules to trigger @mcp.tool() registration
from mcp_mikrotik.scope import (  # noqa: F401, E402
    backup, dhcp, dns, firewall_filter, firewall_nat,
    interfaces, ip_address, ip_pool, logs, queue, safe_mode, routes, users, vlan, wireless, wireguard,
)
