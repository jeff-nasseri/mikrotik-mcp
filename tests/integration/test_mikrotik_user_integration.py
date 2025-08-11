# tests/integration/test_mikrotik_user_integration.py
"""Integration tests for MikroTik user management using testcontainers."""

import pytest
import time
import os
from testcontainers.compose import DockerCompose
from dotenv import load_dotenv
import tempfile
import yaml

# Load environment variables
load_dotenv()

from mcp_mikrotik.scope.users import (
    mikrotik_add_user,
    mikrotik_list_users, 
    mikrotik_remove_user
)


@pytest.fixture(scope="class")
def mikrotik_container():
    """
    Fixture to start a MikroTik RouterOS container using docker-compose.
    This runs once per test class.
    """
    # Create temporary directory for docker-compose files
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create docker-compose.yml content
        compose_content = {
            'version': '3.8',
            'services': {
                'routeros': {
                    'image': 'evilfreelancer/docker-routeros:latest',
                    'container_name': 'routeros-test',
                    'hostname': 'routeros-test',
                    'privileged': True,
                    'environment': {
                        'ROUTEROS_USER': 'admin',
                        'ROUTEROS_PASS': 'admin',
                        'ROUTEROS_LICENSE': 'true'
                    },
                    'ports': [
                        '2222:22',  # SSH port mapped to 2222 to avoid conflicts
                        '8291:8291',  # Winbox
                        '8728:8728'   # API
                    ],
                    'networks': {
                        'routeros-net': {
                            'ipv4_address': '172.20.0.2'
                        }
                    },
                    'cap_add': [
                        'NET_ADMIN',
                        'NET_RAW'
                    ]
                }
            },
            'networks': {
                'routeros-net': {
                    'driver': 'bridge',
                    'ipam': {
                        'config': [{
                            'subnet': '172.20.0.0/24',
                            'gateway': '172.20.0.1'
                        }]
                    }
                }
            }
        }
        
        # Write docker-compose.yml file
        compose_file = os.path.join(temp_dir, 'docker-compose.yml')
        with open(compose_file, 'w') as f:
            yaml.dump(compose_content, f)
        
        # Start the container
        compose = DockerCompose(temp_dir, compose_file_name="docker-compose.yml")
        compose.start()
        
        try:
            # Wait for RouterOS to be ready (it takes some time to boot)
            print("Waiting for RouterOS container to start...")
            time.sleep(60)  # RouterOS needs time to initialize
            
            # Verify container is running and accessible
            _wait_for_mikrotik_ready()
            
            yield {
                'host': 'localhost',
                'port': 2222,
                'username': 'admin', 
                'password': 'admin'
            }
        finally:
            # Clean up
            compose.stop()


def _wait_for_mikrotik_ready(max_attempts=30, delay=5):
    """Wait for MikroTik to be ready to accept SSH connections."""
    import socket
    
    for attempt in range(max_attempts):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex(('localhost', 2222))
            sock.close()
            
            if result == 0:
                print(f"MikroTik SSH port is accessible after {attempt + 1} attempts")
                time.sleep(10)  # Give it a bit more time to fully initialize
                return True
                
        except Exception as e:
            print(f"Attempt {attempt + 1}: Connection failed - {e}")
        
        time.sleep(delay)
    
    raise Exception("MikroTik container failed to become ready within timeout period")


@pytest.fixture(autouse=True)
def setup_mikrotik_config(mikrotik_container, monkeypatch):
    """
    Auto-use fixture to configure MikroTik connection settings for each test.
    """
    # Patch the mikrotik_config to use container settings
    from mcp_mikrotik.settings import configuration
    
    monkeypatch.setattr(configuration.mikrotik_config, 'host', mikrotik_container['host'])
    monkeypatch.setattr(configuration.mikrotik_config, 'port', mikrotik_container['port'])
    monkeypatch.setattr(configuration.mikrotik_config, 'username', mikrotik_container['username'])
    monkeypatch.setattr(configuration.mikrotik_config, 'password', mikrotik_container['password'])
    monkeypatch.setattr(configuration.mikrotik_config, 'key_filename', '')


