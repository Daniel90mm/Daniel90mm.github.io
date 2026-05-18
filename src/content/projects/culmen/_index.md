---
title: Culmen
summary: A visual learning tracker that organises knowledge as a pyramid — foundations at the base, advanced topics on top. See exactly which prerequisites need shoring up before the next course.
status: live
started: 2026-02
stack: [Electron, TypeScript, SQLite]
---

Culmen treats a curriculum as a directed graph of prerequisites and renders it as a pyramid. Each node carries evidence — problems solved, notes written, tests passed — and the UI exposes the **bridges**: the prerequisite edges that are currently load-bearing for whatever target you've pinned at the apex.

The thesis is simple: most "I'm stuck on advanced topic X" failures are actually a weak foundation two layers down. Culmen makes that legible without you having to ask.

## Why

I kept hitting the same wall in self-study — bouncing off advanced material because of a shaky foundation I couldn't name. Existing trackers are flat (Anki) or rigid (curriculum apps). Neither shows you the *structural* gap.

## Where it is now

A working Electron app on Linux and Windows. Pyramid renderer is stable; the evidence-tracking layer is being rewritten to use a content-addressed store so notes can move between nodes without losing history.
