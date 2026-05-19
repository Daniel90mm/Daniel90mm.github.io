"""Unit tests for flightrecorder.web_search normalization."""

from __future__ import annotations

from urllib import error

import pytest

from flightrecorder.web_search import (
    RAW_CONTENT_EXCERPT_CHARS,
    SearchError,
    SearchRequest,
    SearchResult,
    TavilySearchClient,
    normalize_tavily_response,
    search_result_to_spaghetti_body,
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


class TestSearchResultToSpaghettiBody:
    def test_full_result_includes_all_fields(self) -> None:
        result = SearchResult(
            title="Karpathy on Search",
            url="https://karpathy.blog/2025/search",
            snippet="Autoregressive search is the future.",
            raw_content="Many paragraphs of raw page content.",
        )
        body = search_result_to_spaghetti_body(result)
        assert "Karpathy on Search" in body
        assert "https://karpathy.blog/2025/search" in body
        assert "Autoregressive search is the future." in body
        assert "Many paragraphs of raw page content." in body
        assert body.startswith("## Karpathy on Search")
        assert "```text" in body
        assert body.endswith("\n")

    def test_missing_snippet_omits_blockquote(self) -> None:
        result = SearchResult(
            title="No Snippet",
            url="https://example.com",
        )
        body = search_result_to_spaghetti_body(result)
        assert "No Snippet" in body
        assert "https://example.com" in body
        assert "> " not in body

    def test_missing_raw_content_omits_excerpt_section(self) -> None:
        result = SearchResult(
            title="No Raw",
            url="https://example.com",
            snippet="Just a snippet.",
        )
        body = search_result_to_spaghetti_body(result)
        assert "Raw content excerpt:" not in body

    def test_raw_content_truncation_at_default_cap(self) -> None:
        long_raw = "x" * (RAW_CONTENT_EXCERPT_CHARS + 500)
        result = SearchResult(
            title="Long Raw",
            url="https://example.com",
            raw_content=long_raw,
        )
        body = search_result_to_spaghetti_body(result)
        assert "Raw content excerpt:" in body
        assert ("x" * RAW_CONTENT_EXCERPT_CHARS) + "..." in body
        assert ("x" * (RAW_CONTENT_EXCERPT_CHARS + 1)) not in body

    def test_raw_content_at_exact_cap_not_truncated(self) -> None:
        exact_raw = "y" * RAW_CONTENT_EXCERPT_CHARS
        result = SearchResult(
            title="Exact Cap",
            url="https://example.com",
            raw_content=exact_raw,
        )
        body = search_result_to_spaghetti_body(result)
        assert "..." not in body.rsplit("Raw content excerpt:", 1)[-1]

    def test_custom_cap_passed_through(self) -> None:
        long_raw = "z" * 500
        result = SearchResult(
            title="Custom Cap",
            url="https://example.com",
            raw_content=long_raw,
        )
        body = search_result_to_spaghetti_body(result, raw_content_max_chars=200)
        assert "z" * 200 + "..." in body
        assert "z" * 500 not in body

    def test_collapses_title_and_url_to_single_lines(self) -> None:
        result = SearchResult(
            title="Useful title\n## Injected heading",
            url="https://example.com\n[bad](javascript:alert(1))",
            snippet="snippet",
        )
        body = search_result_to_spaghetti_body(result)
        assert body.splitlines()[0] == "## Useful title ## Injected heading"
        assert body.splitlines()[2] == "URL: https://example.com [bad](javascript:alert(1))"
        assert "\n## Injected heading" not in body

    def test_multiline_snippet_stays_inside_blockquote(self) -> None:
        result = SearchResult(
            title="Snippet",
            url="https://example.com",
            snippet="first line\n## injected\n\nlast line",
        )
        body = search_result_to_spaghetti_body(result)
        assert "> first line" in body
        assert "> ## injected" in body
        assert ">\n" in body
        assert "> last line" in body
        assert "\n## injected" not in body

    def test_raw_content_fence_is_escaped(self) -> None:
        result = SearchResult(
            title="Raw",
            url="https://example.com",
            raw_content="before\n```python\nprint('bad')\n```\nafter",
        )
        body = search_result_to_spaghetti_body(result)
        assert body.count("```text") == 1
        assert "```python" not in body
        assert "` ` `python" in body
