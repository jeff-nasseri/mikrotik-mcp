import io

import pytest


def test_ssh_client_requires_connect_for_execute():
    from mcp_mikrotik.mikrotik_ssh_client import MikroTikSSHClient

    client = MikroTikSSHClient(host="h", username="u", password="p", key_filename=None, port=22)
    with pytest.raises(Exception, match="Not connected"):
        client.execute_command("/system identity print")


def test_ssh_client_connect_and_execute(monkeypatch):
    from mcp_mikrotik.mikrotik_ssh_client import MikroTikSSHClient
    import mcp_mikrotik.mikrotik_ssh_client as mod

    state = {"connect_kwargs": None, "closed": 0}

    class DummySSH:
        def set_missing_host_key_policy(self, _policy):
            pass

        def connect(self, **kwargs):
            state["connect_kwargs"] = kwargs

        def exec_command(self, command: str):
            assert command == "/system identity print"
            return (None, io.BytesIO(b"out"), io.BytesIO(b""))

        def close(self):
            state["closed"] += 1

    monkeypatch.setattr(mod.paramiko, "SSHClient", lambda: DummySSH())

    client = MikroTikSSHClient(host="h", username="u", password="p", key_filename="k", port=2222)
    assert client.connect() is True
    assert state["connect_kwargs"]["hostname"] == "h"
    assert state["connect_kwargs"]["port"] == 2222
    assert state["connect_kwargs"]["username"] == "u"
    assert state["connect_kwargs"]["password"] == "p"
    assert state["connect_kwargs"]["key_filename"] == "k"

    assert client.execute_command("/system identity print") == "out"
    client.disconnect()
    assert state["closed"] == 1


def test_ssh_client_returns_stderr_when_no_stdout(monkeypatch):
    from mcp_mikrotik.mikrotik_ssh_client import MikroTikSSHClient
    import mcp_mikrotik.mikrotik_ssh_client as mod

    class DummySSH:
        def set_missing_host_key_policy(self, _policy):
            pass

        def connect(self, **kwargs):
            pass

        def exec_command(self, command: str):
            return (None, io.BytesIO(b""), io.BytesIO(b"failure: nope"))

        def close(self):
            pass

    monkeypatch.setattr(mod.paramiko, "SSHClient", lambda: DummySSH())

    client = MikroTikSSHClient(host="h", username="u", password="p", key_filename=None, port=22)
    assert client.connect() is True
    assert client.execute_command("/x") == "failure: nope"

