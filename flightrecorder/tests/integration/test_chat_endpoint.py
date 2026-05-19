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
from flightrecorder.providers import ChatEvent, TokenEvent, ToolCallEvent, UsageEvent
from flightrecorder.runtime import build_runtime_context
from flightrecorder.web_search import SearchRequest, SearchResult


class StubProvider:
    name: str = "stub"
    model: str = "stub-model"
    supports_images: bool = False
    max_context_tokens: int = 16000
    _events: list[ChatEvent]
    _should_raise: bool = False
    last_system: str | None = None
    last_messages: list | None = None
    last_tools: list[dict] | None = None
    call_count: int = 0
    call_messages: list[list]
    call_tools: list
    _multi_events: list[list[ChatEvent]] | None = None

    def __init__(
        self,
        events: list[ChatEvent] | None = None,
        should_raise: bool = False,
        multi_events: list[list[ChatEvent]] | None = None,
    ) -> None:
        self._events = events or []
        self._should_raise = should_raise
        self._multi_events = multi_events
        self.call_messages = []
        self.call_tools = []

    async def chat(
        self,
        messages: list,
        system: str | None = None,
        tools: list[dict] | None = None,
    ) -> AsyncIterator[ChatEvent]:
        self.last_system = system
        self.last_messages = messages
        self.last_tools = tools
        self.call_messages.append(messages)
        self.call_tools.append(tools)
        if self._should_raise:
            raise RuntimeError("stub provider failure")
        if self._multi_events is not None:
            idx = min(self.call_count, len(self._multi_events) - 1)
            self.call_count += 1
            for event in self._multi_events[idx]:
                yield event
        else:
            for event in self._events:
                yield event


