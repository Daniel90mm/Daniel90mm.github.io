# flightrecorder — specification (v3)

A self-hosted brainstorming web app with curated public publishing. Captures ideas as they happen; routes each idea to the right project document or to a spaghetti wall of unattached thoughts; periodically proposes connections between loose ideas and existing projects; publishes the full journey of each idea (capture → match → implementation) as a public-facing log.

Runs on a personal-assistant server (Termux on an Android phone now, future-portable to RPi/x86), accessed via Tailscale from phone or laptop. Projects live in their existing home (`~/Documents/Projekter/` on the laptop); flightrecorder references them by name but never owns them.

This document is the source of truth for a coding agent. Behavior is normative. Implementation choices flagged "suggested" are guidance, not requirements.

---

## 1. Where things live

**Merged site/source repo:** `github.com/Daniel90mm/Daniel90mm.github.io` (public). flightrecorder source lives under `flightrecorder/`; the Hugo site lives under `src/`.

**On the laptop (development):** `~/Documents/Projekter/Daniel90mm.github.io/flightrecorder/`.

**On pa-server (deployment):**
- `~/hugo-site/` — git clone of `daniel90mm.github.io`. Updated by `git pull`. Disposable except for unpushed publisher output.
- `~/hugo-site/flightrecorder/` — flightrecorder source tree inside the merged checkout.
- `~/hugo-site/src/` — Hugo site tree. The publisher writes log entries, wall pages, and project pages under `src/content/`, then pushes.
- `~/flightrecorder/` — runtime data. Sessions, documents, sqlite db. **Irreplaceable.** This directory should be backed up separately.
- `~/flightrecorder/documents/` — initialized as its own git repo with a daily auto-commit, giving free history for project documents without affecting the merged site/source repo.

---

## 2. Overview

Four layers, each with its own audience:

- **Raw sessions** (private, on pa-server): every brainstorm with the LLM, saved as markdown. Contains real names, half-thoughts, dead ends. Sessions are short and focused.
- **Project documents** (private working state, on pa-server): one append-only markdown file per project. New ideas targeted at a project get appended to a defined section. Documents grow by accretion, not by rewriting.
- **Spaghetti wall** (private working state, on pa-server): a flat append-only stream of unattached ideas. Each idea is a tagged fragment with a timestamp. Ideas live here forever, even after being matched to projects.
- **Curated public surface** (public, automatic): the curator publishes redacted versions of project documents, the spaghetti wall, and per-idea journey pages to the Hugo site. Doxxing-filtered, pokemon-pseudonymized, on a 24h delay.

The brainstorming LLM does not know about curation or publishing. Curation and publishing run after sessions close, as separate offline passes.

---

## 3. Mental model

Daniel thinks in jolts. Each input is a discrete *idea*. The system's job is to route each idea to the right home and surface non-obvious connections.

Three idea fates:

1. **Direct hit.** Daniel says "for my fNIRS project, I will..." — the tagger detects `project_ref: fnirs` and the idea gets *appended* to the fNIRS project document under "Ideas" (or "TODOs" if it has implementation intent). Append-only: no rewriting, no merging with prior entries. The document grows.

2. **Spaghetti.** Daniel says "I think PCA would be cool for future projects" — no project anchor. The idea lands on the spaghetti wall, untouched, with its tags.

3. **Match.** On a schedule (weekly, or when 20+ unmatched spaghetti ideas accumulate), the matchmaker compares the spaghetti wall against every project document and proposes specific connections with rationales. Daniel approves or rejects each. Approved matches *append* a TODO to the relevant project document(s), preserving the rationale. The spaghetti idea is annotated with where it landed but stays on the wall — ideas are not consumed by matching.

A spaghetti idea can match multiple projects. The PCA idea legitimately belongs in both fNIRS and pulse oximeter. The journey page shows it landing in both.

When the project's actual code repo implements an idea (manual marking in v1), the TODO is marked done with a link to the implementation. The journey page now shows: capture → matched to N projects → implemented in M projects → still open in K.

**Append-only is the central discipline.** Project documents are not rewritten by the system. They grow. This protects against drift, makes git history meaningful, and matches the way ideas actually accumulate.

---

## 4. Architecture

```
+-----------------+         +-----------------+
|  phone (PWA)    |         |  laptop browser |
+--------+--------+         +--------+--------+
         |                           |
         +-------- Tailscale --------+
                     |
                     v
        +---------------------------+
        |  pa-server                |
        |  - FastAPI backend        |
        |  - Static frontend        |
        |  - sqlite metadata        |
        |  - sessions/, documents/  |
        |  - spaghetti/, matches/   |
        |  - daily publisher (cron) |
        |  - weekly matchmaker      |
        +-------------+-------------+
                      |
                      | git push
                      v
        +---------------------------+
        |  Hugo repo on GitHub      |
        |  /log /wall /projects     |
        +---------------------------+
```

