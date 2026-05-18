"""Smoke test: termux-phone.sh --help exits 0 and contains install-boot."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> None:
    script_path = (
        Path(__file__).resolve().parent.parent.parent / "scripts" / "termux-phone.sh"
    )

    if not script_path.exists():
        print(f"script not found: {script_path}", file=sys.stderr)
        sys.exit(1)

    if not script_path.stat().st_mode & 0o100:
        print(f"script is not executable: {script_path}", file=sys.stderr)
        sys.exit(1)

    result = subprocess.run(
        ["bash", str(script_path), "--help"],
        capture_output=True,
        text=True,
        timeout=10,
    )

    assert result.returncode == 0, f"--help exited {result.returncode}: {result.stderr}"
    assert "install-boot" in result.stdout, f"--help output missing install-boot:\n{result.stdout}"

    print("termux helper smoke test passed")


if __name__ == "__main__":
    main()
