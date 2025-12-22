# Inspector

```shell
# Run the inspector against the mcp-server-mikrotik
npx @modelcontextprotocol/inspector uvx mcp-server-mikrotik --host <HOST> --username <USERNAME> --password <PASSWORD> --port 22

# Run the inspector against the mcp-config.json
npm install -g @modelcontextprotocol/inspector
cp mcp-config.json.example mcp-config.json
nano mcp-config.json # Edit the values
mcp-inspector --config mcp-config.json --server mikrotik-mcp-server
```
