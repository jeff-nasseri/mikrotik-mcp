# Contributing to MikroTik MCP

Thank you for your interest in contributing to the MikroTik MCP server! This guide will help you understand the project structure and contribution process.

## Overview

This MCP (Model Context Protocol) server provides tools for managing MikroTik RouterOS devices. Contributors can extend functionality by adding new scopes (feature areas) and their corresponding tools.

## Project Structure

```
src/mcp_mikrotik/
├── scope/          # Feature modules — each file registers MCP tools via decorators
├── app.py          # FastMCP instance and ToolAnnotation constants
├── config.py       # Configuration (pydantic-settings, CLI args, env vars)
├── connector.py    # SSH connection handling
├── server.py       # Entry point — imports scopes, starts the server
└── mikrotik_ssh_client.py  # Low-level SSH client

tests/
├── integration/    # Integration tests using testcontainers
└── unit/          # Unit tests
```

## Contributing New Features

To add a new MikroTik feature/scope to the project, follow these steps:

### 1. Create the Scope Implementation

Navigate to `src/mcp_mikrotik/scope/` and create a new Python file for your feature (e.g., `my_feature.py`).

Your scope file should:
- Import `mcp` and the appropriate `ToolAnnotations` constant from `..app`
- Import `execute_mikrotik_command` from `..connector`
- Register tools using `@mcp.tool()` decorators with annotations
- Follow the existing naming convention: `mikrotik_<action>_<resource>`
- Use type hints for all parameters (including `Literal` for fixed-value params)
- Handle errors gracefully and return meaningful messages

**Example structure** (based on `dhcp.py`):
```python
from typing import Optional
from mcp.server.fastmcp import Context
from ..connector import execute_mikrotik_command
from ..app import mcp, READ, WRITE

@mcp.tool(name="create_my_resource", annotations=WRITE)
async def mikrotik_create_my_resource(
    ctx: Context,
    name: str,
    required_param: str,
    optional_param: Optional[str] = None,
    comment: Optional[str] = None
) -> str:
    """Creates a new resource on MikroTik device."""
    await ctx.info(f"Creating resource: name={name}")

    cmd = f"/my/feature add name={name} param={required_param}"

    if optional_param:
        cmd += f" optional-param={optional_param}"
    if comment:
        cmd += f' comment="{comment}"'

    result = await execute_mikrotik_command(cmd, ctx)

    if "failure:" in result.lower() or "error" in result.lower():
        return f"Failed to create resource: {result}"

    return f"Resource created successfully:\n\n{result}"
```

### 2. Choose the Right Tool Annotation

Import the appropriate annotation constant from `app.py` and pass it via `@mcp.tool(annotations=...)`:

| Constant | Use for |
|---|---|
| `READ` | Read-only queries (print, list, get, export) |
| `WRITE` | Non-idempotent writes (add, create) |
| `WRITE_IDEMPOTENT` | Idempotent writes (set, update, enable, disable) |
| `DESTRUCTIVE` | Idempotent destructive operations (remove, flush) |
| `DANGEROUS` | Non-idempotent destructive operations (reset, bulk create) |

### 3. Register Your Scope

Update `src/mcp_mikrotik/app.py` to import your new scope module:

```python
from mcp_mikrotik.scope import (  # noqa: F401
    backup, dhcp, dns, firewall_filter, firewall_nat,
    ip_address, ip_pool, logs, my_feature, routes, users, vlan, wireless,
)
```

The import triggers the `@mcp.tool()` decorators, which automatically register your tools with the MCP server. No manual registry is needed.

### 4. Write Tests

Create tests in `tests/` for unit tests or `tests/integration/` for integration tests.

Integration tests should:
- Use testcontainers to spin up a real MikroTik RouterOS container
- Follow the existing test structure and naming conventions
- Test complete workflows (create, read, update, delete operations)
- Include proper cleanup to ensure tests are isolated
- Use the `@pytest.mark.integration` decorator

**Example structure** (based on `test_mikrotik_user_integration.py`):
```python
"""Integration tests for MikroTik my feature using testcontainers."""

import pytest
from mcp_mikrotik.scope.my_feature import (
    mikrotik_create_my_resource,
    mikrotik_list_my_resources
)

@pytest.mark.integration
class TestMikroTikMyFeatureIntegration:
    def test_01_create_resource(self, mikrotik_container):
        result = mikrotik_create_my_resource(
            name="test_resource",
            required_param="test_value"
        )
        assert "failed" not in result.lower()
        assert "test_resource" in result

    def test_02_list_resources(self, mikrotik_container):
        result = mikrotik_list_my_resources()
        assert "test_resource" in result
```

### 5. Test Your Implementation

Before submitting, ensure your implementation works:

