# Fleet Management

Multi-device fleet management lets you manage a collection of MikroTik routers from a single MCP session.
You define an inventory of devices, each with a name, connection details, and an optional list of tags.
Tools can then target a single device by name, a group of devices by tag, or every device at once —
executing RouterOS commands in parallel and returning per-device results.

## Configuration

Define your fleet by setting the `MIKROTIK_DEVICES` environment variable to a JSON array:

```bash
MIKROTIK_DEVICES='[
  {"name": "mt-nl-1", "host": "1.1.1.1", "username": "admin", "password": "secret", "tags": ["nl", "eu", "core"]},
  {"name": "mt-usa-1", "host": "2.2.2.1", "username": "admin", "password": "secret", "tags": ["usa", "core"]},
  {"name": "mt-uae-1", "host": "3.3.3.1", "username": "admin", "password": "secret", "tags": ["uae"]},
  {"name": "mt-edge-1", "host": "10.0.0.1", "port": 2222, "key_filename": "/keys/id_rsa", "tags": ["edge"]}
]'
```

### DeviceConfig fields

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `name` | string | yes | — | Unique identifier for the device |
| `host` | string | yes | — | IP address or hostname |
| `username` | string | no | `admin` | SSH username |
| `password` | string | no | `""` | SSH password |
| `port` | integer | no | `22` | SSH port |
| `key_filename` | string | no | `null` | Path to private key file |
| `tags` | array[string] | no | `[]` | Labels for grouping (region, role, etc.) |

> **Backward compatibility:** The single-device config (`MIKROTIK_HOST`, `MIKROTIK_USERNAME`, etc.) continues to work unchanged. Set `MIKROTIK_DEVICES` only if you want fleet capabilities; it defaults to an empty list.

---

## Tools

### `list_devices`

Lists all devices currently loaded in the fleet inventory. Read-only — never connects to any device.

**Parameters:** none

**Returns:** JSON array of device summaries (name, host, port, username, tags).

**Example:**
```
list_devices()
```
```json
[
  {"name": "mt-nl-1", "host": "1.1.1.1", "port": 22, "username": "admin", "tags": ["nl", "eu", "core"]},
  {"name": "mt-usa-1", "host": "2.2.2.1", "port": 22, "username": "admin", "tags": ["usa", "core"]},
  {"name": "mt-uae-1", "host": "3.3.3.1", "port": 22, "username": "admin", "tags": ["uae"]}
]
```

---

### `run_command_on_device`

Executes a single RouterOS command on one specific device, identified by name.

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `device_name` | string | yes | The `name` of the target device as defined in `MIKROTIK_DEVICES` |
| `command` | string | yes | RouterOS CLI command (e.g. `/ip address print`) |

**Returns:** The command output prefixed with the device name, or an error message if the device is not found or the connection fails.

**Example:**
```
run_command_on_device(device_name="mt-nl-1", command="/system resource print")
```
```
mt-nl-1:
                   uptime: 5d12h33m24s
                  version: 7.14.3 (stable)
             free-memory: 128.0MiB
```

---

### `run_command_on_tag`

Executes a RouterOS command in parallel on every device that carries the given tag.
Results are returned as a JSON object keyed by device name so you can immediately see
which devices succeeded and which failed.

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `tag` | string | yes | Tag to match (e.g. `"eu"`, `"core"`, `"edge"`) |
| `command` | string | yes | RouterOS CLI command |

**Returns:** JSON object mapping each matching device name to its command output or an error string.

**Example:**
```
run_command_on_tag(tag="core", command="/system resource print")
```
```json
{
  "mt-nl-1": "uptime: 5d12h...",
  "mt-usa-1": "uptime: 2d08h..."
}
```

If a device is unreachable:
```json
{
  "mt-nl-1": "uptime: 5d12h...",
  "mt-usa-1": "Error: Failed to connect to 2.2.2.1"
}
```

---

### `run_command_on_all_devices`

Executes a RouterOS command in parallel on **all** devices in the inventory.
An optional `tag_filter` restricts execution to devices carrying that tag
(equivalent to `run_command_on_tag` but callable without knowing the tag up front).

**Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `command` | string | yes | RouterOS CLI command |
| `tag_filter` | string | no | When provided, only devices with this tag are targeted |

**Returns:** JSON object mapping every targeted device name to its command output or error.

**Example — all devices:**
```
run_command_on_all_devices(command="/ip address print")
```
```json
{
  "mt-nl-1": "...",
  "mt-usa-1": "...",
  "mt-uae-1": "..."
}
```

**Example — filtered by tag:**
```
run_command_on_all_devices(command="/ip address print", tag_filter="eu")
```
```json
{
  "mt-nl-1": "..."
}
```

---

## Notes

- Fleet tools always open a **fresh SSH connection** per device. They do not share the Safe Mode session that may be active on the default single device.
- Commands are dispatched concurrently with `asyncio.gather`, so latency scales with the slowest device, not the total number.
- Passwords are never included in the `list_devices` output.
