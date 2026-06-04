# Installation

## MCP Registry (Recommended)

MikroTik MCP is listed on the [MCP Registry](https://registry.modelcontextprotocol.io) — a community-driven catalog of MCP servers. Registry-aware clients (Claude Desktop, VS Code, Cursor) can install it in one command without manual config file editing.

```bash
claude mcp add io.github.jeff-nasseri/mikrotik-mcp
```

The client fetches the server metadata from the registry, installs `mcp-server-mikrotik` from PyPI, and prompts you for the required environment variables (`MIKROTIK_HOST`, `MIKROTIK_USERNAME`, `MIKROTIK_PASSWORD`).

> **PyPI install only:** If your client does not support registry-based install, use one of the manual methods below.

---

## Prerequisites
- Python 3.8+
- MikroTik RouterOS device with API access enabled
- Python dependencies (routeros-api or similar)

## Manual Installation

```bash
# Clone the repository
git clone https://github.com/jeff-nasseri/mikrotik-mcp.git
cd mikrotik-mcp

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

### Official prebuilt image (GitHub Container Registry)

A multi-arch image (`linux/amd64` + `linux/arm64`) is published to GHCR, so you
can pull it directly instead of building from source:

```bash
# Latest release
docker pull ghcr.io/jeff-nasseri/mikrotik-mcp:latest

# A specific version (matches the PyPI / git tag version)
docker pull ghcr.io/jeff-nasseri/mikrotik-mcp:0.10.1
```

| Tag | Points to |
|-----|-----------|
| `latest` | The most recent release |
| `X.Y.Z` | A specific released version (e.g. `0.10.1`), aligned with the PyPI release |
| `X.Y` | The latest patch of a minor line (e.g. `0.10`) |
| `sha-<short>` | A specific commit |

In the examples below, substitute `ghcr.io/jeff-nasseri/mikrotik-mcp:latest` for
`mikrotik-mcp` to use the prebuilt image instead of a locally built one.

### Build from source

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
   | `MIKROTIK_MCP__ALLOWED_HOSTS` | Comma-separated `Host` header allowlist for the HTTP transports (DNS-rebinding protection). Set to your domain behind a reverse proxy; `*` disables the check. | _(empty)_ |
   | `MIKROTIK_MCP__ALLOWED_ORIGINS` | Comma-separated `Origin` header allowlist for the HTTP transports. | _(empty)_ |

### Docker Compose

For a long-running, self-hosted setup, use an HTTP-based transport
(`sse` or `streamable-http`) so MCP clients can connect over the network. The
`stdio` transport is meant for direct IDE integration where the client attaches
to the process's stdin/stdout, not for a standalone background service.

```yaml
services:
  mikrotik-mcp:
    image: ghcr.io/jeff-nasseri/mikrotik-mcp:latest
    container_name: mikrotik-mcp
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      MIKROTIK_HOST: "192.168.88.1"
      MIKROTIK_USERNAME: "admin"
      MIKROTIK_PASSWORD: "change-me"
      MIKROTIK_PORT: "22"                      # SSH port of the RouterOS device
      MIKROTIK_MCP__TRANSPORT: "streamable-http"
      MIKROTIK_MCP__HOST: "0.0.0.0"
      MIKROTIK_MCP__PORT: "8000"
```

```bash
docker compose up -d
```

The server is then reachable at `http://localhost:8000/mcp` (streamable HTTP)
or `http://localhost:8000/sse` (if you set `MIKROTIK_MCP__TRANSPORT: sse`), and
`GET http://localhost:8000/health` returns `OK`.

#### Behind a reverse proxy (or any non-localhost access)

The HTTP transports (`sse` / `streamable-http`) apply DNS-rebinding protection,
which validates the request's `Host` header. When the server is reached on a
custom domain or a non-localhost IP — e.g. through a reverse proxy — you must
allowlist that host, otherwise requests to `/mcp` are rejected with **HTTP 421
"Invalid Host header"** (while `/health` still works, since it is exempt):

```yaml
    environment:
      MIKROTIK_MCP__TRANSPORT: "streamable-http"
      MIKROTIK_MCP__HOST: "0.0.0.0"
      # Allowlist the Host header(s) clients use to reach the server:
      MIKROTIK_MCP__ALLOWED_HOSTS: "mcp.example.com"
      # Allowlist the Origin header(s) for browser-based clients:
      MIKROTIK_MCP__ALLOWED_ORIGINS: "https://app.example.com"
```

Both accept a **comma-separated** list, e.g.:

```yaml
      MIKROTIK_MCP__ALLOWED_HOSTS: "mcp.example.com, mcp.example.com:*, 192.168.1.50:8000"
      MIKROTIK_MCP__ALLOWED_ORIGINS: "https://app.example.com, https://admin.example.com"
```

- Append `:*` to a host (e.g. `mcp.example.com:*`) to allow it on any port.
- Set `MIKROTIK_MCP__ALLOWED_HOSTS: "*"` to disable the host check entirely.
- If you leave it unset on a non-localhost bind, the check is auto-disabled (a
  warning is logged) so the server still works out of the box.

> ⚠️ Passing `MIKROTIK_PASSWORD` as an environment variable makes it visible via
> `docker inspect`. See [SECURITY.md](../../SECURITY.md) for safer alternatives.
