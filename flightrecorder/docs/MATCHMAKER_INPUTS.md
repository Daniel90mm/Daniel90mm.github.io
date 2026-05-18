# Matchmaker inputs

The future matchmaker (step 11) reads these files and tables. This document
stays factual about what exists, not what will be built.

## Input sources

### 1. Spaghetti markdown files
`$FLIGHTRECORDER_HOME/spaghetti/*.md` - one per unattached idea. Each contains
frontmatter with `idea_id`, `tags`, `topics`, `status`, `match_attempts`,
`matched_to`, `implemented_in`, and the idea body text.

### 2. Ideas rows (sqlite)
`metadata.db.ideas` - indexed mirror of the spaghetti files. Queryable by
`status = 'unmatched'` to find candidates for the current matchmaker pass.

### 3. project documents
`$FLIGHTRECORDER_HOME/documents/*.md` - append-only markdown files with
sections like `## Problem`, `## TODOs`, `## Open questions`. The matchmaker
reads these to understand project context and detect existing related work.

### 4. Project registry
`$FLIGHTRECORDER_HOME/projects.json` - metadata about known projects: names,
refs, descriptions, active flags. Provides project-level summaries for the
matchmaker without needing to read every document header.

## Not implemented

The matchmaker prompt exists in `prompts/matchmaker.md` and the input file
formats are stable, but the actual matchmaker pipeline (loading inputs,
running the prompt, writing match proposal batches) has not been built.