Components:

1. **Frontend** — single-page web app, responsive (mobile-first). Plain Svelte (no Tauri). Installable as a PWA on phone home screen. Chat UI, image paste, voice input, session list, document view, match approval queue.
2. **Backend** — FastAPI on pa-server. Owns session storage, runs idea capture/append, talks to provider APIs, exposes a CLI for ops.
3. **Daily publisher** — cron via `termux-services` (or systemd timer later). Runs curator + reviewer on new sessions and documents, composes ripe snippets into log entries, regenerates per-idea journey pages, commits under `~/hugo-site/src/content/`, and git-pushes the merged site/source repo.
4. **Weekly matchmaker** — separate cron job (or threshold-triggered). Compares spaghetti wall against project documents, drops proposals into `matches/pending/` for Daniel to approve.
5. **Hugo site** — already exists. Gains `/log`, `/wall`, `/projects/<name>`, and `/wall/<idea-id>` routes.
6. **Project registry** — `projects.json` on pa-server, synced from the laptop via `fr-sync-projects`.

Current host: OnePlus Nord 2 running Termux, plugged into the router, charging continuously. No battery concerns. ~256GB free. Battery optimization disabled for Termux. `termux-boot` installed for autostart. `termux-wake-lock` wrapped around cron jobs.

Auth: none for v1. Tailscale is the trust boundary.

---

## 5. Directory layout (on pa-server)

Paths relative to `$FLIGHTRECORDER_HOME` (default `~/flightrecorder/`).

```
~/flightrecorder/
├── config.toml                   # provider keys, paths, feature flags, pricing
├── pricing.toml                  # per-model cost table (separate for easy updates)
├── pause                         # presence = publisher kill switch
├── budget                        # presence = spend hard-stop active
├── metadata.db                   # sqlite: sessions, ideas, matches, api_calls
├── sessions/                     # raw chats
│   ├── 2026-05-18-1730-spaghetti-abcd1234.md
│   └── _assets/
│       └── 2026-05-18-1730-pcb-photo.jpg
├── documents/                    # per-project append-only docs (own git repo)
│   ├── .git/
│   ├── flightrecorder.md
│   ├── pulse-oximeter.md
│   └── fnirs.md
├── spaghetti/                    # flat append-only stream of unattached ideas
│   ├── 2026-05-18-1730-pca-future.md
│   └── 2026-05-19-0915-dvorak-hardware.md
├── matches/                      # matchmaker proposals
│   ├── pending/                  # awaiting Daniel's review
│   │   └── 2026-05-25-1200-batch.md
│   ├── approved/                 # logged for audit
│   └── rejected/                 # logged for audit (helps tune matchmaker)
├── journey/                      # rendered idea-journey artifacts for Hugo
│   └── pca-future.md
├── pending/                      # drafted snippets awaiting 24h delay
├── published/                    # mirror of what got published, audit
├── projects.json                 # known project names + metadata
└── logs/
    └── publisher.log

~/hugo-site/                      # cloned merged site/source repo
├── flightrecorder/               # source tree for this app
└── src/
    └── content/                  # Hugo content; publisher writes here
```

Backups: `~/flightrecorder/` excluding `sessions/_assets/` (large) is the critical set. `documents/` has its own git history. `~/hugo-site/` is disposable after push because it is a Git checkout.

---

## 6. File formats

### 6.1 Session

```markdown
---
session_id: 2026-05-18-1730-spaghetti-abcd1234
started_at: 2026-05-18T17:30:00+02:00
ended_at: 2026-05-18T18:42:00+02:00
provider: google
model: gemini-2.5-pro
message_count: 24
image_count: 2
tags: ["fnirs", "signal-processing"]
project_ref: "fnirs"            # may be null
spaghetti: false                # true if no project anchor
extracted: false                # set true after idea-capture pass
extracted_at: null
curated: false
---

## user [17:30:01]
first message text...

## assistant [17:30:14]
response...
```

### 6.2 Project document

