# Contributing to MikroTik MCP

Thank you for your interest in contributing to the MikroTik MCP server! This guide will help you understand the project structure and contribution process.

## Overview

This MCP (Model Context Protocol) server provides tools for managing MikroTik RouterOS devices. Contributors can extend functionality by adding new scopes (feature areas) and their corresponding tools.

## Project Structure

```
src/mcp_mikrotik/
├── scope/          # Core functionality implementations
├── tools/          # MCP tool definitions and handlers
├── config.py       # Configuration (pydantic-settings, CLI args, env vars)
├── connector.py    # SSH connection handling
└── server.py       # MCP server implementation

tests/
├── integration/    # Integration tests using testcontainers
└── unit/          # Unit tests
```

## Contributing New Features

To add a new MikroTik feature/scope to the project, follow these steps:

### 1. Create the Scope Implementation

Navigate to `src/mcp_mikrotik/scope/` and create a new Python file for your feature (e.g., `my_feature.py`).

Your scope file should:
- Import necessary dependencies: `execute_mikrotik_command`, `app_logger`
- Implement functions that execute MikroTik commands
- Follow the existing naming convention: `mikrotik_<action>_<resource>`
- Include comprehensive docstrings with parameter descriptions
- Handle errors gracefully and return meaningful messages

**Example structure** (based on `dhcp.py`):
```python
from typing import List, Optional
from ..connector import execute_mikrotik_command
from ..logger import app_logger

def mikrotik_create_my_resource(
    name: str,
    required_param: str,
    optional_param: Optional[str] = None,
    comment: Optional[str] = None
) -> str:
    """
    Creates a new resource on MikroTik device.
    
    Args:
        name: Name of the resource
        required_param: Required parameter
        optional_param: Optional parameter
        comment: Optional comment
    
    Returns:
        Command output or error message
    """
    app_logger.info(f"Creating resource: name={name}")
    
    # Build MikroTik command
    cmd = f"/my/feature add name={name} param={required_param}"
    
    if optional_param:
        cmd += f" optional-param={optional_param}"
    if comment:
        cmd += f' comment="{comment}"'
    
    result = execute_mikrotik_command(cmd)
    
    if "failure:" in result.lower() or "error" in result.lower():
        return f"Failed to create resource: {result}"
    
    return f"Resource created successfully:\n\n{result}"
```

### 2. Create the Tools Definition

Navigate to `src/mcp_mikrotik/tools/` and create a corresponding tools file (e.g., `my_feature_tools.py`).

Your tools file should:
- Import the scope functions you created
- Import `Tool` from `mcp.types`
- Define MCP tool schemas with proper validation
- Provide handler functions that map arguments to scope functions

**Example structure** (based on `dhcp_tools.py`):
```python
from typing import Dict, Any, List, Callable
from ..scope.my_feature import (
    mikrotik_create_my_resource,
    mikrotik_list_my_resources
)
from mcp.types import Tool

def get_my_feature_tools() -> List[Tool]:
    """Return the list of my feature tools."""
    return [
        Tool(
            name="mikrotik_create_my_resource",
            description="Creates a new resource on MikroTik device",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "required_param": {"type": "string"},
                    "optional_param": {"type": "string"},
                    "comment": {"type": "string"}
                },
                "required": ["name", "required_param"]
            },
        ),
        # Add more tools...
    ]

def get_my_feature_handlers() -> Dict[str, Callable]:
    """Return the handlers for my feature tools."""
    return {
        "mikrotik_create_my_resource": lambda args: mikrotik_create_my_resource(
            args["name"],
            args["required_param"],
            args.get("optional_param"),
            args.get("comment")
        ),
        # Add more handlers...
    }
```

### 3. Register Your Tools

Update `src/mcp_mikrotik/tools/tool_registry.py` to include your new tools:

1. Import your tool functions
2. Add them to the `get_all_tools()` function
3. Add handlers to the `get_all_handlers()` function

### 4. Write Integration Tests

Create comprehensive integration tests in `tests/integration/test_my_feature_integration.py`.

Your test file should:
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
   
   # Test your MCP server
   mcp-inspector python -m mcp_mikrotik.serve
   ```
3. **Manual testing**: Test with a real MikroTik device to ensure commands work correctly

## Development Guidelines

### Code Style
- Follow existing code patterns and naming conventions
- Use type hints for all function parameters and return values
- Include comprehensive docstrings following the existing format
- Handle errors gracefully with meaningful error messages
- Log important operations using `app_logger`

### MikroTik Command Guidelines
- Always validate command syntax against MikroTik documentation
- Use proper escaping for string parameters (wrap in quotes when needed)
- Implement both creation and listing/querying functionality
- Consider implementing filtering options where appropriate
- Test commands on actual RouterOS before implementation

### Testing Requirements
- Write integration tests that cover the main functionality
- Ensure tests are isolated and clean up after themselves
- Use descriptive test names that explain what is being tested
- Include edge cases and error conditions in your tests

## Commit Message Format

This project follows [Conventional Commits](https://www.conventionalcommits.org/) specification:

### Format
```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Types
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation only changes
- `style`: Changes that do not affect the meaning of the code
- `refactor`: A code change that neither fixes a bug nor adds a feature
- `test`: Adding missing tests or correcting existing tests
- `chore`: Changes to the build process or auxiliary tools

### Examples
```
feat(dhcp): add DHCP server creation and management tools

Add comprehensive DHCP server management including:
- Create DHCP servers with configurable options
- List and filter DHCP servers
- Create DHCP networks and pools
- Remove DHCP servers

Includes integration tests with RouterOS container
```

```
fix(firewall): handle special characters in rule comments

Escape special characters when creating firewall rules with comments
to prevent command parsing errors on RouterOS devices
```

```
test(users): expand integration test coverage

Add tests for user group management and permission validation
```

## Submitting a Pull Request

1. **Fork the repository** and create your feature branch from `master`
2. **Implement your changes** following the guidelines above
3. **Run all tests** to ensure nothing is broken
4. **Test with MCP Inspector** to verify tools work correctly
5. **Write descriptive commit messages** following conventional commits
6. **Submit a pull request** with:
   - Clear description of what you've added
   - Reference to any related issues
   - Screenshots or examples if applicable
   - Confirmation that tests pass

## Getting Help

- Check existing scope and tools implementations for reference
- Review the MikroTik RouterOS documentation for command syntax
- Look at existing integration tests for testing patterns
- Open an issue if you need clarification on implementation details

## Code Review Process

All contributions go through code review to ensure:
- Code follows project conventions and patterns
- MikroTik commands are correct and safe
- Tests provide adequate coverage
- Documentation is clear and complete
- Integration with existing codebase is smooth

Thank you for contributing to MikroTik MCP! Your additions help make RouterOS management more accessible through the Model Context Protocol.