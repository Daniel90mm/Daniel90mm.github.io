# Termux dependencies

Planned Python packages for build order step 1 (backend skeleton). Listed in
`pyproject.toml`.

## Runtime dependencies

| Package | Version | Why |
|---------|---------|-----|
| `anthropic` | >=0.102.0 | Anthropic provider (tagger, idea-capture, matchmaker, curator, composer) |
| `fastapi` | >=0.136.1 | Backend HTTP framework |
| `google-genai` | >=2.4.0 | Google Gemini provider (brainstorm LLM) |
| `openai` | >=2.37.0 | OpenAI provider (reviewer, whisper) |
| `python-multipart` | >=0.0.20 | FastAPI multipart upload parser for image uploads |
| `uvicorn` | >=0.47.0 | ASGI server for FastAPI |

## Dev dependencies

| Package | Version | Why |
|---------|---------|-----|
| `httpx` | >=0.28.1 | Async HTTP test client |
| `pytest` | >=9.0.0 | Test runner |

## Wheel warnings

- Not verified on Termux ARM64 yet.
- Plain `uvicorn` is intentional. Do not switch to `uvicorn[standard]`
  casually; that pulls native extras that are unnecessary for v1.
- `pydantic-core`, `jiter`, and `cryptography` are transitive dependencies
  worth watching during Termux installation.
- `python-multipart` is pure Python and expected to be low risk, but still
  needs the same Termux install check.

Desktop Linux install passed on 2026-05-18. Treat Termux as open until the
commands below pass on pa-server.

## Termux ARM64 verification

Run these commands on pa-server (Termux on Android, ARM64) after cloning:

```sh
# Create a virtualenv (Termux Python path may differ)
python -m venv .venv
source .venv/bin/activate

# Install from pyproject.toml (editable, with dev extras)
pip install -e ".[dev]"

# Verify imports
python -c "
import anthropic; print('anthropic', anthropic.__version__)
import fastapi; print('fastapi ok')
import google.genai; print('google-genai ok')
import openai; print('openai', openai.__version__)
import multipart; print('python-multipart ok')
import uvicorn; print('uvicorn ok')
import httpx; print('httpx ok')
import pytest; print('pytest', pytest.__version__)
print('all imports ok')
"

# Run the test suite
python -m pytest tests/ -v
```
