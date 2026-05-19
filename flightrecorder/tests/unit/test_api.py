from pathlib import Path

from fastapi.testclient import TestClient

from flightrecorder.app import create_app
from flightrecorder.config import parse_config
from flightrecorder.storage import MAX_IMAGE_BYTES


def make_client(tmp_path: Path) -> TestClient:
    config = parse_config({"paths": {"runtime_home": str(tmp_path)}})
    return TestClient(create_app(config=config))


def test_create_session_returns_approved_shape(tmp_path: Path) -> None:
    client = make_client(tmp_path)

    response = client.post(
        "/api/sessions",
        json={
            "provider": "google",
            "model": "gemini-2.5-pro",
            "slug": "spaghetti",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert set(body) == {
        "session_id",
        "started_at",
        "provider",
        "model",
        "message_count",
        "image_count",
    }
    assert body["provider"] == "google"
    assert body["model"] == "gemini-2.5-pro"
    assert body["message_count"] == 0
    assert body["image_count"] == 0


def test_list_and_get_session(tmp_path: Path) -> None:
    client = make_client(tmp_path)
    created = client.post(
        "/api/sessions",
        json={"provider": "openai", "model": "gpt-5-mini", "slug": "one"},
    ).json()

    list_response = client.get("/api/sessions")
    detail_response = client.get(f"/api/sessions/{created['session_id']}")

    assert list_response.status_code == 200
    assert list_response.json()["total"] == 1
    assert list_response.json()["sessions"][0]["session_id"] == created["session_id"]
    assert detail_response.status_code == 200
    assert detail_response.json()["messages"] == []
    assert detail_response.json()["assets"] == []


def test_list_sessions_limit_offset_and_curated_filter(tmp_path: Path) -> None:
    client = make_client(tmp_path)
    first = client.post(
        "/api/sessions",
        json={"provider": "openai", "model": "gpt-5-mini", "slug": "first"},
    ).json()
    second = client.post(
        "/api/sessions",
        json={"provider": "openai", "model": "gpt-5-mini", "slug": "second"},
    ).json()

    response = client.get("/api/sessions", params={"limit": 1, "offset": 1})
    curated_response = client.get("/api/sessions", params={"curated": True})

    assert response.status_code == 200
    assert response.json()["total"] == 2
    assert response.json()["sessions"][0]["session_id"] in {
        first["session_id"],
        second["session_id"],
    }
    assert curated_response.status_code == 200
    assert curated_response.json() == {"sessions": [], "total": 0}


def test_list_sessions_rejects_invalid_pagination(tmp_path: Path) -> None:
    client = make_client(tmp_path)

    assert client.get("/api/sessions", params={"limit": 0}).status_code == 422
    assert client.get("/api/sessions", params={"limit": 201}).status_code == 422
    assert client.get("/api/sessions", params={"offset": -1}).status_code == 422


def test_get_missing_session_returns_404(tmp_path: Path) -> None:
    client = make_client(tmp_path)

    response = client.get("/api/sessions/missing")

    assert response.status_code == 404
    assert response.json() == {"detail": "Session not found"}


def test_upload_session_asset(tmp_path: Path) -> None:
    client = make_client(tmp_path)
    created = client.post(
        "/api/sessions",
        json={"provider": "google", "model": "gemini-2.5-pro", "slug": "upload"},
    ).json()

    response = client.post(
        f"/api/sessions/{created['session_id']}/upload",
        files={"file": ("pcb photo.jpg", b"image-bytes", "image/jpeg")},
    )

    assert response.status_code == 201
    assert response.json()["asset_path"].endswith("pcb_photo.jpg")
    assert response.json()["asset"]["filename"].endswith("pcb_photo.jpg")
    assert response.json()["asset"]["relative_path"].startswith("sessions/_assets/")
    assert response.json()["image_count"] == 1

    detail_response = client.get(f"/api/sessions/{created['session_id']}")
    assert detail_response.status_code == 200
    assert len(detail_response.json()["assets"]) == 1


def test_delete_session_asset(tmp_path: Path) -> None:
    client = make_client(tmp_path)
    created = client.post(
        "/api/sessions",
        json={"provider": "google", "model": "gemini-2.5-pro", "slug": "upload"},
    ).json()
    upload = client.post(
        f"/api/sessions/{created['session_id']}/upload",
        files={"file": ("notes.txt", b"notes", "text/plain")},
    ).json()

    response = client.delete(
        f"/api/sessions/{created['session_id']}/assets/{upload['asset']['filename']}"
    )

    assert response.status_code == 200
    assert response.json()["deleted"] == upload["asset"]["filename"]
    assert response.json()["image_count"] == 0
    assert response.json()["assets"] == []

    detail_response = client.get(f"/api/sessions/{created['session_id']}")
    assert detail_response.status_code == 200
    assert detail_response.json()["image_count"] == 0
    assert detail_response.json()["assets"] == []


def test_delete_session_asset_rejects_wrong_session_and_traversal(tmp_path: Path) -> None:
    client = make_client(tmp_path)
    first = client.post(
        "/api/sessions",
        json={"provider": "google", "model": "gemini-2.5-pro", "slug": "one"},
    ).json()
    second = client.post(
        "/api/sessions",
        json={"provider": "google", "model": "gemini-2.5-pro", "slug": "two"},
    ).json()
    upload = client.post(
        f"/api/sessions/{first['session_id']}/upload",
        files={"file": ("notes.txt", b"notes", "text/plain")},
    ).json()

    wrong_session = client.delete(
        f"/api/sessions/{second['session_id']}/assets/{upload['asset']['filename']}"
    )
    traversal = client.delete(
        f"/api/sessions/{first['session_id']}/assets/..%2F{upload['asset']['filename']}"
    )

    assert wrong_session.status_code == 404
    assert traversal.status_code == 404


def test_upload_missing_session_returns_404(tmp_path: Path) -> None:
    client = make_client(tmp_path)

    response = client.post(
        "/api/sessions/missing/upload",
        files={"file": ("photo.jpg", b"image-bytes", "image/jpeg")},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Session not found"}


def test_upload_oversized_session_asset_returns_413(tmp_path: Path) -> None:
    client = make_client(tmp_path)
    created = client.post(
        "/api/sessions",
        json={"provider": "google", "model": "gemini-2.5-pro", "slug": "upload"},
    ).json()

    response = client.post(
        f"/api/sessions/{created['session_id']}/upload",
        files={"file": ("photo.jpg", b"x" * (MAX_IMAGE_BYTES + 1), "image/jpeg")},
    )

    assert response.status_code == 413
    assert response.json() == {"detail": "asset upload exceeds 5 MiB cap"}
