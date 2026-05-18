# Idea-capture parser validation

What `parse_idea_operations()` in `src/backend/flightrecorder/idea_capture.py`
accepts and rejects.

## Accepts

- A JSON array with **one to eight** elements (max of eight, `MAX_IDEA_OPERATIONS = 8`).
- Each element is a JSON object with a `"type"` field.
- `"type": "project_append"` requires non-empty strings for `project_ref`,
  `section`, and `content`. `section` must be one of:
  `Problem`, `Current state`, `Decisions made`, `Open questions`, `TODOs`,
  `Ideas`. `project_ref` must survive sanitization (not reduce to empty).
- `"type": "spaghetti"` requires a non-empty string for `content`, and
  `tags` / `topics` as lists of non-empty strings.

## Rejects

- Output that is not valid JSON.
- Output that is not a JSON array.
- More than eight operations (padding/babbling guard).
- Any operation with an unknown `"type"` value.
- Missing or empty `project_ref`, `section`, or `content` on a
  `project_append`.
- An unknown section name on a `project_append`.
- Missing or empty `tags`, `topics`, or `content` on a `spaghetti`.
- Any non-string entry in `tags` or `topics` lists.

## Rationale

The parser is intentionally strict. LLM output can drift; a loose parser
would silently accept broken operations. The prompt in
`prompts/idea-capture.md` specifies the expected shape, and the parser
validates it exactly.
