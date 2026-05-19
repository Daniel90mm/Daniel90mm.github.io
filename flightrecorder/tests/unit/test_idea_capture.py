import json
import sqlite3
from datetime import datetime
from pathlib import Path

import pytest

from flightrecorder.documents import create_project_document
from flightrecorder.idea_capture import (
    IdeaCaptureError,
    ProjectAppendOperation,
    SpaghettiOperation,
    apply_idea_operations,
    make_idea_id,
    parse_idea_operations,
    render_spaghetti_idea,
)
from flightrecorder.schema import initialize_database
from flightrecorder.storage import SessionMetadata, index_session


def test_parse_idea_operations_accepts_expected_shapes() -> None:
    operations = parse_idea_operations(
        json.dumps(
            [
                {
                    "type": "project_append",
                    "project_ref": "fnirs",
                    "section": "TODOs",
                    "content": "prototype the amplifier",
                },
                {
                    "type": "spaghetti",
                    "tags": ["pca", "signal-processing"],
                    "topics": ["statistics"],
                    "content": "PCA may denoise future sensor projects.",
                },
            ]
        )
    )

    assert operations == [
        ProjectAppendOperation(
            project_ref="fnirs",
            section="TODOs",
            content="prototype the amplifier",
        ),
        SpaghettiOperation(
            tags=["pca", "signal-processing"],
            topics=["statistics"],
            content="PCA may denoise future sensor projects.",
        ),
    ]


@pytest.mark.parametrize(
    "raw_output",
    [
        '```json\n[{"type":"spaghetti","tags":["pca"],"topics":["statistics"],"content":"Apply PCA to disordered multi-dimensional sensor data."}]\n```',
        'Here is the extraction:\n[{"type":"spaghetti","tags":["ecg","pulse-ox"],"topics":["biophotonics"],"content":"Use ECG as a timing reference to synchronize pulse oximeter heartbeat measurements."}]',
        '{"operations":[{"type":"spaghetti","tags":["pca"],"topics":["statistics"],"content":"Apply PCA to disordered multi-dimensional sensor data."}]}',
        '```json\n{"ideas":[{"type":"spaghetti","tags":["ecg"],"topics":["pulse-ox"],"content":"Use ECG to synchronize pulse oximeter heartbeat windows."}]}\n```',
    ],
)
def test_parse_idea_operations_accepts_wrapped_json_array(raw_output: str) -> None:
    operations = parse_idea_operations(raw_output)

    assert len(operations) == 1
    assert isinstance(operations[0], SpaghettiOperation)


@pytest.mark.parametrize(
    "raw_output",
    [
        "not json",
        "{}",
        json.dumps([{"type": "unknown"}]),
        json.dumps([{"type": "project_append", "project_ref": "fnirs"}]),
        json.dumps(
            [
                {
                    "type": "project_append",
                    "project_ref": "fnirs",
                    "section": "Nope",
                    "content": "x",
                }
            ]
        ),
        json.dumps(
            [
                {
                    "type": "spaghetti",
                    "tags": ["pca"],
                    "topics": [""],
                    "content": "x",
                }
            ]
        ),
        json.dumps([{"type": "spaghetti", "tags": [], "topics": [], "content": "x"}] * 9),
    ],
)
def test_parse_idea_operations_fails_closed(raw_output: str) -> None:
    with pytest.raises(IdeaCaptureError):
        parse_idea_operations(raw_output)


