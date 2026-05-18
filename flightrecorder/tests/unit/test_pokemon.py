"""Unit tests for the pokemon pseudonymization baseline.

Covers determinism (same input -> same output), whitelist passthrough,
case handling, the word-bounded substitution in `pseudonymize_text`,
multi-token name precedence, and parametrized name-table injection.
"""

from __future__ import annotations

import pytest

from flightrecorder.pokemon import (
    POKEMON_NAMES_PLACEHOLDER,
    WHITELIST_NAMES,
    name_to_pokemon,
    pseudonymize_text,
)


# --- Determinism ---


def test_same_name_always_maps_to_same_pokemon() -> None:
    assert name_to_pokemon("Mikkel") == name_to_pokemon("Mikkel")
    assert name_to_pokemon("Anna Svensson") == name_to_pokemon("Anna Svensson")


def test_mapping_is_case_insensitive_on_input() -> None:
    assert name_to_pokemon("MIKKEL") == name_to_pokemon("mikkel")
    assert name_to_pokemon("Mikkel") == name_to_pokemon("mIkKeL")


def test_mapping_is_stable_across_calls() -> None:
    """The mapping should not depend on PYTHONHASHSEED or call order."""
    first = name_to_pokemon("Anna")
    for _ in range(10):
        assert name_to_pokemon("Anna") == first


def test_mapping_returns_a_name_from_the_table() -> None:
    result = name_to_pokemon("Mikkel")
    assert result in POKEMON_NAMES_PLACEHOLDER


# --- Whitelist ---


def test_whitelist_passes_through_unchanged() -> None:
    assert name_to_pokemon("daniel") == "daniel"
    assert name_to_pokemon("Daniel") == "daniel"
    assert name_to_pokemon("DANIEL") == "daniel"


def test_whitelist_constant_contents() -> None:
    """The whitelist is a frozenset containing exactly 'daniel' for v1."""
    assert WHITELIST_NAMES == frozenset({"daniel"})


# --- Validation ---


def test_empty_name_raises() -> None:
    with pytest.raises(ValueError):
        name_to_pokemon("")
    with pytest.raises(ValueError):
        name_to_pokemon("   ")


def test_non_string_name_raises() -> None:
    with pytest.raises(TypeError):
        name_to_pokemon(42)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        name_to_pokemon(None)  # type: ignore[arg-type]


def test_empty_pokemon_table_raises() -> None:
    with pytest.raises(ValueError):
        name_to_pokemon("Mikkel", pokemon_table=())


# --- Custom pokemon table ---


def test_custom_table_is_honored() -> None:
    table = ("Alpha", "Beta", "Gamma")
    result = name_to_pokemon("Mikkel", pokemon_table=table)
    assert result in table


def test_different_tables_can_produce_different_outputs() -> None:
    """Sanity check: a name that maps to one pokemon under the placeholder
    table need not map to the same pokemon under a different table."""
    placeholder = name_to_pokemon("Mikkel")
    custom = name_to_pokemon("Mikkel", pokemon_table=("OnlyOne",))
    assert custom == "OnlyOne"
    # The placeholder result must be from the placeholder table.
    assert placeholder in POKEMON_NAMES_PLACEHOLDER


# --- pseudonymize_text ---


def test_pseudonymize_text_replaces_named_tokens() -> None:
    text = "Mikkel mentioned that Anna would review the manuscript."
    result = pseudonymize_text(text, ["Mikkel", "Anna"])
    assert "Mikkel" not in result
    assert "Anna" not in result
    assert name_to_pokemon("Mikkel") in result
    assert name_to_pokemon("Anna") in result


def test_pseudonymize_text_word_bounded() -> None:
    """`Anna` must not match inside `Annapolis`."""
    text = "Anna lives near Annapolis."
    result = pseudonymize_text(text, ["Anna"])
    assert "Annapolis" in result
    assert name_to_pokemon("Anna") in result


def test_pseudonymize_text_leaves_whitelist_intact() -> None:
    text = "daniel and Mikkel collaborated on the project."
    result = pseudonymize_text(text, ["daniel", "Mikkel"])
    assert "daniel" in result
    assert "Mikkel" not in result


def test_pseudonymize_text_ignores_names_not_present() -> None:
    text = "The amplifier stage drifts under load."
    result = pseudonymize_text(text, ["Mikkel", "Anna"])
    assert result == text


def test_pseudonymize_text_handles_empty_names_list() -> None:
    text = "Mikkel and Anna talked."
    result = pseudonymize_text(text, [])
    assert result == text


def test_pseudonymize_text_strips_empty_and_whitespace_names() -> None:
    text = "Mikkel went home."
    result = pseudonymize_text(text, ["", "   ", "Mikkel"])
    assert "Mikkel" not in result
    assert name_to_pokemon("Mikkel") in result


def test_longer_names_substituted_first() -> None:
    """Multi-token names must win over substrings inside them.

    Without longest-first ordering, replacing `"Anna"` before
    `"Anna Svensson"` would corrupt the longer match.
    """
    text = "Anna Svensson and Anna are different people."
    result = pseudonymize_text(text, ["Anna", "Anna Svensson"])
    anna_pokemon = name_to_pokemon("Anna")
    svensson_pokemon = name_to_pokemon("Anna Svensson")
    assert svensson_pokemon in result
    # The standalone Anna should still be replaced.
    assert anna_pokemon in result
    # The longer mapping must NOT contain the shorter mapping as a
    # substring of a corrupted earlier replace.
    assert "Anna" not in result


def test_pseudonymize_text_validation() -> None:
    with pytest.raises(TypeError):
        pseudonymize_text(42, ["Mikkel"])  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        pseudonymize_text("text", "Mikkel")  # type: ignore[arg-type]


def test_pseudonymize_text_with_custom_table_uses_that_table() -> None:
    table = ("Alpha", "Beta")
    text = "Mikkel reviewed it."
    result = pseudonymize_text(text, ["Mikkel"], pokemon_table=table)
    assert any(name in result for name in table)
    assert "Mikkel" not in result


def test_pseudonymize_text_is_deterministic_across_calls() -> None:
    text = "Mikkel and Anna and Bjorn worked together."
    names = ["Mikkel", "Anna", "Bjorn"]
    first = pseudonymize_text(text, names)
    for _ in range(5):
        assert pseudonymize_text(text, names) == first
