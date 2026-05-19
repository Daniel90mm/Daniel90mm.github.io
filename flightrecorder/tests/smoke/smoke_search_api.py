"""Smoke test: exercise GET /api/search with injected fake search client."""

from __future__ import annotations

import tempfile
from pathlib import Path

from fastapi.testclient import TestClient

from flightrecorder.app import create_app
from flightrecorder.config import parse_config
from flightrecorder.runtime import build_runtime_context
from flightrecorder.web_search import SearchRequest, SearchResult


class FakeSearchClient:
    """In-memory search client for smoke testing. Records the last request."""

    def __init__(self, results: list[SearchResult] | None = None) -> None:
        self._results: list[SearchResult] = results or []
        self.last_request: SearchRequest | None = None

    async def search(self, request: SearchRequest) -> list[SearchResult]:
        self.last_request = request
        return list(self._results)


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)

        config = parse_config({"paths": {"runtime_home": str(tmp_path)}})
        runtime = build_runtime_context(config)

        fake_client = FakeSearchClient(
            results=[
                SearchResult(
                    title="Test Title",
                    url="https://example.com",
                    snippet="A test snippet.",
                    raw_content="Full raw content.",
                )
            ]
        )

        object.__setattr__(runtime, "search_client", fake_client)
        app = create_app(config=config, runtime=runtime)
        client = TestClient(app)

        # 1. Configured fake client returns normalized results.
        resp = client.get("/api/search?q=test")
        assert resp.status_code == 200, f"expected 200, got {resp.status_code}"
        data = resp.json()
        assert data["query"] == "test"
        assert data["include_raw_content"] is False
        results = data["results"]
        assert len(results) == 1
        assert results[0]["title"] == "Test Title"
        assert results[0]["url"] == "https://example.com"
        assert results[0]["snippet"] == "A test snippet."
        assert results[0]["raw_content"] == "Full raw content."

        # 2. include_raw_content=true is passed through to the search client.
        assert fake_client.last_request is not None
        resp2 = client.get("/api/search?q=other&include_raw_content=true")
        assert resp2.status_code == 200
        assert fake_client.last_request.query == "other"
        assert fake_client.last_request.include_raw_content is True

        # 3. Missing search client returns 503.
        object.__setattr__(runtime, "search_client", None)
        resp3 = client.get("/api/search?q=test")
        assert resp3.status_code == 503
        assert resp3.json()["detail"] == "search not configured"

        print("search API smoke test passed")


if __name__ == "__main__":
    main()
