"""HTTP API routes for flightrecorder."""

from __future__ import annotations

import json
import mimetypes
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import APIRouter, File, HTTPException, Query, Request, UploadFile, status
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel, Field

from flightrecorder.assets import extract_text_from_asset
from flightrecorder.costs import (
    BudgetHardStopError,
    ProviderUsage,
    budget_hard_stop_path,
    evaluate_monthly_budget,
    is_budget_hard_stop_active,
)
from flightrecorder.documents import (
    ProjectDocumentError,
    create_project_document,
    documents_dir,
    sanitize_project_ref,
)
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
from flightrecorder.publisher import run_publish_pipeline
from flightrecorder.serializers import (
    asset_to_dict,
    session_detail_to_dict,
    session_metadata_to_dict,
)
from flightrecorder.storage import (
    AssetTooLargeError,
    ChatMessage,
    StorageError,
    safe_session_asset_path,
)


router = APIRouter(prefix="/api")


def _load_prompt_text(filename: str) -> str:
    prompt_path = Path(__file__).resolve().parent.parent.parent.parent / "prompts" / filename
    return prompt_path.read_text(encoding="utf-8")


BRAINSTORM_SYSTEM_PROMPT = _load_prompt_text("brainstorm-system.md")


def _session_assets(runtime_home: Path, session_id: str) -> list[dict[str, object]]:
    asset_dir = runtime_home / "sessions" / "_assets"
    if not asset_dir.is_dir():
        return []
    return [
        asset_to_dict(path, runtime_home)
        for path in sorted(asset_dir.glob(f"{session_id}-*"))
        if path.is_file()
    ]


class CreateSessionRequest(BaseModel):
    provider: str = Field(min_length=1)
    model: str = Field(min_length=1)
    slug: str = "session"


class ChatRequest(BaseModel):
    content: str = Field(max_length=32768)


class RenameSessionRequest(BaseModel):
    display_name: str = Field(min_length=1, max_length=120)


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
        "display_name": metadata.display_name,
        "slug": metadata.display_name or payload.slug,
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
    detail = session_detail_to_dict(metadata, messages)
    detail["assets"] = _session_assets(runtime.config.paths.runtime_home, session_id)
    return detail


@router.patch("/sessions/{session_id}")
async def rename_session(
    session_id: str,
    payload: RenameSessionRequest,
    request: Request,
) -> dict[str, object]:
    """Update the human-visible name for a session."""

    runtime = request.app.state.runtime
    try:
        metadata = runtime.sessions.rename_session(
            session_id=session_id,
            display_name=payload.display_name,
        )
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        ) from exc
    except StorageError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    return session_metadata_to_dict(metadata)


@router.post(
    "/sessions/{session_id}/upload",
    status_code=status.HTTP_201_CREATED,
)
async def upload_session_asset(
    session_id: str,
    request: Request,
    file: UploadFile = File(...),
) -> dict[str, Any]:
    """Upload one file asset to a session."""

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
            detail="asset upload exceeds 5 MiB cap",
        ) from exc

    metadata, _messages = runtime.sessions.get_session(session_id)
    return {
        "asset_path": asset_path.name,
        "asset": asset_to_dict(asset_path, runtime.config.paths.runtime_home),
        "image_count": metadata.image_count,
    }


@router.delete("/sessions/{session_id}/assets/{filename}")
async def delete_session_asset(
    session_id: str,
    filename: str,
    request: Request,
) -> dict[str, object]:
    """Delete one uploaded session asset."""

    runtime = request.app.state.runtime
    try:
        metadata = runtime.sessions.delete_asset(session_id=session_id, filename=filename)
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found",
        ) from exc
    return {
        "deleted": filename,
        "image_count": metadata.image_count,
        "assets": _session_assets(runtime.config.paths.runtime_home, session_id),
    }


@router.get("/sessions/{session_id}/assets/{filename}")
async def get_session_asset(
    session_id: str,
    filename: str,
    request: Request,
) -> FileResponse:
    """Return the raw bytes of one uploaded session asset.

    Uses the same path-guard rules as delete: file must live under
    `<runtime_home>/sessions/_assets`, filename must start with
    `{session_id}-`, and traversal is rejected.
    """

    runtime = request.app.state.runtime
    try:
        runtime.sessions.get_session(session_id)
        asset_path = safe_session_asset_path(
            runtime.config.paths.runtime_home, session_id, filename
        )
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found",
        ) from exc
    if not asset_path.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found",
        )

    content_type, _encoding = mimetypes.guess_type(str(asset_path))
    media_type = content_type or "application/octet-stream"
    return FileResponse(asset_path, media_type=media_type)


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
                system=BRAINSTORM_SYSTEM_PROMPT,
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


