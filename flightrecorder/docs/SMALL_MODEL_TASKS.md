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
| S120 | Publisher pipeline smoke test. |
| S121 | Adversarial fixture directory resolver smoke. |
| S122 | Matchmaker API contract doc and NAVIGATION row. |
| S123 | Hugo path smoke after museum rename. |
| S124 | Local Hugo production build smoke. |
| S125 | GitHub Pages workflow smoke. |
| S126 | Generated-site internal link smoke. |
| S127 | Root deployment README. |
| S128 | Hugo smoke commands to one-liner sync. |
| S129 | Frontend scope synced with implemented API. |
| S130 | Static frontend dogfood shell. |
| S131 | Static frontend served from FastAPI. |
| S132 | Frontend chat stream parser smoke. |
| S133 | Frontend dogfood route smoke. |
| S134 | Frontend dogfood notes. |
| S135 | Dogfood read API contract for projects, documents, and spaghetti. |
| S136 | Read-only projects/documents API, verified and tightened by senior agent. |
| S137 | Read-only spaghetti API, verified and path-guarded by senior agent. |
| S138 | Frontend read panels for documents and spaghetti, verified by senior agent. |
| S139 | Dogfood read round-trip integration test. |
| S140 | Dogfood read workflow docs. |

## Active queue

Pick from the top unless Daniel or the senior agent says otherwise.

## S141 - Add real-provider dogfood config example

Where:
- `flightrecorder/config.example.toml` (new file)
- `flightrecorder/pricing.example.toml` (new file)
- `flightrecorder/README.md`
- `flightrecorder/docs/NAVIGATION.md`

What:
- Add copyable example files for an Anthropic-only MVP dogfood run.
- `config.example.toml` should include:
  1. `[providers.anthropic]` with an obvious placeholder key.
  2. `[roles.brainstorm]` and `[roles.idea_capture]` both using `anthropic`.
  3. Conservative budget thresholds.
  4. `runtime_home`, `hugo_site`, and `pricing_path` examples.
- `pricing.example.toml` should include one Anthropic model entry matching
  the example config model. Use clearly marked placeholder prices if exact
  rates are not already in repo data.
- README should point to the examples and state that real provider dogfood
  needs `FLIGHTRECORDER_CONFIG` plus real API keys.
- Add both new example files to `docs/NAVIGATION.md`.
- Do not include secrets.

Why:
- The MVP is now runnable with stubs, but the next bottleneck is making a real
  Anthropic-only dogfood run easy and repeatable.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
test -f config.example.toml
test -f pricing.example.toml
grep -q "FLIGHTRECORDER_CONFIG" README.md
PYTHONPATH=src/backend python tests/smoke/smoke_docs_navigation_consistency.py
```

Hand-back:
- When all commands pass, stop. Do not commit.

## S142 - Smoke the example config and pricing files

Where:
- `flightrecorder/tests/smoke/smoke_example_config.py` (new file)
- `flightrecorder/docs/SMOKE_COMMANDS.md`

What:
- Add a smoke script that parses `config.example.toml` with
  `flightrecorder.config.load_config`.
- Parse `pricing.example.toml` with `flightrecorder.costs.load_pricing`.
- Verify:
  1. `brainstorm` and `idea_capture` roles exist.
  2. Both roles reference providers that exist in the example config.
  3. Every role model used by those two roles has pricing.
  4. `paths.pricing_path` in the example points to `pricing.example.toml`.
- Add the smoke command to `docs/SMOKE_COMMANDS.md` and the all-smokes
  one-liner if needed.
- Do not edit provider implementation.

Why:
- Example files are only useful if they stay loadable as config parsing
  changes.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
.venv/bin/python tests/smoke/smoke_example_config.py
PYTHONPATH=src/backend python tests/smoke/smoke_small_model_tasks.py
```

Hand-back:
- When all commands pass, stop. Do not commit.

## S143 - Add runtime provider status API contract

Where:
- `flightrecorder/docs/API_CURRENT_STATE.md`
- `flightrecorder/docs/FRONTEND_SCOPE.md`
- `flightrecorder/docs/RUNTIME_PROVIDER_STATUS.md` (new file)
- `flightrecorder/docs/NAVIGATION.md`

What:
- Draft a concise read-only contract for `GET /api/runtime`.
- Response should include only safe runtime status:
  1. configured roles for `brainstorm` and `idea_capture`;
  2. provider name and model;
  3. whether each role is configured;
  4. `runtime_home`;
  5. no API keys or secrets.
