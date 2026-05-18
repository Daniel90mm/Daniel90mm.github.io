# Build status audit

Last audited: 2026-05-18.

Audit of `docs/BUILD_STATUS.md` and `docs/MISSING_WORK.md` against spec
section 19.

## Method

Compared each spec step (1--20) against both status docs. Checked that
status labels match, step names match, and MISSING_WORK counts are
arithmetically consistent with BUILD_STATUS rows.

## Findings

### Step 1 - Backend skeleton

BUILD_STATUS: `mostly done` | MISSING_WORK: `mostly done`. Match.

### Step 2 - Session storage

BUILD_STATUS: `done` | MISSING_WORK: done count includes step 2. Match.

### Step 3 - Chat endpoint

BUILD_STATUS: `done` | MISSING_WORK: done count includes step 3. Match.
BUILD_STATUS correctly notes that the SSE endpoint, budget preflight, and cost
logging are implemented.

### Step 4--7 - Frontend, PWA, Voice, Tagger

All `not started`, all in MISSING_WORK not-started list. Match.

### Step 8 - Project documents + idea capture

BUILD_STATUS: `in progress` | MISSING_WORK: in-progress count includes step 8.
BUILD_STATUS notes append-only helpers, extraction route, provider call,
documents git auto-commit, and round-trip coverage exist. Match.

### Step 9 - Spaghetti capture

BUILD_STATUS: `in progress` | MISSING_WORK: in-progress count includes step 9.
BUILD_STATUS notes spaghetti writing/indexing exists through extraction while
listing and decision surfaces are not built. Match.

### Step 10 - Pokemon mapping

BUILD_STATUS: `in progress` | MISSING_WORK: in-progress count includes step 10.
BUILD_STATUS notes the deterministic placeholder-table baseline and deferred
full name table. Match.

### Step 11 - Matchmaker

BUILD_STATUS: `in progress` | MISSING_WORK: in-progress count includes step 11.
BUILD_STATUS notes the structural endpoint and fail-closed scorer baseline.
Match.

### Step 12 - Curator + reviewer + composer

BUILD_STATUS: `in progress` | MISSING_WORK: in-progress count includes step 12.
BUILD_STATUS notes the fail-closed publisher framework and missing real LLM
stages. Match.

### Step 13--16 - Daily publisher through Implementation marking

Steps 13, 14, and 16 are `not started`, all in MISSING_WORK not-started list.
Step 15 is `in progress` in both files. Match.

### Step 17 - Budget tracking

BUILD_STATUS: `in progress` | MISSING_WORK: in-progress count includes step 17.
BUILD_STATUS notes cost module, sentinel, provider-call guard, and chat/extract
enforcement. Match.

### Step 18 - Polish

BUILD_STATUS: `not started` | MISSING_WORK: in not-started list. Match.

### Step 19 - Termux setup

BUILD_STATUS: `in progress` | MISSING_WORK: in-progress count includes step 19.
BUILD_STATUS notes the dorm-assistant pattern and laptop helper. Match.

### Step 20 - Ship and dogfood

BUILD_STATUS: `not started` | MISSING_WORK: in not-started list. Match.

## Count verification

- Done: 2 (steps 2, 3) - matches MISSING_WORK `Done: **2**`
- Mostly done: 1 (step 1) - matches MISSING_WORK `Mostly done: **1**`
- In progress: 8 (steps 8, 9, 10, 11, 12, 15, 17, 19) - matches MISSING_WORK `In progress: **8**`
- Not started: 9 (remaining) - matches MISSING_WORK `Not started: **9**`
- Sum: 2 + 1 + 8 + 9 = 20. All steps accounted for.

## Verdict

No mismatches found. Both status docs are consistent with each other and with
the spec. Step names and status labels match across all three sources.
