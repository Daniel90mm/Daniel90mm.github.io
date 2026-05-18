"""Round-trip integration test: chat -> extract -> verify full pipeline."""

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


class BrainstormStub:
    name: str = "stub"
    model: str = "stub-brainstorm"
    supports_images: bool = False
    max_context_tokens: int = 16000
    _reply: str
    _usage: UsageEvent

    def __init__(
        self,
        reply: str = "Good idea, let's prototype the AC/DC ratio circuit.",
        usage: UsageEvent | None = None,
    ) -> None:
        self._reply = reply
        self._usage = usage or UsageEvent(input_tokens=200, output_tokens=50)

    async def chat(
        self,
        messages: list,
        system: str | None = None,
    ) -> AsyncIterator[ChatEvent]:
        for char in self._reply:
            yield TokenEvent(text=char)
        yield self._usage


class ExtractStub:
    name: str = "stub"
    model: str = "stub-extract"
    supports_images: bool = False
    max_context_tokens: int = 16000
    _response: str
    _usage: UsageEvent

    def __init__(
        self,
        response: str | None = None,
        usage: UsageEvent | None = None,
    ) -> None:
        self._response = response or json.dumps(
            [
                {
                    "type": "project_append",
                    "project_ref": "pulse-oximeter",
                    "section": "TODOs",
                    "content": "prototype the AC/DC ratio circuit",
                },
                {
                    "type": "spaghetti",
                    "tags": ["signal-processing"],
                    "topics": ["medical-devices"],
                    "content": "AC/DC ratio filtering for reflectance signals.",
                },
            ]
        )
        self._usage = usage or UsageEvent(input_tokens=500, output_tokens=100)

    async def chat(
        self,
        messages: list,
        system: str | None = None,
    ) -> AsyncIterator[ChatEvent]:
        for i in range(0, len(self._response), 8):
            yield TokenEvent(text=self._response[i:i + 8])
        yield self._usage


def _make_pricing() -> PricingTable:
    return PricingTable(
        models={
            "stub-brainstorm": ModelPricing(
                provider="stub",
                model="stub-brainstorm",
                input_per_1k=0.01,
                output_per_1k=0.03,
                cached_per_1k=0.0,
                currency="DKK",
            ),
            "stub-extract": ModelPricing(
                provider="stub",
                model="stub-extract",
                input_per_1k=0.01,
                output_per_1k=0.03,
                cached_per_1k=0.0,
                currency="DKK",
            ),
        },
        exchange_rates_to_dkk={"DKK": 1.0},
    )


def test_round_trip_chat_then_extract(tmp_path: Path) -> None:
    assistant_reply = "That's a great idea. Let's prototype the circuit."
    brainstorm = BrainstormStub(reply=assistant_reply)
    extract = ExtractStub()

    config = parse_config(
        {
            "paths": {"runtime_home": str(tmp_path)},
            "budget": {"warn_at_dkk": 7500, "hard_stop_dkk": 15000, "currency": "DKK"},
        }
    )
    runtime = build_runtime_context(config)
    object.__setattr__(runtime, "brainstorm_provider", brainstorm)
    object.__setattr__(runtime, "idea_capture_provider", extract)
    object.__setattr__(runtime, "pricing", _make_pricing())

    app = create_app(config=config, runtime=runtime)
    client = TestClient(app)

    create = client.post(
        "/api/sessions",
        json={"provider": "stub", "model": "stub-brainstorm", "slug": "pulse-ox-acdc"},
    )
    assert create.status_code == 201
    session_id = create.json()["session_id"]

    chat_response = client.post(
        f"/api/sessions/{session_id}/messages",
        json={"content": "Let's work on the pulse-oximeter AC/DC ratio"},
    )
    assert chat_response.status_code == 200

    extract_response = client.post(f"/api/sessions/{session_id}/extract")
    assert extract_response.status_code == 200
    extract_body = extract_response.json()
    assert extract_body["session_id"] == session_id
    assert extract_body["project_appends"] == 1
    assert extract_body["spaghetti"] == 1

    detail_response = client.get(f"/api/sessions/{session_id}")
    assert detail_response.status_code == 200
    detail = detail_response.json()
    assert detail["message_count"] == 2
    assert len(detail["messages"]) == 2
    assert detail["messages"][0]["role"] == "user"
    assert "pulse-oximeter AC/DC ratio" in detail["messages"][0]["content"]
    assert detail["messages"][1]["role"] == "assistant"
    assert detail["messages"][1]["content"] == assistant_reply

    doc_path = tmp_path / "documents" / "pulse-oximeter.md"
    assert doc_path.exists()
    doc_text = doc_path.read_text(encoding="utf-8")
    assert "prototype the AC/DC ratio circuit" in doc_text

    spaghetti_files = list((tmp_path / "spaghetti").glob("*.md"))
    assert len(spaghetti_files) == 1

    db = sqlite3.connect(str(tmp_path / "metadata.db"))
    try:
        ideas_row = db.execute(
            "SELECT COUNT(*), source_session FROM ideas GROUP BY source_session"
        ).fetchone()
        assert ideas_row == (1, session_id)

        api_calls = db.execute(
            "SELECT role, session_id FROM api_calls ORDER BY id"
        ).fetchall()
        assert len(api_calls) == 2
        assert api_calls[0][0] == "brainstorm"
        assert api_calls[0][1] == session_id
        assert api_calls[1][0] == "idea_capture"
        assert api_calls[1][1] == session_id

        session_row = db.execute(
            "SELECT extracted, extracted_at FROM sessions WHERE session_id = ?",
            (session_id,),
        ).fetchone()
        assert session_row[0] == 1
        assert session_row[1] is not None
    finally:
        db.close()
