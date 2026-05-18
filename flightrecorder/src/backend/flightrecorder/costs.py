"""Cost logging helpers for provider calls."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timedelta
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
    cost_dkk: float
    session_id: str | None = None


@dataclass(frozen=True)
class ProviderUsage:
    timestamp: datetime
    provider: str
    model: str
    role: str
    input_tokens: int
    output_tokens: int
    cached_tokens: int = 0
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
    exchange_rates_to_dkk: dict[str, float]


@dataclass(frozen=True)
class BudgetEvaluation:
    monthly_cost_dkk: float
    warn_at_dkk: float
    hard_stop_dkk: float
    status: str

    @property
    def should_warn(self) -> bool:
        return self.status in {"warn", "hard_stop"}

    @property
    def should_stop(self) -> bool:
        return self.status == "hard_stop"


@dataclass(frozen=True)
class BudgetGuardResult:
    evaluation: BudgetEvaluation
    hard_stop_active: bool
    hard_stop_path: Path


@dataclass(frozen=True)
class ProviderUsageResult:
    api_call_id: int
    cost_dkk: float
    budget: BudgetGuardResult


class BudgetHardStopError(RuntimeError):
    """Raised when a paid provider call is blocked by the budget sentinel."""


class ProviderCallGuard:
    """Enforce budget and cost logging around paid provider calls."""

    runtime_home: Path
    connection: sqlite3.Connection
    pricing: PricingTable
    warn_at_dkk: float
    hard_stop_dkk: float

    def __init__(
        self,
        runtime_home: Path,
        connection: sqlite3.Connection,
        pricing: PricingTable,
        warn_at_dkk: float,
        hard_stop_dkk: float,
    ) -> None:
        self.runtime_home = runtime_home
        self.connection = connection
        self.pricing = pricing
        self.warn_at_dkk = warn_at_dkk
        self.hard_stop_dkk = hard_stop_dkk

    def check_before_call(self, now: datetime) -> BudgetGuardResult:
        """Refuse a paid provider call when the hard-stop sentinel is active."""

        result = enforce_monthly_budget(
            runtime_home=self.runtime_home,
            connection=self.connection,
            now=now,
            warn_at_dkk=self.warn_at_dkk,
            hard_stop_dkk=self.hard_stop_dkk,
        )
        if result.hard_stop_active:
            raise BudgetHardStopError(
                f"budget hard-stop active: {result.hard_stop_path}"
            )
        return result

    def record_usage(self, usage: ProviderUsage) -> ProviderUsageResult:
        """Log one completed provider call and re-enforce the monthly budget."""

        self._validate_usage_provider(usage)
        cost_dkk = compute_cost_dkk(
            pricing=self.pricing,
            model=usage.model,
            input_tokens=usage.input_tokens,
            output_tokens=usage.output_tokens,
            cached_tokens=usage.cached_tokens,
        )
        api_call_id = log_api_call(
            self.connection,
            ApiCallRecord(
                timestamp=usage.timestamp.isoformat(),
                provider=usage.provider,
                model=usage.model,
                role=usage.role,
                input_tokens=usage.input_tokens,
                output_tokens=usage.output_tokens,
                cached_tokens=usage.cached_tokens,
                cost_dkk=cost_dkk,
                session_id=usage.session_id,
            ),
        )
        budget = enforce_monthly_budget(
            runtime_home=self.runtime_home,
            connection=self.connection,
            now=usage.timestamp + timedelta(microseconds=1),
            warn_at_dkk=self.warn_at_dkk,
            hard_stop_dkk=self.hard_stop_dkk,
        )
        return ProviderUsageResult(
            api_call_id=api_call_id,
            cost_dkk=cost_dkk,
            budget=budget,
        )

    def _validate_usage_provider(self, usage: ProviderUsage) -> None:
        try:
            model_pricing = self.pricing.models[usage.model]
        except KeyError as exc:
            raise ValueError(f"missing pricing for model {usage.model}") from exc

        if model_pricing.provider != usage.provider:
            raise ValueError(
                f"pricing for {usage.model} belongs to {model_pricing.provider}, "
                f"not {usage.provider}"
            )


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
            cost_dkk,
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
            record.cost_dkk,
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
        SELECT COALESCE(SUM(cost_dkk), 0)
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
    monthly_cost_dkk: float,
    warn_at_dkk: float,
    hard_stop_dkk: float,
) -> BudgetEvaluation:
    """Classify monthly spend against warn and hard-stop thresholds."""

    _validate_nonnegative_amount(monthly_cost_dkk, "monthly_cost_dkk")
    _validate_nonnegative_amount(warn_at_dkk, "warn_at_dkk")
    _validate_nonnegative_amount(hard_stop_dkk, "hard_stop_dkk")
    if warn_at_dkk > hard_stop_dkk:
        raise ValueError("warn_at_dkk must be less than or equal to hard_stop_dkk")

    if monthly_cost_dkk >= hard_stop_dkk:
        status = "hard_stop"
    elif monthly_cost_dkk >= warn_at_dkk:
        status = "warn"
    else:
        status = "ok"

    return BudgetEvaluation(
        monthly_cost_dkk=monthly_cost_dkk,
        warn_at_dkk=warn_at_dkk,
        hard_stop_dkk=hard_stop_dkk,
        status=status,
    )


def evaluate_monthly_budget(
    connection: sqlite3.Connection,
    now: datetime,
    warn_at_dkk: float,
    hard_stop_dkk: float,
) -> BudgetEvaluation:
    """Return budget status for the current month."""

    return evaluate_budget(
        monthly_cost_to_date(connection, now),
        warn_at_dkk,
        hard_stop_dkk,
    )


def budget_hard_stop_path(runtime_home: Path) -> Path:
    """Return the runtime hard-stop sentinel path."""

    return runtime_home / "budget"


def is_budget_hard_stop_active(runtime_home: Path) -> bool:
    """Return whether the budget hard-stop sentinel exists."""

    return budget_hard_stop_path(runtime_home).exists()


def write_budget_hard_stop(runtime_home: Path, evaluation: BudgetEvaluation) -> Path:
    """Write the budget hard-stop sentinel file."""

    path = budget_hard_stop_path(runtime_home)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(
            [
                "status=hard_stop",
                f"monthly_cost_dkk={evaluation.monthly_cost_dkk}",
                f"warn_at_dkk={evaluation.warn_at_dkk}",
                f"hard_stop_dkk={evaluation.hard_stop_dkk}",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return path


def clear_budget_hard_stop(runtime_home: Path) -> bool:
    """Remove the budget hard-stop sentinel if it exists."""

    path = budget_hard_stop_path(runtime_home)
    if not path.exists():
        return False
    path.unlink()
    return True


def enforce_monthly_budget(
    runtime_home: Path,
    connection: sqlite3.Connection,
    now: datetime,
    warn_at_dkk: float,
    hard_stop_dkk: float,
) -> BudgetGuardResult:
    """Evaluate monthly spend and write hard-stop sentinel if needed."""

    evaluation = evaluate_monthly_budget(
        connection=connection,
        now=now,
        warn_at_dkk=warn_at_dkk,
        hard_stop_dkk=hard_stop_dkk,
    )
    if evaluation.should_stop:
        path = write_budget_hard_stop(runtime_home, evaluation)
        hard_stop_active = True
    else:
        path = budget_hard_stop_path(runtime_home)
        hard_stop_active = path.exists()

    return BudgetGuardResult(
        evaluation=evaluation,
        hard_stop_active=hard_stop_active,
        hard_stop_path=path,
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

    raw_exchange = data.get("exchange_rates_to_dkk", {"DKK": 1.0})
    exchange_mapping = _mapping(raw_exchange, "exchange_rates_to_dkk")
    exchange_rates_to_dkk = {
        str(currency).upper(): _nonnegative_float(rate, f"exchange_rates_to_dkk.{currency}")
        for currency, rate in exchange_mapping.items()
    }
    exchange_rates_to_dkk.setdefault("DKK", 1.0)

    return PricingTable(
        models=models,
        exchange_rates_to_dkk=exchange_rates_to_dkk,
    )


def compute_cost_dkk(
    pricing: PricingTable,
    model: str,
    input_tokens: int,
    output_tokens: int,
    cached_tokens: int = 0,
) -> float:
    """Compute DKK cost for one provider call from token counts."""

    _validate_token_count(input_tokens, "input_tokens")
    _validate_token_count(output_tokens, "output_tokens")
    _validate_token_count(cached_tokens, "cached_tokens")

    model_pricing = pricing.models[model]
    if model_pricing.currency not in pricing.exchange_rates_to_dkk:
        raise ValueError(f"missing DKK exchange rate for {model_pricing.currency}")

    local_cost = (
        input_tokens / 1000 * model_pricing.input_per_1k
        + output_tokens / 1000 * model_pricing.output_per_1k
        + cached_tokens / 1000 * model_pricing.cached_per_1k
    )
    return local_cost * pricing.exchange_rates_to_dkk[model_pricing.currency]


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