```markdown
---
project: fnirs
created: 2026-04-01
last_appended: 2026-05-18T18:45:00+02:00
---

# fnirs

## Problem
<set once, edited rarely. The "why" of the project.>

## Current state
<append-only log of where things stand, dated entries>

### 2026-04-01
<initial state>

### 2026-05-12
<update after a session>

## Decisions made
<append-only log of decisions, dated>

### 2026-05-15: chose AFE-based minimal analog
Rationale: ...
Source: session 2026-05-15-1100

## Open questions
<append-only, but questions can be marked [answered: session-id]>

- 2026-05-10: how to handle motion artifact on the forehead? [open]
- 2026-04-22: optimal source-detector spacing? [answered: 2026-05-08-1430]

## TODOs
<append-only, items can be marked [done] with a link>

- 2026-05-18: prototype the differential amplifier stage [open]
- 2026-05-20: investigate PCA for motion artifact rejection [open, from spaghetti:pca-future]
- 2026-05-01: order SiPMs [done: ordered 2026-05-03]
```

The structure is enforced by the idea-capture prompt; new content always lands in one of the defined sections. Sections are never removed or rewritten by the system. Daniel can edit by hand if he wants.

### 6.3 Spaghetti idea

```markdown
---
idea_id: pca-future
captured_at: 2026-05-18T17:30:00+02:00
source_session: 2026-05-18-1730-spaghetti-abcd1234
tags: ["pca", "signal-processing", "future"]
status: unmatched              # unmatched | matched | orphan
match_attempts: 0
matched_to:                    # list of {project, todo_ref, matched_at, rationale}
implemented_in:                # list of {project, link, implemented_at}
---

I think PCA would be cool for future projects. Could denoise multivariate
signals where a few latent components carry most of the variance.
```

The body is the raw extract from the session, verbatim or lightly cleaned. Frontmatter is the metadata the matchmaker and journey renderer use.

### 6.4 Match proposal

```markdown
---
batch_id: 2026-05-25-1200
generated_at: 2026-05-25T12:00:00+02:00
status: pending                # pending | approved | rejected | partial
---

## Idea: pca-future
"I think PCA would be cool for future projects..."

### Proposed matches

- project: **fnirs**
  rationale: PCA on multichannel optical signals could separate task-related
             hemodynamic response from motion and heart-rate artifacts.
  confidence: high
  proposed_todo: "investigate PCA for motion artifact rejection"
  approve: [ ]

- project: **pulse-oximeter**
  rationale: PCA could help separate the pulsatile AC component from baseline
             DC drift across multiple wavelengths.
  confidence: medium
  proposed_todo: "evaluate PCA vs. bandpass for AC/DC separation"
  approve: [ ]

## Idea: dvorak-hardware
"Idea for a Dvorak-layout mechanical keyboard..."

### Proposed matches

- (no matches found)
  rationale: no existing projects relate to peripherals or input devices.
  approve_as_new_project: [ ]   # creates a new project
  leave_on_wall: [ ]            # default; remains unmatched
```

Daniel reviews via the web UI: a checklist that posts back to the backend, which appends approved TODOs to the relevant project documents and updates the spaghetti idea's frontmatter.

---

## 7. Provider abstraction

```python
class Provider(Protocol):
    name: str
    supports_images: bool
    max_context_tokens: int

    async def chat(
        self,
        messages: list[Message],
        system: str | None = None,
        stream: bool = True,
    ) -> AsyncIterator[str]: ...
```

`config.toml`:

```toml
[providers.anthropic]
api_key = "sk-ant-..."

[providers.openai]
api_key = "sk-..."

[providers.google]
api_key = "..."

[roles.brainstorm]
provider = "google"
model = "gemini-2.5-pro"

[roles.idea_capture]
provider = "anthropic"
model = "claude-sonnet-4-6"

[roles.matchmaker]
provider = "anthropic"
model = "claude-opus-4-7"     # best judgment available; runs weekly

[roles.tagger]
provider = "anthropic"
model = "claude-haiku-4-5"

[roles.curator]
provider = "anthropic"
model = "claude-sonnet-4-6"

[roles.reviewer]
provider = "openai"           # different provider from curator
model = "gpt-5-mini"

[roles.composer]
provider = "anthropic"
model = "claude-sonnet-4-6"

[roles.voice_transcription]
provider = "openai"
model = "whisper-1"

[budget]
warn_at_eur = 30
hard_stop_eur = 80
currency = "EUR"
```

Curator and reviewer use different providers when possible — shared-blindspot failures are real.

---

## 8. Prompts

These prompts are the product. Code is mechanical.

### 8.1 Brainstorm LLM system prompt

