# Setup

Termux setup is build order step 19. This file is a placeholder until the
backend, frontend, publisher, and cron commands exist.

Known deployment shape:

- Clone `github.com/Daniel90mm/Daniel90mm.github.io` to `~/hugo-site/`.
- Run flightrecorder source from `~/hugo-site/flightrecorder/`.
- Store runtime data in `~/flightrecorder/`.
- Keep `~/flightrecorder/documents/` as its own git repo.
- Use the dorm-assistant phone pattern first: SSH from laptop into Termux,
  `nohup` Python processes, pid files, logs in `~/logs`, and Termux:Boot
  scripts in `~/.termux/boot/`.
- Backend boot script target: `~/.termux/boot/start-flightrecorder.sh`.
- Wrap long cron jobs with `termux-wake-lock`.
- Do not use systemd.

See `docs/TERMUX_PHONE_PATTERN.md` for the inspected dorm-assistant details.
