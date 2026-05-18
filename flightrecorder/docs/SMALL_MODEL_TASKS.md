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

## Active queue

Pick from the top unless Daniel or the senior agent says otherwise.

## S101 - Provider usage fixtures smoke

Where:
- `flightrecorder/tests/smoke/smoke_provider_usage_fixtures.py`
- `flightrecorder/tests/fixtures/provider_usage/*.json`

What:
- Add a smoke script that loads every provider usage fixture JSON file.
- Verify each fixture has `provider`, `model`, `role`, `input_tokens`,
  `output_tokens`, and `cached_tokens` fields.
- Verify token fields are non-negative integers.

Why:
- Provider fixtures are now shared test inputs and need basic shape checking.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
.venv/bin/python tests/smoke/smoke_provider_usage_fixtures.py
```

## S102 - Adversarial fixture smoke

Where:
- `flightrecorder/tests/smoke/smoke_adversarial_fixtures.py`
- `flightrecorder/tests/fixtures/adversarial/`

What:
- Add a smoke script that checks every adversarial fixture text file is non-empty.
- Verify filenames cover names, emails, repo_urls, course_codes, mixed, and
  sensitive.
- Do not implement redaction.

Why:
- Redaction work must start from stable fixture coverage.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
.venv/bin/python tests/smoke/smoke_adversarial_fixtures.py
```

## S103 - Project registry fixture smoke

Where:
- `flightrecorder/tests/smoke/smoke_project_registry_fixture.py`
- `flightrecorder/tests/fixtures/project_registry/projects.json`

What:
- Add a smoke script that validates the project registry fixture is a JSON
  array with at least two entries.
- Verify each entry has `name`, `ref`, `path`, and `active`.
- Do not implement project registry loading.

Why:
- The registry contract should have one executable fixture check before code.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
.venv/bin/python tests/smoke/smoke_project_registry_fixture.py
```

## S104 - Spaghetti fixture smoke

Where:
- `flightrecorder/tests/smoke/smoke_spaghetti_fixture.py`
- `flightrecorder/tests/fixtures/spaghetti/*.md`

What:
- Add a smoke script that checks each spaghetti fixture has frontmatter markers
  and required fields: `idea_id`, `source_session`, `tags`, `status`, and
  `match_attempts`.
- Keep it string-based; do not add YAML dependencies.

Why:
- Future matchmaker and publisher tests need stable file-shape fixtures.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
.venv/bin/python tests/smoke/smoke_spaghetti_fixture.py
```

## S105 - Project document fixture smoke

Where:
- `flightrecorder/tests/smoke/smoke_project_document_fixture.py`
- `flightrecorder/tests/fixtures/documents/*.md`

What:
- Add a smoke script that checks project document fixtures include all standard
  project sections from `flightrecorder.documents.PROJECT_SECTIONS`.
- Do not alter runtime documents.

Why:
- Matchmaker and append-only tests need representative project documents.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
.venv/bin/python tests/smoke/smoke_project_document_fixture.py
```

## S106 - Current API docs route list sync

Where:
- `flightrecorder/docs/API_CURRENT_STATE.md`
- `flightrecorder/docs/SMOKE_COMMANDS.md`

What:
- Add `smoke_api_current_state.py` to the smoke command table and all-smoke
  loop if it is missing.
- Ensure `API_CURRENT_STATE.md` says the chat route is draft-only, not
  implemented.
- Documentation-only.

Why:
- API docs are now checked by a smoke script and should be included in the
  standard smoke list.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
grep -q 'smoke_api_current_state.py' docs/SMOKE_COMMANDS.md
grep -q 'draft-only' docs/API_CURRENT_STATE.md
LC_ALL=C grep -n '[^ -~]' docs/API_CURRENT_STATE.md docs/SMOKE_COMMANDS.md && exit 1 || true
```

## S107 - Navigation smoke command sync

Where:
- `flightrecorder/docs/SMOKE_COMMANDS.md`

What:
- Add `smoke_docs_navigation.py` to the smoke command table and all-smoke loop
  if it is missing.
- Documentation-only.

Why:
- Broken doc navigation links should be part of the normal smoke pass.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
grep -q 'smoke_docs_navigation.py' docs/SMOKE_COMMANDS.md
LC_ALL=C grep -n '[^ -~]' docs/SMOKE_COMMANDS.md && exit 1 || true
```

## S108 - Core progress sync with build status

Where:
- `flightrecorder/docs/CORE_PROGRESS.md`
- `flightrecorder/docs/BUILD_STATUS.md`

What:
- Check `CORE_PROGRESS.md` against `BUILD_STATUS.md`.
- If a percentage contradicts the status table, adjust the progress doc only.
- Documentation-only.

Why:
- The progress doc should stay an honest snapshot, not a stale dashboard.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
grep -q 'Overall v1' docs/CORE_PROGRESS.md
grep -q 'Step 17' docs/BUILD_STATUS.md
LC_ALL=C grep -n '[^ -~]' docs/CORE_PROGRESS.md docs/BUILD_STATUS.md && exit 1 || true
```

## S109 - Small task smoke command sync

Where:
- `flightrecorder/docs/SMOKE_COMMANDS.md`

What:
- Add `smoke_small_model_tasks.py` to the smoke command table and all-smoke
  loop if it is missing.
- Documentation-only.

Why:
- The queue integrity smoke should run in the normal smoke pass.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
grep -q 'smoke_small_model_tasks.py' docs/SMOKE_COMMANDS.md
LC_ALL=C grep -n '[^ -~]' docs/SMOKE_COMMANDS.md && exit 1 || true
```

## S110 - Handoff smoke command sync

Where:
- `flightrecorder/docs/SMOKE_COMMANDS.md`

What:
- Add `smoke_handoff_templates.py` to the smoke command table and all-smoke
  loop if it is missing.
- Documentation-only.

Why:
- Parallel work makes handoff/consult template checks part of normal hygiene.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
grep -q 'smoke_handoff_templates.py' docs/SMOKE_COMMANDS.md
LC_ALL=C grep -n '[^ -~]' docs/SMOKE_COMMANDS.md && exit 1 || true
```
