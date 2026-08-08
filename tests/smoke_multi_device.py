"""Multi-device smoke test (issue #44).

Drives the MCP server over the real stdio protocol against the two RouterOS
containers from routeros-docker/docker-compose.yml and proves that a tool call
lands on the device named by the `device` argument.

    docker-compose -f routeros-docker/docker-compose.yml up -d
    python tests/smoke_multi_device.py
"""

import asyncio
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "src"))

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Matches the compose file: routeros-a -> 2222, routeros-b -> 2223
INVENTORY = [
    {"title": "RouterA", "host": "127.0.0.1", "port": 2222,
     "username": "admin", "password": os.environ.get("ROUTEROS_PASS", ""),
     "tags": ["lab", "primary"], "region": "NL"},
    {"title": "RouterB", "host": "127.0.0.1", "port": 2223,
     "username": "admin", "password": os.environ.get("ROUTEROS_PASS", ""),
     "tags": ["lab", "secondary"], "region": "DE"},
]

results = []


def check(label, ok, detail=""):
    results.append((label, ok))
    print(f"[{'PASS' if ok else 'FAIL'}] {label}")
    if detail:
        print("        " + str(detail).replace("\n", " ")[:160])


def env():
    e = dict(os.environ)
    e.update({
        "MIKROTIK_INVENTORY": json.dumps(INVENTORY),
        "MIKROTIK_MCP__TRANSPORT": "stdio",
        "PYTHONPATH": os.path.join(REPO, "src"),
    })
    return e


def txt(res):
    return "\n".join(getattr(c, "text", "") for c in res.content)


async def main():
    params = StdioServerParameters(
        command=sys.executable, args=["-m", "mcp_mikrotik.server"], env=env(), cwd=REPO
    )
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as s:
            await s.initialize()

            tools = (await s.list_tools()).tools
            names = [t.name for t in tools]
            check(f"server exposes {len(tools)} tools incl. list_devices",
                  "list_devices" in names)

            # every device-scoped tool advertises the device argument
            sample = [t for t in tools if t.name == "list_interfaces"][0]
            check("tools advertise a `device` argument",
                  "device" in (sample.input_schema.get("properties") or {}))

            # ── Tool D ────────────────────────────────────────────────────
            out = txt(await s.call_tool("list_devices", {}))
            check("list_devices shows both devices",
                  "RouterA" in out and "RouterB" in out, out)
            check("list_devices leaks no credentials",
                  "password" not in out.lower(), out)

            # ── Targeting ─────────────────────────────────────────────────
            a = txt(await s.call_tool("list_interfaces", {"device": "RouterA"}))
            check("command routed to RouterA", "Failed to connect" not in a and "Error" not in a[:20], a)

            b = txt(await s.call_tool("list_interfaces", {"device": "RouterB"}))
            check("command routed to RouterB", "Failed to connect" not in b and "Error" not in b[:20], b)

            # Decisive proof: each router carries a distinct system identity, so
            # exporting it shows which box actually executed the command.
            ia = txt(await s.call_tool("export_section",
                                       {"device": "RouterA", "section": "system identity"}))
            ib = txt(await s.call_tool("export_section",
                                       {"device": "RouterB", "section": "system identity"}))
            check("RouterA reports its own identity", "RouterA-NL" in ia, ia)
            check("RouterB reports its own identity", "RouterB-DE" in ib, ib)
            check("the two devices are genuinely different hosts",
                  "RouterB-DE" not in ia and "RouterA-NL" not in ib)

            # ── Selection rules ───────────────────────────────────────────
            out = txt(await s.call_tool("list_interfaces", {}))
            check("omitting device with >1 device errors and lists choices",
                  "RouterA" in out and "RouterB" in out and "Error" in out, out)

            out = txt(await s.call_tool("list_interfaces", {"device": "Ghost"}))
            check("unknown device errors and lists choices",
                  "Unknown device" in out and "RouterA" in out, out)

            out = txt(await s.call_tool("list_interfaces", {"device": "routera"}))
            check("device matching is case-insensitive", "Failed to connect" not in out, out)

    print()
    passed = sum(1 for _, ok in results if ok)
    print(f"RESULT: {passed}/{len(results)} smoke checks passed")
    if passed != len(results):
        print("FAILED:", [l for l, ok in results if not ok])
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
