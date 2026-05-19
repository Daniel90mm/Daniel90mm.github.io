# Small-model task queue

These tasks are intentionally narrow. Each task should be doable by a smaller
model without broad architecture decisions. Do one task at a time, keep edits
inside the listed files, and run the smoke test before handing back.

Do not change prompts, public Hugo output, API shapes, sqlite schema, or
publisher redaction behavior unless the task explicitly says so.

## Operating rules for the junior agent

Read these every session. They exist because past collisions cost real
debugging time.

1. **Stay strictly inside the "Where:" file list.** If you find yourself
   wanting to edit a file not in the list, stop. Ask Daniel for a new task
   that includes that file. Do not silently widen scope.
2. **No repo-wide refactors.** Do not run sed/grep-replace across the tree.
   Do not rename symbols outside your task files. Do not "tidy up" adjacent
   code while passing through.
3. **Read files fresh before every edit.** The senior agent and possibly
   other juniors may be editing in parallel. Re-Read the file immediately
   before each Edit. If a file changed since you last read it, treat your
   plan for that file as stale and re-plan.
4. **Run the listed smoke / pytest commands after every meaningful edit.**
   Not just at the end. A failure caught after one file is easy to fix; a
   failure caught after five files is a debugging session.
5. **Hand back when tests pass. Do not commit.** Daniel commits after
   verification. If you commit, you make it harder for the senior agent to
   bundle the work into a coherent commit.
6. **One task at a time. Top of the active queue unless told otherwise.**
   Do not pick S118 and S119 in the same session. Finish, hand back, wait
   for the next task.
7. **If you hit a "file modified since read" error or unexpected diff,
   stop.** Report the state and wait. That is the signal that someone else
   is editing the same file.
8. **No commits, no pushes, no branch changes.** Working tree only.

## Suggested invocation prompt

> You are a junior agent on the flightrecorder project. Open
> `flightrecorder/docs/SMALL_MODEL_TASKS.md` and read the "Operating rules
> for the junior agent" section in full before starting. Then pick the
> single top task in the Active queue, do exactly what its "Where:" /
> "What:" sections say, run the listed smoke / pytest commands, and stop
> when they pass. Do not commit, do not push, do not edit files outside the
> "Where:" list. If a file you need to edit has changed since you read it,
> stop and report.

## Completed ledger

The following small-model tasks are done and should not be repeated unless a
regression is found:

