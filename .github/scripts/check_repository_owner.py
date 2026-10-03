"""Fail unless server.json names the repository this workflow runs in.

The MCP registry accepts io.github.<owner>/<name> only from a workflow run by
<owner>, and it checks the package README against server.json. When
server.json names another owner (for example when it is merged before a
repository transfer is finished), a release publishes to PyPI and only then
fails at the registry. Running this first stops the release before anything
is built or published.
"""

import json
import os
import sys
from urllib.parse import urlparse


def main() -> int:
    here = os.environ.get("GITHUB_REPOSITORY", "")
    with open("server.json", encoding="utf-8") as handle:
        named = urlparse(json.load(handle)["repository"]["url"]).path.strip("/")

    if named.lower() != here.lower():
        print(
            f"::error::server.json names {named} but this workflow runs in {here}. "
            "Finish the repository transfer first, or update server.json, "
            "pyproject.toml and the README mcp-name marker to match."
        )
        return 1

    print(f"server.json names {named}, matching this repository.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
