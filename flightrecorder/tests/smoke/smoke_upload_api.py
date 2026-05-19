"""Smoke test: upload a tiny image, verify image_count and session detail metadata."""

from __future__ import annotations

import sys
from pathlib import Path
from tempfile import TemporaryDirectory

TINY_PNG = (
    b"\x89PNG\r\n\x1a\n"
    b"\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde"
    b"\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18\xd8N"
    b"\x00\x00\x00\x00IEND\xaeB`\x82"
)


def main() -> None:
    from fastapi.testclient import TestClient
    from flightrecorder.app import create_app
    from flightrecorder.config import parse_config
    from flightrecorder.runtime import build_runtime_context

    with TemporaryDirectory() as td:
        tmp_path = Path(td)
        config = parse_config({"paths": {"runtime_home": str(tmp_path)}})
        runtime = build_runtime_context(config)
        app = create_app(config=config, runtime=runtime)
        client = TestClient(app)

        create = client.post(
            "/api/sessions",
            json={"provider": "stub", "model": "stub", "slug": "upload-smoke"},
        )
        assert create.status_code == 201, f"create session: {create.status_code}"
        session_id = create.json()["session_id"]
        initial_image_count = create.json()["image_count"]
        assert initial_image_count == 0

        from io import BytesIO
        upload = client.post(
            f"/api/sessions/{session_id}/upload",
            files={"file": ("smoke.png", BytesIO(TINY_PNG), "image/png")},
        )
        assert upload.status_code == 201, f"upload: {upload.status_code} body={upload.text}"
        upload_body = upload.json()
        assert upload_body["image_count"] == 1, f"image_count after upload: {upload_body['image_count']}"
        assert upload_body["asset"]["filename"].endswith("smoke.png")
        assert upload_body["asset"]["relative_path"].startswith("sessions/_assets/")
        assert upload_body["asset"]["size_bytes"] == len(TINY_PNG)

        detail = client.get(f"/api/sessions/{session_id}")
        assert detail.status_code == 200
        detail_body = detail.json()
        assert detail_body["image_count"] == 1
        assert len(detail_body["assets"]) == 1
        assert detail_body["assets"][0]["filename"].endswith("smoke.png")
        assert detail_body["assets"][0]["relative_path"].startswith("sessions/_assets/")

        assets_dir = tmp_path / "sessions" / "_assets"
        png_files = list(assets_dir.glob(f"{session_id}-*"))
        assert len(png_files) == 1, f"expected 1 asset in _assets, got {len(png_files)}"
        assert png_files[0].stat().st_size > 0

        print("upload API smoke test passed")


if __name__ == "__main__":
    main()
