# Pricing file format

Expected `pricing.toml` shape for per-model API rates. This file lives
alongside `config.toml` at `$FLIGHTRECORDER_HOME/pricing.toml` and is
loaded by the cost-logging module to compute `cost_eur` from token counts.

All rates below are zero placeholders. They document shape only.

## Shape

```toml
[models."claude-haiku-4-5"]
provider = "anthropic"
input_per_1k = 0.0
output_per_1k = 0.0
cached_per_1k = 0.0
currency = "USD"

[models."gpt-5-mini"]
provider = "openai"
input_per_1k = 0.0
output_per_1k = 0.0
cached_per_1k = 0.0
currency = "USD"

[models."gemini-2.5-pro"]
provider = "google"
input_per_1k = 0.0
output_per_1k = 0.0
cached_per_1k = 0.0
currency = "USD"

[models."whisper-1"]
provider = "openai"
input_per_1k = 0.0
output_per_1k = 0.0
cached_per_1k = 0.0
currency = "USD"

[exchange_rates_to_eur]
EUR = 1.0
USD = 0.0
```

- Rates are per **1k tokens** (or per minute for audio models like Whisper,
  in which case `output_per_1k` holds the per-minute rate).
- `cached_per_1k` is the rate when context caching or prompt caching applies
  to a given token.
- Currency must be consistent within a provider group. Conversion to the
  budget currency happens at cost-log time.

**Do not guess prices.** Every rate above is a placeholder. Before committing
`pricing.toml` to the run-data directory, verify each rate against the
provider's current published pricing page. Pricing changes over time and
provider pages are authoritative. Verify exchange rates at the same time,
because `metadata.db.api_calls.cost_eur` is stored in EUR.

## Cost formula

```
cost_eur = (
    input_tokens / 1000 * input_per_1k
    + output_tokens / 1000 * output_per_1k
    + cached_tokens / 1000 * cached_per_1k
) * usd_to_euro_rate
```
