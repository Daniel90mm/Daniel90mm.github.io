"""Integration tests for the read-only budget API route."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from fastapi.testclient import TestClient

from flightrecorder.app import create_app
from flightrecorder.config import parse_config
from flightrecorder.costs import ApiCallRecord, log_api_call
from flightrecorder.runtime import build_runtime_context


def make_app(tmp_path: Path) -> TestClient:
    config = parse_config(
        {
            "paths": {"runtime_home": str(tmp_path)},
            "budget": {"warn_at_dkk": 10, "hard_stop_dkk": 20, "currency": "DKK"},
        }
    )
    runtime = build_runtime_context(config)
    app = create_app(config=config, runtime=runtime)
    return TestClient(app)


def test_budget_route_reports_monthly_spend(tmp_path: Path) -> None:
    client = make_app(tmp_path)
    log_api_call(
        client.app.state.runtime.database,
        ApiCallRecord(
            timestamp=datetime.now(timezone.utc).isoformat(),
            provider="stub",
            model="stub-model",
            role="brainstorm",
            input_tokens=10,
            output_tokens=20,
            cached_tokens=0,
            cost_dkk=12.5,
            session_id="session-1",
        ),
    )

    response = client.get("/api/budget")
    assert response.status_code == 200
    body = response.json()
    assert body["currency"] == "DKK"
    assert body["monthly_cost_dkk"] == 12.5
    assert body["warn_at_dkk"] == 10
    assert body["hard_stop_dkk"] == 20
    assert body["status"] == "warn"
    assert body["hard_stop_active"] is False
    assert body["hard_stop_path"].endswith("/budget")


def test_budget_route_is_read_only(tmp_path: Path) -> None:
    client = make_app(tmp_path)
    sentinel = tmp_path / "budget"

    response = client.get("/api/budget")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert not sentinel.exists()

    sentinel.write_text("status=hard_stop\n", encoding="utf-8")
    response = client.get("/api/budget")
    assert response.status_code == 200
    assert response.json()["hard_stop_active"] is True
