# Core progress

Percentages based on `docs/BUILD_STATUS.md`. Linear components only;
integration and polish are not represented in per-component numbers.

## Individual estimates

| Area | % | Status |
|------|---|--------|
| Backend skeleton | 85% | mostly done, Termux verification deferred |
| Session storage | 100% | done, including approved `/api/sessions*` routes |
| Cost guard | 90% | provider-call guard exists and is wired into chat and extraction; budget API remains unbuilt |
| Project documents | 70% | append-only helpers, tests, extraction route, and documents git auto-commit exist |
| Idea capture | 75% | provider call, parser, apply, spaghetti writer, cost logging, and round-trip coverage exist |
| Chat | 85% | SSE endpoint exists with storage, budget preflight, and cost logging; frontend integration is not built |
| Frontend | 0% | not started |
| Tagger | 5% | prompt exists, no backend code |
| Pokemon mapping | 25% | deterministic baseline exists with placeholder table; full data source deferred |
| Matchmaker | 35% | structural endpoint and rejection-bias framework exist; LLM scorer not wired |
| Publisher | 20% | fail-closed pipeline framework and adversarial fixtures exist; daily job/Hugo writes not built |
| Curator/reviewer | 15% | structural interfaces and Null stages exist; real LLM passes not wired |
| Termux | 30% | dorm-assistant pattern inspected, laptop helper drafted, not run on phone |

## Overall v1

The percentage is not an average of the above - many components are zero-effort
integration only (frontend, polish) or blocked on other components (tagger,
matchmaker, publisher depend on provider calls; frontend depends on API).

The honest summary: the storage, document, chat, extraction, and cost
primitives are solid enough to start proving the end-to-end loop. The remaining
gap is no longer "no provider calls"; it is full pipeline integration,
frontend/dogfooding, Termux verification, and the high-risk publisher/redaction
work.
