"""SQLite schema for flightrecorder metadata."""

from __future__ import annotations

import sqlite3


SCHEMA_VERSION = 1

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sessions (
    session_id TEXT PRIMARY KEY,
    started_at TEXT NOT NULL,
    ended_at TEXT,
    provider TEXT NOT NULL,
    model TEXT NOT NULL,
    message_count INTEGER NOT NULL DEFAULT 0,
    image_count INTEGER NOT NULL DEFAULT 0,
    tags_json TEXT NOT NULL DEFAULT '[]',
    project_ref TEXT,
    spaghetti INTEGER NOT NULL DEFAULT 0,
    extracted INTEGER NOT NULL DEFAULT 0,
    extracted_at TEXT,
    curated INTEGER NOT NULL DEFAULT 0,
    path TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ideas (
    idea_id TEXT PRIMARY KEY,
    captured_at TEXT NOT NULL,
    source_session TEXT NOT NULL,
    tags_json TEXT NOT NULL DEFAULT '[]',
    topics_json TEXT NOT NULL DEFAULT '[]',
    status TEXT NOT NULL DEFAULT 'unmatched',
    match_attempts INTEGER NOT NULL DEFAULT 0,
    matched_to_json TEXT NOT NULL DEFAULT '[]',
    implemented_in_json TEXT NOT NULL DEFAULT '[]',
    path TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_session) REFERENCES sessions(session_id)
);

CREATE TABLE IF NOT EXISTS matches (
    batch_id TEXT PRIMARY KEY,
    generated_at TEXT NOT NULL,
    status TEXT NOT NULL,
    path TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS api_calls (
    id INTEGER PRIMARY KEY,
    timestamp TEXT NOT NULL,
    provider TEXT NOT NULL,
    model TEXT NOT NULL,
    role TEXT NOT NULL,
    input_tokens INTEGER NOT NULL,
    output_tokens INTEGER NOT NULL,
    cached_tokens INTEGER DEFAULT 0,
    cost_dkk REAL NOT NULL,
    session_id TEXT
);

CREATE INDEX IF NOT EXISTS idx_sessions_started_at ON sessions(started_at);
CREATE INDEX IF NOT EXISTS idx_sessions_curated ON sessions(curated);
CREATE INDEX IF NOT EXISTS idx_ideas_status ON ideas(status);
CREATE INDEX IF NOT EXISTS idx_ideas_source_session ON ideas(source_session);
CREATE INDEX IF NOT EXISTS idx_api_calls_timestamp ON api_calls(timestamp);
"""


def initialize_database(connection: sqlite3.Connection) -> None:
    """Apply the schema to an sqlite connection."""

    connection.executescript(SCHEMA_SQL)
    _migrate_api_calls_columns(connection)
    connection.execute(
        "CREATE INDEX IF NOT EXISTS idx_api_calls_session_id ON api_calls(session_id)"
    )
    connection.execute(
        "INSERT OR IGNORE INTO schema_version (version) VALUES (?)",
        (SCHEMA_VERSION,),
    )
    connection.commit()


def _migrate_api_calls_columns(connection: sqlite3.Connection) -> None:
    """Add columns introduced after early local dogfood databases."""

    rows = connection.execute("PRAGMA table_info(api_calls)").fetchall()
    columns = {str(row[1]) for row in rows}
    if "cached_tokens" not in columns:
        connection.execute(
            "ALTER TABLE api_calls ADD COLUMN cached_tokens INTEGER DEFAULT 0"
        )
    if "cost_dkk" not in columns:
        connection.execute(
            "ALTER TABLE api_calls ADD COLUMN cost_dkk REAL NOT NULL DEFAULT 0.0"
        )
    if "session_id" not in columns:
        connection.execute("ALTER TABLE api_calls ADD COLUMN session_id TEXT")


def table_names(connection: sqlite3.Connection) -> list[str]:
    """Return user table names in deterministic order."""

    rows = connection.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        AND name NOT LIKE 'sqlite_%'
        ORDER BY name
        """
    ).fetchall()
    return [str(row[0]) for row in rows]
