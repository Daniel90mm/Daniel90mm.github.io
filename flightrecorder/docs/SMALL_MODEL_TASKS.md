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
| S122 | Matchmaker API contract doc and NAVIGATION row. |

## Active queue

Pick from the top unless Daniel or the senior agent says otherwise.

## S119 - Session round-trip integration test

Where:
- `flightrecorder/tests/integration/test_session_round_trip.py` (new file;
  do not edit any source module).

What:
- Write one integration test that exercises the wired pipeline end-to-end
  on a fresh session:
  1. `POST /api/sessions` to create a session.
  2. `POST /api/sessions/{id}/messages` with a user message that names a
     known project (e.g. "Let's work on the pulse-oximeter AC/DC ratio").
     Stub the brainstorm provider with a fixed assistant reply so the
     stream completes deterministically.
  3. `POST /api/sessions/{id}/extract` with a stub idea-capture provider
     whose canned JSON returns one `project_append` to `pulse-oximeter`
     and one `spaghetti`.
  4. `GET /api/sessions/{id}` and assert the response now lists both the
     user and assistant messages and the message_count is 2.
- Assert in the same test:
  - The project document file `pulse-oximeter.md` exists and contains the
    appended bullet from step 3.
  - The spaghetti directory has exactly one new markdown file.
  - The sqlite `ideas` table has exactly one row, source_session matches.
  - The sqlite `api_calls` table has exactly two rows (one brainstorm,
    one idea_capture) with matching session_id.
  - The session's sqlite row has `extracted=1` and a populated
    `extracted_at`.
- Reuse the stub-provider pattern from
  `tests/integration/test_chat_endpoint.py` and
  `tests/integration/test_extraction_endpoint.py`. Copy whatever stub
  class shape you need into the new test file; do not factor a shared
  helper this round.
- Do NOT touch any source module. The whole task is one new test file.

Why:
- Each of the unit / integration tests today covers one endpoint in
  isolation. The pipeline that produces public output (chat -> message
  -> idea capture -> project document + spaghetti + cost log) has no
  single test exercising the whole chain. Without it, a refactor of any
  one stage can silently break the contract between stages.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
.venv/bin/python -m pytest tests/integration/test_session_round_trip.py -q
.venv/bin/python -m pytest tests/integration/ tests/unit/test_api.py -q
# Both must pass. The second command catches regressions in the
# integration suite that the round-trip test might mask.
```

Hand-back:
- When the tests pass, stop. Do not commit. Daniel verifies before commit.

## S121 - Adversarial fixture directory resolver smoke

Where:
- `flightrecorder/tests/smoke/smoke_publisher_fixture_dir.py` (new
  file; do not edit any source module).

What:
- Write an executable smoke script that verifies
  `flightrecorder.publisher.adversarial_fixture_dir()` returns a path
  that exists, is a directory, and contains the expected fixture files.
- The script must:
  1. Import `adversarial_fixture_dir` from `flightrecorder.publisher`.
  2. Call it, assert the return is a `pathlib.Path`, assert it exists,
     assert it is a directory.
  3. Define a constant `EXPECTED = {"names", "emails", "repo_urls",
     "course_codes", "mixed", "sensitive"}` matching the categories
     documented in `docs/PUBLISHER_ADVERSARIAL_FIXTURES.md`.
  4. Walk `*.txt` files under the directory, collect their stems into a
     set, assert `EXPECTED.issubset(found)`. Extra files are allowed;
     missing ones are not.
  5. For each found `.txt` file, assert it is non-empty (more than 0
     bytes after strip).
  6. Print one summary line per assertion (or one summary line total)
     and `publisher fixture dir smoke test passed` on success.
  7. Exit 0 on success, non-zero with a clear stderr message on
     failure.
- The script should run via system `python` (no FastAPI imports
  needed). Use `PYTHONPATH=src/backend` when running.
- Do NOT touch any source module. Do NOT modify the fixtures
  themselves. The whole task is one new smoke file.

Why:
- `adversarial_fixture_dir()` is the helper the publisher pipeline
  (and its tests) use to locate the doxxing fixtures. If the path
  resolution ever drifts (refactor, file move) the publisher's
  fail-closed sweep silently loses its inputs. A smoke that re-asserts
  the helper's contract catches that immediately.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
PYTHONPATH=src/backend python tests/smoke/smoke_publisher_fixture_dir.py
echo "exit=$?"
# Expect exit=0 and the success line in the output.
```

Hand-back:
- When the smoke exits 0, stop. Do not commit. Daniel verifies before
  commit.

## S120 - Publisher pipeline smoke script

Where:
- `flightrecorder/tests/smoke/smoke_publisher.py` (new file; do not edit
  any source module).

What:
- Write an executable smoke script under `tests/smoke/` that exercises
  the publisher framework's fail-closed default through the public API.
  The script should:
  1. Import `run_publish_pipeline`, `NullCurator`, `NullReviewer`,
     `adversarial_fixture_dir`, and `PipelineResult` from
     `flightrecorder.publisher`.
  2. Walk every `*.txt` file under `adversarial_fixture_dir()`. For each
     fixture: call `run_publish_pipeline(source_kind="adversarial",
     source_id=path.stem, source_body=path.read_text())` with the Null*
     defaults (no explicit curator/reviewer arguments).
  3. Print one line per fixture in the format
     `<fixture_stem>: approved=<count> reason=<rejection_reason>`.
  4. After the walk, print summary lines:
     `total_fixtures: <n>`, `total_approved: <sum of approved counts>`,
     `all_rejected: <True/False>`.
  5. Exit 0 only if `total_approved == 0` and every fixture has a
     non-None `rejection_reason`. Exit 1 otherwise with a clear stderr
     message naming the fixture that leaked.
- The script must run via system `python` (no FastAPI imports needed).
  Use `PYTHONPATH=src/backend` when running, the standard pattern in
  the existing smoke scripts.
- Do NOT touch any source module. Do NOT modify the fixtures. The whole
  task is one new smoke file.

Why:
- The unit test `tests/unit/test_publisher.py` already covers
  fail-closed defaults inside pytest. The smoke version is for the
  human-facing safety check: a single command that proves no
  adversarial fixture can reach `approved` under the framework's
  defaults. If a future refactor accidentally loosens the default
  (changes `NullCurator` to return `publishable=True`, for example),
  this smoke flags it instantly.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
PYTHONPATH=src/backend python tests/smoke/smoke_publisher.py
echo "exit=$?"
# Expect exit=0 and total_approved: 0 in the output.
```

Hand-back:
- When the smoke passes (exit 0), stop. Do not commit. Daniel verifies
  before commit.