@router.get("/projects")
async def list_projects(request: Request) -> dict[str, object]:
    """List active project registry entries.

    Reads `<runtime_home>/projects.json`. Returns empty list if the file is
    missing. Read-only.
    """

    runtime = request.app.state.runtime
    registry_path = runtime.config.paths.runtime_home / "projects.json"
    if not registry_path.exists():
        return {"projects": []}

    try:
        registry = load_project_registry(registry_path)
    except ProjectRegistryError:
        return {"projects": []}

    return {
        "projects": [
            {
                "name": entry.name,
                "ref": entry.ref,
                "path": entry.path,
                "active": entry.active,
                "description": entry.description,
            }
            for entry in registry.active()
        ]
    }


@router.get("/runtime")
async def get_runtime_status(request: Request) -> dict[str, object]:
    """Return safe runtime provider status without secrets. Read-only."""

    runtime = request.app.state.runtime

    def role_status(role_name: str) -> dict[str, object]:
        role = runtime.config.roles.get(role_name)
        if role is None:
            return {
                "provider": "none",
                "model": "none",
                "configured": False,
                "issues": ["role_missing"],
            }

        issues: list[str] = []
        has_provider = role.provider in runtime.config.providers
        if not has_provider:
            issues.append("provider_missing")
        else:
            api_key = runtime.config.providers[role.provider].api_key.strip()
            if role.provider != "prototype" and (
                not api_key or "CHANGEME" in api_key
            ):
                issues.append("api_key_missing")

        if role.provider not in {"anthropic", "deepseek", "prototype"}:
            issues.append("provider_not_implemented")

        has_model = role.model in runtime.pricing.models
        if not has_model:
            issues.append("pricing_missing")
        else:
            pricing_model = runtime.pricing.models[role.model]
            if pricing_model.provider != role.provider:
                issues.append("pricing_provider_mismatch")

        return {
            "provider": role.provider,
            "model": role.model,
            "configured": not issues,
            "issues": issues,
        }

    return {
        "runtime_home": str(runtime.config.paths.runtime_home),
        "roles": {
            "brainstorm": role_status("brainstorm"),
            "idea_capture": role_status("idea_capture"),
        },
    }


@router.get("/budget")
async def get_budget(request: Request) -> dict[str, object]:
    """Return current monthly budget status. Read-only."""

    runtime = request.app.state.runtime
    now = datetime.now(timezone.utc)
    evaluation = evaluate_monthly_budget(
        connection=runtime.database,
        now=now,
        warn_at_dkk=runtime.config.budget.warn_at_dkk,
        hard_stop_dkk=runtime.config.budget.hard_stop_dkk,
    )
    sentinel = budget_hard_stop_path(runtime.config.paths.runtime_home)
    return {
        "currency": runtime.config.budget.currency,
        "monthly_cost_dkk": evaluation.monthly_cost_dkk,
        "warn_at_dkk": evaluation.warn_at_dkk,
        "hard_stop_dkk": evaluation.hard_stop_dkk,
        "status": evaluation.status,
        "hard_stop_active": is_budget_hard_stop_active(
            runtime.config.paths.runtime_home
        ),
        "hard_stop_path": str(sentinel),
    }


@router.get("/documents")
async def list_documents(request: Request) -> dict[str, object]:
    """List project document refs and paths.

    Lists markdown files in `<runtime_home>/documents/`, sorted by filename.
    Returns empty list if the directory is missing. Read-only.
    """

    runtime = request.app.state.runtime
    docs_path = documents_dir(runtime.config.paths.runtime_home)
    if not docs_path.is_dir():
        return {"documents": []}

    docs = []
    for md in sorted(docs_path.glob("*.md")):
        stat = md.stat()
        docs.append(
            {
                "ref": md.stem,
                "path": f"documents/{md.name}",
                "size_bytes": stat.st_size,
                "modified_at": datetime.fromtimestamp(
                    stat.st_mtime, tz=timezone.utc
                ).isoformat(),
            }
        )

    return {"documents": docs}


