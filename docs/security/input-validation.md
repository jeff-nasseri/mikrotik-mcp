# Input Validation & Command Injection Protection

MikroTik MCP implements two zero-dependency layers of protection against
injection attacks (issue [#53](https://github.com/jeff-nasseri/mikrotik-mcp/issues/53)).

---

## Layer 1 — Structural command-injection check

Every assembled RouterOS command is validated by `check_command_safety()`
immediately before it is sent over SSH. Characters that **never appear in a
legitimate command** but are the classic building blocks of injection are rejected:

| Blocked | Reason |
|---------|--------|
| `;` | command separator — `name="x" ; /system reboot` |
| `` ` `` | backtick sub-command |
| `{` `}` | script block delimiters |
| `\n` `\r` | line break — splits one command into two |

`[` and `]` are intentionally **allowed** — the RouterOS `[find ...]`
sub-selector uses them legitimately.

This layer blocks the exact payload from issue #53 — `foo"] ; /system reboot;`
— by default, with no configuration required.

---

## Layer 2 — Per-field allowlist

Each user-supplied string parameter is validated against a tight character
allowlist matched to its RouterOS field type **before** the command is
constructed. Rather than blocking a known-bad set, only a known-good set of
characters is accepted — harder to bypass and gives clear error messages.

### Field types

| Field type | Accepted values | Example |
|---|---|---|
| `INTERFACE_NAME` | letters, digits, `.` `-` `_` (max 47) | `ether1-wan` |
| `IP_ADDRESS` | dotted-decimal IPv4 | `192.168.1.1` |
| `IP_CIDR` | IPv4 with optional `/prefix` | `192.168.1.0/24` |
| `IP_RANGE` | `x.x.x.x-x.x.x.x` | `192.168.1.1-192.168.1.100` |
| `IP_RANGES` | comma-separated ranges/CIDRs | `10.0.0.1-10.0.0.50,10.0.0.100-10.0.0.120` |
| `HOSTNAME` | letters, digits, `.` `-` `_` (max 253) | `vpn.example.com` |
| `MAC_ADDRESS` | `AA:BB:CC:DD:EE:FF` | `00:1A:2B:3C:4D:5E` |
| `BANDWIDTH` | digits + `K`/`M`/`G`, optional `/down` | `10M/5M` |
| `DURATION` | digits + `w`/`d`/`h`/`m`/`s` | `1h30m` |
| `COMMENT` | printable ASCII (max 255 chars) | `office uplink` |
| `ROUTEROS_ID` | optional `*` + digits | `*3` or `42` |
| `PORT_SPEC` | single, range, or comma list | `80-443` |
| `USERNAME` | letters, digits, `.` `-` `_` | `mcp-user` |
| `WG_KEY` | 44-char base64 WireGuard key | `AAAA…=` |
| `ADDRESS_LIST` | letters, digits, space, `.` `-` `_` | `my-blocked-list` |
| `ROUTING_MARK` | letters, digits, `.` `-` `_` | `main` |
| `LOG_PREFIX` | letters, digits, space, `:` `.` `-` | `fw-drop` |

### How it works

In each scope module, user-supplied string parameters are validated at the
start of each tool function:

```python
from ..security import V, validate_field

async def mikrotik_create_vlan_interface(ctx, name, vlan_id, interface, comment=None, ...):
    validate_field(name,      V.INTERFACE_NAME, "name")
    validate_field(interface, V.INTERFACE_NAME, "interface")
    validate_field(comment,   V.COMMENT,        "comment")
    # ... build command
```

`validate_field` is a no-op for `None` and empty strings (optional fields).
It raises `SecurityError` (a `ValueError` subclass) when the value falls
outside the allowed character set.

---

## No external dependencies

Both layers are implemented in pure Python using only the standard `re`
module. There is no ML model, no download, and no runtime overhead beyond a
regex match per validated field.
