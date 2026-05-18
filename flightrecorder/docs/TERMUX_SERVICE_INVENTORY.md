# Termux service inventory

Design inventory of future Termux services from spec sections 4 and 13. Mark
as planning only - do not create runit files or touch the phone.

## Services

### 1. Backend daemon
- FastAPI via uvicorn, `--host 127.0.0.1 --port 8000`.
- Autostart via Termux:Boot (`~/.termux/boot/start-flightrecorder.sh`).
- Laptop-side helper: `scripts/termux-phone.sh start-backend`.
- Abstraction: nohup + pid file (`~/flightrecorder-backend.pid`).
- Log: `~/logs/flightrecorder-backend.log`.

### 2. Daily publisher job
- Cron (scheduled task, not termux-services daemon).
- Runs `fr publish` at 03:00.
- Wrapped in `termux-wake-lock` / `termux-wake-unlock` for the duration.
- Checks `pause` and `budget` kill switch files before running.

### 3. Weekly matchmaker job
- Cron, Sundays at 04:00 (or threshold-triggered at 20+ unmatched ideas).
- Runs `fr match`.
- Also wrapped in wake-lock.
- Produces match proposal batches in `matches/pending/`.

## Wake-lock usage

Long-running jobs (publisher, matchmaker) must hold `termux-wake-lock` while
running to prevent Android from killing the process mid-job. Release with
`termux-wake-unlock` after completion.

## Service manager

The spec (section 4) notes `termux-services` (runit-based). The current
dorm-assistant pattern uses Termux:Boot + pid files + nohup, which is
simple and proven. A future move to `termux-services` is deferred.

## Not implemented

No runit files, no cron entries, no wake-lock wrappers exist.
