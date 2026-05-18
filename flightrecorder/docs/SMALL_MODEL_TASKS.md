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
| S52 | Documents git auto-commit path, completed by senior agent. |

## Active queue

Pick from the top unless Daniel or the senior agent says otherwise.

## S48 - Idea-capture parser edge docs

Where:
- `flightrecorder/docs/IDEA_CAPTURE_VALIDATION.md`
- `flightrecorder/docs/NAVIGATION.md`

What:
- Document what `parse_idea_operations()` accepts and rejects.
- Mention the max of eight operations.
- Documentation-only.

Why:
- Future prompt/provider work needs to know the exact parser boundary.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
grep -q 'max of eight' docs/IDEA_CAPTURE_VALIDATION.md
grep -q 'docs/IDEA_CAPTURE_VALIDATION.md' docs/NAVIGATION.md
LC_ALL=C grep -n '[^ -~]' docs/IDEA_CAPTURE_VALIDATION.md docs/NAVIGATION.md && exit 1 || true
```

## S49 - Idea-capture README status

Where:
- `flightrecorder/README.md`

What:
- Add one short status sentence saying idea-capture operation parsing and
  spaghetti/project routing exist, but the LLM call itself is not wired.
- Do not add commands that do not exist.

Why:
- Step 8 is partially implemented; the README should not overclaim.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
grep -q 'idea-capture operation parsing' README.md
LC_ALL=C grep -n '[^ -~]' README.md && exit 1 || true
```

## S50 - Idea-capture smoke docs

Where:
- `flightrecorder/docs/SMOKE_COMMANDS.md`

What:
- Confirm `smoke_idea_capture.py` and `smoke_termux_helper.py` are both listed
  in the smoke command table and all-smoke loop.
- Documentation-only.

Why:
- The active smoke list should reflect the latest helper scripts.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
grep -q 'smoke_idea_capture.py' docs/SMOKE_COMMANDS.md
grep -q 'smoke_termux_helper.py' docs/SMOKE_COMMANDS.md
LC_ALL=C grep -n '[^ -~]' docs/SMOKE_COMMANDS.md && exit 1 || true
```

## S51 - Documents git smoke

Where:
- `flightrecorder/tests/smoke/smoke_documents_git.py`

What:
- Add a smoke script that creates a temp `documents/` repo with
  `ensure_documents_repo`, appends a project document, commits it, and prints
  the latest commit subject.
- Do not touch real `~/flightrecorder/documents/`.

Why:
- Project documents have their own git history; this must stay easy to verify.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
.venv/bin/python tests/smoke/smoke_documents_git.py
```

## S53 - Documents git docs

Where:
- `flightrecorder/docs/DOCUMENTS_GIT.md`
- `flightrecorder/docs/NAVIGATION.md`

What:
- Document that `~/flightrecorder/documents/` is its own git repo, initialized
  by `ensure_documents_repo()`, and committed by `commit_documents_repo()`.
- Mention that clean-tree commits are skipped.
- Documentation-only.

Why:
- This is a core append-only audit trail and should be explicit for future
  agents.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
grep -q 'clean-tree commits are skipped' docs/DOCUMENTS_GIT.md
grep -q 'docs/DOCUMENTS_GIT.md' docs/NAVIGATION.md
LC_ALL=C grep -n '[^ -~]' docs/DOCUMENTS_GIT.md docs/NAVIGATION.md && exit 1 || true
```
