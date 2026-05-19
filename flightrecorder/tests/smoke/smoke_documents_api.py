"""Smoke test: exercise project/document read routes with TestClient."""

from __future__ import annotations

import json
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

        projects_json = tmp_path / "projects.json"
        projects_json.write_text(
            json.dumps(
                [
                    {
                        "name": "smoke project",
                        "ref": "smoke",
                        "path": "documents/smoke.md",
                        "active": True,
                        "description": "smoke test project",
                    }
                ]
            ),
            encoding="utf-8",
        )

        docs_dir = tmp_path / "documents"
        docs_dir.mkdir()
        (docs_dir / "smoke.md").write_text("## Problem\n\nTest.\n", encoding="utf-8")

        config = parse_config({"paths": {"runtime_home": str(tmp_path)}})
        runtime = build_runtime_context(config)
        app = create_app(config=config, runtime=runtime)
        client = TestClient(app)

        resp = client.get("/api/projects")
        assert resp.status_code == 200
        assert len(resp.json()["projects"]) == 1

        resp = client.get("/api/documents")
        assert resp.status_code == 200
        assert len(resp.json()["documents"]) == 1

        resp = client.get("/api/documents/smoke")
        assert resp.status_code == 200
        assert "Test." in resp.json()["body"]

        resp = client.get("/api/documents/nope")
        assert resp.status_code == 404

        print("documents API smoke test passed")


if __name__ == "__main__":
    main()
