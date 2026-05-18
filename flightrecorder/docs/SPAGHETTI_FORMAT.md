# Spaghetti file format

Produced by `render_spaghetti_idea()` in `src/backend/flightrecorder/idea_capture.py`.
Each spaghetti idea is one markdown file under `$FLIGHTRECORDER_HOME/spaghetti/`.

## Frontmatter

```yaml
idea_id: "pca-future-abcd1234"
captured_at: "2026-05-18T19:00:00+02:00"
source_session: "2026-05-18-1730-smoke-abcd1234"
tags: ["pca", "signal-processing"]
topics: ["statistics"]
status: unmatched
match_attempts: 0
matched_to: []
implemented_in: []
```

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `idea_id` | string | Stable deterministic hash from source session + index + content |
| `captured_at` | iso8601 | When this idea was extracted |
| `source_session` | string | Session ID the idea came from |
| `tags` | `[string]` | Freeform tags from the idea-capture prompt |
| `topics` | `[string]` | Broader themes (optional, only if non-empty) |
| `status` | enum | `unmatched`, `matched`, or `orphan` |
| `match_attempts` | int | How many matchmaker passes have processed this idea |
| `matched_to` | `[{project, todo_ref, matched_at, rationale}]` | Projects this idea was matched to |
| `implemented_in` | `[{project, link, implemented_at}]` | Projects where the matched TODO was marked done |

## Body

The idea text, 1--3 sentences, in Daniel's voice, verbatim from the idea-capture
LLM output.

## File name

`{idea_id}.md` under `spaghetti/`. The idea_id is built by `make_idea_id()`:
```
{first-40-chars-of-content-slug}-{sha256[:8]}
```

## Index

Each spaghetti idea is also indexed in `metadata.db.ideas` with the same
frontmatter fields stored as JSON columns.
