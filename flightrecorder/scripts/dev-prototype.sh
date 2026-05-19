#!/usr/bin/env sh
set -eu

ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
cd "$ROOT"

CONFIG="$ROOT/config.prototype.toml"
PRICING="$ROOT/pricing.prototype.toml"

if [ ! -f "$CONFIG" ]; then
    echo "ERROR: $CONFIG not found." >&2
    echo "Create config.prototype.toml or copy from config.example.toml." >&2
    exit 1
fi

if [ ! -f "$PRICING" ]; then
    echo "ERROR: $PRICING not found." >&2
    echo "Create pricing.prototype.toml or copy from pricing.example.toml." >&2
    exit 1
fi

export FLIGHTRECORDER_CONFIG="$CONFIG"
exec uvicorn "flightrecorder.app:create_app" --factory --host "127.0.0.1" --port "8000" --reload
