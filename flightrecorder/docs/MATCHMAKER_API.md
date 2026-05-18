# Matchmaker API

## Endpoint

`POST /api/matchmaker/run`

Runs the matchmaker over a set of spaghetti ideas against the current project
registry. The default scorer is `NullScorer` which rejects every pair (the
correct default until an LLM scorer is wired).

## Request body

```json
{
    "idea_ids": ["idea-1", "idea-2"]
}
```

- `idea_ids` (required, array of strings, min length 1). Each id must exist
  in the sqlite `ideas` table. If any id is unknown the entire request is
  rejected with 404.

## Response 200

```json
{
    "batch_id": "matches-2026-05-18T120000Z",
    "generated_at": "2026-05-18T12:00:00+00:00",
    "candidates": [],
    "rejected_idea_ids": ["idea-1", "idea-2"]
}
```

- `batch_id` (string): sortable batch identifier, format
  `matches-YYYY-MM-DDTHHMMSSZ`.
- `generated_at` (ISO-8601 string): timestamp the batch was produced.
- `candidates` (array of objects): proposed matches. Each candidate has
  `idea_id` (string), `project_ref` (string), `confidence` (float in
  [0.0, 1.0]), and `rationale` (string). With the default `NullScorer`
  this list is always empty.
- `rejected_idea_ids` (array of strings): every idea id from the request
  that was considered but did not produce a match. With `NullScorer` this
  is identical to the input `idea_ids`.

## Status codes

| Code | Meaning |
|------|---------|
| 200 | Happy path. Candidates may be empty (rejection-bias default). |
| 404 | One or more `idea_id` values are not present in the `ideas` table. |
| 422 | Request body is malformed, empty `idea_ids`, or missing fields. |

## Rejection bias

The matchmaker is designed to **reject by default**. `NullScorer` makes this
explicit: every (idea, project) pair returns no match. The LLM scorer will
land in a separate step without changing this contract. When the scorer is
wired, matches will appear in `candidates` but the response shape stays the
same.

## Inputs and side effects

The endpoint reads from:

- `metadata.db.ideas` for spaghetti idea metadata and file paths.
- `<runtime_home>/spaghetti/<idea_id>.md` for the idea body text.
- `<runtime_home>/projects.json` for active project summaries. If
  `projects.json` is missing the project list is treated as empty
  (fail-closed: all ideas rejected, no matches).

The endpoint does **not** write any files or modify any database rows. It is
read-only.

## Example

```sh
curl -s http://127.0.0.1:8000/api/matchmaker/run \
  -H "Content-Type: application/json" \
  -d '{"idea_ids": ["pca-future-abcd1234"]}'
```

```json
{
    "batch_id": "matches-2026-05-18T120000Z",
    "generated_at": "2026-05-18T12:00:00+00:00",
    "candidates": [],
    "rejected_idea_ids": ["pca-future-abcd1234"]
}
```
