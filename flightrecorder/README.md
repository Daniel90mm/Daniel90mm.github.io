# flightrecorder

Self-hosted brainstorming app with append-only idea capture, matchmaker passes,
and delayed public publishing into the Hugo site in this repo.

The canonical design is [flightrecorder-spec.md](flightrecorder-spec.md).

## Quickstart

```sh
cd flightrecorder
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest tests/ -v
scripts/dev-backend.sh
```

## Status

Backend skeleton, session storage, approved `/api/sessions*` routes, chat SSE,
idea extraction, and cost tracking are built.

Append-only project document helpers and idea-capture operation parsing with
spaghetti/project routing exist. The idea-capture LLM call is wired through the
configured `idea_capture` role.

Budget tracking has a hard-stop sentinel helper and provider-call guard
primitives (`check_before_call`, `record_usage`). Chat and extraction enforce
the guard before provider calls and record usage after successful calls.

## Current API

- `POST /api/sessions`
- `GET /api/sessions`
- `GET /api/sessions/{session_id}`
- `POST /api/sessions/{session_id}/upload`
- `POST /api/sessions/{session_id}/messages`
- `POST /api/sessions/{session_id}/extract`
- `POST /api/matchmaker/run`

## Layout

- `prompts/` - versioned LLM prompts.
- `src/backend/` - FastAPI backend, provider wrappers, storage, pipelines.
- `src/frontend/` - Svelte SPA.
- `src/cli/` - `fr` command.
- `src/data/` - static data such as the pokemon list.
- `tests/` - unit, integration, and adversarial tests.
- `scripts/` - setup and sync scripts.
- `docs/` - design notes.
- `handoffs/` - interrupted-session handoffs.
- `consults/` - decision consults.

## Runtime Data

Runtime data is not stored in this repo. On pa-server it lives under
`~/flightrecorder/`, with project documents in `~/flightrecorder/documents/`
as their own git repo.
