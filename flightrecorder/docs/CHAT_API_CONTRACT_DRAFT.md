# Chat API Contract Draft

> **DRAFT -- requires Daniel approval before implementation.**

The spec (section 11) names the chat endpoint
(`POST /api/sessions/{id}/messages`) but does not define the streaming
contract, SSE event format, or error shapes. This document proposes them.

---

## `POST /api/sessions/{session_id}/messages`

Send a user message to the brainstorm LLM and receive the assistant response
as a Server-Sent Events (SSE) stream.

### Request

```json
{
    "content": "I think PCA would be useful for denoising multichannel fNIRS data"
}
```

- `content` is required, non-empty, max 32768 characters.
- Optional fields deferred to v2: `images` (base64 or asset refs), `voice_ref`,
  `continue` (resume an interrupted stream).

### Response (200, SSE)

Content-Type: `text/event-stream`.

```
event: token
data: {"token": "The "}

event: token
data: {"token": "idea "}

event: token
data: {"token": "is "}

event: token
data: {"token": "interesting..."}

event: done
data: {"input_tokens": 1200, "output_tokens": 42, "message_count": 5}
```

Each `token` event carries a single streaming token. The final event is `done`
with token counts and the updated message count for the session.

The client accumulates tokens into the assistant message. No `[DONE]` sentinel;
the `done` event closes the stream from the server side.

### Error events (SSE)

If the provider call fails before any tokens are emitted:

```
event: error
data: {"detail": "Provider API returned 429: rate limited"}
```

The server closes the stream after the error event. The session's last user
message is preserved; the failed assistant message is not appended.

### Response (non-streaming errors, standard JSON)

- 400: `{"detail": "content is required"}` -- empty or missing body
- 404: `{"detail": "Session not found"}` -- unknown session_id
- 503: `{"detail": "Budget hard-stop active"}` -- publisher/budget kill switch
- 422: FastAPI validation error for malformed body

### After the stream

On clean `done`, the backend:
1. Appends the user message to the session file.
2. Appends the full assistant response to the session file.
3. Updates `message_count` in sqlite.
4. Logs both call costs (user message context + assistant output tokens) to
   `api_calls`.

Provider exceptions mid-stream: the backend appends the user message but not a
truncated assistant response; logs what tokens were consumed and the error.

---

## Open questions

- Should `images` and `voice_ref` be separate endpoints
  (`POST /api/sessions/{id}/upload`, then referenced by ID in the message body),
  or inlined in the message payload?
- Should `continue` (resume) be a separate action or a flag on the message
  request?
- Should the SSE stream include a `session_update` event after `done` with the
  new `message_count` and `image_count`, or rely on the client to re-fetch?
