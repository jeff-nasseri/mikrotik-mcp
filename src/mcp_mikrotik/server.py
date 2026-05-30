import logging
import os
import sys

from mcp_mikrotik import config
from mcp_mikrotik.app import mcp
from mcp_mikrotik.config import MikrotikConfig


def _warn_if_plaintext_password_in_container(cfg: MikrotikConfig, logger: logging.Logger) -> None:
    """Emit a security warning when a plaintext password is detected inside a container.

    Credential management is an infrastructure concern, not an MCP concern — the
    MCP server cannot solve it on its own. This warning nudges operators toward
    safer alternatives (SSH keys, Docker secrets, a vault) without blocking startup.
    """
    in_container = os.path.exists("/.dockerenv") or os.environ.get("container") == "docker"
    if in_container and cfg.password and not cfg.key_filename:
        logger.warning(
            "Security notice: a plaintext password is set as an environment "
            "variable inside a container, so it is visible to anyone who can run "
            "'docker inspect' on the host. Passing it via --env-file or "
            "'export VAR=$(cat file)' does NOT help — the resolved value still "
            "ends up in the container's environment. To keep it out of "
            "'docker inspect', prefer SSH key-based authentication "
            "(MIKROTIK_KEY_FILENAME) so no password is stored, or inject the "
            "secret via Docker secrets / a secrets manager at runtime. "
            "See SECURITY.md."
        )


def main():
    """
    Entry point for the MCP MikroTik server when run as a command-line program.
    """
    config.mikrotik_config = MikrotikConfig(_cli_parse_args=True)

    logger = logging.getLogger(__name__)

    logger.info("Starting MCP MikroTik server")
    logger.info(f"Using host: {config.mikrotik_config.host}")
    logger.info(f"Using username: {config.mikrotik_config.username}")
    if config.mikrotik_config.key_filename:
        logger.info(f"Using key from: {config.mikrotik_config.key_filename}")

    _warn_if_plaintext_password_in_container(config.mikrotik_config, logger)

    try:
        mcp.settings.host = config.mikrotik_config.mcp.host
        mcp.settings.port = config.mikrotik_config.mcp.port
        mcp.run(transport=config.mikrotik_config.mcp.transport)
    except KeyboardInterrupt:
        logger.info("MCP MikroTik server stopped by user")
    except Exception as e:
        logger.error(f"Error running MCP MikroTik server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
