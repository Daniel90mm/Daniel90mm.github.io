"""Web search normalization helpers.

Pure functions with no network dependencies. Convert provider-specific
response shapes to a common internal `SearchResult` format.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
import json
from urllib import error, request
from typing import Protocol


@dataclass(frozen=True)
class SearchRequest:
    """Normalized search request."""

    query: str
    max_results: int = 5
    include_raw_content: bool = False


@dataclass(frozen=True)
class SearchResult:
    """Normalized search result from any provider."""

    title: str
    url: str
    snippet: str = ""
    raw_content: str | None = None


RAW_CONTENT_EXCERPT_CHARS = 2_000


def search_result_to_spaghetti_body(
    result: SearchResult,
    raw_content_max_chars: int = RAW_CONTENT_EXCERPT_CHARS,
) -> str:
    """Convert a SearchResult into a safe spaghetti-note body string.

    Includes title, URL attribution, snippet, and a capped raw-content
    excerpt when present. Does not write files or call sqlite.
    """

    title = _single_markdown_line(result.title, fallback="Untitled search result")
    url = _single_markdown_line(result.url, fallback="unknown")
    lines = [
        f"## {title}",
        "",
        f"URL: {url}",
    ]
    if result.snippet:
        lines.append("")
        lines.extend(_blockquote_lines(result.snippet))
    if result.raw_content:
        raw = result.raw_content.replace("\r\n", "\n").replace("\r", "\n")
        raw = raw.replace("```", "` ` `")
        raw_content_max_chars = max(0, raw_content_max_chars)
        if len(raw) > raw_content_max_chars:
            raw = raw[:raw_content_max_chars] + "..."
        lines.append("")
        lines.append("Raw content excerpt:")
        lines.append("")
        lines.append("```text")
        lines.append(raw)
        lines.append("```")
    return "\n".join(lines) + "\n"


def _single_markdown_line(value: str, fallback: str) -> str:
    """Collapse untrusted text to one markdown line."""

    normalized = " ".join(value.strip().split())
    return normalized or fallback


def _blockquote_lines(value: str) -> list[str]:
    """Render untrusted snippet text as markdown blockquote lines."""

    lines = value.strip().splitlines()
    if not lines:
        return []
    return ["> " + line.strip() if line.strip() else ">" for line in lines]


class SearchClient(Protocol):
    """Protocol for any web search backend."""

    async def search(self, request: SearchRequest) -> list[SearchResult]:
        ...


class SearchError(RuntimeError):
    """Raised when a search provider call fails."""


@dataclass(frozen=True)
class TavilySearchClient:
    """Minimal Tavily REST client using the stdlib."""

    api_key: str
    timeout_seconds: float = 12.0

    async def search(self, request_body: SearchRequest) -> list[SearchResult]:
        return await asyncio.to_thread(self._search_sync, request_body)

    def _search_sync(self, request_body: SearchRequest) -> list[SearchResult]:
        if not self.api_key.strip() or "CHANGEME" in self.api_key:
            raise SearchError("tavily api key is not configured")

        payload = {
            "api_key": self.api_key,
            "query": request_body.query,
            "max_results": request_body.max_results,
            "include_raw_content": request_body.include_raw_content,
        }
        body = json.dumps(payload).encode("utf-8")
        http_request = request.Request(
            "https://api.tavily.com/search",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with request.urlopen(http_request, timeout=self.timeout_seconds) as response:
                response_body = response.read()
        except error.HTTPError as exc:
            raise SearchError(f"tavily search failed: HTTP {exc.code}") from exc
        except error.URLError as exc:
            raise SearchError(f"tavily search failed: {exc.reason}") from exc
        except TimeoutError as exc:
            raise SearchError("tavily search timed out") from exc

        try:
            data = json.loads(response_body.decode("utf-8"))
        except json.JSONDecodeError as exc:
            raise SearchError("tavily search returned invalid JSON") from exc
        if not isinstance(data, dict):
            raise SearchError("tavily search returned non-object JSON")
        return normalize_tavily_response(data)


def normalize_tavily_response(payload: dict) -> list[SearchResult]:
    """Convert a Tavily API response dict to normalized SearchResult objects.

    Expects `payload["results"]` to be a list of dicts with at least
    `title` and `url`. Falls back to empty strings for missing `snippet`
    and preserves `raw_content` when present.
    """

    results_raw = payload.get("results")
    if not isinstance(results_raw, list):
        return []

    normalized: list[SearchResult] = []
    for item in results_raw:
        if not isinstance(item, dict):
            continue
        title = str(item.get("title", ""))
        url = str(item.get("url", ""))
        if not title or not url:
            continue
        snippet_value = item.get("snippet", item.get("content", ""))
        snippet = str(snippet_value) if snippet_value is not None else ""
        raw_content = (
            str(item["raw_content"])
            if item.get("raw_content") is not None
            else None
        )
        normalized.append(
            SearchResult(
                title=title,
                url=url,
                snippet=snippet,
                raw_content=raw_content,
            )
        )
    return normalized
