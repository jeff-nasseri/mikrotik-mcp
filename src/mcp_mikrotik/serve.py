"""
Main module for MikroTik MCP server.
"""
import sys
from .logger import app_logger
from typing import Dict, List, Any

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import TextContent, Tool
except ImportError as e:
    print(f"Error importing MCP: {e}")
    print(f"Current Python path: {sys.path}")
    sys.exit(1)

from .tools.tool_registry import get_all_tools, get_all_handlers

async def serve() -> None:
    """
    Main function to run the MCP server for MikroTik commands.
    """
    app_logger.info("Starting MikroTik MCP server")
    server = Server("mcp-mikrotik")

    @server.list_tools()
    async def list_tools() -> List[Tool]:
        app_logger.info("Listing available tools")
        return get_all_tools()

    @server.call_tool()
    async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
        app_logger.info(f"Tool call: {name} with arguments {arguments}")

        result = ""
        handlers = get_all_handlers()

        if name in handlers:
            try:
                result = handlers[name](arguments)
            except Exception as e:
                error_msg = f"Error executing {name}: {str(e)}"
                app_logger.error(error_msg)
                return [TextContent(type="text", text=error_msg)]
        else:
            error_msg = f"Unknown tool: {name}"
            app_logger.error(error_msg)
            return [TextContent(type="text", text=error_msg)]

        return [TextContent(type="text", text=result)]

    app_logger.info("Creating initialization options")
    options = server.create_initialization_options()

    app_logger.info("Starting stdio server")
    async with stdio_server() as (read_stream, write_stream):
        app_logger.info("Running MCP server")
        await server.run(read_stream, write_stream, options, raise_exceptions=True)
