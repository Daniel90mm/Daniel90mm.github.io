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
| S135 | Dogfood read API contract for projects, documents, and spaghetti. |
| S136 | Read-only projects/documents API, verified and tightened by senior agent. |
| S137 | Read-only spaghetti API, verified and path-guarded by senior agent. |
| S138 | Frontend read panels for documents and spaghetti, verified by senior agent. |
| S139 | Dogfood read round-trip integration test. |
| S140 | Dogfood read workflow docs. |
| S141 | Real-provider Anthropic dogfood config examples. |
| S142 | Example config/pricing smoke, extended by senior agent for prototype config. |
| S143 | Runtime provider status API contract. |
| S144 | Runtime provider status API, tightened by senior agent for API-key/readiness issues. |
| S145 | Frontend runtime readiness panel, hardened by senior agent for safe text rendering. |
| S146 | Termux real-provider dogfood checklist. |
| S147 | One-command prototype launcher, hardened by senior agent for cwd safety. |
| S148 | Frontend auto-selects first document/spaghetti artifacts. |
| S149 | Read-only provider call ledger API. |
| S150 | Frontend provider call ledger panel, hardened by senior agent for safe text rendering. |
| S151 | Image upload control in dogfood frontend. |
| S152 | Offline prototype walkthrough doc and smoke. |

## Active queue

Pick from the top unless Daniel or the senior agent says otherwise.

## S153 - Draft publish preview API contract

Where:
- `flightrecorder/docs/PUBLISH_PREVIEW_API.md` (new file)
- `flightrecorder/docs/API_CURRENT_STATE.md`
- `flightrecorder/docs/NAVIGATION.md`

What:
- Draft a concise contract for `GET /api/publish/preview`.
- It should be read-only and accept:
  1. `source_kind=session|document|spaghetti`
  2. `source_id=<session_id|document_ref|idea_id>`
- Response should include:
  `source_kind`, `source_id`, `publishable`, `rejection_reason`,
  `approved_count`, and `snippets`.
- State clearly that the current Null publisher is fail-closed and can return
  `publishable=false` with a rejection reason.
- Mark the route draft-only in `API_CURRENT_STATE.md`.
- Add the new doc to navigation.
- Do not implement the route in this task.

Why:
- The MVP needs a visible bridge from private capture to public Hugo output,
  but publisher safety must stay explicit and fail-closed.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
grep -q "GET /api/publish/preview" docs/PUBLISH_PREVIEW_API.md
PYTHONPATH=src/backend python tests/smoke/smoke_docs_navigation_consistency.py
```

Hand-back:
- When all commands pass, stop. Do not commit.

## S154 - Implement read-only publish preview API

Where:
- `flightrecorder/src/backend/flightrecorder/api.py`
- `flightrecorder/tests/integration/test_publish_preview_api.py` (new file)
- `flightrecorder/tests/smoke/smoke_publish_preview_api.py` (new file)
- `flightrecorder/docs/API_CURRENT_STATE.md`
- `flightrecorder/docs/SMOKE_COMMANDS.md`

What:
- Implement `GET /api/publish/preview` from `docs/PUBLISH_PREVIEW_API.md`.
- Resolve source bodies for:
  1. `source_kind=session` from session transcript;
  2. `source_kind=document` from project document markdown;
  3. `source_kind=spaghetti` from spaghetti idea markdown body.
- Run the existing `run_publish_pipeline` with default fail-closed stages.
- Return the preview/audit summary as JSON.
- Return 404 for unknown sources and 422 for unknown `source_kind`.
- The route must not write files, sqlite rows, git commits, or Hugo content.
- Add integration and smoke tests.

Why:
- Users need to see the public-publishing gate, even before the real curator
  is wired. Fail-closed preview is still product progress.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
.venv/bin/python -m pytest tests/integration/test_publish_preview_api.py -q
.venv/bin/python tests/smoke/smoke_publish_preview_api.py
PYTHONPATH=src/backend python tests/smoke/smoke_api_current_state.py
```