1. **Run integration tests**: `pytest tests/integration/test_my_feature_integration.py -v`
2. **Use MCP Inspector**: Test your tools interactively using the [MCP Inspector](https://github.com/modelcontextprotocol/inspector)
   ```bash
   # Install MCP Inspector
   npm install -g @modelcontextprotocol/inspector

   # Test your MCP server (stdio transport)
   mcp-inspector python -m mcp_mikrotik.server
   ```
3. **Manual testing**: Test with a real MikroTik device to ensure commands work correctly

## Transport Modes

The server supports three transport modes:

- **stdio** (default) — standard input/output, used by most MCP clients
- **sse** — Server-Sent Events over HTTP (exposes `/health` endpoint)
- **streamable-http** — HTTP with streaming support (exposes `/health` endpoint)

Configure via CLI (`--mcp.transport`) or environment variable (`MIKROTIK_MCP__TRANSPORT`).

## Development Guidelines

### Code Style
- Follow existing code patterns and naming conventions
- Use type hints for all function parameters and return values
- Use `Literal` types for parameters with a fixed set of valid values
- Use `Annotated[..., Field(...)]` for numeric constraints (e.g., VLAN IDs)
- Handle errors gracefully with meaningful error messages
- Log important operations using `ctx.info()` / `ctx.error()` for client-visible logging

### MikroTik Command Guidelines
- Always validate command syntax against MikroTik documentation
- Use proper escaping for string parameters (wrap in quotes when needed)
- Implement both creation and listing/querying functionality
- Consider implementing filtering options where appropriate
- Test commands on actual RouterOS before implementation

### Testing Requirements
- Write tests that cover the main functionality
- Ensure tests are isolated and clean up after themselves
- Use descriptive test names that explain what is being tested
- Include edge cases and error conditions in your tests

## Commit Message Format and Versioning

This project uses [GitVersion](https://gitversion.net/) for automatic semantic versioning based on commit messages. We follow [Conventional Commits](https://www.conventionalcommits.org/) specification for commit message structure.

### Automatic Version Bumping

Your commit messages directly control which version number gets incremented when merged to `master`.

**Default behavior on master branch:** Any commit without an explicit `+semver:` tag will increment the **minor** version by default.

#### Quick Reference Table

| Commit Type | Example | Version Bump | Notes |
|-------------|---------|--------------|-------|
| `feat:` | `feat: add new tool` | **Minor** (0.2.0 → 0.3.0) | Automatic |
| `fix:` | `fix: resolve bug` | **Minor** (0.2.0 → 0.3.0) | Automatic |
| Any commit on master | `docs: update README` | **Minor** (0.2.0 → 0.3.0) | Default behavior |
| `+semver: breaking` | `feat: redesign API`<br>`+semver: breaking` | **Major** (0.2.0 → 1.0.0) | Explicit tag required |
| `+semver: major` | `refactor: breaking change`<br>`+semver: major` | **Major** (0.2.0 → 1.0.0) | Explicit tag required |
| `+semver: patch` | `docs: fix typo`<br>`+semver: patch` | **Patch** (0.2.0 → 0.2.1) | Explicit tag required |
| `+semver: fix` | `style: format code`<br>`+semver: fix` | **Patch** (0.2.0 → 0.2.1) | Explicit tag required |
| `+semver: none` | `ci: update workflow`<br>`+semver: none` | **No bump** | Explicit tag required |
| `+semver: skip` | `test: add tests`<br>`+semver: skip` | **No bump** | Explicit tag required |

#### Minor Version Bump (0.2.0 → 0.3.0)
These commit types will increment the **minor** version:

```bash
# Using conventional commit prefixes (automatically triggers minor bump)
feat: add wireless interface management tools
feat(dhcp): implement DHCP network configuration
fix: resolve connection timeout in SSH client
fix(firewall): correct rule ordering logic

# Any commit without explicit +semver tag (defaults to minor on master)
docs: update installation guide
refactor: reorganize scope modules
chore: update dependencies

# Using explicit semver tags
docs: update installation guide

+semver: minor

# Or
chore: update dependencies

+semver: feature
```

**When to use:** New features, bug fixes, enhancements, or any backward-compatible changes. This is the **default** for commits on the master branch.

#### Major Version Bump (0.2.0 → 1.0.0)
These commit messages will increment the **major** version:

```bash
# Using explicit semver tags (required for major bumps)
refactor: redesign API authentication system

+semver: breaking

# Or
feat: migrate to new MikroTik API protocol

+semver: major
```

**When to use:** Breaking changes, API redesigns, or incompatible updates.

#### Patch Version Bump (0.2.0 → 0.2.1)
These commit messages will increment the **patch** version:

```bash
# Using explicit semver tags
docs: fix typo in README

+semver: patch

# Or
style: format code with black

+semver: fix
```

**When to use:** Documentation updates, code formatting, or minor non-functional changes.

#### No Version Bump
Prevent any version increment:

```bash
ci: update GitHub Actions workflow

+semver: none

# Or
test: add missing unit tests

+semver: skip
```

**When to use:** CI/CD changes, test updates, or internal tooling changes that don't affect the published package.

### Commit Message Structure

```
<type>[optional scope]: <description>

[optional body]

[optional footer with +semver tag]
```

#### Types
- `feat`: A new feature (triggers minor bump)
- `fix`: A bug fix (triggers minor bump)
- `docs`: Documentation only changes
- `style`: Code formatting, missing semicolons, etc.
- `refactor`: Code change that neither fixes a bug nor adds a feature
- `perf`: Performance improvement
- `test`: Adding or updating tests
- `chore`: Build process, tooling, or dependency updates
- `ci`: CI/CD configuration changes

#### Scopes (optional)
Use scopes to indicate which area of the codebase is affected:
- `dhcp`, `dns`, `firewall`, `wireless`, `users`, `backup`, etc.
- `api`, `cli`, `config`, `docs`

### Examples

#### Example 1: Adding a New Feature
```bash
git commit -m "feat(wireless): add WPA3 security profile support

Implement WPA3-Personal and WPA3-Enterprise security profiles
for wireless interfaces. Includes validation and migration path
from WPA2."
```
**Result:** Minor version bump (e.g., 0.2.0 → 0.3.0)

#### Example 2: Bug Fix
```bash
git commit -m "fix(dns): handle empty DNS cache gracefully

Prevent crash when querying DNS cache on devices with
no cached entries. Returns empty list instead of error."
```
**Result:** Minor version bump (e.g., 0.2.0 → 0.3.0)

#### Example 3: Breaking Change
```bash
git commit -m "feat(api): migrate to FastMCP async patterns

BREAKING CHANGE: All tool functions now require Context parameter
as first argument. Legacy synchronous API is removed.

+semver: breaking"
```
**Result:** Major version bump (e.g., 0.2.0 → 1.0.0)

#### Example 4: Documentation Update
```bash
git commit -m "docs: improve DHCP configuration examples

Add complete working examples for DHCP server setup
including network configuration and pool management.

+semver: patch"
```
**Result:** Patch version bump (e.g., 0.2.0 → 0.2.1)

#### Example 5: CI/CD Change
```bash
git commit -m "ci: add Python 3.13 to test matrix

+semver: none"
```
**Result:** No version bump

### Version Release Process

1. **Commits are merged to `master`** → GitVersion calculates the new version
2. **GitHub Actions workflow runs** → Builds and publishes to PyPI
3. **Git tag is created automatically** → Version tag (e.g., `v0.3.0`) is pushed
4. **GitHub Release is generated** → With changelog and artifacts

You don't need to manually tag releases or update version numbers in code—GitVersion and CI/CD handle this automatically based on your commit messages.

### Best Practices

1. **Be intentional with commit types** — `feat:` and `fix:` trigger **minor** version bumps automatically
2. **Default is minor bump** — Any commit to master without `+semver:` tags will bump the minor version
3. **Use `+semver: none` or `+semver: skip`** — To prevent version bumps for CI/CD, tests, or internal changes
4. **Use `+semver: patch`** — For documentation, formatting, or minor non-functional changes that should only bump patch version
5. **Use `+semver: breaking` or `+semver: major`** — For breaking changes that require major version bump
6. **Write clear commit messages** — They become part of the release history and changelog
7. **One logical change per commit** — Makes version history clearer and easier to track
8. **Test before committing** — Failed builds don't get published

## Submitting a Pull Request

1. **Fork the repository** and create your feature branch from `master`
2. **Implement your changes** following the guidelines above
3. **Run all tests** to ensure nothing is broken
4. **Test with MCP Inspector** to verify tools work correctly
5. **Write descriptive commit messages** following the format above
6. **Submit a pull request** with:
   - Clear description of what you've added
   - Reference to any related issues
   - Screenshots or examples if applicable
   - Confirmation that tests pass
   - Indication of version bump impact (minor, major, patch, or none)

## Getting Help

- Check existing scope implementations for reference
- Review the MikroTik RouterOS documentation for command syntax
- Look at existing tests for testing patterns
- Open an issue if you need clarification on implementation details

## Code Review Process

All contributions go through code review to ensure:
- Code follows project conventions and patterns
- MikroTik commands are correct and safe
- Tests provide adequate coverage
- Documentation is clear and complete
- Integration with existing codebase is smooth
- Commit messages follow versioning guidelines

Thank you for contributing to MikroTik MCP! Your additions help make RouterOS management more accessible through the Model Context Protocol.