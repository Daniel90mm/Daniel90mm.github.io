from pathlib import Path

from fastapi.testclient import TestClient

from flightrecorder.app import create_app
from flightrecorder.config import parse_config
from flightrecorder.database import connect_metadata_db


def test_health_endpoint(tmp_path: Path) -> None:
    config = parse_config({"paths": {"runtime_home": str(tmp_path)}})
    client = TestClient(create_app(config=config))

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_app_wires_runtime_context(tmp_path: Path) -> None:
    config = parse_config({"paths": {"runtime_home": str(tmp_path)}})
    database = connect_metadata_db(tmp_path)
    app = create_app(config=config)

    assert app.state.runtime.config == config
    assert app.state.runtime.sessions.runtime_home == tmp_path
    row = app.state.runtime.database.execute("PRAGMA foreign_keys").fetchone()
    assert row[0] == 1
    assert database.execute("PRAGMA foreign_keys").fetchone()[0] == 1
