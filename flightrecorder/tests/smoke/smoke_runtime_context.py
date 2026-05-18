"""Smoke test: build runtime context, print paths, verify metadata.db exists."""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src" / "backend"))

from flightrecorder.runtime import build_runtime_context_for_path


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        runtime_home = Path(tmp)
        ctx = build_runtime_context_for_path(runtime_home)

        print(f"runtime_home: {ctx.config.paths.runtime_home}")
        print(f"sessions_dir: {ctx.sessions.sessions_dir}")
        print(f"metadata_db: {ctx.config.paths.runtime_home / 'metadata.db'}")
        print(f"metadata_db_exists: {(ctx.config.paths.runtime_home / 'metadata.db').exists()}")

        assert (runtime_home / "metadata.db").exists(), "metadata.db was not created"

        ctx.database.close()

    print("runtime context smoke test passed")


if __name__ == "__main__":
    main()
