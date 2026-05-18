from pathlib import Path

import pytest

from flightrecorder.serializers import (
    asset_to_dict,
    chat_message_to_dict,
    session_detail_to_dict,
    session_metadata_to_dict,
)
from flightrecorder.storage import ChatMessage, SessionMetadata


def test_session_metadata_to_dict_uses_spec_fields() -> None:
    metadata = make_metadata()

    result = session_metadata_to_dict(metadata)

    assert result == {
        "session_id": "session-1",
        "started_at": "2026-05-18T17:30:00+02:00",
        "ended_at": None,
        "provider": "google",
        "model": "gemini-2.5-pro",
        "message_count": 1,
        "image_count": 0,
        "tags": ["fnirs"],
        "project_ref": None,
        "spaghetti": True,
        "extracted": False,
        "extracted_at": None,
        "curated": False,
    }


def test_session_detail_to_dict_includes_messages() -> None:
    metadata = make_metadata()
    messages = [ChatMessage(role="user", timestamp="17:30:01", content="hello")]

    result = session_detail_to_dict(metadata, messages)

    assert result["session_id"] == "session-1"
    assert result["messages"] == [
        {"role": "user", "timestamp": "17:30:01", "content": "hello"}
    ]


def test_chat_message_to_dict() -> None:
    message = ChatMessage(role="assistant", timestamp="17:30:14", content="hi")

    assert chat_message_to_dict(message) == {
        "role": "assistant",
        "timestamp": "17:30:14",
        "content": "hi",
    }


def test_asset_to_dict_uses_relative_path(tmp_path: Path) -> None:
    path = tmp_path / "sessions" / "_assets" / "session-1-photo.jpg"
    path.parent.mkdir(parents=True)
    path.write_bytes(b"abc")

    assert asset_to_dict(path, tmp_path) == {
        "filename": "session-1-photo.jpg",
        "relative_path": "sessions/_assets/session-1-photo.jpg",
        "size_bytes": 3,
    }


def test_asset_to_dict_raises_on_path_outside_runtime_home(tmp_path: Path) -> None:
    outside = Path("/tmp") / "outside.jpg"
    outside.write_bytes(b"xyz")

    with pytest.raises(ValueError):
        asset_to_dict(outside, tmp_path)


def make_metadata() -> SessionMetadata:
    return SessionMetadata(
        session_id="session-1",
        started_at="2026-05-18T17:30:00+02:00",
        ended_at=None,
        provider="google",
        model="gemini-2.5-pro",
        message_count=1,
        image_count=0,
        tags=["fnirs"],
        project_ref=None,
        spaghetti=True,
        extracted=False,
        extracted_at=None,
        curated=False,
    )
