# Session close pipeline plan

The intended sequence from existing building blocks. Marks which pieces exist
and which are missing.

## Sequence

```
1. close session -> frontend calls POST /api/sessions/{id}/close
2. tag session -> run tagger prompt on transcript (MISSING)
3. extract ideas -> run idea-capture prompt on transcript (MISSING)
4. parse operations -> parse_idea_operations() (EXISTS)
5. apply operations -> apply_idea_operations() (EXISTS)
6. project document append -> append_to_project_document() (EXISTS)
7. spaghetti write -> write_spaghetti_idea() (EXISTS)
8. mark extracted -> mark_session_extracted() (EXISTS)
9. commit documents -> commit_documents_repo() (EXISTS)
```

## What exists

Steps 4--9: all parser and file-writer functions exist and are tested.
`apply_idea_operations()` can take parsed operations, write project appends and
spaghetti files, mark the session extracted, and optionally commit documents.

## What is missing

Steps 2--3: the tagger and idea-capture LLM prompts are versioned in
`prompts/` but no backend code calls them yet. The session close endpoint
does not exist. `ProviderCallGuard` exists but the LLM call path is not wired.

## Pre-requisites

- Provider SDK calls must be wired (not done).
- `ProviderCallGuard` must be called around both LLM calls.
- API contract for `POST /api/sessions/{id}/close` is not drafted.

## Blockers before implementation

1. **chat endpoint approval** - Daniel must approve the chat SSE contract
   (`docs/CHAT_API_CONTRACT_DRAFT.md`).
2. **provider SDK execution** - `ProviderCallGuard.check_before_call()` and
   `record_usage()` must be wired around actual provider SDK calls.
3. **idea-capture LLM call** - the prompt exists (`prompts/idea-capture.md`)
   but no backend code calls the LLM yet.
4. **retry/error semantics** - on malformed LLM output, the pipeline must fail
   closed (no documents/spaghetti written, session stays available for retry).
   The retry policy is drafted in `docs/IDEA_CAPTURE_RETRY_POLICY.md`.
5. **tagger LLM call** - same as idea-capture: prompt exists, no backend code
   calls it yet.
