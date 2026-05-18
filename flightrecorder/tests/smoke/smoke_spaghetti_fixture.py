"""Smoke test: check spaghetti fixture frontmatter and required fields."""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
FIXTURES_DIR = REPO / "tests" / "fixtures" / "spaghetti"

REQUIRED_FIELDS = {"idea_id", "source_session", "tags", "status", "match_attempts"}


def main() -> None:
    if not FIXTURES_DIR.exists():
        print(f"missing: {FIXTURES_DIR}", file=sys.stderr)
        sys.exit(1)

    for path in sorted(FIXTURES_DIR.glob("*.md")):
        if path.name == "README.md":
            continue
        text = path.read_text(encoding="utf-8")

        if not text.startswith("---"):
            print(f"{path.name}: missing frontmatter", file=sys.stderr)
            sys.exit(1)

        found = {field for field in REQUIRED_FIELDS if f"{field}:" in text.split("---")[1]}

        missing = REQUIRED_FIELDS - found
        if missing:
            print(f"{path.name}: missing frontmatter fields {missing}", file=sys.stderr)
            sys.exit(1)

        print(f"{path.name}: ok")

    print("spaghetti fixture smoke test passed")


if __name__ == "__main__":
    main()
