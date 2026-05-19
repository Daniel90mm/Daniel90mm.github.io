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
| S159 | Frontend uploaded asset list. |
| S160 | Session asset metadata integration test. |
| S161 | Publish preview frontend dogfood assertions, extended by senior agent for matchmaker panel references. |
| S162 | Prototype publish-preview walkthrough update. |
| S163 | Prototype launcher static smoke hardening. |
| S164 | Public page update for publish-preview visibility. |
| S165 | Frontend matchmaker panel for selected spaghetti idea, completed by senior agent. |

## Active queue

Pick from the top unless Daniel or the senior agent says otherwise.

## S166 - Draft session asset serving API contract

Where:
- `flightrecorder/docs/API_CONTRACT_DRAFT.md`
- `flightrecorder/docs/API_CURRENT_STATE.md`
- `flightrecorder/docs/NAVIGATION.md`

What:
- Draft the contract for a read-only session asset serving endpoint:
  `GET /api/sessions/{session_id}/assets/{filename}`.
- State that it serves only files already listed in the selected session's
  `assets` array.
- State path-guard rules clearly:
  1. asset must live under `<runtime_home>/sessions/_assets`;
  2. asset filename must belong to the requested session prefix;
  3. traversal such as `../` must return 404.
- Mark the route as draft-only in `API_CURRENT_STATE.md`.
- Add the API contract doc location to navigation if needed.

Why:
- Uploaded images are listed in the browser, but the user still cannot inspect
  them. The next MVP step is serving those assets safely.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
rg -n "GET /api/sessions/\\{session_id\\}/assets/\\{filename\\}" docs/API_CONTRACT_DRAFT.md
PYTHONPATH=src/backend python tests/smoke/smoke_api_current_state.py
```

Hand-back:
- When both commands pass, stop. Do not commit.

## S167 - Implement safe session asset serving

Where:
- `flightrecorder/src/backend/flightrecorder/api.py`
- `flightrecorder/tests/integration/test_session_asset_serving_api.py` (new file)
- `flightrecorder/tests/smoke/smoke_session_asset_serving_api.py` (new file)
- `flightrecorder/docs/API_CURRENT_STATE.md`
- `flightrecorder/docs/SMOKE_COMMANDS.md`

What:
- Implement `GET /api/sessions/{session_id}/assets/{filename}`.
- Return the uploaded asset bytes with an appropriate media type.
- Return 404 when:
  1. the session does not exist;
  2. the file does not exist;
  3. the filename does not start with `{session_id}-`;
  4. path traversal is attempted.
- Add integration and smoke coverage.

Why:
- The dogfood UI needs to inspect uploaded images without exposing arbitrary
  runtime files.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
.venv/bin/python -m pytest tests/integration/test_session_asset_serving_api.py -q
.venv/bin/python tests/smoke/smoke_session_asset_serving_api.py
PYTHONPATH=src/backend python tests/smoke/smoke_api_current_state.py
```

Hand-back:
- When all commands pass, stop. Do not commit.

## S168 - Link uploaded assets from the frontend

Where:
- `flightrecorder/src/frontend/index.html`
- `flightrecorder/src/frontend/styles.css`
- `flightrecorder/src/frontend/app.js`
- `flightrecorder/tests/smoke/smoke_frontend_static.py`
- `flightrecorder/tests/smoke/smoke_frontend_dogfood.py`
- `flightrecorder/docs/FRONTEND_SCOPE.md`

What:
- Turn each uploaded asset row into a same-tab link to
  `/api/sessions/{session_id}/assets/{filename}`.
- Use DOM node creation and `textContent`; do not build links with raw
  `innerHTML`.
- Keep the filename visible and size readable.
- If there are no assets, show a quiet empty state.
- Update frontend docs and smokes.

Why:
- Uploaded images should be inspectable from the prototype browser surface.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
PYTHONPATH=src/backend python tests/smoke/smoke_frontend_static.py
.venv/bin/python tests/smoke/smoke_frontend_dogfood.py
```

Hand-back:
- When both commands pass, stop. Do not commit.

## S169 - Add matchmaker panel walkthrough notes

Where:
- `flightrecorder/docs/PROTOTYPE_WALKTHROUGH.md`
- `flightrecorder/tests/smoke/smoke_prototype_walkthrough.py`
- `flightrecorder/docs/FRONTEND_SCOPE.md`

What:
- Document the new **Matchmaker** panel in the prototype walkthrough.
- Make clear that it runs only for the selected spaghetti idea.
- Make clear that the current scorer is fail-closed, so zero candidates is
  expected until a real scorer is wired.
- Update the walkthrough smoke to check for `Matchmaker`, `selected spaghetti
  idea`, and `fail-closed scorer`.

Why:
- The prototype now exposes another workflow surface; the walkthrough should
  match what the browser actually shows.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
.venv/bin/python tests/smoke/smoke_prototype_walkthrough.py
```

Hand-back:
- When the command passes, stop. Do not commit.

## S170 - Add browser screenshot assertions for new panels

Where:
- `flightrecorder/tests/smoke/smoke_prototype_ui_screenshot.py`
- `flightrecorder/docs/SMOKE_COMMANDS.md`

What:
- Extend the screenshot smoke to fetch the served HTML/JS and assert the new
  panel ids are present before taking the screenshot:
  1. `asset-list`;
  2. `publish-preview-panel`;
  3. `matchmaker-panel`.
- Keep Chrome optional; still skip cleanly when `google-chrome` is absent.
- Do not add Playwright.

Why:
- The screenshot smoke should catch missing visible panels before a human has
  to open the prototype.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
.venv/bin/python tests/smoke/smoke_prototype_ui_screenshot.py
```

Hand-back:
- When the command passes, stop. Do not commit.

## S171 - Update public page for asset inspection and matchmaker

Where:
- `museum/content/projects/flightrecorder/_index.md`
- `museum/content/projects/flightrecorder/2026-05-19-dogfood-loop.md`
- `flightrecorder/tests/smoke/smoke_hugo_build.py`
- `flightrecorder/tests/smoke/smoke_hugo_internal_links.py`

What:
- Update public copy to mention:
  1. uploaded asset inspection from the browser;
  2. the matchmaker panel for selected spaghetti ideas;
  3. both matchmaker and publisher remain fail-closed until their real LLM
     stages are wired.
- Keep it factual; do not turn it into marketing copy.
- Do not change layouts, archetypes, or unrelated museum pages.

Why:
- The public page should reflect visible MVP surfaces, not just backend work.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
python tests/smoke/smoke_hugo_build.py
python tests/smoke/smoke_hugo_internal_links.py
```

Hand-back:
- When both commands pass, stop. Do not commit.
