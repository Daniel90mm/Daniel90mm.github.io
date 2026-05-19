# Runtime data safety

The merged repo (`daniel90mm.github.io`) contains both source code and a Hugo
site. Runtime data lives outside the repo on pa-server. These files and
directories must **never** be committed to the merged site/source repository.

## Never-commit checklist

- `config.toml` - contains provider API keys, paths, thresholds. In
  `.gitignore`.
- `.env.search.local` - contains the Tavily (or other search) API key.
  Never commit. Use `.env.search.local.example` as a template.
- `metadata.db` - sqlite database with session metadata, idea indices, cost
  logs.
- `sessions/` - raw session transcripts (contain real names, half-thoughts).
- `documents/` - project documents (has its own git repo).
- `spaghetti/` - unattached idea files.
- `matches/` - matchmaker proposal batches.
- `journey/` - rendered idea journey artifacts.
- `pending/` - curated snippets awaiting 24h delay.
- `published/` - mirror of what got published.
- `logs/` - publisher and backend logs.

## Configuration

- `flightrecorder/.gitignore` covers the `flightrecorder/` source tree for
  generated files (`.venv/`, `.pytest_cache/`, `__pycache__`, `*.egg-info/`).
- `config.toml` is in the root `.gitignore` since it lives at the same level
  as the flightrecorder source tree.
- `pricing.toml` is committed (no secrets), but real rates should come from
  provider docs.

## The boundary

- **Repo:** `~/hugo-site/flightrecorder/` (source) + `~/hugo-site/src/`
  (Hugo content produced by publisher)
- **Runtime data:** `~/flightrecorder/` (not in any repo except documents/
  which has its own git)
