"""Integration test: session asset metadata from GET /api/sessions/{id}."""

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


def test_upload_two_images_then_fetch_detail(tmp_path: Path) -> None:
    client = _make_app(tmp_path)

    create = client.post(
        "/api/sessions",
        json={"provider": "stub", "model": "stub", "slug": "asset-test"},
    )
    assert create.status_code == 201
    session_id = create.json()["session_id"]

    upload1 = client.post(
        f"/api/sessions/{session_id}/upload",
        files={"file": ("photo-1.png", BytesIO(TINY_PNG), "image/png")},
    )
    assert upload1.status_code == 201, f"upload1: {upload1.text}"
    assert upload1.json()["image_count"] == 1

    upload2 = client.post(
        f"/api/sessions/{session_id}/upload",
        files={"file": ("photo-2.png", BytesIO(TINY_PNG), "image/png")},
    )
    assert upload2.status_code == 201, f"upload2: {upload2.text}"
    assert upload2.json()["image_count"] == 2

    detail = client.get(f"/api/sessions/{session_id}")
    assert detail.status_code == 200
    body = detail.json()

    assert body["image_count"] == 2

    assets = body.get("assets", [])
    assert isinstance(assets, list), "assets must be a list"
    assert len(assets) == 2, f"expected 2 assets, got {len(assets)}"

    filenames = set()
    for asset in assets:
        assert "filename" in asset, f"missing filename in {asset}"
        assert "relative_path" in asset, f"missing relative_path in {asset}"
        assert "size_bytes" in asset, f"missing size_bytes in {asset}"
        assert isinstance(asset["size_bytes"], int), "size_bytes must be int"
        assert asset["size_bytes"] > 0
        assert isinstance(asset["relative_path"], str)
        assert not asset["relative_path"].startswith("/"), (
            f"relative_path must not be absolute: {asset['relative_path']!r}"
        )
        filenames.add(asset["filename"])

    assert len(filenames) == 2, f"expected 2 unique filenames, got {filenames}"


def test_no_assets_when_no_uploads(tmp_path: Path) -> None:
    client = _make_app(tmp_path)

    create = client.post(
        "/api/sessions",
        json={"provider": "stub", "model": "stub", "slug": "no-assets"},
    )
    session_id = create.json()["session_id"]

    detail = client.get(f"/api/sessions/{session_id}")
    assert detail.status_code == 200
    body = detail.json()
    assert body["image_count"] == 0
    assert body.get("assets") == []
