"""Smoke test: verify dev-prototype.sh exists, is executable, and references required files."""

from __future__ import annotations

import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
SCRIPT = REPO / "scripts" / "dev-prototype.sh"
DEV_BACKEND = REPO / "scripts" / "dev-backend.sh"


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
    assert ".venv/bin/uvicorn" in text, "script must prefer the local virtualenv uvicorn"
    assert "FLIGHTRECORDER_CONFIG" in text, "script must set FLIGHTRECORDER_CONFIG"
    assert 'cd "$ROOT"' in text, "script must run from the flightrecorder root"
    assert 'exec "$UVICORN"' in text, "script must exec the resolved uvicorn"

    assert text.strip().startswith("#!/"), "script must have a shebang"

    if not DEV_BACKEND.is_file():
        print(f"missing: {DEV_BACKEND}", file=sys.stderr)
        sys.exit(1)

    if not os.access(DEV_BACKEND, os.X_OK):
        print(f"not executable: {DEV_BACKEND}", file=sys.stderr)
        sys.exit(1)

    dev_text = DEV_BACKEND.read_text(encoding="utf-8")

    assert dev_text.strip().startswith("#!/"), "dev-backend script must have a shebang"
    assert "uvicorn" in dev_text, "dev-backend script must reference uvicorn"
    assert ".venv/bin/uvicorn" in dev_text, "dev-backend script must prefer the local virtualenv uvicorn"
    assert "FLIGHTRECORDER_CONFIG" in dev_text, "dev-backend script must set FLIGHTRECORDER_CONFIG"
    assert "config.local.toml" in dev_text, "dev-backend script must prefer config.local.toml"
    assert "config.toml" in dev_text, "dev-backend script must check config.toml"
    assert "config.*.local.toml" in dev_text, "dev-backend script must detect provider-specific local configs"
    assert 'cd "$ROOT"' in dev_text, "dev-backend script must run from the flightrecorder root"
    assert 'exec "$UVICORN"' in dev_text, "dev-backend script must exec the resolved uvicorn"

    print("dev-prototype script smoke test passed")
    print("dev-backend script smoke test passed")


if __name__ == "__main__":
    main()
