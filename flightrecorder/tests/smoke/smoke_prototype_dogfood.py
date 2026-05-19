"""Smoke test: offline prototype provider runs the full browser dogfood loop."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

from fastapi.testclient import TestClient

from flightrecorder.app import create_app
from flightrecorder.config import load_config
from flightrecorder.runtime import build_runtime_context


REPO = Path(__file__).resolve().parent.parent.parent


def main() -> None:
    config = load_config(REPO / "config.prototype.toml")
    runtime_home = config.paths.runtime_home
    if runtime_home.exists():
        shutil.rmtree(runtime_home)

    runtime = build_runtime_context(config)
    client = TestClient(create_app(config=config, runtime=runtime))

    status = client.get("/api/runtime")
    assert status.status_code == 200
    roles = status.json()["roles"]
    assert roles["brainstorm"]["configured"] is True
    assert roles["idea_capture"]["configured"] is True

    created = client.post(
        "/api/sessions",
        json={
            "provider": "prototype",
            "model": "prototype-brainstorm",
            "slug": "prototype-smoke",
        },
    )
    assert created.status_code == 201
    session_id = created.json()["session_id"]

    chat = client.post(
        f"/api/sessions/{session_id}/messages",
        json={"content": "Build a visible MVP loop."},
    )
    assert chat.status_code == 200
    assert "Prototype response" in chat.text

    extracted = client.post(f"/api/sessions/{session_id}/extract")
    assert extracted.status_code == 200
    extract_body = extracted.json()
    assert extract_body["project_appends"] == 1
    assert extract_body["spaghetti"] == 1

    document = client.get("/api/documents/prototype")
    assert document.status_code == 200
    assert "Prototype captured" in document.json()["body"]

    spaghetti = client.get("/api/spaghetti")
    assert spaghetti.status_code == 200
    ideas = spaghetti.json()["ideas"]
    assert len(ideas) == 1

    idea = client.get(f"/api/spaghetti/{ideas[0]['idea_id']}")
    assert idea.status_code == 200
    assert "Loose follow-up from prototype session" in idea.json()["body"]

    print("prototype dogfood smoke test passed")


if __name__ == "__main__":
    try:
        main()
    except AssertionError as exc:
        print(f"prototype dogfood smoke failed: {exc}", file=sys.stderr)
        raise
