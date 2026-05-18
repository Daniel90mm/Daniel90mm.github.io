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

## Active queue

Pick from the top unless Daniel or the senior agent says otherwise.

## S111 - Project registry loader

Where:
- `flightrecorder/src/backend/flightrecorder/project_registry.py`
- `flightrecorder/tests/unit/test_project_registry.py`
- `flightrecorder/tests/smoke/smoke_project_registry.py`

What:
- Implement a typed project registry loader for runtime `projects.json`.
- Use dataclasses and type hints.
- Accept a JSON array of project objects with `name`, `ref`, `path`, and
  `active`; optional fields may be preserved if already in the fixture.
- Validate refs with the same conservative slug rules used elsewhere.
- Return only active projects from a helper such as `active_projects()`.
- Add unit tests using `tests/fixtures/project_registry/projects.json`.
- Add a smoke script that loads the fixture and prints active refs.
- Do not add API routes and do not touch schema.

Why:
- This is real build-order step 15 groundwork. Idea capture and matchmaker need
  a shared project reference source instead of ad hoc strings.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
.venv/bin/python -m pytest tests/unit/test_project_registry.py -q
.venv/bin/python tests/smoke/smoke_project_registry.py
```

## S112 - Matchmaker rejection fixture files

Where:
- `flightrecorder/tests/fixtures/matchmaker/scenario_01_no_match.json`
- `flightrecorder/tests/fixtures/matchmaker/scenario_02_weak_lexical.json`
- `flightrecorder/tests/fixtures/matchmaker/scenario_03_unrelated_domains.json`
- `flightrecorder/tests/fixtures/matchmaker/scenario_04_genuine_multi.json`
- `flightrecorder/tests/smoke/smoke_matchmaker_rejection_fixtures.py`

What:
- Translate the four scenarios in `docs/MATCHMAKER_REJECTION_FIXTURES.md` into
  static JSON fixture files. One file per scenario.
- Each file is a JSON object with these required keys:
  - `scenario_id` (string, e.g. `"01_no_match"`)
  - `spaghetti` (string, the loose idea text from the doc)
  - `projects` (array of objects with `ref` (slug) and `summary` (string))
  - `expected_match_count` (integer)
  - `expected_match_refs` (array of project refs that should match; empty for
    scenarios 1-3, the two relevant refs for scenario 4)
  - `notes` (string, copy of the "Expected" sentence from the doc)
- Use conservative slug refs for projects: `web-portfolio`, `pulse-oximeter`,
  `bibliography-manager`, `fnirs`. Lowercase, hyphenated, ASCII only.
- Add a smoke script that loads all four fixtures, validates the schema above
  (keys present, types correct, counts consistent with `expected_match_refs`
  length), prints one summary line per scenario, and exits 0.
- Do not invoke any LLM. Do not import the matchmaker prompt. Fixtures are
  static inputs only.
- Do not touch `prompts/matchmaker.md`, the spec, or the doc itself.

Why:
- The doc describes the scenarios in prose. Downstream adversarial tests need a
  machine-readable form. Splitting fixture authorship from test authorship
  keeps the two reviewable independently.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
.venv/bin/python tests/smoke/smoke_matchmaker_rejection_fixtures.py
```

## S113 - Navigation index consistency

Where:
- `flightrecorder/docs/NAVIGATION.md`
- `flightrecorder/tests/smoke/smoke_docs_navigation_consistency.py`

What:
- `docs/NAVIGATION.md` has drifted from the actual `docs/` directory contents:
  - `docs/API_CURRENT_STATE.md` exists on disk but has no row.
  - `docs/CHAT_API_CONTRACT_DRAFT.md` appears on two rows (currently lines 13
    and 20). Keep one row, remove the duplicate.
- Add a row for `docs/API_CURRENT_STATE.md`. Mirror the prose style of nearby
  rows: one short sentence describing the file's purpose. Read the file
  itself to write an accurate one-liner. Do not invent.
- Remove the duplicate `CHAT_API_CONTRACT_DRAFT.md` row. Keep the row whose
  description you judge most accurate against the file; if both are identical,
  keep the first occurrence.
- Add a new smoke script that:
  1. Lists every `*.md` file under `docs/`.
  2. Parses `docs/NAVIGATION.md` and extracts the path from every table row
     under the `| Path | Purpose |` heading.
  3. Fails (non-zero exit) if any `docs/*.md` file is not referenced, or if
     any path appears more than once in the table.
  4. Prints a one-line summary on success.
