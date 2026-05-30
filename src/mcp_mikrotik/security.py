"""Input validation for MikroTik MCP (issue #53).

Two layers of protection, zero external dependencies:

Layer 1 — Structural command-injection check (always active)
    check_command_safety() rejects characters that never appear in a
    legitimate RouterOS command but enable command-injection:
    ; ` { } newline carriage-return

Layer 2 — Per-field allowlist (always active)
    validate_field() applies a tight character allowlist matched to each
    RouterOS field type. Rather than blocking a known-bad set, it only
    allows a known-good set — much harder to bypass.

Usage in scope files::

    from ..security import V, validate_field

    validate_field(name,     V.INTERFACE_NAME, "name")
    validate_field(address,  V.IP_CIDR,        "address")
    validate_field(comment,  V.COMMENT,        "comment")
"""

from __future__ import annotations

import logging
import re
from enum import Enum
from typing import Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Custom exception
# ---------------------------------------------------------------------------

class SecurityError(ValueError):
    """Raised when a security violation is detected in user input."""


# ---------------------------------------------------------------------------
# Layer 1 — Structural command-injection prevention
# ---------------------------------------------------------------------------

# Characters that NEVER appear in a legitimate RouterOS command string but
# are the classic command-injection enablers.  '[' and ']' are intentionally
# NOT blocked here because RouterOS uses them in the [find ...] selector.
_COMMAND_FORBIDDEN = re.compile(r'[;`{}\r\n]')


def check_command_safety(command: str) -> None:
    """Validate the final assembled RouterOS command for command-injection.

    Called by the connector immediately before the command is sent over SSH.
    Blocks the canonical issue #53 payload (``foo"] ; /system reboot;``) and
    all newline/carriage-return injection without any external dependency.
    """
    match = _COMMAND_FORBIDDEN.search(command)
    if match:
        char = match.group()
        label = {"\n": "newline", "\r": "carriage-return"}.get(char, repr(char))
        raise SecurityError(
            f"RouterOS command contains a forbidden character ({label}). "
            "Possible command injection attempt."
        )


# ---------------------------------------------------------------------------
# Layer 2 — Per-field allowlist
# ---------------------------------------------------------------------------

class V(str, Enum):
    """Field-type identifiers for validate_field()."""
    INTERFACE_NAME  = "interface_name"   # ether1, bridge, wg0 …
    IP_ADDRESS      = "ip_address"       # 192.168.1.1
    IP_CIDR         = "ip_cidr"          # 192.168.1.0/24
    IP_RANGE        = "ip_range"         # 192.168.1.1-192.168.1.100
    IP_RANGES       = "ip_ranges"        # comma-separated CIDR list
    HOSTNAME        = "hostname"         # router.example.com
    MAC_ADDRESS     = "mac_address"      # AA:BB:CC:DD:EE:FF
    BANDWIDTH       = "bandwidth"        # 10M  /  10M/10M
    DURATION        = "duration"         # 1d  12h  1h30m
    COMMENT         = "comment"          # free text, printable ASCII
    ROUTEROS_ID     = "routeros_id"      # *1  /  1  /  0
    USERNAME        = "username"         # admin, mcp-user
    WG_KEY          = "wg_key"           # base64 WireGuard public key
    ROUTING_MARK    = "routing_mark"     # a VRF/policy name
    ADDRESS_LIST    = "address_list"     # firewall address-list name
    PORT_SPEC       = "port_spec"        # 80  /  80-443  /  80,443
    LOG_PREFIX      = "log_prefix"       # short text label


