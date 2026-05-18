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

## Active queue

Pick from the top unless Daniel or the senior agent says otherwise.

## S91 - Idea-capture malformed-output smoke

Where:
- `flightrecorder/tests/smoke/smoke_idea_capture.py`

What:
- Add a small smoke branch that feeds malformed JSON to `parse_idea_operations()`.
- Verify `IdeaCaptureError` is raised.
- Verify no project document, spaghetti file, or `ideas` row is created by that
  malformed parse branch.
- Do not change prompts or provider code.

Why:
- The future LLM execution path must fail closed when model output is malformed.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
.venv/bin/python tests/smoke/smoke_idea_capture.py
```

## S92 - Session close blockers note

Where:
- `flightrecorder/docs/SESSION_CLOSE_PIPELINE.md`

What:
- Add a short "Blockers before implementation" section.
- Include chat endpoint approval, provider SDK execution, idea-capture LLM call,
  and retry/error semantics.
- Documentation-only.

Why:
- Session close is the next bridge to core value, but it should not be wired
  until the upstream pieces are clear.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
grep -q 'Blockers before implementation' docs/SESSION_CLOSE_PIPELINE.md
grep -q 'retry' docs/SESSION_CLOSE_PIPELINE.md
LC_ALL=C grep -n '[^ -~]' docs/SESSION_CLOSE_PIPELINE.md && exit 1 || true
```

## S93 - Project registry fixture skeleton

Where:
- `flightrecorder/tests/fixtures/project_registry/projects.json`
- `flightrecorder/tests/fixtures/project_registry/README.md`

What:
- Add a fake `projects.json` fixture matching the current contract draft.
- Include at least two fake projects with distinct refs and paths.
- Fixtures only. Do not implement registry loading.

Why:
- Future registry tests need a stable fake input before sync code exists.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
python -m json.tool tests/fixtures/project_registry/projects.json >/dev/null
grep -q 'fake project registry' tests/fixtures/project_registry/README.md
LC_ALL=C grep -n '[^ -~]' tests/fixtures/project_registry/README.md tests/fixtures/project_registry/projects.json && exit 1 || true
```

## S94 - Spaghetti format fixture

Where:
- `flightrecorder/tests/fixtures/spaghetti/README.md`
- `flightrecorder/tests/fixtures/spaghetti/*.md`

What:
- Add one fake spaghetti markdown fixture that follows `docs/SPAGHETTI_FORMAT.md`.
- Include tags, topics, status, match_attempts, matched_to, implemented_in,
  source_session, and body text.
- Fixtures only. Do not implement reader code.

Why:
- Matchmaker and publisher tests will need stable spaghetti examples.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
grep -q 'match_attempts' tests/fixtures/spaghetti/*.md
grep -q 'fake spaghetti' tests/fixtures/spaghetti/README.md
LC_ALL=C grep -n '[^ -~]' tests/fixtures/spaghetti/README.md tests/fixtures/spaghetti/*.md && exit 1 || true
```

## S95 - Project document fixture

Where:
- `flightrecorder/tests/fixtures/documents/README.md`
- `flightrecorder/tests/fixtures/documents/*.md`

What:
- Add one fake project document fixture using the standard section headers.
- Include at least one TODO, one idea, and one hand-written note.
- Fixtures only. Do not alter runtime `documents/`.

Why:
- Matchmaker, publisher, and append-only tests need a stable project document
  that is not real runtime data.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
grep -q '## TODOs' tests/fixtures/documents/*.md
grep -q 'fake project document' tests/fixtures/documents/README.md
LC_ALL=C grep -n '[^ -~]' tests/fixtures/documents/README.md tests/fixtures/documents/*.md && exit 1 || true
```

## S96 - Publisher fixture privacy readme

Where:
- `flightrecorder/tests/fixtures/adversarial/README.md`

What:
- Add explicit guidance that adversarial fixtures must remain fake and must not
  include real private data.
- Mention that realistic-looking examples are acceptable only when invented.
- Documentation-only.

Why:
- We need adversarial tests, but not by committing actual sensitive data.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
grep -q 'must remain fake' tests/fixtures/adversarial/README.md
grep -q 'invented' tests/fixtures/adversarial/README.md
LC_ALL=C grep -n '[^ -~]' tests/fixtures/adversarial/README.md && exit 1 || true
```

## S97 - Termux service open questions

Where:
- `flightrecorder/docs/TERMUX_SERVICE_INVENTORY.md`

What:
- Add an "Open questions" section for service names, exact runit paths,
  wake-lock wrapping, and log file locations.
- Documentation-only. Do not create service files.

Why:
- Termux setup needs phone-specific confirmation before scripts become real.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
grep -q 'Open questions' docs/TERMUX_SERVICE_INVENTORY.md
grep -q 'wake-lock' docs/TERMUX_SERVICE_INVENTORY.md
LC_ALL=C grep -n '[^ -~]' docs/TERMUX_SERVICE_INVENTORY.md && exit 1 || true
```

## S98 - API current-state smoke

Where:
- `flightrecorder/tests/smoke/smoke_api_current_state.py`
- `flightrecorder/docs/API_CURRENT_STATE.md`

What:
- Add a smoke script that checks every implemented route documented in
  `API_CURRENT_STATE.md` appears in `src/backend/flightrecorder/api.py` or
  `app.py`.
- Keep it lightweight string matching.

Why:
- API docs should not drift while frontend work is pending.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
.venv/bin/python tests/smoke/smoke_api_current_state.py
```

## S99 - Navigation smoke

Where:
- `flightrecorder/tests/smoke/smoke_docs_navigation.py`
- `flightrecorder/docs/NAVIGATION.md`

What:
- Add a smoke script that extracts `docs/...` paths from `NAVIGATION.md` and
  verifies each referenced file exists.
- Do not require every docs file to be listed yet.

Why:
- The navigation doc is now growing quickly and broken links are easy to miss.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
.venv/bin/python tests/smoke/smoke_docs_navigation.py
```

## S100 - Core progress estimate doc

Where:
- `flightrecorder/docs/CORE_PROGRESS.md`
- `flightrecorder/docs/NAVIGATION.md`

What:
- Create a concise percentage-style progress snapshot for the core v1 areas:
  backend skeleton, session storage, cost guard, project docs, idea capture,
  chat, frontend, tagger, pokemon mapping, matchmaker, publisher, Termux.
- Base it on `BUILD_STATUS.md`; do not overclaim.
- Documentation-only.

Why:
- Daniel asked for percentage thinking, and this should be tracked in-repo
  instead of living only in chat.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
grep -q 'Overall v1' docs/CORE_PROGRESS.md
grep -q 'publisher' docs/CORE_PROGRESS.md
grep -q 'docs/CORE_PROGRESS.md' docs/NAVIGATION.md
LC_ALL=C grep -n '[^ -~]' docs/CORE_PROGRESS.md docs/NAVIGATION.md && exit 1 || true
```
