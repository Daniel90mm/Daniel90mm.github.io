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

## Active queue

Pick from the top unless Daniel or the senior agent says otherwise.

## S29 - Project document smoke script

Where:
- `flightrecorder/tests/smoke/smoke_project_documents.py`

What:
- Create a temp runtime home, call `create_project_document`, append one TODO
  with `append_to_project_document`, and print the resulting path.
- Assert the TODO landed between `## TODOs` and `## Ideas`.
- Do not invoke git or provider calls.

Why:
- The append-only document core is now a critical primitive for idea capture.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
.venv/bin/python tests/smoke/smoke_project_documents.py
```

## S30 - Project document README note

Where:
- `flightrecorder/README.md`

What:
- Add one short status sentence saying append-only project document helpers
  exist, but idea-capture LLM parsing is not wired.
- Do not document commands that do not exist.

Why:
- Future agents should not mistake document helpers for completed step 8.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
grep -q 'append-only project document helpers' README.md
LC_ALL=C grep -n '[^ -~]' README.md && exit 1 || true
```

## S31 - Small-model queue smoke sync

Where:
- `flightrecorder/docs/SMOKE_COMMANDS.md`

What:
- Add `tests/smoke/smoke_project_documents.py` to the smoke command index after
  S29 exists.
- Keep the all-smoke loop working.

Why:
- Smoke docs should track new smoke scripts immediately.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
grep -q 'smoke_project_documents.py' docs/SMOKE_COMMANDS.md
LC_ALL=C grep -n '[^ -~]' docs/SMOKE_COMMANDS.md && exit 1 || true
```

## S32 - Project document filename tests

Where:
- `flightrecorder/tests/unit/test_documents.py`

What:
- Add tests for `sanitize_project_ref` with spaces, uppercase, underscores,
  and hyphens.
- Do not edit backend code.

Why:
- Project refs become filenames, so filename behavior should stay boring and
  deterministic.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
.venv/bin/python -m pytest tests/unit/test_documents.py -q
```

## S33 - Missing-work snapshot sync

Where:
- `flightrecorder/docs/MISSING_WORK.md`

What:
- Confirm the counts match `docs/BUILD_STATUS.md` after step 8 moved to in
  progress.
- Do not change build status unless it is factually wrong.

Why:
- Daniel asked "how much is missing"; this doc must not drift.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
grep -q 'In progress: **3**' docs/MISSING_WORK.md
grep -q 'Not started: **16**' docs/MISSING_WORK.md
LC_ALL=C grep -n '[^ -~]' docs/MISSING_WORK.md && exit 1 || true
```

## S34 - API contract review sync

Where:
- `flightrecorder/docs/API_CONTRACT_REVIEW.md`

What:
- Check whether the review checklist still mentions all open issues from
  `docs/API_CONTRACT_DRAFT.md`.
- Add a note that field names are snake_case if missing.
- Do not edit backend code.

Why:
- API implementation remains blocked on this approval surface.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
grep -q 'snake_case' docs/API_CONTRACT_REVIEW.md
LC_ALL=C grep -n '[^ -~]' docs/API_CONTRACT_REVIEW.md && exit 1 || true
```
