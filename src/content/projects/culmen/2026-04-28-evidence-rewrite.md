---
title: Rewriting the evidence store
date: 2026-04-28
tags: [refactor, storage]
excerpt: The flat row-per-evidence schema couldn't survive moving notes between nodes. Switching to a content-addressed store with reference edges.
---

The original schema was naive: one row per piece of evidence, with a `node_id` foreign key. Worked for a month, then I tried to reorganise the pyramid and discovered that moving a node meant orphaning or duplicating its evidence.

New design:

- Evidence is content-addressed (SHA-256 of normalised body)
- Nodes hold references to evidence hashes, not the bodies
- Reorganising the pyramid is now a pure metadata operation

Migration script is half-written. Will write a smoke test before flipping the prod DB over.
