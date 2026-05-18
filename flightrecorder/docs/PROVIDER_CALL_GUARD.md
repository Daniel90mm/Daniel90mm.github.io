# Provider call guard

Every paid LLM API call passes through `ProviderCallGuard`. This is the single
enforcement point for cost logging and budget discipline.

## Flow

```
1. preflight budget check -> check_before_call()
2. (real provider SDK call - not wired yet)
3. token usage cost computation -> record_usage()
4. api_calls insert -> log_api_call()
5. post-call budget enforcement -> enforce_monthly_budget()
```

## Preflight (`check_before_call`)

Called before the provider SDK call. Evaluates the monthly budget and raises
`BudgetHardStopError` if a hard-stop sentinel is active. This prevents wasting
tokens when the budget is already blown.

## Record usage (`record_usage`)

Called after the provider SDK returns (or after the assistant's response is
fully streamed). Takes a `ProviderUsage` with token counts, computes the EUR
cost from `pricing.toml` rates, inserts one `api_calls` row, and re-enforces
the monthly budget.

If the post-call cost crosses the hard-stop threshold, the budget sentinel is
written *after* the call is logged. The call that breached the budget is still
recorded.

## Validation

- The model must have a pricing entry (`pricing.toml`).
- The pricing entry's `provider` must match the usage's `provider`.
- Token counts must be non-negative integers.

## Not yet wired

`ProviderCallGuard` existence does not mean real provider SDK calls are
wired. The chat endpoint, tagger, idea-capture, matchmaker, curator, and
reviewer paths all need to call `check_before_call()` and
`record_usage()` around their actual LLM calls. Currently only the smoke
test exercises the guard.
