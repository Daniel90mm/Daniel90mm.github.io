# Small-model task queue

These tasks are intentionally narrow. Each task should be doable by a smaller
model without broad architecture decisions. Do one task at a time, keep edits
inside the listed files, and run the smoke test before handing back.

Do not change prompts, public Hugo output, API shapes, sqlite schema, or
publisher redaction behavior unless the task explicitly says so.

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

## Active queue

Pick from the top unless Daniel or the senior agent says otherwise.

## S59 - Provider call guard smoke

Where:
- `flightrecorder/tests/smoke/smoke_provider_call_guard.py`

What:
- After the senior agent lands the provider-call guard, add a smoke script that:
  creates an in-memory metadata database, creates a tiny pricing table, records
  one fake provider usage through the guard, and verifies one `api_calls` row.
- Also verify that an existing temp `budget` sentinel makes the guard refuse a
  new paid call.
- Do not touch real `$FLIGHTRECORDER_HOME`, real `pricing.toml`, or provider
  SDKs.

Why:
- Paid provider execution must have one obvious guard path before real LLM
  calls are wired.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
.venv/bin/python tests/smoke/smoke_provider_call_guard.py
```

## S60 - Provider call guard docs

Where:
- `flightrecorder/docs/PROVIDER_CALL_GUARD.md`
- `flightrecorder/docs/NAVIGATION.md`

What:
- After the senior agent lands the provider-call guard, document the intended
  flow:
  preflight budget check -> provider SDK call -> token usage cost computation
  -> `api_calls` insert -> post-call budget enforcement.
- Mention that real provider SDK calls are still not wired.
- Documentation-only.

Why:
- Future provider implementation should not bypass cost logging or the
  hard-stop sentinel.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
grep -q 'preflight budget check' docs/PROVIDER_CALL_GUARD.md
grep -q 'api_calls' docs/PROVIDER_CALL_GUARD.md
grep -q 'docs/PROVIDER_CALL_GUARD.md' docs/NAVIGATION.md
LC_ALL=C grep -n '[^ -~]' docs/PROVIDER_CALL_GUARD.md docs/NAVIGATION.md && exit 1 || true
```

## S61 - Provider guard status sync

Where:
- `flightrecorder/README.md`
- `flightrecorder/docs/BUILD_STATUS.md`
- `flightrecorder/docs/MISSING_WORK.md`
- `flightrecorder/docs/SMOKE_COMMANDS.md`

What:
- After S59 is complete, add `smoke_provider_call_guard.py` to the smoke index.
- Add one short README/status note saying provider-call guard primitives exist,
  but real SDK calls are not wired.
- Documentation-only.

Why:
- The repo status should stay accurate as step 17 moves from raw budget helpers
  toward guarded paid-call execution.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
grep -q 'smoke_provider_call_guard.py' docs/SMOKE_COMMANDS.md
grep -q 'provider-call guard' README.md docs/BUILD_STATUS.md docs/MISSING_WORK.md
LC_ALL=C grep -n '[^ -~]' README.md docs/BUILD_STATUS.md docs/MISSING_WORK.md docs/SMOKE_COMMANDS.md && exit 1 || true
```
