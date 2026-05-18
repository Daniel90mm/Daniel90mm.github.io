"""Smoke test: validate project registry fixture structure."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
FIXTURE = REPO / "tests" / "fixtures" / "project_registry" / "projects.json"

REQUIRED = {"name", "ref", "path", "active"}


def main() -> None:
    if not FIXTURE.exists():
        print(f"missing: {FIXTURE}", file=sys.stderr)
        sys.exit(1)

    data = json.loads(FIXTURE.read_text(encoding="utf-8"))

    if not isinstance(data, list):
        print("fixture must be a JSON array", file=sys.stderr)
        sys.exit(1)

    if len(data) < 2:
        print(f"expected at least 2 entries, got {len(data)}", file=sys.stderr)
        sys.exit(1)

    for i, entry in enumerate(data):
        missing = REQUIRED - set(entry.keys())
        if missing:
            print(f"entry {i}: missing fields {missing}", file=sys.stderr)
            sys.exit(1)
        print(f"entry {i}: {entry['ref']} ok")

    print("project registry fixture smoke test passed")


if __name__ == "__main__":
    main()
