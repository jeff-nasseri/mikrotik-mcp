import asyncio

import pytest

SELECTOR = '[find comment="managed"]'


@pytest.mark.parametrize(
    ("module_name", "function_name", "kwargs", "expected_command"),
    [
        ("routes", "mikrotik_remove_route", {"route_id": SELECTOR}, f"/ip route remove {SELECTOR}"),
        ("dns", "mikrotik_remove_dns_static", {"entry_id": SELECTOR}, f"/ip dns static remove {SELECTOR}"),
        ("firewall_nat", "mikrotik_remove_nat_rule", {"rule_id": SELECTOR}, f"/ip firewall nat remove {SELECTOR}"),
        ("firewall_nat", "mikrotik_move_nat_rule", {"rule_id": SELECTOR, "destination": 2}, f"/ip firewall nat move {SELECTOR} destination=2"),
        ("wireguard", "mikrotik_remove_wireguard_peer", {"peer_id": SELECTOR}, f"/interface wireguard peers remove {SELECTOR}"),
        ("ipv6_firewall_filter", "mikrotik_update_ipv6_filter_rule", {"rule_id": SELECTOR, "disabled": True}, f"/ipv6 firewall filter set {SELECTOR} disabled=yes"),
        ("ipv6_firewall_filter", "mikrotik_remove_ipv6_filter_rule", {"rule_id": SELECTOR}, f"/ipv6 firewall filter remove {SELECTOR}"),
        ("ipv6_firewall_filter", "mikrotik_move_ipv6_filter_rule", {"rule_id": SELECTOR, "destination": 2}, f"/ipv6 firewall filter move {SELECTOR} destination=2"),
    ],
)
def test_write_selector_is_not_rejected_by_count_check(
    module_name, function_name, kwargs, expected_command, ctx, monkeypatch
):
    module = __import__(f"mcp_mikrotik.scope.{module_name}", fromlist=["*"])
    commands = []

    async def execute(command, _ctx, device=None):
        commands.append(command)
        return "chain=forward" if "print detail" in command else ""

    monkeypatch.setattr(module, "execute_mikrotik_command", execute, raising=True)
    result = asyncio.run(getattr(module, function_name)(ctx, **kwargs))

    assert commands[0] == expected_command
    assert not any("count-only" in command for command in commands)
    assert "success" in result or "moved" in result


@pytest.mark.parametrize(
    ("module_name", "function_name", "kwargs"),
    [
        ("routes", "mikrotik_remove_route", {"route_id": "*99"}),
        ("dns", "mikrotik_remove_dns_static", {"entry_id": "*99"}),
        ("firewall_nat", "mikrotik_remove_nat_rule", {"rule_id": "*99"}),
        ("firewall_nat", "mikrotik_move_nat_rule", {"rule_id": "*99", "destination": 2}),
        ("wireguard", "mikrotik_remove_wireguard_peer", {"peer_id": "*99"}),
        ("ipv6_firewall_filter", "mikrotik_update_ipv6_filter_rule", {"rule_id": "*99", "disabled": True}),
        ("ipv6_firewall_filter", "mikrotik_remove_ipv6_filter_rule", {"rule_id": "*99"}),
        ("ipv6_firewall_filter", "mikrotik_move_ipv6_filter_rule", {"rule_id": "*99", "destination": 2}),
    ],
)
def test_write_reports_routeros_no_such_item(module_name, function_name, kwargs, ctx, monkeypatch):
    module = __import__(f"mcp_mikrotik.scope.{module_name}", fromlist=["*"])

    async def absent(command, _ctx, device=None):
        return "no such item (4)"

    monkeypatch.setattr(module, "execute_mikrotik_command", absent, raising=True)
    result = asyncio.run(getattr(module, function_name)(ctx, **kwargs))

    assert "not found" in result
    assert "success" not in result
