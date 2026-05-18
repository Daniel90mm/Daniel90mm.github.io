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
| S59 | Provider call guard smoke. |
| S60 | Provider call guard docs. |
| S61 | Provider guard status sync. |

## Active queue

Pick from the top unless Daniel or the senior agent says otherwise.

## S62 - Provider guard hard-stop breach smoke

Where:
- `flightrecorder/tests/smoke/smoke_provider_call_guard.py`

What:
- Extend the smoke script to also record one deliberately expensive fake usage
  that crosses `hard_stop_eur`.
- Verify the temp `budget` sentinel is written after that call.
- Verify the expensive call is still present in `api_calls`.
- Keep this smoke fully fake: no real `$FLIGHTRECORDER_HOME`, no real
  `pricing.toml`, and no provider SDK calls.

Why:
- The budget guard must record the call that breached the budget before
  blocking future calls.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
.venv/bin/python tests/smoke/smoke_provider_call_guard.py
```

## S63 - Budget/provider guard cross-links

Where:
- `flightrecorder/docs/BUDGET_GUARD.md`
- `flightrecorder/docs/PROVIDER_CALL_GUARD.md`
- `flightrecorder/docs/NAVIGATION.md`

What:
- Add short cross-links between the budget sentinel doc and the provider guard
  doc.
- Make clear that `BUDGET_GUARD.md` describes the sentinel lifecycle, while
  `PROVIDER_CALL_GUARD.md` describes the paid-call enforcement path.
- Documentation-only.

Why:
- Future agents need to know which document answers which budget question.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
grep -q 'PROVIDER_CALL_GUARD.md' docs/BUDGET_GUARD.md
grep -q 'BUDGET_GUARD.md' docs/PROVIDER_CALL_GUARD.md
grep -q 'docs/PROVIDER_CALL_GUARD.md' docs/NAVIGATION.md
LC_ALL=C grep -n '[^ -~]' docs/BUDGET_GUARD.md docs/PROVIDER_CALL_GUARD.md docs/NAVIGATION.md && exit 1 || true
```

## S64 - Build status consistency audit

Where:
- `flightrecorder/docs/BUILD_STATUS.md`
- `flightrecorder/docs/MISSING_WORK.md`
- `flightrecorder/docs/BUILD_STATUS_AUDIT.md`

What:
- Create a short audit that compares `BUILD_STATUS.md` and `MISSING_WORK.md`
  against spec section 19.
- List any mismatch you find and fix only obvious doc drift in
  `BUILD_STATUS.md` or `MISSING_WORK.md`.
- Do not change code or the spec.

Why:
- The status docs are now updated by several agents and need a consistency
  check before the next implementation wave.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
grep -q 'Step 17' docs/BUILD_STATUS_AUDIT.md
grep -q 'Step 19' docs/BUILD_STATUS_AUDIT.md
LC_ALL=C grep -n '[^ -~]' docs/BUILD_STATUS.md docs/MISSING_WORK.md docs/BUILD_STATUS_AUDIT.md && exit 1 || true
```