def test_apply_idea_operations_appends_project_and_writes_spaghetti(tmp_path: Path) -> None:
    connection = sqlite3.connect(":memory:")
    initialize_database(connection)
    source_session = "2026-05-18-1730-fnirs-abcd1234"
    index_session(connection, make_session_metadata(source_session), tmp_path / "session.md")
    create_project_document(
        tmp_path,
        "fnirs",
        datetime.fromisoformat("2026-05-18T18:45:00+02:00"),
    )
    captured_at = datetime.fromisoformat("2026-05-18T19:00:00+02:00")

    result = apply_idea_operations(
        runtime_home=tmp_path,
        connection=connection,
        source_session=source_session,
        captured_at=captured_at,
        operations=[
            ProjectAppendOperation(
                project_ref="fnirs",
                section="TODOs",
                content="prototype the amplifier",
            ),
            SpaghettiOperation(
                tags=["pca"],
                topics=["statistics"],
                content="PCA may denoise future sensor projects.",
            ),
        ],
    )

    project_text = result.project_paths[0].read_text(encoding="utf-8")
    spaghetti_text = result.spaghetti_paths[0].read_text(encoding="utf-8")
    idea_row = connection.execute(
        "SELECT source_session, tags_json, topics_json, status FROM ideas"
    ).fetchone()
    session_row = connection.execute(
        "SELECT extracted, extracted_at FROM sessions WHERE session_id = ?",
        (source_session,),
    ).fetchone()

    assert "prototype the amplifier [source: 2026-05-18-1730-fnirs-abcd1234]" in project_text
    assert "PCA may denoise future sensor projects." in spaghetti_text
    assert idea_row == (
        source_session,
        json.dumps(["pca"]),
        json.dumps(["statistics"]),
        "unmatched",
    )
    assert session_row == (1, "2026-05-18T19:00:00+02:00")
    assert result.documents_committed is False


def test_apply_idea_operations_can_commit_document_repo(tmp_path: Path) -> None:
    connection = sqlite3.connect(":memory:")
    initialize_database(connection)
    source_session = "2026-05-18-1730-fnirs-abcd1234"
    index_session(connection, make_session_metadata(source_session), tmp_path / "session.md")
    create_project_document(
        tmp_path,
        "fnirs",
        datetime.fromisoformat("2026-05-18T18:45:00+02:00"),
    )

    result = apply_idea_operations(
        runtime_home=tmp_path,
        connection=connection,
        source_session=source_session,
        captured_at=datetime.fromisoformat("2026-05-18T19:00:00+02:00"),
        operations=[
            ProjectAppendOperation(
                project_ref="fnirs",
                section="TODOs",
                content="prototype the amplifier",
            )
        ],
        commit_documents=True,
    )

    assert result.documents_committed is True
    assert (tmp_path / "documents" / ".git").exists()


def test_apply_empty_operations_marks_session_extracted(tmp_path: Path) -> None:
    connection = sqlite3.connect(":memory:")
    initialize_database(connection)
    source_session = "2026-05-18-1730-empty-abcd1234"
    index_session(connection, make_session_metadata(source_session), tmp_path / "session.md")

    result = apply_idea_operations(
        runtime_home=tmp_path,
        connection=connection,
        source_session=source_session,
        captured_at=datetime.fromisoformat("2026-05-18T19:00:00+02:00"),
        operations=[],
    )

    row = connection.execute(
        "SELECT extracted FROM sessions WHERE session_id = ?",
        (source_session,),
    ).fetchone()
    assert result.project_paths == []
    assert result.spaghetti_paths == []
    assert row == (1,)


def test_make_idea_id_is_stable_and_content_based() -> None:
    idea_id = make_idea_id(
        "2026-05-18-1730-spaghetti-abcd1234",
        0,
        "PCA may denoise future sensor projects.",
    )

    assert idea_id.startswith("pca-may-denoise-future-sensor-projects-")
    assert idea_id == make_idea_id(
        "2026-05-18-1730-spaghetti-abcd1234",
        0,
        "PCA may denoise future sensor projects.",
    )


def test_render_spaghetti_idea_uses_frontmatter_shape() -> None:
    text = render_spaghetti_idea(
        idea_id="pca-future",
        captured_at="2026-05-18T19:00:00+02:00",
        source_session="session-1",
        tags=["pca"],
        topics=["statistics"],
        content="PCA may denoise future projects.",
    )

    assert 'idea_id: "pca-future"' in text
    assert 'source_session: "session-1"' in text
    assert 'tags: ["pca"]' in text
    assert 'topics: ["statistics"]' in text
    assert "status: unmatched" in text
    assert text.endswith("PCA may denoise future projects.\n")


def make_session_metadata(session_id: str) -> SessionMetadata:
    return SessionMetadata(
        session_id=session_id,
        started_at="2026-05-18T17:30:00+02:00",
        ended_at=None,
        provider="google",
        model="gemini-2.5-pro",
        message_count=1,
        image_count=0,
        tags=[],
        project_ref="fnirs",
        spaghetti=False,
        extracted=False,
        extracted_at=None,
        curated=False,
    )
