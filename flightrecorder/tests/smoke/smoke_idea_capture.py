"""Smoke test: parse and apply idea-capture operations without provider calls."""

from __future__ import annotations

import json
import sqlite3
import sys
import tempfile
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src" / "backend"))

from flightrecorder.documents import create_project_document
from flightrecorder.idea_capture import apply_idea_operations, parse_idea_operations
from flightrecorder.schema import initialize_database
from flightrecorder.storage import SessionMetadata, index_session


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        runtime_home = Path(tmp)
        connection = sqlite3.connect(":memory:")
        initialize_database(connection)
        session_id = "2026-05-18-1730-smoke-abcd1234"
        index_session(connection, make_metadata(session_id), runtime_home / "session.md")
        create_project_document(
            runtime_home,
            "fnirs",
            datetime.fromisoformat("2026-05-18T18:45:00+02:00"),
        )

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
                        "tags": ["pca"],
                        "topics": ["statistics"],
                        "content": "PCA may denoise future sensor projects.",
                    },
                ]
            )
        )
        result = apply_idea_operations(
            runtime_home=runtime_home,
            connection=connection,
            source_session=session_id,
            operations=operations,
            captured_at=datetime.fromisoformat("2026-05-18T19:00:00+02:00"),
        )

        print(f"project_paths: {len(result.project_paths)}")
        print(f"spaghetti_paths: {len(result.spaghetti_paths)}")
        assert len(result.project_paths) == 1
        assert len(result.spaghetti_paths) == 1
        assert result.spaghetti_paths[0].exists()

    print("idea capture smoke test passed")


def make_metadata(session_id: str) -> SessionMetadata:
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


if __name__ == "__main__":
    main()
