# Using MCPO with MikroTik MCP Server

This guide shows how to expose your MikroTik MCP server as a RESTful API using MCPO (MCP-to-OpenAPI proxy).

## Prerequisites

- Python 3.8+
- MikroTik MCP server already set up
- `uv` package manager (recommended) or `pip`

## Installation

Install MCPO using one of these methods:

```bash
# Option 1: Using uvx (recommended - no installation needed)
uvx mcpo --help

# Option 2: Using pip
pip install mcpo
```

## Configuration

Create a `mcp-config.json` file in your project directory:

```json
{
  "mcpServers": {
    "mikrotik-mcp-server": {
      "command": "python",
      "args": [
        "src/mcp_mikrotik/server.py",
        "--password", "admin",
        "--host", "192.168.1.1",
        "--port", "22",
        "--username", "admin"
      ],
      "env": {}
    }
  }
}
```

**Note:** Adjust the MikroTik connection parameters (`host`, `username`, `password`, `port`) according to your setup.

## Starting the MCPO Server

```bash
# Start MCPO with API key authentication
uvx mcpo --port 8000 --api-key "your-secret-key" --config ./mcp-config.json

# Or without authentication (not recommended for production)
uvx mcpo --port 8000 --config ./mcp-config.json
```

The server will start and display:
- Server running on `http://0.0.0.0:8000`
- Interactive API docs available at `http://localhost:8000/docs`

### cURL Examples

**List IP Addresses:**
```bash
curl -X POST http://localhost:8000/mikrotik-mcp-server/mikrotik_list_ip_addresses \
  -H "Authorization: Bearer your-secret-key" \
  -H "Content-Type: application/json" \
  -d '{}'
```

