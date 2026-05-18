# Design principles

The detailed product contract is in `flightrecorder-spec.md`. These notes are
the short version for implementation work.

## Priorities

- Idea capture, append-only documents, matchmaker proposals, and adversarial
  publishing are the product. Treat the chat UI as supporting machinery.
- Preserve Daniel's working state. Append to project documents; do not rewrite
  existing bullets or sections.
- Publishing is a privacy boundary. False rejects are acceptable; false
  approvals are not.
- Prefer small, inspectable modules over broad abstractions.

## Interface

- The private app should feel like a working notebook, not a marketing site.
- The public flight-recorder pages should match the existing terminal/TUI
  aesthetic of `daniel90mm.github.io`.
- Avoid analytics, telemetry, and public exposure in v1.
