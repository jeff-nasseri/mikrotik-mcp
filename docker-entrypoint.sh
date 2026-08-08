#!/bin/sh
set -e

usage() {
    echo "Usage: $0 [OPTIONS] [COMMAND]"
    echo ""
    echo "Single device:"
    echo "  --host HOST           MikroTik device IP/hostname"
    echo "  --username USERNAME   SSH username"
    echo "  --password PASSWORD   SSH password"
    echo "  --port PORT           SSH port (default: 22)"
    echo ""
    echo "Multiple devices (inventory) — takes precedence over the options above:"
    echo "  --inventory JSON      Inventory as a JSON array of devices"
    echo "  --inventory-file PATH Path to a file holding that JSON"
    echo ""
    echo "Other:"
    echo "  --transport TYPE      Transport: stdio, sse, streamable-http (default: stdio)"
    echo "  --help                Show this help message"
    echo ""
    echo "Environment variables:"
    echo "  MIKROTIK_HOST            MikroTik device IP/hostname"
    echo "  MIKROTIK_USERNAME        SSH username"
    echo "  MIKROTIK_PASSWORD        SSH password"
    echo "  MIKROTIK_PORT            SSH port (default: 22)"
    echo "  MIKROTIK_INVENTORY       Inventory as a JSON array of devices"
    echo "  MIKROTIK_INVENTORY_FILE  Path to a file holding that JSON"
    echo "  MIKROTIK_MCP__TRANSPORT  Transport type (default: stdio)"
    echo ""
    echo "Examples:"
    echo "  $0 --host 192.168.88.1 --username admin --password admin123"
    echo "  $0 --host 192.168.88.1 --username admin --password admin123 --transport sse"
    echo "  MIKROTIK_HOST=192.168.88.1 MIKROTIK_MCP__TRANSPORT=sse $0"
    echo "  $0 --inventory-file /config/inventory.json --transport streamable-http"
    exit 1
}

MIKROTIK_MCP__TRANSPORT="${MIKROTIK_MCP__TRANSPORT:-stdio}"

while [ $# -gt 0 ]; do
    case $1 in
        --host)
            MIKROTIK_HOST="$2"
            shift 2
            ;;
        --username)
            MIKROTIK_USERNAME="$2"
            shift 2
            ;;
        --password)
            MIKROTIK_PASSWORD="$2"
            shift 2
            ;;
        --port)
            MIKROTIK_PORT="$2"
            shift 2
            ;;
        --inventory)
            MIKROTIK_INVENTORY="$2"
            shift 2
            ;;
        --inventory-file)
            MIKROTIK_INVENTORY_FILE="$2"
            shift 2
            ;;
        --transport)
            MIKROTIK_MCP__TRANSPORT="$2"
            shift 2
            ;;
        --help)
            usage
            ;;
        *)
            break
            ;;
    esac
done

export MIKROTIK_MCP__TRANSPORT

# An inventory describes the whole fleet, so it takes precedence over the
# single-device settings. Don't fall back to the 192.168.88.1 default in that
# case: inventing a host nobody asked for reads as if it still applied. Values
# the user passed with `docker run -e` are already in the environment and stay
# there; they are simply ignored by the config layer.
if [ -n "${MIKROTIK_INVENTORY:-}" ] || [ -n "${MIKROTIK_INVENTORY_FILE:-}" ]; then
    if [ -n "${MIKROTIK_INVENTORY_FILE:-}" ] && [ ! -r "$MIKROTIK_INVENTORY_FILE" ]; then
        echo "Error: inventory file '$MIKROTIK_INVENTORY_FILE' is not readable inside the container." >&2
        echo "" >&2
        echo "Mount it, for example:" >&2
        echo "  -v \"\$PWD/inventory.json:/config/inventory.json:ro\"" >&2
        echo "" >&2
        echo "The container runs as uid 1000 (mcpuser), so the file on the host must be" >&2
        echo "readable by that uid — 'chmod 644 inventory.json' is usually enough." >&2
        exit 1
    fi
    [ -n "${MIKROTIK_INVENTORY:-}" ] && export MIKROTIK_INVENTORY
    [ -n "${MIKROTIK_INVENTORY_FILE:-}" ] && export MIKROTIK_INVENTORY_FILE
else
    MIKROTIK_HOST="${MIKROTIK_HOST:-192.168.88.1}"
    MIKROTIK_USERNAME="${MIKROTIK_USERNAME:-admin}"
    MIKROTIK_PASSWORD="${MIKROTIK_PASSWORD:-}"
    MIKROTIK_PORT="${MIKROTIK_PORT:-22}"
    export MIKROTIK_HOST
    export MIKROTIK_USERNAME
    export MIKROTIK_PASSWORD
    export MIKROTIK_PORT
fi

if [ $# -eq 0 ]; then
    exec mcp-server-mikrotik
else
    exec "$@"
fi