```
You are Daniel's thinking partner. He brainstorms a lot, generates ambitious
projects, and uses AI heavily for implementation. He is a DTU bachelor/master
student in optics and biophotonics, based in Denmark. His thesis is a pulse
oximeter. He works across embedded, civic tech, data science, desktop apps,
and home automation.

Your job:
- Be a real thinking partner. Push back. Disagree when you should.
- Surface tradeoffs honestly. Flag when something looks like
  infrastructure-as-procrastination (his known pattern).
- Skip preambles. Match his directness.
- Show reasoning, not just conclusions. Use formulas and short examples.
- Respond in the same language he writes in (Danish or English).
- Avoid sycophancy. Reasonable disagreement is not detachment.

Style:
- Direct, concise unless he asks for detail.
- Double quotes in code. No unicode (write "pi" not the symbol).
- Python preferred for general code, C for embedded.
- When debugging, ask clarifying questions before suggesting fixes.

Sometimes the relevant project document will be injected below this prompt.
It represents accumulated decisions and open questions on this project.
Treat it as Daniel's working state, not as authoritative — he may have
changed his mind, and you should push back on it when you should.

You are not aware of any publishing pipeline or matchmaker. This is a
private workspace.
```

### 8.2 Tagger

Runs on session close. Input: session transcript + list of known projects. Output: JSON.

```
Read the following brainstorming session. Output ONLY a JSON object:

{
  "slug": "short-kebab-case-summary",
  "tags": ["keyword1", "keyword2"],
  "project_ref": "project-name" or null,
  "spaghetti": true/false,
  "topics": ["broader-theme"],
  "entities": ["FirstName LastName"]
}

Existing projects (use exact match for project_ref, or null):
{{project_list}}

Rules:
- If the session ranges across multiple topics with no anchor, set spaghetti=true.
- Do not invent a project_ref. Either match exactly or use null.
- entities: real people mentioned by name. Not place names, not products.
- No prose, no markdown fences. JSON only.
```

### 8.3 Idea capture

Runs after tagging on session close. Extracts discrete ideas from the session and decides where each lands. Input: session transcript + current project document (if `project_ref` is set) + the list of projects. Output: a list of idea operations.

```
Read the following brainstorming session. Extract every discrete IDEA
that emerged. An idea is a thought worth keeping: a hypothesis, a
proposed approach, a decision, an open question, a TODO, a finding.

For each idea, decide where it should land:

- If the session has a project_ref and the idea is about that project,
  emit a project_append operation specifying which section it belongs in.
- If the idea is about a different existing project, emit a project_append
  with that project_ref.
- Otherwise, emit a spaghetti operation.

Output a JSON array. Each element is one operation:

[
  {
    "type": "project_append",
    "project_ref": "fnirs",
    "section": "Open questions" | "Decisions made" | "Current state" | "TODOs" | "Ideas",
    "content": "the idea, rewritten as a single bullet, terse, voice-y"
  },
  {
    "type": "spaghetti",
    "tags": ["pca", "signal-processing"],
    "topics": ["statistics"],
    "content": "the idea, in his voice, 1-3 sentences"
  }
]

Rules:
- Be conservative. Most sessions produce 0-3 ideas. A great session
  might produce 5. More than 8 from one session means you're padding.
- "Current state" is for status updates. "Decisions made" is for choices
  with rationale. "Open questions" is for things to figure out. "TODOs"
  is for action items. "Ideas" is the catchall for "hm, worth exploring."
- Do not invent ideas. If the session is mostly chitchat or debugging,
  return [].
- Match Daniel's voice: terse, first person, past tense for findings,
  imperative for TODOs.
- Output JSON only.
```

### 8.4 Matchmaker

Runs weekly or when 20+ unmatched spaghetti ideas accumulate. Input: all unmatched spaghetti ideas + all project documents + the list of projects with descriptions. Output: a match-proposals markdown file for Daniel to review.

```
You are matchmaking unattached ideas to existing projects.

Most ideas do not fit most projects. Default to no match. Forcing fits
that don't really fit is the failure mode this prompt is designed to
prevent. If you find yourself reaching, stop and return no match.

For each idea, consider every project. For most idea-project pairs,
the answer is no. Only propose a match when:

- the idea would meaningfully advance the project, AND
- you can articulate a specific rationale (not "could be useful"), AND
- the resulting TODO would be concrete enough to act on

Confidence levels:
- high: the idea is directly applicable, the project would clearly
        benefit, the TODO is obvious
- medium: the idea is plausibly applicable, would require some
          adaptation, worth investigating
- (do not output "low" — if it's low, do not match)

An idea may match multiple projects. That is allowed and often correct.

For ideas with no matches, emit a single block noting the lack of
matches and suggesting either:
- approve_as_new_project (when the idea hints at a coherent new project)
- leave_on_wall (the default; idea stays unmatched)

Also count match_attempts for each idea. If an idea has had 3+
unsuccessful matchmaker runs, flag it as a candidate for orphan tag.

Output: a markdown file following the format in spec §6.4. No commentary
outside the file structure.
```

