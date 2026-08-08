# Inventory (multiple devices)

MikroTik MCP can manage a fleet of devices from one server. Devices are
declared in an **inventory**; each entry has a unique `title`, which is the
identifier tools use to target that device.

With no inventory configured the server behaves exactly as before: a single
device built from `MIKROTIK_HOST` / `MIKROTIK_USERNAME` / … , and the `device`
argument can be omitted everywhere.

## Configuring the inventory

Supply a JSON array either inline or from a file:

| Variable | Purpose |
|---|---|
| `MIKROTIK_INVENTORY` | the inventory as a JSON array |
| `MIKROTIK_INVENTORY_FILE` | path to a file containing that JSON |

In an MCP client config these belong in the server's **`env`** block — that is
the channel a client forwards to the spawned process:

```json
{
  "mcpServers": {
    "mikrotik-mcp-server": {
      "command": "python",
      "args": ["-m", "mcp_mikrotik.server"],
      "env": {
        "MIKROTIK_INVENTORY": "[{\"title\":\"TitleA\",\"tags\":[\"tag1\",\"tag2\"],\"region\":\"NL\",\"host\":\"127.0.0.1\",\"port\":22,\"username\":\"admin\",\"password\":\"admin\"},{\"title\":\"TitleB\",\"tags\":[\"tag1\",\"tag3\"],\"region\":\"DE\",\"host\":\"192.168.88.1\",\"port\":22,\"username\":\"admin\",\"password\":\"admin\"}]"
      }
    }
  }
}
```

A file keeps the config readable and the secrets out of the client config:

```json
{ "env": { "MIKROTIK_INVENTORY_FILE": "/etc/mikrotik/inventory.json" } }
```

```json
[
  {
    "title": "TitleA",
    "tags": ["tag1", "tag2"],
    "region": "NL",
    "host": "127.0.0.1",
    "port": 22,
    "username": "admin",
    "password": "admin"
  },
  {
    "title": "TitleB",
    "tags": ["tag1", "tag3"],
    "region": "DE",
    "host": "192.168.88.1",
    "port": 22,
    "username": "admin",
    "key_filename": "/keys/id_ed25519"
  }
]
```

### Device fields

| Field | Required | Notes |
|---|---|---|
| `title` | yes | Unique identifier the LLM passes as `device`. Matching is case-insensitive. |
| `host` | yes | IP or hostname |
| `port` | no | SSH port, default `22` |
| `username` | no | default `admin` |
| `password` | no | omit when using `key_filename` |
| `key_filename` | no | path to an SSH private key (preferred over a password) |
| `tags` | no | free-form labels, e.g. `["branch", "eu"]` |
| `region` | no | free-form label, e.g. `"NL"` |

## Selecting a device

Every device-scoped tool accepts an optional `device` argument:

- **One device configured** — omit `device`; that device is used.
- **More than one** — pass the `title`. Omitting it returns an error that lists
  the available devices, as does an unknown title, so the caller can correct
  itself immediately.

```
list_devices()                                  # discover the fleet
list_interfaces(device="TitleA")                # target one device
create_vlan_interface(device="TitleB", name="vlan100", vlan_id=100, interface="ether1")
```

## `list_devices`

Lists the devices this server manages — title, host, port, username, tags and
region. **Credentials are never returned.**

```
list_devices()
```

## Docker

The image accepts the same two variables, and ships a `/config` directory to
mount the inventory into:

```bash
docker run --rm -i \
  -v "$PWD/inventory.json:/config/inventory.json:ro" \
  -e MIKROTIK_INVENTORY_FILE=/config/inventory.json \
  ghcr.io/jeff-nasseri/mikrotik-mcp:latest
```

The entrypoint also takes `--inventory '<json>'` and `--inventory-file <path>`.

A mounted file is preferable to `MIKROTIK_INVENTORY`: environment values are
visible in `docker inspect`, file contents are not. The container runs as **uid
1000** (`mcpuser`), so the file must be readable by that uid; if it isn't, the
entrypoint stops with an explicit message instead of starting with no devices.

When an inventory is configured it wins, so `MIKROTIK_HOST` / `MIKROTIK_USERNAME`
/ `MIKROTIK_PASSWORD` / `MIKROTIK_PORT` are ignored and can be dropped.

See [Installation](../../getting-started/installation.md) for a Compose example.

## Connections are per command

Every command opens its own SSH connection to the target device and closes it
when the command finishes. Connections are never pooled or shared.

This matters when more than one client session talks to the same server
process: a shared connection would mean shared fate, so one session
disconnecting, timing out or failing to authenticate would break a command
another session was running against the same device. With a connection per
command the sessions cannot disturb each other.

The trade-off is one SSH handshake per command. On a LAN that is a few tens of
milliseconds; if the device is far away or heavily loaded, expect commands to
cost noticeably more than the RouterOS work alone.

## Safe mode is per device

Safe mode holds a persistent session, and each device has its own. Enabling it
on one device does not affect any other:

```
enable_safe_mode(device="TitleA")
create_filter_rule(device="TitleA", chain="forward", action="drop", ...)
commit_safe_mode(device="TitleA")     # or rollback_safe_mode(device="TitleA")
```

## Two-device test environment

`routeros-docker/docker-compose.yml` starts two RouterOS instances for testing:

| Container | SSH | Suggested title |
|---|---|---|
| `routeros-a` | `127.0.0.1:2222` | RouterA |
| `routeros-b` | `127.0.0.1:2223` | RouterB |

```bash
docker-compose -f routeros-docker/docker-compose.yml up -d
python tests/smoke_multi_device.py
```

> Both routers boot inside QEMU and need roughly two minutes before SSH answers.

## Security

Credentials live in the inventory, so the whole inventory is a secret. Prefer
`key_filename` over `password`, keep the JSON in a file with restricted
permissions rather than inline in a client config, and remember that values
passed as environment variables are visible via `docker inspect` — see
[SECURITY.md](../../../SECURITY.md).
