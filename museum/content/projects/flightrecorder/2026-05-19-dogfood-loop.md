---
title: First Visible Dogfood Loop
date: 2026-05-19
---

The first usable loop is now visible enough to judge from the outside:

- FastAPI serves the static dogfood frontend.
- Sessions can be created and loaded from the browser.
- Chat responses stream over SSE.
- Images can be uploaded into sessions.
- Extraction writes project documents and spaghetti ideas.
- Read-only APIs expose those artifacts back to the browser.
- Budget and calls ledger panels track provider spend.
- A local `prototype` provider runs the same loop without API keys.
- A one-command launcher starts everything from fresh state.
- A fail-closed publish preview panel shows what would be published (currently
  always rejected; real curator/reviewer stages are next).
