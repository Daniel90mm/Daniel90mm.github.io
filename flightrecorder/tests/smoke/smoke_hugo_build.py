"""Smoke test: build the Hugo site into a temporary production artifact."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent


def main() -> None:
    museum_dir = REPO_ROOT / "museum"
    hugo_toml = museum_dir / "hugo.toml"
    if not hugo_toml.exists():
        print(f"missing: {hugo_toml}", file=sys.stderr)
        sys.exit(1)

    if shutil.which("hugo") is None:
        print("ERROR: hugo executable not found on PATH", file=sys.stderr)
        sys.exit(1)

    with tempfile.TemporaryDirectory() as temp_dir:
        destination = Path(temp_dir)
        env = {
            **os.environ,
            "HUGO_ENVIRONMENT": "production",
            "HUGO_ENV": "production",
        }
        result = subprocess.run(
            [
                "hugo",
                "--gc",
                "--minify",
                "--destination",
                str(destination),
            ],
            cwd=museum_dir,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if result.returncode != 0:
            print(result.stdout, file=sys.stdout)
            print(result.stderr, file=sys.stderr)
            print("ERROR: hugo production build failed", file=sys.stderr)
            sys.exit(result.returncode)

        index_path = destination / "index.html"
        if not index_path.exists():
            print(f"missing generated home page: {index_path}", file=sys.stderr)
            sys.exit(1)

        home = index_path.read_text(encoding="utf-8").lower()
        required = ("daniel", "projects", "/projects/")
        missing = [needle for needle in required if needle not in home]
        if missing:
            print(
                f"ERROR: generated home page missing expected text: {missing}",
                file=sys.stderr,
            )
            sys.exit(1)

    print("hugo build smoke test passed")


if __name__ == "__main__":
    main()
