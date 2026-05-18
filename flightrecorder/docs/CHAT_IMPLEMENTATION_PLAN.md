# Chat implementation plan

Converted from `docs/CHAT_API_CONTRACT_DRAFT.md`. This document is a
checklist, not implementation. **requires Daniel approval** before code work
starts.

## Files likely touched

- `src/backend/flightrecorder/api.py` - new: `POST /api/sessions/{id}/messages`
  SSE endpoint
- `src/backend/flightrecorder/costs.py` - wire `ProviderCallGuard` around the
  provider SDK call
- `src/backend/flightrecorder/providers.py` - call the brainstorm provider for
  actual streaming tokens
- `src/backend/flightrecorder/storage.py` - append messages to session file,
  update `message_count`

## Tests needed

- Unit: SSE token parsing, session message append, token count update
- Integration: streaming endpoint through TestClient, error events on provider
  failure
- Cost: verify `api_calls` row inserted, budget guard blocks when hard-stop
  active

## Unresolved approval blockers

1. SSE event format (`token`/`done`/`error`) not yet approved by Daniel.
2. Image inclusion strategy: separate upload endpoint vs inline refs.
3. Continue/resume behavior not specified.
4. Whether the chat endpoint uses the brainstorm role's configured provider or
   a hardcoded default.

## Pre-requisites

- Provider SDK calls must be wired (not done).
- `ProviderCallGuard.check_before_call()` and `record_usage()` exist but are
  not yet called from any request path.
- Chat endpoint contract draft (`docs/CHAT_API_CONTRACT_DRAFT.md`) must be
  approved before code.
