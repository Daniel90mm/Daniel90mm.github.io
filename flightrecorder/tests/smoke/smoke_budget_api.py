"""Smoke test: read-only budget API route."""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from fastapi.testclient import TestClient

from flightrecorder.app import create_app
from flightrecorder.config import parse_config
from flightrecorder.runtime import build_runtime_context


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp_dir:
        runtime_home = Path(tmp_dir)
        config = parse_config({"paths": {"runtime_home": str(runtime_home)}})
        runtime = build_runtime_context(config)
        client = TestClient(create_app(config=config, runtime=runtime))

        response = client.get("/api/budget")
        if response.status_code != 200:
            print(f"budget API returned {response.status_code}", file=sys.stderr)
            sys.exit(1)

        body = response.json()
        required = {
            "currency",
            "monthly_cost_dkk",
            "warn_at_dkk",
            "hard_stop_dkk",
            "status",
            "hard_stop_active",
            "hard_stop_path",
        }
        missing = sorted(required.difference(body))
        if missing:
            print(f"budget API missing keys: {missing}", file=sys.stderr)
            sys.exit(1)

        if (runtime_home / "budget").exists():
            print("budget API must not create hard-stop sentinel", file=sys.stderr)
            sys.exit(1)

    print("budget API smoke test passed")


if __name__ == "__main__":
    main()
