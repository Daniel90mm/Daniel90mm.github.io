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
