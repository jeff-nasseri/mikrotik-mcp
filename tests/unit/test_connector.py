"""Connector tests for the inventory-backed (multi-device) execution path."""

import asyncio

import pytest

from mcp_mikrotik.config import DeviceConfig
from mcp_mikrotik.inventory import DeviceNotFoundError, Inventory


class DummyClient:
    """Stand-in for MikroTikSSHClient."""

    def __init__(self, output="identity", raises=None):
        self.output = output
        self.raises = raises
        self.commands = []
        self.uploaded = None
        self.downloaded = None

    def execute_command(self, command: str) -> str:
        self.commands.append(command)
        if self.raises:
            raise self.raises
        return self.output

    def download_file(self, filename: str) -> bytes:
        self.downloaded = filename
        return b"\x00binary"

    def upload_file(self, filename: str, data: bytes) -> None:
        self.uploaded = (filename, data)


class FakeInventory:
    """Minimal inventory double: resolves titles and hands back clients."""

    def __init__(self, clients: dict):
        self._clients = clients
        self._devices = {
            t.casefold(): DeviceConfig(title=t, host=f"10.0.0.{i + 1}")
            for i, t in enumerate(clients)
        }

    def resolve(self, title=None):
        if title is None:
            if len(self._devices) == 1:
                return next(iter(self._devices.values()))
            raise DeviceNotFoundError("multiple devices; specify one")
        dev = self._devices.get(str(title).casefold())
        if dev is None:
            raise DeviceNotFoundError(f"Unknown device {title!r}.")
        return dev

    def get_client(self, title=None):
        return self._clients[self.resolve(title).title]


def _patch_inventory(monkeypatch, inv):
    from mcp_mikrotik import connector

    monkeypatch.setattr(connector, "get_inventory", lambda: inv)
    return connector


# ---------------------------------------------------------------------------
# _execute_sync
# ---------------------------------------------------------------------------

def test_execute_sync_uses_single_device_when_unspecified(monkeypatch):
    client = DummyClient()
    connector = _patch_inventory(monkeypatch, FakeInventory({"OnlyOne": client}))

    assert connector._execute_sync("/system identity print") == "identity"
    assert client.commands == ["/system identity print"]


def test_execute_sync_routes_to_named_device(monkeypatch):
    a, b = DummyClient("from-A"), DummyClient("from-B")
    connector = _patch_inventory(monkeypatch, FakeInventory({"RouterA": a, "RouterB": b}))

    assert connector._execute_sync("/x", device="RouterB") == "from-B"
    assert b.commands == ["/x"] and a.commands == []


def test_execute_sync_unknown_device_raises(monkeypatch):
    connector = _patch_inventory(monkeypatch, FakeInventory({"RouterA": DummyClient()}))
    with pytest.raises(DeviceNotFoundError):
        connector._execute_sync("/x", device="Nope")


# ---------------------------------------------------------------------------
# file transfer
# ---------------------------------------------------------------------------

def test_download_file_sync_targets_device(monkeypatch):
    a, b = DummyClient(), DummyClient()
    connector = _patch_inventory(monkeypatch, FakeInventory({"RouterA": a, "RouterB": b}))

    assert connector.download_file_sync("backup_1.backup", device="RouterB") == b"\x00binary"
    assert b.downloaded == "backup_1.backup"
    assert a.downloaded is None


def test_upload_file_sync_targets_device(monkeypatch):
    a, b = DummyClient(), DummyClient()
    connector = _patch_inventory(monkeypatch, FakeInventory({"RouterA": a, "RouterB": b}))

    connector.upload_file_sync("restore.rsc", b"config-bytes", device="RouterA")
    assert a.uploaded == ("restore.rsc", b"config-bytes")
    assert b.uploaded is None


# ---------------------------------------------------------------------------
# execute_mikrotik_command
# ---------------------------------------------------------------------------

def test_execute_mikrotik_command_logs_error(ctx, monkeypatch):
    connector = _patch_inventory(monkeypatch, FakeInventory({"OnlyOne": DummyClient()}))

    async def fake_to_thread(fn, *args, **kwargs):
        return fn(*args, **kwargs)

    monkeypatch.setattr(asyncio, "to_thread", fake_to_thread)
    monkeypatch.setattr(connector, "_execute_sync", lambda cmd, device=None: "Error: nope")

    result = asyncio.run(connector.execute_mikrotik_command("/bad", ctx))
    assert result == "Error: nope"
    assert ctx.error.await_count == 1


def test_execute_mikrotik_command_unknown_device_is_reported(ctx, monkeypatch):
    """A bad device must fail loudly and never execute somewhere else."""
    client = DummyClient()
    connector = _patch_inventory(monkeypatch, FakeInventory({"RouterA": client}))

    result = asyncio.run(connector.execute_mikrotik_command("/x", ctx, device="Ghost"))
    assert "Unknown device" in result
    assert client.commands == []          # nothing ran anywhere
    assert ctx.error.await_count == 1


def test_execute_mikrotik_command_passes_resolved_device(ctx, monkeypatch):
    a, b = DummyClient("A-out"), DummyClient("B-out")
    connector = _patch_inventory(monkeypatch, FakeInventory({"RouterA": a, "RouterB": b}))

    async def fake_to_thread(fn, *args, **kwargs):
        return fn(*args, **kwargs)

    monkeypatch.setattr(asyncio, "to_thread", fake_to_thread)

    result = asyncio.run(connector.execute_mikrotik_command("/y", ctx, device="RouterB"))
    assert result == "B-out"
    assert b.commands == ["/y"] and a.commands == []
