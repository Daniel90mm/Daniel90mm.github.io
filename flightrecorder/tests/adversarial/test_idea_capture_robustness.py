"""Adversarial robustness tests for parse_idea_operations.

Every test feeds malformed input and asserts the parser fails closed by
raising IdeaCaptureError (or a subclass/related error). The parser must
never return partial results.
"""

from __future__ import annotations

import json

import pytest

from flightrecorder.documents import ProjectDocumentError
from flightrecorder.idea_capture import MAX_IDEA_OPERATIONS, IdeaCaptureError, parse_idea_operations


def valid_project_append() -> dict[str, object]:
    return {
        "type": "project_append",
        "project_ref": "fnirs",
        "section": "TODOs",
        "content": "do something",
    }


def valid_spaghetti() -> dict[str, object]:
    return {
        "type": "spaghetti",
        "tags": ["pca"],
        "topics": ["signal-processing"],
        "content": "PCA for multivariate signal denoising.",
    }


# --- 1. Empty / whitespace-only ---

@pytest.mark.parametrize(
    "raw",
    [
        "",
        "   ",
        "\n\n",
        "\t",
    ],
)
def test_empty_or_whitespace_raises(raw: str) -> None:
    with pytest.raises((IdeaCaptureError, json.JSONDecodeError)):
        parse_idea_operations(raw)


# --- 2. Non-array JSON types ---

@pytest.mark.parametrize(
    "raw",
    [
        "42",
        '"hello"',
        "null",
        "true",
        "false",
        '{"key": "value"}',
    ],
)
def test_non_array_json_raises(raw: str) -> None:
    with pytest.raises(IdeaCaptureError):
        parse_idea_operations(raw)


# --- 3. Array containing non-object elements ---

@pytest.mark.parametrize(
    "raw",
    [
        json.dumps([1]),
        json.dumps(["x"]),
        json.dumps([None]),
        json.dumps([1, {"type": "spaghetti", "tags": ["x"], "topics": [], "content": "y"}]),
    ],
)
def test_array_with_non_object_elements_raises(raw: str) -> None:
    with pytest.raises(IdeaCaptureError):
        parse_idea_operations(raw)


# --- 4. project_append missing required fields ---

@pytest.mark.parametrize(
    "drop_key",
    ["project_ref", "section", "content"],
)
def test_project_append_missing_required_field_raises(drop_key: str) -> None:
    op = valid_project_append()
    del op[drop_key]
    raw = json.dumps([op])

    with pytest.raises(IdeaCaptureError):
        parse_idea_operations(raw)


# --- 5. project_append with invalid section ---

@pytest.mark.parametrize(
    "section",
    [
        "Roadmap",
        "todos",
        "",
        "   ",
    ],
)
def test_project_append_invalid_section_raises(section: str) -> None:
    op = valid_project_append()
    op["section"] = section
    raw = json.dumps([op])

    with pytest.raises(IdeaCaptureError):
        parse_idea_operations(raw)


# --- 6. project_append with project_ref that sanitizes to empty ---

@pytest.mark.parametrize(
    "project_ref",
    [
        "   ",
        "...",
        "!!!",
    ],
)
def test_project_append_empty_slug_ref_raises(project_ref: str) -> None:
    op = valid_project_append()
    op["project_ref"] = project_ref
    raw = json.dumps([op])

    with pytest.raises((IdeaCaptureError, ProjectDocumentError)):
        parse_idea_operations(raw)


# --- 7. spaghetti with tags not a list ---

@pytest.mark.parametrize(
    "tags",
    [
        "pca",
        42,
        {"key": "value"},
    ],
)
def test_spaghetti_tags_not_list_raises(tags: object) -> None:
    op = valid_spaghetti()
    op["tags"] = tags
    raw = json.dumps([op])

    with pytest.raises(IdeaCaptureError):
        parse_idea_operations(raw)


# --- 8. spaghetti with tags containing non-string entry ---

@pytest.mark.parametrize(
    "tags",
    [
        ["pca", 1],
        ["pca", None],
        ["pca", True],
        ["pca", []],
        ["pca", {}],
    ],
)
def test_spaghetti_tags_with_non_string_entry_raises(tags: list[object]) -> None:
    op = valid_spaghetti()
    op["tags"] = tags
    raw = json.dumps([op])

    with pytest.raises(IdeaCaptureError):
        parse_idea_operations(raw)


# --- 9. spaghetti with empty content after strip ---

@pytest.mark.parametrize(
    "content",
    [
        "",
        "   ",
        "\n",
    ],
)
def test_spaghetti_empty_content_raises(content: str) -> None:
    op = valid_spaghetti()
    op["content"] = content
    raw = json.dumps([op])

    with pytest.raises(IdeaCaptureError):
        parse_idea_operations(raw)


# --- 10. Too many operations ---

def test_too_many_operations_raises() -> None:
    ops = [valid_spaghetti() for _ in range(MAX_IDEA_OPERATIONS + 1)]
    raw = json.dumps(ops)

    with pytest.raises(IdeaCaptureError):
        parse_idea_operations(raw)


# --- 11. Unknown type / missing type ---

@pytest.mark.parametrize(
    "operation",
    [
        {"type": "draft", "content": "x", "tags": ["a"], "topics": []},
        {"content": "x", "tags": ["a"], "topics": []},
    ],
)
def test_unknown_or_missing_type_raises(operation: dict[str, object]) -> None:
    raw = json.dumps([operation])

    with pytest.raises(IdeaCaptureError):
        parse_idea_operations(raw)


# --- 12. Deeply nested junk ---

@pytest.mark.parametrize(
    "raw",
    [
        json.dumps([[[[]]]]),
        json.dumps([{"type": ["project_append"]}]),
        json.dumps([{"type": "project_append", "project_ref": "x", "section": "TODOs", "content": [1, 2, 3]}]),
        json.dumps([{"type": "spaghetti", "tags": "x", "topics": [], "content": {"nested": 1}}]),
    ],
)
def test_deeply_nested_junk_raises(raw: str) -> None:
    with pytest.raises((IdeaCaptureError, TypeError, ProjectDocumentError)):
        parse_idea_operations(raw)
