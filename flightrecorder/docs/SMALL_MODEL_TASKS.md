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
| S119 | Session round-trip integration test. |
| S122 | Matchmaker API contract doc and NAVIGATION row. |
| S123 | Hugo path smoke after museum rename. |
| S124 | Local Hugo production build smoke. |
| S125 | GitHub Pages workflow smoke. |

## Active queue

Pick from the top unless Daniel or the senior agent says otherwise.

## S126 - Add generated-site internal link smoke

Where:
- `flightrecorder/tests/smoke/smoke_hugo_internal_links.py` (new file)
- `flightrecorder/docs/SMOKE_COMMANDS.md`

What:
- Add an executable smoke script that builds the Hugo site into a temporary
  directory and checks generated internal links.
- The script should:
  1. Run Hugo from `museum/` into a temporary destination, like S124.
  2. Walk generated `*.html` files.
  3. Parse `href="..."` links using Python standard library tools or a
     small regex.
  4. Ignore external URLs, `mailto:`, fragments, and query-only links.
  5. For root-relative internal links such as `/projects/foo/`, assert the
     destination exists as either `<dest>/projects/foo/index.html` or a file
     path under the generated destination.
  6. For relative internal links, resolve them relative to the current HTML
     file and assert the destination exists.
  7. Print a count of checked links and `hugo internal link smoke test
     passed` on success.
- Add the new script to `docs/SMOKE_COMMANDS.md`.
- Do not edit Hugo content/templates in this task; this is only a smoke.

Why:
- The home page is a project index. Broken internal links are one of the
  easiest ways for the site to look "up" while still being functionally
  broken.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
PYTHONPATH=src/backend python tests/smoke/smoke_hugo_internal_links.py
PYTHONPATH=src/backend python tests/smoke/smoke_small_model_tasks.py
```

Hand-back:
- When both commands pass, stop. Do not commit.

## S127 - Add root deployment README

Where:
- `README.md` (new file at repository root)

What:
- Add a concise root README for this merged repository.
- It should explain:
  1. `museum/` is the Hugo site deployed to GitHub Pages.
  2. `flightrecorder/` is the brainstorming app under active development.
  3. Local site build command:
     `cd museum && hugo --gc --minify`.
  4. Local site preview command:
     `cd museum && hugo server --disableFastRender`.
  5. Deployment path: pushes to `main` run `.github/workflows/hugo.yml`
     and publish to `https://daniel90mm.github.io/`.
  6. Do not commit generated `museum/public/`.
- Keep it short. This is an operator note, not marketing copy.
- Do not edit Hugo content, workflow, or flightrecorder code in this task.

Why:
- After merging repos and renaming the Hugo tree to `museum/`, the root has
  no quick operational entry point. A README prevents future confusion about
  how the public site is built and deployed.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io
test -f README.md
grep -q "museum/" README.md
grep -q "flightrecorder/" README.md
grep -q "hugo --gc --minify" README.md
grep -q "daniel90mm.github.io" README.md
```

Hand-back:
- When the commands pass, stop. Do not commit.

## S128 - Add Hugo smoke commands to one-liner

Where:
- `flightrecorder/docs/SMOKE_COMMANDS.md`

What:
- After S123-S126 exist, update the one-liner in `docs/SMOKE_COMMANDS.md`
  so the new Hugo/Page smoke scripts run with system `python` and
  `PYTHONPATH=src/backend`.
- Keep the table alphabetically or grouped consistently with the existing
  style.
- Do not create new smoke scripts in this task. If any S123-S126 script is
  missing, stop and report which one is missing.

Why:
- A smoke script that is not included in the all-smokes command is easy to
  forget. The deployment checks should be part of the normal quick sweep.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
PYTHONPATH=src/backend python tests/smoke/smoke_hugo_paths.py
PYTHONPATH=src/backend python tests/smoke/smoke_hugo_build.py
PYTHONPATH=src/backend python tests/smoke/smoke_pages_workflow.py
PYTHONPATH=src/backend python tests/smoke/smoke_hugo_internal_links.py
PYTHONPATH=src/backend python tests/smoke/smoke_small_model_tasks.py
```

Hand-back:
- When all commands pass, stop. Do not commit.

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
