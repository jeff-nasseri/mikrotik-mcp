import types

import pytest


def test_server_main_runs_mcp(monkeypatch):
    from mcp_mikrotik import server

    calls = {"run": 0}

    class FakeMcp:
        def __init__(self):
            self.settings = types.SimpleNamespace(host=None, port=None)

        def run(self, transport: str):
            calls["run"] += 1
            assert transport == "stdio"

    cfg = types.SimpleNamespace(
        host="10.0.0.1",
        username="admin",
        key_filename=None,
        mcp=types.SimpleNamespace(host="127.0.0.1", port=8123, transport="stdio"),
    )

    monkeypatch.setattr(server, "MikrotikConfig", lambda _cli_parse_args=True: cfg)
    monkeypatch.setattr(server, "mcp", FakeMcp())

    server.main()
    assert calls["run"] == 1
    assert server.mcp.settings.host == "127.0.0.1"
    assert server.mcp.settings.port == 8123


def test_server_main_exits_on_exception(monkeypatch):
    from mcp_mikrotik import server

    class FakeMcp:
        def __init__(self):
            self.settings = types.SimpleNamespace(host=None, port=None)

        def run(self, transport: str):
            raise RuntimeError("boom")

    cfg = types.SimpleNamespace(
        host="10.0.0.1",
        username="admin",
        key_filename=None,
        mcp=types.SimpleNamespace(host="127.0.0.1", port=8123, transport="stdio"),
    )

    monkeypatch.setattr(server, "MikrotikConfig", lambda _cli_parse_args=True: cfg)
    monkeypatch.setattr(server, "mcp", FakeMcp())

    def fake_exit(code: int):
        raise SystemExit(code)

    monkeypatch.setattr(server.sys, "exit", fake_exit)

    with pytest.raises(SystemExit) as exc:
        server.main()
    assert exc.value.code == 1


def test_server_main_handles_keyboard_interrupt(monkeypatch):
    from mcp_mikrotik import server

    class FakeMcp:
        def __init__(self):
            self.settings = types.SimpleNamespace(host=None, port=None)

        def run(self, transport: str):
            raise KeyboardInterrupt()

    cfg = types.SimpleNamespace(
        host="10.0.0.1",
        username="admin",
        key_filename=None,
        mcp=types.SimpleNamespace(host="127.0.0.1", port=8123, transport="stdio"),
    )

    monkeypatch.setattr(server, "MikrotikConfig", lambda _cli_parse_args=True: cfg)
    monkeypatch.setattr(server, "mcp", FakeMcp())

    server.main()

