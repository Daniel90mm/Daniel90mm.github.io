"""Session file and asset storage."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime
from pathlib import Path
import json
import re
import secrets
import sqlite3


MAX_IMAGE_BYTES = 5 * 1024 * 1024
MESSAGE_HEADING_RE = re.compile(r"^## (?P<role>[a-z]+) \[(?P<timestamp>[^\]]+)\]$")


class StorageError(RuntimeError):
    """Raised when storage operations fail."""


class AssetTooLargeError(StorageError):
    """Raised when an uploaded asset exceeds the configured cap."""


@dataclass(frozen=True)
class ChatMessage:
    role: str
    timestamp: str
    content: str


@dataclass(frozen=True)
class SessionMetadata:
    session_id: str
    started_at: str
    ended_at: str | None
    provider: str
    model: str
    message_count: int
    image_count: int
    tags: list[str]
    project_ref: str | None
    spaghetti: bool
    extracted: bool
    extracted_at: str | None
    curated: bool
    display_name: str | None = None


def write_session(
    path: Path,
    metadata: SessionMetadata,
    messages: list[ChatMessage],
) -> None:
    """Write a session markdown file atomically."""

    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = path.with_suffix(f"{path.suffix}.tmp")
    temporary_path.write_text(
        render_session(metadata, messages),
        encoding="utf-8",
    )
    temporary_path.replace(path)


def read_session(path: Path) -> tuple[SessionMetadata, list[ChatMessage]]:
    """Read a generated session markdown file."""

    text = path.read_text(encoding="utf-8")
    frontmatter, body = split_frontmatter(text)
    metadata = parse_session_metadata(frontmatter)
    messages = parse_messages(body)
    return metadata, messages


def render_session(
    metadata: SessionMetadata,
    messages: list[ChatMessage],
) -> str:
    """Render a session as markdown."""

    lines = ["---"]
    for key, value in session_frontmatter_items(metadata):
        lines.append(f"{key}: {format_frontmatter_value(value)}")
    lines.extend(["---", ""])

    for message in messages:
        lines.append(f"## {message.role} [{message.timestamp}]")
        lines.append(message.content.rstrip())
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def split_frontmatter(text: str) -> tuple[list[str], str]:
    """Split a markdown file into frontmatter lines and body."""

    if not text.startswith("---\n"):
        raise StorageError("session file is missing frontmatter")
    try:
        end = text.index("\n---\n", 4)
    except ValueError as exc:
        raise StorageError("session file has unterminated frontmatter") from exc
    frontmatter = text[4:end].splitlines()
    body = text[end + len("\n---\n") :]
    return frontmatter, body


def parse_session_metadata(frontmatter: list[str]) -> SessionMetadata:
    """Parse session metadata frontmatter."""

    values: dict[str, object] = {}
    for line in frontmatter:
        if not line.strip():
            continue
        key, raw_value = line.split(":", 1)
        values[key.strip()] = parse_frontmatter_value(raw_value.strip())

    return SessionMetadata(
        session_id=str(values["session_id"]),
        started_at=str(values["started_at"]),
        ended_at=optional_str(values["ended_at"]),
        provider=str(values["provider"]),
        model=str(values["model"]),
        message_count=int(values["message_count"]),
        image_count=int(values["image_count"]),
        tags=list_of_str(values["tags"]),
        project_ref=optional_str(values["project_ref"]),
        spaghetti=bool(values["spaghetti"]),
        extracted=bool(values["extracted"]),
        extracted_at=optional_str(values["extracted_at"]),
        curated=bool(values["curated"]),
        display_name=optional_str(values.get("display_name")),
    )


def parse_messages(body: str) -> list[ChatMessage]:
    """Parse session body messages."""

    messages: list[ChatMessage] = []
    current_role: str | None = None
    current_timestamp: str | None = None
    current_lines: list[str] = []

    for line in body.splitlines():
        match = MESSAGE_HEADING_RE.match(line)
        if match:
            if current_role is not None and current_timestamp is not None:
                messages.append(
                    ChatMessage(
                        role=current_role,
                        timestamp=current_timestamp,
                        content="\n".join(current_lines).rstrip(),
                    )
                )
            current_role = match.group("role")
            current_timestamp = match.group("timestamp")
            current_lines = []
            continue
        current_lines.append(line)

    if current_role is not None and current_timestamp is not None:
        messages.append(
            ChatMessage(
                role=current_role,
                timestamp=current_timestamp,
                content="\n".join(current_lines).rstrip(),
            )
        )

    return messages


def index_session(
    connection: sqlite3.Connection,
    metadata: SessionMetadata,
    path: Path,
) -> None:
    """Insert or update one session in the sqlite metadata index."""

    connection.execute(
        """
        INSERT INTO sessions (
            session_id,
            started_at,
            ended_at,
            provider,
            model,
            message_count,
            image_count,
            tags_json,
            project_ref,
            spaghetti,
            extracted,
            extracted_at,
            curated,
            display_name,
            path
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(session_id) DO UPDATE SET
            started_at = excluded.started_at,
            ended_at = excluded.ended_at,
            provider = excluded.provider,
            model = excluded.model,
            message_count = excluded.message_count,
            image_count = excluded.image_count,
            tags_json = excluded.tags_json,
            project_ref = excluded.project_ref,
            spaghetti = excluded.spaghetti,
            extracted = excluded.extracted,
            extracted_at = excluded.extracted_at,
            curated = excluded.curated,
            display_name = excluded.display_name,
            path = excluded.path,
            updated_at = CURRENT_TIMESTAMP
        """,
        (
            metadata.session_id,
            metadata.started_at,
            metadata.ended_at,
            metadata.provider,
            metadata.model,
            metadata.message_count,
            metadata.image_count,
            json.dumps(metadata.tags),
            metadata.project_ref,
            int(metadata.spaghetti),
            int(metadata.extracted),
            metadata.extracted_at,
            int(metadata.curated),
            metadata.display_name,
            str(path),
        ),
    )
    connection.commit()


class SessionStore:
    """File and sqlite-backed session storage."""

    def __init__(self, runtime_home: Path, connection: sqlite3.Connection) -> None:
        self.runtime_home = runtime_home
        self.connection = connection

    @property
    def sessions_dir(self) -> Path:
        """Return the raw sessions directory."""

        return self.runtime_home / "sessions"

    def session_path(self, session_id: str) -> Path:
        """Return the markdown path for a session id."""

        return self.sessions_dir / f"{session_id}.md"

    def create_session(
        self,
        provider: str,
        model: str,
        started_at: datetime,
        slug: str = "session",
    ) -> SessionMetadata:
        """Create and index an empty session."""

        session_id = make_session_id(started_at, slug)
        metadata = SessionMetadata(
            session_id=session_id,
            started_at=started_at.isoformat(),
            ended_at=None,
            provider=provider,
            model=model,
            message_count=0,
            image_count=0,
            tags=[],
            project_ref=None,
            spaghetti=False,
            extracted=False,
            extracted_at=None,
            curated=False,
            display_name=slug.strip() or None,
        )
        path = self.session_path(session_id)
        write_session(path, metadata, [])
        index_session(self.connection, metadata, path)
        return metadata

    def get_session(
        self,
        session_id: str,
    ) -> tuple[SessionMetadata, list[ChatMessage]]:
        """Load one session by id."""

        return read_session(self.session_path(session_id))

    def add_message(
        self,
        session_id: str,
        message: ChatMessage,
    ) -> SessionMetadata:
        """Append one message to a session and update metadata."""

        path = self.session_path(session_id)
        metadata, messages = read_session(path)
        updated_messages = [*messages, message]
        updated_metadata = replace(
            metadata,
            message_count=len(updated_messages),
        )
        write_session(path, updated_metadata, updated_messages)
        index_session(self.connection, updated_metadata, path)
        return updated_metadata

    def rename_session(
        self,
        session_id: str,
        display_name: str,
    ) -> SessionMetadata:
        """Update the human-visible name for a session without changing its id."""

        path = self.session_path(session_id)
        metadata, messages = read_session(path)
        cleaned = display_name.strip()
        if not cleaned:
            raise StorageError("display name is required")
        updated_metadata = replace(metadata, display_name=cleaned[:120])
        write_session(path, updated_metadata, messages)
        index_session(self.connection, updated_metadata, path)
        return updated_metadata

    def close_session(
        self,
        session_id: str,
        ended_at: datetime,
    ) -> SessionMetadata:
        """Mark one session closed and persist the end timestamp."""

        path = self.session_path(session_id)
        metadata, messages = read_session(path)
        updated_metadata = replace(
            metadata,
            ended_at=ended_at.isoformat(),
        )
        write_session(path, updated_metadata, messages)
        index_session(self.connection, updated_metadata, path)
        return updated_metadata

    def mark_extracted(
        self,
        session_id: str,
        extracted_at: datetime,
    ) -> SessionMetadata:
        """Mark one session extracted and persist the extraction timestamp."""

        path = self.session_path(session_id)
        metadata, messages = read_session(path)
        updated_metadata = replace(
            metadata,
            extracted=True,
            extracted_at=extracted_at.isoformat(),
        )
        write_session(path, updated_metadata, messages)
        index_session(self.connection, updated_metadata, path)
        return updated_metadata

    def store_asset(
        self,
        session_id: str,
        filename: str,
        data: bytes,
    ) -> Path:
        """Store a session asset and update image metadata."""

        session_path = self.session_path(session_id)
        metadata, messages = read_session(session_path)
        asset_path = store_session_asset(
            self.runtime_home,
            session_id=session_id,
            filename=filename,
            data=data,
        )
        updated_metadata = replace(
            metadata,
            image_count=metadata.image_count + 1,
        )
        write_session(session_path, updated_metadata, messages)
        index_session(self.connection, updated_metadata, session_path)
        return asset_path

    def delete_asset(
        self,
        session_id: str,
        filename: str,
    ) -> SessionMetadata:
        """Delete one session asset and update asset metadata."""

        session_path = self.session_path(session_id)
        metadata, messages = read_session(session_path)
        asset_path = safe_session_asset_path(self.runtime_home, session_id, filename)
        if not asset_path.is_file():
            raise FileNotFoundError(f"asset not found: {filename}")
        asset_path.unlink()
        updated_metadata = replace(
            metadata,
            image_count=max(0, metadata.image_count - 1),
        )
        write_session(session_path, updated_metadata, messages)
        index_session(self.connection, updated_metadata, session_path)
        return updated_metadata

    def delete_session(self, session_id: str) -> None:
        """Delete one session: file, uploaded assets, sqlite index row.

        Preserves api_calls rows (cost history) and downstream artifacts
        (ideas, project documents, spaghetti notes). Raises FileNotFoundError
        if neither the session file nor an index row exists. Raises
        sqlite3.IntegrityError if foreign-key linked rows still reference
        the session (e.g. extracted ideas).
        """

        session_path = self.session_path(session_id)
        file_exists = session_path.is_file()
        row = self.connection.execute(
            "SELECT 1 FROM sessions WHERE session_id = ?",
            (session_id,),
        ).fetchone()
        if not file_exists and row is None:
            raise FileNotFoundError(f"session not found: {session_id}")

        self.connection.execute(
            "DELETE FROM sessions WHERE session_id = ?",
            (session_id,),
        )
        self.connection.commit()

        asset_dir = self.runtime_home / "sessions" / "_assets"
        if asset_dir.is_dir():
            for asset in asset_dir.glob(f"{session_id}-*"):
                try:
                    asset.unlink()
                except FileNotFoundError:
                    pass

        if file_exists:
            session_path.unlink()

    def list_sessions(self) -> list[SessionMetadata]:
        """List indexed sessions newest first."""

        rows = self.connection.execute(
            """
            SELECT
                session_id,
                started_at,
                ended_at,
                provider,
                model,
                message_count,
                image_count,
                tags_json,
                project_ref,
                spaghetti,
                extracted,
                extracted_at,
                curated,
                display_name
            FROM sessions
            ORDER BY started_at DESC
            """
        ).fetchall()
        return [metadata_from_row(row) for row in rows]


def store_session_asset(
    runtime_home: Path,
    session_id: str,
    filename: str,
    data: bytes,
) -> Path:
    """Store a session asset under sessions/_assets with a 5 MiB cap."""

    if len(data) > MAX_IMAGE_BYTES:
        raise AssetTooLargeError("image upload exceeds 5 MiB cap")

    safe_name = sanitize_filename(Path(filename).name)
    asset_dir = runtime_home / "sessions" / "_assets"
    asset_dir.mkdir(parents=True, exist_ok=True)
    path = asset_dir / f"{session_id}-{safe_name}"
    path.write_bytes(data)
    return path


def safe_session_asset_path(
    runtime_home: Path,
    session_id: str,
    filename: str,
) -> Path:
    """Resolve a stored session asset path without allowing traversal."""

    if Path(filename).name != filename:
        raise FileNotFoundError(f"invalid asset filename: {filename}")
    if not filename.startswith(f"{session_id}-"):
        raise FileNotFoundError(f"asset does not belong to session: {filename}")
    asset_dir = (runtime_home / "sessions" / "_assets").resolve()
    path = (asset_dir / filename).resolve()
    if path.parent != asset_dir:
        raise FileNotFoundError(f"invalid asset path: {filename}")
    return path


def make_session_id(started_at: datetime, slug: str) -> str:
    """Build a sortable session id with a short random suffix."""

    safe_slug = sanitize_slug(slug)
    random_suffix = secrets.token_hex(4)
    return f"{started_at.strftime('%Y-%m-%d-%H%M')}-{safe_slug}-{random_suffix}"


def sanitize_slug(value: str) -> str:
    """Return a conservative kebab-case slug fragment."""

    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "session"


def sanitize_filename(filename: str) -> str:
    """Return a conservative ASCII filename."""

    safe = re.sub(r"[^A-Za-z0-9._-]+", "_", filename).strip("._")
    if not safe:
        raise StorageError("asset filename is empty after sanitization")
    return safe


def session_frontmatter_items(
    metadata: SessionMetadata,
) -> list[tuple[str, object]]:
    """Return frontmatter keys in spec order."""

    return [
        ("session_id", metadata.session_id),
        ("started_at", metadata.started_at),
        ("ended_at", metadata.ended_at),
        ("provider", metadata.provider),
        ("model", metadata.model),
        ("message_count", metadata.message_count),
        ("image_count", metadata.image_count),
        ("tags", metadata.tags),
        ("project_ref", metadata.project_ref),
        ("spaghetti", metadata.spaghetti),
        ("extracted", metadata.extracted),
        ("extracted_at", metadata.extracted_at),
        ("curated", metadata.curated),
        ("display_name", metadata.display_name),
    ]


def format_frontmatter_value(value: object) -> str:
    """Format a simple YAML-compatible frontmatter value."""

    if value is None:
        return "null"
    if isinstance(value, bool):
        return str(value).lower()
    if isinstance(value, int):
        return str(value)
    if isinstance(value, list):
        return json.dumps(value)
    if isinstance(value, str):
        return json.dumps(value)
    raise TypeError(f"unsupported frontmatter value {type(value).__name__}")


def parse_frontmatter_value(raw_value: str) -> object:
    """Parse values emitted by format_frontmatter_value."""

    if raw_value == "null":
        return None
    if raw_value == "true":
        return True
    if raw_value == "false":
        return False
    if raw_value.isdigit():
        return int(raw_value)
    if raw_value.startswith("[") or raw_value.startswith("\""):
        return json.loads(raw_value)
    return raw_value


def optional_str(value: object) -> str | None:
    """Cast a parsed value to optional string."""

    if value is None:
        return None
    return str(value)


def list_of_str(value: object) -> list[str]:
    """Cast a parsed value to list[str]."""

    if not isinstance(value, list):
        raise StorageError("expected a list value")
    return [str(item) for item in value]


def metadata_from_row(row: sqlite3.Row | tuple[object, ...]) -> SessionMetadata:
    """Create SessionMetadata from a sessions table row."""

    return SessionMetadata(
        session_id=str(row[0]),
        started_at=str(row[1]),
        ended_at=optional_str(row[2]),
        provider=str(row[3]),
        model=str(row[4]),
        message_count=int(row[5]),
        image_count=int(row[6]),
        tags=list_of_str(json.loads(str(row[7]))),
        project_ref=optional_str(row[8]),
        spaghetti=bool(row[9]),
        extracted=bool(row[10]),
        extracted_at=optional_str(row[11]),
        curated=bool(row[12]),
        display_name=optional_str(row[13]) if len(row) > 13 else None,
    )
