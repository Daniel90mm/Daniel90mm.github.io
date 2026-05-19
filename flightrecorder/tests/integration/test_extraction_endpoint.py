"""Integration tests for POST /api/sessions/{session_id}/extract idea-capture endpoint."""

from __future__ import annotations

import json
import sqlite3
from collections.abc import AsyncIterator
from datetime import datetime, timezone
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from flightrecorder.app import create_app
from flightrecorder.config import parse_config
from flightrecorder.costs import ModelPricing, PricingTable
from flightrecorder.providers import ChatEvent, TokenEvent, UsageEvent
from flightrecorder.runtime import build_runtime_context
from flightrecorder.storage import ChatMessage


class ExtractorStub:
    name: str = "stub"
    model: str = "stub-extractor"
    supports_images: bool = False
    max_context_tokens: int = 16000
    _response_text: str = ""
    _usage: UsageEvent | None = None
    _should_raise: bool = False

    def __init__(
        self,
        response_text: str = "",
        usage: UsageEvent | None = None,
        should_raise: bool = False,
    ) -> None:
        self._response_text = response_text
        self._usage = usage
        self._should_raise = should_raise

    async def chat(
        self,
        messages: list,
        system: str | None = None,
        tools: list[dict] | None = None,
    ) -> AsyncIterator[ChatEvent]:
        if self._should_raise:
            raise RuntimeError("stub extractor failure")
        for i in range(0, len(self._response_text), 5):
            yield TokenEvent(text=self._response_text[i:i + 5])
        if self._usage:
            yield self._usage


def make_app(tmp_path: Path, stub_extractor: ExtractorStub) -> TestClient:
    config = parse_config(
        {
            "paths": {"runtime_home": str(tmp_path)},
            "budget": {"warn_at_dkk": 375, "hard_stop_dkk": 750, "currency": "DKK"},
        }
    )
    runtime = build_runtime_context(config)

    pricing = PricingTable(
        models={
            "stub-extractor": ModelPricing(
                provider="stub",
                model="stub-extractor",
                input_per_1k=0.01,
                output_per_1k=0.03,
                cached_per_1k=0.0,
                currency="DKK",
            )
        },
        exchange_rates_to_dkk={"DKK": 1.0},
    )
    object.__setattr__(runtime, "idea_capture_provider", stub_extractor)
    object.__setattr__(runtime, "pricing", pricing)

    app = create_app(config=config, runtime=runtime)
    return TestClient(app)


def create_session_with_message(client: TestClient) -> str:
    create = client.post(
        "/api/sessions",
        json={"provider": "google", "model": "gemini-2.5-pro", "slug": "test"},
    )
    assert create.status_code == 201
    session_id = create.json()["session_id"]

    runtime = client.app.state.runtime
    runtime.sessions.add_message(
        session_id,
        ChatMessage(
            role="user",
            timestamp=datetime.now(timezone.utc).isoformat(),
            content="Let's discuss the fNIRS amplifier stage.",
        ),
    )
    runtime.sessions.add_message(
        session_id,
        ChatMessage(
            role="assistant",
            timestamp=datetime.now(timezone.utc).isoformat(),
            content="The differential amplifier stage is a key component.",
        ),
    )
    return session_id


def test_happy_path_extracts_and_routes(tmp_path: Path) -> None:
    stub = ExtractorStub(
        response_text=json.dumps(
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
                    "topics": ["signal-processing"],
                    "content": "PCA for multivariate signal denoising.",
                },
            ]
        ),
        usage=UsageEvent(input_tokens=500, output_tokens=100, cached_tokens=0),
    )
    client = make_app(tmp_path, stub)
    session_id = create_session_with_message(client)

    response = client.post(f"/api/sessions/{session_id}/extract")
    assert response.status_code == 200
    body = response.json()

    assert body["session_id"] == session_id
    assert body["project_appends"] == 1
    assert body["spaghetti"] == 1
    assert body["documents_committed"] is True

    doc_path = tmp_path / "documents" / "fnirs.md"
    assert doc_path.exists()
    assert "prototype the amplifier" in doc_path.read_text(encoding="utf-8")

    spaghetti_files = list((tmp_path / "spaghetti").glob("*.md"))
    assert len(spaghetti_files) >= 1

    db_path = tmp_path / "metadata.db"
    db = sqlite3.connect(str(db_path))
    row = db.execute(
        "SELECT COUNT(*) FROM api_calls WHERE role = 'idea_capture'"
    ).fetchone()
    assert row[0] == 1

    ideas_row = db.execute("SELECT COUNT(*) FROM ideas").fetchone()
    assert ideas_row[0] == 1
    db.close()


def test_malformed_output_logs_usage_but_no_operations(tmp_path: Path) -> None:
    stub = ExtractorStub(
        response_text="not json",
        usage=UsageEvent(input_tokens=100, output_tokens=20, cached_tokens=0),
    )
    client = make_app(tmp_path, stub)
    session_id = create_session_with_message(client)

    response = client.post(f"/api/sessions/{session_id}/extract")
    assert response.status_code == 422

    db_path = tmp_path / "metadata.db"
    db = sqlite3.connect(str(db_path))
    row = db.execute(
        "SELECT COUNT(*) FROM api_calls WHERE role = 'idea_capture'"
    ).fetchone()
    assert row[0] == 1

    ideas_row = db.execute("SELECT COUNT(*) FROM ideas").fetchone()
    assert ideas_row[0] == 0

    spaghetti_dir = tmp_path / "spaghetti"
    spaghetti_files = list(spaghetti_dir.glob("*.md")) if spaghetti_dir.exists() else []
    assert len(spaghetti_files) == 0
    db.close()


def test_no_usage_returns_502(tmp_path: Path) -> None:
    stub = ExtractorStub(response_text="some text", usage=None)
    client = make_app(tmp_path, stub)
    session_id = create_session_with_message(client)

    response = client.post(f"/api/sessions/{session_id}/extract")
    assert response.status_code == 502
    assert response.json()["detail"] == "idea-capture provider returned no usage"

    db_path = tmp_path / "metadata.db"
    db = sqlite3.connect(str(db_path))
    row = db.execute("SELECT COUNT(*) FROM api_calls").fetchone()
    assert row[0] == 0
    db.close()


def test_budget_hard_stop_blocks_extraction(tmp_path: Path) -> None:
    budget_path = tmp_path / "budget"
    budget_path.write_text("status=hard_stop\n", encoding="utf-8")

    stub = ExtractorStub(
        response_text=json.dumps([]),
        usage=UsageEvent(input_tokens=1, output_tokens=1),
    )
    client = make_app(tmp_path, stub)
    session_id = create_session_with_message(client)

    response = client.post(f"/api/sessions/{session_id}/extract")
    assert response.status_code == 503
    assert response.json()["detail"] == "Budget hard-stop active"

    db_path = tmp_path / "metadata.db"
    db = sqlite3.connect(str(db_path))
    row = db.execute("SELECT COUNT(*) FROM api_calls").fetchone()
    assert row[0] == 0
    db.close()


def test_unknown_session_returns_404(tmp_path: Path) -> None:
    stub = ExtractorStub()
    client = make_app(tmp_path, stub)

    response = client.post("/api/sessions/nonexistent/extract")
    assert response.status_code == 404
    assert response.json()["detail"] == "Session not found"
