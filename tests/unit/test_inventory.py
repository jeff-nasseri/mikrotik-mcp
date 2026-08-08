"""Tests for the multi-device Inventory (issue #44)."""

import json

import pytest

from mcp_mikrotik.config import DeviceConfig, MikrotikConfig
from mcp_mikrotik.inventory import DeviceNotFoundError, Inventory


def _dev(title, host="10.0.0.1", **kw):
    return DeviceConfig(title=title, host=host, **kw)


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------

def test_titles_and_len():
    inv = Inventory([_dev("RouterA"), _dev("RouterB", "10.0.0.2")])
    assert len(inv) == 2
    assert inv.titles == ["RouterA", "RouterB"]


def test_duplicate_titles_rejected():
    with pytest.raises(ValueError, match="Duplicate device title"):
        Inventory([_dev("Same"), _dev("Same", "10.0.0.2")])


def test_duplicate_titles_are_case_insensitive():
    with pytest.raises(ValueError, match="Duplicate device title"):
        Inventory([_dev("RouterA"), _dev("routera", "10.0.0.2")])


def test_blank_title_rejected():
    with pytest.raises(ValueError):
        DeviceConfig(title="   ", host="10.0.0.1")


# ---------------------------------------------------------------------------
# Resolution
# ---------------------------------------------------------------------------

def test_single_device_resolves_without_a_title():
    inv = Inventory([_dev("OnlyOne")])
    assert inv.resolve().title == "OnlyOne"
    assert inv.resolve(None).title == "OnlyOne"
    assert inv.resolve("").title == "OnlyOne"


def test_multiple_devices_require_a_title():
    inv = Inventory([_dev("RouterA"), _dev("RouterB", "10.0.0.2")])
    with pytest.raises(DeviceNotFoundError) as exc:
        inv.resolve()
    # The error must list the choices so the caller can self-correct.
    assert "RouterA" in str(exc.value) and "RouterB" in str(exc.value)


def test_resolve_is_case_insensitive_and_trims():
    inv = Inventory([_dev("RouterA"), _dev("RouterB", "10.0.0.2")])
    assert inv.resolve("routera").title == "RouterA"
    assert inv.resolve("  RouterB  ").title == "RouterB"


def test_unknown_title_lists_available_devices():
    inv = Inventory([_dev("RouterA"), _dev("RouterB", "10.0.0.2")])
    with pytest.raises(DeviceNotFoundError) as exc:
        inv.resolve("Ghost")
    msg = str(exc.value)
    assert "Ghost" in msg and "RouterA" in msg and "RouterB" in msg


def test_empty_inventory_resolution_error():
    with pytest.raises(DeviceNotFoundError, match="No MikroTik devices"):
        Inventory([]).resolve()


# ---------------------------------------------------------------------------
# describe() — what the LLM sees
# ---------------------------------------------------------------------------

def test_describe_never_exposes_credentials():
    inv = Inventory([
        _dev("RouterA", username="admin", password="super-secret",
             key_filename="/keys/id_ed25519", tags=["eu"], region="NL")
    ])
    described = inv.describe()
    blob = json.dumps(described)
    assert "super-secret" not in blob
    assert "id_ed25519" not in blob
    assert "password" not in blob and "key_filename" not in blob
    assert described[0]["title"] == "RouterA"
    assert described[0]["tags"] == ["eu"] and described[0]["region"] == "NL"


# ---------------------------------------------------------------------------
# Client handling
# ---------------------------------------------------------------------------

def test_get_client_is_cached_per_device(monkeypatch):
    import mcp_mikrotik.inventory as inv_mod

    built = []

    class FakeSSH:
        def __init__(self, **kw):
            built.append(kw["host"])
            self.client = object()

        def connect(self):
            return True

        def disconnect(self):
            pass

    monkeypatch.setattr(inv_mod, "MikroTikSSHClient", FakeSSH)
    monkeypatch.setattr(Inventory, "_is_alive", staticmethod(lambda c: True))

    inv = Inventory([_dev("RouterA", "10.0.0.1"), _dev("RouterB", "10.0.0.2")])
    c1 = inv.get_client("RouterA")
    c2 = inv.get_client("RouterA")
    c3 = inv.get_client("RouterB")

    assert c1 is c2                 # reused
    assert c3 is not c1             # per-device
    assert built == ["10.0.0.1", "10.0.0.2"]


def test_get_client_rebuilds_a_dead_connection(monkeypatch):
    import mcp_mikrotik.inventory as inv_mod

    built = []

    class FakeSSH:
        def __init__(self, **kw):
            built.append(kw["host"])
            self.client = object()

        def connect(self):
            return True

        def disconnect(self):
            pass

    monkeypatch.setattr(inv_mod, "MikroTikSSHClient", FakeSSH)
    monkeypatch.setattr(Inventory, "_is_alive", staticmethod(lambda c: False))

    inv = Inventory([_dev("RouterA", "10.0.0.1")])
    inv.get_client("RouterA")
    inv.get_client("RouterA")
    assert built == ["10.0.0.1", "10.0.0.1"]   # stale client replaced


def test_get_client_raises_on_connect_failure(monkeypatch):
    import mcp_mikrotik.inventory as inv_mod

    class FailingSSH:
        def __init__(self, **kw):
            self.client = None

        def connect(self):
            return False

        def disconnect(self):
            pass

    monkeypatch.setattr(inv_mod, "MikroTikSSHClient", FailingSSH)
    inv = Inventory([_dev("RouterA", "10.0.0.1")])
    with pytest.raises(ConnectionError, match="RouterA"):
        inv.get_client("RouterA")


# ---------------------------------------------------------------------------
# Loading from configuration
# ---------------------------------------------------------------------------

def test_inventory_parses_json_from_env(monkeypatch):
    payload = json.dumps([
        {"title": "TitleA", "host": "127.0.0.1", "port": 2222,
         "username": "admin", "password": "pw", "tags": ["t1"], "region": "NL"},
        {"title": "TitleB", "host": "192.168.88.1"},
    ])
    monkeypatch.setenv("MIKROTIK_INVENTORY", payload)
    cfg = MikrotikConfig()
    assert [d.title for d in cfg.inventory] == ["TitleA", "TitleB"]
    assert cfg.inventory[0].port == 2222
    assert cfg.inventory[0].tags == ["t1"]
    assert cfg.inventory[1].port == 22          # default


def test_invalid_inventory_json_is_rejected(monkeypatch):
    monkeypatch.setenv("MIKROTIK_INVENTORY", "{not json")
    with pytest.raises(Exception):
        MikrotikConfig()


def test_falls_back_to_single_device_config(monkeypatch):
    """No inventory configured -> synthesise one device from the flat settings."""
    import mcp_mikrotik.inventory as inv_mod
    from mcp_mikrotik import config as cfg_mod

    monkeypatch.delenv("MIKROTIK_INVENTORY", raising=False)
    monkeypatch.setattr(
        cfg_mod, "mikrotik_config",
        MikrotikConfig(host="192.168.88.1", username="u", password="p", port=2022),
    )

    devices = inv_mod._load_devices()
    assert len(devices) == 1
    assert devices[0].host == "192.168.88.1"
    assert devices[0].port == 2022
    assert devices[0].username == "u"
