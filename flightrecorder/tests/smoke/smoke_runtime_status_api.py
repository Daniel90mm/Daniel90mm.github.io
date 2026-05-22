"""Smoke test: exercise GET /api/runtime with TestClient."""

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
        tmp_path = Path(tmp_dir)
        config = parse_config({"paths": {"runtime_home": str(tmp_path)}})
        runtime = build_runtime_context(config)
        app = create_app(config=config, runtime=runtime)
        client = TestClient(app)

        resp = client.get("/api/runtime")
        assert resp.status_code == 200
        body = resp.json()

        assert "runtime_home" in body
        assert "roles" in body
        assert "model_options" in body
        assert isinstance(body["model_options"], list)
        assert "brainstorm" in body["roles"]
        assert "idea_capture" in body["roles"]

        for role_name in ("brainstorm", "idea_capture"):
            role = body["roles"][role_name]
            assert "provider" in role
            assert "model" in role
            assert "configured" in role
            assert "issues" in role

        print("runtime status API smoke test passed")


if __name__ == "__main__":
    main()
