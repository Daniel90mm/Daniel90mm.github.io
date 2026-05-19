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
| S196 | Web search wired as a model-invoked chat tool, verified by senior agent. |

## Active queue

Pick from the top unless Daniel or the senior agent says otherwise.

## Senior instruction for this batch

This queue is now implementation-heavy on purpose. Do not spend the session
writing status docs, planning docs, broad audits, or prose inventories. Your
job is to move working MVP behavior forward and leave focused tests so the
senior agent can verify quickly.

Treat every task as production code:
- Read the listed files fresh before editing.
- Stay inside the listed `Where:` files.
- Prefer small helpers and focused tests over broad rewrites.
- Preserve existing API shapes unless the task explicitly defines a new one.
- Do not commit.
- Do not delete or overwrite user/senior work.
- If the implementation seems to require files outside `Where:`, stop and
  report exactly which file and why.

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
- The feature now has a backend route and model-invoked tool path. It needs a
  cheap FastAPI smoke test that does not depend on Tavily network access.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
.venv/bin/python tests/smoke/smoke_search_api.py
```

Hand-back:
- When the command passes, stop. Do not commit.

## S192 - Add chat web-search tool-loop integration tests

Where:
- `flightrecorder/tests/integration/test_chat_endpoint.py`

What:
- Add integration coverage for the current model-invoked `web_search` loop.
- Extend the existing `StubProvider` locally if needed so it can return a
  different event sequence on each `chat()` call.
- Add a fake search client in this test file only.
- Cover:
  1. provider receives a non-empty `tools` argument when search is configured;
  2. a `ToolCallEvent` triggers a fake search request;
  3. the SSE stream includes a `tool_round` event;
  4. the persisted session contains a `sys` audit message and a final
     assistant message;
  5. a later normal chat turn does not replay persisted `sys` messages back
     to the provider.
- Do not change backend code unless the test exposes a real bug. If it does,
  stop and report the failure instead of widening scope.

Why:
- Web search is now hidden behind the chat model. We need strong tests proving
  the user-visible behavior works without a real network call.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
.venv/bin/python -m pytest tests/integration/test_chat_endpoint.py -q
```

Hand-back:
- When the command passes, stop. Do not commit.

## S193 - Add search result capture helper

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

## S194 - Add search-to-spaghetti backend endpoint

Where:
- `flightrecorder/src/backend/flightrecorder/api.py`
- `flightrecorder/src/backend/flightrecorder/web_search.py`
- `flightrecorder/tests/integration/test_search_to_spaghetti_api.py` (new file)
- `flightrecorder/docs/API_CONTRACT_DRAFT.md`

What:
- Add `POST /api/spaghetti/from-search`.
- Request body should accept `title`, `url`, `snippet`, and optional
  `raw_content`.
- Use the pure helper from S193 and existing spaghetti render/write/index
  helpers.
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

## S195 - Add frontend capture for pasted/sourced search results

Where:
- `flightrecorder/src/frontend/index.html`
- `flightrecorder/src/frontend/styles.css`
- `flightrecorder/src/frontend/app.js`
- `flightrecorder/tests/smoke/smoke_frontend_static.py`

What:
- Add a compact "capture source" form in the Spaghetti detail/read area. It
  should have fields for title, URL, snippet, and optional raw content.
- The form calls `POST /api/spaghetti/from-search`.
- On success, clear the form, refresh the spaghetti grid/list, and show a
  concise success status.
- Render with DOM APIs/textContent, not string-built HTML.
- Do not re-add the old standalone search panel. Web search is invoked by the
  model during chat; this form is only for manually saving a specific source
  the user already has.

Why:
- This gives Daniel a visible way to turn sourced external material into a
  Spaghetti item without waiting for extraction tuning.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
