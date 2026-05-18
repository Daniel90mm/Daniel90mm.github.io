"""Smoke test: load provider usage fixtures and verify field shapes."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
FIXTURES_DIR = REPO / "tests" / "fixtures" / "provider_usage"

REQUIRED = {"provider", "model", "role", "input_tokens", "output_tokens", "cached_tokens"}


def main() -> None:
    if not FIXTURES_DIR.exists():
        print(f"missing: {FIXTURES_DIR}", file=sys.stderr)
        sys.exit(1)

    for path in sorted(FIXTURES_DIR.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))

        missing = REQUIRED - set(data.keys())
        if missing:
            print(f"{path.name}: missing fields {missing}", file=sys.stderr)
            sys.exit(1)

        for field in ("input_tokens", "output_tokens", "cached_tokens"):
            value = data[field]
            if not isinstance(value, int) or value < 0:
                print(f"{path.name}: {field} must be non-negative int, got {value}", file=sys.stderr)
                sys.exit(1)

        print(f"{path.name}: ok")

    print("provider usage fixtures smoke test passed")


if __name__ == "__main__":
    main()
