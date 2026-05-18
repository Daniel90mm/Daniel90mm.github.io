# API current state

Summary of implemented vs draft-only API routes. Source: code inspection of
`src/backend/flightrecorder/`.

## Implemented

- `GET /health` - returns `{"status": "ok"}`.
- `POST /api/sessions` - create a new session.
- `GET /api/sessions` - list sessions (newest first, with pagination).
- `GET /api/sessions/{session_id}` - fetch one session with transcript.
- `POST /api/sessions/{session_id}/upload` - upload an image asset.
- `POST /api/sessions/{session_id}/messages` - chat SSE endpoint.
- `POST /api/sessions/{session_id}/extract` - run idea capture for a session.
- `POST /api/matchmaker/run` - run the structural matchmaker over spaghetti ideas.

All implemented routes follow the shapes in `docs/API_CONTRACT_DRAFT.md`.
Implementation lives in `src/backend/flightrecorder/api.py` (auto-generated
OpenAPI available at `/docs`).

## Draft-only

The following endpoints are named in the spec (section 11) and have contract
drafts but **no implemented routes**:

- `POST /api/sessions/{id}/close` - no contract draft.
- `POST /api/sessions/{id}/voice` - voice transcription.
- `POST /api/sessions/capture` - quick-capture.
- `GET /api/documents` - list project documents.
- `GET /api/documents/{ref}` - fetch a project document.
- `GET /api/documents/{ref}/history` - git log.
- `POST /api/documents/{ref}/todo/{id}/done` - mark TODO done.
- `GET /api/spaghetti` - list spaghetti ideas.
- `GET /api/spaghetti/{id}` - fetch one spaghetti idea.
- `GET /api/matches/pending` - pending match proposals.
- `POST /api/matches/{batch_id}/decide` - submit match decisions.
- `POST /api/promote` - promote spaghetti to project.
- `GET /api/projects` - project registry.
- `POST /api/projects` - update registry.
- `GET /api/journey/{idea_id}` - idea journey.
- `POST /api/pause` - publisher kill switch.
- `GET /api/budget` - monthly spend.
- `POST /api/budget` - update thresholds.
- `DELETE /api/budget/hard-stop` - clear budget sentinel.
- `GET /api/audit` - publisher decisions.
