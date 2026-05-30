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

## Enabling prompt-injection protection (optional)

RouterOS command-injection protection is always active. To additionally enable
the optional [LLM Guard](../security/prompt-injection.md) prompt-injection
scanner, install the `security` extra (`uvx --from "mcp-server-mikrotik[security]"`)
and add the `env` block below:

```json
{
  "mcpServers": {
    "mikrotik": {
      "command": "uvx",
      "args": ["--from", "mcp-server-mikrotik[security]", "mcp-server-mikrotik", "--host", "<HOST>", "--username", "<USERNAME>", "--password", "<PASSWORD>", "--port", "22"],
      "env": {
        "MIKROTIK_SECURITY__PROMPT_INJECTION_ENABLED": "true",
        "MIKROTIK_SECURITY__PROMPT_INJECTION_THRESHOLD": "0.5"
      }
    }
  }
}
```

| Env variable | Description | Default |
|--------------|-------------|---------|
| `MIKROTIK_SECURITY__PROMPT_INJECTION_ENABLED` | Enable LLM Guard prompt-injection scanning | `false` |
| `MIKROTIK_SECURITY__PROMPT_INJECTION_THRESHOLD` | Detection threshold (0.0–1.0) | `0.5` |
