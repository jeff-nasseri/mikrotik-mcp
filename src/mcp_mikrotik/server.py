import logging
import sys

from mcp_mikrotik.serve import serve
from mcp_mikrotik.settings.configuration import mikrotik_config


def main():
    """
    Entry point for the MCP MikroTik server when run as a command-line program.
    """
    import argparse
    import asyncio

    parser = argparse.ArgumentParser(description="MCP MikroTik Server")
    parser.add_argument("--host", type=str, help="MikroTik device IP/hostname")
    parser.add_argument("--username", type=str, help="SSH username")
    parser.add_argument("--password", type=str, help="SSH password")
    parser.add_argument("--key-filename", type=str, help="SSH key filename")
    parser.add_argument("--port", type=int, default=22, help="SSH port (default: 22)")

    args = parser.parse_args()

    if args.host:
        mikrotik_config.host = args.host
    if args.username:
        mikrotik_config.username = args.username
    if args.password:
        mikrotik_config.password = args.password
    if args.key_filename:
        mikrotik_config.key_filename = args.key_filename
    if args.port:
        mikrotik_config.port = args.port

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger(__name__)

    logger.info("Starting MCP MikroTik server")
    logger.info(f"Using host: {mikrotik_config.host}")
    logger.info(f"Using username: {mikrotik_config.username}")
    if mikrotik_config.key_filename:
        logger.info(f"Using key from: {mikrotik_config.key_filename}")

    try:
        asyncio.run(serve())
    except KeyboardInterrupt:
        logger.info("MCP MikroTik server stopped by user")
    except Exception as e:
        logger.error(f"Error running MCP MikroTik server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