# Compiled patterns — tight allowlists that match only what RouterOS actually
# accepts for each field type.
_PATTERNS: dict[V, re.Pattern] = {
    # Interface names: letters, digits, dot, dash, underscore; 1-47 chars
    V.INTERFACE_NAME: re.compile(r'^[a-zA-Z0-9._-]{1,47}$'),

    # IPv4 dotted-decimal (plain host address)
    V.IP_ADDRESS: re.compile(
        r'^(\d{1,3}\.){3}\d{1,3}$'
    ),

    # IPv4 CIDR (address optional prefix-length)
    V.IP_CIDR: re.compile(
        r'^(\d{1,3}\.){3}\d{1,3}(/\d{1,2})?$'
    ),

    # IPv4 range: 192.168.1.1-192.168.1.100
    V.IP_RANGE: re.compile(
        r'^(\d{1,3}\.){3}\d{1,3}-(\d{1,3}\.){3}\d{1,3}$'
    ),

    # Comma-separated CIDR list: "10.0.0.0/8,192.168.1.0/24"
    V.IP_RANGES: re.compile(
        r'^(\d{1,3}\.){3}\d{1,3}(-(\d{1,3}\.){3}\d{1,3}|(/\d{1,2})?)'
        r'(,(\d{1,3}\.){3}\d{1,3}(-(\d{1,3}\.){3}\d{1,3}|(/\d{1,2})?))*$'
    ),

    # Hostname: letters, digits, dot, dash
    V.HOSTNAME: re.compile(r'^[a-zA-Z0-9._-]{1,253}$'),

    # MAC address: AA:BB:CC:DD:EE:FF or AA-BB-CC-DD-EE-FF
    V.MAC_ADDRESS: re.compile(
        r'^([0-9A-Fa-f]{2}[:\-]){5}[0-9A-Fa-f]{2}$'
    ),

    # Bandwidth: "10M", "512K", "1G", "10M/5M"
    V.BANDWIDTH: re.compile(
        r'^\d+(\.\d+)?[KMGkmg]?(\/\d+(\.\d+)?[KMGkmg]?)?$'
    ),

    # Duration: "30s", "5m", "1h", "2d", "1h30m", "1w"
    V.DURATION: re.compile(
        r'^(\d+[wdhms])+$'
    ),

    # Comment: printable ASCII only, max 255 chars
    V.COMMENT: re.compile(r'^[\x20-\x7E]{0,255}$'),

    # RouterOS IDs: "*1", "0", "42"
    V.ROUTEROS_ID: re.compile(r'^\*?\d+$'),

    # Username: alphanumeric + underscore + dash
    V.USERNAME: re.compile(r'^[a-zA-Z0-9._-]{1,64}$'),

    # WireGuard base64 public key (44 chars)
    V.WG_KEY: re.compile(r'^[A-Za-z0-9+/]{43}=$'),

    # Routing mark / VRF name: same as interface name
    V.ROUTING_MARK: re.compile(r'^[a-zA-Z0-9._-]{1,64}$'),

    # Firewall address-list name: letters, digits, spaces, dot, dash, underscore
    V.ADDRESS_LIST: re.compile(r'^[a-zA-Z0-9 ._-]{1,64}$'),

    # Port spec: single port, range, or comma list
    V.PORT_SPEC: re.compile(r'^\d+(-\d+)?(,\d+(-\d+)?)*$'),

    # Log prefix: short printable label, no quotes
    V.LOG_PREFIX: re.compile(r"^[a-zA-Z0-9 ._:\-]{0,64}$"),
}


def validate_field(
    value: Optional[str],
    field_type: V,
    field_name: str = "input",
) -> None:
    """Validate *value* against the allowlist for *field_type*.

    A no-op when *value* is ``None`` or an empty string (optional fields).
    Raises :class:`SecurityError` when the value contains characters outside
    the allowed set for the given field type.

    Parameters
    ----------
    value:
        The user-provided string to validate.
    field_type:
        The :class:`V` enum member that identifies the expected field type.
    field_name:
        Human-readable parameter name used in the error message.
    """
    if not value:
        return

    pattern = _PATTERNS[field_type]
    if not pattern.match(value):
        raise SecurityError(
            f"Invalid value for '{field_name}': {value!r} is not a valid "
            f"{field_type.value.replace('_', ' ')}."
        )
