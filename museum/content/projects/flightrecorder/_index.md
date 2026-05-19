---
title: Flightrecorder
summary: Local-first brainstorming system that turns messy sessions into append-only project notes, a spaghetti idea wall, budget-aware provider calls, and delayed public publishing.
status: live
started: 2026-05
stack: [FastAPI, SQLite, Hugo, static frontend]
repo: https://github.com/Daniel90mm/Daniel90mm.github.io/tree/main/flightrecorder
---

Flightrecorder is the system now being built behind this site: a private,
local-first brainstorming tool that records exploratory sessions, extracts the
useful parts, and routes them into two places:

- project documents for ideas that already have a home;
- a spaghetti wall for loose ideas that should not disappear.

{{< fig src="/images/flightrecorder-dogfood-ui.png" caption="current dogfood UI: create a session, watch budget state, and inspect extracted documents/spaghetti" alt="flightrecorder dogfood browser UI" />}}

## What works now

The MVP loop is in place locally:

1. Create or reopen a session.
2. Chat through the backend streaming endpoint.
3. Run idea extraction on the transcript.
4. Inspect generated project documents and spaghetti ideas in the browser.
5. Watch provider spend through the budget panel before and after calls.

There is also an offline prototype provider now, so this loop can run without
API keys while the real Anthropic config path is being hardened.

The public site is still static Hugo. Flightrecorder is the private runtime
that should eventually decide what is safe and worth publishing here.

## Why it matters

This site should stop being a manually curated museum and become the visible
edge of a working thought system. The private backend captures the messy work;
the public Hugo site shows the polished, delayed, redacted output.

The current target is not a beautiful marketing surface. It is a real dogfood
loop that can survive daily use on a laptop and then on the Termux phone
deployment target.
