import asyncio

import pytest
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

from mcp_mikrotik.http_security import IPAllowListMiddleware, parse_allowed_ips


def _request(client_host, headers=None, trusted_proxies=None):
    called = False
    messages = []

    async def app(scope, receive, send):
        nonlocal called
        called = True
        await send({"type": "http.response.start", "status": 204, "headers": []})
        await send({"type": "http.response.body", "body": b""})

    async def receive():
        return {"type": "http.request", "body": b"", "more_body": False}

    async def send(message):
        messages.append(message)

    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": "GET",
        "scheme": "http",
        "path": "/health",
        "raw_path": b"/health",
        "query_string": b"",
        "headers": headers or [],
        "client": (client_host, 12345) if client_host else None,
        "server": ("testserver", 80),
    }
    middleware = IPAllowListMiddleware(app, parse_allowed_ips("192.0.2.10,10.0.0.0/8,2001:db8::/32"))
    if trusted_proxies:
        middleware = ProxyHeadersMiddleware(middleware, trusted_hosts=trusted_proxies)
    asyncio.run(middleware(scope, receive, send))
    return called, messages[0]["status"]


@pytest.mark.parametrize("client_host", ["192.0.2.10", "10.20.30.40", "2001:db8::1", "::ffff:192.0.2.10"])
def test_ip_allowlist_accepts_addresses_and_networks(client_host):
    assert _request(client_host) == (True, 204)


@pytest.mark.parametrize("client_host", ["192.0.2.11", "2001:db9::1", "not-an-ip", None])
def test_ip_allowlist_rejects_other_or_missing_addresses(client_host):
    assert _request(client_host) == (False, 403)


def test_ip_allowlist_uses_forwarded_address_from_trusted_proxy():
    headers = [(b"x-forwarded-for", b"192.0.2.10")]

    assert _request("172.18.0.2", headers, ["172.18.0.2"]) == (True, 204)


def test_ip_allowlist_ignores_spoofed_forwarded_address_from_untrusted_peer():
    headers = [(b"x-forwarded-for", b"192.0.2.10")]

    assert _request("198.51.100.5", headers, ["172.18.0.2"]) == (False, 403)


def test_parse_allowed_ips_rejects_host_bits_in_network():
    with pytest.raises(ValueError):
        parse_allowed_ips("10.0.0.1/8")


@pytest.mark.parametrize("builder", ["sse_app", "streamable_http_app"])
def test_configured_server_applies_allowlist_to_http_apps(monkeypatch, builder):
    from mcp_mikrotik import config
    from mcp_mikrotik.configured_mcp_server import ConfiguredMCPServer

    monkeypatch.setattr(config.mikrotik_config.mcp, "allowed_ips", "192.0.2.10")
    app = getattr(ConfiguredMCPServer("test"), builder)()

    assert any(middleware.cls is IPAllowListMiddleware for middleware in app.user_middleware)


def test_configured_server_leaves_http_unrestricted_by_default():
    from mcp_mikrotik.configured_mcp_server import ConfiguredMCPServer

    app = ConfiguredMCPServer("test").sse_app()

    assert not any(middleware.cls is IPAllowListMiddleware for middleware in app.user_middleware)
