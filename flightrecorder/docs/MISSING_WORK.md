# Missing work

Snapshot from `docs/BUILD_STATUS.md`. Every step not listed below is done or in
progress.

- Done: **1** of 20 (step 2 session storage)
- Mostly done: **1** (step 1, backend skeleton)
- In progress: **3** (step 8 project documents, step 17 budget tracking, step 19 Termux setup)
- Not started: **15**

## Not started

| Step | Name |
|------|------|
| 3 | Chat endpoint |
| 4 | Frontend skeleton |
| 5 | PWA manifest + service worker |
| 6 | Voice input |
| 7 | Tagger |
| 9 | Spaghetti capture |
| 10 | Pokemon mapping |
| 11 | Matchmaker |
| 12 | Curator + reviewer + composer |
| 13 | Daily publisher |
| 14 | Hugo integration |
| 15 | Project registry |
| 16 | Implementation marking UI |
| 18 | Polish |
| 20 | Ship and dogfood |

## Open

Step 8 has append-only project document helpers, strict idea operation parsing,
spaghetti file writing, sqlite indexing, and documents git auto-commit. The
idea-capture LLM call is not wired yet.

Step 17 has budget logging, sentinel enforcement, and provider-call guard
primitives. Real provider SDK calls are not yet wired.

Step 19 has a documented Termux phone pattern and helper draft. It has not been
run against pa-server.
