# Junior implementation task queue

These tasks are intentionally narrow but should still advance the application.
Use the junior agent for real implementation work: tests, backend endpoints,
frontend behavior, fixtures that protect behavior, and small refactors with a
clear payoff. Do one task at a time, keep edits inside the listed files, and
run the smoke test before handing back.

Do not change prompts, public Hugo output, API shapes, sqlite schema, or
publisher redaction behavior unless the task explicitly says so.

Docs are allowed only when they directly support implementation: API contracts
for code being built next, runtime safety notes for secrets/data, smoke command
updates for a new test, or user-facing walkthrough updates for working features.
Do not write status docs, audits, inventories, or planning docs as standalone
work unless the senior agent explicitly asks for that exact artifact.

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
9. **Implementation first.** A task that only writes docs is suspect. If the
   task says to write docs, keep it short and tied to code/tests. Do not pad
   with process notes.
10. **Pave the road for senior review.** Prefer adding focused tests,
    fixtures, and small callable helpers over broad prose. The senior agent
    will verify, clean up, and integrate after you hand back.

## Suggested invocation prompt

> You are a junior agent on the flightrecorder project. Open
> `flightrecorder/docs/JUNIOR_TASKS.md` and read the "Operating rules for the
> junior agent" section in full before starting. You are here to do useful
> implementation work, not docs for docs' sake. Pick the single top task in
> the Active queue, do exactly what its "Where:" / "What:" sections say, run
> the listed smoke / pytest commands, and stop when they pass. Do not commit,
> do not push, do not edit files outside the "Where:" list. If a file you need
> to edit has changed since you read it, stop and report.

## Completed ledger

The following junior tasks are done and should not be repeated unless a
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
| S172 | Uploaded file removal from API and frontend, completed by senior agent. |
| S173 | Asset serving contract after delete landed. |
| S174 | Safe session asset serving endpoint, session-existence guard added by senior agent. |
| S175 | Frontend links for uploaded assets while preserving remove. |
| S176 | Text and Markdown asset extraction helper. |
| S177 | Attachment context preview API. |
| S178 | Honest attachment limitations documentation. |
| S179 | Superseded by the rail-first UI overhaul; do not repeat old attachment panel task. |
| S180 | Superseded by existing integration coverage for attachment context API. |
| S181 | Superseded by web-search work; attachment-to-chat contract is deferred. |
| S182 | Superseded by web-search work; attachment injection is deferred. |
| S183 | Superseded by web-search work; attachment send toggle is deferred. |
| S184 | Superseded by current prototype walkthrough/UI direction. |
| S185 | Web-search provider contract. |
| S186 | Pure web-search normalization helpers. |
| S187 | Read-only search API with injectable fake client. |
| S188 | Local Tavily config template. |
| S189 | Frontend search panel without chat integration. |
| S190 | Search-to-spaghetti capture flow contract. |

## Active queue

Pick from the top unless Daniel or the senior agent says otherwise.

## S191 - Add search API smoke script

Where:
- `flightrecorder/tests/smoke/smoke_search_api.py` (new file)
- `flightrecorder/docs/SMOKE_COMMANDS.md`

What:
- Add a smoke script for `GET /api/search` using an injected fake search
  client. Do not call the real Tavily network.
- Assert:
  1. configured fake client returns normalized results;
  2. missing search client returns 503;
  3. `include_raw_content=true` is passed through.
- Add the smoke command to `docs/SMOKE_COMMANDS.md`.

Why:
- The feature now has a backend route and frontend panel. It needs a cheap
  smoke test that protects the full FastAPI route shape.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
.venv/bin/python tests/smoke/smoke_search_api.py
```

Hand-back:
- When the command passes, stop. Do not commit.

## S192 - Add search result capture helper

Where:
- `flightrecorder/src/backend/flightrecorder/web_search.py`
- `flightrecorder/tests/unit/test_web_search.py`

What:
- Add a pure helper that converts a `SearchResult` into a safe spaghetti-note
  body string.
- Include the title, URL attribution, snippet, and a capped raw-content excerpt
  when present.
- Do not write files, touch sqlite, or add an API route in this task.
- Unit-test escaping/formatting boundaries and raw-content truncation.

Why:
- Search should feed the spaghetti wall, but the formatting contract should be
  pure and testable before storage/API work.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
.venv/bin/python -m pytest tests/unit/test_web_search.py -q
```

Hand-back:
- When the command passes, stop. Do not commit.

## S193 - Add search-to-spaghetti backend endpoint

Where:
- `flightrecorder/src/backend/flightrecorder/api.py`
- `flightrecorder/src/backend/flightrecorder/web_search.py`
- `flightrecorder/tests/integration/test_search_to_spaghetti_api.py` (new file)
- `flightrecorder/docs/API_CONTRACT_DRAFT.md`

What:
- Add `POST /api/spaghetti/from-search`.
- Request body should accept `title`, `url`, `snippet`, and optional
  `raw_content`.
- Use the pure helper from S192 and existing spaghetti write/index helpers.
- Do not call a provider and do not perform a web request.
- Add integration coverage proving a spaghetti idea file and sqlite row are
  created with source attribution.

Why:
- The product value is not search alone; it is capturing sourced external
  context into the existing idea pipeline.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
.venv/bin/python -m pytest tests/integration/test_search_to_spaghetti_api.py -q
```

Hand-back:
- When the command passes, stop. Do not commit.

## S194 - Add frontend capture button for search results

Where:
- `flightrecorder/src/frontend/index.html`
- `flightrecorder/src/frontend/styles.css`
- `flightrecorder/src/frontend/app.js`
- `flightrecorder/tests/smoke/smoke_frontend_static.py`

What:
- Add a `capture` button beside each rendered search result.
- The button calls `POST /api/spaghetti/from-search` with that result.
- On success, refresh the spaghetti grid and show a concise success status.
- Render with DOM APIs/textContent, not string-built HTML.

Why:
- This makes web search visibly useful inside Flightrecorder instead of being
  a disconnected lookup panel.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
PYTHONPATH=src/backend python tests/smoke/smoke_frontend_static.py
```

Hand-back:
- When the command passes, stop. Do not commit.

## S195 - Add docs archive proposal as a data file

Where:
- `flightrecorder/docs/DOCS_CLEANUP_PLAN.md` (new file)
- `flightrecorder/docs/NAVIGATION.md`

What:
- Create a short, actionable cleanup plan with three tables:
  1. keep active;
  2. archive after review;
  3. merge into another doc.
- Do not move files in this task.
- Keep it under 120 lines.
- Add it to navigation.

Why:
- Docs cleanup needs one explicit review artifact before file moves. This is
  not general doc writing; it is a bounded cleanup map.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
rg -n "archive after review|merge into another doc|keep active" docs/DOCS_CLEANUP_PLAN.md
PYTHONPATH=src/backend python tests/smoke/smoke_docs_navigation_consistency.py
```

Hand-back:
- When both commands pass, stop. Do not commit.
