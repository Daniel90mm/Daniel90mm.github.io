# Research log

Append-only record of decisions and open questions for flightrecorder.

## 2026-05-18 - Repo merge scaffold

The flightrecorder source tree now lives inside the merged
`daniel90mm.github.io` repo at `flightrecorder/`. The Hugo site remains under
`src/`. On pa-server, `~/hugo-site/` is the disposable merged checkout and
`~/flightrecorder/` remains the irreplaceable runtime data directory.

`~/flightrecorder/documents/` still has its own git history. That is separate
from the merged site/source repo and preserves append-only project document
history.

Open next: build order step 1, backend skeleton, after this scaffold pass.

## 2026-05-18 - Backend core start

Added a small-model task queue at `docs/SMALL_MODEL_TASKS.md` so narrow work
can be delegated with explicit where/what/why/smoke-test instructions.

Started build order step 1 without adding dependencies yet:
- config parsing uses `tomllib`, dataclasses, and path expansion
- sqlite schema setup creates `sessions`, `ideas`, `matches`, and `api_calls`
- provider abstraction exists as a protocol plus an unconfigured placeholder
- FastAPI app factory exists, but imports FastAPI lazily and reports the missing
  dependency clearly

Open next: decide and verify backend dependencies on Termux ARM64, then wire
the real FastAPI health endpoint into a runnable dev command.

## 2026-05-18 - Backend dependency boundary

Added approved backend dependencies to `pyproject.toml`:
- `fastapi` and plain `uvicorn` for the ASGI backend
- `anthropic`, `openai`, and `google-genai` for the provider SDKs
- `pytest` and `httpx` as dev/test dependencies

Local desktop verification passed in `.venv`: editable install succeeded,
provider SDK imports succeeded, unit tests passed, and Uvicorn served
`GET /health` with `{"status": "ok"}`.
A clean temp venv install with the plain-Uvicorn dependency set also passed
imports and unit tests.

Plain `uvicorn` is intentional. `uvicorn[standard]` pulls native extras that
are not needed for v1 and are avoidable Termux ARM64 risk.

Termux ARM64 verification is still open. Keep it as a separate explicit check
before treating build order step 1 as deployment-ready.

## 2026-05-18 - Session storage core

Started build order step 2 below the API layer:
- session markdown render/read round-trips the spec section 6.1 shape
- `SessionStore` creates session ids, writes empty session files, and indexes
  sqlite metadata
- `store_session_asset` writes under `sessions/_assets/`, sanitizes filenames,
  and enforces a 5 MiB cap
- `connect_metadata_db` opens and initializes `metadata.db`

Held back on implementing `/api/sessions*` endpoints because the spec lists
paths but does not define request/response bodies. That API contract is queued
as `S08` in `docs/SMALL_MODEL_TASKS.md`.

## 2026-05-18 - Runtime wiring

Added runtime wiring for the backend without expanding the public API:
- `RuntimeContext` owns config, sqlite connection, and `SessionStore`
- `create_app()` attaches the runtime context to `app.state.runtime`
- config discovery supports `FLIGHTRECORDER_CONFIG`, otherwise falls back to
  `~/flightrecorder/config.toml`, and can return defaults when no config file
  exists for local tests
- sqlite connections now use `check_same_thread=False` for ASGI use

Also preserved small-model outputs already present in the tree:
`PROMPT_DRIFT.md`, `TERMUX_DEPENDENCIES.md`, config fixtures, and schema/Hugo
smoke scripts. Corrected the Termux doc to avoid claiming ARM64 wheel status
before pa-server verification.

## 2026-05-18 - Internal session DTOs and cost logging

Added internal serializers for session metadata, session detail, chat messages,
and stored assets. These are not public API routes yet; they create a stable
internal DTO boundary that future route handlers can reuse after API contract
approval.

Added `costs.py` for inserting `api_calls` rows and summing monthly spend.
This keeps the cost-logging requirement centralized before any provider call
code is added.

Finished more of build order step 2 below the API boundary:
- `SessionStore.add_message()` appends messages and updates message counts
- `SessionStore.store_asset()` stores assets, increments image counts, and
  updates sqlite metadata

Expanded `docs/SMALL_MODEL_TASKS.md` through S15 so smaller models can keep
producing fixtures, smoke tests, status docs, and pricing-format notes while
the main implementation stays on architecture and security boundaries.

Open next: Daniel should approve or edit `docs/API_CONTRACT_DRAFT.md` before
implementing `/api/sessions*` routes.

## 2026-05-18 - Pricing helper boundary

Cleaned `docs/SMALL_MODEL_TASKS.md` into a completed ledger plus an active
queue so smaller models have fresh narrow tasks with smoke tests.

Hardened `docs/PRICING_FORMAT.md` so examples use zero placeholder rates only.
Real rates and exchange rates still need to be checked against current provider
docs before any runtime `pricing.toml` is committed on pa-server.

Extended `costs.py` below the provider boundary:
- parse `pricing.toml` shape into typed pricing records
- validate non-negative rates and token counts
- compute EUR cost from input, output, and cached token counts
- preserve existing sqlite `api_calls` logging and monthly totals

No provider calls, API routes, or public Hugo output were added.

## 2026-05-18 - Budget threshold evaluation

Added internal budget evaluation helpers:
- `evaluate_budget()` classifies monthly spend as `ok`, `warn`, or
  `hard_stop`
- `evaluate_monthly_budget()` combines the sqlite monthly rollup with warn and
  hard-stop thresholds
- tests cover start-inclusive/end-exclusive rollups and threshold boundaries

This still does not enforce a kill switch. Provider wrappers must call these
helpers before paid API calls once real provider calls are implemented.

Reconciled the small-model task ledger through S22 and added S23-S28 for the
next narrow delegation wave.

## 2026-05-18 - Build status checkpoint

Build order steps 1 and 2 are substantially complete below the API boundary.

Step 1 (backend skeleton):
- FastAPI app factory with lazy import, health endpoint, runtime context wiring.
- SQLite schema: sessions, ideas, matches, api_calls tables with indexes.
- Config loading from TOML with path expansion and provider/role/budget parsing.
- Provider abstraction protocol exists; concrete provider SDKs (anthropic, openai,
  google-genai) are listed as dependencies but not yet wired for actual calls.

Step 2 (session storage):
- Session markdown read/write with round-trip fidelity to spec section 6.1.
- SessionStore: create, get, add_message, store_asset, list_sessions.
- Asset storage under sessions/_assets/ with 5 MiB cap and filename sanitization.
- SQLite metadata index with upsert semantics.

Still open:
- Termux ARM64 verification deferred (dependencies documented, not yet tested).
- API routes not implemented; API contract draft awaits Daniel approval.
- Provider calls not wired (no live LLM integration yet).
- Matchmaker, tagger, idea-capture, curator, reviewer, composer, publisher: not
  started.

Small-model tasks S01--S22 are queued and being executed to build out fixtures,
smoke tests, status docs, and API contract materials without touching production
API surface or prompts.

## 2026-05-18 - Append-only project document core

Started build order step 8 below the LLM/API boundary:
- project document creation writes stable frontmatter and sections
- append operations insert one bullet under a named section without reflowing
  unrelated sections
- `last_appended` is updated per append
- unknown or missing sections fail closed
- generated bullet content has one leading markdown marker stripped defensively

The valid section list includes `Ideas` because the idea-capture output contract
in spec section 8 includes it, even though the section 6.2 document example
omits it.

Still open for step 8: parse and validate idea-capture operations, wire
documents git auto-commit, and test on hand-rolled sessions before going live.
