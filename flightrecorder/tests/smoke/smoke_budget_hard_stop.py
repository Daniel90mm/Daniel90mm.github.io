"""Smoke test: insert fake cost rows, enforce budget, verify temp budget file written."""

from __future__ import annotations

import sqlite3
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src" / "backend"))

from flightrecorder.costs import (
    ApiCallRecord,
    enforce_monthly_budget,
    log_api_call,
)
from flightrecorder.schema import initialize_database


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        runtime_home = Path(tmp)
        connection = sqlite3.connect(":memory:")
        initialize_database(connection)

        now = datetime.now(timezone.utc)
        record_time = now - timedelta(minutes=1)

        for i in range(10):
            log_api_call(
                connection,
                ApiCallRecord(
                    timestamp=record_time.isoformat(),
                    provider="anthropic",
                    model="claude-haiku-4-5",
                    role="tagger",
                    input_tokens=500,
                    output_tokens=50,
                    cached_tokens=0,
                    cost_dkk=100.0,
                    session_id=f"heavy-session-{i}",
                ),
            )

        result = enforce_monthly_budget(
            runtime_home=runtime_home,
            connection=connection,
            now=now,
            warn_at_dkk=5.0,
            hard_stop_dkk=10.0,
        )

        print(f"hard_stop_active: {result.hard_stop_active}")
        print(f"budget_path: {result.hard_stop_path}")
        print(f"budget_file_exists: {result.hard_stop_path.exists()}")
        print(f"budget_status: {result.evaluation.status}")

        assert result.hard_stop_active
        assert result.hard_stop_path.exists()
        assert result.evaluation.status == "hard_stop"

        connection.close()

    print("budget hard stop smoke test passed")


if __name__ == "__main__":
    main()