### 8.5 Curator (AGENTS.md for the curator)

Checked into `flightrecorder/prompts/` in the merged site/source repo. Loaded as the curator system prompt.

```markdown
# Curator role

You produce publishable redactions of three kinds of content:

1. Project documents — rendered for /projects/<name> pages
2. Spaghetti ideas — rendered for /wall and /wall/<idea-id>
3. Daily log entries — snippets composed from session transcripts

Output is automatically published after a 24-hour delay. There is no
human review gate, only an adversarial reviewer pass after yours.

## Doxxing rules (HARD)

These are non-negotiable. Violations get the content rejected by the
reviewer pass.

- No real names except "daniel" (whitelist). Replace all detected proper
  names with their deterministic pokemon pseudonym via name_to_pokemon().
- No email addresses, phone numbers, physical addresses.
- No employer or client names without explicit "this is OK to share"
  flag in the source session.
- No DTU course codes that pin a specific semester (course names are
  fine; "02100 spring 2026" is not).
- No private repo names, internal URLs, or non-public APIs by name.
- When summarizing a conversation with a real person, default to
  maximum vagueness: "a DTU lecturer" not "Oshawott".
- Pokemon substitution is for incidental name mentions, not for
  attributing significant work or quotes. If something is about what
  someone said or did, default to omitting them.

## Project document redaction

Render the project document as-is, minus any sections or bullets that
contain sensitive content. Preserve structure. Output is markdown.
Do not summarize; redact only.

## Spaghetti idea redaction

Render the idea verbatim minus any doxxing. If the entire idea is
sensitive (medical, financial, relationship), output:
NOT_PUBLISHABLE

## Snippet drafting (daily log entries)

Read recent session transcripts and extract publishable moments:
- Insight: something cracked open
- Productive confusion: a real puzzle worth showing
- Course-correction: noticing a wrong direction and pivoting
- Tradeoff articulation: naming cost/benefit of two paths
- Dead ends recognized as dead ends
- Specific technical decisions with reasoning

Do NOT publish:
- Syntax help, debugging dumps, code without insight
- Small talk, scheduling, off-topic
- Anything sensitive
- Anything about specific other people's projects

Form: narrative fragments, not bullets. Past tense, voice-y. 80-300
words. Lead with the moment. Markdown, no headers inside the body.

If a session has no publishable moment, output: NO_SNIPPETS

## Quantity

Most sessions produce zero snippets. Productive sessions produce one.
Three or more from one session means you're reaching.

## Output format (for snippets)

---
snippet_id: <session_id>-<index>
source_session: <session_id>
drafted_at: <iso8601>
publish_after: <iso8601 + 24h>
tags: [...]
project_ref: ...
---

<snippet body>
```

### 8.6 Adversarial reviewer

Runs on every drafted curator output. Different model and provider when possible.

```
You are an adversarial reviewer protecting Daniel's privacy and
reputation. You will be shown a piece of curator output and the source
material it was drafted from. Your job is to find reasons to REJECT.

Reject if any of the following:
- Real name not in whitelist ["daniel"], even if claimed pseudonymized
- Email, phone, address, dated course code, other identifier
- Information about a third party's unpublished work
- Sensitive personal content (health, finances, relationships)
- Security-relevant detail (API key, infra, repo url)
- Materially inaccurate vs. source
- Would embarrass Daniel professionally
- Filler shaped like content, communicates nothing

Output JSON only:

{
  "verdict": "approve" | "reject",
  "reasons": ["..."],
  "redactions": [{"find": "...", "replace": "..."}]
}

When in doubt, reject. False rejects are cheap; false approves are not.
```

### 8.7 Composer

Runs daily during publishing. Weaves the day's ripe snippets into a single log entry.

```
Compose a daily log entry from the following approved snippets. Short
narrative prose linking them with light connective tissue. Do not
invent content. Do not summarize - present.

Output:

---
date: <today>
slug: <kebab-case summary>
snippet_ids: [...]
---

<2-4 sentences of opening framing, lowercase first letter, terminal-
prompt voice - direct, no warm-ups>

<snippet 1 body, with minimal connective intro if needed>

<snippet 2 body>

<optional 1-sentence closing if natural; omit if forced>

Voice: dispatch from a working notebook. First person, past tense.
No section headers. No emoji.
```

**Zero ripe snippets → no log entry that day.** Quiet days are quiet days.

---

## 9. Pokemon mapping

Stateless, deterministic. No names file to maintain.