- Do not touch any other doc, source file, or test. Do not change row order
  beyond the additions/removals required above.

Why:
- `docs/NAVIGATION.md` is the index a fresh agent hits before anything else
  (see hard rule "Keep docs/NAVIGATION.md current" in CLAUDE.md). A drifted
  index sends the next agent to the wrong place. The smoke script makes this
  drift detectable instead of relying on review discipline.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
.venv/bin/python tests/smoke/smoke_docs_navigation_consistency.py
```

## S114 - Smoke command index sync

Where:
- `flightrecorder/docs/SMOKE_COMMANDS.md`

What:
- Three smoke scripts exist under `tests/smoke/` but are absent from the
  `docs/SMOKE_COMMANDS.md` index:
  - `tests/smoke/smoke_project_registry.py`
  - `tests/smoke/smoke_matchmaker_rejection_fixtures.py`
  - `tests/smoke/smoke_docs_navigation_consistency.py`
- For each, add one row to the index table in the existing format.
- Determine the correct Python invocation for each by reading the script's
  top-of-file imports. Rule (already documented at the bottom of the file):
  scripts that import FastAPI or any module that pulls in FastAPI use
  `.venv/bin/python`; pure-stdlib smoke scripts can use system `python`.
- Update the bash "One-liner to run all" case statement at the bottom of the
  file so any newly added script that needs `.venv/bin/python` is in the
  pattern list. Do not remove or reorder existing entries.
- Do not touch any other file. Do not run the smokes themselves; this task is
  index maintenance only.

Why:
- `docs/SMOKE_COMMANDS.md` is the canonical "what can I quickly verify"
  index. The new smoke scripts already exist and pass, but a future agent
  reading only the index will not know they are available. The bash one-liner
  also silently skips them or runs them with the wrong interpreter unless the
  case list is current.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
# Verify every smoke script is referenced by the index.
diff <(ls tests/smoke/smoke_*.py | sort) \
     <(grep -oE 'tests/smoke/smoke_[a-z_]+\.py' docs/SMOKE_COMMANDS.md \
       | sort -u)
# Empty diff = pass.
```

## S116 - Chat endpoint per approved contract (BIG task)

This is a larger task than the previous queue entries. Daniel has explicitly
approved the LLM-call addition, prompt-touch (none required), and API-surface
work for this scope. The contract is fixed; do not negotiate it.

Where:
- `flightrecorder/src/backend/flightrecorder/api.py` (extend; do not rewrite
  existing routes)
- `flightrecorder/src/backend/flightrecorder/runtime.py` (extend
  `RuntimeContext` with `pricing` and a `guard()` factory; do not change the
  existing fields)
- `flightrecorder/src/backend/flightrecorder/config.py` (add an optional
  `pricing_path` config field defaulting to `<repo>/flightrecorder/pricing.toml`)
- `flightrecorder/tests/integration/test_chat_endpoint.py` (new)

What:
- Implement `POST /api/sessions/{session_id}/messages` exactly as specified in
  `docs/CHAT_API_CONTRACT_DRAFT.md`. The contract is authoritative; do not
  invent extra fields, headers, or event types.
- Use the new typed event interface from
  `flightrecorder.providers`: `Provider.chat()` yields `TokenEvent`
  instances and ends with exactly one `UsageEvent`. Do not parse the anthropic
  SDK directly - go through the Provider abstraction.
- Wire `flightrecorder.costs.ProviderCallGuard`:
  1. Call `guard.check_before_call(now)` before opening the stream. If it
     raises `BudgetHardStopError`, return HTTP 503 with the contract's body
     `{"detail": "Budget hard-stop active"}`. Do not start streaming.
  2. After the stream completes successfully, call
     `guard.record_usage(ProviderUsage(...))` with the counts from the final
     `UsageEvent` and the session_id. `record_usage` already logs the
     `api_calls` row and re-enforces the monthly budget. Do not double-log.
- Persistence rules from the contract:
  - Append the user message to the session file via
    `SessionStore.add_message` **before** opening the provider stream.
  - On clean `done`, append the full assistant message via the same helper.
  - On error mid-stream (provider exception), emit
    `event: error\ndata: {"detail": "<message>"}\n\n` and close the stream.
    Do not persist the assistant message. The user message stays persisted.
  - Send the `done` event with `{"input_tokens": ..., "output_tokens": ...,
    "message_count": <updated>}` after appending the assistant message.
