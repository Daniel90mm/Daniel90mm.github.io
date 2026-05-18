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

Backend skeleton, session storage, approved `/api/sessions*` routes, and cost
tracking are built.

Append-only project document helpers and idea-capture operation parsing with
spaghetti/project routing exist, but the idea-capture LLM call itself is not
yet wired.

Budget tracking has a hard-stop sentinel helper and provider-call guard
primitives (`check_before_call`, `record_usage`), but provider and chat paths
do not enforce them yet -- real SDK calls are not yet wired.

## Current API

- `POST /api/sessions`
- `GET /api/sessions`
- `GET /api/sessions/{session_id}`
- `POST /api/sessions/{session_id}/upload`

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
