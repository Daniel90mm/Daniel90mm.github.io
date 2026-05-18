"""Unit tests for the matchmaker structural framework.

Covers the rejection-bias default, threshold filtering, batch shape, and
fixture loading. No LLM is involved; tests inject stub scorers and assert
the framework wires inputs to outputs correctly.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from flightrecorder.matchmaker import (
    DEFAULT_MIN_CONFIDENCE,
    MatchBatch,
    MatchCandidate,
    MatchScorer,
    NullScorer,
    ProjectSummary,
    SpaghettiIdea,
    load_scenario_fixture,
    propose_matches,
)


FIXTURES_DIR = (
    Path(__file__).resolve().parent.parent / "fixtures" / "matchmaker"
)
ALL_SCENARIOS = sorted(FIXTURES_DIR.glob("scenario_*.json"))


def _idea(idea_id: str = "idea-1", content: str = "some loose thought") -> SpaghettiIdea:
    return SpaghettiIdea(idea_id=idea_id, content=content, tags=[], topics=[])


def _project(ref: str = "fnirs", summary: str = "biophotonics rig") -> ProjectSummary:
    return ProjectSummary(ref=ref, summary=summary)


class _AlwaysScorer:
    """Test scorer that returns a fixed (confidence, rationale) for every pair."""

    def __init__(self, confidence: float, rationale: str = "stub rationale") -> None:
        self._confidence = confidence
        self._rationale = rationale

    def score(
        self,
        idea: SpaghettiIdea,
        project: ProjectSummary,
    ) -> tuple[float, str] | None:
        return self._confidence, self._rationale


class _SelectiveScorer:
    """Scorer that matches only when (idea_id, project_ref) is in an allow-list."""

    def __init__(self, allow: set[tuple[str, str]], confidence: float = 0.9) -> None:
        self._allow = allow
        self._confidence = confidence

    def score(
        self,
        idea: SpaghettiIdea,
        project: ProjectSummary,
    ) -> tuple[float, str] | None:
        if (idea.idea_id, project.ref) not in self._allow:
            return None
        return self._confidence, f"{idea.idea_id} fits {project.ref} for a specific reason"


# --- Rejection-bias defaults ---


def test_null_scorer_returns_none_for_every_pair() -> None:
    scorer = NullScorer()
    assert scorer.score(_idea(), _project()) is None


def test_propose_matches_defaults_to_null_scorer_so_no_candidates() -> None:
    batch = propose_matches(
        ideas=[_idea("a"), _idea("b")],
        projects=[_project("p1"), _project("p2")],
    )
    assert batch.candidates == []
    assert set(batch.rejected_idea_ids) == {"a", "b"}


@pytest.mark.parametrize("scenario_path", ALL_SCENARIOS, ids=lambda p: p.stem)
def test_default_scorer_rejects_every_rejection_fixture(scenario_path: Path) -> None:
    """The structural-only matchmaker rejects every fixture, including the
    scenario_04 multi-match case. That match arrives once the LLM scorer
    is wired. Until then, rejection is the safe default for all four."""

    idea, projects = load_scenario_fixture(scenario_path)
    batch = propose_matches(ideas=[idea], projects=projects)
    assert batch.candidates == []
    assert batch.rejected_idea_ids == [idea.idea_id]


# --- Threshold filtering ---


def test_confidence_below_threshold_is_discarded() -> None:
    batch = propose_matches(
        ideas=[_idea("a")],
        projects=[_project("p1")],
        scorer=_AlwaysScorer(confidence=DEFAULT_MIN_CONFIDENCE - 0.01),
    )
    assert batch.candidates == []
    assert batch.rejected_idea_ids == ["a"]


def test_confidence_at_threshold_is_accepted() -> None:
    batch = propose_matches(
        ideas=[_idea("a")],
        projects=[_project("p1")],
        scorer=_AlwaysScorer(confidence=DEFAULT_MIN_CONFIDENCE),
    )
    assert len(batch.candidates) == 1
    assert batch.candidates[0].confidence == DEFAULT_MIN_CONFIDENCE
    assert batch.rejected_idea_ids == []


def test_custom_min_confidence_overrides_default() -> None:
    batch = propose_matches(
        ideas=[_idea("a")],
        projects=[_project("p1")],
        scorer=_AlwaysScorer(confidence=0.5),
        min_confidence=0.4,
    )
    assert len(batch.candidates) == 1


def test_min_confidence_out_of_range_raises() -> None:
    with pytest.raises(ValueError):
        propose_matches(ideas=[_idea()], projects=[_project()], min_confidence=1.5)
    with pytest.raises(ValueError):
        propose_matches(ideas=[_idea()], projects=[_project()], min_confidence=-0.1)


# --- Scorer-returned junk is rejected loudly ---


def test_score_out_of_range_raises() -> None:
    class _BadScorer:
        def score(self, idea, project):
            return 1.5, "fine"

    with pytest.raises(ValueError, match="out of range"):
        propose_matches(
            ideas=[_idea("a")],
            projects=[_project("p")],
            scorer=_BadScorer(),
        )


def test_empty_rationale_raises() -> None:
    class _BlankRationale:
        def score(self, idea, project):
            return 0.9, "   "

    with pytest.raises(ValueError, match="rationale"):
        propose_matches(
            ideas=[_idea("a")],
            projects=[_project("p")],
            scorer=_BlankRationale(),
        )


# --- Batch shape and accumulation ---


def test_genuine_multi_match_propagates_each_independently() -> None:
    """Scenario 4 in the rejection fixtures: one idea, two projects, both match.
    Verifies that when the scorer DOES return matches, both come through with
    distinct rationales."""

    idea, projects = load_scenario_fixture(
        FIXTURES_DIR / "scenario_04_genuine_multi.json"
    )
    allow = {(idea.idea_id, project.ref) for project in projects}
    batch = propose_matches(
        ideas=[idea],
        projects=projects,
        scorer=_SelectiveScorer(allow=allow, confidence=0.85),
    )

    assert len(batch.candidates) == 2
    refs = sorted(c.project_ref for c in batch.candidates)
    assert refs == sorted(p.ref for p in projects)
    assert batch.rejected_idea_ids == []
    for candidate in batch.candidates:
        assert candidate.rationale.strip() != ""
        assert candidate.idea_id == idea.idea_id


def test_mixed_outcome_rejects_only_unmatched_ideas() -> None:
    ideas = [_idea("matched"), _idea("not-matched")]
    projects = [_project("p1"), _project("p2")]
    allow = {("matched", "p1")}
    batch = propose_matches(
        ideas=ideas,
        projects=projects,
        scorer=_SelectiveScorer(allow=allow),
    )

    assert [c.idea_id for c in batch.candidates] == ["matched"]
    assert batch.rejected_idea_ids == ["not-matched"]


def test_batch_metadata_uses_provided_now() -> None:
    when = datetime(2026, 5, 18, 18, 0, 0, tzinfo=timezone.utc)
    batch = propose_matches(
        ideas=[_idea("a")],
        projects=[_project("p")],
        scorer=NullScorer(),
        now=when,
    )
    assert batch.generated_at == when.isoformat()
    assert batch.batch_id == "matches-2026-05-18T180000Z"


def test_batch_is_a_dataclass_with_expected_shape() -> None:
    batch = propose_matches(ideas=[_idea("a")], projects=[_project("p")])
    assert isinstance(batch, MatchBatch)
    assert isinstance(batch.batch_id, str)
    assert isinstance(batch.generated_at, str)
    assert isinstance(batch.candidates, list)
    assert isinstance(batch.rejected_idea_ids, list)


# --- Fixture loader ---


@pytest.mark.parametrize("scenario_path", ALL_SCENARIOS, ids=lambda p: p.stem)
def test_load_scenario_fixture_returns_typed_inputs(scenario_path: Path) -> None:
    idea, projects = load_scenario_fixture(scenario_path)
    assert isinstance(idea, SpaghettiIdea)
    assert idea.idea_id != ""
    assert idea.content != ""
    assert len(projects) >= 1
    for project in projects:
        assert isinstance(project, ProjectSummary)
        assert project.ref != ""
        assert project.summary != ""
