# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MikroTik MCP is a Model Context Protocol server that bridges AI assistants with MikroTik RouterOS devices via SSH. Built with Python using FastMCP, paramiko for SSH, and pydantic-settings for configuration.

**Package name:** `mcp-server-mikrotik` | **Entry point:** `mcp_mikrotik.server:main`

## Common Commands

```bash
# Requires Python 3.10+ (tested on 3.10-3.12)

# Install all dependencies (runtime + dev)
uv sync

# Run the server (stdio transport, default)
uv run mcp-server-mikrotik --host <IP> --username admin --password <pass>

# Run all tests
uv run pytest

# Run integration tests only
uv run pytest tests/integration/ -v

# Run a single test file
uv run pytest tests/integration/test_mikrotik_user_integration.py -v

# Skip integration tests
uv run pytest -m "not integration"

# Test with MCP Inspector
npx @modelcontextprotocol/inspector uv run mcp-server-mikrotik
```

## Architecture

### Core Flow

`server.py` (CLI + startup) → `config.py` (pydantic BaseSettings) → `app.py` (FastMCP instance) → `scope/*.py` (tool modules) → `connector.py` (async SSH wrapper) → `mikrotik_ssh_client.py` (paramiko)

### Tool Registration

Scope modules in `src/mcp_mikrotik/scope/` define tools via `@mcp.tool()` decorators. Importing a scope module in `app.py` (lines 22-25) auto-registers its tools with FastMCP — no manual registry needed.

### Tool Annotations (defined in `app.py`)

| Constant | Semantics | Use for |
|---|---|---|
| `READ` | Read-only, idempotent | print, list, get, export |
| `WRITE` | Non-idempotent write | add, create |
| `WRITE_IDEMPOTENT` | Idempotent write | set, update, enable, disable |
| `DESTRUCTIVE` | Idempotent destructive | remove, flush |
| `DANGEROUS` | Non-idempotent destructive | reset, bulk operations |

### Tool Function Pattern

Every tool follows this pattern:
```python
@mcp.tool(name="action_resource", annotations=WRITE)
async def mikrotik_action_resource(ctx: Context, param: str, optional: Optional[str] = None) -> str:
    await ctx.info(f"Doing action")
    cmd = f"/path/command param={param}"
    result = await execute_mikrotik_command(cmd, ctx)
    if "failure:" in result.lower() or "error" in result.lower():
        return f"Failed: {result}"
    return f"Success:\n\n{result}"
```

### Configuration

Pydantic `BaseSettings` with env prefix `MIKROTIK_` (e.g., `MIKROTIK_HOST`, `MIKROTIK_MCP__TRANSPORT`). Supports CLI args, env vars, and nested config via `__` separator. Transports: `stdio` (default), `sse`, `streamable-http`.

## Adding a New Scope

1. Create `src/mcp_mikrotik/scope/my_feature.py` with `@mcp.tool()` decorated async functions
2. Import `mcp`, annotation constants from `..app`, and `execute_mikrotik_command` from `..connector`
3. Add the import to `app.py` scope import block
4. Write integration tests in `tests/integration/test_my_feature_integration.py` using `@pytest.mark.integration`

## Code Conventions

- Tool naming: `mikrotik_<action>_<resource>` (function), `action_resource` (MCP tool name)
- All tool functions are `async`, take `Context` as first param, return `str`
- Use `Literal` types for fixed-value params, `Annotated[..., Field(...)]` for numeric constraints
- Use `ctx.info()`/`ctx.error()` for client-visible logging
- Mask sensitive data (passwords, keys) in output — see `users.py` for pattern
- Error detection: check for `"failure:"` or `"error"` in `result.lower()`

## Commit Messages & Versioning

Uses GitVersion with Conventional Commits. Default on master: **minor** bump.

- `feat:`/`fix:` → minor bump (automatic)
- `+semver: patch` in footer → patch bump
- `+semver: breaking` or `+semver: major` → major bump
- `+semver: none` or `+semver: skip` → no bump

## Testing

Integration tests use `testcontainers` with a MikroTik RouterOS Docker container (`evilfreelancer/docker-routeros`). Docker must be running. Tests call tool functions directly with mocked `Context` objects (`AsyncMock` for `ctx.info`/`ctx.error`). 5-minute timeout for container startup.
