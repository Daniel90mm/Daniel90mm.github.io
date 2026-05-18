"""Smoke test: import schema module, create in-memory db, apply schema, list tables."""

from __future__ import annotations

import sqlite3
import sys

try:
    from flightrecorder.schema import initialize_database, table_names
except ImportError as exc:
    print(f"schema module not available: {exc}", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    connection = sqlite3.connect(":memory:")
    initialize_database(connection)
    tables = table_names(connection)
    connection.close()

    for t in tables:
        print(t)

    expected = {"api_calls", "ideas", "matches", "schema_version", "sessions"}
    actual = set(tables)
    if actual != expected:
        missing = expected - actual
        extra = actual - expected
        print(f"table mismatch: missing={missing}, extra={extra}", file=sys.stderr)
        sys.exit(1)

    print("schema smoke test passed")


if __name__ == "__main__":
    main()
