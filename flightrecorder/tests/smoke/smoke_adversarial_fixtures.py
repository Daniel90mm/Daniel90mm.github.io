"""Smoke test: verify adversarial fixture text files are non-empty and cover required categories."""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
FIXTURES_DIR = REPO / "tests" / "fixtures" / "adversarial"

EXPECTED = {"names", "emails", "repo_urls", "course_codes", "mixed", "sensitive"}


def main() -> None:
    if not FIXTURES_DIR.exists():
        print(f"missing: {FIXTURES_DIR}", file=sys.stderr)
        sys.exit(1)

    found: set[str] = set()
    for path in sorted(FIXTURES_DIR.glob("*.txt")):
        stem = path.stem
        found.add(stem)

        size = path.stat().st_size
        if size == 0:
            print(f"{path.name}: file is empty", file=sys.stderr)
            sys.exit(1)

        print(f"{path.name}: {size} bytes, ok")

    missing = EXPECTED - found
    if missing:
        print(f"missing fixture categories: {missing}", file=sys.stderr)
        sys.exit(1)

    print("adversarial fixtures smoke test passed")


if __name__ == "__main__":
    main()
