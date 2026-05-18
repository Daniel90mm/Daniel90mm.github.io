"""Publisher pipeline: curator + reviewer + composer structural framework.

This is the build-order step 12 baseline. The actual redaction work is done
by LLM calls behind these Protocol interfaces; this module wires the three
stages together with fail-closed defaults so the pipeline cannot publish
anything until each stage is explicitly configured.

The doxxing-safety contract from `flightrecorder/CLAUDE.md` is the
controlling document:

    > The curator and reviewer are not "guidelines." They are the only
    > thing between Daniel's raw brainstorms and the open web. The
    > pipeline auto-publishes on a 24h delay with no human approval step.

The defaults here enforce the "reject by default" stance:

- `NullCurator.curate` returns a `CuratorOutput` with `publishable=False`
  and zero snippets.
- `NullReviewer.review` returns `verdict="reject"`.
- `NullComposer.compose` returns `None`.

`run_publish_pipeline` short-circuits as soon as any stage rejects. The
caller's only path to publishable output is to inject configured stages
with passing verdicts; a misconfigured pipeline silently produces zero.

No prompt is loaded here. No provider is called here. The module is pure
Python with no external state.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Protocol


WHITELIST_NAMES = frozenset({"daniel"})
"""Real names that may appear in published output. Anything else must be
pseudonymized or removed by the curator. Treated as case-insensitive."""


VERDICT_APPROVE = "approve"
VERDICT_REJECT = "reject"


@dataclass(frozen=True)
class Snippet:
    """One drafted log snippet, project doc redaction, or spaghetti redaction.

    The `source_kind` discriminator lets the publisher route the snippet
    to the right Hugo content path (`/log/`, `/projects/<ref>.md`,
    `/wall/<idea-id>.md`) without re-parsing the body.
    """

    snippet_id: str
    source_kind: str
    source_id: str
    drafted_at: str
    publish_after: str
    tags: list[str]
    project_ref: str | None
    body: str


@dataclass(frozen=True)
class CuratorOutput:
    """One curator pass over one source artifact.

    `publishable=False` means the curator chose to emit nothing (e.g.
    `NOT_PUBLISHABLE` for a sensitive spaghetti idea, `NO_SNIPPETS` for a
    session of small talk). In that case `snippets` must be empty.

    `publishable=True` with empty `snippets` is invalid - callers should
    treat it as a curator bug and reject.
    """

    source_kind: str
    source_id: str
    publishable: bool
    snippets: list[Snippet] = field(default_factory=list)
    rejection_reason: str | None = None


@dataclass(frozen=True)
class ReviewerVerdict:
    """Adversarial reviewer's call on one snippet.

    The verdict is binary. `reasons` is required when the verdict is
    reject; it documents why so the curator prompt can be tuned. Empty
    `reasons` on a reject is itself a smell.

    `redactions` is the reviewer's suggested fix list (find/replace
    pairs). The framework does not auto-apply them - that is a separate
    judgment call documented in the spec.
    """

    snippet_id: str
    verdict: str
    reasons: list[str] = field(default_factory=list)
    redactions: list[dict[str, str]] = field(default_factory=list)


@dataclass(frozen=True)
class ComposedPost:
    """A daily log entry composed from approved snippets."""

    date: str
    slug: str
    snippet_ids: list[str]
    body: str


@dataclass(frozen=True)
class PipelineResult:
    """The full audit trail of one publisher pipeline run."""

    source_kind: str
    source_id: str
    approved: list[Snippet]
    verdicts: list[ReviewerVerdict]
    rejection_reason: str | None
    """Set when the curator stage rejected the whole source. None when the
    curator returned snippets (the per-snippet verdicts may still be
    rejects)."""


class Curator(Protocol):
    """Stage 1. Turns a source artifact into 0..N drafted snippets."""

    def curate(
        self,
        source_kind: str,
        source_id: str,
        source_body: str,
    ) -> CuratorOutput:
        ...


class Reviewer(Protocol):
    """Stage 2. Adversarial pass over one snippet against the source.

    Implementations should bias toward rejection. Spec section 8.6: "False
    rejects are cheap; false approves are not."
    """

    def review(self, snippet: Snippet, source_body: str) -> ReviewerVerdict:
        ...


class Composer(Protocol):
    """Stage 3. Composes a daily log post from approved snippets.

    Returns None when there is no publishable post for this batch (the
    quiet-day case)."""

    def compose(self, approved_snippets: list[Snippet]) -> ComposedPost | None:
        ...


class NullCurator:
    """Default curator. Emits nothing. Safe until the LLM curator is wired."""

    def curate(
        self,
        source_kind: str,
        source_id: str,
        source_body: str,
    ) -> CuratorOutput:
        return CuratorOutput(
            source_kind=source_kind,
            source_id=source_id,
            publishable=False,
            snippets=[],
            rejection_reason="curator not configured",
        )


class NullReviewer:
    """Default reviewer. Rejects every snippet. Safe until the LLM reviewer is wired."""

    def review(self, snippet: Snippet, source_body: str) -> ReviewerVerdict:
        return ReviewerVerdict(
            snippet_id=snippet.snippet_id,
            verdict=VERDICT_REJECT,
            reasons=["reviewer not configured"],
            redactions=[],
        )


class NullComposer:
    """Default composer. Composes nothing."""

    def compose(self, approved_snippets: list[Snippet]) -> ComposedPost | None:
        return None


def run_publish_pipeline(
    source_kind: str,
    source_id: str,
    source_body: str,
    curator: Curator | None = None,
    reviewer: Reviewer | None = None,
) -> PipelineResult:
    """Run curator -> reviewer on one source, returning a full audit trail.

    Rejection-bias guarantees enforced here, on top of whatever each stage
    enforces:

    - If the curator returns `publishable=False`, the result has empty
      approved/verdicts and the curator's rejection_reason is surfaced.
    - If the curator returns `publishable=True` with zero snippets, that
      is treated as a curator bug and the whole source is rejected.
    - Each snippet is reviewed independently. Only snippets with
      `verdict == "approve"` and non-empty body land in `approved`.
    - A reviewer verdict that is neither approve nor reject is treated as
      reject. The framework never assumes ambiguity is safe.
    """

    active_curator: Curator = curator if curator is not None else NullCurator()
    active_reviewer: Reviewer = reviewer if reviewer is not None else NullReviewer()

    output = active_curator.curate(source_kind, source_id, source_body)

    if not output.publishable:
        return PipelineResult(
            source_kind=source_kind,
            source_id=source_id,
            approved=[],
            verdicts=[],
            rejection_reason=output.rejection_reason or "curator rejected",
        )
    if not output.snippets:
        return PipelineResult(
            source_kind=source_kind,
            source_id=source_id,
            approved=[],
            verdicts=[],
            rejection_reason="curator publishable=True but emitted no snippets",
        )

    verdicts: list[ReviewerVerdict] = []
    approved: list[Snippet] = []
    for snippet in output.snippets:
        verdict = active_reviewer.review(snippet, source_body)
        verdicts.append(verdict)
        if verdict.verdict != VERDICT_APPROVE:
            continue
        if not snippet.body.strip():
            continue
        approved.append(snippet)

    return PipelineResult(
        source_kind=source_kind,
        source_id=source_id,
        approved=approved,
        verdicts=verdicts,
        rejection_reason=None,
    )


def make_snippet_id(source_id: str, index: int) -> str:
    """Stable snippet id derived from source + index, per spec section 8.5."""

    return f"{source_id}-{index:02d}"


def make_publish_after(drafted_at: datetime, delay_hours: int = 24) -> str:
    """The 24h delay before a drafted snippet may be published."""

    from datetime import timedelta

    return (drafted_at + timedelta(hours=delay_hours)).isoformat()


def adversarial_fixture_dir() -> Path:
    """Repo-relative path to the adversarial doxxing fixtures."""

    return (
        Path(__file__).resolve().parent.parent.parent.parent
        / "tests"
        / "fixtures"
        / "adversarial"
    )
