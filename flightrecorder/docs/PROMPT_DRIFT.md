# Prompt drift report

Generated against `flightrecorder-spec.md` section 8 (v3).

## Summary

No substance drift. One trivial formatting difference noted below.

## Per-prompt comparison

### brainstorm-system.md vs spec 8.1

**Match.** Content, structure, voice, and rules are identical.

Trivial formatting difference: line 24 uses a single hyphen `"authoritative - he may have"` while the spec uses a double hyphen `"authoritative -- he may have"`. Same meaning; not substantive.

### tagger.md vs spec 8.2

**Match.** JSON schema, rules, and wording are identical.

### idea-capture.md vs spec 8.3

**Match.** Operation types, section enum (`"Open questions" | "Decisions made" | "Current state" | "TODOs" | "Ideas"`), rules, and output format are identical.

### matchmaker.md vs spec 8.4

**Match.** Rejection bias language, confidence levels, zero-match handling, orphan threshold, and output format reference are identical.

### curator.md vs spec 8.5

**Match.** Doxxing rules, redaction sections, snippet drafting criteria, output format, and quantity guidance are identical.

### reviewer.md vs spec 8.6

**Match.** Reject criteria, output JSON schema, and bias statement are identical.

### composer.md vs spec 8.7

**Match.** Composition rules, frontmatter format, voice description, and quiet-day handling are identical.