Hand-back:
- When all commands pass, stop. Do not commit.

## S155 - Add publish preview panel to the frontend

Where:
- `flightrecorder/src/frontend/index.html`
- `flightrecorder/src/frontend/styles.css`
- `flightrecorder/src/frontend/app.js`
- `flightrecorder/tests/smoke/smoke_frontend_static.py`
- `flightrecorder/tests/smoke/smoke_frontend_dogfood.py`
- `flightrecorder/docs/FRONTEND_SCOPE.md`

What:
- Add a compact "Publish Preview" panel under the document/spaghetti panels.
- Provide buttons for selected document and selected spaghetti idea.
- Call `GET /api/publish/preview` with the selected source.
- Render `publishable`, `rejection_reason`, and snippet count using
  `textContent`.
- Empty state should explain that no source is selected.
- Update frontend smokes and docs.

Why:
- The MVP should make the future public-publishing path visible from the
  browser, not hidden in backend tests.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
PYTHONPATH=src/backend python tests/smoke/smoke_frontend_static.py
.venv/bin/python tests/smoke/smoke_frontend_dogfood.py
```

Hand-back:
- When both commands pass, stop. Do not commit.

## S156 - Add prototype UI screenshot smoke

Where:
- `flightrecorder/tests/smoke/smoke_prototype_ui_screenshot.py` (new file)
- `flightrecorder/docs/SMOKE_COMMANDS.md`

What:
- Add a smoke script that:
  1. skips cleanly if `google-chrome` is unavailable;
  2. starts the app with `config.prototype.toml` using `TestClient` or a local
     subprocess;
  3. creates a prototype session, chat, and extraction;
  4. captures a screenshot to `/tmp/flightrecorder-prototype-ui.png`;
  5. verifies the screenshot file exists and is non-empty.
- Keep it smoke-level; do not add Playwright.
- Update `docs/SMOKE_COMMANDS.md`.

Why:
- We need a repeatable way to prove the browser surface is not just API-green.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
.venv/bin/python tests/smoke/smoke_prototype_ui_screenshot.py
```

Hand-back:
- When the command passes or skips cleanly, stop. Do not commit.

## S157 - Add upload round-trip smoke

Where:
- `flightrecorder/tests/smoke/smoke_upload_api.py` (new file)
- `flightrecorder/docs/SMOKE_COMMANDS.md`

What:
- Add a smoke script using `TestClient` that:
  1. creates a session;
  2. uploads a tiny in-memory PNG or JPEG to
     `POST /api/sessions/{session_id}/upload`;
  3. verifies `image_count` increments;
  4. fetches the session detail and verifies the asset metadata is present.
- Update smoke command docs.

Why:
- The frontend now exposes image upload; the backend upload path should have
  a direct dogfood smoke.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
.venv/bin/python tests/smoke/smoke_upload_api.py
```

Hand-back:
- When the command passes, stop. Do not commit.

## S158 - Update public flightrecorder page for prototype state

Where:
- `museum/content/projects/flightrecorder/_index.md`
- `museum/content/projects/flightrecorder/2026-05-19-dogfood-loop.md`
- `flightrecorder/tests/smoke/smoke_hugo_build.py`
- `flightrecorder/tests/smoke/smoke_hugo_internal_links.py`

What:
- Update public copy to mention:
  1. one-command prototype launcher;
  2. calls ledger panel;
  3. image upload control;
  4. publish preview is next/fail-closed.
- Do not over-market it; keep the tone factual.
- Run Hugo build and internal link smokes.

Why:
- The public site should keep reflecting visible product progress as the MVP
  becomes more real.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
python tests/smoke/smoke_hugo_build.py
python tests/smoke/smoke_hugo_internal_links.py
```

Hand-back:
- When both commands pass, stop. Do not commit.
