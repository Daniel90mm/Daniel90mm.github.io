# Agent Instructions

## Completion Hygiene

After each meaningful, verified change, commit and push the work. Stage only
files that belong to that change, and leave unrelated local edits alone.

## Flightrecorder Extraction Prompting

When changing Flightrecorder spaghetti-item extraction, treat Daniel's judgment
about "good ideas" as product context that must be elicited, not guessed. If the
prompt, examples, or acceptance criteria are underspecified, ask Daniel for
more examples or context before broadening extraction behavior.

Prefer diagnostic questions that collect concrete positive, negative, and
borderline transcripts. Capture the distinction between durable ideas, app
operation chatter, project TODOs, and assistant-only suggestions. Keep extractor
changes conservative: false negatives are better than permanent junk notes.


<!-- BEGIN MANAGED: agent-delegation -->
## DeepSeek Delegation

This repository may use DeepSeek only through `agent-delegate`.

Before delegating, write a task file with YAML front matter declaring `provider`, `topic`, `allowed_read`, `allowed_write`, and `output`. Run `agent-delegate deepseek --dry-run <task-file>` before the first real call.

Use DeepSeek only for bounded, reviewable work. Do not call DeepSeek directly, and do not send secrets, credentials, private logs, compliance-sensitive material, or files outside the declared allowlist.

DeepSeek output is advisory. The active Codex/Claude agent owns final review, tests, edits, and commits.
<!-- END MANAGED: agent-delegation -->
