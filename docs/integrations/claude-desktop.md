# Usage with Claude Desktop

Add this to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "mikrotik": {
      "command": "uvx",
      "args": ["mcp-server-mikrotik", "--host", "<HOST>", "--username", "<USERNAME>", "--password", "<PASSWORD>", "--port", "22"]
    }
  }
}
```
