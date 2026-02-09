#!/bin/sh
set -e

usage() {
    echo "Usage: $0 [OPTIONS] [COMMAND]"
    echo ""
    echo "Options:"
    echo "  --host HOST           MikroTik device IP/hostname"
    echo "  --username USERNAME   SSH username"
    echo "  --password PASSWORD   SSH password"
    echo "  --port PORT           SSH port (default: 22)"
    echo "  --help                Show this help message"
    echo ""
    echo "Environment variables:"
    echo "  MIKROTIK_HOST         MikroTik device IP/hostname"
    echo "  MIKROTIK_USERNAME     SSH username"
    echo "  MIKROTIK_PASSWORD     SSH password"
    echo "  MIKROTIK_PORT         SSH port (default: 22)"
    echo ""
    echo "Examples:"
    echo "  $0 --host 192.168.88.1 --username admin --password admin123"
    echo "  $0 mcp-server-mikrotik --host 192.168.88.1 --username admin --password admin123"
    echo "  MIKROTIK_HOST=192.168.88.1 MIKROTIK_USERNAME=admin MIKROTIK_PASSWORD=admin123 $0"
    exit 1
}

MIKROTIK_HOST="${MIKROTIK_HOST:-192.168.88.1}"
MIKROTIK_USERNAME="${MIKROTIK_USERNAME:-admin}"
MIKROTIK_PASSWORD="${MIKROTIK_PASSWORD:-}"
MIKROTIK_PORT="${MIKROTIK_PORT:-22}"

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
        --help)
            usage
            ;;
        *)
            break
            ;;
    esac
done

export MIKROTIK_HOST
export MIKROTIK_USERNAME
export MIKROTIK_PASSWORD
export MIKROTIK_PORT

if [ $# -eq 0 ]; then
    exec mcp-server-mikrotik
else
    exec "$@"
fi