```python
import hashlib
from flightrecorder.data.pokemon import POKEMON  # 1025 names

WHITELIST = {"daniel"}

def name_to_pokemon(name: str) -> str:
    normalized = name.lower().strip()
    if normalized in WHITELIST:
        return name
    h = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
    idx = int(h[:8], 16) % len(POKEMON)
    return POKEMON[idx]
```

Same input always yields the same pokemon, on any machine, forever.

---

## 10. Public surface (Hugo)

Four route families:

### `/log/<date>-<slug>/`
Daily log entries composed from snippets. Reverse chronological list at `/log/`.

### `/wall/`
Reverse chronological feed of curated spaghetti ideas. Each shows:
- Tagline (first sentence of the idea)
- Date captured
- Status badges: `orphan` / `matched ×N` / `implemented ×M`
- Tags

Click → idea journey page.

### `/wall/<idea-id>/`
The full life of one idea:
- Original idea text (redacted)
- Timeline:
  - Captured 2026-05-18
  - Matched to fnirs on 2026-05-25 (with rationale)
  - Matched to pulse-oximeter on 2026-05-25 (with rationale)
  - Implemented in fnirs on 2026-06-12 (link to commit/release if available)
  - Still open in pulse-oximeter

This is the "live window into iteration." The interesting page.

### `/projects/<name>/`
The redacted project document rendered as HTML. Sections visible. TODOs visible with their status (open/done) and, where applicable, a link to the spaghetti idea that spawned them.

Click on a TODO that came from spaghetti → links back to `/wall/<idea-id>/`. Bidirectional graph.

The main site nav: `log` | `wall` | `projects`. The flight recorder aesthetic matches your existing TUI/terminal-prompt style.

**Implementation marking** for v1 is manual: Daniel marks a TODO done via the web UI, optionally pasting a commit URL or release link. v2 might detect commits in project repos automatically.

---

## 11. Backend API

REST + SSE. Mounted at `/api`.

| method | path | purpose |
|---|---|---|
| POST | `/api/sessions` | start a session |
| GET | `/api/sessions` | list sessions |
| GET | `/api/sessions/{id}` | session detail |
| POST | `/api/sessions/{id}/messages` | post message, stream response (SSE) |
| POST | `/api/sessions/{id}/close` | end session, trigger tagger + idea capture |
| POST | `/api/sessions/{id}/upload` | upload image |
| POST | `/api/sessions/{id}/voice` | upload audio, returns Whisper transcript |
| POST | `/api/sessions/capture` | quick-capture endpoint: one message, auto-close |
| GET | `/api/documents` | list project documents |
| GET | `/api/documents/{project_ref}` | fetch a project document |
| GET | `/api/documents/{project_ref}/history` | git log of the documents repo, filtered to this file |
| POST | `/api/documents/{project_ref}/todo/{id}/done` | mark a TODO done, optional link |
| GET | `/api/spaghetti` | list spaghetti ideas, filterable by status |
| GET | `/api/spaghetti/{id}` | fetch one |
| GET | `/api/matches/pending` | list pending match proposals |
| POST | `/api/matches/{batch_id}/decide` | submit Daniel's approve/reject decisions |
| POST | `/api/promote` | promote a spaghetti idea to a new project |
| GET | `/api/projects` | get project registry |
| POST | `/api/projects` | update project registry (from `fr-sync-projects`) |
| GET | `/api/journey/{idea_id}` | rendered idea journey JSON |
| POST | `/api/pause` | publisher kill switch |
| GET | `/api/budget` | monthly spend, thresholds |
| POST | `/api/budget` | update thresholds (effectively top up) |
| DELETE | `/api/budget/hard-stop` | clear budget hard-stop |
| GET | `/api/audit` | last 30 days of publisher decisions |

---

## 12. CLI

```
fr status                       # paused? last publish? pending? monthly spend?
fr pause / fr resume            # publisher kill switch
fr publish --dry-run / publish  # run publisher (cron uses this)
fr match --dry-run / fr match   # run matchmaker (weekly cron uses this)
fr ideas [--unmatched|orphan]   # list spaghetti ideas
fr docs                         # list project documents and sizes
fr promote <idea-id>            # promote a spaghetti idea to new project
fr retag <session-id>           # rerun tagger
fr recapture <session-id>       # rerun idea capture
fr review                       # open pending snippets and matches in $EDITOR
fr audit                        # recent publisher/matchmaker decisions
fr budget [set|clear-stop]      # budget controls
fr sync-projects --from <path>  # update projects.json
```

Laptop-side:

```
fr-sync-projects                # scans ~/Documents/Projekter/, posts to pa-server
```

---

## 13. Pipelines

Three scheduled pipelines plus on-demand triggers.

### Session close (immediate)

