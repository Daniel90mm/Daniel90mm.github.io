"""Integration tests for read-only project/document API routes."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from flightrecorder.app import create_app
from flightrecorder.config import parse_config
from flightrecorder.runtime import build_runtime_context


def make_app(tmp_path: Path) -> TestClient:
    config = parse_config(
        {"paths": {"runtime_home": str(tmp_path)}}
    )
    runtime = build_runtime_context(config)
    app = create_app(config=config, runtime=runtime)
    return TestClient(app)


def setup_fixtures(tmp_path: Path) -> None:
    projects_json = tmp_path / "projects.json"
    projects_json.write_text(
        json.dumps(
            [
                {
                    "name": "fNIRS amp",
                    "ref": "fnirs",
                    "path": "documents/fnirs.md",
                    "active": True,
                    "description": "fNIRS amplifier hardware",
                },
                {
                    "name": "archived idea",
                    "ref": "archived",
                    "path": "documents/archived.md",
                    "active": False,
                    "description": "",
                },
            ]
        ),
        encoding="utf-8",
    )

    docs_dir = tmp_path / "documents"
    docs_dir.mkdir()
    (docs_dir / "fnirs.md").write_text("## Problem\n\nSignal noisy.\n\n## TODOs\n- [ ] filter\n", encoding="utf-8")
    (docs_dir / "oscillator.md").write_text("# Oscillator design\n\n3-phase approach.\n", encoding="utf-8")


def test_list_projects_with_fixtures(tmp_path: Path) -> None:
    setup_fixtures(tmp_path)
    client = make_app(tmp_path)

    response = client.get("/api/projects")
    assert response.status_code == 200
    body = response.json()
    assert "projects" in body
    assert len(body["projects"]) == 1

    fnirs = body["projects"][0]
    assert fnirs["name"] == "fNIRS amp"
    assert fnirs["ref"] == "fnirs"
    assert fnirs["active"] is True


def test_list_projects_empty(tmp_path: Path) -> None:
    client = make_app(tmp_path)

    response = client.get("/api/projects")
    assert response.status_code == 200
    assert response.json() == {"projects": []}


def test_list_documents_with_fixtures(tmp_path: Path) -> None:
    setup_fixtures(tmp_path)
    client = make_app(tmp_path)

    response = client.get("/api/documents")
    assert response.status_code == 200
    body = response.json()
    assert "documents" in body
    assert len(body["documents"]) == 2

    refs = {doc["ref"] for doc in body["documents"]}
    assert refs == {"fnirs", "oscillator"}

    for doc in body["documents"]:
        assert doc["path"].startswith("documents/")
        assert doc["path"].endswith(".md")
        assert isinstance(doc["size_bytes"], int)
        assert "modified_at" in doc


def test_list_documents_empty(tmp_path: Path) -> None:
    client = make_app(tmp_path)

    response = client.get("/api/documents")
    assert response.status_code == 200
    assert response.json() == {"documents": []}


def test_get_document_by_ref(tmp_path: Path) -> None:
    setup_fixtures(tmp_path)
    client = make_app(tmp_path)

    response = client.get("/api/documents/fnirs")
    assert response.status_code == 200
    body = response.json()
    assert body["ref"] == "fnirs"
    assert body["path"] == "documents/fnirs.md"
    assert "Signal noisy" in body["body"]
    assert "## Problem" in body["body"]
    assert isinstance(body["size_bytes"], int)


def test_get_document_not_found(tmp_path: Path) -> None:
    setup_fixtures(tmp_path)
    client = make_app(tmp_path)

    response = client.get("/api/documents/nonexistent")
    assert response.status_code == 404


def test_get_document_sanitizes_ref(tmp_path: Path) -> None:
    setup_fixtures(tmp_path)
    client = make_app(tmp_path)

    response = client.get("/api/documents/../etc-passwd")
    assert response.status_code == 404

    response = client.get("/api/documents/!!!")
    assert response.status_code == 404


def test_routes_are_read_only(tmp_path: Path) -> None:
    client = make_app(tmp_path)

    docs_dir = tmp_path / "documents"
    assert not docs_dir.exists()

    response = client.get("/api/documents")
    assert response.status_code == 200
    assert response.json() == {"documents": []}
    assert not docs_dir.exists(), "read route must not create documents dir"

    response = client.get("/api/projects")
    assert response.status_code == 200
    projects_file = tmp_path / "projects.json"
    assert not projects_file.exists(), "read route must not create projects.json"
