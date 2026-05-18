# Core progress

Percentages based on `docs/BUILD_STATUS.md`. Linear components only;
integration and polish are not represented in per-component numbers.

## Individual estimates

| Area | % | Status |
|------|---|--------|
| Backend skeleton | 85% | mostly done, Termux verification deferred |
| Session storage | 100% | done, including approved `/api/sessions*` routes |
| Cost guard | 80% | provider-call guard exists, not wired into any paid-call path |
| Project documents | 60% | append-only helpers and tests done, idea-capture LLM parsing exists, LLM call not wired |
| Idea capture | 40% | parser and apply exist, spaghetti writer exists, but LLM prompt not called |
| Chat | 5% | contract draft only, requires Daniel approval |
| Frontend | 0% | not started |
| Tagger | 5% | prompt exists, no backend code |
| Pokemon mapping | 0% | not started |
| Matchmaker | 5% | prompt exists, input contracts documented, no backend code |
| Publisher | 0% | not started, adversarial fixture categories inventoried |
| Curator/reviewer | 0% | not started, doxxing fixture categories inventoried |
| Termux | 30% | dorm-assistant pattern inspected, laptop helper drafted, not run on phone |

## Overall v1

The percentage is not an average of the above - many components are zero-effort
integration only (frontend, polish) or blocked on other components (tagger,
matchmaker, publisher depend on provider calls; frontend depends on API).

The honest summary: the storage, document, and cost primitives are solid. The
gap between primitives and an end-to-end brainstorm-to-publish loop is still
large because provider SDK calls are not wired and the chat endpoint is not
implemented.