- 404 if the session does not exist; 400 if body content is empty or missing;
  let FastAPI return 422 for malformed bodies.
- Use `fastapi.responses.StreamingResponse` with
  `media_type="text/event-stream"`. Each event must be two CRLF/newline
  blocks: `event: <name>\ndata: <json>\n\n`.

Runtime/config plumbing (keep narrow):
- Add `pricing_path: Path | None` to the paths section of `AppConfig`.
  Default to `runtime_home.parent / "pricing.toml"` if unset. Use existing
  `flightrecorder.costs.load_pricing`.
- Add `pricing: PricingTable` and `brainstorm_provider: Provider` to
  `RuntimeContext`. Build the provider with
  `create_role_provider(config, "brainstorm")`.
- Add a `RuntimeContext.guard()` method that returns a fresh
  `ProviderCallGuard` constructed from runtime_home, the metadata db
  connection, `runtime.pricing`, and `config.budget.warn_at_dkk` /
  `hard_stop_dkk`. Building per-request is fine; the guard is cheap.

Do NOT:
- Touch `prompts/` (the brainstorm system prompt is not part of this task).
- Change the public response shape from the contract draft.
- Implement images, voice_ref, or continue/resume. Those are deferred to v2
  per the contract.
- Touch `providers.py` or the `TokenEvent` / `UsageEvent` types. They are
  built and tested.
- Add retry logic, fallback providers, or graceful degradation. Fail closed.

Tests (`tests/integration/test_chat_endpoint.py`):
- Use FastAPI `TestClient`. Spin up the app against a `tmp_path` runtime_home.
- Inject a **stub Provider** that ignores its arguments and yields a fixed
  list of `TokenEvent` followed by one `UsageEvent`. Replace
  `runtime.brainstorm_provider` directly on `app.state.runtime` from the test.
- Cover:
  1. Happy path: SSE stream contains the expected `token` events in order
     and a final `done` event with correct token counts and message_count.
     Verify the session file now contains both the user and assistant
     messages. Verify one `api_calls` row exists with the matching token
     counts.
  2. Empty content: 400 with the contract's detail string.
  3. Unknown session_id: 404 with the contract's detail string.
  4. Provider raises mid-stream: response stream ends with an `event: error`
     and no assistant message is persisted (but the user message is).
  5. Budget hard-stop active before the call: 503 with the contract's detail
     string. No token events are sent and no row is logged.

Why:
- Spec section 11 names this endpoint and the build order has it as step 3.
- This is the path through which Daniel actually talks to flightrecorder;
  every other novel piece (idea capture, matchmaker, publisher) depends on
  sessions accumulating messages this way.
- The contract was drafted, reviewed, and approved before code was started -
  follow it.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
.venv/bin/python -m pytest tests/integration/test_chat_endpoint.py -q
.venv/bin/python -m pytest tests/unit/test_providers.py tests/unit/test_api.py tests/unit/test_costs.py -q
# Both must pass. The second command catches regressions in adjacent modules.
```

Hand-back:
- When the tests pass, stop. Do not commit. Daniel verifies the diff and the
  test run before commit.

## S117 - Idea-capture LLM wiring (BIG task)

Daniel has explicitly approved LLM calls and prompt-touch for this scope. The
prompt at `prompts/idea-capture.md` is fixed - do not edit it.

Where:
- `flightrecorder/src/backend/flightrecorder/idea_capture.py` (extend; do not
  refactor the existing `parse_idea_operations` / `apply_idea_operations`)
- `flightrecorder/src/backend/flightrecorder/api.py` (add a new route only)
- `flightrecorder/src/backend/flightrecorder/runtime.py` (add an
  `idea_capture_provider` field, parallel to `brainstorm_provider`)
- `flightrecorder/tests/integration/test_extraction_endpoint.py` (new)

What:
- Add a function in `idea_capture.py`:
  ```python
  async def run_idea_capture(
      provider: Provider,
      prompt_text: str,
      transcript: str,
  ) -> tuple[str, UsageEvent]:
      """Call the idea-capture provider and return raw JSON output + usage."""
  ```
  Behaviour: build `[Message(role="user", content=transcript)]`, call
  `provider.chat(messages, system=prompt_text)`, accumulate every `TokenEvent`
  into a single string, capture the final `UsageEvent`. Raise
  `IdeaCaptureError` if the stream finishes without a UsageEvent.
- Add a helper that renders a session's stored messages into the transcript
  string the prompt expects. Format: one block per message,
  `## <role>\n<content>\n` joined by blank lines. Use existing
  `SessionStore.get_session()` to load messages.
