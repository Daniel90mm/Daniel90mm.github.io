"""Idea-capture operation parsing and application."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import hashlib
import json
import sqlite3

from flightrecorder.documents import (
    PROJECT_SECTIONS,
    ProjectAppend,
    append_to_project_document,
    commit_documents_repo,
    documents_dir,
    sanitize_project_ref,
)
from flightrecorder.storage import format_frontmatter_value, sanitize_slug


MAX_IDEA_OPERATIONS = 8


class IdeaCaptureError(RuntimeError):
    """Raised when idea-capture output cannot be trusted."""


@dataclass(frozen=True)
class ProjectAppendOperation:
    project_ref: str
    section: str
    content: str


@dataclass(frozen=True)
class SpaghettiOperation:
    tags: list[str]
    topics: list[str]
    content: str


IdeaOperation = ProjectAppendOperation | SpaghettiOperation


@dataclass(frozen=True)
class AppliedIdeaOperations:
    project_paths: list[Path]
    spaghetti_paths: list[Path]


def parse_idea_operations(raw_output: str) -> list[IdeaOperation]:
    """Parse JSON output from the idea-capture prompt."""

    try:
        data = json.loads(raw_output)
    except json.JSONDecodeError as exc:
        raise IdeaCaptureError("idea-capture output is not valid JSON") from exc

    if not isinstance(data, list):
        raise IdeaCaptureError("idea-capture output must be a JSON array")
    if len(data) > MAX_IDEA_OPERATIONS:
        raise IdeaCaptureError("idea-capture output has too many operations")

    return [_parse_operation(item, index) for index, item in enumerate(data)]


def apply_idea_operations(
    runtime_home: Path,
    connection: sqlite3.Connection,
    source_session: str,
    operations: list[IdeaOperation],
    captured_at: datetime,
    commit_documents: bool = False,
) -> AppliedIdeaOperations:
    """Apply parsed idea operations to project documents and spaghetti files."""

    timestamp = captured_at.isoformat()
    project_paths: list[Path] = []
    spaghetti_paths: list[Path] = []

    for index, operation in enumerate(operations):
        if isinstance(operation, ProjectAppendOperation):
            path = append_to_project_document(
                runtime_home,
                ProjectAppend(
                    project_ref=operation.project_ref,
                    section=operation.section,
                    content=operation.content,
                    timestamp=timestamp,
                    source_session=source_session,
                ),
            )
            project_paths.append(path)
            continue

        path = write_spaghetti_idea(
            runtime_home=runtime_home,
            connection=connection,
            source_session=source_session,
            operation=operation,
            captured_at=captured_at,
            operation_index=index,
        )
        spaghetti_paths.append(path)

    mark_session_extracted(connection, source_session, timestamp)

    if commit_documents and project_paths:
        commit_documents_repo(
            documents_dir(runtime_home),
            f"Append ideas from {source_session}",
        )

    return AppliedIdeaOperations(
        project_paths=project_paths,
        spaghetti_paths=spaghetti_paths,
    )


def write_spaghetti_idea(
    runtime_home: Path,
    connection: sqlite3.Connection,
    source_session: str,
    operation: SpaghettiOperation,
    captured_at: datetime,
    operation_index: int,
) -> Path:
    """Write one spaghetti idea markdown file and index it in sqlite."""

    captured_timestamp = captured_at.isoformat()
    idea_id = make_idea_id(source_session, operation_index, operation.content)
    path = spaghetti_path(runtime_home, idea_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        render_spaghetti_idea(
            idea_id=idea_id,
            captured_at=captured_timestamp,
            source_session=source_session,
            tags=operation.tags,
            topics=operation.topics,
            content=operation.content,
        ),
        encoding="utf-8",
    )
    index_spaghetti_idea(
        connection=connection,
        idea_id=idea_id,
        captured_at=captured_timestamp,
        source_session=source_session,
        tags=operation.tags,
        topics=operation.topics,
        path=path,
    )
    return path


def render_spaghetti_idea(
    idea_id: str,
    captured_at: str,
    source_session: str,
    tags: list[str],
    topics: list[str],
    content: str,
) -> str:
    """Render one spaghetti idea markdown file."""

    lines: list[str] = [
        "---",
        f"idea_id: {format_frontmatter_value(idea_id)}",
        f"captured_at: {format_frontmatter_value(captured_at)}",
        f"source_session: {format_frontmatter_value(source_session)}",
        f"tags: {format_frontmatter_value(tags)}",
        "status: unmatched",
        "match_attempts: 0",
        "matched_to: []",
        "implemented_in: []",
        "---",
        "",
        content.strip(),
        "",
    ]
    if topics:
        lines.insert(5, f"topics: {format_frontmatter_value(topics)}")
    return "\n".join(lines)


def index_spaghetti_idea(
    connection: sqlite3.Connection,
    idea_id: str,
    captured_at: str,
    source_session: str,
    tags: list[str],
    topics: list[str],
    path: Path,
) -> None:
    """Insert or update one spaghetti idea row."""

    connection.execute(
        """
        INSERT INTO ideas (
            idea_id,
            captured_at,
            source_session,
            tags_json,
            topics_json,
            status,
            match_attempts,
            matched_to_json,
            implemented_in_json,
            path
        )
        VALUES (?, ?, ?, ?, ?, 'unmatched', 0, '[]', '[]', ?)
        ON CONFLICT(idea_id) DO UPDATE SET
            captured_at = excluded.captured_at,
            source_session = excluded.source_session,
            tags_json = excluded.tags_json,
            topics_json = excluded.topics_json,
            path = excluded.path,
            updated_at = CURRENT_TIMESTAMP
        """,
        (
            idea_id,
            captured_at,
            source_session,
            json.dumps(tags),
            json.dumps(topics),
            str(path),
        ),
    )
    connection.commit()


def mark_session_extracted(
    connection: sqlite3.Connection,
    session_id: str,
    extracted_at: str,
) -> None:
    """Mark a session as having passed idea capture."""

    connection.execute(
        """
        UPDATE sessions
        SET extracted = 1,
            extracted_at = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE session_id = ?
        """,
        (extracted_at, session_id),
    )
    connection.commit()


def spaghetti_path(runtime_home: Path, idea_id: str) -> Path:
    """Return the markdown path for one spaghetti idea."""

    return runtime_home / "spaghetti" / f"{idea_id}.md"


def make_idea_id(source_session: str, operation_index: int, content: str) -> str:
    """Build a stable idea id from source session, operation index, and content."""

    slug = sanitize_slug(content)[:40].strip("-") or "idea"
    digest = hashlib.sha256(
        f"{source_session}:{operation_index}:{content}".encode("utf-8")
    ).hexdigest()[:8]
    return f"{slug}-{digest}"


def _parse_operation(item: object, index: int) -> IdeaOperation:
    if not isinstance(item, dict):
        raise IdeaCaptureError(f"operation {index} must be an object")
    operation_type = item.get("type")
    if operation_type == "project_append":
        return _parse_project_append(item, index)
    if operation_type == "spaghetti":
        return _parse_spaghetti(item, index)
    raise IdeaCaptureError(f"operation {index} has unknown type")


def _parse_project_append(item: dict[str, object], index: int) -> ProjectAppendOperation:
    project_ref = _required_non_empty_string(item, "project_ref", index)
    section = _required_non_empty_string(item, "section", index)
    content = _required_non_empty_string(item, "content", index)
    if section not in PROJECT_SECTIONS:
        raise IdeaCaptureError(f"operation {index} has unknown project section")
    sanitize_project_ref(project_ref)
    return ProjectAppendOperation(
        project_ref=project_ref,
        section=section,
        content=content,
    )


def _parse_spaghetti(item: dict[str, object], index: int) -> SpaghettiOperation:
    return SpaghettiOperation(
        tags=_required_string_list(item, "tags", index),
        topics=_required_string_list(item, "topics", index),
        content=_required_non_empty_string(item, "content", index),
    )


def _required_non_empty_string(
    item: dict[str, object],
    key: str,
    index: int,
) -> str:
    value = item.get(key)
    if not isinstance(value, str) or value.strip() == "":
        raise IdeaCaptureError(f"operation {index}.{key} must be a non-empty string")
    return value.strip()


def _required_string_list(
    item: dict[str, object],
    key: str,
    index: int,
) -> list[str]:
    value = item.get(key)
    if not isinstance(value, list):
        raise IdeaCaptureError(f"operation {index}.{key} must be a list")

    result: list[str] = []
    for item_index, entry in enumerate(value):
        if not isinstance(entry, str) or entry.strip() == "":
            raise IdeaCaptureError(
                f"operation {index}.{key}[{item_index}] must be a non-empty string"
            )
        result.append(entry.strip())
    return result
