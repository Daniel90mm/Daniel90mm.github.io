"""Cost logging helpers for provider calls."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import sqlite3
import tomllib
from typing import Any


@dataclass(frozen=True)
class ApiCallRecord:
    timestamp: str
    provider: str
    model: str
    role: str
    input_tokens: int
    output_tokens: int
    cached_tokens: int
    cost_eur: float
    session_id: str | None = None


@dataclass(frozen=True)
class ModelPricing:
    provider: str
    model: str
    input_per_1k: float
    output_per_1k: float
    cached_per_1k: float
    currency: str


@dataclass(frozen=True)
class PricingTable:
    models: dict[str, ModelPricing]
    exchange_rates_to_eur: dict[str, float]


@dataclass(frozen=True)
class BudgetEvaluation:
    monthly_cost_eur: float
    warn_at_eur: float
    hard_stop_eur: float
    status: str

    @property
    def should_warn(self) -> bool:
        return self.status in {"warn", "hard_stop"}

    @property
    def should_stop(self) -> bool:
        return self.status == "hard_stop"


def log_api_call(connection: sqlite3.Connection, record: ApiCallRecord) -> int:
    """Insert one provider call cost row and return its id."""

    cursor = connection.execute(
        """
        INSERT INTO api_calls (
            timestamp,
            provider,
            model,
            role,
            input_tokens,
            output_tokens,
            cached_tokens,
            cost_eur,
            session_id
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            record.timestamp,
            record.provider,
            record.model,
            record.role,
            record.input_tokens,
            record.output_tokens,
            record.cached_tokens,
            record.cost_eur,
            record.session_id,
        ),
    )
    connection.commit()
    return int(cursor.lastrowid)


def total_cost_between(
    connection: sqlite3.Connection,
    start: datetime,
    end: datetime,
) -> float:
    """Return total cost for calls in [start, end)."""

    row = connection.execute(
        """
        SELECT COALESCE(SUM(cost_eur), 0)
        FROM api_calls
        WHERE timestamp >= ?
        AND timestamp < ?
        """,
        (start.isoformat(), end.isoformat()),
    ).fetchone()
    return float(row[0])


def monthly_cost_to_date(connection: sqlite3.Connection, now: datetime) -> float:
    """Return cost from the first day of the current month through now."""

    start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    return total_cost_between(connection, start, now)


def evaluate_budget(
    monthly_cost_eur: float,
    warn_at_eur: float,
    hard_stop_eur: float,
) -> BudgetEvaluation:
    """Classify monthly spend against warn and hard-stop thresholds."""

    _validate_nonnegative_amount(monthly_cost_eur, "monthly_cost_eur")
    _validate_nonnegative_amount(warn_at_eur, "warn_at_eur")
    _validate_nonnegative_amount(hard_stop_eur, "hard_stop_eur")
    if warn_at_eur > hard_stop_eur:
        raise ValueError("warn_at_eur must be less than or equal to hard_stop_eur")

    if monthly_cost_eur >= hard_stop_eur:
        status = "hard_stop"
    elif monthly_cost_eur >= warn_at_eur:
        status = "warn"
    else:
        status = "ok"

    return BudgetEvaluation(
        monthly_cost_eur=monthly_cost_eur,
        warn_at_eur=warn_at_eur,
        hard_stop_eur=hard_stop_eur,
        status=status,
    )


def evaluate_monthly_budget(
    connection: sqlite3.Connection,
    now: datetime,
    warn_at_eur: float,
    hard_stop_eur: float,
) -> BudgetEvaluation:
    """Return budget status for the current month."""

    return evaluate_budget(
        monthly_cost_to_date(connection, now),
        warn_at_eur,
        hard_stop_eur,
    )


def load_pricing(path: Path) -> PricingTable:
    """Load a pricing table from a TOML file."""

    with path.open("rb") as handle:
        return parse_pricing(tomllib.load(handle))


def parse_pricing(data: Mapping[str, Any]) -> PricingTable:
    """Parse pricing TOML data into typed pricing records."""

    raw_models = _required_mapping(data, "models")
    models: dict[str, ModelPricing] = {}
    for model, raw_value in raw_models.items():
        raw_model = _mapping(raw_value, f"models.{model}")
        provider = _required_string(raw_model, "provider", f"models.{model}")
        currency = _required_string(raw_model, "currency", f"models.{model}").upper()
        models[str(model)] = ModelPricing(
            provider=provider,
            model=str(model),
            input_per_1k=_required_nonnegative_float(
                raw_model,
                "input_per_1k",
                f"models.{model}",
            ),
            output_per_1k=_required_nonnegative_float(
                raw_model,
                "output_per_1k",
                f"models.{model}",
            ),
            cached_per_1k=_required_nonnegative_float(
                raw_model,
                "cached_per_1k",
                f"models.{model}",
            ),
            currency=currency,
        )

    raw_exchange = data.get("exchange_rates_to_eur", {"EUR": 1.0})
    exchange_mapping = _mapping(raw_exchange, "exchange_rates_to_eur")
    exchange_rates_to_eur = {
        str(currency).upper(): _nonnegative_float(rate, f"exchange_rates_to_eur.{currency}")
        for currency, rate in exchange_mapping.items()
    }
    exchange_rates_to_eur.setdefault("EUR", 1.0)

    return PricingTable(
        models=models,
        exchange_rates_to_eur=exchange_rates_to_eur,
    )


def compute_cost_eur(
    pricing: PricingTable,
    model: str,
    input_tokens: int,
    output_tokens: int,
    cached_tokens: int = 0,
) -> float:
    """Compute EUR cost for one provider call from token counts."""

    _validate_token_count(input_tokens, "input_tokens")
    _validate_token_count(output_tokens, "output_tokens")
    _validate_token_count(cached_tokens, "cached_tokens")

    model_pricing = pricing.models[model]
    if model_pricing.currency not in pricing.exchange_rates_to_eur:
        raise ValueError(f"missing EUR exchange rate for {model_pricing.currency}")

    local_cost = (
        input_tokens / 1000 * model_pricing.input_per_1k
        + output_tokens / 1000 * model_pricing.output_per_1k
        + cached_tokens / 1000 * model_pricing.cached_per_1k
    )
    return local_cost * pricing.exchange_rates_to_eur[model_pricing.currency]


def _required_mapping(data: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    if key not in data:
        raise ValueError(f"missing required pricing section: {key}")
    return _mapping(data[key], key)


def _mapping(value: Any, name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise TypeError(f"{name} must be a table")
    return value


def _required_string(data: Mapping[str, Any], key: str, section: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or value == "":
        raise ValueError(f"{section}.{key} must be a non-empty string")
    return value


def _required_nonnegative_float(data: Mapping[str, Any], key: str, section: str) -> float:
    if key not in data:
        raise ValueError(f"{section}.{key} is required")
    return _nonnegative_float(data[key], f"{section}.{key}")


def _nonnegative_float(value: Any, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise TypeError(f"{name} must be a number")
    number = float(value)
    if number < 0:
        raise ValueError(f"{name} must be non-negative")
    return number


def _validate_token_count(value: int, name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be an integer")
    if value < 0:
        raise ValueError(f"{name} must be non-negative")


def _validate_nonnegative_amount(value: float, name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise TypeError(f"{name} must be a number")
    if float(value) < 0:
        raise ValueError(f"{name} must be non-negative")
