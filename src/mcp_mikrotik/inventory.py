import threading
from typing import Dict, List, Optional

from .config import DeviceConfig, mikrotik_config


class DeviceInventory:
    """Registry of MikroTik devices loaded from configuration.

    Devices are keyed by their ``name`` field so lookups are O(1).
    Tag-based queries scan the full list but the fleet is expected to be small
    (tens of devices), so no secondary index is needed.
    """

    def __init__(self, devices: List[DeviceConfig]) -> None:
        self._devices: Dict[str, DeviceConfig] = {d.name: d for d in devices}

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def get_device(self, name: str) -> Optional[DeviceConfig]:
        """Return the device with the given name, or ``None``."""
        return self._devices.get(name)

    def get_devices_by_tag(self, tag: str) -> List[DeviceConfig]:
        """Return all devices that carry *tag*."""
        return [d for d in self._devices.values() if tag in d.tags]

    def get_all_devices(self) -> List[DeviceConfig]:
        """Return every device in the inventory."""
        return list(self._devices.values())

    def count(self) -> int:
        return len(self._devices)

    def list_names(self) -> List[str]:
        return list(self._devices.keys())


# ---------------------------------------------------------------------------
# Module-level singleton (loaded once from mikrotik_config at import time)
# ---------------------------------------------------------------------------

_inventory: Optional[DeviceInventory] = None
_inventory_lock = threading.Lock()


def get_inventory() -> DeviceInventory:
    """Return the global DeviceInventory singleton, creating it on first call."""
    global _inventory
    if _inventory is None:
        with _inventory_lock:
            if _inventory is None:
                _inventory = DeviceInventory(mikrotik_config.devices)
    return _inventory


def reset_inventory() -> None:
    """Discard the cached singleton — intended for tests only."""
    global _inventory
    with _inventory_lock:
        _inventory = None
