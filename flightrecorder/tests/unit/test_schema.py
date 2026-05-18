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
