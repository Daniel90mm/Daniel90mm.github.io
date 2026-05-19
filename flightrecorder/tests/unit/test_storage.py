import json
import sqlite3
from datetime import datetime
from pathlib import Path

import pytest

from flightrecorder.schema import initialize_database
from flightrecorder.storage import (
    MAX_IMAGE_BYTES,
    AssetTooLargeError,
    ChatMessage,
    SessionMetadata,
    SessionStore,
    StorageError,
    index_session,
    make_session_id,
    read_session,
    sanitize_filename,
    sanitize_slug,
    safe_session_asset_path,
    split_frontmatter,
    store_session_asset,
    write_session,
)


def test_write_and_read_session_roundtrip(tmp_path: Path) -> None:
    metadata = SessionMetadata(
        session_id="2026-05-18-1730-spaghetti-abcd1234",
        started_at="2026-05-18T17:30:00+02:00",
        ended_at=None,
        provider="google",
        model="gemini-2.5-pro",
        message_count=2,
        image_count=0,
        tags=["fnirs", "signal-processing"],
        project_ref="fnirs",
        spaghetti=False,
        extracted=False,
        extracted_at=None,
        curated=False,
    )
    messages = [
        ChatMessage(role="user", timestamp="17:30:01", content="first line"),
        ChatMessage(
            role="assistant",
            timestamp="17:30:14",
            content="multi\nline response",
        ),
    ]
    path = tmp_path / "session.md"

    write_session(path, metadata, messages)
    loaded_metadata, loaded_messages = read_session(path)

    assert loaded_metadata == metadata
    assert loaded_messages == messages


def test_index_session_upserts_metadata(tmp_path: Path) -> None:
    connection = sqlite3.connect(":memory:")
    initialize_database(connection)
    metadata = SessionMetadata(
        session_id="session-1",
        started_at="2026-05-18T17:30:00+02:00",
        ended_at="2026-05-18T18:42:00+02:00",
        provider="google",
        model="gemini-2.5-pro",
        message_count=24,
        image_count=2,
        tags=["fnirs"],
        project_ref=None,
        spaghetti=True,
        extracted=False,
        extracted_at=None,
        curated=False,
    )

    index_session(connection, metadata, tmp_path / "session-1.md")

    row = connection.execute(
        "SELECT message_count, image_count, tags_json, spaghetti FROM sessions"
    ).fetchone()
    assert row[0] == 24
    assert row[1] == 2
    assert json.loads(row[2]) == ["fnirs"]
    assert row[3] == 1


def test_store_session_asset_sanitizes_name_and_writes_bytes(tmp_path: Path) -> None:
    path = store_session_asset(
        tmp_path,
        session_id="session-1",
        filename="../pcb photo.jpg",
        data=b"image-bytes",
    )

    assert path.name == "session-1-pcb_photo.jpg"
    assert path.parent == tmp_path / "sessions" / "_assets"
    assert path.read_bytes() == b"image-bytes"


def test_store_session_asset_rejects_oversized_image(tmp_path: Path) -> None:
    with pytest.raises(AssetTooLargeError):
        store_session_asset(
            tmp_path,
            session_id="session-1",
            filename="photo.jpg",
            data=b"x" * (MAX_IMAGE_BYTES + 1),
        )


