"""Integration tests for POST /api/matchmaker/run.

Covers the happy path (NullScorer default yields zero candidates, every
idea is rejected), the 404 on unknown idea_id, the response shape, and
the behaviour when no projects.json is present (fail-closed: empty
projects list, every idea rejected).
"""

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


def _make_app(tmp_path: Path) -> TestClient:
    config = parse_config({"paths": {"runtime_home": str(tmp_path)}})
    runtime = build_runtime_context(config)
    app = create_app(config=config, runtime=runtime)
    return TestClient(app)


def _insert_idea(
    runtime_home: Path,
    idea_id: str,
    content: str,
    tags: list[str] | None = None,
    topics: list[str] | None = None,
) -> Path:
    """Insert a row into the ideas table and write its markdown body."""

    spaghetti_dir = runtime_home / "spaghetti"
    spaghetti_dir.mkdir(parents=True, exist_ok=True)
    path = spaghetti_dir / f"{idea_id}.md"
    body = "\n".join(
        [
            "---",
            f'idea_id: "{idea_id}"',
            'captured_at: "2026-05-18T12:00:00+00:00"',
            'source_session: "session-1"',
            f"tags: {json.dumps(tags or [])}",
            "status: unmatched",
            "match_attempts: 0",
            "matched_to: []",
            "implemented_in: []",
            "---",
            "",
            content,
            "",
        ]
    )
    path.write_text(body, encoding="utf-8")

    db = sqlite3.connect(str(runtime_home / "metadata.db"))
    db.execute(
        """
        INSERT INTO ideas (
            idea_id, captured_at, source_session, tags_json, topics_json,
            status, match_attempts, matched_to_json, implemented_in_json, path
        )
        VALUES (?, ?, ?, ?, ?, 'unmatched', 0, '[]', '[]', ?)
        """,
        (
            idea_id,
            "2026-05-18T12:00:00+00:00",
            "session-1",
            json.dumps(tags or []),
            json.dumps(topics or []),
            str(path),
        ),
    )
    db.commit()
    db.close()
    return path


def _write_projects_json(runtime_home: Path, entries: list[dict[str, object]]) -> None:
    (runtime_home / "projects.json").write_text(
        json.dumps(entries),
        encoding="utf-8",
    )


# --- Happy path ---


def test_default_scorer_produces_zero_candidates(tmp_path: Path) -> None:
    """NullScorer default: every idea is rejected, no candidates returned."""

    client = _make_app(tmp_path)
    _insert_idea(tmp_path, "idea-1", "PCA for multivariate signal denoising")
    _write_projects_json(
        tmp_path,
        [
            {"name": "fNIRS", "ref": "fnirs", "path": "documents/fnirs.md",
             "active": True, "description": "biophotonics rig"},
            {"name": "Pulse Oximeter", "ref": "pulse-oximeter",
             "path": "documents/pulse-oximeter.md", "active": True,
             "description": "reflectance pulse oximeter"},
        ],
    )
    response = client.post("/api/matchmaker/run", json={"idea_ids": ["idea-1"]})
    assert response.status_code == 200

    body = response.json()
    assert body["candidates"] == []
    assert body["rejected_idea_ids"] == ["idea-1"]
    assert isinstance(body["batch_id"], str)
    assert body["batch_id"].startswith("matches-")
    assert isinstance(body["generated_at"], str)


# --- 404 on unknown idea ---


def test_unknown_idea_id_returns_404(tmp_path: Path) -> None:
    _write_projects_json(tmp_path, [])
    client = _make_app(tmp_path)

    response = client.post(
        "/api/matchmaker/run",
        json={"idea_ids": ["does-not-exist"]},
    )
    assert response.status_code == 404
    assert "does-not-exist" in response.json()["detail"]


def test_partial_unknown_idea_id_returns_404(tmp_path: Path) -> None:
    """If any idea in the request is unknown, the whole call fails fast.
    No partial matches returned."""

    client = _make_app(tmp_path)
    _insert_idea(tmp_path, "idea-1", "known idea")
    _write_projects_json(tmp_path, [])

    response = client.post(
        "/api/matchmaker/run",
        json={"idea_ids": ["idea-1", "missing"]},
    )
    assert response.status_code == 404
    assert "missing" in response.json()["detail"]


# --- Response shape ---


def test_response_shape_matches_contract(tmp_path: Path) -> None:
    client = _make_app(tmp_path)
    _insert_idea(tmp_path, "idea-1", "some content", tags=["pca"])
    _insert_idea(tmp_path, "idea-2", "other content", tags=["embedded"])
    _write_projects_json(tmp_path, [])

    response = client.post(
        "/api/matchmaker/run",
        json={"idea_ids": ["idea-1", "idea-2"]},
    )
    assert response.status_code == 200
    body = response.json()

    expected_keys = {"batch_id", "generated_at", "candidates", "rejected_idea_ids"}
    assert expected_keys.issubset(body.keys())
    assert isinstance(body["candidates"], list)
    assert isinstance(body["rejected_idea_ids"], list)
    assert set(body["rejected_idea_ids"]) == {"idea-1", "idea-2"}


# --- Fail-closed: no projects.json ---


def test_missing_projects_json_treated_as_empty_registry(tmp_path: Path) -> None:
    """Without projects.json the route returns an empty match batch
    rather than crashing - fail closed."""

    client = _make_app(tmp_path)
    _insert_idea(tmp_path, "idea-1", "stuff")
    # No _write_projects_json call.

    response = client.post(
        "/api/matchmaker/run",
        json={"idea_ids": ["idea-1"]},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["candidates"] == []
    assert body["rejected_idea_ids"] == ["idea-1"]


# --- Body validation ---


def test_empty_idea_ids_is_rejected(tmp_path: Path) -> None:
    client = _make_app(tmp_path)
    response = client.post("/api/matchmaker/run", json={"idea_ids": []})
    assert response.status_code == 422


def test_missing_body_is_rejected(tmp_path: Path) -> None:
    client = _make_app(tmp_path)
    response = client.post("/api/matchmaker/run", json={})
    assert response.status_code == 422