@pytest.mark.integration
class TestMikroTikUserIntegration:
    """
    Integration tests for MikroTik user management.
    Tests run in order: create -> list -> delete
    """
    
    test_username = "integration_test_user"
    test_password = "test_password_123"
    
    def test_01_create_user(self, mikrotik_container):
        """Test creating a new user on MikroTik device."""
        print(f"\n=== Testing user creation ===")
        print(f"Creating user: {self.test_username}")
        
        result = mikrotik_add_user(
            name=self.test_username,
            password=self.test_password,
            group="read",
            comment="Integration test user"
        )
        
        print(f"Create user result: {result}")
        
        # Verify user was created successfully
        assert "User created successfully" in result or "integration_test_user" in result
        assert "failed" not in result.lower()
        assert "error" not in result.lower()
        
        # Verify password is masked in output
        assert self.test_password not in result
    
    def test_02_list_users(self, mikrotik_container):
        """Test listing users to verify the created user exists."""
        print(f"\n=== Testing user listing ===")
        print("Listing all users...")
        
        result = mikrotik_list_users()
        
        print(f"List users result: {result}")
        
        # Verify the test user appears in the list
        assert "USERS:" in result
        assert self.test_username in result
        assert "admin" in result  # Default admin user should exist
        
        # Test filtering by name
        print(f"Filtering users by name: {self.test_username}")
        filtered_result = mikrotik_list_users(name_filter=self.test_username)
        
        print(f"Filtered result: {filtered_result}")
        
        assert self.test_username in filtered_result
        assert "USERS:" in filtered_result
    
    def test_03_delete_user(self, mikrotik_container):
        """Test deleting the created user."""
        print(f"\n=== Testing user deletion ===")
        print(f"Deleting user: {self.test_username}")
        
        result = mikrotik_remove_user(self.test_username)
        
        print(f"Delete user result: {result}")
        
        # Verify user was deleted successfully
        assert f"User '{self.test_username}' removed successfully" in result
        assert "failed" not in result.lower()
        assert "error" not in result.lower()
        
        # Verify user no longer exists by trying to list it
        print("Verifying user was deleted...")
        list_result = mikrotik_list_users(name_filter=self.test_username)
        
        print(f"Post-deletion list result: {list_result}")
        
        # Should not find the user anymore
        assert "No users found" in list_result or self.test_username not in list_result
    
    def test_04_verify_admin_protection(self, mikrotik_container):
        """Test that admin user cannot be deleted (bonus test)."""
        print(f"\n=== Testing admin user protection ===")
        
        result = mikrotik_remove_user("admin")
        
        print(f"Admin deletion attempt result: {result}")
        
        assert "Cannot remove the admin user" in result


# tests/conftest.py - Add this to your existing conftest.py
"""Updated conftest.py with testcontainers support."""

import pytest
import os
from unittest.mock import Mock
from dotenv import load_dotenv


def pytest_configure(config):
    """Load test environment variables."""
    # Load test-specific env file if it exists
    test_env_path = os.path.join(os.path.dirname(__file__), '.env.test')
    if os.path.exists(test_env_path):
        load_dotenv(test_env_path)
    
    # Load main .env as fallback
    load_dotenv()


# Add integration test marker
def pytest_configure(config):
    config.addinivalue_line(
        "markers", "integration: mark test as integration test that requires external services"
    )


@pytest.fixture(scope="session", autouse=True) 
def setup_test_environment():
    """Set up test environment variables."""
    # Ensure we're using test settings for unit tests
    os.environ.setdefault('USE_MOCK_SSH', 'true')
    os.environ.setdefault('LOG_LEVEL', 'DEBUG')


@pytest.fixture
def mock_ssh_client():
    """Mock SSH client for unit testing."""
    client = Mock()
    client.connect.return_value = True
    client.disconnect.return_value = None
    client.execute_command.return_value = "Mock command output"
    return client


# pytest.ini - Create this file in your project root
"""
[tool:pytest]
markers =
    integration: marks tests as integration tests (deselect with '-m "not integration"')
    slow: marks tests as slow (deselect with '-m "not slow"')

# Test discovery
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# Output options
addopts = 
    -v
    --tb=short
    --strict-markers
    --disable-warnings

# Integration test timeout
timeout = 300

# Minimum version
minversion = 6.0
"""


# requirements-test.txt - Add these testing dependencies
"""
pytest>=7.0.0
pytest-mock>=3.10.0
pytest-asyncio>=0.21.0
pytest-timeout>=2.1.0
testcontainers[compose]>=3.7.0
python-dotenv>=1.0.0
PyYAML>=6.0
"""
