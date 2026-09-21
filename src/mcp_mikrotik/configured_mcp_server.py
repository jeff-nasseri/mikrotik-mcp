from mcp.server.mcpserver import MCPServer
from starlette.applications import Starlette

from . import config
from .http_security import IPAllowListMiddleware, parse_allowed_ips


class ConfiguredMCPServer(MCPServer):
    """Omit mutating tools from the catalogue in read-only mode."""

    def tool(self, *args, **kwargs):
        annotations = kwargs.get("annotations")
        if config.mikrotik_config.read_only and not (
            annotations and annotations.read_only_hint
        ):
            return lambda fn: fn
        return super().tool(*args, **kwargs)

    @staticmethod
    def _apply_ip_allowlist(app: Starlette) -> Starlette:
        allowed_ips = parse_allowed_ips(config.mikrotik_config.mcp.allowed_ips)
        if allowed_ips:
            app.add_middleware(IPAllowListMiddleware, allowed_ips=allowed_ips)
        return app

    def sse_app(self, *args, **kwargs) -> Starlette:
        return self._apply_ip_allowlist(super().sse_app(*args, **kwargs))

    def streamable_http_app(self, *args, **kwargs) -> Starlette:
        return self._apply_ip_allowlist(super().streamable_http_app(*args, **kwargs))
