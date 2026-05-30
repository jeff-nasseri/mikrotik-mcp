import logging
import os
import sys

from mcp_mikrotik import config
from mcp_mikrotik.app import mcp
from mcp_mikrotik.config import MikrotikConfig


def _warn_if_plaintext_password_in_container(cfg: MikrotikConfig, logger: logging.Logger) -> None:
    """Warn when running inside a container with a plaintext password in the env.

    Environment variables are visible via ``docker inspect``, so a password
    passed this way is exposed to anyone with host access. This is purely a
    nudge — it does not block startup. Credential management is ultimately an
    infrastructure concern (Docker secrets, a vault, restricted host access).
    """
    in_container = os.path.exists("/.dockerenv") or os.environ.get("container") == "docker"
    if in_container and cfg.password:
        logger.warning(
            "Security notice: MikroTik MCP is running inside a container with a "
            "plaintext password set as an environment variable. Environment "
            "variables are visible via 'docker inspect', so anyone with access "
            "to the host can read the credential. In shared or production "
            "environments, manage the secret through your infrastructure "
            "(e.g. Docker secrets or a secrets manager) and restrict host "
            "access. See SECURITY.md."
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
