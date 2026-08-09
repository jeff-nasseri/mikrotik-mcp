"""Multi-device smoke test (issue #44).

Drives the MCP server over the real stdio protocol against the two RouterOS
containers from routeros-docker/docker-compose.yml and proves that a tool call
lands on the device named by the `device` argument.

    docker-compose -f routeros-docker/docker-compose.yml up -d
    python tests/smoke_multi_device.py

Every check is self-establishing: nothing here depends on state left behind by
earlier runs (fresh containers boot with default identities, and RouterOS may
rename NICs across container recreations, so neither can be assumed).
"""

import asyncio
import json
import os
import re
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "src"))

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Matches the compose file: routeros-a -> 2222, routeros-b -> 2223
PASSWORD = os.environ.get("ROUTEROS_PASS", "")
INVENTORY_YAML = f"""\
- title: RouterA
  host: 127.0.0.1
  port: 2222
  username: admin
  password: "{PASSWORD}"
  tags: [lab, primary]
  region: NL
- title: RouterB
  host: 127.0.0.1
  port: 2223
  username: admin
  password: "{PASSWORD}"
  tags: [lab, secondary]
  region: DE
"""

results = []


def check(label, ok, detail=""):
    results.append((label, ok))
    print(f"[{'PASS' if ok else 'FAIL'}] {label}")
    if detail:
        print("        " + str(detail).replace("\n", " ")[:160])


def env(inventory_file):
    e = dict(os.environ)
    e.pop("MIKROTIK_INVENTORY", None)
    e.update({
        "MIKROTIK_INVENTORY_FILE": inventory_file,
        "MIKROTIK_MCP__TRANSPORT": "stdio",
        "PYTHONPATH": os.path.join(REPO, "src"),
    })
    return e


def txt(res):
    return "\n".join(getattr(c, "text", "") for c in res.content)


def macs(list_interfaces_output):
    """Map interface name -> MAC from a list_interfaces response."""
    return dict(re.findall(
        r"(\S+)\s+\S+\s+\d+\s+([0-9A-Fa-f:]{17})", list_interfaces_output
    ))


