"""Smoke test: provider call guard records usage and respects budget sentinel."""

from __future__ import annotations

import sqlite3
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src" / "backend"))

from flightrecorder.costs import (
    BudgetHardStopError,
    PricingTable,
    ProviderCallGuard,
    ProviderUsage,
)
from flightrecorder.schema import initialize_database


def make_pricing() -> PricingTable:
    from flightrecorder.costs import ModelPricing
    return PricingTable(
        models={
            "fake-model": ModelPricing(
                provider="test",
                model="fake-model",
                input_per_1k=0.01,
                output_per_1k=0.03,
                cached_per_1k=0.001,
                currency="EUR",
            )
        },
        exchange_rates_to_eur={"EUR": 1.0},
    )


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        runtime_home = Path(tmp)
        connection = sqlite3.connect(":memory:")
        initialize_database(connection)

        pricing = make_pricing()
        now = datetime.now(timezone.utc)

        guard = ProviderCallGuard(
            runtime_home=runtime_home,
            connection=connection,
            pricing=pricing,
            warn_at_eur=5.0,
            hard_stop_eur=10.0,
        )

        guard.check_before_call(now)

        usage = ProviderUsage(
            timestamp=now,
            provider="test",
            model="fake-model",
            role="tagger",
            input_tokens=1000,
            output_tokens=200,
            cached_tokens=0,
            session_id="session-1",
        )

        result = guard.record_usage(usage)
        print(f"api_call_id: {result.api_call_id}")
        print(f"cost_eur: {result.cost_eur}")
        print(f"budget_status: {result.budget.evaluation.status}")

        row_count = connection.execute(
            "SELECT COUNT(*) FROM api_calls"
        ).fetchone()[0]
        print(f"api_calls_rows: {row_count}")

        assert result.api_call_id == 1
        assert row_count == 1
        assert result.cost_eur > 0

        budget_path = runtime_home / "budget"
        budget_path.write_text("status=hard_stop\n", encoding="utf-8")

        try:
            guard.check_before_call(now)
            print("ERROR: BudgetHardStopError not raised")
            sys.exit(1)
        except BudgetHardStopError:
            print("budget_sentinel_blocks: True")

        connection.close()

    print("provider call guard smoke test passed")


if __name__ == "__main__":
    main()
