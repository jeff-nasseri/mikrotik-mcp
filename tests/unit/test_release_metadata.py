"""The repository owner is written in several places that must agree.

A transfer to another owner changes all of them at once, and the failure mode
is silent or late: the MCP registry refuses a name whose namespace does not
match the publishing repository's owner, and checks that the README of the
PyPI package carries the same name as server.json. These tests fail in the PR
that updates one of them without the others, instead of in the release run.
"""

import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def _read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def _server_json() -> dict:
    return json.loads(_read("server.json"))


def _repo_slug(url: str) -> str:
    match = re.fullmatch(r"https://github\.com/([^/]+/[^/]+?)(?:\.git)?/?", url)
    assert match, f"not a plain github.com repository URL: {url}"
    return match.group(1)


def test_registry_name_matches_the_readme_marker():
    """The registry verifies the package README against server.json's name."""
    marker = re.search(r"<!--\s*mcp-name:\s*(\S+)\s*-->", _read("README.md"))
    assert marker, "README.md lost its <!-- mcp-name: ... --> marker"
    assert marker.group(1) == _server_json()["name"]


def test_registry_namespace_is_the_repository_owner():
    """io.github.<owner>/<repo> is only publishable from <owner>'s repository."""
    server = _server_json()
    slug = _repo_slug(server["repository"]["url"])
    assert server["name"] == f"io.github.{slug}"


def test_package_urls_point_at_the_same_repository():
    pyproject = _read("pyproject.toml")
    slug = _repo_slug(_server_json()["repository"]["url"])
    urls = re.findall(r'^(?:Homepage|Issues|Repository)\s*=\s*"([^"]+)"', pyproject, re.M)
    assert len(urls) == 3, "pyproject.toml [project.urls] changed shape"
    for url in urls:
        assert url.startswith(f"https://github.com/{slug}"), url


@pytest.mark.parametrize("relative", [
    "README.md",
    "SECURITY.md",
    "inventory.example.yml",
    "docs/getting-started/installation.md",
    "docs/reference/inventory/README.md",
    "docs/articles/managing-a-mikrotik-fleet.md",
])
def test_documented_image_path_is_the_one_the_workflow_publishes(relative):
    """docker-publish.yml pushes to ghcr.io/<this repository>, so docs must say so.

    The one deliberate exception is the installation page's "moved" note, which
    names the previous path so users can recognise it.
    """
    slug = _repo_slug(_server_json()["repository"]["url"]).lower()
    text = _read(relative)
    if relative == "docs/getting-started/installation.md":
        text = re.sub(r"> \*\*The image moved.*?\n\n", "", text, flags=re.S)
    for path in re.findall(r"ghcr\.io/([a-z0-9._-]+/[a-z0-9._-]+)", text.lower()):
        assert path == slug, f"{relative} documents ghcr.io/{path}, the workflow publishes ghcr.io/{slug}"
