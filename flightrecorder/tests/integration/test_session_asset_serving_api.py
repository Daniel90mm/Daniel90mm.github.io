"""Integration test: GET /api/sessions/{session_id}/assets/{filename}."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path

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

SAMPLE_TEXT = b"hello world\n" * 5


def _make_app(tmp_path: Path) -> TestClient:
    config = parse_config({"paths": {"runtime_home": str(tmp_path)}})
    runtime = build_runtime_context(config)
    return TestClient(create_app(config=config, runtime=runtime))


def _create_session_and_upload_asset(
    client: TestClient, filename: str, content: bytes, content_type: str
) -> str:
    create = client.post(
        "/api/sessions",
        json={"provider": "stub", "model": "stub", "slug": "asset-serve"},
    )
    assert create.status_code == 201
    session_id = create.json()["session_id"]

    upload = client.post(
        f"/api/sessions/{session_id}/upload",
        files={"file": (filename, BytesIO(content), content_type)},
    )
    assert upload.status_code == 201, f"upload: {upload.text}"
    return session_id


class TestGetSessionAsset:

    def test_returns_image_bytes_with_content_type(self, tmp_path: Path) -> None:
        client = _make_app(tmp_path)
        session_id = _create_session_and_upload_asset(client, "photo.png", TINY_PNG, "image/png")

        response = client.get(f"/api/sessions/{session_id}/assets/{session_id}-photo.png")
        assert response.status_code == 200
        assert response.content == TINY_PNG
        assert response.headers["content-type"] == "image/png"

    def test_returns_text_content_type(self, tmp_path: Path) -> None:
        client = _make_app(tmp_path)
        session_id = _create_session_and_upload_asset(client, "notes.txt", SAMPLE_TEXT, "text/plain")

        response = client.get(f"/api/sessions/{session_id}/assets/{session_id}-notes.txt")
        assert response.status_code == 200
        assert response.content == SAMPLE_TEXT
        assert response.headers["content-type"].startswith("text/plain")

    def test_returns_404_when_session_does_not_exist(self, tmp_path: Path) -> None:
        client = _make_app(tmp_path)
        response = client.get("/api/sessions/nonexistent-session/assets/some-file.png")
        assert response.status_code == 404

    def test_returns_404_when_file_does_not_exist(self, tmp_path: Path) -> None:
        client = _make_app(tmp_path)
        session_id = _create_session_and_upload_asset(client, "photo.png", TINY_PNG, "image/png")

        response = client.get(
            f"/api/sessions/{session_id}/assets/{session_id}-nope.png"
        )
        assert response.status_code == 404

    def test_returns_404_when_filename_does_not_match_session(self, tmp_path: Path) -> None:
        client = _make_app(tmp_path)
        session_id = _create_session_and_upload_asset(client, "photo.png", TINY_PNG, "image/png")

        other_session = client.post(
            "/api/sessions",
            json={"provider": "stub", "model": "stub", "slug": "other"},
        ).json()["session_id"]

        response = client.get(
            f"/api/sessions/{other_session}/assets/{session_id}-photo.png"
        )
        assert response.status_code == 404

    def test_returns_404_for_path_traversal(self, tmp_path: Path) -> None:
        client = _make_app(tmp_path)
        _create_session_and_upload_asset(client, "photo.png", TINY_PNG, "image/png")

        response = client.get("/api/sessions/any-session/assets/../../../etc/passwd")
        assert response.status_code == 404
