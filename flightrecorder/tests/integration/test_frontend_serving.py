"""Integration tests for static frontend serving."""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from flightrecorder.app import create_app
from flightrecorder.config import parse_config
from flightrecorder.runtime import build_runtime_context


def make_app(tmp_path: Path) -> TestClient:
    config = parse_config(
        {
            "paths": {"runtime_home": str(tmp_path)},
        }
    )
    runtime = build_runtime_context(config)
    app = create_app(config=config, runtime=runtime)
    return TestClient(app)


def test_root_returns_index_html(tmp_path: Path) -> None:
    client = make_app(tmp_path)

    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "flightrecorder" in response.text
    assert "/assets/app.js" in response.text
    assert "/assets/styles.css" in response.text


def test_assets_serves_js(tmp_path: Path) -> None:
    client = make_app(tmp_path)

    response = client.get("/assets/app.js")
    assert response.status_code == 200
    content_type = response.headers.get("content-type", "")
    assert "javascript" in content_type or "text/" in content_type
    assert "api" in response.text


def test_assets_do_not_serve_index_html(tmp_path: Path) -> None:
    client = make_app(tmp_path)

    response = client.get("/assets/index.html")
    assert response.status_code == 404


def test_health_still_works(tmp_path: Path) -> None:
    client = make_app(tmp_path)

    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_api_sessions_still_works(tmp_path: Path) -> None:
    client = make_app(tmp_path)

    response = client.get("/api/sessions")
    assert response.status_code == 200
    body = response.json()
    assert "sessions" in body
