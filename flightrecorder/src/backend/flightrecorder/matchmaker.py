"""Matchmaker: propose links between loose spaghetti ideas and existing projects.

This module is the structural framework for build-order step 11. The
matchmaker reads a snapshot of spaghetti ideas and project summaries, hands
each (idea, project) pair to a `MatchScorer`, and assembles a `MatchBatch`
with confidence-thresholded candidates plus the ids of every idea that was
considered but rejected.

The default scorer is `NullScorer` and rejects everything. That is the
correct default until an LLM scorer is wired (deferred to a later step):
the spec's matchmaker contract is "reject by default - rationalizing weak
matches is the failure mode this design prevents." `NullScorer` makes that
default explicit. Production runs will swap in `LlmScorer` once the
matchmaker prompt and provider call are approved.

No LLM is called here. No prompt is read here. The module is pure Python
with no external state.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Protocol


DEFAULT_MIN_CONFIDENCE = 0.7
"""Confidence threshold below which a scorer's proposal is discarded.

Set high so the matchmaker rejects weak signals. The doc
docs/MATCHMAKER_REJECTION_FIXTURES.md describes the four scenarios this
threshold protects against.
"""


@dataclass(frozen=True)
class ProjectSummary:
    """One project the matchmaker can route ideas to."""

    ref: str
    summary: str
    tags: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class SpaghettiIdea:
    """One loose idea pulled from the spaghetti wall."""

    idea_id: str
    content: str
    tags: list[str] = field(default_factory=list)
    topics: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class MatchCandidate:
    """One proposed match between an idea and a project."""

    idea_id: str
    project_ref: str
    confidence: float
    rationale: str


@dataclass(frozen=True)
class MatchBatch:
    """The output of one matchmaker run."""

    batch_id: str
    generated_at: str
    candidates: list[MatchCandidate]
    rejected_idea_ids: list[str]


class MatchScorer(Protocol):
    """Strategy for scoring a single (idea, project) pair.

    Implementations return None to reject the pair outright (the default
    case for almost all pairs) or a tuple (confidence, rationale) when the
    scorer wants to propose a match. Confidence is in [0.0, 1.0]; the
    matchmaker still filters against `min_confidence` before accepting.

    Rationale is a short sentence stating *why* this idea fits this
    project. Generic "could be useful here" rationales are themselves a
    rejection-bias smell - implementations should be specific or return
    None.
    """

    def score(
        self,
        idea: SpaghettiIdea,
        project: ProjectSummary,
    ) -> tuple[float, str] | None:
        ...


class NullScorer:
    """Default scorer. Rejects every pair. The right default until the
    LLM scorer is wired."""

    def score(
        self,
        idea: SpaghettiIdea,
        project: ProjectSummary,
    ) -> tuple[float, str] | None:
        return None


def propose_matches(
    ideas: list[SpaghettiIdea],
    projects: list[ProjectSummary],
    scorer: MatchScorer | None = None,
    min_confidence: float = DEFAULT_MIN_CONFIDENCE,
    now: datetime | None = None,
) -> MatchBatch:
    """Run the matchmaker over ideas x projects with rejection-bias defaults."""

    if not 0.0 <= min_confidence <= 1.0:
        raise ValueError("min_confidence must be in [0.0, 1.0]")

    active_scorer: MatchScorer = scorer if scorer is not None else NullScorer()
    generated_dt = now if now is not None else datetime.now(timezone.utc)
    generated_at = generated_dt.isoformat()

    candidates: list[MatchCandidate] = []
    matched: set[str] = set()

    for idea in ideas:
        for project in projects:
            result = active_scorer.score(idea, project)
            if result is None:
                continue
            confidence, rationale = result
            _validate_score(confidence, rationale, idea.idea_id, project.ref)
            if confidence < min_confidence:
                continue
            candidates.append(
                MatchCandidate(
                    idea_id=idea.idea_id,
                    project_ref=project.ref,
                    confidence=confidence,
                    rationale=rationale,
                )
            )
            matched.add(idea.idea_id)

    rejected = [idea.idea_id for idea in ideas if idea.idea_id not in matched]

    return MatchBatch(
        batch_id=_make_batch_id(generated_dt),
        generated_at=generated_at,
        candidates=candidates,
        rejected_idea_ids=rejected,
    )


def load_scenario_fixture(path: Path) -> tuple[SpaghettiIdea, list[ProjectSummary]]:
    """Load one matchmaker rejection-bias scenario into typed inputs.

    Used by tests against `tests/fixtures/matchmaker/scenario_*.json`. The
    fixture's spaghetti text becomes a single SpaghettiIdea whose idea_id
    is the scenario id; each project becomes a ProjectSummary.
    """

    data = json.loads(path.read_text(encoding="utf-8"))
    idea = SpaghettiIdea(
        idea_id=str(data["scenario_id"]),
        content=str(data["spaghetti"]),
        tags=[],
        topics=[],
    )
    projects = [
        ProjectSummary(ref=str(item["ref"]), summary=str(item["summary"]))
        for item in data["projects"]
    ]
    return idea, projects


def _make_batch_id(generated_at: datetime) -> str:
    return generated_at.strftime("matches-%Y-%m-%dT%H%M%SZ")


def _validate_score(
    confidence: float,
    rationale: str,
    idea_id: str,
    project_ref: str,
) -> None:
    if not 0.0 <= confidence <= 1.0:
        raise ValueError(
            f"scorer returned confidence {confidence} out of range for "
            f"{idea_id} -> {project_ref}"
        )
    if not isinstance(rationale, str) or not _rationale_pattern.match(rationale):
        raise ValueError(
            f"scorer returned empty/whitespace rationale for "
            f"{idea_id} -> {project_ref}"
        )


_rationale_pattern = re.compile(r"\S")
