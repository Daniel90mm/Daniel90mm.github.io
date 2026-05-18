# Build status

Rows for spec section 19 build-order steps 1--20.

| Step | Name | Status | Notes |
|------|------|--------|-------|
| 1 | Backend skeleton | mostly done | FastAPI, sqlite schema, config, providers. Termux verification deferred. |
| 2 | Session storage | done | File reader/writer, sqlite index, image storage, serializers, and approved `/api/sessions*` routes implemented. |
| 3 | Chat endpoint | done | SSE route implemented at `POST /api/sessions/{session_id}/messages`, with budget preflight and cost logging. |
| 4 | Frontend skeleton | not started | |
| 5 | PWA manifest + service worker | not started | |
| 6 | Voice input | not started | |
| 7 | Tagger | not started | |
| 8 | Project documents + idea capture | in progress | Append-only docs, spaghetti file writing, strict operation parsing, sqlite indexing, documents git auto-commit, extraction route, idea-capture provider call, and round-trip integration coverage exist. |
| 9 | Spaghetti capture | in progress | Spaghetti markdown writing and sqlite indexing exist through idea extraction. Listing/decision surfaces are not built. |
| 10 | Pokemon mapping | in progress | Deterministic pseudonymization baseline exists with a placeholder table. Full 1025-name data source is deferred. |
| 11 | Matchmaker | in progress | Structural matcher and `POST /api/matchmaker/run` exist with fail-closed `NullScorer`. LLM scorer not wired. |
| 12 | Curator + reviewer + composer | in progress | Publisher structural framework exists with fail-closed Null stages and adversarial fixtures. Real curator/reviewer/composer LLM calls not wired. |
| 13 | Daily publisher | not started | |
| 14 | Hugo integration | not started | |
| 15 | Project registry | in progress | Typed loader, unit tests, and fixture smoke exist. No API route; matchmaker/idea-capture still use ad hoc refs. |
| 16 | Implementation marking UI | not started | |
| 17 | Budget tracking | in progress | Costs module can log calls, sum windows, parse pricing.toml, compute EUR cost, evaluate warn/hard-stop thresholds, write/clear the `budget` sentinel, and run provider-call guard. Chat and extraction paths enforce preflight and record usage. |
| 18 | Polish | not started | |
| 19 | Termux setup checklist | in progress | Dorm-assistant pattern documented and laptop-side helper drafted. Not run on phone. |
| 20 | Ship and dogfood | not started | |
