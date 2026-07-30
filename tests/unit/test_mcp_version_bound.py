"""Regression guard for issue #98.

The `mcp` dependency must be upper-bounded (`<2.0.0`) so that a Docker/pip
install never resolves to mcp 2.x, which removed `mcp.server.fastmcp` and
breaks the server on startup. The floor must be >=1.10.0 — the first release
that ships `mcp.server.transport_security` (used by the HTTP host-allowlist).
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _find_mcp_spec(text: str):
    """Return the raw `mcp` requirement spec (e.g. 'mcp>=1.10.0,<2.0.0') or None."""
    for raw in text.splitlines():
        line = raw.strip().strip(",").strip('"').strip("'")
        # 'mcp' followed by a version operator — excludes mcp-server-mikrotik / mcp_mikrotik
        if re.match(r"^mcp[<>=!~]", line):
            return line
    return None


def test_pyproject_mcp_is_upper_bounded():
    spec = _find_mcp_spec((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    assert spec is not None, "no mcp dependency found in pyproject.toml"
    assert "<2" in spec, (
        f"mcp must be capped below 2.0 (got {spec!r}); mcp 2.x removed "
        "mcp.server.fastmcp and breaks the server (issue #98)."
    )


def test_requirements_mcp_is_upper_bounded():
    spec = _find_mcp_spec((ROOT / "requirements.txt").read_text(encoding="utf-8"))
    assert spec is not None, "no mcp dependency found in requirements.txt"
    assert "<2" in spec, f"mcp must be capped below 2.0 (got {spec!r}); issue #98."


def test_mcp_floor_supports_transport_security():
    # Our code imports mcp.server.transport_security, added in mcp 1.10.0.
    spec = _find_mcp_spec((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    m = re.search(r">=\s*(\d+)\.(\d+)", spec or "")
    assert m, f"mcp spec should declare a lower bound (got {spec!r})"
    major, minor = int(m.group(1)), int(m.group(2))
    assert (major, minor) >= (1, 10), (
        f"mcp floor must be >=1.10.0 (transport_security), got {spec!r}"
    )


def test_pyproject_and_requirements_agree_on_mcp():
    p = _find_mcp_spec((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    r = _find_mcp_spec((ROOT / "requirements.txt").read_text(encoding="utf-8"))
    assert p == r, f"mcp constraint drift: pyproject={p!r} vs requirements={r!r}"
