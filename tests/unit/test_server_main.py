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


def test_credential_warning_emitted_in_container_with_password(monkeypatch):
    """Warning fires when a plaintext password is set inside a container."""
    from mcp_mikrotik.server import _warn_if_plaintext_password_in_container
    import logging, io, types

    monkeypatch.setattr("os.path.exists", lambda p: p == "/.dockerenv")

    cfg = types.SimpleNamespace(password="secret", key_filename=None)
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    logger = logging.getLogger("test_warn")
    logger.addHandler(handler)
    logger.setLevel(logging.WARNING)
    _warn_if_plaintext_password_in_container(cfg, logger)
    logger.removeHandler(handler)
    assert "plaintext password" in stream.getvalue()


def test_credential_warning_suppressed_with_key(monkeypatch):
    """No warning when SSH key is configured (password exposure isn't an issue)."""
    from mcp_mikrotik.server import _warn_if_plaintext_password_in_container
    import logging, io, types

    monkeypatch.setattr("os.path.exists", lambda p: p == "/.dockerenv")

    cfg = types.SimpleNamespace(password="secret", key_filename="/keys/id_ed25519")
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    logger = logging.getLogger("test_warn_key")
    logger.addHandler(handler)
    logger.setLevel(logging.WARNING)
    _warn_if_plaintext_password_in_container(cfg, logger)
    logger.removeHandler(handler)
    assert stream.getvalue() == ""


def test_credential_warning_suppressed_outside_container(monkeypatch):
    """No warning when not running inside a container."""
    from mcp_mikrotik.server import _warn_if_plaintext_password_in_container
    import logging, io, types

    monkeypatch.setattr("os.path.exists", lambda p: False)
    monkeypatch.delenv("container", raising=False)

    cfg = types.SimpleNamespace(password="secret", key_filename=None)
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    logger = logging.getLogger("test_warn_nocontainer")
    logger.addHandler(handler)
    logger.setLevel(logging.WARNING)
    _warn_if_plaintext_password_in_container(cfg, logger)
    logger.removeHandler(handler)
    assert stream.getvalue() == ""


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

