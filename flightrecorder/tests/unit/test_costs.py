import sqlite3
from datetime import datetime
from pathlib import Path

import pytest

from flightrecorder.costs import (
    ApiCallRecord,
    BudgetHardStopError,
    ModelPricing,
    PricingTable,
    ProviderCallGuard,
    ProviderUsage,
    budget_hard_stop_path,
    clear_budget_hard_stop,
    compute_cost_eur,
    enforce_monthly_budget,
    evaluate_budget,
    evaluate_monthly_budget,
    is_budget_hard_stop_active,
    load_pricing,
    log_api_call,
    monthly_cost_to_date,
    parse_pricing,
    total_cost_between,
)
from flightrecorder.schema import initialize_database


def test_log_api_call_inserts_row() -> None:
    connection = sqlite3.connect(":memory:")
    initialize_database(connection)

    row_id = log_api_call(
        connection,
        ApiCallRecord(
            timestamp="2026-05-18T17:30:00+02:00",
            provider="google",
            model="gemini-2.5-pro",
            role="brainstorm",
            input_tokens=100,
            output_tokens=40,
            cached_tokens=0,
            cost_eur=0.0123,
            session_id="session-1",
        ),
    )

    row = connection.execute(
        """
        SELECT provider, model, role, input_tokens, output_tokens, cost_eur, session_id
        FROM api_calls
        WHERE id = ?
        """,
        (row_id,),
    ).fetchone()

    assert row == (
        "google",
        "gemini-2.5-pro",
        "brainstorm",
        100,
        40,
        0.0123,
        "session-1",
    )


def test_monthly_cost_to_date_sums_current_month_only() -> None:
    connection = sqlite3.connect(":memory:")
    initialize_database(connection)
    for timestamp, cost in [
        ("2026-04-30T23:59:00+02:00", 10),
        ("2026-05-01T00:00:00+02:00", 2.5),
        ("2026-05-18T17:30:00+02:00", 1.25),
        ("2026-06-01T00:00:00+02:00", 99),
    ]:
        log_api_call(
            connection,
            ApiCallRecord(
                timestamp=timestamp,
                provider="openai",
                model="gpt-5-mini",
                role="reviewer",
                input_tokens=1,
                output_tokens=1,
                cached_tokens=0,
                cost_eur=cost,
            ),
        )

    total = monthly_cost_to_date(
        connection,
        datetime.fromisoformat("2026-05-31T23:59:59+02:00"),
    )

    assert total == 3.75


def test_total_cost_between_includes_start_and_excludes_end() -> None:
    connection = sqlite3.connect(":memory:")
    initialize_database(connection)
    for timestamp, cost in [
        ("2026-05-01T00:00:00+02:00", 2),
        ("2026-05-31T23:59:59+02:00", 3),
        ("2026-06-01T00:00:00+02:00", 99),
    ]:
        log_api_call(
            connection,
            ApiCallRecord(
                timestamp=timestamp,
                provider="openai",
                model="gpt-5-mini",
                role="reviewer",
                input_tokens=1,
                output_tokens=1,
                cached_tokens=0,
                cost_eur=cost,
            ),
        )

    total = total_cost_between(
        connection,
        datetime.fromisoformat("2026-05-01T00:00:00+02:00"),
        datetime.fromisoformat("2026-06-01T00:00:00+02:00"),
    )

    assert total == 5


def test_parse_pricing_and_compute_cost_eur() -> None:
    pricing = parse_pricing(
        {
            "models": {
                "test-model": {
                    "provider": "openai",
                    "input_per_1k": 1.0,
                    "output_per_1k": 2.0,
                    "cached_per_1k": 0.25,
                    "currency": "USD",
                },
            },
            "exchange_rates_to_eur": {"USD": 0.5},
        }
    )

    cost = compute_cost_eur(
        pricing,
        "test-model",
        input_tokens=1000,
        output_tokens=500,
        cached_tokens=2000,
    )

    assert cost == 1.25


def test_load_pricing_reads_toml(tmp_path: Path) -> None:
    path = tmp_path / "pricing.toml"
    path.write_text(
        """
        [models."test-model"]
        provider = "anthropic"
        input_per_1k = 1.0
        output_per_1k = 2.0
        cached_per_1k = 0.0
        currency = "EUR"
        """,
        encoding="utf-8",
    )

    pricing = load_pricing(path)

    assert pricing.models["test-model"].provider == "anthropic"
    assert compute_cost_eur(pricing, "test-model", 1000, 1000) == 3.0