@router.get("/documents/{ref}")
async def get_document(ref: str, request: Request) -> dict[str, object]:
    """Return one project document body and metadata. Read-only."""

    runtime = request.app.state.runtime
    try:
        sanitized = sanitize_project_ref(ref)
    except ProjectDocumentError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="document not found",
        ) from exc
    docs_path = documents_dir(runtime.config.paths.runtime_home)
    doc_file = docs_path / f"{sanitized}.md"

    if not doc_file.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"document not found: {sanitized}",
        )

    stat = doc_file.stat()
    return {
        "ref": sanitized,
        "path": f"documents/{doc_file.name}",
        "body": doc_file.read_text(encoding="utf-8"),
        "size_bytes": stat.st_size,
        "modified_at": datetime.fromtimestamp(
            stat.st_mtime, tz=timezone.utc
        ).isoformat(),
    }


@router.get("/spaghetti")
async def list_spaghetti(request: Request) -> dict[str, object]:
    """List spaghetti ideas from the sqlite ideas table newest first. Read-only."""

    runtime = request.app.state.runtime
    runtime_home = runtime.config.paths.runtime_home

    rows = runtime.database.execute(
        "SELECT idea_id, captured_at, source_session, tags_json, topics_json, "
        "status, path FROM ideas ORDER BY captured_at DESC, idea_id DESC"
    ).fetchall()

    return {
        "ideas": [
            {
                "idea_id": row[0],
                "captured_at": row[1],
                "source_session": row[2],
                "tags": json.loads(row[3]) if row[3] else [],
                "topics": json.loads(row[4]) if row[4] else [],
                "status": row[5],
                "path": _runtime_relative_path(Path(row[6]), runtime_home),
            }
            for row in rows
        ]
    }


@router.get("/spaghetti/{idea_id}")
async def get_spaghetti(idea_id: str, request: Request) -> dict[str, object]:
    """Return one spaghetti idea body and metadata. Read-only."""

    runtime = request.app.state.runtime

    row = runtime.database.execute(
        "SELECT idea_id, captured_at, source_session, tags_json, topics_json, "
        "status, path FROM ideas WHERE idea_id = ?",
        (idea_id,),
    ).fetchone()

    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"unknown idea_id: {idea_id}",
        )

    path = Path(row[6]).resolve()
    runtime_home = runtime.config.paths.runtime_home.resolve()
    if not path.is_file() or runtime_home not in path.parents:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"idea markdown file missing: {idea_id}",
        )

    return {
        "idea_id": row[0],
        "captured_at": row[1],
        "source_session": row[2],
        "tags": json.loads(row[3]) if row[3] else [],
        "topics": json.loads(row[4]) if row[4] else [],
        "status": row[5],
        "path": _runtime_relative_path(path, runtime_home),
        "body": _read_spaghetti_body(path),
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


def _runtime_relative_path(path: Path, runtime_home: Path) -> str:
    """Return a path relative to runtime home when possible."""

    try:
        return str(path.resolve().relative_to(runtime_home.resolve()))
    except ValueError:
        return str(path)


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


@router.get("/api-calls")
async def list_api_calls(
    request: Request,
    limit: int = Query(default=20, ge=1, le=100),
) -> dict[str, object]:
    """Return newest provider call rows. Read-only."""

    runtime = request.app.state.runtime
    rows = runtime.database.execute(
        "SELECT timestamp, provider, model, role, input_tokens, "
        "output_tokens, cached_tokens, cost_dkk, session_id "
        "FROM api_calls ORDER BY id DESC LIMIT ?",
        (limit,),
    ).fetchall()

    return {
        "api_calls": [
            {
                "timestamp": row[0],
                "provider": row[1],
                "model": row[2],
                "role": row[3],
                "input_tokens": row[4],
                "output_tokens": row[5],
                "cached_tokens": row[6],
                "cost_dkk": row[7],
                "session_id": row[8],
            }
            for row in rows
        ]
    }


VALID_SOURCE_KINDS = frozenset({"session", "document", "spaghetti"})


@router.get("/publish/preview")
async def publish_preview(
    request: Request,
    source_kind: str = Query(...),
    source_id: str = Query(...),
) -> dict[str, object]:
    """Return a read-only publish preview/audit summary for one source artifact.

    Runs the publisher pipeline with the current fail-closed defaults
    (Null curator + Null reviewer), so publishable is always false until
    real stages are wired. The route must not write files, sqlite rows,
    git commits, or Hugo content.
    """

    if source_kind not in VALID_SOURCE_KINDS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="source_kind must be session, document, or spaghetti",
        )

    runtime = request.app.state.runtime
    runtime_home = runtime.config.paths.runtime_home

    source_body: str
    if source_kind == "session":
        try:
            _metadata, messages = runtime.sessions.get_session(source_id)
        except FileNotFoundError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="session not found",
            ) from exc
        source_body = transcript_from_messages(messages)
    elif source_kind == "document":
        try:
            sanitized = sanitize_project_ref(source_id)
        except ProjectDocumentError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="document not found",
            ) from exc
        doc_file = documents_dir(runtime_home) / f"{sanitized}.md"
        if not doc_file.is_file():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"document not found: {sanitized}",
            )
        source_body = doc_file.read_text(encoding="utf-8")
    else:
        row = runtime.database.execute(
            "SELECT path FROM ideas WHERE idea_id = ?",
            (source_id,),
        ).fetchone()
        if row is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"unknown idea_id: {source_id}",
            )
        path = Path(row[0])
        if not path.is_file():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"idea markdown file missing: {source_id}",
            )
        source_body = _read_spaghetti_body(path)

    result = run_publish_pipeline(
        source_kind=source_kind,
        source_id=source_id,
        source_body=source_body,
    )
    rejection_reason = result.rejection_reason
    if rejection_reason is None and not result.approved:
        rejection_reason = "reviewer rejected all snippets"

    return {
        "source_kind": result.source_kind,
        "source_id": result.source_id,
        "publishable": rejection_reason is None,
        "rejection_reason": rejection_reason,
        "approved_count": len(result.approved),
        "snippets": [
            {
                "snippet_id": s.snippet_id,
                "source_kind": s.source_kind,
                "source_id": s.source_id,
                "drafted_at": s.drafted_at,
                "publish_after": s.publish_after,
                "tags": s.tags,
                "project_ref": s.project_ref,
                "body": s.body,
            }
            for s in result.approved
        ],
    }


