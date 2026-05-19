"""Smoke test: GET /api/publish/preview fail-closed with all three source kinds."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory

from fastapi.testclient import TestClient

from flightrecorder.app import create_app
from flightrecorder.config import parse_config
from flightrecorder.runtime import build_runtime_context
from flightrecorder.storage import ChatMessage


def main() -> None:
    with TemporaryDirectory() as td:
        tmp_path = Path(td)

        config = parse_config({"paths": {"runtime_home": str(tmp_path)}})
        runtime = build_runtime_context(config)

        meta = runtime.sessions.create_session(
            provider="s",
            model="s",
            slug="smoke",
            started_at=datetime.now(timezone.utc),
        )
        runtime.sessions.add_message(
            meta.session_id,
            ChatMessage(role="user", timestamp="2026-05-19T10:00:00+00:00", content="hello"),
        )

        docs_dir = tmp_path / "documents"
        docs_dir.mkdir()
        (docs_dir / "test-doc.md").write_text("## Problem\n\ntest.\n", encoding="utf-8")

        spag_dir = tmp_path / "spaghetti"
        spag_dir.mkdir()
        (spag_dir / "smoke-idea-001.md").write_text(
            "---\ntags: [smoke]\n---\n\nsmoke idea body.\n", encoding="utf-8"
        )
        runtime.database.execute(
            "INSERT INTO ideas (idea_id, captured_at, source_session, "
            "tags_json, topics_json, status, match_attempts, "
            "matched_to_json, implemented_in_json, path) "
            "VALUES (?, ?, ?, ?, ?, 'unmatched', 0, '[]', '[]', ?)",
            (
                "smoke-idea-001",
                datetime.now(timezone.utc).isoformat(),
                meta.session_id,
                json.dumps(["smoke"]),
                json.dumps(["testing"]),
                str(spag_dir / "smoke-idea-001.md"),
            ),
        )
        runtime.database.commit()

        app = create_app(config=config, runtime=runtime)
        client = TestClient(app)

        for source_kind, source_id in [
            ("session", meta.session_id),
            ("document", "test-doc"),
            ("spaghetti", "smoke-idea-001"),
        ]:
            r = client.get("/api/publish/preview", params={
                "source_kind": source_kind,
                "source_id": source_id,
            })
            assert r.status_code == 200, f"{source_kind} returned {r.status_code}"
            body = r.json()
            assert body["publishable"] is False, f"{source_kind} must be fail-closed"
            assert body["rejection_reason"] is not None, f"{source_kind} must have rejection_reason"
            assert body["approved_count"] == 0, f"{source_kind} approved_count must be 0"
            assert body["snippets"] == [], f"{source_kind} snippets must be empty"
            print(f"OK {source_kind}: publishable=False reason={body['rejection_reason']!r}")

        r = client.get("/api/publish/preview", params={
            "source_kind": "session",
            "source_id": "nope",
        })
        assert r.status_code == 404

        r = client.get("/api/publish/preview", params={
            "source_kind": "banana",
            "source_id": "whatever",
        })
        assert r.status_code == 422

        print("publish preview API smoke test passed (fail-closed verified)")


if __name__ == "__main__":
    main()
