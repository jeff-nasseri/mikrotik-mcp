try:
    from importlib.metadata import version, PackageNotFoundError

    __version__ = version("mcp-server-mikrotik")
except PackageNotFoundError:
    __version__ = "0.0.0"  # fallback when running from source without install
