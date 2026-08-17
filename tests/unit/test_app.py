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

