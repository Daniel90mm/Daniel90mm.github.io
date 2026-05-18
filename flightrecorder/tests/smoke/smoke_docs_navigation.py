"""Smoke test: every docs/ path referenced in NAVIGATION.md exists on disk."""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent


def main() -> None:
    nav_path = REPO / "docs" / "NAVIGATION.md"
    if not nav_path.exists():
        print("NAVIGATION.md not found", file=sys.stderr)
        sys.exit(1)

    text = nav_path.read_text(encoding="utf-8")
    refs = re.findall(r"`(docs/\S+?\.md)`", text)

    ok = 0
    missing = 0
    for ref in refs:
        path = REPO / ref
        if not path.exists():
            print(f"MISSING: {ref}", file=sys.stderr)
            missing += 1
        else:
            ok += 1

    print(f"navigation_links: {ok} ok, {missing} missing")
    if missing:
        print(f"ERROR: {missing} navigation links are broken", file=sys.stderr)
        sys.exit(1)

    print("docs navigation smoke test passed")


if __name__ == "__main__":
    main()
