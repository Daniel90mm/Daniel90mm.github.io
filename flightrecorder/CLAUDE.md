# AGENTS.md

Operating manual for coding agents working on flightrecorder. The full design is in `flightrecorder-spec.md` (canonical); this file is the working playbook.

## What this is

flightrecorder is a self-hosted brainstorming web app with curated public publishing. It runs on Termux on an Android phone (pa-server), captures Daniel's brainstorms, routes ideas to project documents or a spaghetti wall, proposes matches weekly, and publishes the full journey of each idea to `daniel90mm.github.io` on a 24h delay.

The novel pieces are not the chat UI. They are:

1. **Idea capture** — extracting discrete ideas from each session and routing them.
2. **Append-only project documents** — grow by accretion, never rewritten.
3. **Matchmaker** — weekly pass that proposes how loose ideas connect to existing projects.
4. **Automatic publishing with adversarial review** — no human gate, two-pass redaction with different model providers.

Build the novel pieces with extra care. The chat UI is the easy part.

## Source of truth

The spec is canonical. When this file conflicts with the spec, the spec wins and this file is wrong — flag it.

When the spec is unclear, **ask Daniel**. Do not invent. Do not pattern-match to "what most apps do." The spec was written deliberately; gaps are intentional or oversights, and either way the answer is "ask."

The spec references the build order in §19. Follow it. If a step blocks on a question, ask before working around.

## Critical constraints

These are hard rules. Violating them is worse than missing a deadline.

### 1. Doxxing is a security boundary

The curator and reviewer are not "guidelines." They are the only thing between Daniel's raw brainstorms and the open web. The pipeline auto-publishes on a 24h delay with no human approval step.

- Curator and reviewer must use **different providers** when possible (see `config.toml` defaults).
- Reviewer's bias is "reject by default." When in doubt, reject.
- Before any code touches the publisher pipeline, write tests with adversarial inputs: real-looking names, emails, repo URLs, course codes with semesters, sensitive personal content. The pipeline must catch all of them.
- The whitelist is `{"daniel"}`. Anything else gets pseudonymized or omitted.

### 2. Append-only is sacred

Project documents (`~/flightrecorder/documents/*.md`) are append-only. The system **never** rewrites existing content in these files.

- Code that touches a project document must use append semantics: read, find the right section, append a bullet under it, write back. No re-flowing existing content.
- The idea-capture prompt may *generate* a new bullet to append, but must not modify existing bullets.
- Section headers (`## Problem`, `## Decisions made`, etc.) are stable. Don't add new top-level sections unless the spec defines them.
- Daniel may hand-edit documents. That is fine. The system must tolerate documents that don't perfectly match its conventions.

If you find yourself wanting to rewrite a document "for clarity," stop. That is drift, and it's the failure mode this architecture is designed to prevent.

### 3. Prompts are the product

The prompts in `prompts/` (curator, matchmaker, idea-capture, reviewer, composer, brainstorm-system) are first-class artifacts. They are versioned, tested, and changed deliberately.

- Do not edit prompts casually. Prompt changes need the same care as code changes.
- When tuning a prompt, save the previous version. We need history.
- Tests for prompts are example inputs with expected output shapes (not exact strings — LLM outputs vary). Validate structure and that doxxing/redaction rules hold.

### 4. Termux constraints are real

pa-server is an Android phone running Termux. ARM64. No systemd. Battery optimization will kill processes unless `termux-wake-lock` is held during long-running jobs. `termux-boot` is required for autostart.

- Don't assume Linux server conventions. `/var/lib/` doesn't exist; use `$FLIGHTRECORDER_HOME`.
- Verify Python deps install on Termux ARM64 before committing. Some binary wheels don't exist for `aarch64-linux-android` and need source builds.
- Daemons run under `termux-services` (runit-based), not systemd. Use the runit conventions.
- File paths in config should be expandable (`~`, env vars), never hardcoded.

The code should also run on a normal Linux box without changes. Future migration to RPi or x86 should be a config swap, not a rewrite.

### 5. Cost discipline

Every LLM call logs to `metadata.db.api_calls` with token counts and computed cost. The budget hard-stop is a real kill switch.

- Don't add LLM calls casually. Each new prompt is a new line item on Daniel's monthly bill.
- Use cheap models for structured extraction (Haiku, gpt-5-mini). Reserve expensive long-context models for actual brainstorming and the matchmaker.
- Cache where the API supports it (Anthropic prompt caching for long system prompts, Gemini context caching for project documents in brainstorm context).
- If a feature wants to call an LLM in a loop, propose a batch alternative first.

## Code style

Daniel's preferences, applied throughout:

- **Python** primary. **C** for embedded (not applicable here, but mentioned for completeness).
- **Double quotes** for strings, never single quotes.
- **No unicode** characters in code or output. Write `"pi"` not the Greek letter. Write `"omega"` not the Greek letter. ASCII only.
- **Type hints** on all function signatures.
- **Async-first** for the backend (FastAPI is async; provider calls are async).
- **Small modules.** Big files are a smell; split when something feels crowded.
- **Tests live in `tests/`** matching the `src/` layout.

