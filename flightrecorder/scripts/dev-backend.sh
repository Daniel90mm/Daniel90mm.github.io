#!/usr/bin/env sh
set -eu

ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
cd "$ROOT"

if [ -z "${FLIGHTRECORDER_CONFIG:-}" ]; then
    if [ -f "$ROOT/config.local.toml" ]; then
        export FLIGHTRECORDER_CONFIG="$ROOT/config.local.toml"
    elif [ -f "$ROOT/config.toml" ]; then
        export FLIGHTRECORDER_CONFIG="$ROOT/config.toml"
    else
        set -- "$ROOT"/config.*.local.toml
        if [ "$#" -eq 1 ] && [ -f "$1" ]; then
            export FLIGHTRECORDER_CONFIG="$1"
        fi
    fi
fi

if [ -x "$ROOT/.venv/bin/uvicorn" ]; then
    UVICORN="$ROOT/.venv/bin/uvicorn"
elif command -v uvicorn >/dev/null 2>&1; then
    UVICORN="$(command -v uvicorn)"
else
    echo "ERROR: uvicorn not found. Run: python -m venv .venv && . .venv/bin/activate && pip install -e '.[dev]'" >&2
    exit 127
fi

exec "$UVICORN" "flightrecorder.app:create_app" --factory --host "127.0.0.1" --port "8000" --reload
