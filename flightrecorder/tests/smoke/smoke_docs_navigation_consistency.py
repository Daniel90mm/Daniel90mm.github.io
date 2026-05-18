"""Smoke test: verify NAVIGATION.md references every docs/*.md file, no duplicates."""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
DOCS_DIR = REPO / "docs"
NAV_PATH = DOCS_DIR / "NAVIGATION.md"


def main() -> None:
    if not NAV_PATH.exists():
        print(f"missing: {NAV_PATH}", file=sys.stderr)
        sys.exit(1)

    doc_files = sorted(p.relative_to(REPO).as_posix() for p in DOCS_DIR.glob("*.md"))
    doc_files = [f for f in doc_files if f != "docs/NAVIGATION.md"]

    nav_text = NAV_PATH.read_text(encoding="utf-8")

    table_refs: list[str] = []
    seen: set[str] = set()

    for m in re.finditer(r"`(docs/\S+?\.md)`", nav_text):
        ref = m.group(1)
        table_refs.append(ref)
        if ref in seen:
            print(f"duplicate navigation entry: {ref}", file=sys.stderr)
            sys.exit(1)
        seen.add(ref)

    missing = [f for f in doc_files if f not in seen]
    if missing:
        print(f"docs files not in NAVIGATION.md: {missing}", file=sys.stderr)
        sys.exit(1)

    orphaned = [r for r in table_refs if r not in doc_files]
    if orphaned:
        print(f"NAVIGATION.md references missing files: {orphaned}", file=sys.stderr)
        sys.exit(1)

    print(f"navigation consistency: {len(table_refs)} entries, {len(doc_files)} docs files, 0 missing, 0 duplicates")
    print("docs navigation consistency smoke test passed")


if __name__ == "__main__":
    main()
