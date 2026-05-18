"""Smoke test: GET /health returns 200 with {"status": "ok"} via TestClient."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src" / "backend"))

from fastapi.testclient import TestClient

from flightrecorder.app import create_app


def main() -> None:
    app = create_app()
    client = TestClient(app)

    response = client.get("/health")
    assert response.status_code == 200, f"expected 200, got {response.status_code}"
    assert response.json() == {"status": "ok"}, f"unexpected body: {response.json()}"

    print("backend health smoke test passed")


if __name__ == "__main__":
    main()
