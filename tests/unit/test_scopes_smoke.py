import asyncio
import inspect

import pytest

from tests.conftest import FakeExecutor, make_dummy_value


SCOPE_MODULES = [
    "backup",
    "dhcp",
    "dns",
    "firewall_filter",
    "firewall_nat",
    "ip_address",
    "ip_pool",
    "logs",
    "routes",
    "users",
    "vlan",
    "wireless",
]

BROKEN_WRAPPER_FUNCS = {
    # These wrappers call update_* with a positional argument where `ctx` is first.
    # They currently raise TypeError ("multiple values for argument 'ctx'").
    "mikrotik_disable_dns_static",
    "mikrotik_enable_dns_static",
    "mikrotik_disable_filter_rule",
    "mikrotik_enable_filter_rule",
    "mikrotik_disable_nat_rule",
    "mikrotik_enable_nat_rule",
    "mikrotik_disable_route",
    "mikrotik_enable_route",
    "mikrotik_disable_user",
    "mikrotik_enable_user",
}


@pytest.mark.parametrize("module_name", SCOPE_MODULES)
def test_scope_module_functions_return_string(module_name, ctx, monkeypatch):
    module = __import__(f"mcp_mikrotik.scope.{module_name}", fromlist=["*"])

    # Patch module-level executor (each scope imports it directly)
    fake = FakeExecutor()
    monkeypatch.setattr(module, "execute_mikrotik_command", fake, raising=True)

    # Run every coroutine function once with dummy args.
    for name, fn in inspect.getmembers(module, inspect.iscoroutinefunction):
        if not name.startswith("mikrotik_"):
            continue

        sig = inspect.signature(fn)
        kwargs = {}
        for param in sig.parameters.values():
            if param.name == "ctx":
                kwargs["ctx"] = ctx
                continue
            if param.default is not inspect._empty:
                continue
            kwargs[param.name] = make_dummy_value(param)

        if name in BROKEN_WRAPPER_FUNCS:
            with pytest.raises(TypeError):
                asyncio.run(fn(**kwargs))
            continue

        result = asyncio.run(fn(**kwargs))
        assert isinstance(result, str)