def test_compute_cost_rejects_negative_tokens() -> None:
    pricing = parse_pricing(
        {
            "models": {
                "test-model": {
                    "provider": "google",
                    "input_per_1k": 1.0,
                    "output_per_1k": 1.0,
                    "cached_per_1k": 0.0,
                    "currency": "EUR",
                },
            },
        }
    )

    with pytest.raises(ValueError):
        compute_cost_eur(pricing, "test-model", -1, 0)


def test_parse_pricing_rejects_missing_models() -> None:
    with pytest.raises(ValueError):
        parse_pricing({})


@pytest.mark.parametrize(
    ("monthly_cost", "expected_status", "should_warn", "should_stop"),
    [
        (9.99, "ok", False, False),
        (10.0, "warn", True, False),
        (79.99, "warn", True, False),
        (80.0, "hard_stop", True, True),
    ],
)
def test_evaluate_budget_thresholds(
    monthly_cost: float,
    expected_status: str,
    should_warn: bool,
    should_stop: bool,
) -> None:
    evaluation = evaluate_budget(monthly_cost, warn_at_eur=10.0, hard_stop_eur=80.0)

    assert evaluation.status == expected_status
    assert evaluation.should_warn is should_warn
    assert evaluation.should_stop is should_stop


def test_evaluate_budget_rejects_invalid_threshold_order() -> None:
    with pytest.raises(ValueError):
        evaluate_budget(0.0, warn_at_eur=80.0, hard_stop_eur=10.0)


def test_evaluate_monthly_budget_uses_current_month_cost() -> None:
    connection = sqlite3.connect(":memory:")
    initialize_database(connection)
    for timestamp, cost in [
        ("2026-04-30T23:59:00+02:00", 99),
        ("2026-05-01T00:00:00+02:00", 5),
        ("2026-05-18T17:30:00+02:00", 6),
    ]:
        log_api_call(
            connection,
            ApiCallRecord(
                timestamp=timestamp,
                provider="anthropic",
                model="claude-haiku-4-5",
                role="tagger",
                input_tokens=1,
                output_tokens=1,
                cached_tokens=0,
                cost_eur=cost,
            ),
        )

    evaluation = evaluate_monthly_budget(
        connection,
        datetime.fromisoformat("2026-05-18T18:00:00+02:00"),
        warn_at_eur=10.0,
        hard_stop_eur=80.0,
    )

    assert evaluation.monthly_cost_eur == 11
    assert evaluation.status == "warn"


def test_budget_hard_stop_path_uses_runtime_home(tmp_path: Path) -> None:
    assert budget_hard_stop_path(tmp_path) == tmp_path / "budget"


def test_clear_budget_hard_stop_returns_false_when_missing(tmp_path: Path) -> None:
    assert clear_budget_hard_stop(tmp_path) is False


def test_enforce_monthly_budget_writes_hard_stop_file(tmp_path: Path) -> None:
    connection = sqlite3.connect(":memory:")
    initialize_database(connection)
    log_api_call(
        connection,
        ApiCallRecord(
            timestamp="2026-05-18T17:30:00+02:00",
            provider="google",
            model="gemini-2.5-pro",
            role="brainstorm",
            input_tokens=1,
            output_tokens=1,
            cached_tokens=0,
            cost_eur=81,
        ),
    )

    result = enforce_monthly_budget(
        runtime_home=tmp_path,
        connection=connection,
        now=datetime.fromisoformat("2026-05-18T18:00:00+02:00"),
        warn_at_eur=30,
        hard_stop_eur=80,
    )

    assert result.evaluation.status == "hard_stop"
    assert result.hard_stop_active is True
    assert result.hard_stop_path == tmp_path / "budget"
    assert is_budget_hard_stop_active(tmp_path) is True
    assert "monthly_cost_eur=81.0" in result.hard_stop_path.read_text(encoding="utf-8")


def test_enforce_monthly_budget_warn_does_not_clear_existing_hard_stop(
    tmp_path: Path,
) -> None:
    connection = sqlite3.connect(":memory:")
    initialize_database(connection)
    existing = tmp_path / "budget"
    existing.write_text("status=hard_stop\n", encoding="utf-8")

    result = enforce_monthly_budget(
        runtime_home=tmp_path,
        connection=connection,
        now=datetime.fromisoformat("2026-05-18T18:00:00+02:00"),
        warn_at_eur=0,
        hard_stop_eur=80,
    )

    assert result.evaluation.status == "warn"
    assert result.hard_stop_active is True
    assert existing.exists()


