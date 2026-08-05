"""Guard the `mcp` dependency bound (issues #98 and #100).

#98: an unbounded `mcp>=…` let installs resolve to a new major release that
removed the module the codebase imports, breaking the server on startup.
#100: the codebase was then migrated to the mcp 2.x API (MCPServer).

The lesson from #98 is kept: the dependency must always carry an upper bound
so the *next* major release cannot silently break installs. The floor must be
>=2.0.0, the first release with `mcp.server.mcpserver.MCPServer`.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _find_mcp_spec(text: str):
    """Return the raw `mcp` requirement spec (e.g. 'mcp>=2.0.0,<3.0.0') or None."""
    for raw in text.splitlines():
        line = raw.strip().strip(",").strip('"').strip("'")
        # 'mcp' followed by a version operator — excludes mcp-server-mikrotik / mcp_mikrotik
        if re.match(r"^mcp[<>=!~]", line):
            return line
    return None


def _upper_bound_major(spec: str):
    m = re.search(r"<\s*(\d+)", spec or "")
    return int(m.group(1)) if m else None


def _lower_bound(spec: str):
    m = re.search(r">=\s*(\d+)\.(\d+)", spec or "")
    return (int(m.group(1)), int(m.group(2))) if m else None


def test_pyproject_mcp_has_an_upper_bound():
    spec = _find_mcp_spec((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    assert spec is not None, "no mcp dependency found in pyproject.toml"
    assert _upper_bound_major(spec) is not None, (
        f"mcp must carry an upper bound (got {spec!r}). An unbounded spec let "
        "installs pull a breaking major release (issue #98)."
    )


def test_requirements_mcp_has_an_upper_bound():
    spec = _find_mcp_spec((ROOT / "requirements.txt").read_text(encoding="utf-8"))
    assert spec is not None, "no mcp dependency found in requirements.txt"
    assert _upper_bound_major(spec) is not None, (
        f"mcp must carry an upper bound (got {spec!r}); issue #98."
    )


def test_mcp_floor_is_2x_for_mcpserver_api():
    # The codebase imports mcp.server.mcpserver.MCPServer, which exists only in mcp 2.x.
    spec = _find_mcp_spec((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    lower = _lower_bound(spec)
    assert lower is not None, f"mcp spec should declare a lower bound (got {spec!r})"
    assert lower >= (2, 0), (
        f"mcp floor must be >=2.0.0 (MCPServer API, issue #100), got {spec!r}"
    )


def test_upper_bound_excludes_next_major():
    """The cap must exclude the next major, not merely sit above the floor."""
    spec = _find_mcp_spec((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    lower, upper = _lower_bound(spec), _upper_bound_major(spec)
    assert upper == lower[0] + 1, (
        f"upper bound should exclude the next major (expected <{lower[0] + 1}), got {spec!r}"
    )


def test_pyproject_and_requirements_agree_on_mcp():
    p = _find_mcp_spec((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    r = _find_mcp_spec((ROOT / "requirements.txt").read_text(encoding="utf-8"))
    assert p == r, f"mcp constraint drift: pyproject={p!r} vs requirements={r!r}"


def test_codebase_uses_the_mcp_2x_import_path():
    """No lingering *imports* of the mcp 1.x module removed in 2.0.

    Matches import statements only — a mention of the old path in a comment
    (explaining the migration) is fine.
    """
    old_import = re.compile(
        r"^\s*(?:from\s+mcp\.server\.fastmcp\s+import|import\s+mcp\.server\.fastmcp)",
        re.MULTILINE,
    )
    offenders = [
        str(py.relative_to(ROOT))
        for py in (ROOT / "src").rglob("*.py")
        if old_import.search(py.read_text(encoding="utf-8"))
    ]
    assert not offenders, (
        f"mcp.server.fastmcp was removed in mcp 2.0; still imported by: {offenders}"
    )
