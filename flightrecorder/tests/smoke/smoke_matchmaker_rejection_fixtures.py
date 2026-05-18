"""Smoke test: load all matchmaker rejection fixtures and validate schema."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
FIXTURES_DIR = REPO / "tests" / "fixtures" / "matchmaker"

REQUIRED_KEYS = {"scenario_id", "spaghetti", "projects", "expected_match_count", "expected_match_refs", "notes"}


def main() -> None:
    if not FIXTURES_DIR.exists():
        print(f"missing: {FIXTURES_DIR}", file=sys.stderr)
        sys.exit(1)

    for path in sorted(FIXTURES_DIR.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))

        missing = REQUIRED_KEYS - set(data.keys())
        if missing:
            print(f"{path.name}: missing keys {missing}", file=sys.stderr)
            sys.exit(1)

        if not isinstance(data["scenario_id"], str):
            print(f"{path.name}: scenario_id must be string", file=sys.stderr)
            sys.exit(1)
        if not isinstance(data["spaghetti"], str):
            print(f"{path.name}: spaghetti must be string", file=sys.stderr)
            sys.exit(1)
        if not isinstance(data["projects"], list):
            print(f"{path.name}: projects must be array", file=sys.stderr)
            sys.exit(1)
        if not isinstance(data["expected_match_count"], int):
            print(f"{path.name}: expected_match_count must be int", file=sys.stderr)
            sys.exit(1)
        if not isinstance(data["expected_match_refs"], list):
            print(f"{path.name}: expected_match_refs must be array", file=sys.stderr)
            sys.exit(1)
        if not isinstance(data["notes"], str):
            print(f"{path.name}: notes must be string", file=sys.stderr)
            sys.exit(1)

        for proj in data["projects"]:
            if not isinstance(proj, dict):
                print(f"{path.name}: project entry must be object", file=sys.stderr)
                sys.exit(1)
            if "ref" not in proj or "summary" not in proj:
                print(f"{path.name}: project missing ref/summary", file=sys.stderr)
                sys.exit(1)

        if data["expected_match_count"] != len(data["expected_match_refs"]):
            print(
                f"{path.name}: count {data['expected_match_count']} != "
                f"refs length {len(data['expected_match_refs'])}",
                file=sys.stderr,
            )
            sys.exit(1)

        if data["expected_match_count"] < 0:
            print(f"{path.name}: expected_match_count must be >= 0", file=sys.stderr)
            sys.exit(1)

        print(f"{data['scenario_id']}: count={data['expected_match_count']}, refs={data['expected_match_refs']}")

    print("matchmaker rejection fixtures smoke test passed")


if __name__ == "__main__":
    main()
