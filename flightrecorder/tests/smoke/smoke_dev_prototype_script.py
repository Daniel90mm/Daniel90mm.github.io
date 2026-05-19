"""Smoke test: verify dev-prototype.sh exists, is executable, and references required files."""

from __future__ import annotations

import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
SCRIPT = REPO / "scripts" / "dev-prototype.sh"


def main() -> None:
    if not SCRIPT.is_file():
        print(f"missing: {SCRIPT}", file=sys.stderr)
        sys.exit(1)

    if not os.access(SCRIPT, os.X_OK):
        print(f"not executable: {SCRIPT}", file=sys.stderr)
        sys.exit(1)

    text = SCRIPT.read_text(encoding="utf-8")

    assert "config.prototype.toml" in text, "script must reference config.prototype.toml"
    assert "uvicorn" in text, "script must reference uvicorn"
    assert "FLIGHTRECORDER_CONFIG" in text, "script must set FLIGHTRECORDER_CONFIG"
    assert 'cd "$ROOT"' in text, "script must run from the flightrecorder root"
    assert "exec uvicorn" in text, "script must use exec uvicorn"

    assert text.strip().startswith("#!/"), "script must have a shebang"

    print("dev-prototype script smoke test passed")


if __name__ == "__main__":
    main()
