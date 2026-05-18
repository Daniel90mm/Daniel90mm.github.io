---
title: Quant Football
summary: Terminal-first football research stack — sync match data into SQLite, build leak-safe features, benchmark probabilistic 1X2 models against market prices.
status: live
started: 2026-01
---

The hard parts of football modelling aren't the models. They're (a) keeping training data leak-free across walk-forward splits, and (b) being honest about whether your model beats the *market*, not just your own holdout. This stack tries to make both first-class.

Workflow is all CLI: sync, build dataset, train, score upcoming fixtures, compare to closing odds.
