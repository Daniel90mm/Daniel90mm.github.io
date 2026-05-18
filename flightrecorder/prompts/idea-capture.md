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
