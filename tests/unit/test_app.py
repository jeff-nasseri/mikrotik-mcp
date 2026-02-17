import asyncio
from unittest.mock import MagicMock


def test_health_check_returns_ok():
    from mcp_mikrotik.app import health_check

    resp = asyncio.run(health_check(MagicMock()))
    assert resp.body == b"OK"
    assert resp.media_type == "text/plain"

