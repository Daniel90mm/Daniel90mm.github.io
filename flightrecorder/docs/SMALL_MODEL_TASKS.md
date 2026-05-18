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

## Active queue

Pick from the top unless Daniel or the senior agent says otherwise.

## S55 - Budget sentinel smoke

Where:
- `flightrecorder/tests/smoke/smoke_budget_hard_stop.py`

What:
- Add a smoke script that inserts fake cost rows, calls
  `enforce_monthly_budget()`, and verifies a temp `budget` file is written.
- Do not touch real `~/flightrecorder/budget`.

Why:
- The hard-stop kill switch is a runtime safety boundary.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
.venv/bin/python tests/smoke/smoke_budget_hard_stop.py
```

## S56 - Budget docs update

Where:
- `flightrecorder/docs/BUDGET_GUARD.md`
- `flightrecorder/docs/NAVIGATION.md`

What:
- Document the `budget` sentinel file behavior:
  write on hard-stop, do not auto-clear on warn/ok, clear only explicitly.
- Documentation-only.

Why:
- Provider work must understand the safety boundary before adding paid calls.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
grep -q 'do not auto-clear' docs/BUDGET_GUARD.md
grep -q 'docs/BUDGET_GUARD.md' docs/NAVIGATION.md
LC_ALL=C grep -n '[^ -~]' docs/BUDGET_GUARD.md docs/NAVIGATION.md && exit 1 || true
```

## S57 - Smoke command sync for new guards

Where:
- `flightrecorder/docs/SMOKE_COMMANDS.md`

What:
- Add `smoke_documents_git.py` to the smoke command table and all-smoke loop.
- If S55 is already complete, add `smoke_budget_hard_stop.py` too.
- Documentation-only.

Why:
- The smoke index should stay aligned with runnable safety checks.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
grep -q 'smoke_documents_git.py' docs/SMOKE_COMMANDS.md
grep -q 'smoke_documents_git' docs/SMOKE_COMMANDS.md
LC_ALL=C grep -n '[^ -~]' docs/SMOKE_COMMANDS.md && exit 1 || true
```

## S58 - Budget guard README status

Where:
- `flightrecorder/README.md`

What:
- Add one short status sentence saying budget tracking has a hard-stop sentinel
  helper, but provider/chat paths do not enforce it yet.
- Do not document any setup command for clearing the sentinel.

Why:
- The README should reflect the hard-stop primitive without overclaiming that
  paid-call enforcement exists.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
grep -q 'hard-stop sentinel' README.md
grep -q 'do not enforce it yet' README.md
LC_ALL=C grep -n '[^ -~]' README.md && exit 1 || true
```
