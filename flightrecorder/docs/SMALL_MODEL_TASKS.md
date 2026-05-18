# Small-model task queue

These tasks are intentionally narrow. Each task should be doable by a smaller
model without broad architecture decisions. Do one task at a time, keep edits
inside the listed files, and run the smoke test before handing back.

Do not change prompts, public Hugo output, API shapes, sqlite schema, or
publisher redaction behavior unless the task explicitly says so.

## Completed ledger

The following small-model tasks are done and should not be repeated unless a
regression is found:

| ID | Result |
|----|--------|
| S01 | Prompt/spec drift report in `docs/PROMPT_DRIFT.md`. |
| S02 | Termux dependency note in `docs/TERMUX_DEPENDENCIES.md`. |
| S03 | Config fixtures in `tests/fixtures/config/`. |
| S04 | SQLite schema smoke script. |
| S05 | README quickstart after backend skeleton. |
| S06 | Hugo workflow path smoke script. |
| S07 | Session storage smoke script. |
| S08 | Draft session API contract. |
| S09 | Runtime context smoke script. |
| S10 | README quickstart factory correction. |
| S11 | Storage edge-case tests. |
| S12 | Config fixture tests. |
| S13 | Build-order status doc. |
| S14 | API call logging smoke script. |
| S15 | Pricing file format note. |
| S16 | Backend health smoke script. |
| S17 | Serializer asset path regression test. |
| S18 | Pricing smoke script. |
| S19 | API contract review checklist. |
| S20 | Cost boundary tests, taken by senior agent during cleanup. |
| S21 | Research log checkpoint. |
| S22 | Smoke command index. |
| S23 | Budget smoke script. |
| S24 | Missing-work status doc. |
| S25 | Config budget threshold validation tests. |
| S26 | API draft examples consistency pass, completed by senior agent. |
| S27 | Package import smoke. |
| S28 | README missing approval warning. |
| S29 | Project document smoke script. |
| S30 | Project document README note. |
| S31 | Small-model queue smoke sync. |
| S32 | Project document filename tests. |
| S33 | Missing-work snapshot sync. |
| S34 | API contract review sync. |
| S35 | Session API smoke script, completed by senior agent. |
| S36 | Session API README examples, completed by senior agent. |
| S37 | API pagination validation tests, completed by senior agent. |
| S39 | Termux docs sync, completed by senior agent. |
| S40 | Session API smoke command sync, completed by senior agent. |
| S41 | Missing-work snapshot after API completion, completed by senior agent. |

## Active queue

Pick from the top unless Daniel or the senior agent says otherwise.

## S38 - Termux phone helper draft

Where:
- `flightrecorder/scripts/termux-phone.sh`

What:
- Draft a laptop-side helper inspired by dorm-assistant with commands:
  `shell`, `exec`, `status`, and `install-boot`.
- The boot script should start only the backend, not publisher cron.
- Do not run it against the phone.

Why:
- The existing phone workflow is SSH/SCP plus Termux:Boot, not systemd.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
bash -n scripts/termux-phone.sh
grep -q 'termux-wake-lock' scripts/termux-phone.sh
LC_ALL=C grep -n '[^ -~]' scripts/termux-phone.sh && exit 1 || true
```

## S42 - API smoke route status docs

Where:
- `flightrecorder/docs/BUILD_STATUS.md`
- `flightrecorder/docs/MISSING_WORK.md`

What:
- Confirm step 2 is marked done and `/api/sessions*` is no longer described as
  blocked.
- Documentation-only.

Why:
- The API contract was approved and implemented; old blocker wording should not
  survive.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
grep -q 'Done: **1**' docs/MISSING_WORK.md
! grep -q 'blocked on Daniel approval' docs/MISSING_WORK.md
LC_ALL=C grep -n '[^ -~]' docs/BUILD_STATUS.md docs/MISSING_WORK.md && exit 1 || true
```

## S43 - Termux helper smoke doc

Where:
- `flightrecorder/docs/TERMUX_PHONE_PATTERN.md`

What:
- After `scripts/termux-phone.sh` exists, add the exact command for checking
  its syntax and installing the boot script.
- Documentation-only; do not run against the phone.

Why:
- The helper should remain dry-run safe until Daniel explicitly wants phone
  deployment.

Smoke test:

```sh
cd /home/daniel/Documents/Projekter/Daniel90mm.github.io/flightrecorder
grep -q 'bash -n scripts/termux-phone.sh' docs/TERMUX_PHONE_PATTERN.md
LC_ALL=C grep -n '[^ -~]' docs/TERMUX_PHONE_PATTERN.md && exit 1 || true
```
