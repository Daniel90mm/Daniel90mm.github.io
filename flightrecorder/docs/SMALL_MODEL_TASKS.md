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
| S129 | Frontend scope synced with implemented API. |
| S130 | Static frontend dogfood shell. |
| S131 | Static frontend served from FastAPI. |
| S132 | Frontend chat stream parser smoke. |
| S133 | Frontend dogfood route smoke. |
| S134 | Frontend dogfood notes. |

## Active queue

Pick from the top unless Daniel or the senior agent says otherwise.

## S135 - Draft read-only dogfood API contract

Where:
- `flightrecorder/docs/DOGFOOD_READ_API.md` (new file)
- `flightrecorder/docs/NAVIGATION.md`

What:
- Draft a concise contract for the next read-only routes needed by the
  dogfood frontend.
- Cover these routes only:
  1. `GET /api/projects` - list active project registry entries.
  2. `GET /api/documents` - list project document refs and paths.
  3. `GET /api/documents/{ref}` - return one project document as plain
     markdown text plus metadata.
  4. `GET /api/spaghetti` - list spaghetti ideas from sqlite.
  5. `GET /api/spaghetti/{idea_id}` - return one spaghetti markdown body
     plus indexed metadata.
- For each route, specify request, success response, and failure status
  codes. Keep response shapes simple and JSON-only except markdown bodies
  embedded as strings.
- State explicitly that these routes are read-only and must not mutate
  documents, spaghetti files, git state, or sqlite rows.
- Add the new doc to `docs/NAVIGATION.md`.
- Do not edit source code in this task.

Why:
- The frontend can create/chat/extract, but cannot inspect extracted project
  documents or spaghetti ideas through HTTP. The read-only contract should be
  settled before implementation.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
test -f docs/DOGFOOD_READ_API.md
grep -q "GET /api/documents/{ref}" docs/DOGFOOD_READ_API.md
grep -q "GET /api/spaghetti/{idea_id}" docs/DOGFOOD_READ_API.md
PYTHONPATH=src/backend python tests/smoke/smoke_docs_navigation_consistency.py
```

Hand-back:
- When the commands pass, stop. Do not commit.

## S136 - Implement read-only projects and documents API

Where:
- `flightrecorder/src/backend/flightrecorder/api.py`
- `flightrecorder/tests/integration/test_documents_api.py` (new file)
- `flightrecorder/tests/smoke/smoke_documents_api.py` (new file)
- `flightrecorder/docs/API_CURRENT_STATE.md`
- `flightrecorder/docs/SMOKE_COMMANDS.md`

What:
- Implement the read-only project/document routes from
  `docs/DOGFOOD_READ_API.md`:
  1. `GET /api/projects`
  2. `GET /api/documents`
  3. `GET /api/documents/{ref}`
- Use existing helpers from `documents.py` and `project_registry.py` where
  possible. Do not add dependencies.
- Behavior:
  1. `GET /api/projects` reads `<runtime_home>/projects.json` if present.
     If absent, return `{"projects": []}`.
  2. `GET /api/documents` lists markdown files in
     `<runtime_home>/documents/`, sorted by filename. If absent, return
     `{"documents": []}`.
  3. `GET /api/documents/{ref}` sanitizes refs with existing document
     helpers and returns 404 if the markdown file does not exist.
  4. None of these routes may create files, initialize git, or mutate sqlite.
- Add integration tests using a temp runtime with a small `projects.json` and
  two document files.
- Add a smoke script that exercises the three routes with `TestClient`.
- Update `API_CURRENT_STATE.md` and `SMOKE_COMMANDS.md`.

Why:
- After extraction, dogfooding needs a way to inspect the append-only project
  documents from the browser.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
.venv/bin/python -m pytest tests/integration/test_documents_api.py -q
.venv/bin/python tests/smoke/smoke_documents_api.py
PYTHONPATH=src/backend python tests/smoke/smoke_api_current_state.py
```

Hand-back:
- When all commands pass, stop. Do not commit.

## S137 - Implement read-only spaghetti API

Where:
- `flightrecorder/src/backend/flightrecorder/api.py`
- `flightrecorder/tests/integration/test_spaghetti_api.py` (new file)
- `flightrecorder/tests/smoke/smoke_spaghetti_api.py` (new file)
- `flightrecorder/docs/API_CURRENT_STATE.md`
- `flightrecorder/docs/SMOKE_COMMANDS.md`

What:
- Implement the read-only spaghetti routes from `docs/DOGFOOD_READ_API.md`:
  1. `GET /api/spaghetti`
  2. `GET /api/spaghetti/{idea_id}`
- Use sqlite `ideas` as the index and read markdown bodies from the indexed
  path. Do not mutate files or sqlite.
