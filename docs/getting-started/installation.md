# Installation

## Prerequisites
- Python 3.8+
- MikroTik RouterOS device with API access enabled
- Python dependencies (routeros-api or similar)

## Manual Installation

```bash
# Clone the repository
git clone https://github.com/jeff-nasseri/mikrotik-mcp/tree/master
cd mcp-mikrotik

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e .

# Run the server (stdio, default)
mcp-server-mikrotik

# Run with SSE transport
mcp-server-mikrotik --mcp.transport sse

# Run with streamable HTTP transport
mcp-server-mikrotik --mcp.transport streamable-http
```

### CLI Options

| Flag | Description | Default |
|------|-------------|---------|
| `--host` | MikroTik device IP/hostname | from config |
| `--username` | SSH username | from config |
| `--password` | SSH password | from config |
| `--key-filename` | SSH key filename | from config |
| `--port` | SSH port | `22` |
| `--mcp.transport` | Transport type: `stdio`, `sse`, `streamable-http` | `stdio` |
| `--mcp.host` | HTTP server listen address | `0.0.0.0` |
| `--mcp.port` | HTTP server listen port | `8000` |

HTTP-based transports (`sse`, `streamable-http`) expose a `GET /health` endpoint for health checks. This endpoint is **not available** in `stdio` mode.

## Docker Installation

The easiest way to run the MCP MikroTik server is using Docker.

1. **Clone the repository:**
   ```bash
   git clone https://github.com/jeff-nasseri/mikrotik-mcp.git
   cd mikrotik-mcp
   ```

2. **Build the Docker image:**
   ```bash
   docker build -t mikrotik-mcp .
   ```

3. **Run with stdio (default, for IDE integration):**

   Add this to your `~/.cursor/mcp.json`:
   ```json
   {
     "mcpServers": {
       "mikrotik-mcp-server": {
         "command": "docker",
         "args": [
           "run",
           "--rm",
           "-i",
           "-e", "MIKROTIK_HOST=192.168.88.1",
           "-e", "MIKROTIK_USERNAME=sshuser",
           "-e", "MIKROTIK_PASSWORD=your_password",
           "-e", "MIKROTIK_PORT=22",
           "mikrotik-mcp"
         ]
       }
     }
   }
   ```

4. **Run with SSE or streamable HTTP transport:**

   ```bash
   docker run --rm -p 8000:8000 \
     -e MIKROTIK_HOST=192.168.88.1 \
     -e MIKROTIK_USERNAME=sshuser \
     -e MIKROTIK_PASSWORD=your_password \
     -e MIKROTIK_MCP__TRANSPORT=sse \
     mikrotik-mcp
   ```

   The server will be available at `http://localhost:8000/sse` (SSE) or `http://localhost:8000/mcp` (streamable HTTP).

   **Environment Variables:**

   | Variable | Description | Default |
   |----------|-------------|---------|
   | `MIKROTIK_HOST` | MikroTik device IP/hostname | `192.168.88.1` |
   | `MIKROTIK_USERNAME` | SSH username | `admin` |
   | `MIKROTIK_PASSWORD` | SSH password | _(empty)_ |
   | `MIKROTIK_PORT` | SSH port | `22` |
   | `MIKROTIK_MCP__TRANSPORT` | Transport type: `stdio`, `sse`, `streamable-http` | `stdio` |
   | `MIKROTIK_MCP__HOST` | HTTP server listen address | `0.0.0.0` |
   | `MIKROTIK_MCP__PORT` | HTTP server listen port | `8000` |