Frontend (Svelte):

- Plain Svelte, no SvelteKit unless there's a clear reason.
- TypeScript over plain JS for non-trivial logic.
- Tailwind for styling, terminal/TUI aesthetic to match `daniel90mm.github.io`.
- No analytics, no telemetry. Tailscale is the trust boundary; nothing leaks out.

For plots (rare in this project but in case):

- `figsize=(13, 5)`, `dpi=300`.

## Build approach

Follow the build order in spec §19. Each numbered step is a milestone with a verifiable outcome.

For each step:

1. **Re-read the relevant spec sections.** Don't work from memory of an earlier read.
2. **Propose a plan** before writing code. Plan = files you'll touch, key interfaces, test approach. Ask Daniel to confirm if the step is non-trivial.
3. **Write tests first** for anything that has correctness criteria (doxxing redaction, append-only semantics, idea-capture extraction, matchmaker rejection bias).
4. **Implement.**
5. **Verify against the spec.** Did you actually build what §X said to build?
6. **Update `RESEARCH_LOG.md`** with what you found, what you decided, what's still open.
7. **Hand off** if the session ends mid-step (see Protocols below).

Do not skip steps because they feel obvious. Especially do not skip tests for the doxxing path, the append-only path, and the cost-logging path.

### Junior task queue

When a task is narrow and suitable for the junior agent, move it into `docs/JUNIOR_TASKS.md` instead of doing it inline. Each queued task must include where to work, what to do, why it matters, and a specific smoke test. Use the junior for implementation-first work: tests, fixtures, endpoints, UI behavior, and small helpers. Do not queue docs for docs' sake; docs are acceptable only when they directly support code that is being built or verified. Keep the senior agent focused on architectural judgment, security judgment, prompt judgment, and cross-file integration.

## Testing posture

What gets tested:

- **Doxxing redaction.** Adversarial inputs, both pre-reviewer (curator output) and post-reviewer (final published artifact). Pokemon mapping is deterministic — verify with hash tests.
- **Append-only document semantics.** Property test: after N appends, every input bullet is present in the output document, in some section, exactly once.
- **Idea-capture extraction.** Given a fixed transcript, the extraction is *structurally* stable: same number of operations of the same types, same project_refs. Exact text content may vary (LLM nondeterminism); structure should not.
- **Matchmaker rejection bias.** Given a session that genuinely doesn't match any project, the matchmaker must produce zero matches across multiple runs. Otherwise it's rationalizing.
- **Cost logging.** Every code path that calls a provider writes an `api_calls` row. Verify by counting rows after a test run.
- **Pipeline integration.** End-to-end test: feed a session, watch it tag → extract → publish through curator+reviewer → land in `published/`. Compare against a golden output (structure, not exact text).

What doesn't need full coverage:

