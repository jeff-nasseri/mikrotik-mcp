"""The repository owner is written in several places that must agree.

A transfer to another owner changes all of them at once, and the failure mode
is silent or late: the MCP registry refuses a name whose namespace does not
match the publishing repository's owner, and checks that the README of the
PyPI package carries the same name as server.json. These tests fail in the PR
that updates one of them without the others, instead of in the release run.
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
INSTALL_DOC = ROOT / "docs" / "getting-started" / "installation.md"


def _read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def _server_json() -> dict:
    return json.loads(_read("server.json"))


def _repo_slug(url: str) -> str:
    match = re.fullmatch(r"https://github\.com/([^/]+/[^/]+?)(?:\.git)?/?", url)
    assert match, f"not a plain github.com repository URL: {url}"
    return match.group(1)


def _slug() -> str:
    return _repo_slug(_server_json()["repository"]["url"])


def test_registry_name_matches_the_readme_marker():
    """The registry verifies the package README against server.json's name."""
    marker = re.search(r"<!--\s*mcp-name:\s*(\S+)\s*-->", _read("README.md"))
    assert marker, "README.md lost its <!-- mcp-name: ... --> marker"
    assert marker.group(1) == _server_json()["name"]


def test_registry_namespace_is_the_repository_owner():
    """io.github.<owner>/<repo> is only publishable from <owner>'s repository."""
    assert _server_json()["name"] == f"io.github.{_slug()}"


def test_package_urls_point_at_the_same_repository():
    urls = dict(re.findall(r'^(Homepage|Issues|Repository)\s*=\s*"([^"]+)"', _read("pyproject.toml"), re.M))
    assert urls == {
        "Homepage": f"https://github.com/{_slug()}",
        "Repository": f"https://github.com/{_slug()}",
        "Issues": f"https://github.com/{_slug()}/issues",
    }


# ---------------------------------------------------------------------------
# the image path in the docs is the one the workflow publishes
# ---------------------------------------------------------------------------

def _files_naming_an_image():
    candidates = [
        *ROOT.glob("*.md"), *ROOT.glob("*.yml"), *ROOT.glob("*.yaml"),
        *(ROOT / "docs").rglob("*.md"), *(ROOT / ".github" / "workflows").glob("*.yml"),
    ]
    return [path for path in candidates if re.search(r"ghcr\.io/", path.read_text(encoding="utf-8"), re.I)]


def test_documented_image_path_is_the_one_the_workflow_publishes():
    """docker-publish.yml pushes to ghcr.io/<this repository>, so every doc must say so.

    The one deliberate exception is the "image moved" note in the install
    guide, which names the previous path so users can recognise it.
    """
    assert "ghcr.io/${{ github.repository }}" in _read(".github/workflows/docker-publish.yml")

    repo_name = _slug().split("/")[1].lower()
    files = _files_naming_an_image()
    assert files, "no file documents the image path any more"

    wrong = []
    for path in files:
        text = path.read_text(encoding="utf-8")
        if path == INSTALL_DOC:
            text = re.sub(r"(?m)^> \*\*The image moved.*(?:\n>.*)*", "", text)
        for found in re.findall(r"ghcr\.io/([a-z0-9][a-z0-9._-]*/[a-z0-9][a-z0-9._-]*)", text.lower()):
            found = found.rstrip(".")
            if found.split("/")[1] == repo_name and found != _slug().lower():
                wrong.append(f"{path.relative_to(ROOT)}: ghcr.io/{found}")
    assert wrong == [], f"documented image path differs from ghcr.io/{_slug()}: {wrong}"


# ---------------------------------------------------------------------------
# the release guard: server.json must name the repository the workflow runs in
# ---------------------------------------------------------------------------

GUARD = ROOT / ".github" / "scripts" / "check_repository_owner.py"


def _run_guard(repository, cwd=ROOT):
    env = {key: value for key, value in os.environ.items() if key != "GITHUB_REPOSITORY"}
    if repository is not None:
        env["GITHUB_REPOSITORY"] = repository
    return subprocess.run(
        [sys.executable, str(GUARD)], cwd=cwd, env=env, capture_output=True, text=True
    )


def _server_json_naming(tmp_path, url):
    (tmp_path / "server.json").write_text(json.dumps({"repository": {"url": url}}), encoding="utf-8")
    return tmp_path


def test_guard_passes_in_the_repository_server_json_names():
    assert _run_guard(_slug()).returncode == 0
    assert _run_guard(_slug().upper()).returncode == 0  # GitHub owners are case-insensitive


def test_guard_stops_a_release_from_any_other_repository():
    """server.json merged before a transfer must not reach PyPI."""
    result = _run_guard("someone-else/mikrotik-mcp")
    assert result.returncode == 1
    assert "::error::server.json names" in result.stdout


def test_guard_accepts_a_git_suffixed_url(tmp_path):
    cwd = _server_json_naming(tmp_path, "https://github.com/wiresage/mikrotik-mcp.git")
    assert _run_guard("wiresage/mikrotik-mcp", cwd).returncode == 0


def test_guard_reports_a_missing_repository_variable_clearly():
    result = _run_guard(None)
    assert result.returncode == 1
    assert "GITHUB_REPOSITORY is not set" in result.stdout


@pytest.mark.parametrize("content", ["{}", '{"repository": {}}', "not json", '{"repository": null}'])
def test_guard_reports_an_unreadable_server_json_as_an_error_not_a_traceback(tmp_path, content):
    (tmp_path / "server.json").write_text(content, encoding="utf-8")
    result = _run_guard("wiresage/mikrotik-mcp", tmp_path)
    assert result.returncode == 1
    assert "::error::server.json has no readable repository.url" in result.stdout
    assert "Traceback" not in result.stderr


@pytest.mark.parametrize("workflow", ["publish.yml", "docker-publish.yml"])
def test_release_workflows_run_the_guard_first_and_every_other_job_waits_for_it(workflow):
    jobs = yaml.safe_load(_read(f".github/workflows/{workflow}"))["jobs"]
    guarded = [
        name for name, job in jobs.items()
        if any("check_repository_owner.py" in str(step.get("run", "")) for step in job["steps"])
    ]
    assert len(guarded) == 1, "the guard must run in exactly one job"

    first = guarded[0]
    steps = jobs[first]["steps"]
    assert "actions/checkout" in steps[0]["uses"]
    assert "check_repository_owner.py" in steps[1]["run"]
    # only forks may skip it; anything else would let a release through unchecked
    assert steps[1].get("if") in (None, "${{ !github.event.repository.fork }}")

    for name, job in jobs.items():
        if name == first:
            continue
        needs = job.get("needs", [])
        needs = [needs] if isinstance(needs, str) else needs
        assert first in needs, f"job '{name}' does not wait for the guard in '{first}'"
