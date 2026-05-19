Read the following brainstorming session. Extract only the discrete IDEAS
worth keeping. A keeper is a specific hypothesis, technical approach,
measurement trick, analysis method, design decision, open question, TODO, or
finding that could be useful later.

Generic software chores are not ideas. Ignore entries like "improve UI",
"remove bugs", "add tests", "make it better", "clean up code", or project
management noise unless the transcript includes a specific technical method or
decision. Preserve the useful concrete core: "apply PCA to disordered
multi-dimensional data" is worth keeping; "improve data analysis" is not.

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
- Prefer concrete technical nouns over generic labels. Keep "ECG reference for
  pulse-ox heartbeat synchronization", not "improve measurement accuracy".
- "Current state" is for status updates. "Decisions made" is for choices
  with rationale. "Open questions" is for things to figure out. "TODOs"
  is for action items. "Ideas" is the catchall for "hm, worth exploring."
- Do not invent ideas. If the session is mostly chitchat or debugging,
  return [].
- Match Daniel's voice: terse, first person, past tense for findings,
  imperative for TODOs.
- Output JSON only: no markdown fence, no prose, no explanation.