def make_app(
    tmp_path: Path,
    stub_provider: StubProvider,
    with_pricing: bool = False,
    search_client: object | None = None,
) -> TestClient:
    config = parse_config(
        {
            "paths": {"runtime_home": str(tmp_path)},
            "budget": {"warn_at_dkk": 375, "hard_stop_dkk": 750, "currency": "DKK"},
        }
    )
    runtime = build_runtime_context(config)
    object.__setattr__(runtime, "brainstorm_provider", stub_provider)

    if search_client is not None:
        object.__setattr__(runtime, "search_client", search_client)

    if with_pricing:
        pricing = PricingTable(
            models={
                "stub-model": ModelPricing(
                    provider="stub",
                    model="stub-model",
                    input_per_1k=0.01,
                    output_per_1k=0.03,
                    cached_per_1k=0.001,
                    currency="DKK",
                )
            },
            exchange_rates_to_dkk={"DKK": 1.0},
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
    assert stub.last_system is not None
    assert "Daniel's thinking partner" in stub.last_system

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


class _FakeSearchClient:
    """In-memory search client for web_search tool-loop tests."""

    def __init__(self, results: list[SearchResult] | None = None) -> None:
        self.results: list[SearchResult] = results or []
        self.last_request: SearchRequest | None = None

    async def search(self, request: SearchRequest) -> list[SearchResult]:
        self.last_request = request
        return list(self.results)


def test_web_search_tool_loop_integration(tmp_path: Path) -> None:
    """Provider receives tools, ToolCallEvent triggers search, SSE has
    tool_round event, persisted session has sys audit + final assistant."""
    fake_results = [
        SearchResult(title="Result One", url="https://one.com", snippet="snippet one"),
        SearchResult(title="Result Two", url="https://two.com", snippet="snippet two"),
    ]
    fake_search = _FakeSearchClient(results=fake_results)

    stub = StubProvider(
        multi_events=[
            [
                ToolCallEvent(
                    id="call_1",
                    name="web_search",
                    arguments='{"query": "test query", "max_results": 2}',
                ),
                UsageEvent(input_tokens=100, output_tokens=50, cached_tokens=0),
            ],
            [
                TokenEvent(text="Here is the answer based on search."),
                UsageEvent(input_tokens=200, output_tokens=20, cached_tokens=0),
            ],
        ]
    )
    client = make_app(tmp_path, stub, with_pricing=True, search_client=fake_search)

    create = client.post(
        "/api/sessions",
        json={"provider": "stub", "model": "stub-model", "slug": "test"},
    )
    assert create.status_code == 201
    session_id = create.json()["session_id"]

    response = client.post(
        f"/api/sessions/{session_id}/messages",
        json={"content": "search for test"},
    )
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")

    events = sse_lines(response.text)

    # 1. Provider receives non-empty tools when search client is configured.
    assert len(stub.call_tools) >= 2
    assert stub.call_tools[0] is not None
    assert len(stub.call_tools[0]) == 1
    assert stub.call_tools[0][0]["function"]["name"] == "web_search"

    # 2. ToolCallEvent triggers a real search request on the fake client.
    assert fake_search.last_request is not None
    assert fake_search.last_request.query == "test query"
    assert fake_search.last_request.max_results == 2

    # The second provider round sees the assistant tool call and tool result
    # inside the same user turn.
    assert len(stub.call_messages) >= 2
    second_round_messages = stub.call_messages[1]
    second_round_roles = [m.role for m in second_round_messages]
    assert second_round_roles[-2:] == ["assistant", "tool"]
    assert second_round_messages[-2].tool_calls[0]["function"]["name"] == "web_search"
    assert second_round_messages[-1].tool_call_id == "call_1"
    tool_payload = json.loads(second_round_messages[-1].content)
    assert tool_payload[0]["title"] == "Result One"

    # 3. SSE stream includes a tool_round event.
    tool_events = [e for e in events if e["event"] == "tool_round"]
    assert len(tool_events) == 1
    assert tool_events[0]["data"]["name"] == "web_search"
    assert tool_events[0]["data"]["ok"] is True
    assert tool_events[0]["data"]["result_count"] == 2
    assert tool_events[0]["data"]["query"] == "test query"

    # 4. SSE stream ends with done.
    done_events = [e for e in events if e["event"] == "done"]
    assert len(done_events) == 1

    # 5. Persisted session contains sys audit message and final assistant.
    detail = client.get(f"/api/sessions/{session_id}")
    assert detail.status_code == 200
    body = detail.json()
    messages = body["messages"]

    sys_msgs = [m for m in messages if m["role"] == "sys"]
    assert len(sys_msgs) == 1
    assert "web_search" in sys_msgs[0]["content"]
    assert "test query" in sys_msgs[0]["content"]
    assert "2 results" in sys_msgs[0]["content"]

    asst_msgs = [m for m in messages if m["role"] == "assistant"]
    assert len(asst_msgs) == 1
    assert "Here is the answer" in asst_msgs[0]["content"]

    # Message ordering: user, sys, assistant.
    roles = [m["role"] for m in messages]
    assert roles == ["user", "sys", "assistant"], f"unexpected roles: {roles}"


def test_sys_messages_not_replayed_on_next_turn(tmp_path: Path) -> None:
    """After a tool-loop turn persists sys audit lines, the next chat turn
    must not replay those sys messages back to the provider."""
    fake_search = _FakeSearchClient(
        results=[SearchResult(title="X", url="https://x.com", snippet="x")]
    )

    stub = StubProvider(
        multi_events=[
            [
                ToolCallEvent(
                    id="tc1",
                    name="web_search",
                    arguments='{"query": "q1"}',
                ),
                UsageEvent(input_tokens=100, output_tokens=50, cached_tokens=0),
            ],
            [
                TokenEvent(text="answer one"),
                UsageEvent(input_tokens=200, output_tokens=20, cached_tokens=0),
            ],
        ]
    )
    client = make_app(tmp_path, stub, with_pricing=True, search_client=fake_search)

    create = client.post(
        "/api/sessions",
        json={"provider": "stub", "model": "stub-model", "slug": "test"},
    )
    session_id = create.json()["session_id"]

    # First turn: tool loop completes, persisting user + sys + assistant.
    client.post(
        f"/api/sessions/{session_id}/messages",
        json={"content": "search q1"},
    )

    # Reset call tracking and swap to a plain provider for the second turn.
    stub.call_count = 0
    stub.call_messages = []
    stub.call_tools = []
    stub._multi_events = [
        [
            TokenEvent(text="second answer no search"),
            UsageEvent(input_tokens=50, output_tokens=10, cached_tokens=0),
        ]
    ]

    # Second turn: plain message, no tool calls expected.
    response2 = client.post(
        f"/api/sessions/{session_id}/messages",
        json={"content": "hello again"},
    )
    assert response2.status_code == 200

    # The provider must not see any sys or tool messages replayed.
    assert len(stub.call_messages) >= 1
    second_call_msgs = stub.call_messages[0]
    roles_seen = [m.role for m in second_call_msgs]
    assert "sys" not in roles_seen, f"sys replayed: {roles_seen}"
    assert "tool" not in roles_seen, f"tool replayed: {roles_seen}"

    # But the persisted session still carries the first turn's sys lines.
    detail = client.get(f"/api/sessions/{session_id}")
    body = detail.json()
    roles_all = [m["role"] for m in body["messages"]]
    assert "sys" in roles_all
    assert body["messages"][-1]["role"] == "assistant"
    assert "second answer" in body["messages"][-1]["content"]
