"""Smoke test: check project document fixtures include all standard sections."""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
FIXTURES_DIR = REPO / "tests" / "fixtures" / "documents"

PROJECT_SECTIONS = {
    "Problem", "Current state", "Decisions made",
    "Open questions", "TODOs", "Ideas",
}


def main() -> None:
    if not FIXTURES_DIR.exists():
        print(f"missing: {FIXTURES_DIR}", file=sys.stderr)
        sys.exit(1)

    for path in sorted(FIXTURES_DIR.glob("*.md")):
        if path.name == "README.md":
            continue
        text = path.read_text(encoding="utf-8")
        found = {section for section in PROJECT_SECTIONS if f"## {section}" in text}

        missing = PROJECT_SECTIONS - found
        if missing:
            print(f"{path.name}: missing sections {missing}", file=sys.stderr)
            sys.exit(1)

        print(f"{path.name}: all sections present")

    print("project document fixture smoke test passed")


if __name__ == "__main__":
    main()
