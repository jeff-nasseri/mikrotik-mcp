"""Integration tests for MikroTik user management using testcontainers."""

import asyncio
import os
import subprocess
import time
from unittest.mock import AsyncMock, MagicMock

import pytest

pytest.importorskip("testcontainers.core.container")
from testcontainers.core.container import DockerContainer

from mcp_mikrotik import config as mikrotik_config_module
from mcp_mikrotik.scope.users import mikrotik_add_user, mikrotik_list_users, mikrotik_remove_user


def _make_ctx():
    """Create a mock FastMCP Context for direct tool function calls."""
    ctx = MagicMock()
    ctx.info = AsyncMock()
    ctx.debug = AsyncMock()
    ctx.warning = AsyncMock()
    ctx.error = AsyncMock()
    return ctx


def _docker_available() -> bool:
    try:
        result = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            text=True,
            check=False,
        )
        return result.returncode == 0
    except Exception:
        return False


@pytest.fixture(scope="class")
def mikrotik_container():
    """Start a MikroTik RouterOS container."""
    if not _docker_available():
        pytest.skip("Docker is not available/running; skipping integration tests.")

    container = (
        DockerContainer("evilfreelancer/docker-routeros:latest")
        .with_env("ROUTEROS_USER", "admin")
        .with_env("ROUTEROS_PASS", "mikrotik123")
        .with_env("ROUTEROS_LICENSE", "true")
        .with_exposed_ports(22)
        .with_kwargs(privileged=True, cap_add=["NET_ADMIN", "NET_RAW"])
    )

    if os.name != "nt":
        container = container.with_kwargs(devices=["/dev/net/tun:/dev/net/tun"])

    try:
        container.start()
        host = container.get_container_host_ip()
        port = int(container.get_exposed_port(22))

        _wait_for_mikrotik_ready(host, port)
        _ensure_mikrotik_password(host, port, "mikrotik123")

        yield {
            "host": host,
            "port": port,
            "username": "admin",
            "password": "mikrotik123",
        }
    finally:
        try:
            container.stop()
        except Exception as cleanup_error:
            print(f"Warning: Cleanup failed: {cleanup_error}")


def _wait_for_mikrotik_ready(host: str, port: int, max_attempts: int = 60, delay: int = 5):
    import socket
    for attempt in range(max_attempts):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((host, port))
            sock.close()
            if result == 0:
                print(f"MikroTik SSH port {port} accessible after {attempt + 1} attempts")
                return True
        except Exception as e:
            print(f"Attempt {attempt + 1}: Connection failed - {e}")
        time.sleep(delay)
    raise Exception("MikroTik container failed to become ready within timeout period")


def _try_set_mikrotik_password(host: str, port: int, new_password: str) -> bool:
    import paramiko
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(
            hostname=host,
            port=port,
            username="admin",
            password="",
            timeout=20,
            look_for_keys=False,
            allow_agent=False,
        )
        ssh.exec_command(f'/password set 0 name=admin password={new_password}')
        ssh.close()
        print("Initial MikroTik password set successfully.")
        return True
    except Exception:
        return False


def _verify_ssh_auth(host: str, port: int, password: str, max_attempts: int = 10, delay: int = 10) -> bool:
    import paramiko
    for attempt in range(max_attempts):
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(
                hostname=host,
                port=port,
                username="admin",
                password=password,
                timeout=10,
                look_for_keys=False,
                allow_agent=False,
            )
            stdin, stdout, stderr = ssh.exec_command('/system identity print')
            result = stdout.read().decode()
            ssh.close()
            if result:
                print(f"SSH authentication verified after {attempt + 1} attempts")
                return True
        except Exception as e:
            print(f"SSH auth attempt {attempt + 1}: {e}")
        time.sleep(delay)
    return False


@pytest.fixture(autouse=True)
def setup_mikrotik_config(mikrotik_container, monkeypatch):
    """Point the library config at the integration-test container."""
    monkeypatch.setattr(mikrotik_config_module.mikrotik_config, "host", mikrotik_container["host"], raising=False)
    monkeypatch.setattr(mikrotik_config_module.mikrotik_config, "port", mikrotik_container["port"], raising=False)
    monkeypatch.setattr(mikrotik_config_module.mikrotik_config, "username", mikrotik_container["username"], raising=False)
    monkeypatch.setattr(mikrotik_config_module.mikrotik_config, "password", mikrotik_container["password"], raising=False)
    monkeypatch.setattr(mikrotik_config_module.mikrotik_config, "key_filename", None, raising=False)


def _ensure_mikrotik_password(host: str, port: int, password: str) -> None:
    # Prefer the configured password; fall back to setting from empty password if needed.
    if _verify_ssh_auth(host, port, password, max_attempts=12, delay=5):
        return
    if _try_set_mikrotik_password(host, port, password):
        if _verify_ssh_auth(host, port, password, max_attempts=12, delay=5):
            return
    raise Exception("Unable to authenticate to MikroTik container over SSH")


@pytest.mark.integration
class TestMikroTikUserIntegration:
    test_username = "integration_test_user"
    test_password = "test_password_123"

    def test_01_create_user(self, mikrotik_container):
        print(f"\n=== Testing user creation ===")
        ctx = _make_ctx()
        result = asyncio.run(mikrotik_add_user(
            name=self.test_username,
            password=self.test_password,
            ctx=ctx,
            group="read",
            comment="Integration test user"
        ))
        assert "failed" not in result.lower()
        assert self.test_username in result

    def test_02_list_users(self, mikrotik_container):
        print(f"\n=== Testing user listing ===")
        ctx = _make_ctx()
        result = asyncio.run(mikrotik_list_users(ctx=ctx))
        print(result)
        assert "admin" in result
        assert self.test_username in result

    def test_03_delete_user(self, mikrotik_container):
        print(f"\n=== Testing user deletion ===")
        ctx = _make_ctx()
        result = asyncio.run(mikrotik_remove_user(ctx=ctx, name=self.test_username))
        assert "removed successfully" in result.lower()

        # confirm it's gone
        result = asyncio.run(mikrotik_list_users(ctx=ctx))
        assert self.test_username not in result
