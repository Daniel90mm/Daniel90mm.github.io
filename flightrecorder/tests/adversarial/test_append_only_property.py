"""Property tests for append-only project document semantics.

The append-only contract is one of flightrecorder's hard rules: project
documents grow by accretion and the system never rewrites existing content.
The narrow cases are covered in `tests/unit/test_documents.py`. This module
covers the property the spec mandates:

    "After N appends, every input bullet is present in the output document,
    in some section, exactly once."

Plus the byte-level corollary: hand-written content surrounding the append
sites must survive unchanged.

The tests use seeded `random` (no hypothesis dependency) so failures are
reproducible by re-running with the same seed.
"""

from __future__ import annotations

import random
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from flightrecorder.documents import (
    PROJECT_SECTIONS,
    ProjectAppend,
    append_to_project_document,
    create_project_document,
    project_document_path,
)


SEEDS = [1, 2, 3, 17, 42, 137, 2026]
N_APPENDS = 40
SECTION_HEADER_RE = re.compile(r"(?m)^## (.+)$")


@dataclass(frozen=True)
class GeneratedAppend:
    """One synthetic append plus the nonce used to locate it later."""

    nonce: str
    append: ProjectAppend


def _generate_appends(rng: random.Random, count: int) -> list[GeneratedAppend]:
    """Build a list of distinct appends with monotonic timestamps."""

    base = datetime(2026, 5, 18, 12, 0, 0, tzinfo=timezone.utc)
    results: list[GeneratedAppend] = []
    for index in range(count):
        nonce = f"NONCE-{index:04d}-{rng.randrange(10**9):09d}"
        section = rng.choice(PROJECT_SECTIONS)
        timestamp = (base + timedelta(seconds=index)).isoformat()
        source = (
            f"2026-05-18-1200-fnirs-{rng.randrange(16**8):08x}"
            if rng.random() < 0.5
            else None
        )
        word = rng.choice(("investigate", "prototype", "review", "ship", "defer"))
        content = f"{word} thing {nonce}"
        results.append(
            GeneratedAppend(
                nonce=nonce,
                append=ProjectAppend(
                    project_ref="fnirs",
                    section=section,
                    content=content,
                    timestamp=timestamp,
                    source_session=source,
                ),
            )
        )
    return results


def _section_of(text: str, line: str) -> str:
    """Return the most recent `## <Section>` header above the given line."""

    idx = text.index(line)
    headers = list(SECTION_HEADER_RE.finditer(text[:idx]))
    assert headers, f"no section header precedes line: {line!r}"
    return headers[-1].group(1)


def _section_order(text: str) -> list[str]:
    return [match.group(1) for match in SECTION_HEADER_RE.finditer(text)]


@pytest.mark.parametrize("seed", SEEDS)
def test_every_bullet_present_exactly_once_in_target_section(
    tmp_path: Path,
    seed: int,
) -> None:
    """After N random appends each bullet appears once under its target section."""

    rng = random.Random(seed)
    create_project_document(
        tmp_path,
        "fnirs",
        datetime.fromisoformat("2026-05-18T12:00:00+00:00"),
    )
    appends = _generate_appends(rng, N_APPENDS)

    for generated in appends:
        append_to_project_document(tmp_path, generated.append)

    text = project_document_path(tmp_path, "fnirs").read_text(encoding="utf-8")

    for generated in appends:
        occurrences = text.count(generated.nonce)
        assert occurrences == 1, (
            f"seed={seed} nonce={generated.nonce} occurred {occurrences} times; "
            "append-only requires exactly once"
        )
        bullet_line = next(
            line for line in text.splitlines() if generated.nonce in line
        )
        assert _section_of(text, bullet_line) == generated.append.section


@pytest.mark.parametrize("seed", SEEDS)
def test_section_headers_remain_in_canonical_order(
    tmp_path: Path,
    seed: int,
) -> None:
    """No append reorders, drops, or duplicates the six section headers."""

    rng = random.Random(seed)
    create_project_document(
        tmp_path,
        "fnirs",
        datetime.fromisoformat("2026-05-18T12:00:00+00:00"),
    )

    for generated in _generate_appends(rng, N_APPENDS):
        append_to_project_document(tmp_path, generated.append)

    text = project_document_path(tmp_path, "fnirs").read_text(encoding="utf-8")
    assert _section_order(text) == list(PROJECT_SECTIONS)


