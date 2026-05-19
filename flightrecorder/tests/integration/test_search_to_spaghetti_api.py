"""Integration tests for POST /api/spaghetti/from-search."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from fastapi.testclient import TestClient

from flightrecorder.app import create_app
from flightrecorder.config import parse_config
from flightrecorder.runtime import build_runtime_context


def make_app(tmp_path: Path) -> TestClient:
    config = parse_config({"paths": {"runtime_home": str(tmp_path)}})
    runtime = build_runtime_context(config)
    app = create_app(config=config, runtime=runtime)
    return TestClient(app)


def test_capture_search_result_creates_spaghetti_idea(tmp_path: Path) -> None:
    client = make_app(tmp_path)

    payload = {
        "title": "Karpathy on Search",
        "url": "https://karpathy.blog/2025/search",
        "snippet": "Autoregressive search is the future.",
        "raw_content": "Detailed analysis of search architectures.",
    }
    response = client.post("/api/spaghetti/from-search", json=payload)
    assert response.status_code == 201
    data = response.json()

    assert "idea_id" in data
    idea_id = data["idea_id"]
    assert data["title"] == "Karpathy on Search"
    assert data["url"] == "https://karpathy.blog/2025/search"
    assert data["captured_at"] is not None
    assert data["path"].startswith("spaghetti/")

    # File was created on disk.
    spag_file = tmp_path / data["path"]
    assert spag_file.is_file()
    content = spag_file.read_text(encoding="utf-8")
    assert "Karpathy on Search" in content
    assert "https://karpathy.blog/2025/search" in content
    assert "Autoregressive search is the future." in content
    assert "Detailed analysis of search architectures." in content
    assert "tags:" in content
    assert "web-search" in content
    assert "source_session:" in content
    assert "web-search-capture" in content

    # Sqlite row was created.
    db_path = tmp_path / "metadata.db"
    db = sqlite3.connect(str(db_path))
    row = db.execute(
        "SELECT idea_id, source_session, tags_json, status, path "
        "FROM ideas WHERE idea_id = ?",
        (idea_id,),
    ).fetchone()
    assert row is not None, f"idea {idea_id} not found in sqlite"
    assert row[1] == "web-search-capture"
    tags = json.loads(row[2])
    assert "web-search" in tags
    assert row[3] == "unmatched"
    sentinel_row = db.execute(
        "SELECT COUNT(*) FROM sessions WHERE session_id = ?",
        ("web-search-capture",),
    ).fetchone()
    assert sentinel_row == (1,), "search capture should keep FK provenance"
    db.close()

    sessions_response = client.get("/api/sessions")
    assert sessions_response.status_code == 200
    session_ids = {s["session_id"] for s in sessions_response.json()["sessions"]}
    assert "web-search-capture" not in session_ids


def test_capture_minimal_result_missing_snippet_and_raw(tmp_path: Path) -> None:
    client = make_app(tmp_path)

    payload = {
        "title": "Minimal Result",
        "url": "https://example.com/minimal",
    }
    response = client.post("/api/spaghetti/from-search", json=payload)
    assert response.status_code == 201
    data = response.json()

    spag_file = tmp_path / data["path"]
    content = spag_file.read_text(encoding="utf-8")
    assert "Minimal Result" in content
    assert "https://example.com/minimal" in content
    # No snippet blockquote and no raw content excerpt.
    assert "> " not in content
    assert "Raw content excerpt:" not in content


def test_capture_missing_title_rejected(tmp_path: Path) -> None:
    client = make_app(tmp_path)

    response = client.post(
        "/api/spaghetti/from-search",
        json={"url": "https://example.com"},
    )
    assert response.status_code == 422


def test_capture_missing_url_rejected(tmp_path: Path) -> None:
    client = make_app(tmp_path)

    response = client.post(
        "/api/spaghetti/from-search",
        json={"title": "Missing URL"},
    )
    assert response.status_code == 422