- Mark the route draft-only in `API_CURRENT_STATE.md`.
- Mention in `FRONTEND_SCOPE.md` that the frontend should show provider
  readiness before chat/extract.
- Add the new doc to `docs/NAVIGATION.md`.
- Do not implement the route in this task.

Why:
- Before real-provider dogfood, the browser should make misconfigured roles
  obvious without exposing secrets.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
grep -q "GET /api/runtime" docs/RUNTIME_PROVIDER_STATUS.md
PYTHONPATH=src/backend python tests/smoke/smoke_docs_navigation_consistency.py
```

Hand-back:
- When all commands pass, stop. Do not commit.

## S144 - Implement read-only runtime provider status API

Where:
- `flightrecorder/src/backend/flightrecorder/api.py`
- `flightrecorder/tests/integration/test_runtime_status_api.py` (new file)
- `flightrecorder/tests/smoke/smoke_runtime_status_api.py` (new file)
- `flightrecorder/docs/API_CURRENT_STATE.md`
- `flightrecorder/docs/SMOKE_COMMANDS.md`

What:
- Implement `GET /api/runtime` from `docs/RUNTIME_PROVIDER_STATUS.md`.
- Return safe JSON only. Do not include API keys, environment variables, or
  raw config objects.
- Include role entries for `brainstorm` and `idea_capture`; each entry should
  include provider, model, and configured boolean.
- Add integration tests for configured and missing-role cases.
- Add a smoke script using `TestClient`.
- Update `API_CURRENT_STATE.md` and `SMOKE_COMMANDS.md`.

Why:
- This is the simplest way to catch "the backend is running but no real model
  is wired" before the user hits chat/extract.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
.venv/bin/python -m pytest tests/integration/test_runtime_status_api.py -q
.venv/bin/python tests/smoke/smoke_runtime_status_api.py
PYTHONPATH=src/backend python tests/smoke/smoke_api_current_state.py
```

Hand-back:
- When all commands pass, stop. Do not commit.

## S145 - Add frontend runtime readiness panel

Where:
- `flightrecorder/src/frontend/index.html`
- `flightrecorder/src/frontend/styles.css`
- `flightrecorder/src/frontend/app.js`
- `flightrecorder/tests/smoke/smoke_frontend_static.py`
- `flightrecorder/tests/smoke/smoke_frontend_dogfood.py`
- `flightrecorder/docs/FRONTEND_SCOPE.md`

What:
- Add a compact runtime readiness panel next to the budget panel.
- It should call `GET /api/runtime` on page load and render:
  1. brainstorm provider/model/configured status;
  2. idea_capture provider/model/configured status;
  3. runtime home.
- Use `textContent`; do not render HTML from API values.
- Do not block the existing stub dogfood flow if the runtime route fails;
  show a clear failure string in the panel.
- Update frontend smokes to assert the route string and panel element exist.
- Update `FRONTEND_SCOPE.md` to mark runtime readiness visible.

Why:
- Real dogfood needs the browser to show whether chat and extract are actually
  backed by configured providers.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
PYTHONPATH=src/backend python tests/smoke/smoke_frontend_static.py
.venv/bin/python tests/smoke/smoke_frontend_dogfood.py
```

Hand-back:
- When both commands pass, stop. Do not commit.

## S146 - Add Termux real-provider dogfood checklist

Where:
- `flightrecorder/docs/TERMUX_DEPENDENCIES.md`
- `flightrecorder/docs/TERMUX_PHONE_PATTERN.md`
- `flightrecorder/README.md`

What:
- Add a short checklist for running the current FastAPI dogfood UI on Termux
  with a real Anthropic config.
- Include:
  1. creating/copying config from `config.example.toml`;
  2. setting `FLIGHTRECORDER_CONFIG`;
  3. installing the package with dev dependencies;
  4. running `scripts/dev-backend.sh`;
  5. opening the phone/browser URL;
  6. checking budget and runtime readiness panels before chat/extract.
- Keep it as a checklist, not a long tutorial.
- Do not edit scripts or source code in this task.

Why:
- The next MVP milestone is running the dogfood loop on the intended phone
  deployment target, not only on a laptop.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
grep -q "FLIGHTRECORDER_CONFIG" docs/TERMUX_DEPENDENCIES.md
grep -q "runtime readiness" docs/TERMUX_PHONE_PATTERN.md
PYTHONPATH=src/backend python tests/smoke/smoke_small_model_tasks.py
```

Hand-back:
- When all commands pass, stop. Do not commit.
