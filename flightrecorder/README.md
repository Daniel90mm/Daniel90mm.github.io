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
- `GET /api/budget`
- `GET /api/projects`
- `GET /api/documents`
- `GET /api/documents/{ref}`
- `GET /api/spaghetti`
- `GET /api/spaghetti/{idea_id}`
- `POST /api/matchmaker/run`

## Dogfood frontend

The static frontend in `src/frontend/` lets you exercise the API loop
without build tools.

```sh
scripts/dev-backend.sh
```

Open `http://127.0.0.1:8000/`. The minimal dogfood workflow:

1. Create a session with provider, model, and optional slug.
2. Click a session in the list to select it.
3. Type a message and send -- the assistant response streams over SSE.
4. Click "Extract Ideas" to run idea capture on the transcript.
5. Watch budget status, then inspect the transcript, extraction result, project documents, and
   spaghetti ideas in the browser.

Tests use stubs. Real providers require `config.toml` with API keys
configured in the `[providers]` and `[roles]` sections.

For an offline end-to-end prototype with no API keys:

```sh
FLIGHTRECORDER_CONFIG=$PWD/config.prototype.toml scripts/dev-backend.sh
```

Then open `http://127.0.0.1:8000/`, create a session, chat, extract, and
inspect the generated document/spaghetti panels.

Copy `config.example.toml` and `pricing.example.toml` as starting points,
set `FLIGHTRECORDER_CONFIG` to your config path, and replace the placeholder
API key with a real one.

## Layout

- `prompts/` - versioned LLM prompts.
- `src/backend/` - FastAPI backend, provider wrappers, storage, pipelines.
- `src/frontend/` - static dogfood frontend.
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
