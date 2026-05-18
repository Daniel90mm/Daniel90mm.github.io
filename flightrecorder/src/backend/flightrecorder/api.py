"""HTTP API routes for flightrecorder."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, File, HTTPException, Query, Request, UploadFile, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from pathlib import Path

from flightrecorder.costs import BudgetHardStopError, ProviderUsage
from flightrecorder.documents import create_project_document
from flightrecorder.idea_capture import (
    IDEA_CAPTURE_PROMPT,
    IdeaCaptureError,
    ProjectAppendOperation,
    apply_idea_operations,
    parse_idea_operations,
    run_idea_capture,
    transcript_from_messages,
)
from flightrecorder.matchmaker import (
    MatchBatch,
    ProjectSummary,
    SpaghettiIdea,
    propose_matches,
)
from flightrecorder.project_registry import ProjectRegistryError, load_project_registry
from flightrecorder.providers import Message, TokenEvent, UsageEvent
from flightrecorder.serializers import session_detail_to_dict, session_metadata_to_dict
from flightrecorder.storage import AssetTooLargeError, ChatMessage


router = APIRouter(prefix="/api")


class CreateSessionRequest(BaseModel):
    provider: str = Field(min_length=1)
    model: str = Field(min_length=1)
    slug: str = "session"


class ChatRequest(BaseModel):
    content: str = Field(max_length=32768)


@router.post(
    "/sessions",
    status_code=status.HTTP_201_CREATED,
)
async def create_session(
    payload: CreateSessionRequest,
    request: Request,
) -> dict[str, object]:
    """Create a new empty session."""

    runtime = request.app.state.runtime
    metadata = runtime.sessions.create_session(
        provider=payload.provider,
        model=payload.model,
        slug=payload.slug,
        started_at=datetime.now(timezone.utc),
    )
    return {
        "session_id": metadata.session_id,
        "started_at": metadata.started_at,
        "provider": metadata.provider,
        "model": metadata.model,
        "message_count": metadata.message_count,
        "image_count": metadata.image_count,
    }


@router.get("/sessions")
async def list_sessions(
    request: Request,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    curated: bool | None = None,
) -> dict[str, object]:
    """List sessions newest first."""

    runtime = request.app.state.runtime
    sessions = runtime.sessions.list_sessions()
    if curated is not None:
        sessions = [metadata for metadata in sessions if metadata.curated is curated]

    page = sessions[offset : offset + limit]
    return {
        "sessions": [session_metadata_to_dict(metadata) for metadata in page],
        "total": len(sessions),
    }


@router.get("/sessions/{session_id}")
async def get_session(session_id: str, request: Request) -> dict[str, object]:
    """Fetch a single session including transcript messages."""

    runtime = request.app.state.runtime
    try:
        metadata, messages = runtime.sessions.get_session(session_id)
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        ) from exc
    return session_detail_to_dict(metadata, messages)


@router.post(
    "/sessions/{session_id}/upload",
    status_code=status.HTTP_201_CREATED,
)
async def upload_session_asset(
    session_id: str,
    request: Request,
    file: UploadFile = File(...),
) -> dict[str, Any]:
    """Upload one image asset to a session."""

    runtime = request.app.state.runtime
    data = await file.read()
    try:
        asset_path = runtime.sessions.store_asset(
            session_id=session_id,
            filename=file.filename or "upload",
            data=data,
        )
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        ) from exc
    except AssetTooLargeError as exc:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail="image upload exceeds 5 MiB cap",
        ) from exc

    metadata, _messages = runtime.sessions.get_session(session_id)
    return {
        "asset_path": asset_path.name,
        "image_count": metadata.image_count,
    }


@router.post("/sessions/{session_id}/messages")
async def send_message(
    session_id: str,
    payload: ChatRequest,
    request: Request,
) -> StreamingResponse:
    """Send a user message and stream the assistant response via SSE."""

    runtime = request.app.state.runtime

    if payload.content.strip() == "":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="content is required",
        )

    try:
        metadata = runtime.sessions.get_session(session_id)[0]
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        ) from exc

    try:
        runtime.guard().check_before_call(datetime.now(timezone.utc))
    except BudgetHardStopError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Budget hard-stop active",
        ) from exc

    user_message = ChatMessage(
        role="user",
        timestamp=_timestamp_now(),
        content=payload.content,
    )
    runtime.sessions.add_message(session_id, user_message)

    assistant_text_parts: list[str] = []
    usage: UsageEvent | None = None

    async def event_stream():
        nonlocal usage
        try:
            async for event in runtime.brainstorm_provider.chat(
                messages=[Message(role="user", content=payload.content)],
            ):
                if isinstance(event, TokenEvent):
                    assistant_text_parts.append(event.text)
                    yield _sse_event("token", {"token": event.text})
                elif isinstance(event, UsageEvent):
                    usage = event

            if usage is None:
                yield _sse_event(
                    "error",
                    {"detail": "Provider stream finished without usage info"},
                )
                return

            assistant_content = "".join(assistant_text_parts)
            updated = runtime.sessions.add_message(
                session_id,
                ChatMessage(
                    role="assistant",
                    timestamp=_timestamp_now(),
                    content=assistant_content,
                ),
            )

            runtime.guard().record_usage(
                ProviderUsage(
                    timestamp=datetime.now(timezone.utc),
                    provider=runtime.brainstorm_provider.name,
                    model=runtime.brainstorm_provider.model,
                    role="brainstorm",
                    input_tokens=usage.input_tokens,
                    output_tokens=usage.output_tokens,
                    cached_tokens=usage.cached_tokens,
                    session_id=session_id,
                ),
            )

            yield _sse_event(
                "done",
                {
                    "input_tokens": usage.input_tokens,
                    "output_tokens": usage.output_tokens,
                    "message_count": updated.message_count,
                },
            )

        except Exception as exc:
            yield _sse_event(
                "error",
                {"detail": str(exc)},
            )

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
    )


def _sse_event(event: str, data: dict[str, object]) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


def _timestamp_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@router.post("/sessions/{session_id}/extract")
async def extract_ideas(
    session_id: str,
    request: Request,
) -> dict[str, object]:
    """Run idea capture on a session, routing ideas to project docs and spaghetti."""

    runtime = request.app.state.runtime

    try:
        metadata, messages = runtime.sessions.get_session(session_id)
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        ) from exc

    try:
        runtime.guard().check_before_call(datetime.now(timezone.utc))
    except BudgetHardStopError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Budget hard-stop active",
        ) from exc

    transcript = transcript_from_messages(messages)

    try:
        raw, usage = await run_idea_capture(
            runtime.idea_capture_provider,
            IDEA_CAPTURE_PROMPT,
            transcript,
        )
    except IdeaCaptureError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="idea-capture provider returned no usage",
        ) from exc

    runtime.guard().record_usage(
        ProviderUsage(
            timestamp=datetime.now(timezone.utc),
            provider=runtime.idea_capture_provider.name,
            model=runtime.idea_capture_provider.model,
            role="idea_capture",
            input_tokens=usage.input_tokens,
            output_tokens=usage.output_tokens,
            cached_tokens=usage.cached_tokens,
            session_id=session_id,
        ),
    )

    try:
        operations = parse_idea_operations(raw)
    except IdeaCaptureError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    runtime_home = runtime.config.paths.runtime_home

    captured_at = datetime.now(timezone.utc)
    for op in operations:
        if isinstance(op, ProjectAppendOperation):
            create_project_document(runtime_home, op.project_ref, captured_at)

    applied = apply_idea_operations(
        runtime_home=runtime_home,
        connection=runtime.database,
        source_session=session_id,
        operations=operations,
        captured_at=captured_at,
        commit_documents=True,
    )

    return {
        "session_id": session_id,
        "project_appends": len(applied.project_paths),
        "spaghetti": len(applied.spaghetti_paths),
        "documents_committed": applied.documents_committed,
    }


class MatchmakerRunRequest(BaseModel):
    idea_ids: list[str] = Field(min_length=1)


@router.post("/matchmaker/run")
async def run_matchmaker(
    payload: MatchmakerRunRequest,
    request: Request,
) -> dict[str, object]:
    """Run the matchmaker on a list of spaghetti idea ids.

    The current implementation uses the NullScorer default, so the batch
    is always empty (rejection-bias baseline). When the LLM scorer is
    wired the route gains a scorer parameter; the contract here stays
    stable.
    """

    runtime = request.app.state.runtime
    runtime_home: Path = runtime.config.paths.runtime_home

    ideas: list[SpaghettiIdea] = []
    for idea_id in payload.idea_ids:
        row = runtime.database.execute(
            "SELECT idea_id, tags_json, topics_json, path FROM ideas "
            "WHERE idea_id = ?",
            (idea_id,),
        ).fetchone()
        if row is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"unknown idea_id: {idea_id}",
            )
        ideas.append(
            SpaghettiIdea(
                idea_id=row[0],
                content=_read_spaghetti_body(Path(row[3])),
                tags=json.loads(row[1]),
                topics=json.loads(row[2]),
            )
        )

    projects = _load_active_project_summaries(runtime_home)
    batch = propose_matches(ideas=ideas, projects=projects)
    return _batch_to_dict(batch)


def _read_spaghetti_body(path: Path) -> str:
    """Return the body of a spaghetti markdown file, stripping frontmatter."""

    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8")
    if text.startswith("---\n"):
        end = text.find("\n---\n", 4)
        if end != -1:
            return text[end + 5 :].strip()
    return text.strip()


def _load_active_project_summaries(runtime_home: Path) -> list[ProjectSummary]:
    """Load active projects from `<runtime_home>/projects.json`. Fail-closed."""

    path = runtime_home / "projects.json"
    if not path.exists():
        return []
    try:
        registry = load_project_registry(path)
    except ProjectRegistryError:
        return []
    return [
        ProjectSummary(ref=entry.ref, summary=entry.description or entry.name)
        for entry in registry.active()
    ]


def _batch_to_dict(batch: MatchBatch) -> dict[str, object]:
    return {
        "batch_id": batch.batch_id,
        "generated_at": batch.generated_at,
        "candidates": [
            {
                "idea_id": c.idea_id,
                "project_ref": c.project_ref,
                "confidence": c.confidence,
                "rationale": c.rationale,
            }
            for c in batch.candidates
        ],
        "rejected_idea_ids": batch.rejected_idea_ids,
    }