.venv/bin/python tests/smoke/smoke_frontend_static.py
```

Hand-back:
- When the command passes, stop. Do not commit.

## S197 - Inject text attachment context into chat requests

Where:
- `flightrecorder/src/backend/flightrecorder/api.py`
- `flightrecorder/src/backend/flightrecorder/assets.py`
- `flightrecorder/tests/integration/test_chat_endpoint.py`
- `flightrecorder/tests/integration/test_attachment_context_api.py`

What:
- When a session has uploaded text-like assets (`.txt`, `.md`, `.markdown`,
  or MIME `text/*`), include a capped attachment context block in the provider
  message for the current chat call.
- Do not persist the injected context into the session markdown. Persist only
  the user's original message and assistant response.
- Do not attempt image or PDF understanding in this task. Reuse existing
  skip/extract behavior from the attachment context API.
- Keep the total injected text capped. If no cap exists in `assets.py`, add a
  small exported constant and tests around truncation.
- Add integration coverage proving:
  1. text/markdown attachment content reaches the provider;
  2. image/PDF files are not injected;
  3. persisted user message remains exactly what the user typed.

Why:
- This is a high-value MVP step: uploaded notes should actually help chat.
  It also avoids pretending DeepSeek can see images.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
.venv/bin/python -m pytest tests/integration/test_chat_endpoint.py tests/integration/test_attachment_context_api.py -q
```

Hand-back:
- When the command passes, stop. Do not commit.

## S198 - Add extraction quality regression fixtures

Where:
- `flightrecorder/tests/unit/test_idea_capture.py`
- `flightrecorder/prompts/idea-capture.md`

What:
- Add tests that codify the desired extraction behavior Daniel described:
  keep concrete technical ideas like "Apply PCA to disordered
  multi-dimensional data" or "Use ECG to synchronize pulse oximeter
  heartbeat windows"; reject generic filler like "Improve UI", "Remove bugs",
  "Make it better", and "Optimize performance" when there is no concrete
  technical content.
- If existing parser/validation code already rejects generic filler, only add
  tests. If tests fail, make the smallest prompt/validation adjustment needed
  in the listed files.
- Do not change the extraction endpoint or provider plumbing.

Why:
- The Spaghetti wall is only useful if extraction is less eager about generic
  product-management filler.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
.venv/bin/python -m pytest tests/unit/test_idea_capture.py -q
```

Hand-back:
- When the command passes, stop. Do not commit.

## S199 - Move obsolete docs into an archive folder

Where:
- `flightrecorder/docs/`
- `flightrecorder/docs/NAVIGATION.md`
- `flightrecorder/docs/SMOKE_COMMANDS.md`

What:
- This is the only docs-heavy task in this batch, and it is cleanup, not
  writing new prose.
- Create `flightrecorder/docs/archive/`.
- Move obviously obsolete planning/status docs there. Good candidates include
  old build-status snapshots, old missing-work/status audits, and early API
  draft/review docs that no longer describe the current app.
- Do not move active operator docs such as `JUNIOR_TASKS.md`,
  `SMOKE_COMMANDS.md`, `TERMUX_DEPENDENCIES.md`, provider/runtime docs, or
  docs that are referenced by tests unless you update those references.
- Update `NAVIGATION.md` so links do not point at moved files.
- Keep the moved file contents unchanged.

Why:
- The docs folder is too noisy because earlier junior work created many
  standalone status artifacts. This task reduces noise without losing history.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
.venv/bin/python tests/smoke/smoke_frontend_static.py
.venv/bin/python tests/smoke/smoke_docs_navigation_consistency.py
```

Hand-back:
- When both commands pass, stop. Do not commit.

## S200 - Make publish preview fail-closed state useful in the UI

Where:
- `flightrecorder/src/frontend/app.js`
- `flightrecorder/src/frontend/index.html`
- `flightrecorder/src/frontend/styles.css`
- `flightrecorder/tests/smoke/smoke_frontend_static.py`
- `flightrecorder/tests/smoke/smoke_publish_preview_api.py`

What:
- Improve the `## publish preview` panel so `preview session`,
  `preview document`, and `preview spaghetti` all show a clear fail-closed
  result when the backend returns `rejection_reason: curator not configured`.
- The user-facing text should make it obvious that the preview route is
  reachable, but real curator/reviewer publishing is not configured yet.
- Preserve the current fail-closed safety behavior. Do not make anything
  publishable in this task.
- Add/extend smoke assertions that cover all three source kinds and the
  rendered frontend strings/routes.
- If one of the preview buttons currently fails because no source is selected,
  improve only the frontend empty-state message. Do not invent fake sources.

Why:
- Daniel currently sees this as "preview does not work." The MVP needs to
  distinguish "route works but safe publishing is disabled" from broken UI.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
.venv/bin/python tests/smoke/smoke_publish_preview_api.py
.venv/bin/python tests/smoke/smoke_frontend_static.py
```

Hand-back:
- When both commands pass, stop. Do not commit.

## S201 - Make bad generated ideas retractable, not just hidden

Where:
- `flightrecorder/src/backend/flightrecorder/api.py`
- `flightrecorder/src/backend/flightrecorder/documents.py`
- `flightrecorder/tests/unit/test_documents.py`
- `flightrecorder/tests/integration/test_spaghetti_api.py`
- `flightrecorder/tests/smoke/smoke_spaghetti_api.py`
- `flightrecorder/src/frontend/app.js`
- `flightrecorder/src/frontend/index.html`
- `flightrecorder/tests/smoke/smoke_frontend_static.py`

What:
- Change the current one-click Spaghetti action from destructive deletion into
  "discard / retract bad generated idea" semantics.
- For a loose Spaghetti item that has not affected a project document:
  - remove it from the visible wall/list;
  - set `ideas.status = "discarded"` (or `"dismissed"` if that is already
    easier in code) and `updated_at = CURRENT_TIMESTAMP`;
  - keep enough metadata to know it existed, but do not show it in
    `GET /api/spaghetti`.
- For a generated idea that already affected a project document, add a safe
  active-document retraction helper in `documents.py`:
  - remove the exact generated bullet/block from the active project document;
  - do not remove unrelated human-written text;
  - leave the git history / sqlite status as the audit trail;
  - add unit tests for exact-match removal and "do nothing if no exact match".
- If current project-document bullets are not uniquely identifiable enough,
  first add a small source marker format for future generated appends. Keep it
  readable, for example `[source: session-id] [op: N]`.
- Update frontend copy away from "delete selected" toward "discard selected"
  or "retract selected" so the user understands this is a bad-extraction
  cleanup path. Keep it one-click and no confirmation prompt.
- Update tests that currently expect row/file removal.

Why:
- Bad/hallucinated extraction output must not leave bad text stuck in active
  project documents. Preserve auditability through status/git history, but
  make the visible working document correct.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
.venv/bin/python -m pytest tests/integration/test_spaghetti_api.py -q
.venv/bin/python -m pytest tests/unit/test_documents.py -q
.venv/bin/python tests/smoke/smoke_spaghetti_api.py
.venv/bin/python tests/smoke/smoke_frontend_static.py
```

Hand-back:
- When all commands pass, stop. Do not commit.

## S202 - Sync museum project pages into Flightrecorder documents

Where:
- `flightrecorder/src/backend/flightrecorder/documents.py`
- `flightrecorder/src/backend/flightrecorder/project_registry.py`
- `flightrecorder/src/backend/flightrecorder/api.py`
- `flightrecorder/tests/integration/test_documents_api.py` (new file if none exists)
- `flightrecorder/tests/smoke/smoke_documents_api.py`

What:
- Add an idempotent sync path that lets Flightrecorder seed/update its runtime
  `documents/` and `projects.json` from the Hugo museum project pages under
  the configured `hugo_site` path.
- This is sync, not a one-time import. It must be safe to run repeatedly.
- The sync should read `content/projects/*/_index.md` style project pages,
  extract at least `title`, `summary`, `status`, and the body, and maintain:
  - one runtime project document per project;
  - a matching `projects.json` entry with `name`, `ref`, `path`, `active`,
    and `description`.
- Keep it local and deterministic. Do not call Hugo, git, providers, or the
  network.
- Do not overwrite extracted brainstorming sections. Treat museum content as
  the public-project baseline and Flightrecorder appends as the private working
  layer.
- Add a lightweight sync metadata marker (for example in frontmatter or a
  sidecar json) so the API can report when a document was last synced and from
  which museum path.
- Add an API endpoint only if needed for dogfood, for example
  `POST /api/documents/sync-museum`, and protect it with tests.

Why:
- The local `## documents` panel should become the editable/private working
  mirror of the public `/projects/` museum pages, so brainstormed ideas can be
  routed into real project documents.
