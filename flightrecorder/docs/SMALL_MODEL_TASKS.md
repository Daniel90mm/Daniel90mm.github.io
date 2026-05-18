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

## Active queue

Pick from the top unless Daniel or the senior agent says otherwise.

## S23 - Budget smoke script

Where:
- `flightrecorder/tests/smoke/smoke_budget.py`

What:
- Add a smoke script that initializes an in-memory sqlite database, inserts
  enough fake `api_calls` rows to cross the warn threshold, and prints the
  result from `evaluate_monthly_budget`.
- Do not add provider calls, real prices, routes, or schema changes.

Why:
- Budget warning and hard-stop behavior need a quick check before provider
  wrappers start using it.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
.venv/bin/python tests/smoke/smoke_budget.py
```

## S24 - Missing-work status doc

Where:
- `flightrecorder/docs/MISSING_WORK.md`
- `flightrecorder/docs/NAVIGATION.md`

What:
- Create a short human-readable snapshot of what remains from spec section 19.
- Use `docs/BUILD_STATUS.md` as the source, not memory.
- Include a count of done/in-progress/not-started steps.
- Add the new doc to navigation.

Why:
- Daniel asked how much is missing. A doc keeps the answer durable across
  agents.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
grep -q 'Not started' docs/MISSING_WORK.md
grep -q 'docs/MISSING_WORK.md' docs/NAVIGATION.md
LC_ALL=C grep -n '[^ -~]' docs/MISSING_WORK.md docs/NAVIGATION.md && exit 1 || true
```

## S25 - Config budget threshold validation tests

Where:
- `flightrecorder/tests/unit/test_config.py`

What:
- Add tests documenting the current config behavior for budget thresholds:
  defaults, explicit values, and the current lack of validation when warn is
  greater than hard stop.
- Do not change production code.

Why:
- If we later decide config parsing should reject invalid budget thresholds,
  the behavior change will be explicit.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
.venv/bin/python -m pytest tests/unit/test_config.py -q
```

## S26 - API draft examples consistency pass

Where:
- `flightrecorder/docs/API_CONTRACT_DRAFT.md`

What:
- Check that every example uses the same field names as `serializers.py`.
- Fix documentation-only mismatches if found.
- Do not edit backend code.

Why:
- Route implementation is blocked on Daniel approval, but the draft can still
  be made internally consistent.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
grep -q 'session_id' docs/API_CONTRACT_DRAFT.md
grep -q 'image_count' docs/API_CONTRACT_DRAFT.md
LC_ALL=C grep -n '[^ -~]' docs/API_CONTRACT_DRAFT.md && exit 1 || true
```

## S27 - Package import smoke

Where:
- `flightrecorder/tests/smoke/smoke_imports.py`

What:
- Add a smoke script that imports the backend modules directly:
  `app`, `config`, `costs`, `database`, `providers`, `runtime`, `schema`,
  `serializers`, and `storage`.
- Do not instantiate provider SDK clients.

Why:
- It catches accidental import-time dependency problems early.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
.venv/bin/python tests/smoke/smoke_imports.py
```

## S28 - README missing approval warning

Where:
- `flightrecorder/README.md`

What:
- Add one short note that `/api/sessions*` route implementation is waiting for
  Daniel approval of `docs/API_CONTRACT_DRAFT.md`.
- Do not add API commands that do not work yet.

Why:
- Prevents future agents from treating the draft API contract as implemented.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
grep -q 'API_CONTRACT_DRAFT.md' README.md
LC_ALL=C grep -n '[^ -~]' README.md && exit 1 || true
```
