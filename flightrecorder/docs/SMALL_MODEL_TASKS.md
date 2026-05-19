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
| S153 | Publish preview API contract. |
| S154 | Read-only fail-closed publish preview API. |
| S155 | Frontend publish preview panel, extended by senior agent with session preview and selected-session summary. |
| S156 | Prototype UI screenshot smoke. |
| S157 | Upload round-trip smoke, tightened by senior agent for returned asset metadata. |
| S158 | Public flightrecorder page update for prototype state. |

## Active queue

Pick from the top unless Daniel or the senior agent says otherwise.

## S159 - Add uploaded asset list to the frontend

Where:
- `flightrecorder/src/frontend/index.html`
- `flightrecorder/src/frontend/styles.css`
- `flightrecorder/src/frontend/app.js`
- `flightrecorder/tests/smoke/smoke_frontend_static.py`
- `flightrecorder/tests/smoke/smoke_frontend_dogfood.py`
- `flightrecorder/docs/FRONTEND_SCOPE.md`

What:
- Add a compact uploaded-assets list for the selected session.
- Use the `assets` array from `GET /api/sessions/{id}`.
- Show filename and size in bytes for each asset.
- Update the list immediately after an upload by reloading the selected
  session detail.
- Render with DOM nodes and `textContent`; do not use `innerHTML` for asset
  rows.

Why:
- Image upload is now visible as a button and API response, but the MVP should
  show what is attached to the active session without inspecting the filesystem.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
PYTHONPATH=src/backend python tests/smoke/smoke_frontend_static.py
.venv/bin/python tests/smoke/smoke_frontend_dogfood.py
```

Hand-back:
- When both commands pass, stop. Do not commit.

## S160 - Add session asset metadata integration test

Where:
- `flightrecorder/tests/integration/test_session_assets_api.py` (new file)
- `flightrecorder/docs/API_CONTRACT_DRAFT.md`
- `flightrecorder/docs/SMOKE_COMMANDS.md`

What:
- Add an integration test that creates a session, uploads two tiny images, then
  fetches `GET /api/sessions/{id}`.
- Assert that `image_count == 2` and `assets` contains two objects with
  `filename`, `relative_path`, and `size_bytes`.
- Assert `relative_path` never exposes an absolute path.
- Add the pytest command to the smoke command docs.

Why:
- Uploaded asset metadata is now part of the MVP API surface and needs direct
  regression coverage beyond the smoke script.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
.venv/bin/python -m pytest tests/integration/test_session_assets_api.py -q
```

Hand-back:
- When the command passes, stop. Do not commit.

## S161 - Add publish preview frontend dogfood assertions

Where:
- `flightrecorder/tests/smoke/smoke_frontend_dogfood.py`
- `flightrecorder/tests/smoke/smoke_publish_preview_api.py`

What:
- Extend the frontend dogfood smoke to verify `/assets/app.js` references:
  1. `preview-session-btn`;
  2. `preview-doc-btn`;
  3. `preview-spag-btn`;
  4. `api/publish/preview`.
- Extend the publish preview smoke to cover the session/document/spaghetti
  paths plus one unknown-source 404.
- Do not add a browser dependency here.

Why:
- The publish preview is now a visible MVP gate; smoke coverage should catch
  accidental frontend/API drift.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
.venv/bin/python tests/smoke/smoke_frontend_dogfood.py
.venv/bin/python tests/smoke/smoke_publish_preview_api.py
```

Hand-back:
- When both commands pass, stop. Do not commit.

## S162 - Document the prototype publish-preview walkthrough

Where:
- `flightrecorder/docs/PROTOTYPE_WALKTHROUGH.md`
- `flightrecorder/tests/smoke/smoke_prototype_walkthrough.py`
- `flightrecorder/docs/NAVIGATION.md`

What:
- Update the walkthrough with the current UI flow:
  1. start `scripts/dev-prototype.sh`;
  2. create or auto-select a session;
  3. chat and extract;
  4. inspect session summary and uploaded assets;
  5. run session/document/spaghetti publish preview and observe fail-closed
     output.
- Update the walkthrough smoke so it checks these concrete phrases.

Why:
- The local prototype should be runnable by Daniel without remembering which
  parts landed in which commit.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
.venv/bin/python tests/smoke/smoke_prototype_walkthrough.py
```

Hand-back:
- When the command passes, stop. Do not commit.

## S163 - Add prototype server health smoke for the launcher

Where:
- `flightrecorder/tests/smoke/smoke_dev_prototype_script.py`
- `flightrecorder/docs/SMOKE_COMMANDS.md`

What:
- Extend the launcher smoke to verify `scripts/dev-prototype.sh` contains:
  1. `config.prototype.toml`;
  2. `FLIGHTRECORDER_CONFIG`;
  3. `uvicorn`;
  4. `cd "$ROOT"`;
  5. `exec uvicorn`.
- Add a note in smoke docs that this is a static launcher smoke and does not
  start a long-running server.

Why:
- The launcher is the fastest path to visible progress; regressions here are
  expensive during dogfooding.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
.venv/bin/python tests/smoke/smoke_dev_prototype_script.py
```

Hand-back:
- When the command passes, stop. Do not commit.

## S164 - Update public page for publish-preview visibility

Where:
- `museum/content/projects/flightrecorder/_index.md`
- `museum/content/projects/flightrecorder/2026-05-19-dogfood-loop.md`
- `flightrecorder/tests/smoke/smoke_hugo_build.py`
- `flightrecorder/tests/smoke/smoke_hugo_internal_links.py`

What:
- Update the public Flight Recorder copy to mention the now-visible publish
  preview panel and selected-session summary.
- Keep it factual: fail-closed preview, no real auto-publishing yet.
- Do not change layouts, archetypes, or unrelated museum pages.

Why:
- The public site should keep showing real product movement, not only backend
  internals.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
python tests/smoke/smoke_hugo_build.py
python tests/smoke/smoke_hugo_internal_links.py
```

Hand-back:
- When both commands pass, stop. Do not commit.
