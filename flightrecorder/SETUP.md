# Setup

Termux setup is build order step 19. This file is a placeholder until the
backend, frontend, publisher, and cron commands exist.

Known deployment shape:

- Clone `github.com/Daniel90mm/Daniel90mm.github.io` to `~/hugo-site/`.
- Run flightrecorder source from `~/hugo-site/flightrecorder/`.
- Store runtime data in `~/flightrecorder/`.
- Keep `~/flightrecorder/documents/` as its own git repo.
- Use `termux-services`, not systemd.
- Wrap long cron jobs with `termux-wake-lock`.
