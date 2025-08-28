"""Integration tests for MikroTik user management using testcontainers."""

import pytest
import time
import os
import uuid
from testcontainers.compose import DockerCompose
import tempfile
import yaml
import subprocess

from mcp_mikrotik.scope.users import (
    mikrotik_add_user,
    mikrotik_list_users,
    mikrotik_remove_user
)


@pytest.fixture(scope="class")
def mikrotik_container():
    """Start a MikroTik RouterOS container using docker-compose."""
    _cleanup_docker_networks()

    with tempfile.TemporaryDirectory() as temp_dir:
        unique_id = str(uuid.uuid4())[:8]
        network_name = f"routeros-net-{unique_id}"
        container_name = f"routeros-test-{unique_id}"

        import random
        subnet_third_octet = random.randint(100, 250)
        subnet = f"10.{subnet_third_octet}.0.0/24"
        gateway = f"10.{subnet_third_octet}.0.1"
        container_ip = f"10.{subnet_third_octet}.0.2"

        ssh_port = random.randint(12000, 15000)
        platform = os.getenv('PLATFORM', 'linux/amd64')

        compose_content = {
            'version': '3.8',
            'services': {
                'routeros': {
                    'image': 'evilfreelancer/docker-routeros:latest',
                    'container_name': container_name,
                    'hostname': container_name,
                    'platform': platform,
                    'privileged': True,
                    'restart': 'no',
                    'environment': {
                        'ROUTEROS_USER': 'admin',
                        'ROUTEROS_PASS': 'mikrotik123',
                        'ROUTEROS_LICENSE': 'true'
                    },
                    'ports': [f'{ssh_port}:22'],
                    'networks': {
                        network_name: {
                            'ipv4_address': container_ip
                        }
                    },
                    'cap_add': ['NET_ADMIN', 'NET_RAW'],
                    'devices': [
                        '/dev/net/tun:/dev/net/tun'
                    ] if os.name != 'nt' else [],
                    'cap_add': [
                        'NET_ADMIN',
                        'NET_RAW'
                    ],
                    'healthcheck': {
                        'test': ['CMD', 'true'],
                        'interval': '5s',
                        'timeout': '3s',
                        'retries': 5,
                        'start_period': '1s'
                    },
                    'restart': 'unless-stopped'
                }
            },
            'networks': {
                network_name: {
                    'driver': 'bridge',
                    'ipam': {'config': [{'subnet': subnet, 'gateway': gateway}]}
                }
            }
        }

        compose_file = os.path.join(temp_dir, 'docker-compose.yml')
        with open(compose_file, 'w') as f:
            yaml.dump(compose_content, f)

        compose = DockerCompose(temp_dir, compose_file_name="docker-compose.yml")

        try:
            compose.start()
            print("Waiting for RouterOS container to start...")
            time.sleep(60)

            _wait_for_mikrotik_ready(ssh_port)
            _initialize_mikrotik_password(ssh_port, "mikrotik123")
            _verify_ssh_auth(ssh_port, "mikrotik123")

            yield {
                'host': 'localhost',
                'port': ssh_port,
                'username': 'admin',
                'password': 'mikrotik123'
            }
        finally:
            try:
                compose.stop()
            except Exception as cleanup_error:
                print(f"Warning: Cleanup failed: {cleanup_error}")


def _cleanup_docker_networks():
    try:
        subprocess.run(['docker', 'network', 'prune', '-f'],
                       capture_output=True, check=False)
        result = subprocess.run(['docker', 'network', 'ls', '--format', '{{.Name}}'],
                                capture_output=True, text=True, check=False)
        if result.stdout:
            existing_networks = result.stdout.strip().split('\n')
            for network in existing_networks:
                if network.startswith('routeros-net-') or network.startswith('tmp'):
                    subprocess.run(['docker', 'network', 'rm', network],
                                   capture_output=True, check=False)
    except Exception:
        pass


def _wait_for_mikrotik_ready(port, max_attempts=30, delay=5):
    import socket
    for attempt in range(max_attempts):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            if result == 0:
                print(f"MikroTik SSH port {port} accessible after {attempt + 1} attempts")
                time.sleep(10)
                return True
        except Exception as e:
            print(f"Attempt {attempt + 1}: Connection failed - {e}")
        time.sleep(delay)
    raise Exception("MikroTik container failed to become ready within timeout period")


def _initialize_mikrotik_password(port, new_password="mikrotik123"):
    import paramiko
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname='localhost', port=port, username='admin',
                    password="", timeout=20, look_for_keys=False, allow_agent=False)
        ssh.exec_command(f'/password set 0 name=admin password={new_password}')
        ssh.close()
        print("Initial MikroTik password set successfully.")
    except Exception as e:
        print(f"Password initialization skipped or failed: {e}")


def _verify_ssh_auth(port, password, max_attempts=10, delay=10):
    import paramiko
    for attempt in range(max_attempts):
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname='localhost', port=port, username='admin',
                        password=password, timeout=10, look_for_keys=False, allow_agent=False)
            stdin, stdout, stderr = ssh.exec_command('/system identity print')
            result = stdout.read().decode()
            ssh.close()
            if result:
                print(f"SSH authentication verified after {attempt + 1} attempts")
                return True
        except Exception as e:
            print(f"SSH auth attempt {attempt + 1}: {e}")
        time.sleep(delay)
    raise Exception("SSH authentication failed after all attempts")


@pytest.fixture(autouse=True)
def setup_mikrotik_config(mikrotik_container, monkeypatch):
    """Patch paramiko.SSHClient.connect to always use correct test port."""
    import paramiko

    orig_connect = paramiko.SSHClient.connect

    def patched_connect(self, hostname, port=22, username=None,
                        password=None, *args, **kwargs):
        return orig_connect(
            self,
            hostname=mikrotik_container['host'],
            port=mikrotik_container['port'],
            username=mikrotik_container['username'],
            password=mikrotik_container['password'],
            *args, **kwargs
        )

    monkeypatch.setattr(paramiko.SSHClient, "connect", patched_connect)


@pytest.mark.integration
class TestMikroTikUserIntegration:
    test_username = "integration_test_user"
    test_password = "test_password_123"

    def test_01_create_user(self, mikrotik_container):
        print(f"\n=== Testing user creation ===")
        result = mikrotik_add_user(
            name=self.test_username,
            password=self.test_password,
            group="read",
            comment="Integration test user"
        )
        assert "failed" not in result.lower()
        assert self.test_username in result

    def test_02_list_users(self, mikrotik_container):
        print(f"\n=== Testing user listing ===")
        result = mikrotik_list_users()
        print(result)
        assert "admin" in result
        assert self.test_username in result

    def test_03_delete_user(self, mikrotik_container):
        print(f"\n=== Testing user deletion ===")
        result = mikrotik_remove_user(self.test_username)
        assert "removed successfully" in result.lower()

        # confirm it's gone
        result = mikrotik_list_users()
        assert self.test_username not in result