@pytest.mark.parametrize("seed", SEEDS)
def test_handwritten_content_survives_byte_for_byte(
    tmp_path: Path,
    seed: int,
) -> None:
    """Pre-existing hand-written paragraphs and bullets are never rewritten."""

    rng = random.Random(seed)
    path = project_document_path(tmp_path, "fnirs")
    path.parent.mkdir(parents=True)
    handwritten_markers = {
        "Problem": "HAND-PROBLEM-paragraph that Daniel typed by hand",
        "Current state": "HAND-CURRENT-still bench-testing the AFE",
        "Decisions made": "- HAND-DECISION-use four wavelengths not three",
        "Open questions": "HAND-OPEN-do we need a reference channel?",
        "TODOs": "- HAND-TODO-order the photodiodes",
        "Ideas": "HAND-IDEA-multiplex the LEDs in software",
    }
    body_lines = [
        "---",
        "project: fnirs",
        "last_appended: 2026-05-01T00:00:00+00:00",
        "---",
        "",
        "# fnirs",
        "",
    ]
    for section in PROJECT_SECTIONS:
        body_lines.extend((f"## {section}", handwritten_markers[section], ""))
    original = "\n".join(body_lines)
    path.write_text(original, encoding="utf-8")

    for generated in _generate_appends(rng, N_APPENDS):
        append_to_project_document(tmp_path, generated.append)

    text = path.read_text(encoding="utf-8")
    for marker in handwritten_markers.values():
        assert text.count(marker) == 1, (
            f"seed={seed} hand-written marker {marker!r} was rewritten or dropped"
        )


@pytest.mark.parametrize("seed", SEEDS)
def test_last_appended_tracks_final_timestamp(tmp_path: Path, seed: int) -> None:
    """The frontmatter `last_appended` reflects the most recent append timestamp."""

    rng = random.Random(seed)
    create_project_document(
        tmp_path,
        "fnirs",
        datetime.fromisoformat("2026-05-18T12:00:00+00:00"),
    )
    appends = _generate_appends(rng, N_APPENDS)
    for generated in appends:
        append_to_project_document(tmp_path, generated.append)

    text = project_document_path(tmp_path, "fnirs").read_text(encoding="utf-8")
    final_timestamp = appends[-1].append.timestamp
    assert f"last_appended: {final_timestamp}" in text


@pytest.mark.parametrize("seed", SEEDS)
def test_total_bullet_count_equals_appends_plus_handwritten(
    tmp_path: Path,
    seed: int,
) -> None:
    """No append duplicates an existing bullet or invents extra bullets."""

    rng = random.Random(seed)
    path = project_document_path(tmp_path, "fnirs")
    path.parent.mkdir(parents=True)
    handwritten_bullets = {
        "Decisions made": "- HAND-DECISION-use four wavelengths not three",
        "TODOs": "- HAND-TODO-order the photodiodes",
    }
    body_lines = [
        "---",
        "project: fnirs",
        "last_appended: 2026-05-01T00:00:00+00:00",
        "---",
        "",
        "# fnirs",
        "",
    ]
    for section in PROJECT_SECTIONS:
        body_lines.append(f"## {section}")
        if section in handwritten_bullets:
            body_lines.append(handwritten_bullets[section])
        body_lines.append("")
    path.write_text("\n".join(body_lines), encoding="utf-8")

    for generated in _generate_appends(rng, N_APPENDS):
        append_to_project_document(tmp_path, generated.append)

    text = path.read_text(encoding="utf-8")
    bullet_lines = [line for line in text.splitlines() if line.startswith("- ")]
    assert len(bullet_lines) == N_APPENDS + len(handwritten_bullets), (
        f"seed={seed} unexpected bullet count: "
        f"got {len(bullet_lines)}, want {N_APPENDS + len(handwritten_bullets)}"
    )
