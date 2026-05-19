"""Integration tests for read-only spaghetti API routes."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from flightrecorder.app import create_app
from flightrecorder.config import parse_config
from flightrecorder.runtime import build_runtime_context


def make_app(tmp_path: Path) -> TestClient:
    config = parse_config({"paths": {"runtime_home": str(tmp_path)}})
    runtime = build_runtime_context(config)
    app = create_app(config=config, runtime=runtime)
    return TestClient(app)


def setup_spaghetti_fixtures(tmp_path: Path) -> None:
    spag_dir = tmp_path / "spaghetti"
    spag_dir.mkdir()

    now = datetime.now(timezone.utc).isoformat()

    (spag_dir / "idea-alpha-abc001.md").write_text(
        "---\ntags: [ml, vision]\n---\n\nCNN for denoising.\n",
        encoding="utf-8",
    )
    (spag_dir / "idea-beta-def002.md").write_text(
        "---\ntags: [hardware]\n---\n\nLow-noise amplifier.\n",
        encoding="utf-8",
    )

    runtime = build_runtime_context(
        parse_config({"paths": {"runtime_home": str(tmp_path)}})
    )
    db = runtime.database

    db.execute(
        """INSERT INTO sessions (session_id, started_at, provider, model,
        message_count, image_count, tags_json, project_ref, spaghetti,
        extracted, extracted_at, curated, path)
        VALUES (?, ?, 'stub', 'stub', 0, 0, '[]', NULL, 0, 0, NULL, 0, ?)""",
        ("session-1", now, str(tmp_path / "sessions" / "session-1" / "metadata.json")),
    )
    (tmp_path / "sessions" / "session-1").mkdir(parents=True)
    (tmp_path / "sessions" / "session-1" / "metadata.json").write_text(
        json.dumps({}), encoding="utf-8"
    )

    db.execute(
        """INSERT INTO ideas (idea_id, captured_at, source_session,
        tags_json, topics_json, status, match_attempts,
        matched_to_json, implemented_in_json, path)
        VALUES (?, ?, ?, ?, ?, 'unmatched', 0, '[]', '[]', ?)""",
        (
            "idea-alpha-abc001",
            now,
            "session-1",
            json.dumps(["ml", "vision"]),
            json.dumps(["denoising"]),
            str(spag_dir / "idea-alpha-abc001.md"),
        ),
    )
    db.execute(
        """INSERT INTO ideas (idea_id, captured_at, source_session,
        tags_json, topics_json, status, match_attempts,
        matched_to_json, implemented_in_json, path)
        VALUES (?, ?, ?, ?, ?, 'unmatched', 0, '[]', '[]', ?)""",
        (
            "idea-beta-def002",
            now,
            "session-1",
            json.dumps(["hardware"]),
            json.dumps(["amplifier"]),
            str(spag_dir / "idea-beta-def002.md"),
        ),
    )
    db.commit()


def test_list_spaghetti_with_fixtures(tmp_path: Path) -> None:
    setup_spaghetti_fixtures(tmp_path)
    client = make_app(tmp_path)

    response = client.get("/api/spaghetti")
    assert response.status_code == 200
    body = response.json()
    assert "ideas" in body
    assert len(body["ideas"]) == 2

    ids = {idea["idea_id"] for idea in body["ideas"]}
    assert ids == {"idea-alpha-abc001", "idea-beta-def002"}

    for idea in body["ideas"]:
        assert isinstance(idea["tags"], list)
        assert isinstance(idea["topics"], list)
        assert idea["status"] == "unmatched"
        assert "captured_at" in idea
        assert "source_session" in idea
        assert idea["path"].startswith("spaghetti/")


def test_list_spaghetti_empty(tmp_path: Path) -> None:
    client = make_app(tmp_path)

    response = client.get("/api/spaghetti")
    assert response.status_code == 200
    assert response.json() == {"ideas": []}


def test_get_spaghetti_by_id(tmp_path: Path) -> None:
    setup_spaghetti_fixtures(tmp_path)
    client = make_app(tmp_path)

    response = client.get("/api/spaghetti/idea-alpha-abc001")
    assert response.status_code == 200
    body = response.json()
    assert body["idea_id"] == "idea-alpha-abc001"
    assert body["tags"] == ["ml", "vision"]
    assert body["topics"] == ["denoising"]
    assert body["path"] == "spaghetti/idea-alpha-abc001.md"
    assert "CNN for denoising" in body["body"]
    assert "---" not in body["body"]


def test_get_spaghetti_not_found(tmp_path: Path) -> None:
    setup_spaghetti_fixtures(tmp_path)
    client = make_app(tmp_path)

    response = client.get("/api/spaghetti/nonexistent-id")
    assert response.status_code == 404


def test_delete_spaghetti_removes_file_and_index_row(tmp_path: Path) -> None:
    setup_spaghetti_fixtures(tmp_path)
    client = make_app(tmp_path)
    idea_path = tmp_path / "spaghetti" / "idea-alpha-abc001.md"

    response = client.delete("/api/spaghetti/idea-alpha-abc001")

    assert response.status_code == 200
    assert response.json() == {"deleted": "idea-alpha-abc001"}
    assert idea_path.exists() is False
    assert client.get("/api/spaghetti/idea-alpha-abc001").status_code == 404

    list_response = client.get("/api/spaghetti")
    ids = {idea["idea_id"] for idea in list_response.json()["ideas"]}
    assert ids == {"idea-beta-def002"}


def test_delete_spaghetti_not_found(tmp_path: Path) -> None:
    client = make_app(tmp_path)

    response = client.delete("/api/spaghetti/nope")

    assert response.status_code == 404


def test_get_spaghetti_rejects_path_outside_runtime(tmp_path: Path) -> None:
    setup_spaghetti_fixtures(tmp_path)
    outside = tmp_path.parent / "outside-spaghetti.md"
    outside.write_text("outside runtime\n", encoding="utf-8")

    runtime = build_runtime_context(
        parse_config({"paths": {"runtime_home": str(tmp_path)}})
    )
    runtime.database.execute(
        "UPDATE ideas SET path = ? WHERE idea_id = ?",
        (str(outside), "idea-alpha-abc001"),
    )
    runtime.database.commit()

    client = make_app(tmp_path)
    response = client.get("/api/spaghetti/idea-alpha-abc001")
    assert response.status_code == 404


def test_routes_are_read_only(tmp_path: Path) -> None:
    client = make_app(tmp_path)

    response = client.get("/api/spaghetti")
    assert response.status_code == 200

    response = client.get("/api/spaghetti/anything")
    assert response.status_code == 404

    db = client.app.state.runtime.database
    count = db.execute("SELECT COUNT(*) FROM ideas").fetchone()[0]
    assert count == 0, "read route must not create ideas rows"