```
1. Tagger runs on transcript.
2. Idea capture runs:
   - For each project_append op: append to documents/<project_ref>.md
     in the named section. Auto-commit documents/ git repo.
   - For each spaghetti op: write a new file in spaghetti/.
3. Log token usage.
```

### Daily publisher (cron, 03:00)

```
1. Check pause file → exit if present.
2. Check budget file → exit if present.
3. For each session where curated=false and ended_at < (now - 1h):
   - Run curator → 0..N snippets
   - For each snippet: reviewer pass → pending/ or rejected
   - Mark session curated=true
4. For each project document changed since last publish:
   - Run curator on the full doc → redacted version
   - Reviewer pass
   - Write to ~/hugo-site/src/content/projects/<name>.md
5. For each spaghetti idea created or updated since last publish:
   - Run curator on the idea → redacted version
   - Reviewer pass
   - Write to ~/hugo-site/src/content/wall/<idea-id>.md
6. For each idea with updated journey (new match, new implementation):
   - Render journey JSON, write to ~/hugo-site/src/content/wall/<idea-id>.md frontmatter
7. Find pending snippets where publish_after < now:
   - If zero → log "quiet day", skip log composition
   - Else → run composer, write log entry
8. git pull && git commit && git push (Hugo repo)
9. Move ripe snippets pending/ → published/
10. Roll up monthly token spend. Warn or hard-stop if thresholds crossed.
11. Append run summary to publisher.log.
```

### Weekly matchmaker (cron, Sundays 04:00, or when threshold hit)

```
1. Check pause and budget files.
2. Load all unmatched + non-orphan spaghetti ideas.
3. Load all project documents.
4. Run matchmaker prompt.
5. Write proposal batch to matches/pending/<date>.md.
6. Increment match_attempts on each idea included.
7. Mark ideas with match_attempts >= 3 and no matches as status=orphan.
8. Optional: send notification (deferred to v2).
```

### Match approval (on-demand, Daniel via UI)

```
1. Daniel ticks approve/reject boxes on a pending batch.
2. For each approved match:
   - Append a TODO to documents/<project_ref>.md under "TODOs"
     with rationale and source spaghetti idea_id.
   - Append to spaghetti/<idea-id>.md frontmatter: matched_to.
   - Auto-commit documents/ git repo.
3. For each "approve_as_new_project":
   - Run promotion prompt → suggested name + initial doc.
   - Show to Daniel for confirmation, then create.
4. Move batch from pending/ to approved/ (or rejected/).
```

### Implementation marking (on-demand, Daniel via UI)

```
1. Daniel views a project document, clicks "mark done" on a TODO.
2. Optionally pastes a commit URL or release link.
3. Backend updates the document (append [done: <date>, <link>]).
4. If the TODO has a spaghetti source: update spaghetti idea's
   implemented_in field.
5. Auto-commit documents/.
```

Failure modes for each pipeline are in §15.

---

## 14. Session lifecycle

- **Open:** "new session" button, or quick-capture (one-message session).
- **Active:** stays open as long as messages flow. No timeout while active.
- **Idle:** after 12h of silence, server auto-closes and runs session-close pipeline. Configurable.
- **Manual close:** "close session" button always available; runs pipeline immediately.
- **Resume:** there is no resume. New sessions are new blocks. Project documents carry memory forward.
- **Cross-device:** session state is server-side. Open session is reachable from phone or laptop.

---

## 15. Failure modes and observability

| failure | behavior |
|---|---|
| pause file present | publisher exits cleanly |
| budget hard-stop file present | brainstorm refuses new messages, publisher and matchmaker skip |
| provider API down | log, exit non-zero, cron retries |
| tagger returns malformed output | session stays untagged, retry on next pass |
| idea capture returns malformed output | session stays unextracted, retry on next pass |
| matchmaker proposes nonsense | Daniel rejects via UI; rejected/ batch logged for future prompt tuning |
| curator returns malformed output | log, skip, do not mark curated |
| reviewer rejects everything | log rejections, no log entry that day |
| git push fails (Hugo repo) | log, leave files in working state, audit surfaces |
| documents/ git commit fails | log, leave file in working state, surface via `fr audit` |
| voice transcription fails | error to frontend; user types instead |
| name detection misses an entity | reviewer should catch; `fr audit` shows if both miss |
| pa-server killed by Android | termux-boot restarts on next phone reboot |
| phone unplugged + drained | down until plugged in; `fr audit` shows gap |
| projects.json missing | tagger uses empty list; all sessions get project_ref=null |
| concurrent edits to same project document | last-write-wins; serialized server-side, rare in practice |
| orphan idea pile grows | quarterly review surfaces them in `fr ideas --orphan` |

