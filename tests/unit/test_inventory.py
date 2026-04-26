"""Unit tests for mcp_mikrotik.inventory."""

import pytest

from mcp_mikrotik.config import DeviceConfig
from mcp_mikrotik.inventory import DeviceInventory, get_inventory, reset_inventory


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_devices():
    return [
        DeviceConfig(name="mt-nl-1", host="1.1.1.1", tags=["nl", "eu", "core"]),
        DeviceConfig(name="mt-nl-2", host="1.1.1.2", tags=["nl", "eu"]),
        DeviceConfig(name="mt-usa-1", host="2.2.2.1", tags=["usa", "core"]),
        DeviceConfig(name="mt-uae-1", host="3.3.3.1", tags=["uae"]),
    ]


# ---------------------------------------------------------------------------
# DeviceInventory
# ---------------------------------------------------------------------------

class TestDeviceInventory:
    def test_count(self):
        inv = DeviceInventory(_make_devices())
        assert inv.count() == 4

    def test_get_device_found(self):
        inv = DeviceInventory(_make_devices())
        device = inv.get_device("mt-nl-1")
        assert device is not None
        assert device.host == "1.1.1.1"

    def test_get_device_not_found(self):
        inv = DeviceInventory(_make_devices())
        assert inv.get_device("nonexistent") is None

    def test_get_devices_by_tag_single_match(self):
        inv = DeviceInventory(_make_devices())
        devices = inv.get_devices_by_tag("uae")
        assert len(devices) == 1
        assert devices[0].name == "mt-uae-1"

    def test_get_devices_by_tag_multiple_matches(self):
        inv = DeviceInventory(_make_devices())
        devices = inv.get_devices_by_tag("nl")
        names = {d.name for d in devices}
        assert names == {"mt-nl-1", "mt-nl-2"}

    def test_get_devices_by_tag_cross_region(self):
        inv = DeviceInventory(_make_devices())
        core_devices = inv.get_devices_by_tag("core")
        names = {d.name for d in core_devices}
        assert names == {"mt-nl-1", "mt-usa-1"}

    def test_get_devices_by_tag_no_match(self):
        inv = DeviceInventory(_make_devices())
        assert inv.get_devices_by_tag("nonexistent-tag") == []

    def test_get_all_devices_returns_all(self):
        inv = DeviceInventory(_make_devices())
        all_devices = inv.get_all_devices()
        assert len(all_devices) == 4

    def test_list_names(self):
        inv = DeviceInventory(_make_devices())
        names = set(inv.list_names())
        assert names == {"mt-nl-1", "mt-nl-2", "mt-usa-1", "mt-uae-1"}

    def test_empty_inventory(self):
        inv = DeviceInventory([])
        assert inv.count() == 0
        assert inv.get_all_devices() == []
        assert inv.get_device("any") is None
        assert inv.get_devices_by_tag("any") == []

    def test_device_defaults(self):
        inv = DeviceInventory([DeviceConfig(name="basic", host="10.0.0.1")])
        device = inv.get_device("basic")
        assert device.username == "admin"
        assert device.password == ""
        assert device.port == 22
        assert device.key_filename is None
        assert device.tags == []


# ---------------------------------------------------------------------------
# Singleton helpers
# ---------------------------------------------------------------------------

class TestGetInventorySingleton:
    def setup_method(self):
        reset_inventory()

    def teardown_method(self):
        reset_inventory()

    def test_returns_same_instance(self, monkeypatch):
        monkeypatch.setattr(
            "mcp_mikrotik.inventory.mikrotik_config",
            type("cfg", (), {"devices": _make_devices()})(),
        )
        inv1 = get_inventory()
        inv2 = get_inventory()
        assert inv1 is inv2

    def test_loads_from_config(self, monkeypatch):
        monkeypatch.setattr(
            "mcp_mikrotik.inventory.mikrotik_config",
            type("cfg", (), {"devices": _make_devices()})(),
        )
        inv = get_inventory()
        assert inv.count() == 4

    def test_empty_config(self, monkeypatch):
        monkeypatch.setattr(
            "mcp_mikrotik.inventory.mikrotik_config",
            type("cfg", (), {"devices": []})(),
        )
        inv = get_inventory()
        assert inv.count() == 0
