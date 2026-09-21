def test_config_defaults():
    from mcp_mikrotik.config import MikrotikConfig

    cfg = MikrotikConfig()
    assert cfg.host == "127.0.0.1"
    assert cfg.port == 22
    assert cfg.username == "admin"
    assert cfg.read_only is False
    assert cfg.sensitive_hiding is False
    assert cfg.mcp.transport == "stdio"
    assert cfg.mcp.host == "0.0.0.0"
    assert cfg.mcp.port == 8000
    assert cfg.mcp.allowed_ips == ""


def test_config_env_overrides(monkeypatch):
    from mcp_mikrotik.config import MikrotikConfig

    monkeypatch.setenv("MIKROTIK_HOST", "10.0.0.10")
    monkeypatch.setenv("MIKROTIK_PORT", "2222")
    monkeypatch.setenv("MIKROTIK_USERNAME", "u")
    monkeypatch.setenv("MIKROTIK_PASSWORD", "p")
    monkeypatch.setenv("MIKROTIK_READ_ONLY", "true")
    monkeypatch.setenv("MIKROTIK_SENSITIVE_HIDING", "true")
    monkeypatch.setenv("MIKROTIK_MCP__TRANSPORT", "sse")
    monkeypatch.setenv("MIKROTIK_MCP__HOST", "127.0.0.1")
    monkeypatch.setenv("MIKROTIK_MCP__PORT", "9000")
    monkeypatch.setenv("MIKROTIK_MCP__ALLOWED_IPS", "192.0.2.10,10.0.0.0/8")

    cfg = MikrotikConfig()
    assert cfg.host == "10.0.0.10"
    assert cfg.port == 2222
    assert cfg.username == "u"
    assert cfg.password == "p"
    assert cfg.read_only is True
    assert cfg.sensitive_hiding is True
    assert cfg.mcp.transport == "sse"
    assert cfg.mcp.host == "127.0.0.1"
    assert cfg.mcp.port == 9000
    assert cfg.mcp.allowed_ips == "192.0.2.10,10.0.0.0/8"


def test_config_rejects_invalid_allowed_ip():
    import pytest
    from pydantic import ValidationError

    from mcp_mikrotik.config import MikrotikConfig

    with pytest.raises(ValidationError, match="invalid IP address or network"):
        MikrotikConfig(mcp={"allowed_ips": "10.0.0.1/8"})
