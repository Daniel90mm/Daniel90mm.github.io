"""Integration tests for GET /api/api-calls route."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from flightrecorder.app import create_app
from flightrecorder.config import parse_config
from flightrecorder.costs import ApiCallRecord, log_api_call
from flightrecorder.runtime import build_runtime_context


def make_app(tmp_path: Path) -> TestClient:
    config = parse_config({"paths": {"runtime_home": str(tmp_path)}})
    runtime = build_runtime_context(config)
    app = create_app(config=config, runtime=runtime)
    return TestClient(app)


def insert_call(
    runtime: object,
    role: str = "brainstorm",
    cost: float = 0.05,
    session_id: str | None = None,
) -> None:
    log_api_call(
        runtime.database,
        ApiCallRecord(
            timestamp=datetime.now(timezone.utc).isoformat(),
            provider="test-prov",
            model="test-model",
            role=role,
            input_tokens=100,
            output_tokens=50,
            cached_tokens=0,
            cost_dkk=cost,
            session_id=session_id,
        ),
    )


def test_empty_returns_empty_list(tmp_path: Path) -> None:
    client = make_app(tmp_path)

    response = client.get("/api/api-calls")
    assert response.status_code == 200
    assert response.json() == {"api_calls": []}


def test_returns_rows_newest_first(tmp_path: Path) -> None:
    client = make_app(tmp_path)
    runtime = client.app.state.runtime

    insert_call(runtime, role="brainstorm")
    insert_call(runtime, role="idea_capture")

    response = client.get("/api/api-calls")
    assert response.status_code == 200
    body = response.json()
    assert len(body["api_calls"]) == 2
    assert body["api_calls"][0]["role"] == "idea_capture"
    assert body["api_calls"][1]["role"] == "brainstorm"


def test_respects_limit_param(tmp_path: Path) -> None:
    client = make_app(tmp_path)
    runtime = client.app.state.runtime

    for _ in range(5):
        insert_call(runtime)

    response = client.get("/api/api-calls?limit=2")
    assert response.status_code == 200
    assert len(response.json()["api_calls"]) == 2


def test_limit_below_1_returns_422(tmp_path: Path) -> None:
    client = make_app(tmp_path)

    response = client.get("/api/api-calls?limit=0")
    assert response.status_code == 422


def test_limit_above_100_returns_422(tmp_path: Path) -> None:
    client = make_app(tmp_path)

    response = client.get("/api/api-calls?limit=101")
    assert response.status_code == 422


def test_includes_all_fields(tmp_path: Path) -> None:
    client = make_app(tmp_path)
    runtime = client.app.state.runtime

    insert_call(runtime, session_id="sess-1")

    response = client.get("/api/api-calls")
    body = response.json()["api_calls"][0]
    assert body["provider"] == "test-prov"
    assert body["model"] == "test-model"
    assert body["role"] == "brainstorm"
    assert body["input_tokens"] == 100
    assert body["output_tokens"] == 50
    assert body["cached_tokens"] == 0
    assert body["cost_dkk"] == 0.05
    assert body["session_id"] == "sess-1"


def test_read_only(tmp_path: Path) -> None:
    client = make_app(tmp_path)
    runtime = client.app.state.runtime

    count_before = runtime.database.execute(
        "SELECT COUNT(*) FROM api_calls"
    ).fetchone()[0]
    assert count_before == 0

    response = client.get("/api/api-calls")
    assert response.status_code == 200

    count_after = runtime.database.execute(
        "SELECT COUNT(*) FROM api_calls"
    ).fetchone()[0]
    assert count_after == 0
