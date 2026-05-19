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