- Load the idea-capture prompt text from `prompts/idea-capture.md` once at
  module import time (cache it). Do not inline the prompt text in code.
- Add `POST /api/sessions/{session_id}/extract` route. Flow:
  1. Load session via `runtime.sessions.get_session(session_id)`. 404 if
     missing.
  2. `runtime.guard().check_before_call(datetime.now(timezone.utc))`. 503 if
     `BudgetHardStopError` per S116's pattern.
  3. `raw, usage = await run_idea_capture(runtime.idea_capture_provider,
     IDEA_CAPTURE_PROMPT, transcript)`. On `IdeaCaptureError` from
     `run_idea_capture` (no UsageEvent) return 502
     `{"detail": "idea-capture provider returned no usage"}`.
  4. `operations = parse_idea_operations(raw)`. On `IdeaCaptureError` from
     malformed output return 422 with `{"detail": str(exc)}`. **Do not apply
     partial operations.** Do not retry. Fail closed.
  5. `applied = apply_idea_operations(runtime_home=..., connection=...,
     source_session=session_id, operations=operations,
     captured_at=datetime.now(timezone.utc), commit_documents=True)`.
  6. `runtime.guard().record_usage(ProviderUsage(...))` with the role
     `"idea_capture"` and the session_id. Always log usage if the provider
     call succeeded, even if parsing later fails. (Specifically: log usage
     between steps 3 and 4, not after 5.)
  7. Return JSON:
     ```json
     {
       "session_id": "...",
       "project_appends": <int>,
       "spaghetti": <int>,
       "documents_committed": <bool>
     }
     ```
- Runtime: construct `idea_capture_provider` via
  `create_role_provider(config, "idea_capture")`. Use the same safe-fallback
  helper pattern S116 used for `brainstorm_provider` (an unconfigured shell
  provider when the role is missing) so tests that don't configure the role
  still build runtime cleanly.

Do NOT:
- Edit `prompts/idea-capture.md`. Read it as text; that's all.
- Retry on malformed output. Spec section "Idea-capture LLM" says fail
  closed. See `docs/IDEA_CAPTURE_RETRY_POLICY.md`.
- Apply operations partially. Either all parse + all apply, or none.
- Change the existing parse/apply function signatures.
- Use the brainstorm provider for extraction. Idea-capture has its own role
  and uses a cheap model.

Tests (`tests/integration/test_extraction_endpoint.py`):
- Reuse the `StubProvider` pattern from S116's chat endpoint test (copy or
  factor a helper). Each test injects a stub onto
  `runtime.idea_capture_provider`.
- Cover:
  1. Happy path: stub yields JSON for one project_append and one spaghetti,
     plus a UsageEvent. Endpoint returns 200 with counts {project_appends: 1,
     spaghetti: 1, documents_committed: true}. Verify the project document
     gained the bullet, the spaghetti file exists, the sqlite `ideas` table
     has one row, and `api_calls` has exactly one row tagged
     `role="idea_capture"`.
  2. Malformed output: stub yields `"not json"` plus a UsageEvent. Endpoint
     returns 422 with detail mentioning JSON. Verify the api_calls row was
     still logged (usage logging happens before parsing). Verify no idea
     rows, no spaghetti files, no document edits.
  3. No usage: stub yields tokens but no UsageEvent. Endpoint returns 502
     with the expected detail. Verify no api_calls row, no document edits.
  4. Budget hard-stop active: 503 with `{"detail": "Budget hard-stop active"}`.
     No provider call, no api_calls row.
  5. Unknown session: 404 with `{"detail": "Session not found"}`.

Why:
- Spec section 8 (Project documents + idea capture) and build order step 8
  list this. Capture mechanics are in place; the LLM call is the last
  missing piece for end-to-end. Without this, every session that ends just
  sits there - nothing gets routed to project documents or the spaghetti
  wall.
- Idea-capture is a doxxing-adjacent path because spaghetti ideas may
  surface for publishing later. Failing closed on malformed output is what
  prevents corrupted JSON from getting partially applied and propagating.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
.venv/bin/python -m pytest tests/integration/test_extraction_endpoint.py -q
.venv/bin/python -m pytest tests/unit/test_idea_capture.py \
    tests/integration/test_idea_capture_pipeline.py \
    tests/integration/test_chat_endpoint.py \
    tests/unit/test_providers.py -q
