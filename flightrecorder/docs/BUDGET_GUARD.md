# Budget hard-stop sentinel

The `budget` file at `$FLIGHTRECORDER_HOME/budget` is the hard-stop kill
switch for paid LLM calls.

## Sentinel lifecycle

- **Written by** `enforce_monthly_budget()` when `monthly_cost_eur >= hard_stop_eur`.
  The file contains key=value lines: `status=hard_stop`, current cost, and
  threshold values.
- **Checked by** `is_budget_hard_stop_active()`. Any code path that makes paid
  provider calls must check this before calling.
- **do not auto-clear** (the sentinel persists until explicitly removed). When spend drops below the hard-stop threshold (e.g., a
  new month begins), the sentinel is *not* automatically removed. It persists
  until explicitly cleared.
- **Cleared explicitly** via `clear_budget_hard_stop()`. The spec also calls
  for a future `fr budget clear-stop` CLI command; that command is not wired
  yet.

## Why not auto-clear

A hard-stop means "someone should look at this." Auto-clearing on month
rollover hides the fact that the budget was hit. The sentinel stays until
Daniel decides to remove it.

## Enforce function

`enforce_monthly_budget(runtime_home, connection, now, warn_at_eur, hard_stop_eur)`:
1. Evaluates current monthly spend against thresholds.
2. If `should_stop`: writes the `budget` sentinel, returns `hard_stop_active=True`.
3. If `should_warn` or `ok`: does NOT clear an existing sentinel. Just returns
   whether one is already present.
