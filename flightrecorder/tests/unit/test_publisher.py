"""Unit tests for the publisher pipeline structural framework.

Covers the rejection-bias defaults, curator-output validation, per-snippet
reviewer routing, and rejection of every adversarial fixture under the
default Null* stages. No LLM is involved; tests inject stub curators and
reviewers and assert the framework wires inputs to outputs correctly.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from flightrecorder.publisher import (
    VERDICT_APPROVE,
    VERDICT_REJECT,
    ComposedPost,
    Curator,
    CuratorOutput,
    NullComposer,
    NullCurator,
    NullReviewer,
    PipelineResult,
    Reviewer,
    ReviewerVerdict,
    Snippet,
    adversarial_fixture_dir,
    make_publish_after,
    make_snippet_id,
    run_publish_pipeline,
)


def _snippet(snippet_id: str = "s1", body: str = "a real moment", source_id: str = "src-1") -> Snippet:
    return Snippet(
        snippet_id=snippet_id,
        source_kind="session",
        source_id=source_id,
        drafted_at="2026-05-18T12:00:00+00:00",
        publish_after="2026-05-19T12:00:00+00:00",
        tags=["fnirs"],
        project_ref="fnirs",
        body=body,
    )


class _ApprovingReviewer:
    def review(self, snippet, source_body):
        return ReviewerVerdict(snippet_id=snippet.snippet_id, verdict=VERDICT_APPROVE)


class _RejectingReviewer:
    def review(self, snippet, source_body):
        return ReviewerVerdict(
            snippet_id=snippet.snippet_id,
            verdict=VERDICT_REJECT,
            reasons=["mentions a real name"],
        )


class _MixedReviewer:
    """Approves snippets whose body contains 'GOOD', rejects everything else."""

    def review(self, snippet, source_body):
        verdict = VERDICT_APPROVE if "GOOD" in snippet.body else VERDICT_REJECT
        reasons = [] if verdict == VERDICT_APPROVE else ["body did not pass mixed gate"]
        return ReviewerVerdict(
            snippet_id=snippet.snippet_id,
            verdict=verdict,
            reasons=reasons,
        )


class _AmbiguousReviewer:
    """Returns a non-approve, non-reject verdict to test fail-closed routing."""

    def review(self, snippet, source_body):
        return ReviewerVerdict(snippet_id=snippet.snippet_id, verdict="maybe")


def _curator_emitting(snippets: list[Snippet]) -> Curator:
    class _StubCurator:
        def curate(self, source_kind, source_id, source_body):
            return CuratorOutput(
                source_kind=source_kind,
                source_id=source_id,
                publishable=True,
                snippets=snippets,
            )

    return _StubCurator()


def _empty_publishable_curator() -> Curator:
    """A curator that violates the contract by returning publishable=True but
    no snippets. The pipeline must reject this."""

    class _Curator:
        def curate(self, source_kind, source_id, source_body):
            return CuratorOutput(
                source_kind=source_kind,
                source_id=source_id,
                publishable=True,
                snippets=[],
            )

    return _Curator()


# --- Rejection-bias defaults ---


def test_null_curator_returns_not_publishable() -> None:
    output = NullCurator().curate("session", "src-1", "any body")
    assert output.publishable is False
    assert output.snippets == []
    assert output.rejection_reason == "curator not configured"


def test_null_reviewer_rejects() -> None:
    verdict = NullReviewer().review(_snippet(), "source body")
    assert verdict.verdict == VERDICT_REJECT
    assert verdict.reasons == ["reviewer not configured"]


def test_null_composer_returns_none() -> None:
    assert NullComposer().compose([_snippet()]) is None


def test_default_pipeline_publishes_nothing() -> None:
    """Empty stages plus a non-empty source: zero approved, curator's reason
    surfaced. This is the always-on fail-closed contract."""

    result = run_publish_pipeline(
        source_kind="session",
        source_id="src-1",
        source_body="some text that could have been redacted",
    )
    assert isinstance(result, PipelineResult)
    assert result.approved == []
    assert result.verdicts == []
    assert result.rejection_reason == "curator not configured"


# --- Curator-output validation ---


def test_curator_returns_not_publishable_short_circuits_reviewer() -> None:
    """If the curator rejects, the reviewer must not even be called."""

    reviewer_calls: list[Snippet] = []

    class _SpyReviewer:
        def review(self, snippet, source_body):
            reviewer_calls.append(snippet)
            return ReviewerVerdict(snippet_id=snippet.snippet_id, verdict=VERDICT_APPROVE)

    class _RejectingCurator:
        def curate(self, source_kind, source_id, source_body):
            return CuratorOutput(
                source_kind=source_kind,
                source_id=source_id,
                publishable=False,
                snippets=[],
                rejection_reason="contains sensitive medical content",
            )

    result = run_publish_pipeline(
        source_kind="session",
        source_id="src-1",
        source_body="body",
        curator=_RejectingCurator(),
        reviewer=_SpyReviewer(),
    )
    assert reviewer_calls == []
    assert result.approved == []
    assert result.rejection_reason == "contains sensitive medical content"


def test_publishable_true_with_no_snippets_is_treated_as_curator_bug() -> None:
    result = run_publish_pipeline(
        source_kind="session",
        source_id="src-1",
        source_body="body",
        curator=_empty_publishable_curator(),
        reviewer=_ApprovingReviewer(),
    )
    assert result.approved == []
    assert result.rejection_reason is not None
    assert "emitted no snippets" in result.rejection_reason


# --- Reviewer routing ---


def test_approved_snippet_lands_in_approved() -> None:
    snippet = _snippet(body="something real")
    result = run_publish_pipeline(
        source_kind="session",
        source_id="src-1",
        source_body="body",
        curator=_curator_emitting([snippet]),
        reviewer=_ApprovingReviewer(),
    )
    assert result.approved == [snippet]
    assert len(result.verdicts) == 1
    assert result.verdicts[0].verdict == VERDICT_APPROVE


def test_rejected_snippet_is_dropped_but_verdict_kept() -> None:
    snippet = _snippet(body="something")
    result = run_publish_pipeline(
        source_kind="session",
        source_id="src-1",
        source_body="body",
        curator=_curator_emitting([snippet]),
        reviewer=_RejectingReviewer(),
    )
    assert result.approved == []
    assert len(result.verdicts) == 1
    assert result.verdicts[0].verdict == VERDICT_REJECT


def test_mixed_reviewer_keeps_only_approved_snippets() -> None:
    good = _snippet(snippet_id="s1", body="this is GOOD content")
    bad = _snippet(snippet_id="s2", body="this is bad content")
    result = run_publish_pipeline(
        source_kind="session",
        source_id="src-1",
        source_body="body",
        curator=_curator_emitting([good, bad]),
        reviewer=_MixedReviewer(),
    )
    assert [s.snippet_id for s in result.approved] == ["s1"]
    assert [v.verdict for v in result.verdicts] == [VERDICT_APPROVE, VERDICT_REJECT]


def test_ambiguous_verdict_is_treated_as_reject() -> None:
    """A reviewer that returns anything other than approve must NOT publish.
    The framework refuses to assume ambiguous output is safe."""

    snippet = _snippet(body="ambiguous content")
    result = run_publish_pipeline(
        source_kind="session",
        source_id="src-1",
        source_body="body",
        curator=_curator_emitting([snippet]),
        reviewer=_AmbiguousReviewer(),
    )
    assert result.approved == []
    assert result.verdicts[0].verdict == "maybe"


def test_snippet_with_empty_body_is_dropped_even_when_approved() -> None:
    """Belt-and-braces: if a reviewer approves an empty snippet body, the
    pipeline still drops it."""

    snippet = _snippet(body="   \n  ")
    result = run_publish_pipeline(
        source_kind="session",
        source_id="src-1",
        source_body="body",
        curator=_curator_emitting([snippet]),
        reviewer=_ApprovingReviewer(),
    )
    assert result.approved == []
    assert result.verdicts[0].verdict == VERDICT_APPROVE


# --- Adversarial fixtures pass fail-closed ---


def _adversarial_fixture_paths() -> list[Path]:
    return sorted(adversarial_fixture_dir().glob("*.txt"))


@pytest.mark.parametrize(
    "fixture_path",
    _adversarial_fixture_paths(),
    ids=lambda p: p.stem,
)
def test_default_pipeline_rejects_every_adversarial_fixture(fixture_path: Path) -> None:
    """Every doxxing fixture (real-looking names, emails, repo urls, etc.)
    must produce zero approved output under the Null* defaults. Any future
    regression that loosens the default would surface here."""

    source_body = fixture_path.read_text(encoding="utf-8")
    result = run_publish_pipeline(
        source_kind="adversarial",
        source_id=fixture_path.stem,
        source_body=source_body,
    )
    assert result.approved == []
    assert result.rejection_reason is not None


def test_adversarial_fixtures_exist() -> None:
    paths = _adversarial_fixture_paths()
    assert len(paths) >= 5, (
        "expected the publisher adversarial fixture inventory to be populated"
    )


# --- Helpers ---


def test_make_snippet_id_is_stable_and_padded() -> None:
    assert make_snippet_id("session-id", 0) == "session-id-00"
    assert make_snippet_id("session-id", 7) == "session-id-07"
    assert make_snippet_id("session-id", 13) == "session-id-13"


def test_make_publish_after_offsets_by_24h_by_default() -> None:
    from datetime import datetime, timezone

    drafted = datetime(2026, 5, 18, 12, 0, 0, tzinfo=timezone.utc)
    publish_after = make_publish_after(drafted)
    assert publish_after == "2026-05-19T12:00:00+00:00"


def test_make_publish_after_honors_custom_delay() -> None:
    from datetime import datetime, timezone

    drafted = datetime(2026, 5, 18, 12, 0, 0, tzinfo=timezone.utc)
    publish_after = make_publish_after(drafted, delay_hours=48)
    assert publish_after == "2026-05-20T12:00:00+00:00"


# --- Composer is a Protocol shell (no production wiring this round) ---


def test_composer_protocol_allows_returning_a_post() -> None:
    """Sanity check that a composer implementation can return a ComposedPost."""

    class _StubComposer:
        def compose(self, approved_snippets):
            if not approved_snippets:
                return None
            return ComposedPost(
                date="2026-05-18",
                slug="test-post",
                snippet_ids=[s.snippet_id for s in approved_snippets],
                body="composed body",
            )

    composer = _StubComposer()
    assert composer.compose([]) is None
    post = composer.compose([_snippet(snippet_id="s1")])
    assert isinstance(post, ComposedPost)
    assert post.snippet_ids == ["s1"]
