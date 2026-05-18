---
title: Hammurabi
summary: Agent-based society simulator that derives civilisational outcomes from first principles. Seed it with founding parameters, watch inequality, housing markets, and justice systems emerge.
status: research
started: 2026-03
stack: [Rust, Polars]
---

Hammurabi is a microsimulation: a few thousand agents with budgets, beliefs, and access to land. The simulation steps forward in seasons. Markets, courts, and informal coalitions are not coded — they *emerge* from local rules. The interesting question is which seed parameters cause which equilibria.

This is research scaffolding, not a product. The goal is a set of reproducible runs that show how small founding-condition perturbations cascade over a hundred simulated years.
