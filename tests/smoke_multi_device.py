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
import re
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


def ether2_mac(output):
    """Pull ether2's MAC from a list_interfaces response.

    Each container generates its own ether2 MAC, so the MAC in a response
    identifies which router actually produced it.
    """
    m = re.search(r"ether2\s+\S+\s+\d+\s+([0-9A-Fa-f:]{17})", output)
    return m.group(1) if m else ""


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

            # ── Session isolation ─────────────────────────────────────────
            mac_a = ether2_mac(a)
            mac_b = ether2_mac(b)
            check("the routers have distinct ether2 MACs (usable as a fingerprint)",
                  bool(mac_a) and bool(mac_b) and mac_a != mac_b,
                  f"A={mac_a} B={mac_b}")

            # Fire interleaved calls at both routers at once.  These run in
            # parallel threads sharing the inventory, so a pooled or shared
            # SSH client would surface here as cross-talk between devices or
            # as a session dropped out from under a running command.
            targets = ["RouterA", "RouterB"] * 6
            outs = [txt(o) for o in await asyncio.gather(
                *[s.call_tool("list_interfaces", {"device": d}) for d in targets]
            )]
            got = [ether2_mac(o) for o in outs]
            want = [mac_a if d == "RouterA" else mac_b for d in targets]

            check(f"{len(targets)} concurrent calls each reached the right router",
                  got == want, f"want {want[:4]}... got {got[:4]}...")
            check("no concurrent call errored",
                  not any("Error" in o for o in outs),
                  next((o for o in outs if "Error" in o), ""))

            # Connection churn must not exhaust the router's session limit.
            serial = [txt(await s.call_tool("list_interfaces", {"device": "RouterA"}))
                      for _ in range(10)]
            check("10 back-to-back commands all succeed (no session exhaustion)",
                  all(ether2_mac(o) == mac_a for o in serial),
                  next((o for o in serial if ether2_mac(o) != mac_a), ""))

    print()
    passed = sum(1 for _, ok in results if ok)
    print(f"RESULT: {passed}/{len(results)} smoke checks passed")
    if passed != len(results):
        print("FAILED:", [l for l, ok in results if not ok])
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
