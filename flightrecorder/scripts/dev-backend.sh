#!/usr/bin/env sh
set -eu

ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
cd "$ROOT"

if [ -x "$ROOT/.venv/bin/uvicorn" ]; then
    UVICORN="$ROOT/.venv/bin/uvicorn"
elif command -v uvicorn >/dev/null 2>&1; then
    UVICORN="$(command -v uvicorn)"
else
    echo "ERROR: uvicorn not found. Run: python -m venv .venv && . .venv/bin/activate && pip install -e '.[dev]'" >&2
    exit 127
fi

exec "$UVICORN" "flightrecorder.app:create_app" --factory --host "127.0.0.1" --port "8000" --reload