ATTACHMENT_CONTEXT_MAX_CHARS = 30_000


@router.get("/sessions/{session_id}/attachment-context")
async def attachment_context(
    session_id: str,
    request: Request,
) -> dict[str, object]:
    """Return a read-only preview of attachment text for one session.

    Lists all uploaded assets and extracts text from text-like files
    (`.txt`, `.md`, `.markdown`, `text/*` mime types). Binary assets such
    as images and PDFs are skipped with a reason. No provider calls are
    made. The combined text is capped at 30,000 characters.
    """

    runtime = request.app.state.runtime
    runtime_home = runtime.config.paths.runtime_home

    asset_dir = runtime_home / "sessions" / "_assets"
    asset_paths: list[Path] = []
    if asset_dir.is_dir():
        asset_paths = sorted(
            p for p in asset_dir.glob(f"{session_id}-*") if p.is_file()
        )

    included: list[dict[str, object]] = []
    skipped: list[dict[str, object]] = []
    combined_parts: list[str] = []

    for path in asset_paths:
        content_type, _encoding = mimetypes.guess_type(str(path))
        extracted = extract_text_from_asset(path, mime_type=content_type)
        if extracted is not None:
            included.append({
                "filename": path.name,
                "size_bytes": path.stat().st_size,
                "content_type": content_type or "unknown",
                "extracted_chars": len(extracted),
                "text": extracted,
            })
            combined_parts.append(extracted)
        else:
            skipped.append({
                "filename": path.name,
                "size_bytes": path.stat().st_size,
                "content_type": content_type or "unknown",
                "reason": "unsupported_binary",
            })

    combined_text = "\n\n".join(combined_parts)
    if len(combined_text) > ATTACHMENT_CONTEXT_MAX_CHARS:
        combined_text = combined_text[:ATTACHMENT_CONTEXT_MAX_CHARS]

    return {
        "session_id": session_id,
        "included": included,
        "skipped": skipped,
        "combined_text": combined_text,
    }