def test_make_session_id_is_sortable_and_sanitizes_slug(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("flightrecorder.storage.secrets.token_hex", lambda _: "abcd1234")

    session_id = make_session_id(
        datetime.fromisoformat("2026-05-18T17:30:00+02:00"),
        "PCB photo idea",
    )

    assert session_id == "2026-05-18-1730-pcb-photo-idea-abcd1234"


def test_session_store_creates_indexes_and_loads_session(tmp_path: Path) -> None:
    connection = sqlite3.connect(":memory:")
    initialize_database(connection)
    store = SessionStore(tmp_path, connection)

    metadata = store.create_session(
        provider="google",
        model="gemini-2.5-pro",
        started_at=datetime.fromisoformat("2026-05-18T17:30:00+02:00"),
        slug="spaghetti",
    )

    loaded_metadata, messages = store.get_session(metadata.session_id)
    listed = store.list_sessions()

    assert loaded_metadata == metadata
    assert messages == []
    assert listed == [metadata]
    assert store.session_path(metadata.session_id).exists()


def test_session_store_adds_message_and_updates_metadata(tmp_path: Path) -> None:
    connection = sqlite3.connect(":memory:")
    initialize_database(connection)
    store = SessionStore(tmp_path, connection)
    metadata = store.create_session(
        provider="google",
        model="gemini-2.5-pro",
        started_at=datetime.fromisoformat("2026-05-18T17:30:00+02:00"),
        slug="spaghetti",
    )

    updated_metadata = store.add_message(
        metadata.session_id,
        ChatMessage(role="user", timestamp="17:30:01", content="hello"),
    )

    loaded_metadata, messages = store.get_session(metadata.session_id)
    row = connection.execute(
        "SELECT message_count FROM sessions WHERE session_id = ?",
        (metadata.session_id,),
    ).fetchone()

    assert updated_metadata.message_count == 1
    assert loaded_metadata.message_count == 1
    assert messages == [ChatMessage(role="user", timestamp="17:30:01", content="hello")]
    assert row[0] == 1


def test_session_store_renames_session_without_changing_id(tmp_path: Path) -> None:
    connection = sqlite3.connect(":memory:")
    initialize_database(connection)
    store = SessionStore(tmp_path, connection)
    metadata = store.create_session(
        provider="google",
        model="gemini-2.5-pro",
        started_at=datetime.fromisoformat("2026-05-18T17:30:00+02:00"),
        slug="spaghetti",
    )

    renamed = store.rename_session(metadata.session_id, "Pulse ox PCA ideas")
    loaded_metadata, messages = store.get_session(metadata.session_id)
    row = connection.execute(
        "SELECT display_name FROM sessions WHERE session_id = ?",
        (metadata.session_id,),
    ).fetchone()

    assert renamed.session_id == metadata.session_id
    assert renamed.display_name == "Pulse ox PCA ideas"
    assert loaded_metadata.display_name == "Pulse ox PCA ideas"
    assert messages == []
    assert row == ("Pulse ox PCA ideas",)


def test_session_store_closes_session_and_preserves_messages(tmp_path: Path) -> None:
    connection = sqlite3.connect(":memory:")
    initialize_database(connection)
    store = SessionStore(tmp_path, connection)
    metadata = store.create_session(
        provider="google",
        model="gemini-2.5-pro",
        started_at=datetime.fromisoformat("2026-05-18T17:30:00+02:00"),
        slug="spaghetti",
    )
    store.add_message(
        metadata.session_id,
        ChatMessage(role="user", timestamp="17:30:01", content="hello"),
    )
    ended_at = datetime.fromisoformat("2026-05-18T17:45:00+02:00")

    closed_metadata = store.close_session(metadata.session_id, ended_at)

    loaded_metadata, messages = store.get_session(metadata.session_id)
    row = connection.execute(
        "SELECT ended_at, message_count FROM sessions WHERE session_id = ?",
        (metadata.session_id,),
    ).fetchone()

    assert closed_metadata.ended_at == "2026-05-18T17:45:00+02:00"
    assert loaded_metadata.ended_at == "2026-05-18T17:45:00+02:00"
    assert messages == [ChatMessage(role="user", timestamp="17:30:01", content="hello")]
    assert row == ("2026-05-18T17:45:00+02:00", 1)


def test_session_store_stores_asset_and_updates_image_count(tmp_path: Path) -> None:
    connection = sqlite3.connect(":memory:")
    initialize_database(connection)
    store = SessionStore(tmp_path, connection)
    metadata = store.create_session(
        provider="google",
        model="gemini-2.5-pro",
        started_at=datetime.fromisoformat("2026-05-18T17:30:00+02:00"),
        slug="spaghetti",
    )

    asset_path = store.store_asset(
        metadata.session_id,
        filename="pcb photo.jpg",
        data=b"image-bytes",
    )

    loaded_metadata, messages = store.get_session(metadata.session_id)
    row = connection.execute(
        "SELECT image_count FROM sessions WHERE session_id = ?",
        (metadata.session_id,),
    ).fetchone()

    assert asset_path.exists()
    assert loaded_metadata.image_count == 1
    assert messages == []
    assert row[0] == 1


def test_session_store_deletes_asset_and_updates_image_count(tmp_path: Path) -> None:
    connection = sqlite3.connect(":memory:")
    initialize_database(connection)
    store = SessionStore(tmp_path, connection)
    metadata = store.create_session(
        provider="google",
        model="gemini-2.5-pro",
        started_at=datetime.fromisoformat("2026-05-18T17:30:00+02:00"),
        slug="spaghetti",
    )
    asset_path = store.store_asset(
        metadata.session_id,
        filename="pcb photo.jpg",
        data=b"image-bytes",
    )

    updated = store.delete_asset(metadata.session_id, asset_path.name)
    loaded_metadata, _messages = store.get_session(metadata.session_id)

    assert asset_path.exists() is False
    assert updated.image_count == 0
    assert loaded_metadata.image_count == 0


def test_safe_session_asset_path_rejects_traversal_and_wrong_session(tmp_path: Path) -> None:
    safe = safe_session_asset_path(tmp_path, "session-1", "session-1-photo.jpg")
    assert safe == (tmp_path / "sessions" / "_assets" / "session-1-photo.jpg").resolve()

    with pytest.raises(FileNotFoundError):
        safe_session_asset_path(tmp_path, "session-1", "../session-1-photo.jpg")
    with pytest.raises(FileNotFoundError):
        safe_session_asset_path(tmp_path, "session-1", "session-2-photo.jpg")


def test_split_frontmatter_raises_on_missing_frontmatter() -> None:
    with pytest.raises(StorageError, match="missing frontmatter"):
        split_frontmatter("no frontmatter here\njust text\n")


def test_split_frontmatter_raises_on_unterminated_frontmatter() -> None:
    with pytest.raises(StorageError, match="unterminated frontmatter"):
        split_frontmatter("---\nsession_id: test\nnever closed\n")


def test_sanitize_filename_raises_on_empty_after_sanitization() -> None:
    with pytest.raises(StorageError, match="empty after sanitization"):
        sanitize_filename("...")


def test_sanitize_slug_returns_session_for_empty_input() -> None:
    result = sanitize_slug("")
    assert result == "session"


def test_sanitize_slug_returns_session_for_symbols_only() -> None:
    result = sanitize_slug("!!!")
    assert result == "session"
