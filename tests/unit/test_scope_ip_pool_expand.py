import asyncio

import pytest


def test_expand_ip_pool_hits_wrapper_bug(ctx, monkeypatch):
    """
    Current implementation calls mikrotik_update_ip_pool with `name` as the first positional argument
    even though `ctx` is the first parameter, then also passes `ctx=...`, which raises TypeError.
    """
    from mcp_mikrotik.scope import ip_pool as mod

    async def fake_exec(command: str, _ctx):
        if "print detail" in command:
            return 'name="pool1" ranges=10.0.0.1-10.0.0.10'
        return ""

    monkeypatch.setattr(mod, "execute_mikrotik_command", fake_exec, raising=True)

    with pytest.raises(TypeError):
        asyncio.run(mod.mikrotik_expand_ip_pool(ctx=ctx, name="pool1", additional_ranges="10.0.0.11-10.0.0.12"))

