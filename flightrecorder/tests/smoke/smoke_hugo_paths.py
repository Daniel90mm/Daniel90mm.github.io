"""Smoke test: assert Hugo workflow uses working-directory: ./src and hugo.toml exists."""

from __future__ import annotations

import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent


def main() -> None:
    workflow_path = REPO_ROOT / ".github" / "workflows" / "hugo.yml"
    if not workflow_path.exists():
        print(f"missing: {workflow_path}", file=sys.stderr)
        sys.exit(1)

    content = workflow_path.read_text(encoding="utf-8")
    if not re.search(r"working-directory:\s*\./src", content):
        print("ERROR: Hugo workflow does not use working-directory: ./src", file=sys.stderr)
        sys.exit(1)

    hugo_toml = REPO_ROOT / "src" / "hugo.toml"
    if not hugo_toml.exists():
        print(f"missing: {hugo_toml}", file=sys.stderr)
        sys.exit(1)

    print("Hugo path assertions passed")


if __name__ == "__main__":
    main()