def test_clear_budget_hard_stop_removes_existing_file(tmp_path: Path) -> None:
    path = tmp_path / "budget"
    path.write_text("status=hard_stop\n", encoding="utf-8")

    assert clear_budget_hard_stop(tmp_path) is True
    assert is_budget_hard_stop_active(tmp_path) is False


def test_provider_call_guard_refuses_existing_hard_stop(tmp_path: Path) -> None:
    connection = sqlite3.connect(":memory:")
    initialize_database(connection)
    (tmp_path / "budget").write_text("status=hard_stop\n", encoding="utf-8")
    guard = ProviderCallGuard(
        runtime_home=tmp_path,
        connection=connection,
        pricing=_pricing_table(),
        warn_at_eur=30,
        hard_stop_eur=80,
    )

    with pytest.raises(BudgetHardStopError):
        guard.check_before_call(datetime.fromisoformat("2026-05-18T18:00:00+02:00"))


def test_provider_call_guard_records_usage_and_cost(tmp_path: Path) -> None:
    connection = sqlite3.connect(":memory:")
    initialize_database(connection)
    guard = ProviderCallGuard(
        runtime_home=tmp_path,
        connection=connection,
        pricing=_pricing_table(),
        warn_at_eur=30,
        hard_stop_eur=80,
    )

    result = guard.record_usage(
        ProviderUsage(
            timestamp=datetime.fromisoformat("2026-05-18T18:00:00+02:00"),
            provider="anthropic",
            model="claude-haiku-4-5",
            role="tagger",
            input_tokens=1000,
            output_tokens=500,
            cached_tokens=100,
            session_id="2026-05-18-1800-test-abcd1234",
        )
    )
    row = connection.execute(
        """
        SELECT provider, model, role, input_tokens, output_tokens, cached_tokens,
               cost_eur, session_id
        FROM api_calls
        WHERE id = ?
        """,
        (result.api_call_id,),
    ).fetchone()

    assert result.cost_eur == pytest.approx(0.0021)
    assert result.budget.evaluation.status == "ok"
    assert row == (
        "anthropic",
        "claude-haiku-4-5",
        "tagger",
        1000,
        500,
        100,
        pytest.approx(0.0021),
        "2026-05-18-1800-test-abcd1234",
    )


def test_provider_call_guard_writes_hard_stop_after_usage(tmp_path: Path) -> None:
    connection = sqlite3.connect(":memory:")
    initialize_database(connection)
    guard = ProviderCallGuard(
        runtime_home=tmp_path,
        connection=connection,
        pricing=_pricing_table(input_per_1k=100),
        warn_at_eur=30,
        hard_stop_eur=80,
    )

    result = guard.record_usage(
        ProviderUsage(
            timestamp=datetime.fromisoformat("2026-05-18T18:00:00+02:00"),
            provider="anthropic",
            model="claude-haiku-4-5",
            role="brainstorm",
            input_tokens=1000,
            output_tokens=0,
        )
    )

    assert result.budget.evaluation.status == "hard_stop"
    assert result.budget.hard_stop_active is True
    assert (tmp_path / "budget").exists()


def test_provider_call_guard_rejects_provider_pricing_mismatch(
    tmp_path: Path,
) -> None:
    connection = sqlite3.connect(":memory:")
    initialize_database(connection)
    guard = ProviderCallGuard(
        runtime_home=tmp_path,
        connection=connection,
        pricing=_pricing_table(),
        warn_at_eur=30,
        hard_stop_eur=80,
    )

    with pytest.raises(ValueError, match="belongs to anthropic"):
        guard.record_usage(
            ProviderUsage(
                timestamp=datetime.fromisoformat("2026-05-18T18:00:00+02:00"),
                provider="openai",
                model="claude-haiku-4-5",
                role="tagger",
                input_tokens=1,
                output_tokens=1,
            )
        )

    count = connection.execute("SELECT COUNT(*) FROM api_calls").fetchone()[0]
    assert count == 0


def _pricing_table(input_per_1k: float = 0.001) -> PricingTable:
    return PricingTable(
        models={
            "claude-haiku-4-5": ModelPricing(
                provider="anthropic",
                model="claude-haiku-4-5",
                input_per_1k=input_per_1k,
                output_per_1k=0.002,
                cached_per_1k=0.001,
                currency="EUR",
            )
        },
        exchange_rates_to_eur={"EUR": 1.0},
    )
