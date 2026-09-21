import functools
import inspect

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from starlette.applications import Starlette

from . import config
from .http_security import IPAllowListMiddleware, parse_allowed_ips
from .sensitive import SENSITIVE_PARAMETER_NAMES, SensitiveContext, redact_sensitive_data


SENSITIVE_TOOLS = frozenset({"download_file", "generate_wireguard_client_config"})


class ConfiguredMCPServer(MCPServer):
    """Apply configured catalogue and response policies to MCP tools."""

    def tool(self, *args, **kwargs):
        annotations = kwargs.get("annotations")
        if config.mikrotik_config.read_only and not (
            annotations and annotations.read_only_hint
        ):
            return lambda fn: fn
        name = kwargs.get("name") or (args[0] if args else None)
        if config.mikrotik_config.sensitive_hiding and name in SENSITIVE_TOOLS:
            return lambda fn: fn

        decorator = super().tool(*args, **kwargs)
        if not config.mikrotik_config.sensitive_hiding:
            return decorator

        def sensitive_decorator(fn):
            signature = inspect.signature(fn)

            def prepare_call(call_args, call_kwargs):
                bound = signature.bind_partial(*call_args, **call_kwargs)
                secrets = [
                    str(value) for parameter, value in bound.arguments.items()
                    if parameter in SENSITIVE_PARAMETER_NAMES and value
                ]
                if "ctx" in bound.arguments:
                    bound.arguments["ctx"] = SensitiveContext(bound.arguments["ctx"], secrets)
                return bound, secrets

            if inspect.iscoroutinefunction(fn):
                @functools.wraps(fn)
                async def wrapped(*call_args, **call_kwargs):
                    bound, secrets = prepare_call(call_args, call_kwargs)
                    try:
                        result = await fn(*bound.args, **bound.kwargs)
                    except Exception as exc:
                        message = redact_sensitive_data(str(exc), secrets)
                        if message == str(exc):
                            raise
                        raise RuntimeError(message) from None
                    return redact_sensitive_data(result, secrets)
            else:
                @functools.wraps(fn)
                def wrapped(*call_args, **call_kwargs):
                    bound, secrets = prepare_call(call_args, call_kwargs)
                    try:
                        result = fn(*bound.args, **bound.kwargs)
                    except Exception as exc:
                        message = redact_sensitive_data(str(exc), secrets)
                        if message == str(exc):
                            raise
                        raise RuntimeError(message) from None
                    return redact_sensitive_data(result, secrets)

            return decorator(wrapped)

        return sensitive_decorator

    async def call_tool(self, name, arguments, context=None):
        if not config.mikrotik_config.sensitive_hiding:
            return await super().call_tool(name, arguments, context)

        secrets = [
            str(value) for parameter, value in arguments.items()
            if parameter in SENSITIVE_PARAMETER_NAMES and value
        ]
        try:
            return await super().call_tool(name, arguments, context)
        except Exception as exc:
            message = redact_sensitive_data(str(exc), secrets)
            if message == str(exc):
                raise
            raise ToolError(message) from None

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
