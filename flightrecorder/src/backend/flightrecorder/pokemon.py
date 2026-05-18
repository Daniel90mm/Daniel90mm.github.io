"""Deterministic pokemon-name pseudonymization for the publisher pipeline.

Per spec section 8.5: real names (except the whitelist `{"daniel"}`) must
be replaced with a deterministic pokemon pseudonym before content reaches
the public Hugo site. The mapping is stable: the same real name always
maps to the same pokemon, across every published page, so journey pages
stay coherent over time.

This module is the **structural baseline** (build-order step 10). It ships
with a 20-name placeholder table - the full 1025-name list lands in a
separate step that needs a verified data source. The API is stable now so
the curator/reviewer pipeline can be wired against it.

Design notes:

- The mapping is sha256-based, not pseudorandom. We want it deterministic
  across machines and across restarts, not unpredictable. Anyone who
  knows the algorithm and the name table can reproduce the mapping, and
  that is fine - the goal is reader privacy, not cryptographic
  unguessability.
- `pseudonymize_text` only substitutes names the caller hands in. The LLM
  curator is responsible for identifying *which* tokens in source text
  are real names. This module performs the substitution deterministically
  once that decision is made. That split keeps the regex-driven walker
  free of false positives.
- The name table is a parameter, defaulting to the placeholder. Tests can
  inject custom tables. Production callers will pass the eventual
  1025-name table once it lands.
"""

from __future__ import annotations

import hashlib
import re


WHITELIST_NAMES = frozenset({"daniel"})
"""Real names that may appear in published output verbatim. Case-insensitive
on input; the canonical form is lowercase."""


POKEMON_NAMES_PLACEHOLDER: tuple[str, ...] = (
    "Bulbasaur",
    "Charmander",
    "Squirtle",
    "Pikachu",
    "Eevee",
    "Snorlax",
    "Gengar",
    "Lapras",
    "Mewtwo",
    "Dragonite",
    "Tyranitar",
    "Lugia",
    "Celebi",
    "Blaziken",
    "Gardevoir",
    "Salamence",
    "Garchomp",
    "Lucario",
    "Greninja",
    "Magikarp",
)
"""20-name placeholder. The full 1025-name table ships separately."""


def name_to_pokemon(
    name: str,
    pokemon_table: tuple[str, ...] = POKEMON_NAMES_PLACEHOLDER,
) -> str:
    """Map one real name to a deterministic pseudonym.

    Whitelist names pass through unchanged (normalized to lowercase).
    Every other name is hashed (sha256) and the first 8 bytes are used
    as an index into the supplied pokemon table. The same input always
    produces the same output for the same table.
    """

    if not isinstance(name, str):
        raise TypeError(f"name must be a string, got {type(name).__name__}")
    stripped = name.strip()
    if stripped == "":
        raise ValueError("name must not be empty after strip")
    if not pokemon_table:
        raise ValueError("pokemon_table must not be empty")

    lowered = stripped.lower()
    if lowered in WHITELIST_NAMES:
        return lowered

    digest = hashlib.sha256(lowered.encode("utf-8")).digest()
    index = int.from_bytes(digest[:8], "big") % len(pokemon_table)
    return pokemon_table[index]


def pseudonymize_text(
    text: str,
    names: list[str],
    pokemon_table: tuple[str, ...] = POKEMON_NAMES_PLACEHOLDER,
) -> str:
    """Replace each occurrence of `names` in `text` with its pokemon mapping.

    Word-bounded substitution: `"Anna"` does not match `"Annapolis"`. The
    caller is responsible for identifying which strings are real names
    (an LLM curator handles that in production); this function only does
    deterministic, case-sensitive substitution once the decision is made.

    Whitelist names in the `names` list pass through (mapped to their
    canonical lowercase form via `name_to_pokemon`). Names not present in
    `text` are silently ignored.

    Longer names are substituted first so multi-token names like
    `"Anna Svensson"` win over a substring `"Anna"` that would otherwise
    match inside the longer name.
    """

    if not isinstance(text, str):
        raise TypeError(f"text must be a string, got {type(text).__name__}")
    if not isinstance(names, list):
        raise TypeError(f"names must be a list, got {type(names).__name__}")

    out = text
    for name in sorted({n for n in names if isinstance(n, str) and n.strip() != ""}, key=len, reverse=True):
        replacement = name_to_pokemon(name, pokemon_table)
        out = re.sub(rf"\b{re.escape(name)}\b", replacement, out)
    return out