async def main():
    with tempfile.TemporaryDirectory() as tmp:
        inv_path = os.path.join(tmp, "inventory.yaml")
        with open(inv_path, "w", encoding="utf-8") as fh:
            fh.write(INVENTORY_YAML)

        params = StdioServerParameters(
            command=sys.executable, args=["-m", "mcp_mikrotik.server"],
            env=env(inv_path), cwd=REPO,
        )
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as s:
                await s.initialize()

                tools = (await s.list_tools()).tools
                names = [t.name for t in tools]
                check(f"server exposes {len(tools)} tools incl. list_devices",
                      "list_devices" in names)

                sample = [t for t in tools if t.name == "list_interfaces"][0]
                check("tools advertise a `device` argument",
                      "device" in (sample.input_schema.get("properties") or {}))

                # ── Tool D (inventory loaded from the YAML file) ──────────
                out = txt(await s.call_tool("list_devices", {}))
                check("YAML inventory loaded: list_devices shows both devices",
                      "RouterA" in out and "RouterB" in out, out)
                check("list_devices leaks no credentials",
                      "password" not in out.lower(), out)

                # ── Fingerprint the two boxes ─────────────────────────────
                a = txt(await s.call_tool("list_interfaces", {"device": "RouterA"}))
                b = txt(await s.call_tool("list_interfaces", {"device": "RouterB"}))
                check("command routed to RouterA", "Error" not in a[:20], a)
                check("command routed to RouterB", "Error" not in b[:20], b)

                macs_a, macs_b = macs(a), macs(b)
                distinct = sorted(
                    n for n in macs_a.keys() & macs_b.keys()
                    if macs_a[n] != macs_b[n]
                )
                check("routers expose an interface with distinct MACs (fingerprint)",
                      bool(distinct),
                      f"A={macs_a} B={macs_b}")
                fp = distinct[0] if distinct else None
                parent_a = sorted(n for n in macs_a if n.startswith("ether"))[-1]
                parent_b = sorted(n for n in macs_b if n.startswith("ether"))[-1]

                # ── Write isolation: a VLAN per router, then cross-check ──
                out = txt(await s.call_tool("create_vlan_interface", {
                    "device": "RouterA", "name": "smoke-vlan-a", "vlan_id": 210,
                    "interface": parent_a, "comment": "smoke test"}))
                check("VLAN created on RouterA", "successfully" in out, out)
                out = txt(await s.call_tool("create_vlan_interface", {
                    "device": "RouterB", "name": "smoke-vlan-b", "vlan_id": 220,
                    "interface": parent_b, "comment": "smoke test"}))
                check("VLAN created on RouterB", "successfully" in out, out)

                va = txt(await s.call_tool("list_vlan_interfaces", {"device": "RouterA"}))
                vb = txt(await s.call_tool("list_vlan_interfaces", {"device": "RouterB"}))
                check("RouterA has only its own VLAN",
                      "smoke-vlan-a" in va and "smoke-vlan-b" not in va, va)
                check("RouterB has only its own VLAN",
                      "smoke-vlan-b" in vb and "smoke-vlan-a" not in vb, vb)

                # ── Selection rules ───────────────────────────────────────
                out = txt(await s.call_tool("list_interfaces", {}))
                check("omitting device with >1 device errors and lists choices",
                      "RouterA" in out and "RouterB" in out and "Error" in out, out)

                out = txt(await s.call_tool("list_interfaces", {"device": "Ghost"}))
                check("unknown device errors and lists choices",
                      "Unknown device" in out and "RouterA" in out, out)

                out = txt(await s.call_tool("list_interfaces", {"device": "routera"}))
                check("device matching is case-insensitive",
                      "Error" not in out[:20], out)

                # ── Concurrency: interleaved calls must not cross-talk ────
                if fp:
                    targets = ["RouterA", "RouterB"] * 6
                    outs = [txt(o) for o in await asyncio.gather(
                        *[s.call_tool("list_interfaces", {"device": d})
                          for d in targets]
                    )]
                    got = [macs(o).get(fp) for o in outs]
                    want = [macs_a[fp] if d == "RouterA" else macs_b[fp]
                            for d in targets]
                    check(f"{len(targets)} concurrent calls each reached the right router",
                          got == want, f"want {want[:4]}... got {got[:4]}...")
                    check("no concurrent call errored",
                          not any("Error" in o for o in outs),
                          next((o for o in outs if "Error" in o), ""))

                    serial = [txt(await s.call_tool(
                        "list_interfaces", {"device": "RouterA"}))
                        for _ in range(10)]
                    check("10 back-to-back commands all succeed (no session exhaustion)",
                          all(macs(o).get(fp) == macs_a[fp] for o in serial),
                          next((o for o in serial if macs(o).get(fp) != macs_a[fp]), ""))

                # ── Cleanup (also exercises remove + routing) ─────────────
                out = txt(await s.call_tool("remove_vlan_interface",
                                            {"device": "RouterA", "name": "smoke-vlan-a"}))
                check("VLAN removed from RouterA", "successfully" in out, out)
                out = txt(await s.call_tool("remove_vlan_interface",
                                            {"device": "RouterB", "name": "smoke-vlan-b"}))
                check("VLAN removed from RouterB", "successfully" in out, out)
                va = txt(await s.call_tool("list_vlan_interfaces", {"device": "RouterA"}))
                vb = txt(await s.call_tool("list_vlan_interfaces", {"device": "RouterB"}))
                check("both routers back to baseline",
                      "smoke-vlan" not in va and "smoke-vlan" not in vb)

    print()
    passed = sum(1 for _, ok in results if ok)
    print(f"RESULT: {passed}/{len(results)} smoke checks passed")
    if passed != len(results):
        print("FAILED:", [l for l, ok in results if not ok])
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
