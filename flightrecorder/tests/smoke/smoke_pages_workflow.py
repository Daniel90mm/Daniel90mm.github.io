"""Smoke test: validate the GitHub Pages Hugo workflow contract."""

from __future__ import annotations

import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent


def require(pattern: str, text: str, description: str) -> None:
    if not re.search(pattern, text, re.MULTILINE):
        print(f"ERROR: workflow missing {description}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    workflow_path = REPO_ROOT / ".github" / "workflows" / "hugo.yml"
    if not workflow_path.exists():
        print(f"missing: {workflow_path}", file=sys.stderr)
        sys.exit(1)

    text = workflow_path.read_text(encoding="utf-8")

    require(r"branches:\s*\[main\]", text, "push trigger for main")
    require(r"workflow_dispatch:", text, "manual workflow_dispatch trigger")
    require(r"pages:\s*write", text, "pages: write permission")
    require(r"id-token:\s*write", text, "id-token: write permission")
    require(r"HUGO_VERSION:\s*0\.161\.1", text, "Hugo version 0.161.1")
    require(r"submodules:\s*recursive", text, "recursive submodule checkout")
    require(r"working-directory:\s*\./museum", text, "museum working directory")

    if '--baseURL "${{ steps.pages.outputs.base_url }}/"' not in text:
        print("ERROR: workflow missing Pages baseURL output", file=sys.stderr)
        sys.exit(1)
    if "path: ./museum/public" not in text:
        print("ERROR: workflow missing ./museum/public artifact path", file=sys.stderr)
        sys.exit(1)
    if "actions/deploy-pages" not in text:
        print("ERROR: workflow missing actions/deploy-pages", file=sys.stderr)
        sys.exit(1)

    print("pages workflow smoke test passed")


if __name__ == "__main__":
    main()