| ID | Result |
|----|--------|
| S01 | Prompt/spec drift report in `docs/PROMPT_DRIFT.md`. |
| S02 | Termux dependency note in `docs/TERMUX_DEPENDENCIES.md`. |
| S03 | Config fixtures in `tests/fixtures/config/`. |
| S04 | SQLite schema smoke script. |
| S05 | README quickstart after backend skeleton. |
| S06 | Hugo workflow path smoke script. |
| S07 | Session storage smoke script. |
| S08 | Draft session API contract. |
| S09 | Runtime context smoke script. |
| S10 | README quickstart factory correction. |
| S11 | Storage edge-case tests. |
| S12 | Config fixture tests. |
| S13 | Build-order status doc. |
| S14 | API call logging smoke script. |
| S15 | Pricing file format note. |
| S16 | Backend health smoke script. |
| S17 | Serializer asset path regression test. |
| S18 | Pricing smoke script. |
| S19 | API contract review checklist. |
| S20 | Cost boundary tests, taken by senior agent during cleanup. |
| S21 | Research log checkpoint. |
| S22 | Smoke command index. |
| S23 | Budget smoke script. |
| S24 | Missing-work status doc. |
| S25 | Config budget threshold validation tests. |
| S26 | API draft examples consistency pass, completed by senior agent. |
| S27 | Package import smoke. |
| S28 | README missing approval warning. |
| S29 | Project document smoke script. |
| S30 | Project document README note. |
| S31 | Small-model queue smoke sync. |
| S32 | Project document filename tests. |
| S33 | Missing-work snapshot sync. |
| S34 | API contract review sync. |
| S35 | Session API smoke script, completed by senior agent. |
| S36 | Session API README examples, completed by senior agent. |
| S37 | API pagination validation tests, completed by senior agent. |
| S38 | Termux phone helper draft, completed by senior agent. |
| S39 | Termux docs sync, completed by senior agent. |
| S40 | Session API smoke command sync, completed by senior agent. |
| S41 | Missing-work snapshot after API completion, completed by senior agent. |
| S42 | API smoke route status docs, completed by senior agent. |
| S43 | Termux helper smoke doc, completed by senior agent. |
| S44 | Termux helper command tests. |
| S45 | Chat endpoint contract draft. |
| S46 | Idea-capture operation boundary, completed by senior agent. |
| S47 | Idea-capture smoke command sync, completed by senior agent. |
| S48 | Idea-capture parser edge docs. |
| S49 | Idea-capture README status. |
| S50 | Idea-capture smoke docs. |
| S51 | Documents git smoke. |
| S52 | Documents git auto-commit path, completed by senior agent. |
| S53 | Documents git docs. |
| S54 | Budget hard-stop sentinel, completed by senior agent. |
| S55 | Budget sentinel smoke. |
| S56 | Budget docs update. |
| S57 | Smoke command sync for new guards. |
| S58 | Budget guard README status. |
| S59 | Provider call guard smoke. |
| S60 | Provider call guard docs. |
| S61 | Provider guard status sync. |
| S62 | Provider guard hard-stop breach smoke. |
| S63 | Budget/provider guard cross-links. |
| S64 | Build status consistency audit. |
| S65 | Completed worker task. |
| S66 | Completed worker task. |
| S67 | Completed worker task. |
| S68 | Completed worker task. |
| S69 | Completed worker task. |
| S70 | Completed worker task. |
| S71 | Completed worker task. |
| S72 | Completed worker task. |
| S73 | Completed worker task. |
| S74 | Completed worker task. |
| S75 | Completed worker task. |
| S76 | Completed worker task. |
| S77 | Completed worker task. |
| S78 | Completed worker task. |
| S79 | Completed worker task. |
| S80 | Completed worker task. |
| S81 | Completed worker task. |
| S82 | Completed worker task. |
| S83 | Completed worker task. |
| S84 | Completed worker task. |
| S85 | Completed worker task. |
| S86 | Completed worker task. |
| S87 | Completed worker task. |
| S88 | Completed worker task. |
| S89 | Completed worker task. |
| S90 | Completed worker task. |
| S91 | Completed worker task. |
| S92 | Completed worker task. |
| S93 | Completed worker task. |
| S94 | Completed worker task. |
| S95 | Completed worker task. |
| S96 | Completed worker task. |
| S97 | Completed worker task. |
| S98 | Completed worker task. |
| S99 | Completed worker task. |
| S100 | Completed worker task. |
| S101 | Completed worker task. |
| S102 | Completed worker task. |
| S103 | Completed worker task. |
| S104 | Completed worker task. |
| S105 | Completed worker task. |
| S106 | Completed worker task. |
| S107 | Completed worker task. |
| S108 | Completed worker task. |
| S109 | Completed worker task. |
| S110 | Completed worker task. |
| S111 | Project registry loader. |
| S112 | Matchmaker rejection fixture files. |
| S113 | Navigation index consistency smoke. |
| S114 | Smoke command index sync. |
| S115 | Build status update for project registry step. |
| S116 | Chat endpoint per approved contract, verified by senior agent. |
| S117 | Idea-capture LLM wiring, verified by senior agent. |
| S118 | Adversarial robustness sweep for parse_idea_operations. |
| S119 | Session round-trip integration test. |
| S120 | Publisher pipeline smoke test. |
| S121 | Adversarial fixture directory resolver smoke. |
| S122 | Matchmaker API contract doc and NAVIGATION row. |
| S123 | Hugo path smoke after museum rename. |
| S124 | Local Hugo production build smoke. |
| S125 | GitHub Pages workflow smoke. |
| S126 | Generated-site internal link smoke. |
| S127 | Root deployment README. |
| S128 | Hugo smoke commands to one-liner sync. |

## Active queue

Pick from the top unless Daniel or the senior agent says otherwise.

## S129 - Sync frontend scope with implemented API

Where:
- `flightrecorder/docs/FRONTEND_SCOPE.md`
- `flightrecorder/docs/NAVIGATION.md`

What:
- Update `docs/FRONTEND_SCOPE.md` so it no longer says all frontend surfaces
  are not started and no longer lists chat/extract as missing.
- Keep this as a planning/status document, not an implementation proposal.
- It should state:
  1. Backend routes currently available to a v1 dogfood frontend:
     `GET /health`, `POST /api/sessions`, `GET /api/sessions`,
     `GET /api/sessions/{id}`, `POST /api/sessions/{id}/upload`,
     `POST /api/sessions/{id}/messages`,
     `POST /api/sessions/{id}/extract`,
     `POST /api/matchmaker/run`.
  2. First dogfood frontend target: create/list sessions, chat over SSE,
     run extraction, and inspect returned session transcript.
  3. Still missing from backend: document/spaghetti listing routes,
     match decision routes, voice, budget API, publisher controls.
  4. Frontend implementation should be plain static HTML/CSS/JS first,
     no framework, until dogfooding proves the API shape.
