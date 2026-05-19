"""Smoke test: end-to-end frontend/API dogfood loop."""

from __future__ import annotations

import json
import sys
import tempfile
from collections.abc import AsyncIterator
from pathlib import Path

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

    def __init__(self, output_text: str = "Hello from stub", with_usage: bool = True) -> None:
        self._output_text = output_text
        self._with_usage = with_usage

    async def chat(
        self,
        messages: list,
        system: str | None = None,
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
                    "project_ref": "dogfood",
                    "section": "TODOs",
                    "content": "verify dogfood route smoke.",
                },
                {
                    "type": "spaghetti",
                    "tags": ["smoke"],
                    "topics": ["testing"],
                    "content": "dogfood route smoke for frontend backend loop.",
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


def sse_events(response_text: str) -> list[dict]:
    events: list[dict] = []
    current_event: str | None = None
    for line in response_text.strip().split("\n"):
        if line.startswith("event: "):
            current_event = line[len("event: "):]
        elif line.startswith("data: "):
            try:
                data = json.loads(line[len("data: "):])
                events.append({"event": current_event, "data": data})
            except json.JSONDecodeError:
                pass
            current_event = None
    return events


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        client = make_app(tmp_path)

        response = client.get("/")
        assert response.status_code == 200, f"GET / returned {response.status_code}"
        assert "flightrecorder" in response.text, "frontend not found in GET /"

        app_js_resp = client.get("/assets/app.js")
        assert app_js_resp.status_code == 200
        app_js_text = app_js_resp.text
        assert '"/api/budget"' in app_js_text or "api/budget" in app_js_text
        assert '"/api/documents"' in app_js_text or "api/documents" in app_js_text
        assert '"/api/spaghetti"' in app_js_text or "api/spaghetti" in app_js_text
        assert '"/api/runtime"' in app_js_text or "api/runtime" in app_js_text

        budget_resp = client.get("/api/budget")
        assert budget_resp.status_code == 200
        assert budget_resp.json()["status"] == "ok"

        create_resp = client.post(
            "/api/sessions",
            json={"provider": "stub", "model": "stub-model", "slug": "dogfood-test"},
        )
        assert create_resp.status_code == 201, f"create session: {create_resp.status_code}"
        session_id = create_resp.json()["session_id"]

        chat_resp = client.post(
            f"/api/sessions/{session_id}/messages",
            json={"content": "Hello from dogfood smoke"},
        )
        assert chat_resp.status_code == 200, f"chat: {chat_resp.status_code}"
        assert chat_resp.headers["content-type"].startswith("text/event-stream")
        events = sse_events(chat_resp.text)
        assert len(events) >= 2, f"expected >= 2 SSE events, got {len(events)}"
        assert events[0]["event"] == "token", f"first event not token: {events[0]}"
        last_events = [e for e in events if e["event"] == "done"]
        assert len(last_events) >= 1, "no done event"

        extract_resp = client.post(f"/api/sessions/{session_id}/extract")
        assert extract_resp.status_code == 200, f"extract: {extract_resp.status_code} {extract_resp.text}"
        extract_body = extract_resp.json()
        assert extract_body["session_id"] == session_id
        assert extract_body["project_appends"] == 1
        assert extract_body["spaghetti"] == 1

        detail_resp = client.get(f"/api/sessions/{session_id}")
        assert detail_resp.status_code == 200
        detail = detail_resp.json()
        assert detail["message_count"] == 2, f"expected 2 messages, got {detail['message_count']}"

        print("frontend dogfood smoke test passed")


if __name__ == "__main__":
    main()
