"""Integration test: GET /api/search with injectable fake client."""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from flightrecorder.app import create_app
from flightrecorder.config import parse_config
from flightrecorder.runtime import build_runtime_context
from flightrecorder.web_search import SearchClient, SearchRequest, SearchResult


class FakeSearchClient:
    """Injectable fake that returns hardcoded results without network calls."""

    _results: list[SearchResult]
    last_request: SearchRequest | None = None

    def __init__(self, results: list[SearchResult] | None = None) -> None:
        self._results = results or []

    async def search(self, request: SearchRequest) -> list[SearchResult]:
        self.last_request = request
        candidates = [r for r in self._results if request.query.lower() in r.title.lower()]
        return candidates[:request.max_results]


def _make_app(tmp_path: Path, search_client: SearchClient | None) -> TestClient:
    config = parse_config({"paths": {"runtime_home": str(tmp_path)}})
    runtime = build_runtime_context(config)
    object.__setattr__(runtime, "search_client", search_client)
    return TestClient(create_app(config=config, runtime=runtime))


class TestSearchApi:

    def test_returns_normalized_results(self, tmp_path: Path) -> None:
        fake = FakeSearchClient(
            [
                SearchResult(
                    title="Karpathy on search",
                    url="https://karpathy.blog/2025/search",
                    snippet="autoregressive search post.",
                ),
                SearchResult(
                    title="Another post",
                    url="https://example.com",
                    snippet="not about karpathy.",
                ),
            ]
        )
        client = _make_app(tmp_path, fake)

        response = client.get("/api/search?q=karpathy")
        assert response.status_code == 200
        body = response.json()
        assert body["query"] == "karpathy"
        assert body["include_raw_content"] is False
        assert len(body["results"]) == 1
        assert body["results"][0]["title"] == "Karpathy on search"
        assert body["results"][0]["url"] == "https://karpathy.blog/2025/search"
        assert body["results"][0]["raw_content"] is None

    def test_passes_include_raw_content_to_client(self, tmp_path: Path) -> None:
        fake = FakeSearchClient(
            [
                SearchResult(
                    title="Karpathy raw",
                    url="https://example.com/raw",
                    snippet="raw",
                    raw_content="full page text",
                )
            ]
        )
        client = _make_app(tmp_path, fake)

        response = client.get("/api/search?q=karpathy&include_raw_content=true")

        assert response.status_code == 200
        assert fake.last_request is not None
        assert fake.last_request.include_raw_content is True
        assert response.json()["include_raw_content"] is True
        assert response.json()["results"][0]["raw_content"] == "full page text"

    def test_respects_max_results(self, tmp_path: Path) -> None:
        results = [
            SearchResult(title=f"Result {i}", url=f"https://example.com/{i}")
            for i in range(10)
        ]
        fake = FakeSearchClient(results)
        client = _make_app(tmp_path, fake)

        response = client.get("/api/search?q=result&max_results=3")
        assert response.status_code == 200
        assert len(response.json()["results"]) == 3

    def test_returns_503_when_no_client(self, tmp_path: Path) -> None:
        client = _make_app(tmp_path, None)
        response = client.get("/api/search?q=test")
        assert response.status_code == 503
        assert "search not configured" in response.json()["detail"]

    def test_returns_422_for_missing_query(self, tmp_path: Path) -> None:
        fake = FakeSearchClient()
        client = _make_app(tmp_path, fake)
        response = client.get("/api/search")
        assert response.status_code == 422

    def test_empty_query_rejected(self, tmp_path: Path) -> None:
        fake = FakeSearchClient()
        client = _make_app(tmp_path, fake)
        response = client.get("/api/search?q=")
        assert response.status_code == 422
