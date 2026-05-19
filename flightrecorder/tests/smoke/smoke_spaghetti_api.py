"""Smoke test: exercise spaghetti read routes with TestClient."""

from __future__ import annotations

import json
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from fastapi.testclient import TestClient

from flightrecorder.app import create_app
from flightrecorder.config import parse_config
from flightrecorder.runtime import build_runtime_context


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)

        spag_dir = tmp_path / "spaghetti"
        spag_dir.mkdir()
        (spag_dir / "smoke-idea-xyz001.md").write_text(
            "---\ntags: [smoke]\n---\n\nA smoke test idea.\n",
            encoding="utf-8",
        )

        config = parse_config({"paths": {"runtime_home": str(tmp_path)}})
        runtime = build_runtime_context(config)

        now = datetime.now(timezone.utc).isoformat()

        session_id = "session-smoke"
        (tmp_path / "sessions" / session_id).mkdir(parents=True)
        (tmp_path / "sessions" / session_id / "metadata.json").write_text(
            json.dumps({}), encoding="utf-8"
        )
        runtime.database.execute(
            """INSERT INTO sessions (session_id, started_at, provider, model,
            message_count, image_count, tags_json, project_ref, spaghetti,
            extracted, extracted_at, curated, path)
            VALUES (?, ?, 'stub', 'stub', 0, 0, '[]', NULL, 0, 0, NULL, 0, ?)""",
            (session_id, now, str(tmp_path / "sessions" / session_id / "metadata.json")),
        )

        runtime.database.execute(
            """INSERT INTO ideas (idea_id, captured_at, source_session,
            tags_json, topics_json, status, match_attempts,
            matched_to_json, implemented_in_json, path)
            VALUES (?, ?, ?, ?, ?, 'unmatched', 0, '[]', '[]', ?)""",
            (
                "smoke-idea-xyz001",
                now,
                "session-smoke",
                json.dumps(["smoke"]),
                json.dumps(["testing"]),
                str(spag_dir / "smoke-idea-xyz001.md"),
            ),
        )
        runtime.database.commit()

        app = create_app(config=config, runtime=runtime)
        client = TestClient(app)

        resp = client.get("/api/spaghetti")
        assert resp.status_code == 200
        assert len(resp.json()["ideas"]) == 1

        resp = client.get("/api/spaghetti/smoke-idea-xyz001")
        assert resp.status_code == 200
        body = resp.json()
        assert "A smoke test idea" in body["body"]
        assert body["tags"] == ["smoke"]

        resp = client.get("/api/spaghetti/nope")
        assert resp.status_code == 404

        print("spaghetti API smoke test passed")


if __name__ == "__main__":
    main()
