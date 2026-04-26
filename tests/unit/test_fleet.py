"""Unit tests for mcp_mikrotik.scope.fleet."""

import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from mcp_mikrotik.config import DeviceConfig
from mcp_mikrotik.inventory import DeviceInventory, reset_inventory
import mcp_mikrotik.scope.fleet as fleet_module


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def ctx():
    c = MagicMock()
    c.info = AsyncMock()
    c.error = AsyncMock()
    return c


def _sample_devices():
    return [
        DeviceConfig(name="mt-nl-1", host="1.1.1.1", tags=["nl", "eu", "core"]),
        DeviceConfig(name="mt-usa-1", host="2.2.2.1", tags=["usa", "core"]),
        DeviceConfig(name="mt-uae-1", host="3.3.3.1", tags=["uae"]),
    ]


@pytest.fixture(autouse=True)
def _reset_inventory():
    reset_inventory()
    yield
    reset_inventory()


# ---------------------------------------------------------------------------
# list_devices
# ---------------------------------------------------------------------------

class TestListDevices:
    def test_returns_json_with_devices(self, ctx, monkeypatch):
        inv = DeviceInventory(_sample_devices())
        monkeypatch.setattr(fleet_module, "get_inventory", lambda: inv)

        result = asyncio.run(fleet_module.mikrotik_list_devices(ctx))

        data = json.loads(result)
        assert isinstance(data, list)
        assert len(data) == 3
        names = {d["name"] for d in data}
        assert names == {"mt-nl-1", "mt-usa-1", "mt-uae-1"}

    def test_device_summary_fields(self, ctx, monkeypatch):
        inv = DeviceInventory(_sample_devices())
        monkeypatch.setattr(fleet_module, "get_inventory", lambda: inv)

        result = asyncio.run(fleet_module.mikrotik_list_devices(ctx))
        data = json.loads(result)
        entry = next(d for d in data if d["name"] == "mt-nl-1")

        assert entry["host"] == "1.1.1.1"
        assert entry["port"] == 22
        assert "nl" in entry["tags"]

    def test_empty_inventory_returns_help_text(self, ctx, monkeypatch):
        inv = DeviceInventory([])
        monkeypatch.setattr(fleet_module, "get_inventory", lambda: inv)

        result = asyncio.run(fleet_module.mikrotik_list_devices(ctx))
        assert "MIKROTIK_DEVICES" in result

    def test_returns_str(self, ctx, monkeypatch):
        inv = DeviceInventory(_sample_devices())
        monkeypatch.setattr(fleet_module, "get_inventory", lambda: inv)
        assert isinstance(asyncio.run(fleet_module.mikrotik_list_devices(ctx)), str)


# ---------------------------------------------------------------------------
# run_command_on_device
# ---------------------------------------------------------------------------

class TestRunCommandOnDevice:
    def test_success(self, ctx, monkeypatch):
        inv = DeviceInventory(_sample_devices())
        monkeypatch.setattr(fleet_module, "get_inventory", lambda: inv)

        async def fake_exec(device, command, ctx):
            return "ether1  1.1.1.1/24  running"

        monkeypatch.setattr(fleet_module, "execute_command_on_device", fake_exec)

        result = asyncio.run(
            fleet_module.mikrotik_run_command_on_device(ctx, "mt-nl-1", "/ip address print")
        )
        assert "mt-nl-1" in result
        assert "ether1" in result

    def test_device_not_found(self, ctx, monkeypatch):
        inv = DeviceInventory(_sample_devices())
        monkeypatch.setattr(fleet_module, "get_inventory", lambda: inv)

        result = asyncio.run(
            fleet_module.mikrotik_run_command_on_device(ctx, "ghost-router", "/ip address print")
        )
        assert "not found" in result.lower()
        assert "ghost-router" in result

    def test_device_not_found_lists_available(self, ctx, monkeypatch):
        inv = DeviceInventory(_sample_devices())
        monkeypatch.setattr(fleet_module, "get_inventory", lambda: inv)

        result = asyncio.run(
            fleet_module.mikrotik_run_command_on_device(ctx, "nope", "/ip address print")
        )
        assert "mt-nl-1" in result or "Available" in result

    def test_returns_str(self, ctx, monkeypatch):
        inv = DeviceInventory(_sample_devices())
        monkeypatch.setattr(fleet_module, "get_inventory", lambda: inv)

        async def fake_exec(device, command, ctx):
            return "ok"

        monkeypatch.setattr(fleet_module, "execute_command_on_device", fake_exec)

        result = asyncio.run(
            fleet_module.mikrotik_run_command_on_device(ctx, "mt-nl-1", "/system resource print")
        )
        assert isinstance(result, str)


# ---------------------------------------------------------------------------
# run_command_on_tag
# ---------------------------------------------------------------------------

