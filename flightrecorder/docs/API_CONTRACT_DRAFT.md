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

Upload an image asset to a session. Cap: 5 MiB.

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
    "detail": "image upload exceeds 5 MiB cap"
}
```

**Notes:**
- Filenames are sanitized to ASCII before storage.
- Increments the session's `image_count`.
