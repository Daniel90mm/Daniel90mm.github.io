# Termux phone pattern from dorm-assistant

Source inspected: `/home/daniel/Documents/Projekter/dorm-assistant`.

The dorm-assistant phone setup is laptop-driven and intentionally simple:

- The laptop controls the phone over SSH on Termux port `8022`.
- `scripts/termux-phone.sh` defines `PHONE_HOST`, `PHONE_USER`, `PHONE_PORT`,
  and `PHONE_KEY`, then wraps `ssh` and `scp`.
- Services are plain Python processes started with `nohup`, not systemd.
- Long-running processes call `termux-wake-lock` before starting.
- Logs live in `~/logs/*.log`.
- Pids live in `~/*.pid`.
- Start commands kill the old pid first, then start one new background process.
- Termux:Boot is used by writing executable scripts under `~/.termux/boot/`.
- The boot script starts `sshd`, takes a wake lock, creates `~/logs`, then uses
  a local `start_once()` helper to avoid duplicate daemons.

Important dorm-assistant details to reuse:

```sh
termux-wake-lock 2>/dev/null || true
sshd 2>/dev/null || true
mkdir -p "$HOME/logs"
nohup env ... python "$HOME/service.py" >"$HOME/logs/service.log" 2>&1 &
echo $! > "$HOME/service.pid"
```

For flightrecorder, adapt this pattern rather than introducing systemd or a
desktop Linux service manager:

- laptop-side helper: `scripts/termux-phone.sh`
- phone checkout: `~/hugo-site/`
- source: `~/hugo-site/flightrecorder/`
- runtime data: `~/flightrecorder/`
- logs: `~/logs/flightrecorder-backend.log`
- pid: `~/flightrecorder-backend.pid`
- boot script: `~/.termux/boot/start-flightrecorder.sh`

The dorm-assistant repo does not use `termux-services` for these daemons yet.
It uses Termux:Boot plus pid files. That is probably the lowest-friction first
flightrecorder deployment too. A later move to `termux-services` can happen
after the app is stable.