`fr audit` is primary observability. `publisher.log` is structured JSON, grep-able.

---

## 16. Voice input

Whisper API server-side. On-device transcription rejected for quality reasons.

```
1. User taps mic in chat UI.
2. Browser captures audio (MediaRecorder).
3. On stop, audio POSTs to /api/sessions/{id}/voice.
4. Backend forwards to OpenAI Whisper, returns transcript.
5. Frontend inserts transcript into message input. User can edit
   before sending.
6. Cost logged to api_calls (whisper-1 is ~$0.006/min).
```

5-minute cap per recording. Audio not stored after transcription. Whisper handles Danish and English equally.

---

## 17. Cost monitoring

Every API call writes a row in `metadata.db.api_calls`:

```sql
CREATE TABLE api_calls (
    id INTEGER PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    provider TEXT NOT NULL,
    model TEXT NOT NULL,
    role TEXT NOT NULL,
    input_tokens INTEGER NOT NULL,
    output_tokens INTEGER NOT NULL,
    cached_tokens INTEGER DEFAULT 0,
    cost_eur REAL NOT NULL,
    session_id TEXT
);
```

`pricing.toml` holds per-model rates, separate from `config.toml` so it can be updated independently. After every call:

- Recompute monthly rolling spend.
- If over `warn_at_eur`: log warning, surface in `fr status` and UI banner.
- If over `hard_stop_eur`: write `budget` kill switch file. Brainstorm and publisher refuse to run until cleared.

Clear via `fr budget clear-stop` or by raising `hard_stop_eur` (top-up).

---

## 18. Open questions / v2 deferrals

1. **Hugo content path** — confirm against `.github/workflows/*.yml`, fill into `config.toml`.
2. **Matchmaker auto-trigger threshold** — start at 20 unmatched ideas, tune by observation.
3. **Orphan threshold** — start at 3 unsuccessful matchmaker passes, tune by observation.
4. **Implementation marking automation** — git hooks on project repos that detect "fixes #idea-pca-future" in commit messages. v2.
5. **Cross-project idea search** — currently no retrieval. If the wall grows past several hundred ideas, add sqlite FTS5 for keyword search. Vector search not needed unless that proves insufficient.
6. **Notifications** — Pushover or ntfy when matchmaker has new proposals or publisher fails for 2+ days. v2.
7. **Public exposure** — read-only flight recorder UI behind Cloudflare tunnel. v2.
8. **Image handling in published artifacts** — currently text-only. Decide later.
9. **Quarterly orphan review surface** — a UI page listing orphans for periodic human attention. v1.5.
10. **Slab lag investigation** — separate, not flightrecorder.

---

## 19. Build order

1. **Backend skeleton.** FastAPI, sqlite schema (sessions, ideas, matches, api_calls), config loading, provider abstraction (Anthropic + Google + OpenAI). Health endpoint. Verify deps install on Termux ARM64.
2. **Session storage.** File reader/writer, sqlite metadata index, image upload (cap 5MB).
3. **Chat endpoint.** Streaming SSE, message persistence, image inclusion, token logging.
4. **Frontend skeleton.** Svelte SPA, responsive, chat UI, session list, image paste. Verify on iOS Safari and Android Chrome over Tailscale.
5. **PWA manifest + service worker.** Installable on phone, `/capture` home-screen shortcut.
6. **Voice input.** MediaRecorder + Whisper endpoint.
7. **Tagger.** Runs on session close.
8. **Project documents + idea capture.** This is the core append loop. `documents/` git repo, auto-commit. Test on 5-10 hand-rolled sessions before going live.
9. **Spaghetti capture.** Same loop, different sink.
10. **Pokemon mapping.** Module + tests.
11. **Matchmaker.** Cron + on-demand. The match-approval UI in the frontend.
12. **Curator + reviewer + composer.** Each runnable standalone, then wire into daily publisher.
13. **Daily publisher.** termux-services + cron + wake-lock. Dry-run mode.
14. **Hugo integration.** Confirm content path, write log entries, project pages, wall pages, journey pages, push.
15. **Project registry.** API endpoint, `fr-sync-projects` script for laptop.
16. **Implementation marking UI.** Mark TODOs done, link to commits.
17. **Budget tracking.** Pricing table, monthly rollup, warn and hard-stop.
18. **Polish.** `fr audit`, kill switches in UI, error handling.
19. **Termux setup checklist.** termux-boot, battery optimization, autostart, in `SETUP.md`.
20. **Ship and dogfood for two weeks.** Fix what breaks.

Do not build retrieval, notifications, public exposure, or orphan-review UI in v1.