# Both must pass.
```

Hand-back:
- When the tests pass, stop. Do not commit. Daniel verifies before commit.

## S118 - Adversarial robustness tests for the idea-capture parser

Where:
- `flightrecorder/tests/adversarial/test_idea_capture_robustness.py` (new
  file; do not edit any source module).

What:
- Write a test module that hammers `parse_idea_operations` from
  `flightrecorder.idea_capture` with adversarial-shaped inputs and asserts
  it fails closed by raising `IdeaCaptureError`. The parser must never
  return partial garbage; either the whole JSON parses and validates, or
  it raises.
- Cover at minimum:
  1. Empty string and whitespace-only string.
  2. JSON that is a number, a string, `null`, a bool, or an object (only
     an array is accepted).
  3. An array containing a non-object element (e.g. `[1]`, `["x"]`,
     `[null]`).
  4. `project_append` missing each required field
     (`project_ref`, `section`, `content`) one at a time.
  5. `project_append` with `section` set to a string that isn't in
     `PROJECT_SECTIONS` (e.g. `"Roadmap"`, `"todos"` lowercase, `""`).
  6. `project_append` with `project_ref` that sanitizes to empty
     (e.g. `"   "`, `"..."`, `"!!!"`).
  7. `spaghetti` with `tags` not a list (string, int, dict).
  8. `spaghetti` with `tags` containing a non-string entry (`["pca", 1]`,
     `["pca", null]`).
  9. `spaghetti` with empty `content` after `.strip()`.
  10. An array of `MAX_IDEA_OPERATIONS + 1` valid operations (too many).
  11. Operation with unknown `type` (e.g. `"draft"`, `"comment"`, missing
      `type` field entirely).
  12. Deeply nested junk (`[[[[]]]]`, `[{"type": ["project_append"]}]`).
- For each case, use `pytest.raises(IdeaCaptureError)`. Group the cases
  with `pytest.mark.parametrize` where the input shape varies but the
  assertion is identical, otherwise write one focused test per category.
- Do NOT test the happy path here. `tests/integration/` and
  `tests/unit/test_idea_capture.py` already cover that.
- Do NOT touch any source module. The whole task is one new test file.

Why:
- Idea-capture is doxxing-adjacent because spaghetti ideas may surface for
  publishing later. The parser is the boundary between LLM output and the
  filesystem / sqlite. A property-style sweep against malformed inputs
  catches regressions that the existing happy-path tests miss.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
.venv/bin/python -m pytest tests/adversarial/test_idea_capture_robustness.py -q
.venv/bin/python -m pytest tests/unit/test_idea_capture.py \
    tests/integration/test_idea_capture_pipeline.py -q
# Both must pass. The second command catches false positives where the
# new tests are accidentally too strict and reject happy-path inputs.
```

Hand-back:
- When the tests pass, stop. Do not commit. Daniel verifies before commit.

## S115 - Build status: project registry now in progress

Where:
- `flightrecorder/docs/BUILD_STATUS.md`
- `flightrecorder/docs/MISSING_WORK.md`

What:
- Build-order step 15 (Project registry) now has a typed loader, unit tests,
  and a fixture smoke (delivered by S111). It is no longer "not started".
- In `docs/BUILD_STATUS.md`, change the step 15 row from `not started` to
  `in progress`. In the Notes column add a one-sentence summary citing the
  loader, unit tests, and smoke script; mention what is still missing
  (matchmaker/idea-capture wiring still reads project refs ad hoc; no API
  route exposes the registry yet). Keep wording terse and factual.
- In `docs/MISSING_WORK.md`:
  - Update the count line at the top: "In progress" goes from 3 to 4 and
    "Not started" goes from 15 to 14. List step 15 with the other
    in-progress steps.
  - Remove step 15 from the "Not started" table.
  - Add a paragraph under "## Open" describing what step 15 still lacks (one
    or two sentences, same content as the BUILD_STATUS note above).
- Do not edit any source code, tests, or other docs. Do not change rows for
  other steps.

Why:
- The build-status pair is the snapshot a fresh agent reads to decide what to
  pick up. Leaving step 15 as "not started" misleads the next agent into
  re-implementing the registry.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
grep -E '^\| 15 \| Project registry \| in progress' docs/BUILD_STATUS.md
grep -E 'In progress: \*\*4\*\*' docs/MISSING_WORK.md
grep -E 'Not started: \*\*14\*\*' docs/MISSING_WORK.md
# All three greps must match exactly once.
```
