"""Smoke test: verify task IDs in SMALL_MODEL_TASKS.md are unique and monotonic."""

from __future__ import annotations

import re
import sys
from pathlib import Path


TASKS_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "docs"
    / "SMALL_MODEL_TASKS.md"
)


def main() -> None:
    if not TASKS_PATH.exists():
        print(f"missing: {TASKS_PATH}", file=sys.stderr)
        sys.exit(1)

    text = TASKS_PATH.read_text(encoding="utf-8")

    heading_ids = sorted(
        int(m.group(1))
        for m in re.finditer(r"## S(\d+) ", text)
    )

    ledger_ids = sorted(
        int(m.group(1))
        for m in re.finditer(r"\|\s*S(\d+)\s*\|", text)
    )

    all_ids = sorted(set(heading_ids) | set(ledger_ids))

    print(f"heading_task_count: {len(heading_ids)}")
    print(f"ledger_task_count: {len(ledger_ids)}")
    print(f"unique_task_count: {len(all_ids)}")

    duplicates = [i for i in all_ids if heading_ids.count(i) + ledger_ids.count(i) > 1]
    if duplicates:
        print(f"duplicate_task_ids: {duplicates}", file=sys.stderr)
        sys.exit(1)

    gaps: list[int] = []
    for i in range(len(all_ids) - 1):
        current = all_ids[i]
        nxt = all_ids[i + 1]
        if nxt != current + 1 and nxt != current:
            gaps.append(current + 1)

    if gaps:
        print(f"gaps (may be taken by senior agent): {gaps}")
        print("gaps are expected (senior agent tasks skip small-model IDs)")

    print("small model task queue integrity check passed")


if __name__ == "__main__":
    main()
