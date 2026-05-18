"""SQLite connection helpers."""

from __future__ import annotations

from pathlib import Path
import sqlite3

from flightrecorder.schema import initialize_database


def metadata_db_path(runtime_home: Path) -> Path:
    """Return the metadata database path for a runtime home."""

    return runtime_home / "metadata.db"


def connect_metadata_db(runtime_home: Path) -> sqlite3.Connection:
    """Open and initialize metadata.db under the runtime home."""

    runtime_home.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(metadata_db_path(runtime_home), check_same_thread=False)
    connection.execute("PRAGMA foreign_keys = ON")
    initialize_database(connection)
    return connection
