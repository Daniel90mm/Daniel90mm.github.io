"""Integration test for the parse -> apply -> persist idea-capture pipeline.

The unit tests in `tests/unit/test_idea_capture.py` cover each helper in
isolation. The property tests in `tests/adversarial/test_append_only_property.py`
cover documents.py end-to-end. This module covers the cross-file wiring that
actually runs in production: a raw idea-capture JSON string lands in
`parse_idea_operations`, the parsed operations flow through
`apply_idea_operations`, and four sinks must reach a consistent state:

    1. The project document files under `documents/` gain new bullets in the
       requested sections, with hand-written content preserved.
    2. The spaghetti markdown files under `spaghetti/` are created with the
       expected frontmatter and indexed in sqlite `ideas`.
    3. The sqlite `sessions` row for the source session is flipped to
       `extracted=1` with a populated `extracted_at`.
    4. The documents git repo has a commit per call when `commit_documents`
       is requested.

A second pass with a fresh batch of operations verifies the system is genuinely
append-only across pipeline invocations.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import pytest

from flightrecorder.documents import (
    create_project_document,
    documents_dir,
    project_document_path,
)
from flightrecorder.idea_capture import (
    IdeaCaptureError,
    apply_idea_operations,
    parse_idea_operations,
)
from flightrecorder.schema import initialize_database
from flightrecorder.storage import SessionMetadata, index_session


SESSION_ID = "2026-05-18-1200-fnirs-deadbeef"
SOURCE_PATH = "sessions/2026-05-18-1200-fnirs-deadbeef.md"


def _connection() -> sqlite3.Connection:
    connection = sqlite3.connect(":memory:")
    connection.execute("PRAGMA foreign_keys = ON")
    initialize_database(connection)
    return connection


def _seed_session(connection: sqlite3.Connection) -> None:
    index_session(
        connection,
        SessionMetadata(
            session_id=SESSION_ID,
            started_at="2026-05-18T12:00:00+00:00",
            ended_at="2026-05-18T12:30:00+00:00",
            provider="anthropic",
            model="claude-haiku-4-5-20251001",
            message_count=4,
            image_count=0,
            tags=["fnirs", "hardware"],
            project_ref="fnirs",
            spaghetti=False,
            extracted=False,
            extracted_at=None,
            curated=False,
        ),
        Path(SOURCE_PATH),
    )


def _seed_project_documents(runtime_home: Path) -> None:
    created = datetime.fromisoformat("2026-05-18T11:00:00+00:00")
    create_project_document(runtime_home, "fnirs", created)
    create_project_document(runtime_home, "pulse-oximeter", created)


def _seed_handwritten(runtime_home: Path) -> None:
    """Add a hand-written bullet that subsequent appends must not rewrite."""

    path = project_document_path(runtime_home, "fnirs")
    text = path.read_text(encoding="utf-8")
    marker = "- HAND-WRITTEN-untouched-bullet (Daniel typed this)"
    text = text.replace("## TODOs\n", f"## TODOs\n{marker}\n")
    path.write_text(text, encoding="utf-8")


def _raw_first_batch() -> str:
    return json.dumps(
        [
            {
                "type": "project_append",
                "project_ref": "fnirs",
                "section": "TODOs",
                "content": "prototype the differential amplifier stage",
            },
            {
                "type": "project_append",
                "project_ref": "pulse-oximeter",
                "section": "Open questions",
                "content": "does the AC/DC ratio drift across LED brightness?",
            },
            {
                "type": "spaghetti",
                "tags": ["embedded", "tooling"],
                "topics": ["build-systems"],
                "content": "consider switching the firmware build to zig",
            },
            {
                "type": "spaghetti",
                "tags": ["health"],
                "topics": [],
                "content": "log sleep duration alongside HRV traces",
            },
        ]
    )


def _raw_second_batch() -> str:
    return json.dumps(
        [
            {
                "type": "project_append",
                "project_ref": "fnirs",
                "section": "Decisions made",
                "content": "use four wavelengths, drop the reference channel idea",
            },
            {
                "type": "spaghetti",
                "tags": ["writing"],
                "topics": ["museum"],
                "content": "draft the fnirs writeup for the museum half",
            },
        ]
    )


def test_pipeline_persists_to_all_four_sinks(tmp_path: Path) -> None:
    runtime_home = tmp_path
    connection = _connection()
    _seed_session(connection)
    _seed_project_documents(runtime_home)
    _seed_handwritten(runtime_home)

    operations = parse_idea_operations(_raw_first_batch())
    captured_at = datetime(2026, 5, 18, 13, 0, 0, tzinfo=timezone.utc)

    applied = apply_idea_operations(
        runtime_home=runtime_home,
        connection=connection,
        source_session=SESSION_ID,
        operations=operations,
        captured_at=captured_at,
        commit_documents=True,
    )

    fnirs_text = project_document_path(runtime_home, "fnirs").read_text(encoding="utf-8")
    pulse_text = project_document_path(runtime_home, "pulse-oximeter").read_text(
        encoding="utf-8"
    )
    assert "prototype the differential amplifier stage" in fnirs_text
    assert "does the AC/DC ratio drift" in pulse_text
    assert "HAND-WRITTEN-untouched-bullet" in fnirs_text
    assert fnirs_text.count("HAND-WRITTEN-untouched-bullet") == 1

    assert len(applied.spaghetti_paths) == 2
    for path in applied.spaghetti_paths:
        assert path.exists()
        body = path.read_text(encoding="utf-8")
        assert body.startswith("---\n")
        assert "status: unmatched" in body
        assert f'source_session: "{SESSION_ID}"' in body

    idea_rows = connection.execute(
        "SELECT idea_id, source_session, status FROM ideas ORDER BY idea_id"
    ).fetchall()
    assert len(idea_rows) == 2
    for _, source, status in idea_rows:
        assert source == SESSION_ID
        assert status == "unmatched"

    session_row = connection.execute(
        "SELECT extracted, extracted_at FROM sessions WHERE session_id = ?",
        (SESSION_ID,),
    ).fetchone()
    assert session_row[0] == 1
    assert session_row[1] == captured_at.isoformat()

    assert applied.documents_committed is True
    assert (documents_dir(runtime_home) / ".git").exists()


def test_pipeline_is_append_only_across_calls(tmp_path: Path) -> None:
    runtime_home = tmp_path
    connection = _connection()
    _seed_session(connection)
    _seed_project_documents(runtime_home)

    first_captured = datetime(2026, 5, 18, 13, 0, 0, tzinfo=timezone.utc)
    second_captured = datetime(2026, 5, 18, 14, 0, 0, tzinfo=timezone.utc)

    apply_idea_operations(
        runtime_home=runtime_home,
        connection=connection,
        source_session=SESSION_ID,
        operations=parse_idea_operations(_raw_first_batch()),
        captured_at=first_captured,
        commit_documents=False,
    )
    fnirs_first = project_document_path(runtime_home, "fnirs").read_text(
        encoding="utf-8"
    )
    first_bullet = "prototype the differential amplifier stage"
    assert fnirs_first.count(first_bullet) == 1

    apply_idea_operations(
        runtime_home=runtime_home,
        connection=connection,
        source_session=SESSION_ID,
        operations=parse_idea_operations(_raw_second_batch()),
        captured_at=second_captured,
        commit_documents=False,
    )

    fnirs_after = project_document_path(runtime_home, "fnirs").read_text(
        encoding="utf-8"
    )
    assert fnirs_after.count(first_bullet) == 1
    assert "use four wavelengths" in fnirs_after
    todos_start = fnirs_after.index("## TODOs")
    todos_end = fnirs_after.index("## Ideas", todos_start)
    decisions_start = fnirs_after.index("## Decisions made")
    decisions_end = fnirs_after.index("## Open questions", decisions_start)
    assert todos_start < fnirs_after.index(first_bullet) < todos_end
    assert decisions_start < fnirs_after.index("use four wavelengths") < decisions_end
    assert f"last_appended: {second_captured.isoformat()}" in fnirs_after

    idea_count = connection.execute("SELECT COUNT(*) FROM ideas").fetchone()[0]
    assert idea_count == 3  # 2 from first batch + 1 from second

    extracted_at = connection.execute(
        "SELECT extracted_at FROM sessions WHERE session_id = ?",
        (SESSION_ID,),
    ).fetchone()[0]
    assert extracted_at == second_captured.isoformat()


def test_pipeline_rejects_malformed_capture_output(tmp_path: Path) -> None:
    """Bad LLM output never reaches the sinks - parse step fails closed."""

    runtime_home = tmp_path
    connection = _connection()
    _seed_session(connection)
    _seed_project_documents(runtime_home)

    bad_inputs = [
        "not json at all",
        json.dumps({"not": "an array"}),
        json.dumps(
            [{"type": "project_append", "project_ref": "fnirs", "section": "Nope",
              "content": "x"}]
        ),
        json.dumps([{"type": "spaghetti", "tags": "not-a-list", "topics": [],
                     "content": "x"}]),
        json.dumps([{"type": "unknown_op", "content": "x"}]),
        json.dumps([{"type": "project_append", "project_ref": "", "section": "TODOs",
                     "content": "x"}]),
    ]
    for raw in bad_inputs:
        with pytest.raises(IdeaCaptureError):
            parse_idea_operations(raw)

    fnirs_text = project_document_path(runtime_home, "fnirs").read_text(encoding="utf-8")
    assert "## Open questions\n\n## TODOs" in fnirs_text
    bullet_lines = [line for line in fnirs_text.splitlines() if line.startswith("- ")]
    assert bullet_lines == []
    assert connection.execute("SELECT COUNT(*) FROM ideas").fetchone()[0] == 0
    assert connection.execute(
        "SELECT extracted FROM sessions WHERE session_id = ?", (SESSION_ID,)
    ).fetchone()[0] == 0


def test_pipeline_skips_commit_when_only_spaghetti_operations(tmp_path: Path) -> None:
    """Documents git commit only fires when project documents actually changed."""

    runtime_home = tmp_path
    connection = _connection()
    _seed_session(connection)
    _seed_project_documents(runtime_home)

    spaghetti_only = json.dumps(
        [
            {
                "type": "spaghetti",
                "tags": ["misc"],
                "topics": [],
                "content": "loose thought with no project",
            }
        ]
    )

    applied = apply_idea_operations(
        runtime_home=runtime_home,
        connection=connection,
        source_session=SESSION_ID,
        operations=parse_idea_operations(spaghetti_only),
        captured_at=datetime(2026, 5, 18, 13, 0, 0, tzinfo=timezone.utc),
        commit_documents=True,
    )

    assert applied.project_paths == []
    assert len(applied.spaghetti_paths) == 1
    assert applied.documents_committed is False