- The frontend UI. Manual verification is fine. Snapshot tests are overkill for v1.
- Provider abstraction internals (they're thin wrappers).
- Hugo template rendering.

## Protocols

### Completion commit protocol

When a coherent chunk of work is complete and worth preserving, commit and push
it after verification unless Daniel explicitly says not to.

- Run the relevant tests or smoke checks first.
- Inspect `git status` and `git diff` before staging.
- Stage only files that belong to the completed chunk. Do not sweep in
  unrelated user edits, runtime data, secrets, caches, or generated build
  output.
- Use a direct commit message that names the completed work.
- Push the current branch after the commit succeeds.
- If the tree contains unrelated changes that make a clean commit ambiguous,
  stop and ask Daniel which files belong in the commit.

### Handoff protocol

When a session ends without finishing the current build step, write a handoff to `handoffs/YYYY-MM-DD-HHMM-<slug>.md`:

```markdown
# Handoff: <one-line summary>

Date: <iso8601>
Step: <build order step number from spec §19>
State: <in-progress | blocked | ready-for-review>

## What's done
- ...

## What's not done
- ...

## Open questions
- ...

## Where to pick up
1. ...
2. ...

## Files touched this session
- ...
```

The next agent reads the most recent handoff first. If multiple handoffs exist for the same step, read them in chronological order.

### Consult protocol

When stuck or facing a decision with non-obvious tradeoffs, write a consult to `consults/YYYY-MM-DD-HHMM-<slug>.md`:

```markdown
# Consult: <decision title>

## Context
<what we're trying to do>

## Options
1. <option A> — pros: ... cons: ...
2. <option B> — pros: ... cons: ...
3. <option C> — pros: ... cons: ...

## Lean
<your current best guess, with reasoning>

## Asking
<what you want from a second opinion>
```

Then either ask Daniel to weigh in, or run the consult past a different model. Don't proceed with a non-obvious decision on autopilot.

### Spec-change protocol

If you believe the spec is wrong, do not silently work around it.

1. Write a consult arguing for the change.
2. Get Daniel's sign-off.
3. Update the spec.
4. Then implement.

The spec is the contract. Code that contradicts it is bugs in disguise.

## Communication style

Match Daniel's preferences when reporting progress or asking questions:

- **Skip preambles.** Don't say "Great question!" or "Let me think about this." Start with the answer.
- **Concise by default.** Verbose only when asked.
- **Honest tradeoffs.** Don't sell. Name the cost-benefit.
- **Flag procrastination.** Daniel has a documented infrastructure-as-procrastination pattern. If a proposed task looks like building scaffolding to avoid the real work, say so.
- **Push back when you should.** Reasonable disagreement is not disrespect.
- **Show reasoning.** Especially for engineering decisions.
- **Match his language.** He writes in Danish or English; answer in whichever he used.

What not to do:

- Don't restate his question before answering.
- Don't apologize unprompted.
- Don't use emoji unless he does first.
- Don't pad responses with options when the right answer is clear.

## When to stop and ask

Stop and ask Daniel before:

- Adding a new dependency (especially anything that pulls in a heavy native build chain on Termux).
- Adding a new LLM call to any pipeline (cost impact).
- Changing a prompt in `prompts/` materially.
- Changing the public API surface (`/api/*` paths or response shapes).
- Changing the data model (`metadata.db` schema, file formats).
- Anything that touches the publisher pipeline's redaction logic.
- Anything that would change Hugo output structure (since it affects the public site).

Don't ask before:

- Refactoring code that's already correct.
- Adding tests.
- Updating docs.
- Fixing bugs in non-publishing code paths.
- Renaming local variables.

When asking, propose a default. "I want to do X because Y; any objection?" beats "What should I do?"

## Things to never do

- **Never** publish to the Hugo repo without the reviewer pass having approved the content. There is no "just this once."
- **Never** delete content from a project document. Append-only includes the case where the content looks wrong.
- **Never** commit `config.toml`, API keys, or anything from `~/flightrecorder/` (sessions, documents) to git. `config.toml` is in `.gitignore`; `pricing.toml` is committed.
- **Never** hard-code paths. Use `$FLIGHTRECORDER_HOME` or the config.
- **Never** add a feature that wasn't in the spec without asking. Scope creep is the enemy.
- **Never** assume LLM output is well-formed. Parse defensively, fall back to retry, fall back to skipping the session.

## Files in the flightrecorder source tree

flightrecorder lives inside the merged `daniel90mm.github.io` repo at `flightrecorder/`. The Hugo site lives beside it at `src/`; runtime data still lives outside the repo on pa-server.

```
flightrecorder/
├── AGENTS.md                     # this file
├── CLAUDE.md                     # copy of AGENTS.md
├── README.md                     # public-facing intro
├── flightrecorder-spec.md        # canonical design doc
├── DESIGN_PRINCIPLES.md          # the "why" behind structural choices
├── RESEARCH_LOG.md               # findings, decisions, open questions
├── IDEAS_TRAIL.md                # future ideas, deferred features
├── SETUP.md                      # Termux install + autostart instructions
├── prompts/                      # versioned LLM prompts
│   ├── brainstorm-system.md
│   ├── tagger.md
│   ├── idea-capture.md
│   ├── matchmaker.md
│   ├── curator.md
│   ├── reviewer.md
│   └── composer.md
├── src/
│   ├── backend/                  # FastAPI app
│   ├── frontend/                 # Svelte SPA
│   ├── cli/                      # the `fr` command
│   └── data/
│       └── pokemon.py            # the 1025 names
├── tests/
│   ├── unit/
│   ├── integration/
│   └── adversarial/              # doxxing inputs
├── scripts/
│   ├── setup-termux.sh           # one-shot pa-server setup
│   ├── sync-projects.sh          # laptop-side, posts to pa-server
│   └── dev.sh                    # local dev runner
├── handoffs/                     # session handoffs
├── consults/                     # decision consults
└── docs/                         # design notes, architecture diagrams
```

Two paths NOT in the merged site/source repo, but on pa-server:

- `~/flightrecorder/config.toml` — secrets, paths, thresholds. Local only.
- `~/flightrecorder/` — all runtime data. Backed up separately by Daniel.

## First session checklist

Any agent picking up this project for the first time:

1. Read `flightrecorder-spec.md` end-to-end. Yes, all of it.
2. Read this file (AGENTS.md) end-to-end.
3. Read the most recent handoff in `handoffs/` if any exists.
4. Check `RESEARCH_LOG.md` for current state and open questions.
5. Identify which build-order step is current.
6. Propose a plan for the next chunk of work.
7. Ask Daniel to confirm before starting.

If steps 1-4 take longer than the chunk of work, that's normal and correct. The cost of building the wrong thing is higher than the cost of reading.

## A note on the museum half

The current `daniel90mm.github.io` is described in user-facing terms as a "showcase portfolio" and "museum of creativity." flightrecorder produces the *flight recorder* half (live log, wall, project working state). The *museum* half (curated project writeups) is deliberately out of scope for v1.

Don't build museum features. Don't fold museum concerns into project documents. The two halves coexist on the same site but are produced by different workflows. Stay in the flight recorder lane.
