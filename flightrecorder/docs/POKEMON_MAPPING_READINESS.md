# Pokemon mapping readiness

Pre-implementation notes for spec section 10 (pokemon pseudonymization).

## What the spec requires

- Deterministic `name_to_pokemon(name)` using SHA-256 hash of normalized name,
  index into a fixed 1025-name pokemon list.
- **whitelist**: `{"daniel"}` - denylist excludes. Only Daniel's name passes
  through unaltered.
- Same input always yields the same pokemon, on any machine, forever.
- Pokemon substitution is for incidental name mentions only. When someone is
  attributed with significant work or quotes, default to omitting them.

## What exists

- `src/data/` has a `.gitkeep`. The 1025-name pokemon list needs to be added
  as `src/data/pokemon.py`.
- The `flightrecorder.data.pokemon` import path is referenced in the spec but
  the module does not exist yet.

## Tests needed (before any redaction code)

1. **Deterministic hash mapping** - same input multiple times, same pokemon.
2. **Whitelist** - `"daniel"` returns `"daniel"`, not a pokemon.
3. **Stable table** - verify `POKEMON` list has exactly 1025 entries and is
   byte-for-byte stable (hash test).
4. **No accidental real names** - the pokemon list contains only pokemon names,
   no real person names.

## Not started

The module and tests have not been written. This is a prerequisite for
curator/reviewer redaction work (steps 12--14).
