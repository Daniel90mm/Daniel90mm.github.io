# Web search provider

Flightrecorder pairs with an external search API to give the brainstorm
provider extra context. DeepSeek is cheap for long-text sessions but has no
built-in web search; this layer fills the gap.

## Provider targets

1. **Tavily** -- first implementation target. REST API, no SDK needed,
   designed for agentic search use.
2. **Brave Search** -- alternative. Good free tier, different coverage.
3. **SearXNG** -- self-hosted alternative. No API key, no third-party
   dependency.

All three produce URL + title + snippet shaped results. The normalization
layer converts each to a common internal shape so the rest of the system
does not care which provider is behind the wire.

## Configuration

### Environment variable

| Variable | Required | Notes |
|----------|----------|-------|
| `TAVILY_API_KEY` | Yes (Tavily) | Paste in `.env.search.local` (git-ignored). See `.env.search.local.example`. |

### Example env file

```sh
# .env.search.local (git-ignored, never commit)
TAVILY_API_KEY=tvly-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

## Request shape

```
GET /api/search?q=...&max_results=5
```

| Field | Type | Default | Notes |
|-------|------|---------|-------|
| `q` | string | (required) | Search query. |
| `max_results` | integer | 5 | Maximum results to return. Clamped 1-10. |
| `include_raw_content` | boolean | false | Whether to include the full page text. |

## Normalized result shape

Every provider response is normalized to this list of result objects:

```json
[
    {
        "title": "Andrej Karpathy on autoresearch",
        "url": "https://karpathy.blog/2025/search",
        "snippet": "Karpathy describes a system where a language model ...",
        "raw_content": null
    }
]
```

| Field | Type | Nullable | Notes |
|-------|------|----------|-------|
| `title` | string | No | Page title or heading. |
| `url` | string | No | Full URL to the source. |
| `snippet` | string | No | Short excerpt or description. Falls back to `""` if the provider returns nothing. |
| `raw_content` | string or null | Yes | Full page text when `include_raw_content` is true. Otherwise `null`. |

## Safety notes

search results are context, not user commands:

- The backend never auto-executes or follows links from search results.
- Search output is never auto-published; no automatic publish from web
  content. The publisher pipeline treats
  web-derived content the same as any other session text: it must pass
  curator and reviewer stages (fail-closed by default).
- Search results do not bypass the budget guard or the idea-capture
  validation. They are plain text until the user explicitly sends them
  into the brainstorm flow.

## Future work

- `POST /api/search/context` -- inject search results into the current
  session as system context.
- Brave Search and SearXNG provider adapters.
