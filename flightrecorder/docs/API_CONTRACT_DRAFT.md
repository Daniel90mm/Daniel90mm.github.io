# API Contract Draft

> **Approved by Daniel on 2026-05-18.**
>
> The spec (section 11) names API paths but not exact payload shapes. This
> document defines shapes for the first four session endpoints.

---

## `POST /api/sessions`

Create a new session.

**Request:**

```json
{
    "provider": "google",
    "model": "gemini-2.5-pro",
    "slug": "optional-kebab-title"
}
```

**Response (201):**

```json
{
    "session_id": "2026-05-18-1730-optional-kebab-title-abcd1234",
    "started_at": "2026-05-18T17:30:00+02:00",
    "provider": "google",
    "model": "gemini-2.5-pro",
    "message_count": 0,
    "image_count": 0
}
```

**Notes:**
- `slug` is optional; defaults to `"session"` if omitted.
- `provider` and `model` must match configured provider and role names in
  `config.toml`.

---

## `GET /api/sessions`

List sessions, newest first.

**Query params (all optional):**

- `limit` (int, default 50, max 200)
- `offset` (int, default 0)
- `curated` (bool, filter by curation status)

**Response (200):**

```json
{
    "sessions": [
        {
            "session_id": "2026-05-18-1730-spaghetti-abcd1234",
            "started_at": "2026-05-18T17:30:00+02:00",
            "ended_at": null,
            "provider": "google",
            "model": "gemini-2.5-pro",
            "message_count": 0,
            "image_count": 0,
            "tags": [],
            "project_ref": null,
            "spaghetti": false,
            "extracted": false,
            "curated": false
        }
    ],
    "total": 1
}
```

**Notes:**
- Field names match `SessionMetadata` dataclass keys. They are snake_case in
  JSON to match the internal serializers.

---

## `GET /api/sessions/{session_id}`

Fetch a single session by ID, including the full transcript.

**Response (200):**

```json
{
    "session_id": "2026-05-18-1730-spaghetti-abcd1234",
    "started_at": "2026-05-18T17:30:00+02:00",
    "ended_at": null,
    "provider": "google",
    "model": "gemini-2.5-pro",
    "message_count": 2,
    "image_count": 0,
    "tags": [],
    "project_ref": null,
    "spaghetti": false,
    "extracted": false,
    "curated": false,
    "assets": [
        {
            "filename": "2026-05-18-1730-spaghetti-abcd1234-pcb_photo.jpg",
            "relative_path": "sessions/_assets/2026-05-18-1730-spaghetti-abcd1234-pcb_photo.jpg",
            "size_bytes": 12345
        }
    ],
    "messages": [
        {
            "role": "user",
            "timestamp": "17:30:01",
            "content": "first message text..."
        },
        {
            "role": "assistant",
            "timestamp": "17:30:14",
            "content": "response..."
        }
    ]
}
```

**Response (404):**

```json
{
    "detail": "Session not found"
}
```

---

## `POST /api/sessions/{session_id}/upload`

Upload a file asset to a session. Cap: 5 MiB. Current browser target accepts
images, PDFs, plain text, and Markdown. Uploaded assets are session metadata
for now; sending their contents into provider context is a separate route.

**Request:** `multipart/form-data` with field `file`.

**Response (201):**

```json
{
    "asset_path": "2026-05-18-1730-spaghetti-abcd1234-pcb_photo.jpg",
    "asset": {
        "filename": "2026-05-18-1730-spaghetti-abcd1234-pcb_photo.jpg",
        "relative_path": "sessions/_assets/2026-05-18-1730-spaghetti-abcd1234-pcb_photo.jpg",
        "size_bytes": 12345
    },
    "image_count": 1
}
```

**Response (413):**

```json
{
    "detail": "asset upload exceeds 5 MiB cap"
}
```

**Notes:**
- Filenames are sanitized to ASCII before storage.
- Increments the session's `image_count`.

---

## `DELETE /api/sessions/{session_id}/assets/{filename}`

Remove one uploaded session asset. The `filename` must be one of the filenames
returned in the session detail `assets` array.

**Response (200):**

```json
{
    "deleted": "2026-05-18-1730-spaghetti-abcd1234-pcb_photo.jpg",
    "image_count": 0,
    "assets": []
}
```

**Response (404):**

```json
{
    "detail": "Asset not found"
}
```

Path-guard rules:

- the file must live under `<runtime_home>/sessions/_assets`;
- the filename must start with `{session_id}-`;
- traversal such as `../` returns 404.

---

## `GET /api/sessions/{session_id}/assets/{filename}`

Return the bytes of one uploaded session asset. The asset must belong to the
given session and live under `<runtime_home>/sessions/_assets`.

Path-guard rules (same as DELETE):

- the file must live under `<runtime_home>/sessions/_assets`;
- the filename must start with `{session_id}-`;
- traversal such as `../` returns 404.

**Response (200):** raw file bytes with `Content-Type` derived from the file
extension (e.g. `image/png`, `text/plain`).

**Response (404):**

```json
{
    "detail": "Asset not found"
}
```

**Notes:**
- Does not return asset metadata; use `GET /api/sessions/{session_id}` for the
  metadata list.
- Does not serve the frontend asset path (`/assets/{asset_path:path}`); this is
  a separate route for session-specific file uploads.

---

## `GET /api/search`

Search for web content. Fail-closed: returns 503 when no search provider is
configured.

**Query params:**

| Name | Type | Default | Notes |
|------|------|---------|-------|
| `q` | string | (required) | Search query, min length 1. |
| `max_results` | integer | 5 | Clamped 1-10. |
| `include_raw_content` | boolean | false | Ask provider for full page text when available. |

**Response (200):**

```json
{
    "query": "karpathy autoregressive search",
    "include_raw_content": false,
    "results": [
        {
            "title": "Andrej Karpathy on search",
            "url": "https://karpathy.blog/2025/search",
            "snippet": "A description of autoregressive search.",
            "raw_content": null
        }
    ]
}
```

**Response (503):**

```json
{
    "detail": "search not configured"
}
```

**Response (422):**

```json
{
    "detail": [{"msg": "ensure this value has at least 1 characters", ...}]
}
```

**Notes:**
- Does not store results, call any LLM, or create spaghetti notes.
- Search results are read-only context; no automatic publish.
