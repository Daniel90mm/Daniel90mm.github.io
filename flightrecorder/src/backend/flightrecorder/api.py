"""HTTP API routes for flightrecorder."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, File, HTTPException, Query, Request, UploadFile, status
from pydantic import BaseModel, Field

from flightrecorder.serializers import session_detail_to_dict, session_metadata_to_dict
from flightrecorder.storage import AssetTooLargeError


router = APIRouter(prefix="/api")


class CreateSessionRequest(BaseModel):
    provider: str = Field(min_length=1)
    model: str = Field(min_length=1)
    slug: str = "session"


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
