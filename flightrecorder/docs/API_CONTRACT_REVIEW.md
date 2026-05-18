# API contract review checklist

To be approved by Daniel before implementing `/api/sessions*` routes.

Extracted from `docs/API_CONTRACT_DRAFT.md`.

---

## 1. Response envelope

**Current draft:** List endpoints wrap results in `{"sessions": [...], "total": N}`.
Single-item endpoints return the object directly.

- [ ] Is a `total` field wanted, or should we return a flat array?
- [ ] Should error responses follow the FastAPI default `{"detail": "..."}` or use a
  custom envelope?

---

## 2. Upload style

**Current draft:** `POST /api/sessions/{id}/upload` uses `multipart/form-data`
with a single `file` field. The response returns `asset_path` and `image_count`.

- [ ] Is `multipart/form-data` acceptable, or should we accept base64-encoded
  payloads instead (simpler PWA integration)?
- [ ] Should the upload return a full asset object (`filename`, `relative_path`,
  `size_bytes`) from the serializers instead of just `asset_path`?

---

## 3. Pagination defaults

**Current draft:** `GET /api/sessions` takes optional `limit` (default 50, max 200)
and `offset` (default 0).

- [ ] Are these defaults reasonable, or should the default be lower (10--20) and
  more data fetched via a cursor/offset pattern?
- [ ] Should the list response include a `next` link or cursor, or is plain
  `total` + `offset` enough for v1?

---

## 4. Error shape

**Current draft:** Only a 404 example is given. Other errors (400, 413, 422) are
implied but not specified.

- [ ] Should we adopt FastAPI's native `{"detail": [{"loc": [...], "msg": "..."}]}`
  validation error format, or normalize all errors to a single shape?
- [ ] What is the error response for a `POST /api/sessions` with an unknown
  `provider`? A plain 422, or a custom 400 with a structured message?
