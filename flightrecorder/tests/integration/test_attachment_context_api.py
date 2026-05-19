"""Integration test: GET /api/sessions/{session_id}/attachment-context."""

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


def _make_app(tmp_path: Path) -> TestClient:
    config = parse_config({"paths": {"runtime_home": str(tmp_path)}})
    runtime = build_runtime_context(config)
    return TestClient(create_app(config=config, runtime=runtime))


def test_includes_text_assets_skips_images(tmp_path: Path) -> None:
    client = _make_app(tmp_path)

    create = client.post(
        "/api/sessions",
        json={"provider": "stub", "model": "stub", "slug": "ctx-test"},
    )
    assert create.status_code == 201, create.text
    session_id = create.json()["session_id"]

    client.post(
        f"/api/sessions/{session_id}/upload",
        files={"file": ("notes.txt", BytesIO(b"important notes here"), "text/plain")},
    )
    client.post(
        f"/api/sessions/{session_id}/upload",
        files={"file": ("readme.md", BytesIO(b"# Title\nbody\n"), "text/markdown")},
    )
    client.post(
        f"/api/sessions/{session_id}/upload",
        files={"file": ("photo.png", BytesIO(TINY_PNG), "image/png")},
    )

    response = client.get(f"/api/sessions/{session_id}/attachment-context")
    assert response.status_code == 200
    body = response.json()

    assert body["session_id"] == session_id

    assert len(body["included"]) == 2
    included_filenames = [item["filename"] for item in body["included"]]
    assert f"{session_id}-notes.txt" in included_filenames
    assert f"{session_id}-readme.md" in included_filenames

    for item in body["included"]:
        assert "text" in item
        assert "extracted_chars" in item
        assert isinstance(item["extracted_chars"], int)
        assert item["extracted_chars"] > 0

    assert len(body["skipped"]) == 1
    assert body["skipped"][0]["filename"] == f"{session_id}-photo.png"
    assert body["skipped"][0]["reason"] == "unsupported_binary"

    assert "important notes" in body["combined_text"]
    assert "# Title" in body["combined_text"]


def test_empty_session(tmp_path: Path) -> None:
    client = _make_app(tmp_path)

    create = client.post(
        "/api/sessions",
        json={"provider": "stub", "model": "stub", "slug": "empty"},
    )
    session_id = create.json()["session_id"]

    response = client.get(f"/api/sessions/{session_id}/attachment-context")
    assert response.status_code == 200
    body = response.json()
    assert body["session_id"] == session_id
    assert body["included"] == []
    assert body["skipped"] == []
    assert body["combined_text"] == ""


def test_attachment_context_is_read_only(tmp_path: Path) -> None:
    client = _make_app(tmp_path)

    create = client.post(
        "/api/sessions",
        json={"provider": "stub", "model": "stub", "slug": "ro"},
    )
    session_id = create.json()["session_id"]

    client.post(
        f"/api/sessions/{session_id}/upload",
        files={"file": ("doc.txt", BytesIO(b"content"), "text/plain")},
    )

    before_calls = client.app.state.runtime.database.execute(
        "SELECT COUNT(*) FROM api_calls"
    ).fetchone()[0]

    response = client.get(f"/api/sessions/{session_id}/attachment-context")
    assert response.status_code == 200

    after_calls = client.app.state.runtime.database.execute(
        "SELECT COUNT(*) FROM api_calls"
    ).fetchone()[0]
    assert before_calls == after_calls
