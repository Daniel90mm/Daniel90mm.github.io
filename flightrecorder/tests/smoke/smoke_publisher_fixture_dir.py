"""Smoke test: verify adversarial_fixture_dir() contract."""

from __future__ import annotations

import sys
from pathlib import Path

from flightrecorder.publisher import adversarial_fixture_dir

EXPECTED = {"names", "emails", "repo_urls", "course_codes", "mixed", "sensitive"}


def main() -> None:
    fixture_dir = adversarial_fixture_dir()

    if not isinstance(fixture_dir, Path):
        print("ERROR: adversarial_fixture_dir did not return a Path", file=sys.stderr)
        sys.exit(1)

    if not fixture_dir.exists():
        print(f"ERROR: fixture dir does not exist: {fixture_dir}", file=sys.stderr)
        sys.exit(1)

    if not fixture_dir.is_dir():
        print(f"ERROR: fixture path is not a directory: {fixture_dir}", file=sys.stderr)
        sys.exit(1)

    found = {p.stem for p in fixture_dir.glob("*.txt")}

    missing = EXPECTED - found
    if missing:
        print(f"ERROR: missing expected fixture files: {missing}", file=sys.stderr)
        sys.exit(1)

    for txt_path in fixture_dir.glob("*.txt"):
        content = txt_path.read_text(encoding="utf-8").strip()
        if not content:
            print(f"ERROR: fixture file is empty: {txt_path}", file=sys.stderr)
            sys.exit(1)

    print(f"fixture_dir: {fixture_dir}")
    print(f"found_categories: {len(found)}")
    print(f"expected_categories: {len(EXPECTED)}")
    print("publisher fixture dir smoke test passed")


if __name__ == "__main__":
    main()
