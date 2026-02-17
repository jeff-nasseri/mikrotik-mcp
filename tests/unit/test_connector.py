import asyncio


def test_execute_sync_success(monkeypatch):
    from mcp_mikrotik import connector

    disconnected = {"called": 0}

    class DummyClient:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

        def connect(self):
            return True

        def execute_command(self, command: str) -> str:
            assert command == "/system identity print"
            return "identity"

        def disconnect(self):
            disconnected["called"] += 1

    monkeypatch.setattr(connector, "MikroTikSSHClient", lambda **kw: DummyClient(**kw))
    result = connector._execute_sync("/system identity print")
    assert result == "identity"
    assert disconnected["called"] == 1


def test_execute_sync_connect_failure(monkeypatch):
    from mcp_mikrotik import connector

    disconnected = {"called": 0}

    class DummyClient:
        def connect(self):
            return False

        def disconnect(self):
            disconnected["called"] += 1

    monkeypatch.setattr(connector, "MikroTikSSHClient", lambda **kw: DummyClient())
    result = connector._execute_sync("/system identity print")
    assert result.startswith("Error: Failed to connect")
    assert disconnected["called"] == 1


def test_execute_sync_exception(monkeypatch):
    from mcp_mikrotik import connector

    disconnected = {"called": 0}

    class DummyClient:
        def connect(self):
            return True

        def execute_command(self, command: str) -> str:
            raise RuntimeError("boom")

        def disconnect(self):
            disconnected["called"] += 1

    monkeypatch.setattr(connector, "MikroTikSSHClient", lambda **kw: DummyClient())
    result = connector._execute_sync("/system identity print")
    assert result.startswith("Error executing command: boom")
    assert disconnected["called"] == 1


def test_execute_mikrotik_command_logs_error(ctx, monkeypatch):
    from mcp_mikrotik import connector

    async def fake_to_thread(fn, *args, **kwargs):
        return fn(*args, **kwargs)

    monkeypatch.setattr(asyncio, "to_thread", fake_to_thread)
    monkeypatch.setattr(connector, "_execute_sync", lambda cmd: "Error: nope")

    result = asyncio.run(connector.execute_mikrotik_command("/bad", ctx))
    assert result == "Error: nope"
    assert ctx.error.await_count == 1

