# Search-to-spaghetti capture

Web search results can be captured as spaghetti wall notes so external
references become traceable idea fragments in the Flightrecorder system.

## UX contract

1. After running a search, the user may select one or more results and choose
   "capture to spaghetti."
2. Each captured result becomes a new spaghetti idea with:
   - the search result title as the idea heading;
   - the source URL as attribution;
   - the snippet and optionally the raw content as the idea body;
   - a `source:url` frontmatter field.
3. Captured ideas appear in the spaghetti grid and are indexed in
   `metadata.db.ideas` with the same fields as other spaghetti ideas.

## Backend contract

A future `POST /api/spaghetti/from-search` endpoint (or similar) would accept
a `SearchResult` object and produce a spaghetti idea. The date-derived idea_id
format follows the existing `make_idea_id()` convention.

## Attribution and boundaries

- Every captured idea includes a source URL; Flightrecorder never strips
  attribution.
- The snippet and raw content are preserved as-is. The user is responsible
  for any additional filtering before capture.
- No automatic link-following: the search result is a snapshot at capture
  time, not a live mirror.

## Trust boundaries

web content is untrusted context:

- Search results are never injected into system prompts or project documents
  without explicit user action (copy-paste or capture).
- no automatic public publishing from web-derived content. The publisher
  pipeline treats web-sourced ideas the same as all other spaghetti ideas:
  curator + reviewer stages still apply (fail-closed by default).
- The `autoresearch` pattern (Andrej Karpathy's "let the model search then
  reason") may pre-fill context behind a confirm step, but the confirm step
  is mandatory — no invisible search injection.

## Example: capturing an `autoresearch` query

1. User searches `"Karpathy autoregressive search architecture"`.
2. Results return: title "Autoregressive Search", URL `https://karpathy.blog/...`,
   snippet "Karpathy describes a system where...".
3. User clicks "capture to spaghetti".
4. A new spaghetti idea is created with:
   - idea_id: `search-karpathy-autoregressive-<hash>`
   - body: snippet + attribution line + optional raw_content excerpt
   - frontmatter: `source: https://karpathy.blog/...`

This is a read-then-capture flow. No automated crawling, no silent injection.