- If `docs/NAVIGATION.md` already contains the `docs/FRONTEND_SCOPE.md`
  row, leave it alone. If missing, add it.
- Do not edit source code in this task.

Why:
- The frontend scope doc is stale and currently pushes the next agent toward
  outdated assumptions. Dogfooding needs the status document to match the
  actual backend routes.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
PYTHONPATH=src/backend python tests/smoke/smoke_docs_navigation_consistency.py
grep -q "POST /api/sessions/{id}/messages" docs/FRONTEND_SCOPE.md
grep -q "POST /api/sessions/{id}/extract" docs/FRONTEND_SCOPE.md
grep -q "plain static HTML/CSS/JS" docs/FRONTEND_SCOPE.md
```

Hand-back:
- When the commands pass, stop. Do not commit.

## S130 - Add static frontend dogfood shell

Where:
- `flightrecorder/src/frontend/index.html` (new file)
- `flightrecorder/src/frontend/styles.css` (new file)
- `flightrecorder/src/frontend/app.js` (new file)
- `flightrecorder/tests/smoke/smoke_frontend_static.py` (new file)
- `flightrecorder/docs/SMOKE_COMMANDS.md`

What:
- Build a plain static frontend shell for the dogfood loop. No build tool,
  no framework, no dependency changes.
- `index.html` should include:
  1. App title `flightrecorder`.
  2. A session creation form with provider, model, and slug inputs.
  3. A session list container.
  4. A transcript container.
  5. A message textarea/button.
  6. An extract button.
  7. A status/output area for errors and extraction results.
  8. Links to `styles.css` and `app.js`.
- `styles.css` should create a quiet terminal/TUI-inspired layout that works
  on mobile and desktop. Keep it compact; no decorative marketing page.
- `app.js` should define functions for:
  1. `api(path, options)` wrapper.
  2. Creating a session with `POST /api/sessions`.
  3. Listing sessions with `GET /api/sessions`.
  4. Loading one session with `GET /api/sessions/{id}`.
  5. Sending a message to `POST /api/sessions/{id}/messages` and rendering
     streamed SSE tokens from the response body.
  6. Running extraction with `POST /api/sessions/{id}/extract`.
  7. Rendering transcript messages and status text.
- Keep the JS defensive: disable chat/extract buttons when no session is
  selected, show readable error text, and avoid global namespace clutter
  except one `window.flightrecorderApp` debug object.
- Add `tests/smoke/smoke_frontend_static.py` that asserts the three frontend
  files exist and that `app.js` references the route strings above.
- Add the new smoke to `docs/SMOKE_COMMANDS.md`.
- Do not edit backend serving in this task.

Why:
- A static frontend gives us the fastest dogfood surface without committing
  to Svelte/build tooling before the API loop has been exercised.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
PYTHONPATH=src/backend python tests/smoke/smoke_frontend_static.py
PYTHONPATH=src/backend python tests/smoke/smoke_small_model_tasks.py
```

Hand-back:
- When both commands pass, stop. Do not commit.

## S131 - Serve static frontend from FastAPI

Where:
- `flightrecorder/src/backend/flightrecorder/app.py`
- `flightrecorder/tests/integration/test_frontend_serving.py` (new file)
- `flightrecorder/docs/API_CURRENT_STATE.md`
- `flightrecorder/docs/FRONTEND_SCOPE.md`

What:
- Serve the static frontend files from FastAPI when `src/frontend/index.html`
  exists.
- Add:
  1. `GET /` returns `src/frontend/index.html`.
  2. Static assets under `/assets/*` serve files from `src/frontend/`
     except `index.html`.
- Use FastAPI/Starlette standard responses. Do not add dependencies.
- Keep `/api/*` behavior unchanged.
- Add integration tests that:
  1. `GET /` returns status 200 and contains `flightrecorder`.
  2. `GET /assets/app.js` returns status 200 and JavaScript content.
  3. `GET /health` still returns `{"status": "ok"}`.
  4. `GET /api/sessions` still works against a temp runtime.
- Update docs to mention the root frontend route and static asset route.
- Do not change the frontend files in this task except if a path reference
  must be corrected from S130.

Why:
- Opening a file from disk is useful, but dogfooding on the phone/server
  needs the backend to serve the UI from the same origin as the API.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
