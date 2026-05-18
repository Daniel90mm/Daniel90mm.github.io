"""Smoke test: create in-memory db, log an API call, print id and monthly cost."""

from __future__ import annotations

import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src" / "backend"))

from flightrecorder.costs import ApiCallRecord, log_api_call, monthly_cost_to_date
from flightrecorder.schema import initialize_database


def main() -> None:
    connection = sqlite3.connect(":memory:")
    initialize_database(connection)

    record = ApiCallRecord(
        timestamp=datetime.now(timezone.utc).isoformat(),
        provider="anthropic",
        model="claude-haiku-4-5",
        role="tagger",
        input_tokens=1200,
        output_tokens=42,
        cached_tokens=0,
        cost_dkk=0.0015,
        session_id="2026-05-18-1730-test-abcd1234",
    )

    inserted_id = log_api_call(connection, record)
    print(f"inserted_id: {inserted_id}")

    cost = monthly_cost_to_date(connection, datetime.now(timezone.utc))
    print(f"monthly_cost: {cost}")

    connection.close()
    print("cost logging smoke test passed")


if __name__ == "__main__":
    main()
