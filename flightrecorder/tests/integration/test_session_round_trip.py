"""Integration test for a full session chat -> extract round trip."""

from __future__ import annotations

import json
import sqlite3
from collections.abc import AsyncIterator
from pathlib import Path

from fastapi.testclient import TestClient

from flightrecorder.app import create_app
from flightrecorder.config import parse_config
from flightrecorder.costs import ModelPricing, PricingTable
from flightrecorder.providers import ChatEvent, TokenEvent, UsageEvent
from flightrecorder.runtime import build_runtime_context


class ChatStub:
    name: str = "stub"
    model: str = "stub-brainstorm"
    supports_images: bool = False
    max_context_tokens: int = 16000

    def __init__(self, events: list[ChatEvent]) -> None:
        self._events = events

    async def chat(
        self,
        messages: list,
        system: str | None = None,
    ) -> AsyncIterator[ChatEvent]:
        for event in self._events:
            yield event


class ExtractorStub:
    name: str = "stub"
    model: str = "stub-extractor"
    supports_images: bool = False
    max_context_tokens: int = 16000

    def __init__(self, response_text: str, usage: UsageEvent) -> None:
        self._response_text = response_text
        self._usage = usage

    async def chat(
        self,
        messages: list,
        system: str | None = None,
    ) -> AsyncIterator[ChatEvent]:
        for i in range(0, len(self._response_text), 5):
            yield TokenEvent(text=self._response_text[i:i + 5])
        yield self._usage


def make_app(
    tmp_path: Path,
    chat_stub: ChatStub,
    extractor_stub: ExtractorStub,
) -> TestClient:
    config = parse_config(
        {
            "paths": {"runtime_home": str(tmp_path)},
            "budget": {"warn_at_dkk": 375, "hard_stop_dkk": 750, "currency": "DKK"},
        }
    )
    runtime = build_runtime_context(config)

    pricing = PricingTable(
        models={
            "stub-brainstorm": ModelPricing(
                provider="stub",
                model="stub-brainstorm",
                input_per_1k=0.01,
                output_per_1k=0.03,
                cached_per_1k=0.001,
                currency="DKK",
            ),
            "stub-extractor": ModelPricing(
                provider="stub",
                model="stub-extractor",
                input_per_1k=0.01,
                output_per_1k=0.03,
                cached_per_1k=0.0,
                currency="DKK",
            ),
        },
        exchange_rates_to_dkk={"DKK": 1.0},
    )
    object.__setattr__(runtime, "brainstorm_provider", chat_stub)
    object.__setattr__(runtime, "idea_capture_provider", extractor_stub)
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


def test_session_chat_extract_round_trip(tmp_path: Path) -> None:
    appended_bullet = "Capture AC/DC ratio notes for the pulse-oximeter design."
    chat_stub = ChatStub(
        events=[
            TokenEvent(text="We can track the AC/DC ratio in the "),
            TokenEvent(text="pulse-oximeter pipeline."),
            UsageEvent(input_tokens=100, output_tokens=25, cached_tokens=0),
        ]
    )
    extractor_stub = ExtractorStub(
        response_text=json.dumps(
            [
                {
                    "type": "project_append",
                    "project_ref": "pulse-oximeter",
                    "section": "Ideas",
                    "content": appended_bullet,
                },
                {
                    "type": "spaghetti",
                    "tags": ["pulse-oximeter"],
                    "topics": ["signal-processing"],
                    "content": "Consider normalizing the AC/DC ratio before alerts.",
                },
            ]
        ),
        usage=UsageEvent(input_tokens=500, output_tokens=120, cached_tokens=0),
    )
    client = make_app(tmp_path, chat_stub, extractor_stub)

    create = client.post(
        "/api/sessions",
        json={"provider": "stub", "model": "stub-brainstorm", "slug": "round-trip"},
    )
    assert create.status_code == 201
    session_id = create.json()["session_id"]

    message = client.post(
        f"/api/sessions/{session_id}/messages",
        json={"content": "Let's work on the pulse-oximeter AC/DC ratio"},
    )
    assert message.status_code == 200
    events = sse_lines(message.text)
    assert events[-1]["event"] == "done"

    extract = client.post(f"/api/sessions/{session_id}/extract")
    assert extract.status_code == 200
    assert extract.json()["project_appends"] == 1
    assert extract.json()["spaghetti"] == 1

    detail = client.get(f"/api/sessions/{session_id}")
    assert detail.status_code == 200
    body = detail.json()
    assert body["message_count"] == 2
    assert [message["role"] for message in body["messages"]] == ["user", "assistant"]
    assert "pulse-oximeter AC/DC ratio" in body["messages"][0]["content"]
    assert body["messages"][1]["content"] == (
        "We can track the AC/DC ratio in the pulse-oximeter pipeline."
    )

    doc_path = tmp_path / "documents" / "pulse-oximeter.md"
    assert doc_path.exists()
    assert appended_bullet in doc_path.read_text(encoding="utf-8")

    spaghetti_files = list((tmp_path / "spaghetti").glob("*.md"))
    assert len(spaghetti_files) == 1

    db = sqlite3.connect(str(tmp_path / "metadata.db"))
    try:
        ideas_row = db.execute(
            "SELECT COUNT(*), source_session FROM ideas GROUP BY source_session"
        ).fetchone()
        assert ideas_row == (1, session_id)

        api_call_rows = db.execute(
            "SELECT role, session_id FROM api_calls ORDER BY id"
        ).fetchall()
        assert api_call_rows == [
            ("brainstorm", session_id),
            ("idea_capture", session_id),
        ]

        session_row = db.execute(
            "SELECT extracted, extracted_at FROM sessions WHERE session_id = ?",
            (session_id,),
        ).fetchone()
        assert session_row[0] == 1
        assert session_row[1]
    finally:
        db.close()
