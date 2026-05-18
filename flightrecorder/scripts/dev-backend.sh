#!/usr/bin/env sh
set -eu

exec uvicorn "flightrecorder.app:create_app" --factory --host "127.0.0.1" --port "8000" --reload
