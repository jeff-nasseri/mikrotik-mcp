"""Device inventory for multi-device (fleet) support — issue #44.

The :class:`Inventory` owns the list of MikroTik devices and the
``MikroTikSSHClient`` used to reach each one.  Tools pass a device ``title``
down to the connector, which asks the inventory to resolve it to the matching
client and runs the command over that client's SSH channel.

Clients are created lazily (on first use for a device) rather than eagerly at
start-up, so an unreachable device cannot block server start-up or wedge the
whole inventory.
"""

import json
import logging
import os
import threading
from typing import Dict, List, Optional

from . import config
from .config import DeviceConfig
from .mikrotik_ssh_client import MikroTikSSHClient

logger = logging.getLogger(__name__)


class DeviceNotFoundError(LookupError):
    """Raised when a requested device title cannot be resolved."""


class Inventory:
    """Holds device definitions and their SSH clients, keyed by title."""

    def __init__(self, devices: List[DeviceConfig]) -> None:
        self._devices: Dict[str, DeviceConfig] = {}
        self._clients: Dict[str, MikroTikSSHClient] = {}
        self._lock = threading.Lock()

        for device in devices:
            key = device.title.casefold()
            if key in self._devices:
                raise ValueError(
                    f"Duplicate device title {device.title!r} in inventory — "
                    "titles must be unique."
                )
            self._devices[key] = device

    # ── Introspection ──────────────────────────────────────────────────────

    def __len__(self) -> int:
        return len(self._devices)

    @property
    def titles(self) -> List[str]:
        return [d.title for d in self._devices.values()]

    def all_devices(self) -> List[DeviceConfig]:
        return list(self._devices.values())

    def describe(self) -> List[dict]:
        """Device metadata for the LLM. Never includes credentials."""
        return [
            {
                "title": d.title,
                "host": d.host,
                "port": d.port,
                "username": d.username,
                "tags": d.tags,
                "region": d.region,
            }
            for d in self._devices.values()
        ]

    # ── Resolution ─────────────────────────────────────────────────────────

    def resolve(self, title: Optional[str] = None) -> DeviceConfig:
        """Resolve a device title to its definition.

        With a single-device inventory the title may be omitted.  With more
        than one device the title is required, and an unknown title raises
        :class:`DeviceNotFoundError` listing the valid titles so the caller can
        correct itself in one step.
        """
        if not self._devices:
            raise DeviceNotFoundError(
                "No MikroTik devices are configured. Set MIKROTIK_INVENTORY "
                "(or the single-device MIKROTIK_HOST settings)."
            )

        if title is None or not str(title).strip():
            if len(self._devices) == 1:
                return next(iter(self._devices.values()))
            raise DeviceNotFoundError(
                "This server manages multiple MikroTik devices, so a device "
                f"must be specified. Available devices: {', '.join(self.titles)}."
            )

        device = self._devices.get(str(title).strip().casefold())
        if device is None:
            raise DeviceNotFoundError(
                f"Unknown device {title!r}. "
                f"Available devices: {', '.join(self.titles)}."
            )
        return device

    # ── SSH clients ────────────────────────────────────────────────────────

    def get_client(self, title: Optional[str] = None) -> MikroTikSSHClient:
        """Return a connected SSH client for the resolved device.

        The client for each device is created once and reused.  A client whose
        connection has dropped is rebuilt transparently on the next call.
        """
        device = self.resolve(title)
        key = device.title.casefold()

        with self._lock:
            client = self._clients.get(key)
            if client is not None and self._is_alive(client):
                return client

            if client is not None:
                # Stale/broken session — drop it before rebuilding.
                try:
                    client.disconnect()
                except Exception:
                    pass
                self._clients.pop(key, None)

            client = MikroTikSSHClient(
                host=device.host,
                username=device.username,
                password=device.password,
                key_filename=device.key_filename,
                port=device.port,
            )
            if not client.connect():
                raise ConnectionError(
                    f"Failed to connect to MikroTik device '{device.title}' "
                    f"({device.host}:{device.port})"
                )
            self._clients[key] = client
            logger.info(f"Opened SSH client for device '{device.title}'")
            return client

    @staticmethod
    def _is_alive(client: MikroTikSSHClient) -> bool:
        """True when the client's transport is still usable."""
        try:
            transport = client.client.get_transport() if client.client else None
            return bool(transport and transport.is_active())
        except Exception:
            return False

    def close(self) -> None:
        """Disconnect every open client."""
        with self._lock:
            for title, client in self._clients.items():
                try:
                    client.disconnect()
                except Exception:
                    logger.debug(f"Error closing client for '{title}'", exc_info=True)
            self._clients.clear()


# ---------------------------------------------------------------------------
# Module-level inventory
# ---------------------------------------------------------------------------

_inventory: Optional[Inventory] = None
_inventory_lock = threading.Lock()


def _load_devices() -> List[DeviceConfig]:
    """Build the device list from configuration.

    Precedence: ``inventory`` (inline JSON) > ``inventory_file`` > the flat
    single-device settings.  The last case keeps every existing single-device
    deployment working with no configuration change.
    """
    cfg = config.mikrotik_config

    if cfg.inventory:
        return list(cfg.inventory)

    if cfg.inventory_file:
        path = os.path.expanduser(cfg.inventory_file)
        with open(path, "r", encoding="utf-8") as fh:
            raw = json.load(fh)
        if isinstance(raw, dict):
            raw = raw.get("inventory", [raw])
        return [DeviceConfig(**item) for item in raw]

    # Backwards-compatible single device.
    return [
        DeviceConfig(
            title=cfg.host,
            host=cfg.host,
            port=cfg.port,
            username=cfg.username,
            password=cfg.password,
            key_filename=cfg.key_filename,
        )
    ]


def get_inventory() -> Inventory:
    global _inventory
    if _inventory is None:
        with _inventory_lock:
            if _inventory is None:
                _inventory = Inventory(_load_devices())
    return _inventory


def reset_inventory() -> None:
    """Drop the cached inventory (used by tests and after config reloads)."""
    global _inventory
    with _inventory_lock:
        if _inventory is not None:
            _inventory.close()
        _inventory = None
