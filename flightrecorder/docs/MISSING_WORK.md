# Missing work

Snapshot from `docs/BUILD_STATUS.md`. Every step not listed below is done or in
progress.

- Done: **2** of 20 (step 2 session storage, step 3 chat endpoint)
- Mostly done: **1** (step 1, backend skeleton)
- In progress: **8** (step 8 project documents, step 9 spaghetti capture, step 10 pokemon mapping, step 11 matchmaker, step 12 publisher framework, step 15 project registry, step 17 budget tracking, step 19 Termux setup)
- Not started: **9**

## Not started

| Step | Name |
|------|------|
| 4 | Frontend skeleton |
| 5 | PWA manifest + service worker |
| 6 | Voice input |
| 7 | Tagger |
| 13 | Daily publisher |
| 14 | Hugo integration |
| 16 | Implementation marking UI |
| 18 | Polish |
| 20 | Ship and dogfood |

## Open

Step 8 has append-only project document helpers, strict idea operation parsing,
spaghetti file writing, sqlite indexing, documents git auto-commit, an
extraction route, a wired idea-capture provider call, and round-trip
integration coverage.

Step 9 has spaghetti markdown writing and sqlite indexing through idea
extraction. Listing and decision surfaces are not built.

Step 10 has a deterministic pokemon pseudonymization baseline with a
placeholder table. The full 1025-name data source is deferred.

Step 11 has structural matchmaker code and `POST /api/matchmaker/run` with a
fail-closed `NullScorer`. The LLM scorer is not wired.

Step 12 has publisher pipeline structure with fail-closed Null stages and
adversarial fixtures. Real curator/reviewer/composer LLM calls are not wired.

Step 15 has a typed project registry loader, unit tests, and fixture smoke.
No API route exposes the registry yet; matchmaker and idea-capture still read
project refs ad hoc.

Step 17 has budget logging, sentinel enforcement, and provider-call guard
primitives. Chat and extraction enforce preflight and record usage.

Step 19 has a documented Termux phone pattern and helper draft. It has not been
run against pa-server.
