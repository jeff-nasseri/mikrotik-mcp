import logging
import sys

from mcp_mikrotik import config
from mcp_mikrotik.app import mcp
from mcp_mikrotik.config import MikrotikConfig


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

    try:
        mcp.run()
    except KeyboardInterrupt:
        logger.info("MCP MikroTik server stopped by user")
    except Exception as e:
        logger.error(f"Error running MCP MikroTik server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
