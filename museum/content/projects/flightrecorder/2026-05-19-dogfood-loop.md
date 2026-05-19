---
title: First Visible Dogfood Loop
date: 2026-05-19
---

The first usable loop is now visible enough to judge from the outside:

- FastAPI serves the static dogfood frontend.
- Sessions can be created and loaded from the browser.
- Chat responses stream over SSE.
- Extraction writes project documents and spaghetti ideas.
- Read-only APIs expose those artifacts back to the browser.
- Budget status is visible before real-provider dogfooding.
- A local `prototype` provider runs the same loop without API keys.

The next work is making real-provider setup obvious and hard to misconfigure:
example config, pricing smoke, runtime readiness, and a Termux checklist.
