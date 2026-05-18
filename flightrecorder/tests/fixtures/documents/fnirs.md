---
project: fnirs
created: 2026-05-01
last_appended: 2026-05-18T19:00:00+02:00
---

# fnirs

## Problem

Build a functional near-infrared spectroscopy system for brain imaging research.

## Current state

The AFE-based frontend design is complete. PCB layout in progress.

## Decisions made

### 2026-05-15: chose AFE-based minimal analog

Rationale: the integrated AFE reduces component count and noise compared to
discrete op-amp chains.

Source: session 2026-05-15-1100

## Open questions

- 2026-05-10: how to handle motion artifact on the forehead? [open]
- 2026-04-22: optimal source-detector spacing? [answered: 2026-05-08-1430]

Here is a hand-written note that Daniel added manually outside any section.
It discusses calibration drift and references a paper.

## TODOs

- 2026-05-18: prototype the differential amplifier stage [open]
- 2026-05-20: investigate PCA for motion artifact rejection [open, from spaghetti:pca-future]

## Ideas

- adaptive gain control based on ambient light levels
