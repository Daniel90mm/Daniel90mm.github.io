"""Serialization helpers for internal DTO boundaries."""

from __future__ import annotations

from pathlib import Path

from flightrecorder.storage import ChatMessage, SessionMetadata


def session_display_slug(metadata: SessionMetadata) -> str:
    """Return the UI label for a session."""

    if metadata.display_name:
        return metadata.display_name
    parts = metadata.session_id.split("-")
    if len(parts) > 5:
        return "-".join(parts[5:-1]) or metadata.session_id
    return metadata.session_id


def session_metadata_to_dict(metadata: SessionMetadata) -> dict[str, object]:
    """Serialize session metadata using the spec frontmatter field names."""

    return {
        "session_id": metadata.session_id,
        "started_at": metadata.started_at,
        "ended_at": metadata.ended_at,
        "provider": metadata.provider,
        "model": metadata.model,
        "message_count": metadata.message_count,
        "image_count": metadata.image_count,
        "tags": metadata.tags,
        "project_ref": metadata.project_ref,
        "spaghetti": metadata.spaghetti,
        "extracted": metadata.extracted,
        "extracted_at": metadata.extracted_at,
        "curated": metadata.curated,
        "display_name": metadata.display_name,
        "slug": session_display_slug(metadata),
    }


def chat_message_to_dict(message: ChatMessage) -> dict[str, str]:
    """Serialize one chat message."""

    return {
        "role": message.role,
        "timestamp": message.timestamp,
        "content": message.content,
    }


def session_detail_to_dict(
    metadata: SessionMetadata,
    messages: list[ChatMessage],
) -> dict[str, object]:
    """Serialize a full session detail object."""

    return {
        **session_metadata_to_dict(metadata),
        "messages": [chat_message_to_dict(message) for message in messages],
    }


def asset_to_dict(path: Path, runtime_home: Path) -> dict[str, object]:
    """Serialize a stored asset path without exposing absolute paths by default."""

    return {
        "filename": path.name,
        "relative_path": path.relative_to(runtime_home).as_posix(),
        "size_bytes": path.stat().st_size,
    }
