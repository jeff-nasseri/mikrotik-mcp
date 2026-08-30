import asyncio
from unittest.mock import MagicMock


def test_health_check_returns_ok():
    from mcp_mikrotik.app import health_check

    resp = asyncio.run(health_check(MagicMock()))
    assert resp.body == b"OK"
    assert resp.media_type == "text/plain"


def test_device_guidance_lives_in_server_instructions_not_every_tool():
    """The `device` argument is explained once, at initialize.

    Repeating it in each tool description put the same sentence in front of
    the model ~182 times, for no extra information.
    """
    from mcp_mikrotik.app import mcp

    instructions = mcp.instructions or ""
    assert "device" in instructions
    assert "list_devices" in instructions

    tools = asyncio.run(mcp.list_tools())
    repeated = [
        t.name for t in tools
        if "title of the target device" in (t.description or "")
        or "Device title from the inventory" in (t.description or "")
    ]
    assert repeated == [], f"device guidance duplicated into tool descriptions: {repeated}"


def test_every_tool_still_accepts_a_device_argument():
    """Dropping the prose must not drop the parameter."""
    from mcp_mikrotik.app import mcp

    tools = asyncio.run(mcp.list_tools())
    missing = [
        t.name for t in tools
        if t.name != "list_devices"
        and "device" not in (t.input_schema.get("properties") or {})
    ]
    assert missing == []


def test_read_only_server_registers_only_read_tools(monkeypatch):
    from mcp_mikrotik import config
    from mcp_mikrotik.app import ConfiguredMCPServer, READ, WRITE, annotate
    from mcp_mikrotik.config import MikrotikConfig

    monkeypatch.setattr(config, "mikrotik_config", MikrotikConfig(read_only=True))
    server = ConfiguredMCPServer("read-only-test")

    @server.tool(name="read", annotations=annotate(READ, "Read"))
    async def read_tool() -> str:
        return "read"

    @server.tool(name="write", annotations=annotate(WRITE, "Write"))
    async def write_tool() -> str:
        return "write"

    tools = asyncio.run(server.list_tools())
    assert [tool.name for tool in tools] == ["read"]
    assert tools[0].annotations.title == "Read"
    assert tools[0].annotations.read_only_hint is True


def test_file_creating_tools_are_not_marked_read_only():
    from mcp_mikrotik.app import mcp

    tools = {tool.name: tool for tool in asyncio.run(mcp.list_tools())}
    assert tools["create_export"].annotations.read_only_hint is not True
    assert tools["export_logs"].annotations.read_only_hint is not True
