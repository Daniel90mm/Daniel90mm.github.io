"""Smoke test: every implemented route in API_CURRENT_STATE.md exists in api.py or app.py."""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent


def main() -> None:
    state_path = REPO / "docs" / "API_CURRENT_STATE.md"
    if not state_path.exists():
        print("API_CURRENT_STATE.md not found", file=sys.stderr)
        sys.exit(1)

    text = state_path.read_text(encoding="utf-8")

    implemented_section = text.split("## Implemented")[1].split("## Draft-only")[0]
    routes = re.findall(r"`([A-Z]+) (/[^`]+)`", implemented_section)

    api_py = REPO / "src" / "backend" / "flightrecorder" / "api.py"
    app_py = REPO / "src" / "backend" / "flightrecorder" / "app.py"
    app_text = ""
    if api_py.exists():
        app_text += api_py.read_text(encoding="utf-8")
    if app_py.exists():
        app_text += app_py.read_text(encoding="utf-8")

    for method, path in routes:
        path_search = path.replace("/api/", "/")
        found = path_search in app_text
        status = "ok" if found else "MISSING"
        print(f"{method} {path}: {status}")
        if not found:
            print(f"ERROR: route {path} not found in api.py or app.py", file=sys.stderr)
            sys.exit(1)

    print("api current state smoke test passed")


if __name__ == "__main__":
    main()
