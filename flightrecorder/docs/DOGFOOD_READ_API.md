# Dogfood read API

Read-only routes needed by the dogfood frontend to inspect extraction results.
These routes must not mutate documents, spaghetti files, git state, or sqlite
rows.

## `GET /api/projects`

List active project registry entries.

### Response 200

```json
{
    "projects": [
        {
            "name": "fnirs amp",
            "ref": "fnirs",
            "path": "documents/fnirs.md",
            "active": true,
            "description": "fNIRS amplifier hardware"
        }
    ]
}
```

- Reads `<runtime_home>/projects.json`. If the file is absent, returns
  `{"projects": []}`.
- `ref` is the sanitized project reference used in filenames and URLs.
- `path` is relative to `<runtime_home>/`.

### Status codes

| Code | Meaning |
|------|---------|
| 200 | Success (empty list if `projects.json` missing). |

---

## `GET /api/documents`

List project document refs and paths.

### Response 200

```json
{
    "documents": [
        {
            "ref": "fnirs",
            "path": "documents/fnirs.md",
            "size_bytes": 2048,
            "modified_at": "2026-05-19T12:00:00+02:00"
        }
    ]
}
```

- Lists markdown files in `<runtime_home>/documents/`, sorted by filename.
- If `<runtime_home>/documents/` does not exist, returns `{"documents": []}`.
- `ref` is the filename stem without extension.
- `modified_at` is the filesystem modification time in ISO-8601.

### Status codes

| Code | Meaning |
|------|---------|
| 200 | Success (empty list if directory missing). |

---

## `GET /api/documents/{ref}`

Return one project document as plain markdown text plus metadata.

### Path parameter

| Name | Type | Notes |
|------|------|-------|
| `ref` | string | Project reference (filename stem). Sanitized the same way as `sanitize_project_ref`. |

### Response 200

```json
{
    "ref": "fnirs",
    "path": "documents/fnirs.md",
    "body": "## Problem\n\n...\n\n## TODOs\n- [ ] build amp\n",
    "size_bytes": 2048,
    "modified_at": "2026-05-19T12:00:00+02:00"
}
```

- `body` is the raw markdown content as a string.
- Returns 404 if the sanitized ref does not match an existing `.md` file in
  the documents directory.

### Status codes

| Code | Meaning |
|------|---------|
| 200 | Document found and returned. |
| 404 | No document file exists for the given ref. |

---

## `GET /api/spaghetti`

List spaghetti ideas from the sqlite `ideas` table.

### Response 200

```json
{
    "ideas": [
        {
            "idea_id": "pca-denoising-abcd1234",
            "captured_at": "2026-05-19T12:00:00+02:00",
            "source_session": "2026-05-19-1000-session-abcd1234",
            "tags": ["pca", "signal-processing"],
            "topics": ["denoising", "multivariate"],
            "status": "unmatched",
            "path": "spaghetti/pca-denoising-abcd1234.md"
        }
    ]
}
```

- Returns rows from the `ideas` table ordered newest first by `captured_at`,
  falling back to `idea_id` if `captured_at` is null.
- `tags` and `topics` are decoded from the stored JSON columns.
- `path` is the indexed markdown file path relative to `<runtime_home>`.

### Status codes

| Code | Meaning |
|------|---------|
| 200 | Success (empty list if no ideas exist). |

---

## `GET /api/spaghetti/{idea_id}`

Return one spaghetti idea markdown body plus indexed metadata.

### Path parameter

| Name | Type | Notes |
|------|------|-------|
| `idea_id` | string | The `idea_id` from the `ideas` table. |

### Response 200

```json
{
    "idea_id": "pca-denoising-abcd1234",
    "captured_at": "2026-05-19T12:00:00+02:00",
    "source_session": "2026-05-19-1000-session-abcd1234",
    "tags": ["pca", "signal-processing"],
    "topics": ["denoising", "multivariate"],
    "status": "unmatched",
    "path": "spaghetti/pca-denoising-abcd1234.md",
    "body": "PCA for multivariate signal denoising.\n"
}
```

- `body` is the markdown content with frontmatter stripped (same stripping
  logic used by the matchmaker's `_read_spaghetti_body`).
- Returns 404 if the `idea_id` is not found in the `ideas` table, or if the
  indexed markdown file is missing.

### Status codes

| Code | Meaning |
|------|---------|
| 200 | Idea found, body returned. |
| 404 | Unknown `idea_id` or missing markdown file. |

---

## Read-only guarantees

All five routes are strictly read-only. They must not:

- Create files or directories.
- Initialize or commit a git repository.
- Insert, update, or delete sqlite rows.
- Write to `projects.json`, document files, or spaghetti files.
- Record `api_calls` rows.
- Hold locks longer than the request duration.