- Behavior:
  1. List route returns newest first if `captured_at` exists, otherwise by
     `idea_id`.
  2. Detail route returns 404 for unknown ids.
  3. Detail route should include indexed metadata plus markdown body with
     frontmatter stripped, matching the helper behavior already used by
     matchmaker.
  4. If the indexed markdown file is missing, return 404 rather than an empty
     body.
- Add integration tests with temp sqlite rows and temp markdown files.
- Add a smoke script that writes one spaghetti idea through existing helper
  code if practical, then verifies list/detail routes.
- Update `API_CURRENT_STATE.md` and `SMOKE_COMMANDS.md`.

Why:
- Extracted loose ideas currently disappear into files/sqlite from the user's
  point of view. The dogfood UI needs a read path for the wall.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
.venv/bin/python -m pytest tests/integration/test_spaghetti_api.py -q
.venv/bin/python tests/smoke/smoke_spaghetti_api.py
PYTHONPATH=src/backend python tests/smoke/smoke_api_current_state.py
```

Hand-back:
- When all commands pass, stop. Do not commit.

## S138 - Add frontend read panels for documents and spaghetti

Where:
- `flightrecorder/src/frontend/index.html`
- `flightrecorder/src/frontend/styles.css`
- `flightrecorder/src/frontend/app.js`
- `flightrecorder/tests/smoke/smoke_frontend_static.py`
- `flightrecorder/tests/smoke/smoke_frontend_dogfood.py`

What:
- Extend the static dogfood frontend to inspect read-only project documents
  and spaghetti ideas once S136/S137 routes exist.
- Add UI sections for:
  1. Project document list.
  2. Selected project document markdown body.
  3. Spaghetti idea list.
  4. Selected spaghetti markdown body.
- `app.js` should add functions for:
  1. `GET /api/documents`
  2. `GET /api/documents/{ref}`
  3. `GET /api/spaghetti`
  4. `GET /api/spaghetti/{idea_id}`
- After extraction completes, refresh document and spaghetti lists.
- Keep rendering safe: use `textContent` for markdown bodies, not
  `innerHTML`.
- Update the frontend static smoke to check for the new route references.
- Update the dogfood smoke to assert the frontend still loads and that the
  new route strings exist in served `app.js`.

Why:
- The first dogfood loop is not complete until the browser can inspect what
  extraction wrote.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
PYTHONPATH=src/backend python tests/smoke/smoke_frontend_static.py
.venv/bin/python tests/smoke/smoke_frontend_dogfood.py
```

Hand-back:
- When both commands pass, stop. Do not commit.

## S139 - Add read API round-trip integration test

Where:
- `flightrecorder/tests/integration/test_dogfood_read_round_trip.py` (new file)
- `flightrecorder/docs/SMOKE_COMMANDS.md`

What:
- Add one integration test that proves the whole dogfood read path:
  1. Create a session.
  2. Send one stubbed chat message.
  3. Run extraction with one `project_append` and one `spaghetti`.
  4. Use `GET /api/documents` to find the project document.
  5. Use `GET /api/documents/{ref}` to verify the appended bullet.
  6. Use `GET /api/spaghetti` to find the idea.
  7. Use `GET /api/spaghetti/{idea_id}` to verify the markdown body.
  8. Verify `api_calls` still has two rows for the session.
- Reuse stub patterns from existing integration tests. Do not factor shared
  helpers in this task.
- Add any new test command to `SMOKE_COMMANDS.md` only if you add a smoke;
  otherwise leave `SMOKE_COMMANDS.md` untouched.

Why:
- Unit-level route tests are useful, but the contract that matters is
  extraction output becoming visible through read APIs.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
.venv/bin/python -m pytest tests/integration/test_dogfood_read_round_trip.py -q
.venv/bin/python -m pytest tests/integration/ -q
```

Hand-back:
- When both commands pass, stop. Do not commit.

## S140 - Document dogfood read workflow

Where:
- `flightrecorder/README.md`
- `flightrecorder/docs/FRONTEND_SCOPE.md`
- `flightrecorder/docs/API_CURRENT_STATE.md`

What:
- Update docs after S136-S139 are done.
- README dogfood workflow should mention:
  1. Create a session.
  2. Chat.
  3. Extract.
  4. Inspect project documents and spaghetti ideas in the browser.
- `FRONTEND_SCOPE.md` should mark document/spaghetti read panels as
  implemented.
- `API_CURRENT_STATE.md` should accurately list all read-only document and
  spaghetti routes.
- Do not edit code in this task.

Why:
- Once the read path exists, docs need to tell Daniel how to use it and what
  remains missing.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
grep -q "spaghetti" README.md
grep -q "GET /api/documents/{ref}" docs/API_CURRENT_STATE.md
grep -q "GET /api/spaghetti/{idea_id}" docs/API_CURRENT_STATE.md
PYTHONPATH=src/backend python tests/smoke/smoke_small_model_tasks.py
```

Hand-back:
- When all commands pass, stop. Do not commit.
