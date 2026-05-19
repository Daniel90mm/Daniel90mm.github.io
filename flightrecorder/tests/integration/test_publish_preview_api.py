"""Integration tests for GET /api/publish/preview."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from flightrecorder.app import create_app
from flightrecorder.config import parse_config
from flightrecorder.runtime import build_runtime_context
from flightrecorder.storage import ChatMessage


def _build_runtime(tmp_path: Path):
    config = parse_config({"paths": {"runtime_home": str(tmp_path)}})
    return build_runtime_context(config)


def make_app(tmp_path: Path) -> TestClient:
    return TestClient(create_app(
        config=parse_config({"paths": {"runtime_home": str(tmp_path)}}),
        runtime=_build_runtime(tmp_path),
    ))


def _make_session(tmp_path: Path) -> str:
    runtime = _build_runtime(tmp_path)
    metadata = runtime.sessions.create_session(
        provider="stub",
        model="stub",
        slug="test",
        started_at=datetime.now(timezone.utc),
    )
    runtime.sessions.add_message(
        metadata.session_id,
        ChatMessage(
            role="user",
            timestamp="2026-05-19T10:00:00+00:00",
            content="AC/DC ratio for pulse oximetry.",
        ),
    )
    runtime.sessions.add_message(
        metadata.session_id,
        ChatMessage(
            role="assistant",
            timestamp="2026-05-19T10:00:05+00:00",
            content="Good idea, let's prototype.",
        ),
    )
    return metadata.session_id


def _make_document(tmp_path: Path, ref: str, body: str) -> None:
    _build_runtime(tmp_path)
    docs_dir = tmp_path / "documents"
    docs_dir.mkdir(parents=True, exist_ok=True)
    (docs_dir / f"{ref}.md").write_text(body, encoding="utf-8")


def _make_spaghetti(tmp_path: Path, idea_id: str, body: str) -> None:
    runtime = _build_runtime(tmp_path)
    spag_dir = tmp_path / "spaghetti"
    spag_dir.mkdir(parents=True, exist_ok=True)
    spag_path = spag_dir / f"{idea_id}.md"
    spag_path.write_text(
        f"---\ntags: [test]\n---\n\n{body}\n", encoding="utf-8"
    )

    now = datetime.now(timezone.utc).isoformat()
    db = runtime.database
    db.execute(
        "INSERT INTO sessions (session_id, started_at, provider, model, "
        "message_count, image_count, tags_json, project_ref, spaghetti, "
        "extracted, extracted_at, curated, path) "
        "VALUES (?, ?, 'stub', 'stub', 0, 0, '[]', NULL, 0, 0, NULL, 0, ?)",
        ("spag-session-1", now, str(spag_dir / "_dummy.json")),
    )
    db.execute(
        "INSERT INTO ideas (idea_id, captured_at, source_session, "
        "tags_json, topics_json, status, match_attempts, "
        "matched_to_json, implemented_in_json, path) "
        "VALUES (?, ?, ?, ?, ?, 'unmatched', 0, '[]', '[]', ?)",
        (
            idea_id,
            now,
            "spag-session-1",
            json.dumps(["test"]),
            json.dumps(["testing"]),
            str(spag_path),
        ),
    )
    db.commit()


class TestPublishPreviewSession:

    def test_session_happy_path(self, tmp_path: Path) -> None:
        session_id = _make_session(tmp_path)
        client = make_app(tmp_path)

        response = client.get(
            "/api/publish/preview",
            params={"source_kind": "session", "source_id": session_id},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["source_kind"] == "session"
        assert body["source_id"] == session_id
        assert body["publishable"] is False
        assert body["rejection_reason"] is not None
        assert body["approved_count"] == 0
        assert body["snippets"] == []

    def test_session_not_found(self, tmp_path: Path) -> None:
        client = make_app(tmp_path)
        response = client.get(
            "/api/publish/preview",
            params={"source_kind": "session", "source_id": "nonexistent"},
        )
        assert response.status_code == 404


class TestPublishPreviewDocument:

    def test_document_happy_path(self, tmp_path: Path) -> None:
        _make_document(tmp_path, "fnirs", "## Problem\n\nAmp noise.\n")
        client = make_app(tmp_path)

        response = client.get(
            "/api/publish/preview",
            params={"source_kind": "document", "source_id": "fnirs"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["source_kind"] == "document"
        assert body["source_id"] == "fnirs"
        assert body["publishable"] is False
        assert body["rejection_reason"] is not None
        assert body["approved_count"] == 0
        assert body["snippets"] == []

    def test_document_not_found(self, tmp_path: Path) -> None:
        client = make_app(tmp_path)
        response = client.get(
            "/api/publish/preview",
            params={"source_kind": "document", "source_id": "nope"},
        )
        assert response.status_code == 404


class TestPublishPreviewSpaghetti:

    def test_spaghetti_happy_path(self, tmp_path: Path) -> None:
        _make_spaghetti(tmp_path, "idea-abc-001", "Spaghetti idea body.")
        client = make_app(tmp_path)

        response = client.get(
            "/api/publish/preview",
            params={"source_kind": "spaghetti", "source_id": "idea-abc-001"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["source_kind"] == "spaghetti"
        assert body["source_id"] == "idea-abc-001"
        assert body["publishable"] is False
        assert body["rejection_reason"] is not None
        assert body["approved_count"] == 0
        assert body["snippets"] == []

    def test_spaghetti_not_found(self, tmp_path: Path) -> None:
        client = make_app(tmp_path)
        response = client.get(
            "/api/publish/preview",
            params={"source_kind": "spaghetti", "source_id": "nope"},
        )
        assert response.status_code == 404


class TestPublishPreviewValidation:

    def test_unknown_source_kind(self, tmp_path: Path) -> None:
        client = make_app(tmp_path)
        response = client.get(
            "/api/publish/preview",
            params={"source_kind": "banana", "source_id": "whatever"},
        )
        assert response.status_code == 422

    def test_missing_source_kind(self, tmp_path: Path) -> None:
        client = make_app(tmp_path)
        response = client.get(
            "/api/publish/preview",
            params={"source_id": "whatever"},
        )
        assert response.status_code == 422


class TestPublishPreviewReadOnly:

    def test_does_not_write_files_or_db(self, tmp_path: Path) -> None:
        session_id = _make_session(tmp_path)
        client = make_app(tmp_path)

        before_db = (tmp_path / "metadata.db").read_bytes()

        response = client.get(
            "/api/publish/preview",
            params={"source_kind": "session", "source_id": session_id},
        )
        assert response.status_code == 200

        after_db = (tmp_path / "metadata.db").read_bytes()
        assert before_db == after_db

        api_calls = client.app.state.runtime.database.execute(
            "SELECT COUNT(*) FROM api_calls"
        ).fetchone()[0]
        assert api_calls == 0
