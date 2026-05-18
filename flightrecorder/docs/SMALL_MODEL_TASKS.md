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
| S62 | Provider guard hard-stop breach smoke. |
| S63 | Budget/provider guard cross-links. |
| S64 | Build status consistency audit. |

## Active queue

Pick from the top unless Daniel or the senior agent says otherwise.

## S65 - Provider guard missing pricing smoke

Where:
- `flightrecorder/tests/smoke/smoke_provider_call_guard.py`

What:
- Extend the smoke script to verify that a usage record for an unknown model
  raises `ValueError`.
- Verify no `api_calls` row is inserted for the rejected unknown model.
- Keep this smoke fully fake: no real `$FLIGHTRECORDER_HOME`, no real
  `pricing.toml`, and no provider SDK calls.

Why:
- Missing pricing must fail closed before real provider calls are wired.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
.venv/bin/python tests/smoke/smoke_provider_call_guard.py
```

## S66 - Provider guard mismatch smoke

Where:
- `flightrecorder/tests/smoke/smoke_provider_call_guard.py`

What:
- Extend the smoke script to verify that a usage record whose provider does
  not match the pricing entry raises `ValueError`.
- Verify no `api_calls` row is inserted for the rejected mismatch.
- Keep this smoke fully fake.

Why:
- Provider/model mismatches are usually configuration bugs and must not create
  misleading cost rows.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
.venv/bin/python tests/smoke/smoke_provider_call_guard.py
```

## S67 - Provider guard doc examples

Where:
- `flightrecorder/docs/PROVIDER_CALL_GUARD.md`

What:
- Add a short "Failure cases" section covering:
  missing pricing, provider/model mismatch, existing budget sentinel, and
  post-call hard-stop breach.
- Documentation-only. Do not mention commands that do not exist.

Why:
- The guard is small but security/cost critical; future agents should know the
  intended fail-closed behavior.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
grep -q 'Failure cases' docs/PROVIDER_CALL_GUARD.md
grep -q 'missing pricing' docs/PROVIDER_CALL_GUARD.md
grep -q 'provider/model mismatch' docs/PROVIDER_CALL_GUARD.md
LC_ALL=C grep -n '[^ -~]' docs/PROVIDER_CALL_GUARD.md && exit 1 || true
```

## S68 - Build status audit navigation

Where:
- `flightrecorder/docs/NAVIGATION.md`
- `flightrecorder/docs/BUILD_STATUS_AUDIT.md`

What:
- Add `docs/BUILD_STATUS_AUDIT.md` to `docs/NAVIGATION.md`.
- Add a one-line "Last audited" note at the top of
  `docs/BUILD_STATUS_AUDIT.md` with today's date.
- Documentation-only.

Why:
- The audit is only useful if future agents can find it and know when it was
  last checked.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
grep -q 'docs/BUILD_STATUS_AUDIT.md' docs/NAVIGATION.md
grep -q 'Last audited' docs/BUILD_STATUS_AUDIT.md
LC_ALL=C grep -n '[^ -~]' docs/NAVIGATION.md docs/BUILD_STATUS_AUDIT.md && exit 1 || true
```

## S69 - Smoke command all-loop audit

Where:
- `flightrecorder/docs/SMOKE_COMMANDS.md`

What:
- Compare every file in `tests/smoke/*.py` with the smoke command table.
- Add any missing smoke script rows.
- Make sure the all-smoke loop routes every FastAPI/package-dependent smoke
  through `.venv/bin/python`.
- Documentation-only.

Why:
- The smoke list has become the handoff surface for small tasks; it should not
  silently miss scripts.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
for script in tests/smoke/*.py; do grep -q "$(basename "$script")" docs/SMOKE_COMMANDS.md; done
LC_ALL=C grep -n '[^ -~]' docs/SMOKE_COMMANDS.md && exit 1 || true
```

## S70 - README status line wrap

Where:
- `flightrecorder/README.md`

What:
- Reflow the long status paragraph into readable lines without changing its
  meaning.
- Do not add claims about real provider SDK calls, chat endpoint completion, or
  frontend work.
- Documentation-only.

Why:
- The README status is getting too dense and easy to misread.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
grep -q 'real SDK calls are not yet wired' README.md
LC_ALL=C grep -n '[^ -~]' README.md && exit 1 || true
```

## S71 - Termux helper dry-run docs

Where:
- `flightrecorder/docs/TERMUX_PHONE_PATTERN.md`
- `flightrecorder/docs/NAVIGATION.md`

What:
- Add a short section describing what has and has not been run on pa-server:
  dorm-assistant pattern inspected, helper syntax/smoke checked locally,
  phone execution still pending.
- Documentation-only. Do not run phone commands.

Why:
- Step 19 is intentionally in progress; future agents need the exact boundary.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
grep -q 'phone execution still pending' docs/TERMUX_PHONE_PATTERN.md
grep -q 'docs/TERMUX_PHONE_PATTERN.md' docs/NAVIGATION.md
LC_ALL=C grep -n '[^ -~]' docs/TERMUX_PHONE_PATTERN.md docs/NAVIGATION.md && exit 1 || true
```

## S72 - Small task queue integrity check

Where:
- `flightrecorder/docs/SMALL_MODEL_TASKS.md`
- `flightrecorder/tests/smoke/smoke_small_model_tasks.py`

What:
- Add a smoke script that checks task IDs are unique and increase
  monotonically within the completed ledger plus active queue.
- Keep it parser-light: regex over `SNN` headings and ledger rows is fine.

Why:
- This file is now a coordination surface for parallel work; duplicate task IDs
  would waste time.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
.venv/bin/python tests/smoke/smoke_small_model_tasks.py
```
