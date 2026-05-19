"""Smoke test: insert fake api_calls to cross warn threshold, print budget status."""

from __future__ import annotations

import sqlite3
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src" / "backend"))

from flightrecorder.costs import (
    ApiCallRecord,
    evaluate_monthly_budget,
    log_api_call,
)
from flightrecorder.schema import initialize_database


def main() -> None:
    connection = sqlite3.connect(":memory:")
    initialize_database(connection)

    now = datetime.now(timezone.utc)
    record_time = now - timedelta(minutes=1)

    cost_per_call = 2.0
    warn_threshold = 5.0
    hard_stop = 10.0

    for i in range(4):
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
                cost_dkk=cost_per_call,
                session_id=f"session-{i}",
            ),
        )

    evaluation = evaluate_monthly_budget(
        connection, now, warn_at_dkk=warn_threshold, hard_stop_dkk=hard_stop
    )

    print(f"monthly_cost_dkk: {evaluation.monthly_cost_dkk}")
    print(f"warn_at_dkk: {evaluation.warn_at_dkk}")
    print(f"hard_stop_dkk: {evaluation.hard_stop_dkk}")
    print(f"status: {evaluation.status}")
    print(f"should_warn: {evaluation.should_warn}")
    print(f"should_stop: {evaluation.should_stop}")

    expected_cost = cost_per_call * 4
    assert evaluation.monthly_cost_dkk == expected_cost
    assert evaluation.status == "warn"
    assert evaluation.should_warn is True
    assert evaluation.should_stop is False

    connection.close()
    print("budget smoke test passed")


if __name__ == "__main__":
    main()
