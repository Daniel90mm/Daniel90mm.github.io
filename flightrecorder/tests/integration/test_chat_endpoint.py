"""Integration tests for POST /api/sessions/{session_id}/messages SSE chat endpoint."""

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


class StubProvider:
    name: str = "stub"
    model: str = "stub-model"
    supports_images: bool = False
    max_context_tokens: int = 16000
    _events: list[ChatEvent]
    _should_raise: bool = False

    def __init__(
        self,
        events: list[ChatEvent] | None = None,
        should_raise: bool = False,
    ) -> None:
        self._events = events or []
        self._should_raise = should_raise

    async def chat(
        self,
        messages: list,
        system: str | None = None,
    ) -> AsyncIterator[ChatEvent]:
        if self._should_raise:
            raise RuntimeError("stub provider failure")
        for event in self._events:
            yield event


def make_app(
    tmp_path: Path,
    stub_provider: StubProvider,
    with_pricing: bool = False,
) -> TestClient:
    config = parse_config(
        {
            "paths": {"runtime_home": str(tmp_path)},
            "budget": {"warn_at_eur": 5, "hard_stop_eur": 10, "currency": "EUR"},
        }
    )
    runtime = build_runtime_context(config)
    object.__setattr__(runtime, "brainstorm_provider", stub_provider)

    if with_pricing:
        pricing = PricingTable(
            models={
                "stub-model": ModelPricing(
                    provider="stub",
                    model="stub-model",
                    input_per_1k=0.01,
                    output_per_1k=0.03,
                    cached_per_1k=0.001,
                    currency="EUR",
                )
            },
            exchange_rates_to_eur={"EUR": 1.0},
        )
        object.__setattr__(runtime, "pricing", pricing)

    app = create_app(config=config, runtime=runtime)
    return TestClient(app)


def sse_lines(response_text: str) -> list[dict[str, object]]:
    events: list[dict[str, object]] = []
    current_event: str | None = None
    for line in response_text.strip().split("\n"):
        if line.startswith("event: "):
            current_event = line[len("event: "):]
        elif line.startswith("data: "):
            data = json.loads(line[len("data: "):])
            events.append({"event": current_event, "data": data})
            current_event = None
    return events


def test_happy_path_sse_stream(tmp_path: Path) -> None:
    stub = StubProvider(
        events=[
            TokenEvent(text="Hello "),
            TokenEvent(text="world"),
            UsageEvent(input_tokens=100, output_tokens=50, cached_tokens=0),
        ]
    )
    client = make_app(tmp_path, stub, with_pricing=True)

    create = client.post(
        "/api/sessions",
        json={"provider": "stub", "model": "stub-model", "slug": "test"},
    )
    assert create.status_code == 201
    session_id = create.json()["session_id"]

    response = client.post(
        f"/api/sessions/{session_id}/messages",
        json={"content": "hi"},
    )
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")

    events = sse_lines(response.text)
    assert len(events) >= 2
    assert events[0]["event"] == "token"
    assert events[-1]["event"] == "done"
    assert events[-1]["data"]["input_tokens"] == 100
    assert events[-1]["data"]["output_tokens"] == 50

    detail = client.get(f"/api/sessions/{session_id}")
    assert detail.status_code == 200
    body = detail.json()
    assert body["message_count"] == 2
    assert len(body["messages"]) == 2
    assert body["messages"][0]["role"] == "user"
    assert body["messages"][1]["role"] == "assistant"
    assert body["messages"][1]["content"] == "Hello world"

    db_path = tmp_path / "metadata.db"
    db = sqlite3.connect(str(db_path))
    row = db.execute("SELECT COUNT(*) FROM api_calls").fetchone()
    assert row[0] == 1
    db.close()


def test_empty_content_returns_400(tmp_path: Path) -> None:
    stub = StubProvider()
    client = make_app(tmp_path, stub)

    create = client.post(
        "/api/sessions",
        json={"provider": "stub", "model": "stub-model", "slug": "test"},
    )
    session_id = create.json()["session_id"]

    response = client.post(
        f"/api/sessions/{session_id}/messages",
        json={"content": ""},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "content is required"


def test_unknown_session_returns_404(tmp_path: Path) -> None:
    stub = StubProvider()
    client = make_app(tmp_path, stub)

    response = client.post(
        "/api/sessions/nonexistent-id/messages",
        json={"content": "hi"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Session not found"


def test_provider_error_mid_stream_preserves_user_message(tmp_path: Path) -> None:
    stub = StubProvider(should_raise=True)
    client = make_app(tmp_path, stub)

    create = client.post(
        "/api/sessions",
        json={"provider": "stub", "model": "stub-model", "slug": "test"},
    )
    session_id = create.json()["session_id"]

    response = client.post(
        f"/api/sessions/{session_id}/messages",
        json={"content": "hi"},
    )
    assert response.status_code == 200

    events = sse_lines(response.text)
    assert events[-1]["event"] == "error"

    detail = client.get(f"/api/sessions/{session_id}")
    body = detail.json()
    assert body["message_count"] == 1
    assert len(body["messages"]) == 1
    assert body["messages"][0]["role"] == "user"


def test_budget_hard_stop_blocks_call(tmp_path: Path) -> None:
    budget_path = tmp_path / "budget"
    budget_path.write_text("status=hard_stop\n", encoding="utf-8")

    stub = StubProvider(
        events=[
            TokenEvent(text="should not see this"),
            UsageEvent(input_tokens=1, output_tokens=1),
        ]
    )
    client = make_app(tmp_path, stub)

    create = client.post(
        "/api/sessions",
        json={"provider": "stub", "model": "stub-model", "slug": "test"},
    )
    session_id = create.json()["session_id"]

    response = client.post(
        f"/api/sessions/{session_id}/messages",
        json={"content": "hi"},
    )
    assert response.status_code == 503
    assert response.json()["detail"] == "Budget hard-stop active"

    db_path = tmp_path / "metadata.db"
    db = sqlite3.connect(str(db_path))
    row = db.execute("SELECT COUNT(*) FROM api_calls").fetchone()
    assert row[0] == 0
    db.close()
