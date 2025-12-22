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

# Run the server
mcp-server-mikrotik
```

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

3. **Configure Cursor IDE:**

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

   **Environment Variables:**
   - `MIKROTIK_HOST`: MikroTik device IP/hostname
   - `MIKROTIK_USERNAME`: SSH username
   - `MIKROTIK_PASSWORD`: SSH password
   - `MIKROTIK_PORT`: SSH port (default: 22)
