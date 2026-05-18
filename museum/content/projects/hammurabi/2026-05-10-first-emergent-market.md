---
title: First emergent market
date: 2026-05-10
tags: [milestone, economics]
excerpt: With no explicit price-setting code, agents trading surplus grain converged on a stable bid-ask spread within ~40 simulated seasons.
---

Today the simulation produced its first emergent market. No price-setting code — just agents with preferences, surplus inventory, and a willingness to walk a few tiles to trade. Within ~40 seasons a stable bid-ask spread formed and the price tracked seasonal scarcity within ±8%.

Caveats:

- The convergence is fragile to the initial wealth distribution. A 10% perturbation can extend convergence to 200+ seasons or prevent it entirely.
- The "market" is geographic — agents 5+ tiles away pay a measurable premium. I'm leaving that in for now; it's a feature, not a bug.

Next: introduce a land-tenure shock and see whether the market re-converges or fragments.
