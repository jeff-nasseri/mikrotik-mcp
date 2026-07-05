"""Contract tests for the uv packaging/release toolchain (T4/T5/T6/T7).

Per the test plan, the release chain (AC-04/06/09) and the block-a-bad-state
guards (AC-03/05/08) are verified at *contract* level: parse the committed
artifact (CI + release workflows, Dockerfile, manifest, lockfile) and assert the
required declaration/flag is present and correctly set — no live process.

These assertions codify the migration's invariants so they cannot silently
regress once the feature ships.
"""

from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]
CI = REPO / ".github" / "workflows" / "ci.yml"
PUBLISH = REPO / ".github" / "workflows" / "publish.yml"
DOCKERFILE = REPO / "Dockerfile"
PYPROJECT = REPO / "pyproject.toml"
UV_LOCK = REPO / "uv.lock"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _load(path: Path) -> dict:
    return yaml.safe_load(_text(path))


def _all_run_steps(workflow: dict) -> str:
    """Concatenate every step's `run:` script across all jobs."""
    chunks = []
    for job in workflow.get("jobs", {}).values():
        for step in job.get("steps", []) or []:
            run = step.get("run")
            if run:
                chunks.append(run)
    return "\n".join(chunks)


def _python_matrices(workflow: dict) -> list[list]:
    out = []
    for job in workflow.get("jobs", {}).values():
        versions = (job.get("strategy", {}) or {}).get("matrix", {}).get("python-version")
        if versions:
            out.append([str(v) for v in versions])
    return out


# --- AC-03 (T4): CI carries a lockfile-drift gate that fails on a stale lock ---

def test_ci_has_lockfile_drift_gate():
    runs = _all_run_steps(_load(CI))
    assert "uv lock --check" in runs, (
        "ci.yml must run `uv lock --check` to block an out-of-date lockfile"
    )


def test_ci_drift_gate_names_the_lockfile_in_plain_language():
    runs = _all_run_steps(_load(CI))
    assert "out of date" in runs.lower() and "uv.lock" in runs, (
        "the drift gate must fail with a plain-language message naming uv.lock as out of date"
    )


# --- AC-01/AC-02: CI proves the 3.10/3.11/3.12 matrix on the frozen lock ---

def test_ci_runs_full_python_matrix_on_frozen_lock():
    wf = _load(CI)
    matrices = _python_matrices(wf)
    assert any({"3.10", "3.11", "3.12"} <= set(m) for m in matrices), (
        f"ci.yml must test Python 3.10/3.11/3.12; found matrices {matrices}"
    )
    runs = _all_run_steps(wf)
    assert "uv sync --frozen" in runs, "ci.yml must provision with `uv sync --frozen`"
    assert "uv run pytest" in runs, "ci.yml must run the suite via `uv run pytest`"


# --- AC-04 (T5): release workflow builds from the frozen lockfile ---

def test_publish_builds_from_frozen_lock():
    runs = _all_run_steps(_load(PUBLISH))
    assert "uv build" in runs, "publish.yml must build the distributable with `uv build`"
    assert "uv lock --check" in runs, (
        "publish.yml must verify the frozen lock (`uv lock --check`) before building, "
        "so the published artifact is produced from the locked-and-tested set"
    )


# --- AC-06: publish is gated on OIDC authorization, no stored token ---

def test_publish_is_gated_on_oidc_trusted_publisher():
    wf = _load(PUBLISH)
    has_id_token = any(
        (job.get("permissions", {}) or {}).get("id-token") == "write"
        for job in wf.get("jobs", {}).values()
    )
    assert has_id_token, "a publish job must request `id-token: write` for OIDC"
    text = _text(PUBLISH)
    assert "pypa/gh-action-pypi-publish" in text, "publish must use the PyPI trusted-publisher action"
    assert "skip-existing" in text, "publish must set skip-existing to tolerate duplicate versions"


# --- AC-06 (T7): release-time tooling is pinned + integrity-verified ---

def test_mcp_publisher_is_pinned_and_checksum_verified():
    text = _text(PUBLISH)
    assert "/latest/download/" not in text, (
        "mcp-publisher must be pinned to a specific release, not pulled from /latest/"
    )
    assert "sha256sum -c" in text, (
        "the downloaded mcp-publisher tarball must be checksum-verified before use"
    )


# --- AC-09 (T6): container build installs from the frozen lock on the pinned base ---

def test_dockerfile_uses_frozen_lock_on_pinned_uv_base():
    text = _text(DOCKERFILE)
    assert "ghcr.io/astral-sh/uv:0.11" in text, "Dockerfile must use the pinned uv base image"
    assert "uv sync --frozen" in text, "Dockerfile must install deps with `uv sync --frozen`"


# --- AC-08: manifest declares the minimum supported Python floor ---

def test_pyproject_declares_python_floor():
    text = _text(PYPROJECT)
    assert 'requires-python = ">=3.10"' in text, (
        "pyproject.toml must declare requires-python >=3.10 so a lower interpreter is refused"
    )


# --- AC-05: every registry-sourced dependency in the lockfile carries a hash ---

def test_uv_lock_records_integrity_hash_for_every_registry_package():
    blocks = _text(UV_LOCK).split("[[package]]")
    registry_pkgs = [b for b in blocks if "source = { registry" in b]
    assert registry_pkgs, "uv.lock should pin registry packages"
    missing = [
        b.splitlines()[1] if len(b.splitlines()) > 1 else b[:40]
        for b in registry_pkgs
        if "sha256:" not in b
    ]
    assert not missing, f"registry packages in uv.lock without an integrity hash: {missing}"
