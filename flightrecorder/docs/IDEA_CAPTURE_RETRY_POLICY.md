# Idea-capture retry policy

Proposed fail-closed behavior for malformed idea-capture LLM output. The parser
(`parse_idea_operations`) already behaves this way; the future LLM execution
path should match.

## Policy

```
parse error -> no document append -> no spaghetti write ->
session remains available for retry via fr recapture or
manual inspection via fr review
```

When the idea-capture LLM returns output that the parser rejects:
1. `parse_idea_operations()` raises `IdeaCaptureError`.
2. No project documents are modified. No spaghetti files are written.
3. The session's `extracted` flag remains `false` in sqlite.
4. The session stays in the "unprocessed" pool for retry.
5. The raw LLM output is logged (provider response, not stored permanently).

## Rationale

- Append-only project documents are sacred: never write unvalidated content.
- A silent skip would lose ideas. A best-effort write would drift the
  document structure. Failing closed and surfacing for human review is the
  only safe option.
- Costs are already spent when the LLM returns; the only choice is whether to
  trust broken output. The answer is no.

## Not yet proven

The code currently only exercises the parser against hand-crafted JSON in tests.
When real LLM output feeds the parser, additional retry logic (re-prompt once,
then give up) may be warranted. This policy statement is the baseline, not the
final word.
