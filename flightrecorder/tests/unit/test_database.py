from pathlib import Path

from flightrecorder.database import connect_metadata_db, metadata_db_path
from flightrecorder.schema import table_names


def test_metadata_db_path(tmp_path: Path) -> None:
    assert metadata_db_path(tmp_path) == tmp_path / "metadata.db"


def test_connect_metadata_db_initializes_schema(tmp_path: Path) -> None:
    connection = connect_metadata_db(tmp_path)

    assert metadata_db_path(tmp_path).exists()
    assert table_names(connection) == [
        "api_calls",
        "ideas",
        "matches",
        "schema_version",
        "sessions",
    ]
    assert connection.execute("PRAGMA foreign_keys").fetchone()[0] == 1
