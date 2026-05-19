"""Smoke test: verify PROTOTYPE_WALKTHROUGH.md exists and references expected commands and panels."""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
DOC = REPO / "docs" / "PROTOTYPE_WALKTHROUGH.md"


def main() -> None:
    if not DOC.is_file():
        print(f"missing: {DOC}", file=sys.stderr)
        sys.exit(1)

    text = DOC.read_text(encoding="utf-8")

    for marker in [
        "scripts/dev-prototype.sh",
        "http://127.0.0.1:8000",
        "runtime panel",
        "Create Session",
        "Extract Ideas",
        "Documents",
        "Spaghetti",
        "Budget",
        "Calls",
    ]:
        if marker not in text:
            print(f"missing reference in walkthrough: {marker}", file=sys.stderr)
            sys.exit(1)

    print("prototype walkthrough smoke test passed")


if __name__ == "__main__":
    main()
