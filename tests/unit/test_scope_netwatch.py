import asyncio

from tests.conftest import FakeExecutor


def _run(coro):
    return asyncio.run(coro)


class DetailFake(FakeExecutor):
    async def __call__(self, command, _ctx, device=None):
        result = await super().__call__(command, _ctx, device)
        return "host=192.0.2.1 status=up " + result if "print" in command.lower() else result


class LegendOnlyFake(FakeExecutor):
    """A no-match `print detail` still returns the Flags legend."""

    async def __call__(self, command, _ctx, device=None):
        await super().__call__(command, _ctx, device)
        return "Flags: X - DISABLED\n"


def test_command_filters_and_device(ctx, monkeypatch):
    from mcp_mikrotik.scope import netwatch

    fake = DetailFake()
    monkeypatch.setattr(netwatch, "execute_mikrotik_command", fake, raising=True)

    out = _run(netwatch.mikrotik_list_netwatch(ctx, device="edge"))
    assert fake.commands == ["/tool netwatch print detail"]
    assert fake.devices == ["edge"]
    assert out.startswith("NETWATCH PROBES:")

    _run(netwatch.mikrotik_list_netwatch(
        ctx, host_filter="1.1.1.1", comment_filter="Internet",
        status_filter="down", type_filter="simple",
    ))
    assert fake.commands[-1] == (
        '/tool netwatch print detail where host~"1.1.1.1" comment~"Internet" '
        'status="down" type="simple"'
    )


def test_no_match_is_not_the_legend(ctx, monkeypatch):
    from mcp_mikrotik.scope import netwatch

    monkeypatch.setattr(netwatch, "execute_mikrotik_command", LegendOnlyFake(), raising=True)
    out = _run(netwatch.mikrotik_list_netwatch(ctx, status_filter="down"))
    assert out == "No netwatch probes found matching the criteria."