- Longer term, the museum should be a time-windowed public view into this
  process: generated Spaghetti, absorbed items, discarded items, and polished
  project updates. This task is the local sync foundation, not the public
  publishing policy.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
.venv/bin/python -m pytest tests/integration/test_documents_api.py -q
.venv/bin/python tests/smoke/smoke_documents_api.py
```

Hand-back:
- When both commands pass, stop. Do not commit.

## S203 - Add model catalog API with provider labels and DKK pricing

Where:
- `flightrecorder/src/backend/flightrecorder/api.py`
- `flightrecorder/src/backend/flightrecorder/costs.py`
- `flightrecorder/tests/integration/test_runtime_status_api.py`
- `flightrecorder/tests/smoke/smoke_runtime_status_api.py`

What:
- Add a read-only endpoint, suggested path `GET /api/models`, that returns the
  available configured/priced models for UI selection.
- Include for each model:
  - `provider`;
  - `model`;
  - human-friendly `display_name`;
  - whether it is currently configured/usable for the brainstorm role;
  - input/output/cached price converted to DKK per 1K tokens;
  - a concise comparison label such as `0.001 / 0.002 DKK per 1K`.
- Add a small helper in `costs.py` if needed to convert model pricing to DKK.
- Do not expose API keys or raw secret config.
- For `deepseek/deepseek-chat`, use a display label that can say
  `DeepSeek V4 Pro` when that mapping is known locally. If uncertain, use
  `DeepSeek (deepseek-chat)` rather than a misleading generic label.

Why:
- Provider/model should be picked from known options, not free-text fields,
  and the composer header should show the real selected model in human terms.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
.venv/bin/python -m pytest tests/integration/test_runtime_status_api.py -q
.venv/bin/python tests/smoke/smoke_runtime_status_api.py
```

