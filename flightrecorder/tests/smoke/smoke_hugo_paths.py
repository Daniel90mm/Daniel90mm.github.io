"""Smoke test: assert Hugo workflow and site files point at museum/."""

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
    if not re.search(r"working-directory:\s*\./museum", content):
        print("ERROR: Hugo workflow does not use working-directory: ./museum", file=sys.stderr)
        sys.exit(1)

    if not re.search(r"path:\s*\./museum/public", content):
        print("ERROR: Hugo workflow does not upload ./museum/public", file=sys.stderr)
        sys.exit(1)

    hugo_toml = REPO_ROOT / "museum" / "hugo.toml"
    if not hugo_toml.exists():
        print(f"missing: {hugo_toml}", file=sys.stderr)
        sys.exit(1)

    index_template = REPO_ROOT / "museum" / "layouts" / "index.html"
    if not index_template.exists():
        print(f"missing: {index_template}", file=sys.stderr)
        sys.exit(1)

    print("Hugo museum path assertions passed")


if __name__ == "__main__":
    main()
