# Build status

Rows for spec section 19 build-order steps 1--20.

| Step | Name | Status | Notes |
|------|------|--------|-------|
| 1 | Backend skeleton | mostly done | FastAPI, sqlite schema, config, providers. Termux verification deferred. |
| 2 | Session storage | done | File reader/writer, sqlite index, image storage, serializers, and approved `/api/sessions*` routes implemented. |
| 3 | Chat endpoint | not started | |
| 4 | Frontend skeleton | not started | |
| 5 | PWA manifest + service worker | not started | |
| 6 | Voice input | not started | |
| 7 | Tagger | not started | |
| 8 | Project documents + idea capture | in progress | Append-only project document helpers and tests exist. Idea-capture LLM operation parsing and documents git auto-commit not wired. |
| 9 | Spaghetti capture | not started | |
| 10 | Pokemon mapping | not started | |
| 11 | Matchmaker | not started | |
| 12 | Curator + reviewer + composer | not started | |
| 13 | Daily publisher | not started | |
| 14 | Hugo integration | not started | |
| 15 | Project registry | not started | |
| 16 | Implementation marking UI | not started | |
| 17 | Budget tracking | in progress | Costs module can log calls, sum windows, parse pricing.toml, compute EUR cost, and evaluate warn/hard-stop thresholds. Kill switch not wired yet. |
| 18 | Polish | not started | |
| 19 | Termux setup checklist | in progress | Dorm-assistant pattern documented and laptop-side helper drafted. Not run on phone. |
| 20 | Ship and dogfood | not started | |
