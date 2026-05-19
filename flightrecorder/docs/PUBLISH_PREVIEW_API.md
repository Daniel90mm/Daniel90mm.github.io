# Publish preview API

## Endpoint

`GET /api/publish/preview`

Returns a preview/audit summary for one source artifact (session, project
document, or spaghetti idea). Runs the publisher pipeline with the current
fail-closed defaults (Null curator + Null reviewer), so `publishable` is always
`false` until real curator/reviewer stages are wired. The route is read-only
and must not write files, sqlite rows, git commits, or Hugo content.

## Query parameters

| Name | Type | Required | Notes |
|------|------|----------|-------|
| `source_kind` | string (enum: `session`, `document`, `spaghetti`) | yes | Discriminates the source type. |
| `source_id` | string | yes | Session id, document ref, or spaghetti idea id. |

## Response 200

```json
{
    "source_kind": "session",
    "source_id": "2026-05-19-1000-session-abcd1234",
    "publishable": false,
    "rejection_reason": "curator not configured",
    "approved_count": 0,
    "snippets": []
}
```

- `source_kind` (string): echo of the query parameter.
- `source_id` (string): echo of the query parameter.
- `publishable` (boolean): whether the curator stage accepted the source.
  Always `false` with the current Null curator.
- `rejection_reason` (string or null): curator or reviewer rejection reason,
  or null when publishable is true (the 200-response shape is shared; see
  non-publishable example below).
- `approved_count` (integer): number of snippets that passed curator +
  reviewer. Always 0 with the current fail-closed defaults.
- `snippets` (array of objects): the approved (redacted) snippet bodies and
  metadata. Empty when publishable is false. Each snippet has:
  `snippet_id`, `source_kind`, `source_id`, `drafted_at`, `publish_after`,
  `tags`, `project_ref`, `body`.

When the real curator is wired and a source is fully approved:

```json
{
    "source_kind": "document",
    "source_id": "fnirs",
    "publishable": true,
    "rejection_reason": null,
    "approved_count": 2,
    "snippets": [
        {
            "snippet_id": "fnirs-00",
            "source_kind": "document",
            "source_id": "fnirs",
            "drafted_at": "2026-05-20T10:00:00+00:00",
            "publish_after": "2026-05-21T10:00:00+00:00",
            "tags": ["hardware", "signal-processing"],
            "project_ref": "fnirs",
            "body": "fNIRS amplifier prototype update: low-noise front-end ..."
        }
    ]
}
```

## Source body resolution

| source_kind | Body resolved from |
|-------------|-------------------|
| `session` | Session transcript rendered from stored messages via `transcript_from_messages`. |
| `document` | Project document markdown from `<runtime_home>/documents/{ref}.md`. |
| `spaghetti` | Spaghetti idea markdown body from `<runtime_home>/spaghetti/{idea_id}.md` (frontmatter stripped). |

If the source cannot be resolved (session not found, document file missing,
spaghetti idea_id unknown), the endpoint returns 404.

If `source_kind` is not one of `session`, `document`, or `spaghetti`, the
endpoint returns 422.

## Status codes

| Code | Meaning |
|------|---------|
| 200 | Happy path. Publishable may be false (fail-closed default). |
| 404 | Unknown `source_id` for the given `source_kind`. |
| 422 | Unknown `source_kind` or missing query parameters. |

## Fail-closed guarantee

The current implementation uses `run_publish_pipeline` with default `NullCurator`
and `NullReviewer`. The curator rejects every source (`publishable=false`,
`rejection_reason="curator not configured"`). The reviewer rejects every
snippet. No content can pass until both stages are wired with LLM providers.
This is the same fail-closed contract as the matchmaker's `NullScorer`.

## Read-only guarantees

The endpoint must not:

- Create or modify files or directories.
- Insert, update, or delete sqlite rows.
- Create git repositories, commits, or tags.
- Write to the Hugo content directory.
- Record `api_calls` rows.
- Hold locks longer than the request duration.
