"""Unit tests for flightrecorder.web_search normalization."""

from __future__ import annotations

from urllib import error

import pytest

from flightrecorder.web_search import (
    SearchError,
    SearchRequest,
    SearchResult,
    TavilySearchClient,
    normalize_tavily_response,
)


def test_empty_results() -> None:
    assert normalize_tavily_response({}) == []
    assert normalize_tavily_response({"results": []}) == []
    assert normalize_tavily_response({"results": "not a list"}) == []


def test_skips_items_missing_title() -> None:
    payload = {
        "results": [
            {"title": "", "url": "https://example.com"},
            {"title": "Good", "url": "https://example.org"},
        ]
    }
    results = normalize_tavily_response(payload)
    assert len(results) == 1
    assert results[0].title == "Good"


def test_skips_items_missing_url() -> None:
    payload = {
        "results": [
            {"title": "No URL", "url": ""},
            {"title": "Valid", "url": "https://example.org"},
        ]
    }
    results = normalize_tavily_response(payload)
    assert len(results) == 1
    assert results[0].title == "Valid"


def test_missing_snippet_falls_back_to_empty_string() -> None:
    payload = {
        "results": [
            {"title": "T", "url": "https://a.com"},
        ]
    }
    results = normalize_tavily_response(payload)
    assert results[0].snippet == ""


def test_null_snippet_falls_back_to_empty_string() -> None:
    payload = {
        "results": [
            {"title": "T", "url": "https://a.com", "snippet": None},
        ]
    }
    results = normalize_tavily_response(payload)
    assert results[0].snippet == ""


def test_preserves_raw_content() -> None:
    payload = {
        "results": [
            {
                "title": "Full article",
                "url": "https://example.com/article",
                "snippet": "excerpt",
                "raw_content": "the entire page text here.",
            },
        ]
    }
    results = normalize_tavily_response(payload)
    assert results[0].raw_content == "the entire page text here."


def test_null_raw_content_stays_null() -> None:
    payload = {
        "results": [
            {
                "title": "No raw",
                "url": "https://example.com",
                "raw_content": None,
            },
        ]
    }
    results = normalize_tavily_response(payload)
    assert results[0].raw_content is None


def test_full_payload() -> None:
    payload = {
        "results": [
            {
                "title": "Karpathy on search",
                "url": "https://karpathy.blog/2025/search",
                "snippet": "A description of autoregressive search.",
                "raw_content": "long text...",
            },
            {
                "title": "Second result",
                "url": "https://example.com/2",
            },
        ],
        "response_time": 1.2,
    }
    results = normalize_tavily_response(payload)
    assert len(results) == 2
    assert results[0].title == "Karpathy on search"
    assert results[0].url == "https://karpathy.blog/2025/search"
    assert results[1].snippet == ""
    assert results[1].raw_content is None


def test_tavily_client_rejects_missing_key() -> None:
    client = TavilySearchClient(api_key="")

    with pytest.raises(SearchError, match="api key"):
        client._search_sync(SearchRequest(query="x"))


def test_tavily_client_normalizes_provider_response(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self) -> bytes:
            return (
                b'{"results":[{"title":"Karpathy autoresearch",'
                b'"url":"https://example.com","content":"snippet"}]}'
            )

    captured: dict[str, object] = {}

    def fake_urlopen(req, timeout):
        captured["request"] = req
        captured["timeout"] = timeout
        return FakeResponse()

    monkeypatch.setattr("flightrecorder.web_search.request.urlopen", fake_urlopen)
    client = TavilySearchClient(api_key="tvly-test", timeout_seconds=3)

    results = client._search_sync(SearchRequest(query="karpathy", max_results=2))

    assert captured["timeout"] == 3
    assert results == [
        SearchResult(
            title="Karpathy autoresearch",
            url="https://example.com",
            snippet="snippet",
        )
    ]


def test_tavily_client_raises_on_http_error(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_urlopen(req, timeout):
        raise error.HTTPError(req.full_url, 429, "rate limited", hdrs=None, fp=None)

    monkeypatch.setattr("flightrecorder.web_search.request.urlopen", fake_urlopen)
    client = TavilySearchClient(api_key="tvly-test")

    with pytest.raises(SearchError, match="HTTP 429"):
        client._search_sync(SearchRequest(query="karpathy"))
