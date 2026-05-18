---
title: Wi-Fi Guardian
summary: Fedora-focused defensive Wi-Fi watcher — when a new network goes active, it runs a bounded safety check, files a report, and pings the desktop.
status: live
started: 2026-03
---

Connecting to an unknown Wi-Fi is a moment of trust. Wi-Fi Guardian sits in the background, notices when a new network becomes active, runs a quick assessment (captive portal detection, suspicious gateway behaviour, etc.), and drops a structured report under `~/.local/state/wifi-guardian/`. A desktop notification surfaces the result so you can act before doing anything sensitive.

Bounded by design — never blocks the connection, never phones home.
