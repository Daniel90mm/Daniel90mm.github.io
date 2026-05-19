"""Smoke test: GET /api/sessions/{session_id}/assets/{filename} round-trip."""

from __future__ import annotations

import sys
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory

from fastapi.testclient import TestClient

from flightrecorder.app import create_app
from flightrecorder.config import parse_config
from flightrecorder.runtime import build_runtime_context


TINY_PNG = (
    b"\x89PNG\r\n\x1a\n"
    b"\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde"
    b"\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18\xd8N"
    b"\x00\x00\x00\x00IEND\xaeB`\x82"
)


def main() -> None:
    with TemporaryDirectory() as td:
        tmp_path = Path(td)
        config = parse_config({"paths": {"runtime_home": str(tmp_path)}})
        runtime = build_runtime_context(config)
        app = create_app(config=config, runtime=runtime)
        client = TestClient(app)

        create = client.post(
            "/api/sessions",
            json={"provider": "stub", "model": "stub", "slug": "serve-smoke"},
        )
        assert create.status_code == 201
        session_id = create.json()["session_id"]

        client.post(
            f"/api/sessions/{session_id}/upload",
            files={"file": ("pic.png", BytesIO(TINY_PNG), "image/png")},
        )

        stored_filename = f"{session_id}-pic.png"
        r = client.get(f"/api/sessions/{session_id}/assets/{stored_filename}")
        assert r.status_code == 200, f"expected 200, got {r.status_code}"
        assert r.content == TINY_PNG
        assert r.headers["content-type"] == "image/png"
        print(f"OK GET asset: {len(r.content)} bytes, type={r.headers['content-type']}")

        r404 = client.get(f"/api/sessions/{session_id}/assets/{session_id}-nope.png")
        assert r404.status_code == 404

        r_trav = client.get("/api/sessions/x/assets/../../../etc/passwd")
        assert r_trav.status_code == 404

        print("session asset serving API smoke test passed")


if __name__ == "__main__":
    main()
