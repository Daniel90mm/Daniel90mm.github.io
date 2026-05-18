"""Smoke test: approved session API routes work through TestClient."""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src" / "backend"))

from fastapi.testclient import TestClient

from flightrecorder.app import create_app
from flightrecorder.config import parse_config


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        runtime_home = Path(tmp)
        config = parse_config({"paths": {"runtime_home": str(runtime_home)}})
        client = TestClient(create_app(config=config))

        created_response = client.post(
            "/api/sessions",
            json={
                "provider": "google",
                "model": "gemini-2.5-pro",
                "slug": "smoke",
            },
        )
        assert created_response.status_code == 201
        created = created_response.json()

        list_response = client.get("/api/sessions")
        assert list_response.status_code == 200
        assert list_response.json()["total"] == 1

        detail_response = client.get(f"/api/sessions/{created['session_id']}")
        assert detail_response.status_code == 200
        assert detail_response.json()["messages"] == []

        upload_response = client.post(
            f"/api/sessions/{created['session_id']}/upload",
            files={"file": ("smoke photo.jpg", b"image-bytes", "image/jpeg")},
        )
        assert upload_response.status_code == 201
        assert upload_response.json()["image_count"] == 1

        print(f"session_id: {created['session_id']}")
        print(f"runtime_home: {runtime_home}")
        print("session API smoke test passed")


if __name__ == "__main__":
    main()
