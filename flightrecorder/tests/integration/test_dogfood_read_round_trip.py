"""Integration test: full dogfood read path from extraction through inspection."""

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
    _output_text: str
    _with_usage: bool

    def __init__(self, output_text: str = "", with_usage: bool = True) -> None:
        self._output_text = output_text
        self._with_usage = with_usage

    async def chat(
        self,
        messages: list,
        system: str | None = None,
        tools: list[dict] | None = None,
    ) -> AsyncIterator[ChatEvent]:
        for i in range(0, len(self._output_text), 5):
            yield TokenEvent(text=self._output_text[i:i + 5])
        if self._with_usage:
            yield UsageEvent(input_tokens=10, output_tokens=5, cached_tokens=0)


def make_app(tmp_path: Path) -> TestClient:
    config = parse_config(
        {
            "paths": {"runtime_home": str(tmp_path)},
            "budget": {"warn_at_dkk": 375, "hard_stop_dkk": 750, "currency": "DKK"},
        }
    )
    runtime = build_runtime_context(config)

    stub = StubProvider()
    object.__setattr__(runtime, "brainstorm_provider", stub)

    extractor = StubProvider(
        output_text=json.dumps(
            [
                {
                    "type": "project_append",
                    "project_ref": "roundtrip",
                    "section": "TODOs",
                    "content": "verify full round trip path.",
                },
                {
                    "type": "spaghetti",
                    "tags": ["testing"],
                    "topics": ["roundtrip"],
                    "content": "Integration test for read path.",
                },
            ]
        )
    )
    object.__setattr__(runtime, "idea_capture_provider", extractor)

    pricing = PricingTable(
        models={
            "stub-model": ModelPricing(
                provider="stub",
                model="stub-model",
                input_per_1k=0.01,
                output_per_1k=0.03,
                cached_per_1k=0.0,
                currency="DKK",
            )
        },
        exchange_rates_to_dkk={"DKK": 1.0},
    )
    object.__setattr__(runtime, "pricing", pricing)

    app = create_app(config=config, runtime=runtime)
    return TestClient(app)


def test_read_round_trip(tmp_path: Path) -> None:
    client = make_app(tmp_path)

    create_resp = client.post(
        "/api/sessions",
        json={"provider": "stub", "model": "stub-model", "slug": "roundtrip"},
    )
    assert create_resp.status_code == 201
    session_id = create_resp.json()["session_id"]

    chat_resp = client.post(
        f"/api/sessions/{session_id}/messages",
        json={"content": "Test the read path."},
    )
    assert chat_resp.status_code == 200

    extract_resp = client.post(f"/api/sessions/{session_id}/extract")
    assert extract_resp.status_code == 200
    extract_body = extract_resp.json()
    assert extract_body["project_appends"] == 1
    assert extract_body["spaghetti"] == 1

    docs_resp = client.get("/api/documents")
    assert docs_resp.status_code == 200
    docs = docs_resp.json()["documents"]
    assert len(docs) >= 1
    roundtrip_doc = [d for d in docs if d["ref"] == "roundtrip"][0]

    doc_detail = client.get("/api/documents/roundtrip")
    assert doc_detail.status_code == 200
    assert "verify full round trip path" in doc_detail.json()["body"]

    spag_resp = client.get("/api/spaghetti")
    assert spag_resp.status_code == 200
    ideas = spag_resp.json()["ideas"]
    assert len(ideas) >= 1

    idea_id = ideas[0]["idea_id"]
    idea_detail = client.get(f"/api/spaghetti/{idea_id}")
    assert idea_detail.status_code == 200
    assert "Integration test for read path" in idea_detail.json()["body"]

    db_path = tmp_path / "metadata.db"
    db = sqlite3.connect(str(db_path))
    row = db.execute(
        "SELECT COUNT(*) FROM api_calls WHERE session_id = ?",
        (session_id,),
    ).fetchone()
    assert row[0] == 2
    db.close()
