from mcp.server.mcpserver import MCPServer

from . import config


class ConfiguredMCPServer(MCPServer):
    """Omit mutating tools from the catalogue in read-only mode."""

    def tool(self, *args, **kwargs):
        annotations = kwargs.get("annotations")
        if config.mikrotik_config.read_only and not (
            annotations and annotations.read_only_hint
        ):
            return lambda fn: fn
        return super().tool(*args, **kwargs)