class TestRunCommandOnTag:
    def test_parallel_execution(self, ctx, monkeypatch):
        inv = DeviceInventory(_sample_devices())
        monkeypatch.setattr(fleet_module, "get_inventory", lambda: inv)

        async def fake_exec(device, command, ctx):
            return f"output-from-{device.name}"

        monkeypatch.setattr(fleet_module, "execute_command_on_device", fake_exec)

        result = asyncio.run(
            fleet_module.mikrotik_run_command_on_tag(ctx, "core", "/system resource print")
        )
        data = json.loads(result)
        assert "mt-nl-1" in data
        assert "mt-usa-1" in data
        assert "output-from-mt-nl-1" in data["mt-nl-1"]

    def test_tag_not_found(self, ctx, monkeypatch):
        inv = DeviceInventory(_sample_devices())
        monkeypatch.setattr(fleet_module, "get_inventory", lambda: inv)

        result = asyncio.run(
            fleet_module.mikrotik_run_command_on_tag(ctx, "nonexistent", "/ip address print")
        )
        assert "not found" in result.lower() or "No devices" in result

    def test_exception_is_captured(self, ctx, monkeypatch):
        inv = DeviceInventory(_sample_devices())
        monkeypatch.setattr(fleet_module, "get_inventory", lambda: inv)

        async def fail(device, command, ctx):
            if device.name == "mt-usa-1":
                raise ConnectionError("timeout")
            return "ok"

        monkeypatch.setattr(fleet_module, "execute_command_on_device", fail)

        result = asyncio.run(
            fleet_module.mikrotik_run_command_on_tag(ctx, "core", "/system resource print")
        )
        data = json.loads(result)
        assert "Error" in data["mt-usa-1"]
        assert data["mt-nl-1"] == "ok"

    def test_returns_json_str(self, ctx, monkeypatch):
        inv = DeviceInventory(_sample_devices())
        monkeypatch.setattr(fleet_module, "get_inventory", lambda: inv)

        async def fake_exec(device, command, ctx):
            return "ok"

        monkeypatch.setattr(fleet_module, "execute_command_on_device", fake_exec)

        result = asyncio.run(
            fleet_module.mikrotik_run_command_on_tag(ctx, "nl", "/ip address print")
        )
        assert isinstance(result, str)
        json.loads(result)  # must be valid JSON


# ---------------------------------------------------------------------------
# run_command_on_all_devices
# ---------------------------------------------------------------------------

class TestRunCommandOnAllDevices:
    def test_all_devices(self, ctx, monkeypatch):
        inv = DeviceInventory(_sample_devices())
        monkeypatch.setattr(fleet_module, "get_inventory", lambda: inv)

        async def fake_exec(device, command, ctx):
            return "ok"

        monkeypatch.setattr(fleet_module, "execute_command_on_device", fake_exec)

        result = asyncio.run(
            fleet_module.mikrotik_run_command_on_all_devices(ctx, "/system resource print")
        )
        data = json.loads(result)
        assert set(data.keys()) == {"mt-nl-1", "mt-usa-1", "mt-uae-1"}

    def test_with_tag_filter(self, ctx, monkeypatch):
        inv = DeviceInventory(_sample_devices())
        monkeypatch.setattr(fleet_module, "get_inventory", lambda: inv)

        async def fake_exec(device, command, ctx):
            return "ok"

        monkeypatch.setattr(fleet_module, "execute_command_on_device", fake_exec)

        result = asyncio.run(
            fleet_module.mikrotik_run_command_on_all_devices(
                ctx, "/system resource print", tag_filter="eu"
            )
        )
        data = json.loads(result)
        assert set(data.keys()) == {"mt-nl-1"}

    def test_empty_inventory(self, ctx, monkeypatch):
        inv = DeviceInventory([])
        monkeypatch.setattr(fleet_module, "get_inventory", lambda: inv)

        result = asyncio.run(
            fleet_module.mikrotik_run_command_on_all_devices(ctx, "/ip address print")
        )
        assert isinstance(result, str)
        assert "No devices" in result

    def test_tag_filter_no_match(self, ctx, monkeypatch):
        inv = DeviceInventory(_sample_devices())
        monkeypatch.setattr(fleet_module, "get_inventory", lambda: inv)

        result = asyncio.run(
            fleet_module.mikrotik_run_command_on_all_devices(
                ctx, "/ip address print", tag_filter="unknown-tag"
            )
        )
        assert "not found" in result.lower() or "No devices" in result

    def test_returns_json_str(self, ctx, monkeypatch):
        inv = DeviceInventory(_sample_devices())
        monkeypatch.setattr(fleet_module, "get_inventory", lambda: inv)

        async def fake_exec(device, command, ctx):
            return "data"

        monkeypatch.setattr(fleet_module, "execute_command_on_device", fake_exec)

        result = asyncio.run(
            fleet_module.mikrotik_run_command_on_all_devices(ctx, "/ip address print")
        )
        assert isinstance(result, str)
        json.loads(result)  # must be valid JSON
