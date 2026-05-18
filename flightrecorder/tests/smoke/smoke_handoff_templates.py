"""Smoke test: README files for handoffs/ and consults/ mention required sections."""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent


def main() -> None:
    handoff_readme = REPO / "handoffs" / "README.md"
    consult_readme = REPO / "consults" / "README.md"

    for path, name, required in [
        (handoff_readme, "handoffs/README.md", ["done", "pick up"]),
        (consult_readme, "consults/README.md", ["context", "options", "lean", "asking"]),
    ]:
        if not path.exists():
            text = ""
            print(f"missing: {name}, creating with template", file=sys.stderr)
        else:
            text = path.read_text(encoding="utf-8")

        missing = [r for r in required if r not in text.lower()]
        if missing:
            print(f"{name} missing sections: {missing}", file=sys.stderr)
            sys.exit(1)

        print(f"{name}: ok")

    print("handoff template smoke test passed")


if __name__ == "__main__":
    main()
