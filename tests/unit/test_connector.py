import asyncio

import pytest


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


def test_download_file_sync_success(monkeypatch):
    from mcp_mikrotik import connector

    disconnected = {"called": 0}

    class DummyClient:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

        def connect(self):
            return True

        def download_file(self, filename: str) -> bytes:
            assert filename == "backup_1.backup"
            return b"\x00binary"

        def disconnect(self):
            disconnected["called"] += 1

    monkeypatch.setattr(connector, "MikroTikSSHClient", lambda **kw: DummyClient(**kw))
    assert connector.download_file_sync("backup_1.backup") == b"\x00binary"
    assert disconnected["called"] == 1


def test_download_file_sync_connect_failure(monkeypatch):
    from mcp_mikrotik import connector

    disconnected = {"called": 0}

    class DummyClient:
        def connect(self):
            return False

        def disconnect(self):
            disconnected["called"] += 1

    monkeypatch.setattr(connector, "MikroTikSSHClient", lambda **kw: DummyClient())
    with pytest.raises(ConnectionError):
        connector.download_file_sync("x.backup")
    assert disconnected["called"] == 1


def test_upload_file_sync_success(monkeypatch):
    from mcp_mikrotik import connector

    captured = {}
    disconnected = {"called": 0}

    class DummyClient:
        def connect(self):
            return True

        def upload_file(self, filename: str, data: bytes) -> None:
            captured["filename"] = filename
            captured["data"] = data

        def disconnect(self):
            disconnected["called"] += 1

    monkeypatch.setattr(connector, "MikroTikSSHClient", lambda **kw: DummyClient())
    connector.upload_file_sync("restore.rsc", b"config-bytes")
    assert captured == {"filename": "restore.rsc", "data": b"config-bytes"}
    assert disconnected["called"] == 1


def test_upload_file_sync_connect_failure(monkeypatch):
    from mcp_mikrotik import connector

    disconnected = {"called": 0}

    class DummyClient:
        def connect(self):
            return False

        def disconnect(self):
            disconnected["called"] += 1

    monkeypatch.setattr(connector, "MikroTikSSHClient", lambda **kw: DummyClient())
    with pytest.raises(ConnectionError):
        connector.upload_file_sync("x.rsc", b"data")
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