Hand-back:
- When both commands pass, stop. Do not commit.

## S204 - Replace free-text provider/model fields with model picker UI

Where:
- `flightrecorder/src/frontend/index.html`
- `flightrecorder/src/frontend/styles.css`
- `flightrecorder/src/frontend/app.js`
- `flightrecorder/tests/smoke/smoke_frontend_static.py`

What:
- Replace the advanced free-text `provider` and `model` inputs with a
  dropdown/list populated from `GET /api/models`.
- Keep session `name` as the primary field.
- Show each model option with provider, human display name, configured status,
  and DKK pricing comparison.
- When a model is selected, populate the provider/model values used by
  `POST /api/sessions` without requiring the user to type them.
- Update the composer provider chip so it displays a human-friendly label,
  for example `DeepSeek V4 Pro · deepseek-chat`, not only
  `deepseek/deepseek-chat`.
- Fail gracefully if `/api/models` is unavailable: keep the current runtime
  brainstorm provider/model as the default and show a short status message.

Why:
- The app should feel like a configured tool, not a raw API form. Pricing and
  real model identity should be visible at the point of choice.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
.venv/bin/python tests/smoke/smoke_frontend_static.py
.venv/bin/python tests/smoke/smoke_frontend_dogfood.py
```

Hand-back:
- When both commands pass, stop. Do not commit.

## S205 - Discover local project folders as Flightrecorder projects

Where:
- `flightrecorder/src/backend/flightrecorder/config.py`
- `flightrecorder/src/backend/flightrecorder/project_registry.py`
- `flightrecorder/src/backend/flightrecorder/api.py`
- `flightrecorder/tests/unit/test_config.py`
- `flightrecorder/tests/unit/test_project_registry.py`
- `flightrecorder/tests/integration/test_documents_api.py`

What:
- Add a local project discovery path for Daniel's normal workspace folder,
  `/home/daniel/Documents/Projekter`, without hard-coding it as the only
  possible root.
- Prefer a config value such as `paths.project_roots = [...]`, with a sensible
  fallback that can be tested using temporary directories.
- Discovery should scan immediate child directories and derive safe project
  refs from folder names.
- Do not recurse deeply, do not inspect git remotes, and do not modify those
  project folders.
- Add a read-only API endpoint, suggested path `GET /api/project-roots`, that
  returns discovered folders and whether each folder is already represented in
  runtime `projects.json`.
- Add focused tests with temporary folders. Do not depend on the real
  `/home/daniel/Documents/Projekter` during tests.

Why:
- New projects often begin as folders in `~/Documents/Projekter`. Flightrecorder
  should be able to notice them and let Daniel promote them into project
  documents/museum entries naturally.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
.venv/bin/python -m pytest tests/unit/test_config.py tests/unit/test_project_registry.py tests/integration/test_documents_api.py -q
```

Hand-back:
- When the command passes, stop. Do not commit.

## S206 - Add sync/activity status for museum-facing project updates

Where:
- `flightrecorder/src/backend/flightrecorder/api.py`
- `flightrecorder/tests/integration/test_documents_api.py`
- `flightrecorder/src/frontend/app.js`
- `flightrecorder/src/frontend/index.html`
- `flightrecorder/tests/smoke/smoke_frontend_static.py`

What:
- Add a read-only status surface that answers: since the last museum sync,
  what has changed in Flightrecorder?
- Include at least:
  - number of generated Spaghetti items;
  - number of discarded/retracted Spaghetti items;
  - number of project documents changed;
  - last museum sync timestamp if S202 has created one;
  - a concise per-project changed/not-changed flag.
- Add a small visible frontend panel or line near `## documents` showing this
  status. Keep it compact and factual.
- Do not publish anything to Hugo in this task. This is only status plumbing.

Why:
- The museum should eventually show a daily or "since last sync" window into
  the brainstorming process: what was generated, what was absorbed, and what
  was discarded. The MVP needs status before write-back publishing.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
.venv/bin/python -m pytest tests/integration/test_documents_api.py -q
.venv/bin/python tests/smoke/smoke_frontend_static.py
```

Hand-back:
- When both commands pass, stop. Do not commit.
