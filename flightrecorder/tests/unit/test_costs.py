import sqlite3
from datetime import datetime
from pathlib import Path

import pytest

from flightrecorder.costs import (
    ApiCallRecord,
    compute_cost_eur,
    evaluate_budget,
    evaluate_monthly_budget,
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
