"""Smoke test: provider call guard records usage, respects sentinel, writes sentinel on breach, rejects missing/mismatched pricing."""

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
        exchange_rates_to_dkk={"EUR": 1.0},
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
            warn_at_dkk=5.0,
            hard_stop_dkk=10.0,
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
        print(f"cost_dkk: {result.cost_dkk}")
        print(f"budget_status: {result.budget.evaluation.status}")

        row_count = connection.execute(
            "SELECT COUNT(*) FROM api_calls"
        ).fetchone()[0]
        print(f"api_calls_rows: {row_count}")

        assert result.api_call_id == 1
        assert row_count == 1
        assert result.cost_dkk > 0

        budget_path = runtime_home / "budget"
        budget_path.write_text("status=hard_stop\n", encoding="utf-8")

        try:
            guard.check_before_call(now)
            print("ERROR: BudgetHardStopError not raised")
            sys.exit(1)
        except BudgetHardStopError:
            print("budget_sentinel_blocks: True")

        print("--- hard-stop breach test ---")

        budget_path.unlink()
        connection2 = sqlite3.connect(":memory:")
        initialize_database(connection2)
        runtime_home2 = Path(tmp) / "breach"
        runtime_home2.mkdir()

        guard2 = ProviderCallGuard(
            runtime_home=runtime_home2,
            connection=connection2,
            pricing=pricing,
            warn_at_dkk=5.0,
            hard_stop_dkk=10.0,
        )

        guard2.check_before_call(now)

        expensive = ProviderUsage(
            timestamp=now,
            provider="test",
            model="fake-model",
            role="tagger",
            input_tokens=500_000,
            output_tokens=200_000,
            cached_tokens=0,
            session_id="session-expensive",
        )

        breach_result = guard2.record_usage(expensive)
        breach_sentinel = runtime_home2 / "budget"

        print(f"breach_sentinel_exists: {breach_sentinel.exists()}")
        print(f"breach_budget_status: {breach_result.budget.evaluation.status}")
        print(f"breach_hard_stop_active: {breach_result.budget.hard_stop_active}")

        expensive_calls = connection2.execute(
            "SELECT COUNT(*) FROM api_calls WHERE session_id = ?",
            ("session-expensive",),
        ).fetchone()[0]
        print(f"expensive_call_in_api_calls: {expensive_calls == 1}")

        assert breach_sentinel.exists(), "budget sentinel not written on breach"
        assert breach_result.budget.hard_stop_active
        assert expensive_calls == 1, "expensive call not logged"

        connection.close()
        connection2.close()

        print("--- unknown model test ---")

        connection3 = sqlite3.connect(":memory:")
        initialize_database(connection3)
        runtime_home3 = Path(tmp) / "unknown"
        runtime_home3.mkdir()

        guard3 = ProviderCallGuard(
            runtime_home=runtime_home3,
            connection=connection3,
            pricing=pricing,
            warn_at_dkk=5.0,
            hard_stop_dkk=10.0,
        )

        unknown_usage = ProviderUsage(
            timestamp=now,
            provider="test",
            model="unknown-model",
            role="tagger",
            input_tokens=100,
            output_tokens=10,
            session_id="session-unknown",
        )

        try:
            guard3.record_usage(unknown_usage)
            print("ERROR: ValueError not raised for unknown model")
            sys.exit(1)
        except ValueError as exc:
            print(f"unknown_model_value_error: {bool(exc)}")

        unknown_rows = connection3.execute(
            "SELECT COUNT(*) FROM api_calls"
        ).fetchone()[0]
        print(f"unknown_model_no_api_calls: {unknown_rows == 0}")

        assert unknown_rows == 0, "api_calls row inserted for unknown model"

        connection3.close()

        print("--- provider mismatch test ---")

        connection4 = sqlite3.connect(":memory:")
        initialize_database(connection4)
        runtime_home4 = Path(tmp) / "mismatch"
        runtime_home4.mkdir()

        guard4 = ProviderCallGuard(
            runtime_home=runtime_home4,
            connection=connection4,
            pricing=pricing,
            warn_at_dkk=5.0,
            hard_stop_dkk=10.0,
        )

        mismatch_usage = ProviderUsage(
            timestamp=now,
            provider="wrong-provider",
            model="fake-model",
            role="tagger",
            input_tokens=100,
            output_tokens=10,
            session_id="session-mismatch",
        )

        try:
            guard4.record_usage(mismatch_usage)
            print("ERROR: ValueError not raised for provider mismatch")
            sys.exit(1)
        except ValueError as exc:
            print(f"provider_mismatch_value_error: {bool(exc)}")

        mismatch_rows = connection4.execute(
            "SELECT COUNT(*) FROM api_calls"
        ).fetchone()[0]
        print(f"mismatch_no_api_calls: {mismatch_rows == 0}")

        assert mismatch_rows == 0, "api_calls row inserted for provider mismatch"

        connection4.close()

    print("provider call guard smoke test passed")


if __name__ == "__main__":
    main()