.venv/bin/python -m pytest tests/integration/test_frontend_serving.py tests/unit/test_app.py -q
PYTHONPATH=src/backend python tests/smoke/smoke_frontend_static.py
```

Hand-back:
- When the commands pass, stop. Do not commit.

## S132 - Add frontend chat stream parser smoke

Where:
- `flightrecorder/src/frontend/app.js`
- `flightrecorder/tests/smoke/smoke_frontend_sse_parser.py` (new file)
- `flightrecorder/docs/SMOKE_COMMANDS.md`

What:
- Add a small pure function in `app.js` for parsing SSE text chunks from the
  chat endpoint response into `{event, data}` objects. Keep it independent
  from DOM state so it can be checked by a smoke script.
- The parser should handle:
  1. Multiple events in one chunk.
  2. Partial trailing event buffered until the next chunk.
  3. `event: token` with JSON data.
  4. `event: done` with JSON data.
  5. `event: error` with JSON data.
- Expose the parser through `window.flightrecorderApp` only when running in
  a browser.
- Add `tests/smoke/smoke_frontend_sse_parser.py` that reads `app.js` and,
  using a minimal JS execution approach available locally if possible
  (`node` if installed), verifies sample chunks parse correctly. If `node`
  is not installed, the smoke may fall back to strict text checks for the
  parser function name and sample event literals, but it should print that
  it skipped runtime JS execution.
- Add the smoke to `docs/SMOKE_COMMANDS.md`.
- Do not edit backend code.

Why:
- The chat endpoint streams SSE. The most fragile frontend logic is usually
  incremental parsing; isolate it before styling or layout work grows.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
PYTHONPATH=src/backend python tests/smoke/smoke_frontend_sse_parser.py
PYTHONPATH=src/backend python tests/smoke/smoke_frontend_static.py
```

Hand-back:
- When both commands pass, stop. Do not commit.

## S133 - Add frontend dogfood route smoke

Where:
- `flightrecorder/tests/smoke/smoke_frontend_dogfood.py` (new file)
- `flightrecorder/docs/SMOKE_COMMANDS.md`

What:
- Add an executable smoke script that starts the FastAPI app in-process with
  `TestClient` and verifies the frontend/API dogfood loop at the HTTP level.
- The smoke should:
  1. Build a runtime in a temporary directory.
  2. Stub `runtime.brainstorm_provider` and `runtime.idea_capture_provider`
     like the integration tests do.
  3. `GET /` and assert the frontend HTML loads.
  4. `POST /api/sessions` to create a session.
  5. `POST /api/sessions/{id}/messages` and assert the SSE response includes
     token and done events.
  6. `POST /api/sessions/{id}/extract` and assert one project append and one
     spaghetti idea.
  7. `GET /api/sessions/{id}` and assert two messages are present.
  8. Print `frontend dogfood smoke test passed` on success.
- Add the smoke to `docs/SMOKE_COMMANDS.md`.
- Do not edit source modules unless the smoke exposes a real serving bug from
  S131; if that happens, keep the fix minimal and explain it in comments.

Why:
- This proves the usable path we care about: load UI, create a session, chat,
  extract ideas, and inspect the session.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
.venv/bin/python tests/smoke/smoke_frontend_dogfood.py
PYTHONPATH=src/backend python tests/smoke/smoke_small_model_tasks.py
```

Hand-back:
- When both commands pass, stop. Do not commit.

## S134 - Add frontend dogfood notes

Where:
- `flightrecorder/README.md`
- `flightrecorder/docs/FRONTEND_SCOPE.md`
- `flightrecorder/docs/SMOKE_COMMANDS.md`

What:
- Document how to run the dogfood frontend locally.
- README should include:
  1. Start command: `scripts/dev-backend.sh`.
  2. Browser URL: `http://127.0.0.1:8000/`.
  3. Minimal dogfood workflow: create session, send message, run extract,
     inspect transcript/result.
  4. Note that real providers require config/API keys; tests use stubs.
- `FRONTEND_SCOPE.md` should mark the static dogfood shell as implemented
  once S130-S133 are done.
- `SMOKE_COMMANDS.md` should include any frontend smoke that exists but is
  missing from the table.
- Do not edit backend or frontend source in this task.

Why:
- Once the dogfood loop exists, the next person should not have to reverse
  engineer how to start it.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
grep -q "http://127.0.0.1:8000/" README.md
grep -q "scripts/dev-backend.sh" README.md
PYTHONPATH=src/backend python tests/smoke/smoke_small_model_tasks.py
```

Hand-back:
- When the commands pass, stop. Do not commit.
