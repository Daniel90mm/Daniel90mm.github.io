import sqlite3

from flightrecorder.schema import initialize_database, table_names


def test_initialize_database_creates_expected_tables() -> None:
    connection = sqlite3.connect(":memory:")

    initialize_database(connection)

    assert table_names(connection) == [
        "api_calls",
        "ideas",
        "matches",
        "schema_version",
        "sessions",
    ]


def test_api_calls_schema_matches_spec_columns() -> None:
    connection = sqlite3.connect(":memory:")
    initialize_database(connection)

    rows = connection.execute("PRAGMA table_info(api_calls)").fetchall()
    columns = [row[1] for row in rows]

    assert columns == [
        "id",
        "timestamp",
        "provider",
        "model",
        "role",
        "input_tokens",
        "output_tokens",
        "cached_tokens",
        "cost_dkk",
        "session_id",
    ]


def test_sessions_schema_includes_display_name() -> None:
    connection = sqlite3.connect(":memory:")
    initialize_database(connection)

    rows = connection.execute("PRAGMA table_info(sessions)").fetchall()
    columns = [row[1] for row in rows]

    assert "display_name" in columns


def test_initialize_database_migrates_early_sessions_table() -> None:
    connection = sqlite3.connect(":memory:")
    connection.executescript(
        """
        CREATE TABLE sessions (
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
            path TEXT NOT NULL
        );
        """
    )

    initialize_database(connection)

    rows = connection.execute("PRAGMA table_info(sessions)").fetchall()
    columns = [row[1] for row in rows]
    assert "display_name" in columns


def test_initialize_database_migrates_early_api_calls_table() -> None:
    connection = sqlite3.connect(":memory:")
    connection.executescript(
        """
        CREATE TABLE api_calls (
            id INTEGER PRIMARY KEY,
            timestamp TEXT NOT NULL,
            provider TEXT NOT NULL,
            model TEXT NOT NULL,
            role TEXT NOT NULL,
            input_tokens INTEGER NOT NULL,
            output_tokens INTEGER NOT NULL
        );
        INSERT INTO api_calls (
            timestamp, provider, model, role, input_tokens, output_tokens
        ) VALUES (
            '2026-05-19T00:00:00+00:00', 'stub', 'stub-model',
            'brainstorm', 1, 2
        );
        """
    )

    initialize_database(connection)

    rows = connection.execute("PRAGMA table_info(api_calls)").fetchall()
    columns = [row[1] for row in rows]
    assert "cached_tokens" in columns
    assert "cost_dkk" in columns
    assert "session_id" in columns

    row = connection.execute(
        "SELECT cached_tokens, cost_dkk, session_id FROM api_calls"
    ).fetchone()
    assert row == (0, 0.0, None)
